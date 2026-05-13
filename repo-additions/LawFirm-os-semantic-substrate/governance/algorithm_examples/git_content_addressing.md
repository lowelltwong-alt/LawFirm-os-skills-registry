# Git Content Addressing

## Why it is world-class

Git Content Addressing is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

Object identity is derived from content, so changed content changes identity.

## What it deletes

It deletes trust in mutable labels and replaces it with hashes and history.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

Every imported skill should be hashed before review, approval, and install.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

Mutable approvals without hashes; inability to reproduce what was reviewed; silent edits after approval.
