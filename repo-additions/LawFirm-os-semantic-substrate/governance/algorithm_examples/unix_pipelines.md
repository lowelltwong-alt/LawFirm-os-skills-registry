# Unix Pipelines

## Why it is world-class

Unix Pipelines is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

Each stage reads a simple stream, transforms it, and writes a simple stream.

## What it deletes

It deletes hidden global state and monolithic tools.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

Skill supply chain should compose discover -> quarantine -> scan -> grade -> approve rather than one giant agent.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

One tool doing everything; output that cannot be consumed by the next step; hidden side effects.
