# Dijkstra Shortest Path

## Why it is world-class

Dijkstra Shortest Path is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

When the lowest-cost frontier node is settled, its best distance is final under nonnegative costs.

## What it deletes

It deletes backtracking across settled safe decisions.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

Skill approval should settle hard-fail gates first, then optimize for quality among surviving candidates.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

Negative or changing costs; reopening settled gates without evidence; optimizing before validity.
