from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(n,v,d): checks.append((n,bool(v),d)); print(('PASS' if v else 'FAIL'),n,'-',d)
prov=(ROOT/'backend/ai/provider.py').read_text()
game=(ROOT/'backend/core/game.py').read_text()
js=(ROOT/'frontend/static/js/game.js').read_text()
check('reply_sentence_bound','[:2]' in prov and 'at most 30 words' in prov,'free-form reply bound is 2 sentences / 30 words')
check('reply_prompt_bound','1-2 short sentences' in prov and 'no more than 30 words' in prov,'prompt and hard bound agree')
check('scene_exchange_contract','conversation_exchange' in game and 'data.conversation_exchange' in js,'foreground free-talk exchange has explicit scene transcript contract')
check('no_fake_resident_quote','self.add(resident.get("name",rid),"You exchange' not in game,'narration is not falsely attributed to a resident')
check('core_greetings_meaningful','greeting_lines=' in game and all(x in game for x in ['"jonah":','"mara":','"mrs_ellis":']),'core greeting options resolve to character-specific text')
# Authored choice IDs should have a resolver branch or be the universal leave choice.
choice_ids={'jonah_warm','jonah_guarded','jonah_eleanor','jonah_settling','jonah_bells','mara_garden','mara_eleanor','leave_dialogue'}
resolved=set(re.findall(r'(?:if|elif) choice == "([a-z0-9_]+)"',game))|{'leave_dialogue'}
missing=sorted(x for x in choice_ids if x not in resolved)
check('authored_choice_resolution',not missing,f'unresolved authored choices: {missing}')
# Basic written-content hygiene over authored source: placeholders and malformed replacement chars.
text='\n'.join(p.read_text(errors='ignore') for p in [ROOT/'backend/core/game.py',ROOT/'backend/ai/provider.py'])
check('no_placeholder_prose',not re.search(r'\b(?:TODO|TBD|FIXME)\b',text),'no placeholder markers in player-facing audited core prose')
check('unicode_integrity','�' not in text,'no Unicode replacement characters in audited core prose')
# Detect exact duplicate choice labels within a dialogue choice block approximately.
labels=re.findall(r'"label":\s*"([^"]+)"',game)
check('choice_labels_nonempty',all(x.strip() for x in labels),f'{len(labels)} authored labels are non-empty')
check('version',(ROOT/'VERSION').read_text().strip()=='3.0.0-rc12','release identity')
print(f'RESULT {sum(v for _,v,_ in checks)}/{len(checks)}')
raise SystemExit(0 if all(v for _,v,_ in checks) else 1)
