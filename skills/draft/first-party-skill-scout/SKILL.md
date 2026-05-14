---
name: first-party-skill-scout
description: Use when LawFirm OS needs to discover candidate agent skills, compare multiple public SKILL.md examples, respond to an Exception Lake skill-gap candidate, or draft a safer first-party replacement. Produces reference-pattern notes, a candidate first-party skill package, security/evaluation reports, fixture-readiness results, and a human-review packet without installing third-party code.
metadata:
  version: "0.1.0"
  status: draft_internal_candidate
  candidate_only: "true"
---

# First-Party Skill Scout

## Purpose

Find skill opportunities and turn them into first-party LawFirm OS skills without importing unknown code.

This skill treats public skills like design references, not dependencies. It compares multiple examples, extracts structural lessons, writes a new LawFirm OS skill from scratch, then sends the result through scan, evaluation, fixture, and human-review gates.

## Operating loop

```text
gap or search intent
-> reference-only search
-> compare several SKILL.md structures
-> extract patterns, not code
-> synthesize first-party SKILL.md
-> create fixtures
-> scan
-> evaluate
-> human review packet
```

## Musk-style design pass

1. Question requirements: name the workflow owner, repeated defect, reviewer need, and authority source.
2. Delete before optimize: reject direct installs, scripts, registry cloning, unbounded browsing, and external writes.
3. Simplify and optimize: summarize reference patterns into deterministic feature flags.
4. Accelerate: create a compact review packet with provenance and reports.
5. Automate last: propose only; approval and installation remain human-gated.

## Invariants

- External skills are reference material only.
- Full external text is not retained unless a reviewer explicitly requests a quarantine review.
- New skills are first-party drafts with `candidate_only: true`.
- The skill never approves, installs, executes, or schedules another skill.
- The skill never defines canonical schemas, route meaning, registries, governance policy, or approval authority.
- Missing evidence, missing authority, or single-anecdote support causes abstention or observation, not approval.

## Required inputs

- `skill_gap_candidate` or `search_intent`
- `support_count`
- `affected_workflows`
- `source_refs`
- optional `reference_patterns`
- optional `allow_network_reference_search`

## Method

1. Restate the gap and the authority boundary.
2. Confirm whether the request is from the control plane, evidence plane, or execution plane.
3. Search only for reference patterns when network access is explicitly allowed.
4. Compare at least two references when available; otherwise draft from internal doctrine only.
5. Extract patterns such as trigger specificity, hard rules, output contracts, examples, edge cases, progressive disclosure, and feedback loops.
6. Penalize references that rely on shell execution, install commands, external fetches, broad tool grants, or self-updating registries.
7. Draft a new LawFirm OS skill in `skills/draft`.
8. Generate `tests/fixtures.jsonl`.
9. Run security scan, skill evaluator, and fixture harness.
10. Produce a review packet.

## Output contract

```json
{
  "status": "candidate_review_packet",
  "not_canonical_truth": true,
  "gap_id": "",
  "candidate_skill_id": "",
  "reference_patterns_used": [],
  "reference_patterns_rejected": [],
  "draft_path": "",
  "security_report": "",
  "evaluation_report": "",
  "fixture_report": "",
  "approval_status": "candidate_only",
  "missing_inputs": [],
  "reviewer_note": "",
  "recommended_next_gate": "human_review"
}
```

## Hard rules

- Do not clone or install a third-party skill.
- Do not copy external scripts or command blocks.
- Do not execute candidate skill scripts.
- Do not write to sibling repositories.
- Do not write to GitHub, email, messaging, cloud storage, or any external service.
- Do not handle real client, matter, employee, or privileged data.
- Do not approve the generated skill.
