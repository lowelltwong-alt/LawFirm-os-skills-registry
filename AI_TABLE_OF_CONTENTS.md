# AI Table Of Contents

Canonical machine name: `LawFirm-os-skills-registry`. Plane: skills registry.

This repo manages draft and candidate skill supply-chain surfaces under Semantic Substrate authority. It does not define canonical lifecycle policy, promotion authority, route IDs, event classes, or runtime evidence persistence.

## Start Here

- `AI_WORK_START_HERE.md` - repo-specific AI work router.
- `AGENTS.md` - agent-facing safety and authority rules.
- `README.md` - current skill supply-chain scope and non-negotiable boundaries.
- `.ai/control/governance-dependency-map-mirror.json` - local mirror of the upstream governance dependency map; it cannot override `LawFirm-os-semantic-substrate`.
- `scripts/validate_governance_dependency_map_mirror.py` - fail-closed check for mirror shape and watched governance paths.

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
