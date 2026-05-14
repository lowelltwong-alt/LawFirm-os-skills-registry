# PR6 — Legal Knowledge Runtime Seed

## Goal

Add draft skills for legal document ingestion, structure extraction, retrieval planning, context bundle assembly, privilege-aware retrieval review, and retrieval quality evaluation.

## Required checks

- Skills remain in `skills/draft` until reviewed.
- No scripts are added.
- No network, shell, browser, or external-write permissions are requested.
- Each skill declares `not_canonical_truth`.
- Each skill states that Semantic Substrate owns canon.

## Acceptance

- Existing skills registry tests remain green.
- Candidate skills pass static review.
- Approved skills registry is not modified until human approval.
