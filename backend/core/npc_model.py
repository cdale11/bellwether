"""Part 2 NPC identity and personal-life substrate.

Authored identity is immutable catalogue data. Runtime personal-life state is
save-persistent and intentionally separate from canon and conversation memory.
"""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NPC_DATA_PATH = ROOT / "content" / "npcs" / "core_cast.json"

class NPCModel:
    REQUIRED = {"name","tier","pronouns","age_band","public_role","home_location","work_locations","identity","preferences","needs","obligations","personal_threads"}
    NEED_KEYS = {"rest","food","social","purpose","security"}

    def __init__(self, path=NPC_DATA_PATH):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8"))
        self.schema_version = int(self.data.get("schema_version", 1))
        self.npcs = self.data["npcs"]
        self.validate()

    def validate(self):
        errors=[]
        for npc_id, npc in self.npcs.items():
            missing=self.REQUIRED-set(npc)
            if missing: errors.append(f"{npc_id}: missing {sorted(missing)}")
            if set(npc.get("needs",{})) != self.NEED_KEYS: errors.append(f"{npc_id}: needs must be {sorted(self.NEED_KEYS)}")
            for key,val in npc.get("needs",{}).items():
                if not isinstance(val,(int,float)) or not 0 <= val <= 100: errors.append(f"{npc_id}: invalid need {key}={val}")
            ident=npc.get("identity",{})
            for key in ("values","dislikes","social_style","private_tension"):
                if key not in ident: errors.append(f"{npc_id}: identity missing {key}")
        if errors: raise ValueError("Invalid NPC data: " + "; ".join(errors))
        return True

    def profile(self, npc_id): return deepcopy(self.npcs[npc_id])
    def public_identity(self, npc_id):
        n=self.npcs[npc_id]
        return {k:deepcopy(n[k]) for k in ("name","tier","pronouns","age_band","public_role")}
    def dialogue_identity(self, npc_id): return deepcopy(self.npcs[npc_id]["identity"])
    def runtime_defaults(self):
        return {npc_id:{
            "schema_version":self.schema_version,
            "needs":deepcopy(npc["needs"]),
            "current_intent":None,
            "intent_history":[],
            "personal_thread_state":{t["id"]:t["state"] for t in npc["personal_threads"]},
            "daily_experiences":[],
            "last_need_update_minute":None
        } for npc_id,npc in self.npcs.items()}

    def active_obligations(self, npc_id, minute):
        tod=minute%1440
        return [deepcopy(o) for o in self.npcs[npc_id]["obligations"] if o["start_minute"] <= tod < o["end_minute"]]

    def purpose_context(self, npc_id, minute, weather_state):
        n=self.npcs[npc_id]
        needs=n["needs"]
        runtime={"dominant_authored_need":max(needs,key=needs.get),"active_obligations":self.active_obligations(npc_id,minute)}
        prefs=n["preferences"]
        runtime["weather_preference"] = "likes" if weather_state in prefs["weather_likes"] else "dislikes" if weather_state in prefs["weather_dislikes"] else "neutral"
        return runtime

NPC_MODEL = NPCModel()
