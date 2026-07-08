#!/usr/bin/env python3
"""Focused Part 2 identity/personal-life checks; deterministic and Ollama-free."""
import copy, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); os.environ["BELLWETHER_AI"]="0"
from backend.core.npc_model import NPC_MODEL
from backend.core.game import Game

def main():
    checks=[]
    def check(name,fn): fn(); checks.append(name); print("PASS",name)
    check("npc schema validates",NPC_MODEL.validate)
    check("core cast profiles present",lambda: set(NPC_MODEL.npcs)=={"jonah","mara","mrs_ellis"} or (_ for _ in ()).throw(AssertionError()))
    check("authored identity query",lambda: "craft" in NPC_MODEL.dialogue_identity("jonah")["values"] or (_ for _ in ()).throw(AssertionError()))
    check("bounded obligation query",lambda: bool(NPC_MODEL.active_obligations("jonah",600)) or (_ for _ in ()).throw(AssertionError()))
    g=Game(); before=copy.deepcopy(g.state["npc_lives"]); g.advance(60)
    assert g.state["npc_lives"]["jonah"]["needs"] != before["jonah"]["needs"]
    checks.append("personal needs evolve with game time"); print("PASS personal needs evolve with game time")
    ctx=g.npc_life_context("mara"); assert "runtime" in ctx and "authored_constraints" in ctx
    checks.append("dialogue life context available"); print("PASS dialogue life context available")
    old=copy.deepcopy(g.state); old.pop("npc_lives",None); g.state=old; g.migrate_state()
    assert set(g.state["npc_lives"]) >= set(NPC_MODEL.npcs)
    checks.append("old-save npc-life migration"); print("PASS old-save npc-life migration")
    canon=NPC_MODEL.profile("mrs_ellis"); g.state["npc_lives"]["mrs_ellis"]["needs"]["social"]=99
    assert NPC_MODEL.profile("mrs_ellis")==canon
    checks.append("runtime state cannot mutate authored identity"); print("PASS runtime state cannot mutate authored identity")
    assert g._npc_social_personality("jonah")["style"]==NPC_MODEL.dialogue_identity("jonah")["social_style"]
    checks.append("conversation identity integration"); print("PASS conversation identity integration")
    print(f"Part 2 passes: {len(checks)}/{len(checks)}"); return 0
if __name__=="__main__": raise SystemExit(main())
