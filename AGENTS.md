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

Before reporting success, run `python scripts/run_full_pytest.py` in this repository and the AI front-door integrity gate: `python ../LawFirm-os-semantic-substrate/scripts/validate_ai_front_door.py --substrate-root ../LawFirm-os-semantic-substrate`. The pytest wrapper is required by `config/validation-runtime-policy.yaml`; direct pytest invocation is blocked so validation always gets the long ceiling.

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

    python scripts/run_full_pytest.py
    python ../LawFirm-os-semantic-substrate/scripts/validate_skill_agent_control_plane.py --workspace ..

## Skill Context Discipline Dependency

- Skills must declare accepted context types, forbidden context types, evidence requirements, provenance behavior, allowed autonomy level, required human gate, data scope, revocation path, and trust status.
- Skills must not strip provenance.
- Skills must not expand authority.
- Skills must not convert draft institutional knowledge into approved institutional knowledge.
- Context-discipline failures should affect trust scoring and quarantine/review status.

<!-- BEGIN DIGITAL_ASSET_DIRECTORY_GOVERNANCE -->
## Digital Asset Directory learning and mail pointer

Central hub: `C:\Users\lowel\OneDrive\Desktop\Git Projects\04_Digital_Assett_Directory`
Wave: `1`
Rollout policy: `skill_wrapper_pointer`
Authority tier: `skill_supply_chain`
Recommended profiles: `skills-registry, asset-skill-wrapper, python-modular-design`

Before material AI-assisted work:
1. Read this repository's own front door and authority surfaces first.
2. Run: `asset-dir agent preflight --repo . --agent <agent> --task "<task>" --hub "C:\Users\lowel\OneDrive\Desktop\Git Projects\04_Digital_Assett_Directory"`
3. State scope, allowed and forbidden paths, validation plan, and stop conditions.
4. Preserve this repo's local canon. DAD is advisory evidence and learning transport, not semantic authority.

Before reporting completion or pushing material changes:
1. Run this repo's required validation.
2. Run: `asset-dir agent postflight --session <SESSION_ID> --repo . --summary "<summary>" --hub "C:\Users\lowel\OneDrive\Desktop\Git Projects\04_Digital_Assett_Directory"`
3. Capture lessons, discoveries, failures, reusable patterns, missing capabilities, risks, and unknowns.

DAD mail lives at `.digital-asset/mail/` and is candidate-only inbox/outbox transport. Mail can suggest lessons, workflows, assets, taxonomy, capabilities, or governance notices; local review decides whether anything is adopted. Agent review is triage only, and human review/public-release gates remain separate.

Hooks are not enabled by this Wave 1 install. Do not set `core.hooksPath` or add hook enforcement without separate human approval.
<!-- END DIGITAL_ASSET_DIRECTORY_GOVERNANCE -->
