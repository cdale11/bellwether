#!/usr/bin/env python3
from copy import deepcopy
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game,INITIAL_STATE
from backend.core.player_identity_model import PLAYER_IDENTITY_MODEL
def check(n,c): print(('PASS ' if c else 'FAIL ')+n); return bool(c)
g=Game();g.state=deepcopy(INITIAL_STATE);g.migrate_state();r=[]
r.append(check('identity schema present','player_identity' in g.state and set(PLAYER_IDENTITY_MODEL.TRAITS)<=set(g.state['player_identity']['traits'])))
r.append(check('fresh identity is unformed',PLAYER_IDENTITY_MODEL.refresh(g.state)['coping_style']=='unformed'))
# care pattern
g.state['branch_state']['care']=8; g.state['player_life']['activity_history']=[{'activity':'tidy'} for _ in range(8)]
rt=PLAYER_IDENTITY_MODEL.refresh(g.state,'diagnostic_care');r.append(check('repeated behaviour shapes identity',rt['traits']['care']>=45 and 'care' in rt['dominant_traits']))
# inquiry + horror changes coping
g.state['branch_state']['inquiry']=10;g.state['investigation']['evidence']=[{} for _ in range(7)];g.state['systemic_horror']['experienced']=['x']
rt=PLAYER_IDENTITY_MODEL.refresh(g.state,'diagnostic_horror');r.append(check('investigation and exposure shape coping',rt['coping_style']=='pattern_seeking'))
r.append(check('meaningful identity evolution is recorded',len(rt['evolution_history'])>=1))
ctx=PLAYER_IDENTITY_MODEL.public_context(g.state);r.append(check('bounded public identity context',ctx['coping_style']=='pattern_seeking' and 'trait_levels' in ctx))
# social town reaction
g.state['relationships']['jonah'].update({'talks':4,'trust':3});g.state['relationships']['mara'].update({'talks':3,'trust':2})
rt=PLAYER_IDENTITY_MODEL.refresh(g.state,'diagnostic_social');r.append(check('town read responds to social history',rt['town_read']=='known_neighbor'))
# dialogue integration without calling model: inspect source
src=(ROOT/'backend/core/game.py').read_text();r.append(check('dialogue receives evolving identity','player_evolving_identity' in src and 'PLAYER_IDENTITY_MODEL.public_context(s)' in src))
old=deepcopy(INITIAL_STATE);old.pop('player_identity',None);g2=Game();g2.state=old;g2.migrate_state();r.append(check('old-save identity migration','player_identity' in g2.state))
# derived layer cannot mutate source history
before=deepcopy(g.state['player_life']['activity_history']);PLAYER_IDENTITY_MODEL.refresh(g.state);r.append(check('identity derivation does not mutate behaviour history',before==g.state['player_life']['activity_history']))
# persistence round trip shape
snap=deepcopy(g.state['player_identity']);g3=Game();g3.state=deepcopy(g.state);g3.migrate_state();r.append(check('identity state persists across state round trip',g3.state['player_identity']==snap))
print(f'Part 13 passes: {sum(r)}/{len(r)}');raise SystemExit(0 if all(r) else 1)
