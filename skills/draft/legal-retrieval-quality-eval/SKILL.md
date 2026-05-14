---
name: legal-retrieval-quality-eval
description: Use when evaluating legal search quality, context bundle sufficiency, citation grounding, retrieval trace completeness, and missing-evidence defects. Produces quality scores, defect tags, and improvement proposals without mutating canon.
metadata:
  version: "0.1.0"
  risk_tier: medium
  status: draft_candidate
---

# Legal Retrieval Quality Eval

## Purpose

Turn retrieval defects into measured improvement candidates.

## Required sequence

1. compare bundle to task contract.
2. score completeness.
3. verify source refs.
4. tag defects.
5. write evaluation record.
6. propose smallest improvement.


## LawFirm OS invariants

- Semantic Substrate owns canon.
- Legal Knowledge Runtime assembles retrieval evidence and context bundles.
- Orchestrator coordinates execution and approvals.
- Exception Lake stores evidence and candidate signals only.
- Skills produce reusable expertise, not authority.
- Ambiguity must abstain or escalate.

## Output contract

```json
{
  "skill_id": "",
  "risk_tier": "low|medium|high|critical",
  "status": "pass|fail|needs_review|abstain",
  "findings": [],
  "missing_required_context": [],
  "recommended_next_action": "continue|block|human_review|open_candidate_improvement",
  "evidence_refs": [],
  "not_canonical_truth": true
}
```

## Hard rules

- Do not ingest real client or matter data.
- Do not approve production connectors.
- Do not mutate Semantic Substrate schemas, registries, route IDs, event classes, or governance doctrine.
- Do not store full legal document payloads in Exception Lake.
- Do not treat retrieved context as legal advice or final work product.
