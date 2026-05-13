# PageRank

## Why it is world-class

PageRank is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

Authority is recursive: important nodes are linked by other important nodes.

## What it deletes

It deletes pure self-asserted authority.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

Skill trust scoring should use source reputation, maintainer history, provenance, and evaluations, not just a skill's own claims.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

Treating a skill description as proof of quality; popularity without security review.
