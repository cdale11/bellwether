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
    def public(self,state):
        return {'schema_version':1,'entries':deepcopy(self.migrate(state)['entries'])}

PRESENTATION_LEDGER_MODEL=PresentationLedgerModel()
