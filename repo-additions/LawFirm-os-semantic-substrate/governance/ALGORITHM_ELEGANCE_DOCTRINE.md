# Algorithm Elegance Doctrine

LawFirm OS grades algorithms inside skills because a skill can hide a bad process behind polished prose.

The target is **simplicity on the far side of complexity**: not shallow simplification, but a design that has understood the problem deeply enough to remove the nonessential.

## Elegant algorithm properties

1. **Correct objective** — solves the real constraint, not a proxy.
2. **Minimal authority** — uses the least privilege and least side effects.
3. **Small state** — tracks only the state needed for correctness and audit.
4. **Clear invariants** — names what must always remain true.
5. **Deterministic where possible** — uses code/rules for exact checks and LLMs only for bounded judgment.
6. **Fail-closed** — ambiguity stops, abstains, or escalates instead of guessing.
7. **Composable outputs** — produces structured artifacts downstream systems can use.
8. **Evidence-bearing** — carries source refs, hashes, and missing-evidence flags.
9. **Complexity-aware** — avoids unnecessary loops, fan-out, and repeated model calls.
10. **Testable** — can be verified with fixtures and adversarial cases.

## Canonical examples to learn from

These examples are not copied into skills as code. They are reference patterns for grading elegance:

| Algorithm pattern | Why it is elegant |
|---|---|
| Binary search | Deletes linear scan by using a sorted invariant. |
| Dijkstra's algorithm | Separates local frontier choice from global shortest-path correctness. |
| Union-find | Keeps connected-component state minimal and nearly constant-time. |
| Topological sort | Makes dependency ordering explicit and deterministic. |
| Dynamic programming / memoization | Deletes repeated work by naming subproblem state. |
| Hash map lookup | Trades small memory for direct access and simpler control flow. |
| Unix pipeline | Composes small tools through simple interfaces. |
| Merkle tree / content hash | Makes integrity checkable without rereading everything. |
| MapReduce | Separates embarrassingly parallel transformation from aggregation. |
| Idempotent command pattern | Makes retries safe by making effects explicit. |

## Anti-patterns

- Big planner loops before a deterministic check.
- Optimizing a step that should be deleted.
- Letting the model invent authority.
- Using a tool call where a local validator suffices.
- Adding an agent where a schema, enum, or rule would do.
- Capturing raw confidential payloads instead of references and hashes.

## Best-in-world examples library

Use `docs/algorithm_examples/` as the concrete grading library for algorithmic elegance. The examples are not meant to be copied mechanically; they are reference patterns for invariants, deletion, composability, feedback, and bounded state transitions.

Initial examples include binary search, Unix pipelines, Git content addressing, MapReduce, PageRank, Dijkstra, Kalman filtering, Monte Carlo tree search, TCP congestion control, and Kubernetes control loops.

