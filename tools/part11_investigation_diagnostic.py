#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game,INITIAL_STATE
from backend.core.investigation_model import INVESTIGATION_MODEL
def check(n,c): print(("PASS " if c else "FAIL ")+n); return bool(c)
g=Game();g.state=deepcopy(INITIAL_STATE);g.migrate_state();r=[]
r.append(check("mystery schema validates",INVESTIGATION_MODEL.validate()))
g.record_evidence("green_worn_paths","Paths","Observed paths",location="village_green")
r.append(check("evidence enters investigation graph","green_worn_paths" in g.state["mystery_investigation"]["observations"]))
r.append(check("evidence links to bounded mystery","green_worn_paths" in g.state["mystery_investigation"]["mystery_progress"]["village_routines"]["evidence"]))
r.append(check("eligible hypothesis emerges from support",any(x[0]=="routines_carry_information" for x in INVESTIGATION_MODEL.eligible_hypotheses(g.state["mystery_investigation"]))))
a=g.assess_hypothesis("routines_carry_information");r.append(check("hypothesis initially tentative",a and a["status"]=="tentative"))
g.record_evidence("bakery_regulars","Regulars","Orders anticipated",location="bakery");g.record_testimony("jonah","bakery_morning_rhythm");a=g.assess_hypothesis("routines_carry_information")
r.append(check("independent support can strengthen hypothesis",a and a["status"]=="supported" and a["support_count"]>=3))
r.append(check("unknown hypothesis rejected",g.assess_hypothesis("invented_llm_theory") is None))
r.append(check("unknown testimony fact rejected",not g.record_testimony("jonah","invented_fact")))
# bounded conflicting testimony
g.learn_npc_fact("mara","railway_halt_avoided",.7);g.state["npc_knowledge"]["npcs"]["mara"]["beliefs"]["railway_halt_avoided"]["variant"]="distortion:0";g.record_testimony("mrs_ellis","railway_halt_avoided");g.record_testimony("mara","railway_halt_avoided")
r.append(check("conflicting testimony creates contradiction",any(x["fact_id"]=="railway_halt_avoided" for x in g.state["mystery_investigation"]["contradictions"])))
r.append(check("testimony remains distinct from observation","railway_halt_avoided" not in g.state["mystery_investigation"]["observations"]))
old=deepcopy(INITIAL_STATE);old.pop("mystery_investigation",None);g2=Game();g2.state=old;g2.migrate_state();r.append(check("old-save investigation migration","mystery_investigation" in g2.state and "mystery_progress" in g2.state["mystery_investigation"]))
before=deepcopy(INVESTIGATION_MODEL.data);g.assess_hypothesis("routines_carry_information");r.append(check("runtime cannot mutate authored mystery canon",before==INVESTIGATION_MODEL.data))
print(f"Part 11 passes: {sum(r)}/{len(r)}");raise SystemExit(0 if all(r) else 1)
