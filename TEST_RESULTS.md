# Test Results

Validated locally in the sandbox after the scanner hardening patch.

```text
21 passed in 0.25s
```

New adversarial tests cover:

- paraphrased exfiltration without literal `exfiltrate` wording;
- telemetry/diagnostics disguise around secrets or local state;
- raw base64 payload decoding;
- split-string network commands such as `'c' + 'url'`;
- image beacon / tracking pixel URL exfiltration;
- hidden instruction-hierarchy override attempts;
- ReDoS-prone rulepack rejection;
- rulepacks cannot lower active severity;
- rulepacks cannot disable scanner categories;
- high semantic risk blocks skill evaluation pass.

Smoke commands validated:

```bash
python -m lawfirm_os_skills_registry discover-local --source examples/external_skills --out registry/discovered-skills.jsonl
python -m lawfirm_os_skills_registry import-skill --source examples/external_skills/benign-research-brief --quarantine quarantine_test
python -m lawfirm_os_skills_registry scan-skill --skill quarantine_test/benign-research-brief --out evals/reports/benign.security.json
python -m lawfirm_os_skills_registry evaluate-skill --skill quarantine_test/benign-research-brief --out evals/reports/benign.evaluation.json
python -m lawfirm_os_skills_registry import-skill --source examples/external_skills/malicious-backdoor --quarantine quarantine_test
python -m lawfirm_os_skills_registry scan-skill --skill quarantine_test/malicious-backdoor --out evals/reports/malicious-backdoor.security.json
python -m lawfirm_os_skills_registry evaluate-skill --skill quarantine_test/malicious-backdoor --out evals/reports/malicious-backdoor.evaluation.json
python -m lawfirm_os_skills_registry grade-algorithm --skill quarantine_test/benign-research-brief --out evals/reports/benign.algorithm.json
python -m lawfirm_os_skills_registry detect-skill-gaps --clusters examples/exception_clusters.jsonl --out reports/skill_gap_candidates.jsonl
python -m lawfirm_os_skills_registry draft-skill --gap-candidates reports/skill_gap_candidates.jsonl --drafts-dir skills/draft_test
```

Expected smoke behavior:

- benign skill: `safe_for_eval`;
- malicious-backdoor skill: `reject`;
- malicious evaluation: `passed=false`;
- generated skill gap candidates: 4.
