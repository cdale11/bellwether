"""Shared progressive-disclosure action grammar for human and AI players.

Classification is structural first. Text matching is a final fallback only, so an
interaction involving food cannot become a Food subcategory and animal care does
not collapse into generic ordinary life.
"""
CATEGORY_ORDER=("people","work","home","explore","investigate","travel")
LABELS={"people":"People","work":"Work & Trade","home":"Home & Life","explore":"Explore","investigate":"Investigate","travel":"Travel"}

def classify(a):
 aid=str(a.get("id","")).lower(); kind=str(a.get("kind","")).lower(); explicit=str(a.get("category","")).lower()
 if explicit in CATEGORY_ORDER:return explicit
 if kind in {"talk","free_talk","choice","social"} or aid.startswith(("social:","society:greet:")):return "people"
 if kind in {"job","economy"} or aid.startswith(("job:","economy:")):return "work"
 if kind=="travel" or aid.startswith(("travel:","move:")):return "travel"
 if kind=="investigate" or aid.startswith("investigate:"):return "investigate"
 if kind=="observe" or aid in {"look","ask_village"}:return "explore"
 return "home"

def annotate(actions):
 return [{**a,"category":classify(a),"intent":_intent(a)} for a in actions]

def _intent(a):
 aid=str(a.get("id","")).lower();kind=str(a.get("kind","")).lower();text=aid+" "+str(a.get("label","")).lower()
 # Structural families outrank incidental words in labels.
 if kind in {"talk","free_talk","choice","social"} or aid.startswith(("social:","society:greet:")):return "conversation"
 prefix_intents=(("animals:buy", "animal_supplies"),("animals:build", "animal_shelter"),("animals:","animal_care"),("arc:","community_help"),("property:","property"),("business:","enterprise"),("transport:","transport"),("status:eat:","food"),("content:repair:","maintenance"),("recover:","recovery"),("ending:","story"))
 for prefix,intent in prefix_intents:
  if aid.startswith(prefix):return intent
 if aid in {"sleep","rest"}:return "rest"
 if aid in {"read_letter","new_run"} or kind=="story":return "story"
 for intent,words in (("employment",("job","shift","employment")),("food",("food","breakfast","loaf","cook","meal","eat")),("garden",("garden","plant","water","weed","harvest","soil")),("maintenance",("repair","tidy","weatherproof","cottage")),("observation",("look","watch","observe","listen","study","examine")),("movement",("travel","visit","return","walk toward"))):
  if any(w in text for w in words):return intent
 return "ordinary_life"

def compact(actions,limit_per_category=8):
 seen=set();buckets={k:[] for k in CATEGORY_ORDER}
 for a in annotate(actions):
  key=(a.get("category"),a.get("intent"),str(a.get("label","")).lower())
  if key in seen:continue
  seen.add(key);buckets.setdefault(a["category"],[]).append(a)
 out=[]
 for cat in CATEGORY_ORDER:
  xs=buckets.get(cat,[])
  xs.sort(key=lambda a:(0 if str(a.get("id",""))=="sleep" else 1,a.get("intent") in {"observation","ordinary_life"},a.get("label","")))
  out.extend(xs[:limit_per_category])
 return out
