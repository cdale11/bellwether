from copy import deepcopy
from backend.core.game import Game, INITIAL_STATE
from backend.core.relationship_life_model import RELATIONSHIP_LIFE_MODEL
checks=[]
def ck(n,v): checks.append((n,bool(v))); print(('PASS' if v else 'FAIL'),n)
g=Game(); g.state=deepcopy(INITIAL_STATE); g.migrate_state(); s=g.state
ck('migration', 'relationship_life' in s)
# make Mara available and close, then exercise authored route
s['flags']['met_mara']=True;s['npcs']['mara']['visible']=True;s['npcs']['mara']['location']='ashcroft_cottage';s['location']='ashcroft_cottage';s['relationships']['mara'].update({'affinity':30,'trust':30,'familiarity':40})
acts=dict(RELATIONSHIP_LIFE_MODEL.actions(s));ck('interest_exposed','relationship:interest:mara' in acts)
ok,_,_=RELATIONSHIP_LIFE_MODEL.perform(s,'relationship:interest:mara');ck('courtship',ok and s['relationship_life']['routes']['mara']['stage']=='courting')
s['location']='riverside_path'
for _ in range(2): ck('date',RELATIONSHIP_LIFE_MODEL.perform(s,'relationship:date:mara')[0])
s['location']='ashcroft_cottage';s['npcs']['mara']['location']='ashcroft_cottage';s['relationships']['mara']['trust']=35
ck('commit',RELATIONSHIP_LIFE_MODEL.perform(s,'relationship:commit:mara')[0] and s['relationship_life']['partner']=='mara')
s.setdefault('property',{}).setdefault('cottage_expansion',{})['completed']=['pantry_room','work_room','upper_room']
ck('cohabit',RELATIONSHIP_LIFE_MODEL.perform(s,'relationship:cohabit')[0] and s['relationship_life']['cohabiting'])
ck('family_talk',RELATIONSHIP_LIFE_MODEL.perform(s,'relationship:family_talk')[0] and s['relationship_life']['family_intent']=='open_to_future')
before=s['relationship_life']['routes']['mara']['shared_days'];s['day']+=1;RELATIONSHIP_LIFE_MODEL.daily_tick(s);ck('daily_progress',s['relationship_life']['routes']['mara']['shared_days']==before+1)
ck('public_surface',RELATIONSHIP_LIFE_MODEL.public(s)['partner']=='mara')
ck('authored_routes_only',set(s['relationship_life']['routes'])=={'jonah','mara'})
raise SystemExit(0 if all(v for _,v in checks) else 1)
