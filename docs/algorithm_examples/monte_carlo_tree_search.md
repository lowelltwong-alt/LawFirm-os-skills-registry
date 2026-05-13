# Monte Carlo Tree Search

## Why it is world-class

Monte Carlo Tree Search is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

Explore where uncertainty and value justify exploration, then exploit the best-proven branches.

## What it deletes

It deletes exhaustive search of every path.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

Skill Factory should draft candidates for high-support gaps first and keep alternatives as proposals.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

Unbounded generation; too many draft skills; no eval feedback.
