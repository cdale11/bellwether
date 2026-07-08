"""Part 9 bounded purpose-driven NPC behaviour.

Scores authored candidate actions against runtime needs, obligations, identity,
weather, relationships, events, opening hours and location suitability. It never
creates destinations or actions; it only ranks candidates already authored and
validated by the movement topology.
"""
from copy import deepcopy
from backend.core.npc_model import NPC_MODEL
from backend.core.world_model import WORLD_MODEL

NEED_KIND = {"rest":"rest", "food":"errand", "social":"social", "purpose":"work", "security":"routine"}

class PurposeModel:
    def dominant_need(self, npc_id, state):
        rt=state.get("npc_lives",{}).get(npc_id,{})
        needs=rt.get("needs", NPC_MODEL.npcs[npc_id]["needs"])
        return max(needs, key=needs.get), float(max(needs.values()))

    def score_candidate(self, npc_id, candidate, state):
        npc=NPC_MODEL.npcs[npc_id]; score=0.0; reasons=[]
        kind=candidate.get("kind","routine"); dest=candidate.get("destination")
        minute=int(state.get("minute",0)); weather=state.get("weather",{}).get("state")
        need,value=self.dominant_need(npc_id,state)
        if NEED_KIND.get(need)==kind:
            score += 3.0 + value/40.0; reasons.append(f"need:{need}")
        obligations=NPC_MODEL.active_obligations(npc_id,minute)
        for ob in obligations:
            if dest in ob.get("locations",[]) and (kind==ob.get("purpose") or candidate.get("id")!="continue"):
                score += float(ob.get("priority",50))/10.0; reasons.append(f"obligation:{ob['id']}")
        prefs=npc.get("preferences",{})
        if dest in prefs.get("favoured_places",[]): score+=2.0; reasons.append("favoured_place")
        if dest in prefs.get("avoided_places",[]): score-=6.0; reasons.append("avoided_place")
        if weather in prefs.get("weather_likes",[]) and kind in ("rest","routine","social"): score+=1.0; reasons.append("weather_like")
        if weather in prefs.get("weather_dislikes",[]) and dest != state.get("npcs",{}).get(npc_id,{}).get("location"):
            score-=2.0; reasons.append("weather_dislike")
        if dest in WORLD_MODEL.locations:
            open_ok,_=WORLD_MODEL.access_status(dest,minute)
            if not open_ok and WORLD_MODEL.location(dest).get("access")=="opening_hours": score-=20.0; reasons.append("closed")
            suitability=WORLD_MODEL.suitability(dest,purpose=kind,role=npc.get("public_role"))
            score+=suitability["score"]*.5
            reasons += [f"world:{r}" for r in suitability["reasons"]]
        active_events=state.get("dynamic_events",{}).get("active",{})
        event_iter=active_events.values() if isinstance(active_events,dict) else active_events
        for ev in event_iter:
            if not isinstance(ev,dict): continue
            if dest in ev.get("affected_locations",[]) or dest==ev.get("location"):
                score+=1.0; reasons.append("active_event")
        return {"score":round(score,2),"reasons":reasons,"dominant_need":need}

    def rank_candidates(self,npc_id,candidates,state):
        ranked=[]
        for c in candidates:
            item=deepcopy(c); item["purpose_score"]=self.score_candidate(npc_id,c,state); ranked.append(item)
        return sorted(ranked,key=lambda x:x["purpose_score"]["score"],reverse=True)

    def shortlist(self,npc_id,candidates,state,limit=12):
        ranked=self.rank_candidates(npc_id,candidates,state)
        if not ranked: return []
        # Preserve bounded variety: strongest choices plus a few plausible alternatives.
        strong=ranked[:max(4,limit-2)]
        alternatives=[x for x in ranked[max(4,limit-2):] if x["purpose_score"]["score"]>-10][:2]
        return (strong+alternatives)[:limit]

    def context(self,npc_id,state,candidates=None):
        need,value=self.dominant_need(npc_id,state)
        obligations=NPC_MODEL.active_obligations(npc_id,int(state.get("minute",0)))
        out={"dominant_need":need,"dominant_need_value":value,"active_obligations":deepcopy(obligations)}
        if candidates is not None:
            out["ranked_options"]=[{"id":c.get("id"),"score":c["purpose_score"]["score"],"reasons":c["purpose_score"]["reasons"]} for c in self.rank_candidates(npc_id,candidates,state)[:6]]
        return out

PURPOSE_MODEL=PurposeModel()
