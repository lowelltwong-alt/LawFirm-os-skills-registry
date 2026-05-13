# Best-in-World Algorithm Examples Library

This library turns “elegant design” into concrete review examples. It is not a museum of clever algorithms. It is a grading aid for skills, agents, and workflows.

Each example asks the same questions:

1. What invariant makes it reliable?
2. What does it delete?
3. How does it become simple after complexity?
4. What is the LawFirm OS analogy?
5. What red flags show that a skill is violating the pattern?

Use this library when grading skill algorithms for elegant, bounded, auditable design.

## Included patterns

| Example | Pattern to learn |
|---|---|
| Binary search | Minimal search through ordered possibility space |
| Unix pipelines | Composable small tools with clear contracts |
| Git content addressing | Immutable identity, lineage, and diffability |
| MapReduce | Decompose parallel work, then reduce deterministically |
| PageRank | Recursive authority from graph structure |
| Dijkstra | Best-known frontier expansion with nonnegative costs |
| Kalman filter | Recursive uncertainty update |
| Monte Carlo tree search | Bounded exploration with feedback |
| TCP congestion control | Feedback, stability, and backoff |
| Kubernetes control loop | Desired-state reconciliation |

## Scoring use

A skill should score higher when it borrows these properties without overfitting the example. A skill should score lower when it copies vocabulary but lacks invariants, termination, composability, or evidence.
