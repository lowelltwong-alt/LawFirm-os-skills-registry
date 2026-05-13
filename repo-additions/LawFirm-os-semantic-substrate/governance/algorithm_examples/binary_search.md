# Binary Search

## Why it is world-class

Binary Search is world-class because it turns a broad problem into a bounded procedure with a small number of stable rules.

## Core invariant

At every step, the answer remains inside the surviving interval.

## What it deletes

It deletes half the remaining search space on each step and avoids inspecting every candidate.

## Why it is simple after complexity

It is not simplistic. The hard work is in defining the invariant, the boundary, and the allowed state transition. Once those are correct, the implementation is small and predictable.

## LawFirm OS analogy

Skill intake should narrow candidates by hard gates before expensive review: missing SKILL.md, script surface, semantic risk, and then quality.

## How to grade skills against this pattern

Reward skills that state the invariant, bound the search or workflow, produce composable output, preserve provenance, and fail closed when the invariant is missing.

## Red flags

Linear scanning when ordered gates exist; no termination condition; changing the search target midstream.
