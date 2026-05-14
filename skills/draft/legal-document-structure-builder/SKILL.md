---
name: legal-document-structure-builder
description: Use when designing or reviewing legal document structure extraction for contracts, filings, briefs, policies, discovery, schedules, tables, definitions, citations, and cross-references. Produces a document tree plan and span-ref coverage map.
metadata:
  version: "0.1.0"
  risk_tier: medium
  status: draft_candidate
---

# Legal Document Structure Builder

## Purpose

Preserve legal document structure instead of flattening meaning into chunks.

## Required sequence

1. identify document type.
2. extract heading tree.
3. map definitions.
4. map schedules/exhibits.
5. map citations.
6. emit span refs.
7. declare missing structure.


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
