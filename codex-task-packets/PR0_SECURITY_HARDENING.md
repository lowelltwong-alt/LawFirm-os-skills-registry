# PR0 — Security hardening for malicious skill intake

## Goal

Patch the skill intake system so public or generated skills cannot bypass review through paraphrased malicious intent, disguised telemetry, encoded payloads, split-string commands, image beacons, or unsafe threat-rule updates.

## Required behavior

The intake path must be:

```text
discover -> quarantine -> hash -> static scan -> semantic intent scan -> rulepack safety validation -> quality/elegance evaluation -> explicit human approval
```

## Files changed or added

- `src/lawfirm_os_skills_registry/security/semantic_intent.py`
- `src/lawfirm_os_skills_registry/security/rulepack_validator.py`
- `src/lawfirm_os_skills_registry/security/scanner.py`
- `src/lawfirm_os_skills_registry/evaluation/evaluator.py`
- `src/lawfirm_os_skills_registry/registry/store.py`
- `tests/test_security_hardening.py`
- `docs/MALICIOUS_SKILL_INTAKE_POLICY.md`
- `skills/approved/malicious-skill-review/SKILL.md`

## Acceptance tests

Run:

```bash
python -m pytest -q
```

Expected:

```text
21 passed
```

## Safety requirements

- No third-party skill scripts are executed.
- Rulepacks are untrusted inputs.
- ReDoS-prone patterns are rejected.
- Rulepacks cannot disable scanner categories or lower severity.
- High/critical semantic intent blocks approval.
- The scanner writes local reports only.
- Nothing writes to Semantic Substrate, Orchestrator, or Exception Lake.

## Risk / effort

Medium effort, high safety value.
