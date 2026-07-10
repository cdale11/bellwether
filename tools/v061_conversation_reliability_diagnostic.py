from backend.ai.provider import AIProvider
from backend.core.game import Game

checks=[]
def check(name, ok, detail=''):
    checks.append(bool(ok)); print(('PASS' if ok else 'FAIL'), name, detail)

p=AIProvider(); p.enabled=True
calls=[]
responses=[
    'Mrs Ellis: Good morning to you.\nSOCIAL: {"affinity":0,"trust":0,"familiarity":1,"tone":["neutral"],"memory":"The player greeted Mrs Ellis."}',
]
def fake(*args, **kwargs):
    calls.append((args,kwargs)); return responses.pop(0)
p._plain_request=fake
ctx={'daypart':'morning','weather':{'label':'Soft overcast','temperature_c':12},'recent_conversation':[],'npc_personality':{'style':'courteous'}}
r=p.ask_player_reply('Mrs Ellis','Hi!',ctx)
check('short one-line dialogue', r['dialogue']=='Good morning to you.', r['dialogue'])
check('generation budget reduced', calls[0][1]['max_tokens']==48, calls[0][1]['max_tokens'])
check('prompt asks for short sentence', 'ONE short natural sentence' in calls[0][0][1])

p2=AIProvider(); p2.enabled=True
calls2=[]
responses2=[
    'Mrs Ellis: Good morning to you.\nSOCIAL: {"affinity":0,"trust":0,"familiarity":1,"tone":["neutral"],"memory":"The player commented on the weather."}',
    'Mrs Ellis: It is pleasant enough; the rain seems to be holding off.\nSOCIAL: {"affinity":0,"trust":0,"familiarity":1,"tone":["pleasant"],"memory":"The player commented on the weather."}',
]
def fake2(*args, **kwargs): calls2.append((args,kwargs)); return responses2.pop(0)
p2._plain_request=fake2
ctx2={'daypart':'morning','weather':{'label':'Soft overcast','temperature_c':12},'recent_conversation':[{'player_message':'Hi!','npc_reply_summary':'NPC replied: Good morning to you.'}]}
r2=p2.ask_player_reply('Mrs Ellis',"What a fine day, isn't it?",ctx2)
check('repetition triggers repair retry', len(calls2)==2, len(calls2))
check('fresh retry accepted', r2['dialogue'].startswith('It is pleasant enough'), r2['dialogue'])

# Engine social clamp: ordinary weather small talk cannot create trust +1/familiarity +2.
g=Game(); social=g._clamp_acknowledgement_social("What a fine day isn't it?",{'affinity':0,'trust':1,'familiarity':2,'tone':['warm'],'memory':'weather'})
check('weather trust clamped', social['trust']==0, social)
check('weather familiarity clamped', social['familiarity']<=1, social)

# Recent context must not inject the full old long response verbatim.
g.state.setdefault('conversation_sessions',{})['mrs_ellis']=[{'absolute_minute':0,'player':'Hi!','npc':'I am Mrs Ellis, standing in a quiet shop on Village Road with soft overcast skies outside and explaining everything at length.'}]
c=g._conversation_recent_exchange_context('mrs_ellis')
check('recent reply compacted', len(c[0]['npc_reply_summary'].split())<=15, c)
check('old full reply not re-injected', 'explaining everything at length' not in c[0]['npc_reply_summary'], c)

print(f'v0.6.1 conversation reliability diagnostic: {sum(checks)}/{len(checks)} PASS')
raise SystemExit(0 if all(checks) else 1)
