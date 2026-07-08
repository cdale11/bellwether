
import json, os, re, time, urllib.request, random, threading, difflib

class AIProvider:
    def __init__(self):
        self.enabled=os.getenv("BELLWETHER_AI","1").lower() in {"1","true","yes","on"}
        self.base_url=os.getenv("BELLWETHER_AI_URL","http://127.0.0.1:11434")
        # v0.5.0 integrated local-model selection: models already pulled into Ollama
        # are discovered and used automatically. Environment variables remain optional
        # developer overrides, not a requirement for normal play.
        installed = self._installed_ollama_models()
        fast_override = os.getenv("BELLWETHER_AI_FAST_MODEL") or os.getenv("BELLWETHER_AI_MODEL")
        deep_override = os.getenv("BELLWETHER_AI_DEEP_MODEL")
        self.fast_model = fast_override or self._pick_installed_model(
            installed, ["qwen3.5:2b", "qwen3.5:4b", "qwen3:1.7b", "llama3.2:3b"]
        ) or "qwen3.5:2b"
        self.deep_model = deep_override or self._pick_installed_model(
            installed, ["qwen3.5:4b", "qwen3.5:2b", self.fast_model]
        ) or self.fast_model
        self.model=self.fast_model  # compatibility: existing diagnostics and UI report the foreground model
        self.num_ctx=max(1024,int(os.getenv("BELLWETHER_AI_NUM_CTX","4096")))
        self.timeout=float(os.getenv("BELLWETHER_AI_TIMEOUT","30"))
        # v0.6.1: default to every CPU thread available to this process. sched_getaffinity
        # respects containers/cgroups and CPU affinity; os.cpu_count is the portable fallback.
        try:
            detected_threads = len(os.sched_getaffinity(0))
        except (AttributeError, OSError):
            detected_threads = os.cpu_count() or 1
        self.num_threads=max(1,int(os.getenv("BELLWETHER_AI_THREADS",str(detected_threads))))
        self._health_cache=None
        self._health_cache_at=0.0
        self.last_status={"state":"not_checked","connected":False,"model":self.model,
          "last_error":"No AI request yet","last_latency_ms":None,"last_director":None,
          "valid_response":False,"attempts_used":0}
        self.debug_traces=[]
        self._last_trace_index=None
        # Ollama is a shared local resource. Only one generation runs at a time;
        # waiting player-facing dialogue is admitted before queued background Directors.
        self._ai_gate = threading.Condition()
        self._ai_active = False
        self._foreground_waiters = 0
        # Part 27: compact whole-playthrough overview supplied by Game before calls.
        # It is not model-hidden state: it is explicit saveable metadata rebuilt from
        # authoritative game state and attached to every Director/dialogue request.
        self.overview_context = {}
        self.recent_call_memory = []


    def _installed_ollama_models(self):
        """Return locally installed Ollama model names without requiring shell configuration."""
        try:
            with urllib.request.urlopen(self.base_url.rstrip("/") + "/api/tags", timeout=1.5) as r:
                data = json.loads(r.read().decode())
            return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
        except Exception:
            return []

    @staticmethod
    def _pick_installed_model(installed, preferences):
        for preferred in preferences:
            if not preferred:
                continue
            for name in installed:
                if name == preferred or name.startswith(preferred + ":"):
                    return name
        return None

    def model_for_task(self,director):
        # v0.5.0 routing-ready boundary. Existing synchronous Directors stay fast;
        # future strategic tasks can opt into the deep model without changing callers.
        if director in {"town_mind","procedural_arc","recurrence_strategy","horror_strategy"}:
            return self.deep_model
        return self.fast_model

    def remember_call(self, director, result):
        self.recent_call_memory.append({"director": director, "result": result})
        self.recent_call_memory = self.recent_call_memory[-12:]

    def set_overview_context(self, overview):
        self.overview_context = overview or {}

    def _context_projection(self, director):
        """Route compact global memory; bounded calls get only non-duplicated essentials."""
        o=self.overview_context or {}
        world=o.get("world_now",{})
        if director=="weather":
            return {
                "story_phase":o.get("story_summary"),
                "village_mood":world.get("village_mood"),
            }
        if director=="traffic":
            return {
                "story_phase":o.get("story_summary"),
                "village_mood":world.get("village_mood"),
            }
        if director=="npc":
            return {
                "story_phase":o.get("story_summary"),
                "player_style":o.get("player_style"),
                "psychological_stage":o.get("psychological_context",{}).get("state",{}).get("stage","ordinary"),
            }
        if director=="conversation":
            return {
                "story_summary":o.get("story_summary"),
                "story_beats":o.get("story_beats",[])[-3:],
                "season":world.get("season"),
                "weather":world.get("weather"),
                "village_mood":world.get("village_mood"),
                "relationships":o.get("relationships"),
                "recent_world_history":o.get("recent_world_history",[])[-5:],
                "psychological_context":o.get("psychological_context"),
            }
        if director=="player_conversation":
            # Foreground dialogue needs continuity, not the entire compiled world dump.
            # Keep this projection intentionally compact so small local models can
            # answer before the player-facing timeout.
            return {
                "story_summary":o.get("story_summary"),
                "story_beats":o.get("story_beats",[])[-2:],
                "player_style":o.get("player_style"),
                "psychological_stage":o.get("psychological_context",{}).get("state",{}).get("stage","ordinary"),
                "branch_context":o.get("branch_context"),
            }
        if director=="season":
            return {"run_history":o.get("run_history",[])[-2:]}
        return o

    def _recent_decisions_for(self, director):
        """Route recent LLM memory by relevance instead of attaching every call."""
        recent=self.recent_call_memory[-12:]
        if director=="weather":
            same=[x for x in recent if x.get("director")=="weather"]
            return same[-2:]
        if director in ("traffic","npc"):
            # Actor-specific history is supplied by the Director context. Mixed
            # same-domain decisions from other actors create false causal influence.
            return []
        if director=="conversation":
            return recent[-4:]
        if director=="player_conversation":
            # Bounded Director choices are irrelevant to a direct NPC reply and were
            # a major source of foreground prompt bloat in Part 30.2.
            return []
        return recent[-4:]

    def _context_with_overview(self, context, director=None):
        merged = dict(context or {})
        projection=self._context_projection(director)
        if projection:
            merged["game_overview_memory"] = projection
        recent=self._recent_decisions_for(director)
        if recent:
            merged["recent_llm_decisions"] = recent
        return merged


    def _acquire_ai_slot(self, foreground=False):
        with self._ai_gate:
            if foreground:
                self._foreground_waiters += 1
            try:
                while self._ai_active or (not foreground and self._foreground_waiters > 0):
                    self._ai_gate.wait()
                self._ai_active = True
            finally:
                if foreground:
                    self._foreground_waiters -= 1

    def _release_ai_slot(self):
        with self._ai_gate:
            self._ai_active = False
            self._ai_gate.notify_all()

    def health(self):
        now=time.time()
        if self._health_cache is not None and now-self._health_cache_at < 10:
            return dict(self._health_cache)
        if not self.enabled:
            self.last_status.update(state="disabled",connected=False,last_error="AI disabled")
            self._health_cache=dict(self.last_status)
            self._health_cache_at=now
            return dict(self.last_status)
        try:
            with urllib.request.urlopen(self.base_url.rstrip("/")+"/api/tags",timeout=3) as r:
                data=json.loads(r.read().decode())
            names=[m.get("name","") for m in data.get("models",[])]
            ok=any(n==self.model or n.startswith(self.model+":") for n in names)
            self.last_status.update(state="ready" if ok else "model_missing",connected=True,
                last_error=None if ok else f"{self.model} is not installed")
        except Exception as exc:
            self.last_status.update(state="server_unreachable",connected=False,
                last_error=f"{type(exc).__name__}: {str(exc)[:160]}")
        self._health_cache=dict(self.last_status)
        self._health_cache_at=time.time()
        return dict(self.last_status)

    @staticmethod
    def meaningful(v):
        if v is None:return False
        if isinstance(v,str):return bool(v.strip())
        if isinstance(v,dict):return bool(v) and any(AIProvider.meaningful(x) for x in v.values())
        if isinstance(v,list):return bool(v) and any(AIProvider.meaningful(x) for x in v)
        return True

    def ask_value(self,director,question,context,allowed=None):
        """Ask one narrow state question. Retry only empty/no-result replies."""
        if not self.enabled:return None
        context = self._context_with_overview(context, director)
        tries=max(1,int(os.getenv("BELLWETHER_AI_RETRIES","3")))
        for attempt in range(1,tries+1):
            self.last_status["last_director"]=director
            started=time.time()
            allowed_text=f"\nALLOWED VALUES: {json.dumps(allowed)}" if allowed else ""
            prompt=(
              "You are a state decision component for Bellwether, a living village simulation. "
              "Answer the ONE QUESTION only. Return JSON exactly as {\"value\": ...}. "
              "Never return an empty value. No explanation."
              f"\nDIRECTOR: {director}\nQUESTION: {question}{allowed_text}"
              f"\nCONTEXT: {json.dumps(context,separators=(',',':'))}"
            )
            payload=json.dumps({"model":self.model_for_task(director),"prompt":prompt,"stream":False,
              "format":"json","keep_alive":"10m",
              "options":{"temperature":0.55,"num_predict":80,"num_thread":self.num_threads,"num_ctx":self.num_ctx}}).encode()
            req=urllib.request.Request(self.base_url.rstrip("/")+"/api/generate",data=payload,
              headers={"Content-Type":"application/json"},method="POST")
            try:
                with urllib.request.urlopen(req,timeout=self.timeout) as response:
                    outer=json.loads(response.read().decode())
                    obj=json.loads(outer.get("response","{}"))
                    value=obj.get("value") if isinstance(obj,dict) else None
                latency=int((time.time()-started)*1000)
                if self.meaningful(value):
                    self.last_status.update(state="ready",connected=True,last_error=None,
                      last_latency_ms=latency,valid_response=True,attempts_used=attempt)
                    self.remember_call(director, {"type":"value","value":value})
                    return value
                self.last_status.update(state="ready",connected=True,
                  last_error=f"Empty value; retrying ({attempt}/{tries})",
                  last_latency_ms=latency,valid_response=False,attempts_used=attempt)
            except TimeoutError:
                self.last_status.update(state="request_timeout",connected=True,
                  last_error=f"Request timed out ({attempt}/{tries})",
                  last_latency_ms=int((time.time()-started)*1000),valid_response=False,attempts_used=attempt)
            except Exception as exc:
                self.last_status.update(state="request_failed",connected=False,
                  last_error=f"{type(exc).__name__}: {str(exc)[:160]}",
                  last_latency_ms=int((time.time()-started)*1000),valid_response=False,attempts_used=attempt)
            if attempt<tries:
                # A timed-out Ollama request may still be unwinding server-side.
                # Give it a short bounded cooldown instead of immediately piling on.
                cooldown = min(2.0, 0.75 * attempt) if self.last_status.get("state") in {"request_timeout","request_failed"} else 0.25 * attempt
                time.sleep(cooldown)
        return None

    def _record_trace(self, trace):
        self.debug_traces.append(trace)
        self.debug_traces=self.debug_traces[-80:]
        self._last_trace_index=len(self.debug_traces)-1
        return self._last_trace_index

    def _annotate_last_trace(self, **fields):
        if self._last_trace_index is not None and 0 <= self._last_trace_index < len(self.debug_traces):
            self.debug_traces[self._last_trace_index].update(fields)

    def _plain_request(self, director, prompt, max_tokens=120, temperature=0.5, no_think=False, tries_override=None, foreground=False, timeout_override=None):
        """Raw Ollama request with complete observability and adaptive length recovery."""
        tries=max(1, int(tries_override if tries_override is not None else os.getenv("BELLWETHER_AI_RETRIES","3")))
        request_timeout=float(timeout_override if timeout_override is not None else self.timeout)
        current_tokens=max_tokens
        for attempt in range(1,tries+1):
            self.last_status["last_director"]=director
            started=time.time()
            payload_obj={
                "model":self.model_for_task(director),"prompt":prompt,"stream":False,"keep_alive":"10m",
                "options":{"temperature":temperature,"num_predict":current_tokens,"num_thread":self.num_threads,"num_ctx":self.num_ctx}
            }
            if no_think:
                # Qwen3 reasoning mode must be disabled through Ollama's top-level API field.
                # A /no_think prompt prefix is not reliable for /api/generate.
                payload_obj["think"] = False
            payload=json.dumps(payload_obj).encode()
            req=urllib.request.Request(self.base_url.rstrip("/")+"/api/generate",data=payload,
                headers={"Content-Type":"application/json"},method="POST")
            trace={
                "timestamp":time.strftime("%H:%M:%S"),
                "director":director,
                "attempt":attempt,
                "max_attempts":tries,
                "endpoint":"/api/generate",
                "model":self.model_for_task(director),
                "prompt":prompt,
                "prompt_chars":len(prompt),
                "prompt_words":len(prompt.split()),
                "request_options":payload_obj["options"],
                "think":payload_obj.get("think"),
                "http_status":None,
                "ollama_fields":{},
                "raw_response":None,
                "parser_stage":"awaiting_response",
                "parser_detail":"",
                "result":"pending",
                "latency_ms":None,
                "queue_wait_ms":None,
                "http_inference_ms":None,
                "timeout_seconds":request_timeout,
            }
            slot_acquired = False
            try:
                queue_started=time.perf_counter()
                self._acquire_ai_slot(foreground=foreground)
                trace["queue_wait_ms"]=int((time.perf_counter()-queue_started)*1000)
                slot_acquired = True
                http_started=time.perf_counter()
                with urllib.request.urlopen(req,timeout=request_timeout) as response:
                    trace["http_status"]=getattr(response,"status",200)
                    body=response.read().decode()
                    outer=json.loads(body)
                    text=str(outer.get("response",""))
                    trace["raw_response"]=text
                    trace["http_inference_ms"]=int((time.perf_counter()-http_started)*1000)
                    trace["ollama_fields"]={
                        k:outer.get(k) for k in
                        ("model","created_at","done","done_reason","total_duration",
                         "load_duration","prompt_eval_count","prompt_eval_duration",
                         "eval_count","eval_duration")
                        if k in outer
                    }
                latency=int((time.time()-started)*1000)
                trace["latency_ms"]=latency
                if text.strip():
                    trace["parser_stage"]="raw_text_received"
                    trace["parser_detail"]="Non-empty text returned; caller parser will inspect it."
                    trace["result"]="response_received"
                    self._record_trace(trace)
                    self.last_status.update(state="ready",connected=True,last_error=None,
                        last_latency_ms=latency,valid_response=True,attempts_used=attempt)
                    return text.strip()

                done_reason = outer.get("done_reason")
                trace["parser_stage"]="empty_response"
                if done_reason == "length":
                    next_tokens = min(max(current_tokens * 2, 96), 384)
                    trace["parser_detail"] = (
                        f"Empty visible response after length exhaustion at {current_tokens} tokens. "
                        f"Next attempt budget: {next_tokens}."
                    )
                    current_tokens = next_tokens
                else:
                    trace["parser_detail"]="Ollama response field was empty or whitespace."
                trace["result"]="retry" if attempt<tries else "failed"
                self._record_trace(trace)
                self.last_status.update(state="ready",connected=True,
                    last_error=f"Empty response; retrying ({attempt}/{tries})",
                    last_latency_ms=latency,valid_response=False,attempts_used=attempt)
            except TimeoutError as exc:
                if trace.get("queue_wait_ms") is not None:
                    trace["http_inference_ms"]=int((time.perf_counter()-http_started)*1000)
                trace["latency_ms"]=int((time.time()-started)*1000)
                trace["parser_stage"]="transport_error"
                trace["parser_detail"]=f"TimeoutError: {exc}"
                trace["result"]="retry" if attempt<tries else "failed"
                self._record_trace(trace)
                self.last_status.update(state="request_timeout",connected=True,
                    last_error=f"Request timed out ({attempt}/{tries})",
                    last_latency_ms=trace["latency_ms"],valid_response=False,attempts_used=attempt)
            except Exception as exc:
                trace["latency_ms"]=int((time.time()-started)*1000)
                trace["parser_stage"]="transport_or_decode_error"
                trace["parser_detail"]=f"{type(exc).__name__}: {str(exc)}"
                trace["result"]="retry" if attempt<tries else "failed"
                self._record_trace(trace)
                self.last_status.update(state="request_failed",connected=False,
                    last_error=f"{type(exc).__name__}: {str(exc)[:160]}",
                    last_latency_ms=trace["latency_ms"],valid_response=False,attempts_used=attempt)
            finally:
                if slot_acquired:
                    self._release_ai_slot()
            if attempt<tries: time.sleep(.25*attempt)
        return None

    def ask_choice(self,director,question,context,candidates):
        """Choose one Director candidate and record every parser decision."""
        if not self.enabled or not candidates:return None
        context = self._context_with_overview(context, director)
        # Shuffle presentation order to prevent persistent A/first-option bias while retaining candidate mapping.
        candidates=list(candidates)
        random.SystemRandom().shuffle(candidates)
        letters=[chr(65+i) for i in range(len(candidates))]
        options="\n".join(f"{letters[i]} = {candidates[i]['label']}" for i in range(len(candidates)))
        prompt=(
            "You are making ONE bounded state decision for Bellwether. "
            "Use the context and choose one plausible option. Favor grounded variety when several options fit, "
            "and avoid repeating recent actions shown in context unless repetition is strongly justified. "
            "Reply with exactly ONE option letter and nothing else.\n"
            f"DIRECTOR: {director}\nCONTEXT: {json.dumps(context,separators=(',',':'))}\n"
            f"QUESTION: {question}\nOPTIONS:\n{options}\nANSWER:"
        )
        bounded_timeout=float(os.getenv("BELLWETHER_BOUNDED_AI_TIMEOUT","45"))
        text=self._plain_request(director,prompt,max_tokens=8,temperature=.5,no_think=True,
                                 tries_override=2,timeout_override=bounded_timeout)
        if not text:
            return None

        upper=text.upper().strip()
        parsed=None
        method=None

        if upper in letters:
            parsed=upper
            method="exact_token"
        else:
            tokens=re.findall(r'(?<![A-Z])([A-Z])(?![A-Z])',upper)
            for token in tokens:
                if token in letters:
                    parsed=token
                    method="token_from_prose"
                    break

        if parsed is None:
            low=text.lower()
            for i,candidate in enumerate(candidates):
                if candidate["label"].lower() in low:
                    parsed=letters[i]
                    method="full_label_match"
                    break

        if parsed is not None:
            chosen=candidates[letters.index(parsed)]
            self._annotate_last_trace(
                parser_stage="choice_parsed",
                parser_detail=f"Matched option {parsed} using {method}.",
                extracted_token=parsed,
                candidate=chosen,
                result="accepted_by_parser"
            )
            self.remember_call(director, {"type":"choice","choice":chosen.get("id"),"label":chosen.get("label")})
            return chosen

        self._annotate_last_trace(
            parser_stage="choice_parse_failed",
            parser_detail=f"No valid option extracted. Allowed tokens: {letters}.",
            extracted_token=None,
            candidate=None,
            result="parser_failed"
        )
        self.last_status.update(valid_response=False,
            last_error="Qwen returned text, but no valid candidate option could be extracted.")
        return None

    def _obvious_daypart_contradiction(self, dialogue, daypart):
        """Reject only explicit, obvious daypart contradictions; avoid semantic overreach."""
        text=(dialogue or "").lower()
        terms={
            "morning":("sun is setting","sun is just beginning to set","sun is beginning to set","sunset","nightfall","good evening","tonight"),
            "afternoon":("good morning","sunrise","dawn"),
            "evening":("good morning","sunrise","dawn"),
            "night":("good morning","sunrise","dawn","sun is setting"),
        }
        return any(term in text for term in terms.get(str(daypart).lower(),()))

    def _dialogue_repeats_recent(self, dialogue, recent_summaries):
        """Detect near-verbatim conversational loops without treating shared topic words as repetition."""
        def norm(text):
            return " ".join(re.findall(r"[a-z0-9']+", (text or "").lower()))
        current=norm(dialogue)
        if not current:
            return False
        for item in recent_summaries or []:
            prior=norm(item.get("npc_reply_summary", "") if isinstance(item,dict) else str(item))
            if prior.startswith("npc replied "):
                prior=prior[len("npc replied "):]
            if not prior:
                continue
            if current == prior or (len(current) >= 28 and current in prior) or (len(prior) >= 28 and prior in current):
                return True
            if difflib.SequenceMatcher(None,current,prior).ratio() >= 0.78:
                return True
        return False

    def _parse_player_reply(self, npc_name, text):
        result={"raw":text,"dialogue":None,"social":None}
        lines=[line.strip() for line in (text or "").splitlines() if line.strip()]
        for line in lines:
            if line.lower().startswith(npc_name.lower()+":") and result["dialogue"] is None:
                candidate=line.split(":",1)[1].strip()
                if len(candidate)>=2 and candidate[0]==candidate[-1] and candidate[0] in ('"',"'"):
                    candidate=candidate[1:-1].strip()
                if candidate:
                    result["dialogue"]=candidate
            if line.upper().startswith("SOCIAL:"):
                raw=line.split(":",1)[1].strip()
                try:
                    meta=json.loads(raw)
                    if isinstance(meta,dict):
                        aff=int(meta.get("affinity",0)); trust=int(meta.get("trust",0)); fam=int(meta.get("familiarity",0))
                        tone=meta.get("tone",[]); memory=str(meta.get("memory","")).strip()[:180]
                        if -2<=aff<=2 and -2<=trust<=2 and 0<=fam<=2:
                            if not isinstance(tone,list): tone=[str(tone)]
                            result["social"]={"affinity":aff,"trust":trust,"familiarity":fam,
                                "tone":[str(x).strip()[:32] for x in tone[:3] if str(x).strip()],"memory":memory}
                except (ValueError,TypeError,json.JSONDecodeError):
                    pass
        # Degraded-but-usable dialogue recovery remains available, but diagnostics mark it as repaired.
        if result["dialogue"] is None and lines:
            first=lines[0]
            if not first.upper().startswith("SOCIAL:"):
                result["dialogue"]=first.split(":",1)[1].strip() if ":" in first else first
                result["format_repaired"]=True
        return result

    def ask_player_reply(self, npc_name, player_text, context):
        """One short foreground reply plus bounded social interpretation."""
        if not self.enabled:
            return None
        prompt=(
            f"You are {npc_name}, a resident of the fictional English village of Bellwether. "
            "Reply directly to CURRENT_PLAYER_MESSAGE in character. Keep the spoken reply to ONE short natural sentence, normally 4-18 words. "
            "Do not narrate your location, weather, posture, activity, biography, or internal state unless the player explicitly asks. "
            "Do not introduce yourself unless asked. Do not turn a greeting or weather remark into exposition. "
            "RECENT_CONVERSATION is a compact continuity summary, not text to copy. Continue naturally and do not repeat an earlier reply. "
            "DAYPART and WORLD_FACTS are authoritative. Do not invent plot facts, secrets, invitations, shared plans, objects, or off-screen events. "
            "Do not mention game systems or numeric relationship values. Output exactly two lines.\n"
            f"{npc_name}: <one short sentence>\n"
            'SOCIAL: {"affinity":0,"trust":0,"familiarity":0,"tone":["neutral"],"memory":"brief social meaning"}\n'
            "SOCIAL rules: judge only the current player message. Ordinary greetings, weather talk, and casual small talk normally give affinity 0, trust 0, familiarity 0 or 1. "
            "Use familiarity 2 only for a significant disclosure or consequential exchange. Memory must describe only the current player message.\n"
            f"CONTEXT: {json.dumps(context,separators=(',',':'))}\n"
            f"CURRENT_PLAYER_MESSAGE: {json.dumps((player_text or '')[:400])}\n"
            f"{npc_name}:"
        )
        timeout=float(os.getenv("BELLWETHER_PLAYER_CONVERSATION_TIMEOUT","75"))
        text=self._plain_request("player_conversation",prompt,max_tokens=48,temperature=.58,no_think=True,
            tries_override=2,foreground=True,timeout_override=timeout)
        if not text:
            return None
        result=self._parse_player_reply(npc_name,text)
        dialogue=result.get("dialogue")
        contradiction=dialogue and self._obvious_daypart_contradiction(dialogue,context.get("daypart"))
        repeated=dialogue and self._dialogue_repeats_recent(dialogue,context.get("recent_conversation",[]))
        if contradiction or repeated:
            reason="repeated an earlier reply" if repeated else f"contradicted the {context.get('daypart')} daypart"
            correction=(prompt+f"\nCORRECTION: The previous answer {reason}. Give a fresh direct one-sentence reply to the CURRENT_PLAYER_MESSAGE. Do not reuse previous wording.\n{npc_name}:")
            retry=self._plain_request("player_conversation",correction,max_tokens=48,temperature=.64,no_think=True,
                tries_override=1,foreground=True,timeout_override=timeout)
            if retry:
                candidate=self._parse_player_reply(npc_name,retry)
                if candidate.get("dialogue") and not self._dialogue_repeats_recent(candidate["dialogue"],context.get("recent_conversation",[])):
                    result=candidate; dialogue=result.get("dialogue")
                    result["repetition_repaired"]=bool(repeated)
        if result.get("dialogue"):
            # Hard display/storage bound: one line and at most 24 words. Prefer sentence boundary.
            d=" ".join(result["dialogue"].split())
            sentence=re.split(r"(?<=[.!?])\s+",d)[0]
            words=sentence.split()
            if len(words)>24: sentence=" ".join(words[:24]).rstrip(",;:")+"…"
            result["dialogue"]=sentence
            repaired=bool(result.get("format_repaired") or result.get("repetition_repaired"))
            self._annotate_last_trace(parser_stage="player_reply_repaired" if repaired else "player_reply_received",
                parser_detail="Foreground reply accepted after validation." if not repaired else "Foreground reply accepted after bounded repair.",
                result="accepted_player_reply_repaired" if repaired else "accepted_player_reply")
            self.remember_call("player_conversation",{"type":"conversation","text":result["dialogue"][:180],"social":result.get("social")})
            return result
        return None

    def ask_text(self,director,instruction,context,max_tokens=220):
        """Free natural-language generation for dialogue and expressive content."""
        if not self.enabled:return None
        context = self._context_with_overview(context, director)
        prompt=(
            "Write natural in-world text for Bellwether, a cozy village RPG that gradually "
            "develops psychological supernatural horror. Stay grounded in the supplied context. "
            "Do not mention AI, prompts, game mechanics, or state variables. "
            f"\nTASK: {instruction}\nCONTEXT: {json.dumps(context,separators=(',',':'))}\nTEXT:"
        )
        # Ambient dialogue is latency-sensitive; direct generation is preferable to hidden reasoning.
        is_foreground=(director == "player_conversation")
        foreground_timeout=float(os.getenv("BELLWETHER_PLAYER_CONVERSATION_TIMEOUT","45"))
        text=self._plain_request(
            director,prompt,max_tokens=max_tokens,temperature=.72,no_think=True,
            tries_override=2 if is_foreground else 1,
            foreground=is_foreground,
            timeout_override=foreground_timeout if is_foreground else None
        )
        if text:
            self._annotate_last_trace(
                parser_stage="free_text_accepted",
                parser_detail="Non-empty generative dialogue accepted as expressive content.",
                result="accepted_free_text"
            )
            self.remember_call(director, {"type":"text","text":text[:240]})
        return text

provider=AIProvider()
