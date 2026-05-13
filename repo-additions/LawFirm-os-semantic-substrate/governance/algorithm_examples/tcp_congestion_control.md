# TCP Congestion Control

## Why it is world-class

TCP Congestion Control is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

Increase cautiously and back off sharply when the system signals congestion.

## What it deletes

It deletes blind throughput maximization.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

The Orchestrator should slow skill invocation when review queues, validation failures, or defect rates rise.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

More agents when reviewers are overloaded; no backpressure; retry storms.
