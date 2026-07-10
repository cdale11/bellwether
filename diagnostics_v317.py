from pathlib import Path
p=Path(__file__).parent/'backend/core/ai_player.py'
s=p.read_text()
checks={
 'version':(Path(__file__).parent/'VERSION').read_text().strip()=='3.17.0',
 'critic_method':'_story_critic_review' in s,
 'critic_provider':'qa_story_critic' in s and 'provider.ask_text' in s,
 'bounded_findings':'return out[:3]' in s,
 'report_surface':'STORY CRITIC / PLAYER IRRITATION' in s,
 'interrupt_safe':'diagnostic_ai_player_live.jsonl' in s and 'diagnostic_ai_player_live_report.txt' in s,
 'roles':all(x in s for x in ('human_player','completionist','chaos_player')),
}
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
raise SystemExit(0 if all(checks.values()) else 1)
