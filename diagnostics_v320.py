from backend.core.ai_player import AIPlayerRunner

def main():
 r=AIPlayerRunner(); s=r.snapshot(); checks=[]
 checks.append(('action_evidence' in s,'bounded action evidence status'))
 cov={'cooking':{'status':'untested','attempts':8,'acted':0,'successes':0,'note':'cook','last_gap':'no action'}}
 fs=r._unified_findings(cov,[{'severity':'warning','type':'target_action_mismatch','detail':'cooking -> observe'}])
 checks.append((len(fs)>=2,'unified finding aggregation'))
 checks.append((r._release_assessment(fs,cov) in {'NEEDS CORRECTION','CONDITIONALLY READY','NOT READY'},'release assessment'))
 groups=r._root_cause_groups(fs); checks.append((bool(groups['reachability_and_progression']),'root cause grouping'))
 r._update(action_evidence=[{'day':1,'minute':600,'role':'human_player','archetype':'social_anchor','target':'cooking','action':'look','label':'Look','ok':True,'diff':['minute changed']}])
 checks.append((bool(r._reproduction_lines(fs)),'reproduction trace'))
 for ok,name in checks: print(('PASS' if ok else 'FAIL'),name)
 if not all(x for x,_ in checks): raise SystemExit(1)
 print(f'{sum(x for x,_ in checks)}/{len(checks)} passed')
if __name__=='__main__': main()
