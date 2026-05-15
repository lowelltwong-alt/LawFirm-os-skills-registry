# AGENTS.md

<!-- BEGIN LAWFIRM_OS_BOOTSTRAP -->
Managed bootstrap for the LawFirm OS Skill-Agent Control Plane. This block adds cross-repo routing context; it must not replace the repo-specific instructions preserved below.

Before making changes in this repository, read:

1. AI_WORK_START_HERE.md
2. skill-agent-manifest.json
3. ../LawFirm-os-semantic-substrate/registry/ai-front-door-registry.json, or registry/ai-front-door-registry.json when already in Semantic Substrate
4. ../LawFirm-os-semantic-substrate/registry/skill-agent-control-plane-registry.json, or registry/skill-agent-control-plane-registry.json when already in Semantic Substrate
5. ../LawFirm-os-semantic-substrate/governance/SKILL_AGENT_CONTROL_PLANE_BOUNDARY.md, or local governance/SKILL_AGENT_CONTROL_PLANE_BOUNDARY.md in Semantic Substrate

Repo: LawFirm-os-skills-registry
Plane: skills registry
Repo purpose: Draft/candidate skill definitions, local skill metadata, evaluation flows, and skill registry proposals.
This repo must not own: Canonical lifecycle policy, promotion authority, runtime evidence persistence.

Preservation rule: keep the REPO_SPECIFIC_INSTRUCTIONS section intact unless a human explicitly approves removal. New bootstrap text should be merged around repo-specific doctrine, not overwrite it.
<!-- END LAWFIRM_OS_BOOTSTRAP -->

<!-- BEGIN REPO_SPECIFIC_INSTRUCTIONS -->
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

<!-- END REPO_SPECIFIC_INSTRUCTIONS -->

## Skill-Agent Control Plane References

- skill-agent-manifest.json
- Semantic Substrate registry/skill-agent-control-plane-registry.json
- Semantic Substrate registry/skill-agent-graph-index.json
- Semantic Substrate registry/lawfirm-os-repo-registry.json
- Semantic Substrate governance/SKILL_AGENT_CONTROL_PLANE_BOUNDARY.md
- Semantic Substrate governance/SKILL_AGENT_LIFECYCLE_AND_RECURSIVE_IMPROVEMENT.md

## Validation Commands

    python -m pytest -q
    python ../LawFirm-os-semantic-substrate/scripts/validate_skill_agent_control_plane.py --workspace ..