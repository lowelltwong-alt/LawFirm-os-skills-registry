# MapReduce

## Why it is world-class

MapReduce is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

Map work independently, then reduce results through a deterministic aggregation.

## What it deletes

It deletes unnecessary coordination during independent work.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

GitHub skill scouting can map candidate scans across many repos, then reduce into ranked candidates and risk reports.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

Cross-candidate coupling; reducers that invent meaning; no deterministic aggregation.
