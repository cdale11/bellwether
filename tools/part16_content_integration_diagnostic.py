#!/usr/bin/env python3
import os,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['BELLWETHER_AI']='0'
from backend.core.game import Game
from backend.core.content_model import CONTENT_MODEL,RECIPES,REPAIRS,SEASONAL_COTTAGE

def main():
 checks=[]
 def ok(n,x): assert x,n;checks.append(n);print('PASS',n)
 g=Game();g.state['location']='ashcroft_cottage';g.migrate_state()
 ok('content runtime schema present',g.state['content_progression']['schema_version']==1)
 ok('all seasonal cottage prose present',len(SEASONAL_COTTAGE)==10)
 ok('cooking unavailable without ingredients',not CONTENT_MODEL.cooking_actions(g.state))
 g.state['player_activities']['garden']['harvest_store']['radish']=2;g.state['economy']['household']['bread_loaf']=1
 acts=dict(CONTENT_MODEL.cooking_actions(g.state));ok('recipe appears from real inventory','content:cook:radish_toast' in acts)
 before=g.state['player_life']['meals'];g.perform('content:cook:radish_toast');ok('cooking consumes produce',g.state['player_activities']['garden']['harvest_store']['radish']==0);ok('cooking advances meal progression',g.state['player_life']['meals']>before)
 g.state['economy']['household']['repair_supplies']=1;acts=dict(CONTENT_MODEL.repair_actions(g.state));ok('repair appears with supplies','content:repair:kitchen_stove' in acts)
 care=g.state['player_life']['cottage_care'];g.perform('content:repair:kitchen_stove');ok('repair persists','kitchen_stove' in g.state['content_progression']['home_restoration']['completed']);ok('repair consumes supplies',g.state['economy']['household']['repair_supplies']==0);ok('repair improves cottage care',g.state['player_life']['cottage_care']>care)
 old=copy.deepcopy(g.state);old.pop('content_progression');g.state=old;g.migrate_state();ok('old save content migration',g.state['content_progression']['schema_version']==1)
 ok('authored recipe catalogue isolated','history' not in RECIPES['radish_toast'])
 print(f'Part 16 passes: {len(checks)}/{len(checks)}')
if __name__=='__main__':main()
