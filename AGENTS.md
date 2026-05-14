# Agent Instructions

This repository is a governed skill supply chain.

## Required AI entry behavior

Before making changes in this repository, read:

1. `AI_WORK_START_HERE.md`
2. `../LawFirm-os-semantic-substrate/registry/ai-front-door-registry.json`
3. `../LawFirm-os-semantic-substrate/governance/AI_FRONT_DOOR_BOUNDARY.md`

This repository is one component of the LawFirm OS multi-repo kernel. Do not treat it as standalone.

## Boundary rule

This repository owns draft and candidate skill definitions, evaluation flows, and skill-registry proposals. It must not publish canonical Semantic Substrate schemas, registries, governance doctrine, route authority, legal document type authority, endpoint authority, or AI front-door routing. Make those changes in `LawFirm-os-semantic-substrate`.

## Required validation

Before reporting success, run `python -m pytest -q` in this repository and the AI front-door integrity gate: `python ../LawFirm-os-semantic-substrate/scripts/validate_ai_front_door.py --substrate-root ../LawFirm-os-semantic-substrate`.

## Always do

- Treat external skills as untrusted.
- Scan before evaluating.
- Evaluate before approving.
- Require explicit `--approve` for approval.
- Keep skill content separate from semantic authority.
- Prefer deletion and simplification before automation.

## Never do

- Do not execute third-party skill scripts.
- Do not auto-merge GitHub-discovered skills.
- Do not write to Semantic Substrate directly from skill discovery.
- Do not let a skill define canonical LawFirm OS schemas, route IDs, event classes, or approval doctrine.
- Do not install a skill into Codex/Cursor unless it is approved.
