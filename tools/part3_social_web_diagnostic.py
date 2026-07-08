#!/usr/bin/env python3
"""Focused Part 3 social-web checks; deterministic and Ollama-free."""
import copy, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); os.environ["BELLWETHER_AI"]="0"
from backend.core.social_model import SOCIAL_MODEL
from backend.core.game import Game

def main():
    checks=[]
    def ok(name,cond):
        assert cond; checks.append(name); print("PASS",name)
    ok("social schema validates",SOCIAL_MODEL.validate())
    ok("complete core cast graph",set(SOCIAL_MODEL.edges)=={"jonah|mara","jonah|mrs_ellis","mara|mrs_ellis"})
    ok("authored edge query",SOCIAL_MODEL.authored_edge("mara","jonah")["history"]!="")
    g=Game(); before=copy.deepcopy(g.state["npc_social_web"])
    g.state["npcs"]["jonah"].update(location="village_green",visible=True,activity="serving neighbours")
    g.state["npcs"]["mrs_ellis"].update(location="village_green",visible=True,activity="morning errand")
    g.update_npc_social_web(); edge=g.state["npc_social_web"]["jonah|mrs_ellis"]
    ok("co-location creates autonomous encounter",edge["encounter_count"]==before["jonah|mrs_ellis"]["encounter_count"]+1)
    count=edge["encounter_count"]; g.update_npc_social_web(); ok("encounter cooldown prevents pulse inflation",edge["encounter_count"]==count)
    ok("bounded relationship effect",edge["state"]["familiarity"]==before["jonah|mrs_ellis"]["state"]["familiarity"]+1)
    canon=SOCIAL_MODEL.authored_edge("jonah","mrs_ellis"); edge["state"]["trust"]=-50; ok("runtime cannot mutate authored social canon",SOCIAL_MODEL.authored_edge("jonah","mrs_ellis")==canon)
    ok("bounded topic sharing hook",g.share_npc_topic("jonah","mara","bakery_delivery_delay") and "bakery_delivery_delay" in g.state["npc_social_web"]["jonah|mara"]["shared_topics"])
    old=copy.deepcopy(g.state); old.pop("npc_social_web",None); g.state=old; g.migrate_state(); ok("old-save social-web migration",set(g.state["npc_social_web"])==set(SOCIAL_MODEL.edges))
    ctx=g.npc_social_context("mara"); ok("director dialogue social context available",set(ctx)=={"jonah","mrs_ellis"})
    print(f"Part 3 passes: {len(checks)}/{len(checks)}"); return 0
if __name__=="__main__": raise SystemExit(main())
