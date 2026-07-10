from backend.core.game import Game
from backend.core.dialogue_expression_model import DIALOGUE_EXPRESSION_MODEL,VOICE
from backend.core.npc_model import NPC_MODEL

def main():
 g=Game(); checks=[]
 def c(n,x): checks.append((n,bool(x)))
 c('version',open('VERSION').read().strip()=='3.0.0-rc3')
 c('authored_voice_profiles',all(x in VOICE for x in ('jonah','mara','mrs_ellis')))
 c('distinct_cadence',len({VOICE[x]['cadence'] for x in VOICE})==len(VOICE))
 c('identity_preserved',all(NPC_MODEL.dialogue_identity(x).get('social_style') for x in VOICE))
 for nid in VOICE:
  ctx=DIALOGUE_EXPRESSION_MODEL.context(g.state,nid)
  c('context_'+nid,bool(ctx['voice']['cadence']) and 'recent_life_events' in ctx)
 src=open('backend/core/game.py').read(); prov=open('backend/ai/provider.py').read(); amb=open('backend/ai/specific_directors.py').read()
 c('foreground_context_wired','"dialogue_expression": DIALOGUE_EXPRESSION_MODEL.context' in src)
 c('social_web_wired','"npc_social_web": self.npc_social_context' in src)
 c('knowledge_wired','"npc_knowledge": self.npc_knowledge_context' in src)
 c('provider_voice_instruction','recognizably theirs' in prov)
 c('ambient_identity_wired','character_context' in amb and 'recognizably distinct' in amb)
 for n,ok in checks: print(('PASS' if ok else 'FAIL'),n)
 print(f'{sum(x for _,x in checks)}/{len(checks)} PASS')
 raise SystemExit(0 if all(x for _,x in checks) else 1)
if __name__=='__main__': main()
