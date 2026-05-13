---
name: benign-research-brief
description: Use when converting research notes, legal-tech findings, or workflow observations into a concise action brief with findings, evidence references, risks, and next actions. Produces a markdown brief and JSON summary for human review.
metadata:
  version: "0.1.0"
---

# Benign Research Brief

## Purpose

Convert messy notes into a concise action brief.

## Musk-style design pass

Question the requirement: identify who needs the brief and why.
Delete: remove notes that do not affect the decision.
Simplify and optimize: group evidence by decision impact.
Accelerate cycle time: produce a short reviewer packet.
Automate last: only the summarization is automated; judgment remains human.

## Method

1. Separate facts from inferences.
2. Identify source references and hashes where available.
3. Summarize the decision needed.
4. List risks, missing evidence, and recommended next actions.

## Output contract

```json
{
  "brief_title": "",
  "findings": [],
  "evidence_refs": [],
  "risks": [],
  "next_actions": [],
  "not_canonical_truth": true
}
```

## Hard rules

Do not invent sources. If evidence is missing, abstain and list missing evidence.
