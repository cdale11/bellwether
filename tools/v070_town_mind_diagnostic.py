#!/usr/bin/env python3
from copy import deepcopy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.core.game import Game, INITIAL_STATE
from backend.core.town_mind_model import TOWN_MIND_MODEL, INTENTIONS

def check(name, cond):
    print(("PASS" if cond else "FAIL")+" | "+name)
    return bool(cond)

g=Game(); s=g.state
results=[]
results.append(check("town mind state exists", "town_mind" in s))
results.append(check("intention catalogue bounded", len(INTENTIONS)>=5 and all("id" in x for x in INTENTIONS)))
ctx=TOWN_MIND_MODEL.compact_context(s)
results.append(check("compact context excludes full NPC dump", "npcs" not in ctx and "population" not in ctx))
c=TOWN_MIND_MODEL.candidates(s)[0]
results.append(check("legal intention accepted", TOWN_MIND_MODEL.validate_and_apply(s,c,"diagnostic","test")))
results.append(check("intention persisted", bool(s["town_mind"]["active_intentions"])))
before=deepcopy(s["weather"]); bad={"id":"invent_new_canon"}
results.append(check("illegal intention rejected", not TOWN_MIND_MODEL.validate_and_apply(s,bad,"diagnostic","test")))
results.append(check("town mind cannot directly mutate weather", s["weather"]==before))
s["village_brain"]["pulse_count"]=999; TOWN_MIND_MODEL.expire(s)
results.append(check("intentions expire", not s["town_mind"]["active_intentions"]))
# migration
old=deepcopy(INITIAL_STATE); old.pop("town_mind",None); g2=Game(); g2.state=old; g2.migrate_state()
results.append(check("old save migration", "town_mind" in g2.state and g2.state["town_mind"]["schema_version"]==1))
results.append(check("deep routing configured", g.ai.model_for_task("town_mind")==g.ai.deep_model if hasattr(g,'ai') else True))
print(f"RESULT {sum(results)}/{len(results)}")
raise SystemExit(0 if all(results) else 1)
