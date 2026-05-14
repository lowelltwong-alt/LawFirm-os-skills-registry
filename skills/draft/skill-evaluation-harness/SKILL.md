---
name: skill-evaluation-harness
description: Use when reviewing a new or changed LawFirm OS skill for readiness before approval. Produces a security score, trigger-quality score, output-contract score, portability score, law-firm fit score, algorithmic-elegance score, fixture-readiness score, missing-test findings, and a human-review recommendation.
metadata:
  version: "0.1.0"
  status: draft_internal_candidate
  candidate_only: "true"
---

# Skill Evaluation Harness

## Purpose

Evaluate whether a skill is safe, useful, specific, bounded, testable, and aligned with LawFirm OS governance before it can be approved or installed.

## Evaluation sequence

```text
format check
-> security scan
-> semantic-intent scan
-> algorithmic-elegance grade
-> output-contract review
-> fixture-readiness check
-> human-review recommendation
```

## Musk-style design pass

1. Question requirements: identify the workflow owner, user need, evidence source, and approval owner.
2. Delete before optimize: fail skills that rely on unnecessary scripts, broad authority, or vague routing.
3. Simplify and optimize: prefer deterministic checks before subjective judgment.
4. Accelerate: produce one compact review packet with scores and fixes.
5. Automate last: scores can recommend; only a human can approve.

## Required checks

- `SKILL.md` exists.
- `name` is lowercase kebab-case and matches the parent folder.
- `description` explains what the skill does and when to use it.
- Main instructions include an output contract.
- The skill states what it must not do.
- The skill handles missing inputs and abstention.
- The skill includes test fixtures or concrete examples.
- Security scan is safe enough for evaluation.
- Algorithmic-elegance score is not hiding unnecessary process complexity.

## Fixture-readiness rubric

A skill should include `tests/fixtures.jsonl` with:

1. Happy path.
2. Missing-input or missing-evidence abstention.
3. Governance-boundary case.
4. Expected JSON keys or deterministic expected terms.
5. Forbidden terms or forbidden outcomes.

## Output contract

```json
{
  "skill_id": "",
  "not_canonical_truth": true,
  "scores": {
    "safety": 0,
    "trigger_quality": 0,
    "output_contract": 0,
    "portability": 0,
    "lawfirm_fit": 0,
    "algorithmic_elegance": 0,
    "fixture_readiness": 0,
    "overall": 0
  },
  "errors": [],
  "warnings": [],
  "missing_tests": [],
  "recommendation": "reject|revise|fixtures_ready|approve_for_human_review",
  "reviewer_note": ""
}
```

## Hard rules

- Do not approve the skill yourself.
- Do not execute scripts during evaluation.
- Do not treat examples as proof of correctness.
- Do not allow external skill popularity to override security review.
- Do not write to the Semantic Substrate, Exceptions Lake Runtime, Orchestrator, GitHub, email, messaging, or external services.
