#!/usr/bin/env python3
from backend.core.game import Game, WORLD
from backend.core.travel_model import TRAVEL_MODEL
from backend.ai.provider import AIProvider
checks=[]
def check(name, ok): checks.append((name,bool(ok))); print(('PASS' if ok else 'FAIL'), name)

g=Game(); s=g.state
check('travel state exists', 'travel' in s)
plan=TRAVEL_MODEL.plan(s,'bus_stop','village_road',WORLD)
check('journey plan positive', plan['minutes'] >= 5)
# direct move through public perform path
before=s['travel']['total_journeys']; g.perform('move:village_road')
check('journey count increments', s['travel']['total_journeys']==before+1)
key=TRAVEL_MODEL.route_key('bus_stop','village_road')
check('route familiarity persists', s['travel']['routes'][key]['familiarity']==1)
check('first observation recorded', s['travel']['routes'][key]['first_observation_seen'])
check('journey log recorded', bool(s['travel']['journey_log']))
# repeated travel should not be slower in identical conditions
s['location']='bus_stop'; p1=TRAVEL_MODEL.plan(s,'bus_stop','village_road',WORLD)
s['travel']['routes'][key]['familiarity']=10; p2=TRAVEL_MODEL.plan(s,'bus_stop','village_road',WORLD)
check('familiar route is faster or equal', p2['minutes'] <= p1['minutes'])
# bad weather slows exposed route
s['weather']['state']='clear'; clear=TRAVEL_MODEL.plan(s,'field_lane','calder_farm',WORLD)['minutes']
s['weather']['state']='heavy_rain'; wet=TRAVEL_MODEL.plan(s,'field_lane','calder_farm',WORLD)['minutes']
check('weather affects travel time', wet > clear)
# migration
old={'location':'bus_stop'}; TRAVEL_MODEL.migrate(old)
check('old state migration', 'travel' in old and old['travel']['schema_version']==1)
# all-thread default
p=AIProvider()
try:
    import os
    expected=len(os.sched_getaffinity(0))
except (AttributeError,OSError):
    import os
    expected=os.cpu_count() or 1
check('AI defaults to all available CPU threads', p.num_threads==expected)
check('task routing preserved', p.model_for_task('town_mind')==p.deep_model and p.model_for_task('conversation')==p.fast_model)
print(f'v0.6.1 travel/journey diagnostic: {sum(v for _,v in checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(v for _,v in checks) else 1)
