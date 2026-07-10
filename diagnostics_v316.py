from pathlib import Path
p=Path('backend/core/ai_player.py').read_text()
checks={
'roles': 'QA_ROLES=("human_player","completionist","chaos_player")' in p,
'human_llm': "HUMAN CAMPAIGN: preserve a coherent intention" in p,
'completionist': "qa_role=='completionist'" in p,
'chaos': "deterministic_adversary" in p,
'role_report': 'TEST DIRECTOR ROLE SUMMARY' in p,
'checkpoint': 'diagnostic_ai_player_live.jsonl' in p and '_checkpoint' in p,
'memory': 'swap_used_mb' in p and 'ollama_rss_mb' in p,
'backpressure': '_wait_for_backpressure' in p,
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
raise SystemExit(0 if all(checks.values()) else 1)
