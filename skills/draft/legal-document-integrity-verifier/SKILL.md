# Legal Document Integrity Verifier

## Status

Draft candidate skill. Not approved for autonomous production use.

## Purpose

Detects silent corruption risk in synthetic legal-document transformations using hashes, diffs, citation preservation, defined-term preservation, and source-ref checks.

## LawFirm OS boundaries

- Reads canonical schema/guardrail definitions from Semantic Substrate.
- Emits candidate findings, never canonical truth.
- May create evidence references or review packets.
- Must not store full raw privileged legal documents in Exception Lake.
- Must remain synthetic/local-first until governed approval.

## Required controls

- Fail closed on missing contract or schema.
- Use claim-check refs and hashes for source materials.
- Require human review for high-impact legal outputs.
- Do not mutate canon.
