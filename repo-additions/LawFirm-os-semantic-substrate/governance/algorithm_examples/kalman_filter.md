# Kalman Filter

## Why it is world-class

Kalman Filter is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

Update belief by combining prediction and observation according to uncertainty.

## What it deletes

It deletes overreaction to noisy single observations.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

Exception Lake skill-gap detection should require repeated defect support before proposing new skills.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

Creating a new skill from one anecdote; no uncertainty or support count.
