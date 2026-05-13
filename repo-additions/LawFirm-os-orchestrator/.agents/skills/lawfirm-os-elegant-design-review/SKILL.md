---
name: elegant-design-review
description: Use when reviewing a skill, algorithm, workflow, agent plan, repo change, or proposed automation for elegant simple design on the far side of complexity. Applies the Musk-style sequence: question requirements, delete, simplify/optimize, accelerate, automate last. Produces a design score, deletion candidates, simplification plan, and approval recommendation.
metadata:
  version: "0.1.0"
  risk_tier: medium
  status: approved_internal
---

# Elegant Design Review

## Purpose

Grade whether a proposed skill or algorithm is an elegant solution, not just a working one.

## Review sequence

1. Question every requirement. Name the owner and reason.
2. Delete unnecessary parts, steps, tools, scripts, branches, and model calls.
3. Simplify and optimize what remains.
4. Accelerate cycle time only after deletion and simplification.
5. Automate last, and only when the remaining process is stable and governed.

## LawFirm OS invariants

- Semantic Substrate owns canon.
- Orchestrator coordinates execution and records ledgers.
- Exception Lake stores evidence and candidates.
- Skills produce reusable expertise, not authority.
- Ambiguity must abstain or escalate.

## Output contract

```json
{
  "design_score": 0,
  "requirement_questions": [],
  "deletion_candidates": [],
  "simplification_plan": [],
  "cycle_time_improvements": [],
  "automation_allowed": false,
  "approval_recommendation": "approve|revise|reject",
  "not_canonical_truth": true
}
```
