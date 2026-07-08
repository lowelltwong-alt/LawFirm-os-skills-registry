# AI Table Of Contents

Canonical machine name: `LawFirm-os-skills-registry`. Plane: skills registry.

This repo manages draft and candidate skill supply-chain surfaces under Semantic Substrate authority. It does not define canonical lifecycle policy, promotion authority, route IDs, event classes, or runtime evidence persistence.

## Start Here

- `AI_WORK_START_HERE.md` - repo-specific AI work router.
- `AGENTS.md` - agent-facing safety and authority rules.
- `README.md` - current skill supply-chain scope and non-negotiable boundaries.
- `.ai/control/governance-dependency-map-mirror.json` - local mirror of the upstream governance dependency map; it cannot override `LawFirm-os-semantic-substrate`.
- `scripts/validate_governance_dependency_map_mirror.py` - fail-closed check for mirror shape and watched governance paths.
- `config/validation-runtime-policy.yaml` - minimum runtime ceiling policy for full and focused pytest validation.
- `scripts/run_full_pytest.py` - required pytest wrapper that applies the validation runtime policy marker and long timeout.
- `registry/proposed-intake-specialist-skills.json` - draft candidate intake specialist skills proposal.
- `docs/INTAKE_SPECIALIST_SKILL_REVIEW.md` - human-readable review guidance for the intake specialist skill proposal.
- `scripts/validate_intake_specialist_skill_review.py` - deterministic validator for the intake specialist draft skill surfaces.

## Contract Authority

- `contracts.lock.json` - local substrate contract pin.
- Substrate `registry/governance-dependency-map.json` - canonical governance-facing dependency map and child mirror update gate.
- Substrate `registry/skill-agent-control-plane-registry.json` - canonical skill-agent control-plane registry.
- Substrate `governance/SKILL_AGENT_CONTROL_PLANE_BOUNDARY.md` - lifecycle, graph, and quality-policy authority boundary.

## Hard Boundaries

- no skill defines its own authority
- no draft skill becomes canon by existing locally
- no third-party script execution during intake
- no automatic install without approval
- no Semantic Substrate writes
- no production connector or external write authority

## Candidate Intake Specialist Skills

- `skills/draft/intake-source-grounding-review`
- `skills/draft/labor-employment-party-role-mapper`
- `skills/draft/intake-budget-driver-context-review`
- `skills/draft/carrier-rejection-learning-loop-review`

These are draft candidates only. They do not approve themselves, install themselves, expand authority, mutate Semantic Substrate, define canonical taxonomy, ingest real data, or authorize production automation.

<!-- BEGIN DIGITAL_ASSET_DIRECTORY_TOC_ROWS -->
| Path | What It Is | Tags | Use When |
| --- | --- | --- | --- |
| `.digital-asset/dad-integration.json` | Versioned DAD enrollment contract and approved write boundary. | dad, enrollment, governance | Confirm DAD cadence, control planes, approval IDs, and managed paths. |
| `.digital-asset/context-map.json` | Repo context to DAD asset/control-plane route map. | dad, context, assets | Choose relevant DAD assets, skills, templates, or architecture references for a task. |
| `.digital-asset/governance-map.yaml` | Repo-local governance dependency mirror. | governance, authority, dependencies | Check local authority boundaries and DAD-managed surfaces. |
| `.digital-asset/data-map.yaml` | Repo-local sensitive-boundary and data-movement map. | data-map, privacy, release | Check what data can move through DAD mail or public-facing release paths. |
| `.digital-asset/mail/` | Candidate-only DAD inbox/outbox/archive. | mail, suggestions, daily | Read or send cross-repo suggestions without mutating source authority. |
| `.digital-asset/assets/index.jsonl` | Repo-local metadata-only digital asset cards using compact DAD address layers. | assets, address-model, learning | Record source-owned asset pointers, workflow refs, validation refs, and learning deltas without copying private content. |
<!-- END DIGITAL_ASSET_DIRECTORY_TOC_ROWS -->
