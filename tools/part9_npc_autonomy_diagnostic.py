#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ["BELLWETHER_AI"]="0"
from backend.core.game import Game
from backend.core.purpose_model import PURPOSE_MODEL
from backend.ai.specific_directors import npc_candidates, _npc_transition_candidates

passes=0
def check(name, cond):
 global passes
 if not cond: raise AssertionError(name)
 passes+=1; print('PASS',name)

g=Game(); s=g.state
check('purpose model available', PURPOSE_MODEL is not None)
# Jonah during bakery obligation should rank bakery work strongly.
s['minute']=600
j=s['npcs']['jonah']; cand=_npc_transition_candidates(j,npc_candidates('jonah',j,s))
ranked=PURPOSE_MODEL.rank_candidates('jonah',cand,s)
check('obligation influences ranking', any('obligation:bakery_morning' in r['purpose_score']['reasons'] for r in ranked[:5]))
check('ranking remains authored and bounded', all(r['id'] in {c['id'] for c in cand} for r in ranked))
# High social need should favour social action over otherwise neutral continuation.
s['npc_lives']['mara']['needs']['social']=100
m=s['npcs']['mara']; mc=_npc_transition_candidates(m,npc_candidates('mara',m,s)); mr=PURPOSE_MODEL.rank_candidates('mara',mc,s)
check('runtime need influences purpose', any(r['kind']=='social' and 'need:social' in r['purpose_score']['reasons'] for r in mr[:8]))
# Avoided place penalty.
me=s['npcs']['mrs_ellis']; ec=_npc_transition_candidates(me,npc_candidates('mrs_ellis',me,s)); er=PURPOSE_MODEL.rank_candidates('mrs_ellis',ec,s)
rail=[r for r in er if r['destination']=='railway_halt']
check('place avoidance influences purpose', (not rail) or rail[0]['purpose_score']['score'] < max(x['purpose_score']['score'] for x in er))
# Weather dislike affects travel.
s['weather']['state']='heavy_rain'; er2=PURPOSE_MODEL.rank_candidates('mrs_ellis',ec,s)
check('weather influences movement purpose', any('weather_dislike' in r['purpose_score']['reasons'] for r in er2 if r['destination']!=me['location']))
# Closed shop receives hard penalty.
s['minute']=120
cand2=[{'id':'shop','label':'shop','activity':'shopping','destination':'village_shop','kind':'errand'}]
sc=PURPOSE_MODEL.score_candidate('mrs_ellis',cand2[0],s)
check('opening hours constrain purpose', 'closed' in sc['reasons'] and sc['score'] < 0)
# Context exposes bounded ranked reasons.
ctx=PURPOSE_MODEL.context('jonah',s,cand)
check('director purpose context bounded', len(ctx.get('ranked_options',[]))<=6 and 'dominant_need' in ctx)
# Runtime state changes ranking without mutating authored canon.
before=deepcopy(PURPOSE_MODEL.context('mara',s,mc)); s['npc_lives']['mara']['needs']['rest']=100; after=PURPOSE_MODEL.context('mara',s,mc)
check('runtime purpose state is reactive', before['dominant_need']!=after['dominant_need'] or after['dominant_need']=='rest')
check('authored npc canon remains isolated', PURPOSE_MODEL is not None and 'current_intent' not in __import__('backend.core.npc_model',fromlist=['NPC_MODEL']).NPC_MODEL.npcs['mara'])
# Existing topology remains authoritative.
short=PURPOSE_MODEL.shortlist('jonah',cand,s)
allowed={j['location']} | __import__('backend.core.world_model',fromlist=['WORLD_MODEL']).WORLD_MODEL.npc_neighbors(j['location'])
check('purpose cannot bypass topology', all(c['destination'] in allowed for c in short))
print(f'Part 9 passes: {passes}/11')
