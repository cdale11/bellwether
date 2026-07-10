"""v2.0 shared progressive-disclosure action grammar for human and AI players."""

CATEGORY_ORDER=("people","work","home","explore","investigate","travel")
LABELS={"people":"People","work":"Work & Trade","home":"Home & Life","explore":"Explore","investigate":"Investigate","travel":"Travel"}

def classify(a):
 aid=str(a.get("id","")).lower(); kind=str(a.get("kind","")).lower(); text=(aid+" "+str(a.get("label","")).lower())
 if kind in {"talk","free_talk","choice","social"} or aid.startswith("society:greet:"): return "people"
 if kind in {"job","economy"} or aid.startswith(("job:","economy:")): return "work"
 if kind=="travel" or aid.startswith("travel:"): return "travel"
 if kind=="investigate" or aid.startswith("investigate:"): return "investigate"
 if kind=="observe" or any(x in text for x in ("walk","watch","look around","listen","study")): return "explore"
 return "home"

def annotate(actions):
 out=[]
 for a in actions:
  b=dict(a); b["category"]=classify(b); b["intent"]=_intent(b); out.append(b)
 return out

def _intent(a):
 aid=str(a.get("id","")).lower(); kind=str(a.get("kind","")).lower(); text=(aid+" "+str(a.get("label","")).lower())
 # Structural interaction kind outranks incidental subject words (for example a shared meal).
 if kind in {"talk","free_talk","choice","social"} or aid.startswith("society:greet:"): return "conversation"
 for intent,words in (("conversation",("talk","speak","few words")),("employment",("job","shift","work")),("food",("food","breakfast","loaf","cook","meal","eat")),("garden",("garden","plant","water","weed","harvest","soil")),("maintenance",("repair","tidy","cottage")),("observation",("look","watch","observe","listen","study")),("movement",("travel","visit","return","walk toward"))):
  if any(w in text for w in words): return intent
 return "ordinary_life"

def compact(actions,limit_per_category=8):
 """Same bounded surface used by UI and AI; preserve urgent/story choices and remove exact semantic duplicates."""
 seen=set(); buckets={k:[] for k in CATEGORY_ORDER}
 for a in annotate(actions):
  key=(a.get("category"),a.get("intent"),str(a.get("label","")).lower())
  if key in seen: continue
  seen.add(key); buckets.setdefault(a["category"],[]).append(a)
 out=[]
 for cat in CATEGORY_ORDER:
  xs=buckets.get(cat,[])
  # Passive observation is useful but should not crowd out consequential choices.
  xs.sort(key=lambda a:(0 if str(a.get("id",""))=="sleep" else 1, a.get("intent") in {"observation","ordinary_life"}, a.get("label","")))
  out.extend(xs[:limit_per_category])
 return out
