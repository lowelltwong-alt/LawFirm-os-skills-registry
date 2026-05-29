# AI_WORK_START_HERE.md

<!-- BEGIN LAWFIRM_OS_BOOTSTRAP -->
Managed bootstrap for AI-assisted work in the LawFirm OS multi-repo workspace. Route through the canonical AI front door and Skill-Agent Control Plane, but preserve local repo operating doctrine.

Required bootstrap read order:

1. AGENTS.md
2. skill-agent-manifest.json
3. Semantic Substrate registry/ai-front-door-registry.json
4. Semantic Substrate registry/skill-agent-control-plane-registry.json
5. Semantic Substrate governance/SKILL_AGENT_CONTROL_PLANE_BOUNDARY.md

Repo: LawFirm-os-skills-registry
Plane: skills registry
Repo purpose: Draft/candidate skill definitions, local skill metadata, evaluation flows, and skill registry proposals.
This repo must not own: Canonical lifecycle policy, promotion authority, runtime evidence persistence.

Run workspace preservation and control-plane validation before reporting success on managed patch work.
<!-- END LAWFIRM_OS_BOOTSTRAP -->

<!-- BEGIN REPO_SPECIFIC_INSTRUCTIONS -->
# AI Work Start Here

This repo is **LawFirm-os-skills-registry** (governed skill supply chain). It is not the Semantic Substrate.

## Before you edit

1. Read `AGENTS.md` in this repository.
2. Open the canonical AI front door in Semantic Substrate (sibling checkout):
   - `../LawFirm-os-semantic-substrate/registry/ai-front-door-registry.json`
   - `../LawFirm-os-semantic-substrate/governance/AI_FRONT_DOOR_BOUNDARY.md`
3. Run `python -m pytest -q` here after changes.
4. Run the substrate AI front-door gate:  
   `python ../LawFirm-os-semantic-substrate/scripts/validate_ai_front_door.py --substrate-root ../LawFirm-os-semantic-substrate`

If your workspace layout differs, point `--substrate-root` at your `LawFirm-os-semantic-substrate` checkout.

<!-- END REPO_SPECIFIC_INSTRUCTIONS -->

## Skill-Agent Control Plane References

- skill-agent-manifest.json
- Semantic Substrate registry/skill-agent-control-plane-registry.json
- Semantic Substrate registry/skill-agent-lifecycle-policy-registry.json
- Semantic Substrate registry/skill-agent-quality-scoring-registry.json
- Semantic Substrate scripts/validate_skill_agent_control_plane.py

## Validation Commands

    python -m pytest -q
    python ../LawFirm-os-semantic-substrate/scripts/validate_skill_agent_control_plane.py --workspace ..

## Skill Context Discipline Dependency

- Skills must declare accepted context types, forbidden context types, evidence requirements, provenance behavior, allowed autonomy level, required human gate, data scope, revocation path, and trust status.
- Skills must not strip provenance.
- Skills must not expand authority.
- Skills must not convert draft institutional knowledge into approved institutional knowledge.
- Context-discipline failures should affect trust scoring and quarantine/review status.
