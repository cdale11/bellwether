"""v3.8.0 player-visible presentation backlog.

Authoritative simulation history and the player presentation backlog are deliberately
separate. The backlog records prose actually committed through Game.add(), in order,
with enough context for VN-style review. It does not rewrite objective world facts.
"""
from copy import deepcopy

class PresentationLedgerModel:
    SCHEMA_VERSION=1
    def migrate(self,state):
        rt=state.setdefault('presentation_ledger',{'schema_version':1,'next_id':1,'entries':[]})
        rt.setdefault('schema_version',1);rt.setdefault('next_id',1);rt.setdefault('entries',[])
        return rt
    def append(self,state,speaker,text,source_type='game_text',source_event_id=None):
        rt=self.migrate(state)
        row={'entry_id':f"text_{int(rt['next_id']):07d}",'run_id':int(state.get('recurrence',{}).get('run_index',1) or 1),
             'day':int(state.get('day',1) or 1),'minute':int(state.get('minute',0) or 0),'location':state.get('location'),
             'speaker':str(speaker),'text':str(text).strip(),'source_type':source_type,'source_event_id':source_event_id}
        rt['next_id']=int(rt['next_id'])+1;rt['entries'].append(row)
        return row
    def public(self,state,limit=80):
        entries=self.migrate(state)['entries']
        return {'schema_version':1,'total':len(entries),'entries':deepcopy(entries[-max(1,int(limit)):])}
    def page(self,state,offset=0,limit=100,query='',kind='all'):
        rows=self.migrate(state)['entries']; q=str(query or '').strip().lower(); kind=str(kind or 'all').lower()
        def keep(r):
            sp=str(r.get('speaker','')); k='narration' if sp.lower()=='narrator' else ('bellwether' if sp.lower()=='bellwether' else 'dialogue')
            return (kind=='all' or k==kind) and (not q or q in (sp+' '+str(r.get('text',''))).lower())
        filtered=[r for r in rows if keep(r)]; total=len(filtered); start=max(0,int(offset)); lim=max(1,min(200,int(limit)))
        page=list(reversed(filtered))[start:start+lim]
        return {'schema_version':1,'total':total,'offset':start,'limit':lim,'entries':deepcopy(page),'has_more':start+lim<total}

PRESENTATION_LEDGER_MODEL=PresentationLedgerModel()
