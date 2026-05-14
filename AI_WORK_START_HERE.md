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
