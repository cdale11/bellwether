"""RC3 bounded dialogue-expression context.

Provides authored voice constraints and compact live-life hooks to generative dialogue.
It never generates canon, changes relationships, or mutates story state.
"""
from copy import deepcopy

VOICE = {
    "jonah": {"cadence":"plain, warm, practical; occasional light humour; rarely abstract",
              "habits":["answers the question before adding context","uses work and bread imagery sparingly, not every reply","understates his own strain"],
              "avoid":["mystical certainty","flowery speeches","constant reassurance"]},
    "mara": {"cadence":"concise, observant, practical; dry kindness; comfortable with silence",
             "habits":["notices concrete details","offers help through actions more readily than declarations","does not over-explain concern"],
             "avoid":["effusive sentiment","instant intimacy","vague motivational language"]},
    "mrs_ellis": {"cadence":"measured, courteous, precise; gently probing without becoming cryptic",
                  "habits":["distinguishes recollection from fact","asks careful follow-up questions","uses local history only when relevant"],
                  "avoid":["constant ominous hints","premature mystery exposition","generic grandmotherly clichés"]},
}

class DialogueExpressionModel:
    def context(self,state,npc_id):
        spec=deepcopy(VOICE.get(npc_id,{"cadence":"grounded and natural","habits":[],"avoid":["generic exposition"]}))
        life=state.get("npc_autonomous_life",{}).get("core",{}).get(npc_id,{})
        npc_life=state.get("npc_lives",{}).get(npc_id,{})
        recent=[]
        for event in state.get("npc_autonomous_life",{}).get("event_history",[])[-20:]:
            if npc_id in event.get("actors",[]) or event.get("npc_id")==npc_id:
                recent.append({k:event.get(k) for k in ("day","type","summary") if event.get(k) is not None})
        needs=npc_life.get("needs",{})
        dominant=max(needs,key=needs.get) if needs else None
        return {"voice":spec,"current_personal_goal":life.get("active_goal") or life.get("goal"),
                "goal_progress":life.get("progress"),"dominant_need":dominant,
                "recent_life_events":recent[-3:],
                "rule":"Use these as subtext when relevant. Do not force them into every reply or invent developments."}

DIALOGUE_EXPRESSION_MODEL=DialogueExpressionModel()
