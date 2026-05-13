# LawFirm OS Skill Quality Doctrine

A best-in-class skill is not a long prompt. It is a compact, reusable, testable method.

## The standard

A skill must be:

1. **Specific** — its description is a routing signal, not a label.
2. **Lean** — the core `SKILL.md` contains only what the agent needs to trigger and execute correctly.
3. **Contractual** — it has a clear output contract.
4. **Safe** — it states what it must not do.
5. **Composable** — its output can be handed to another skill, tool, or reviewer.
6. **Testable** — it has examples, fixtures, or measurable acceptance criteria.
7. **Boundary-aware** — it does not invent canonical LawFirm OS meaning.
8. **Evidence-aware** — it preserves provenance and missing-evidence flags.
9. **Human-readable** — a new team member can learn from it.
10. **Agent-readable** — an agent can decide when to call it.

## Best-in-class skill rubric

| Dimension | Excellent behavior |
|---|---|
| Description quality | Names trigger phrases, artifact types, inputs, and expected output. |
| Method quality | Gives reasoning framework, not just brittle step list. |
| Output contract | Defines required fields and format. |
| Edge cases | Handles missing inputs, ambiguity, low confidence, and abstention. |
| Examples | Shows what good looks like. |
| Safety boundary | States forbidden actions and authority limits. |
| Composability | Output can be consumed by another agent or deterministic validator. |
| Testability | Includes fixtures, expected outputs, or scoring criteria. |
| Elegance | Deletes unnecessary instructions and avoids solving problems it should not own. |

## Approval bar

A skill should not be approved unless it is safe, useful, and simpler than the problem it solves.
