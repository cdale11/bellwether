from backend.core.ai_player import PLAYER_ARCHETYPES, ARCHETYPE_GUIDANCE, _player_archetype, AIPlayerRunner

def main():
 checks=[]
 checks.append((len(PLAYER_ARCHETYPES)==5,'five archetypes'))
 checks.append((len(set(PLAYER_ARCHETYPES))==5,'unique archetypes'))
 checks.append((all(x in ARCHETYPE_GUIDANCE for x in PLAYER_ARCHETYPES),'guidance coverage'))
 checks.append((_player_archetype(0)=='social_anchor' and _player_archetype(30)=='cottage_isolation','block rotation'))
 r=AIPlayerRunner(); snap=r.snapshot()
 checks.append(('adaptation_snapshots' in snap and 'adaptation_findings' in snap,'status evidence'))
 fake=[{'archetype':'social_anchor','town_intentions':['x'],'town_strategy':'a','pressure_strategy':None,'town_hypotheses':['h'],'chorus_hypotheses':[]},{'archetype':'cottage_isolation','town_intentions':['x'],'town_strategy':'a','pressure_strategy':None,'town_hypotheses':['h2'],'chorus_hypotheses':[]}]
 checks.append((any(x['type']=='adaptation_signature_collision' for x in r._adaptation_findings(fake)),'collision detector'))
 for ok,name in checks: print(('PASS' if ok else 'FAIL'),name)
 if not all(x for x,_ in checks): raise SystemExit(1)
 print(f'{sum(x for x,_ in checks)}/{len(checks)} passed')
if __name__=='__main__':main()
