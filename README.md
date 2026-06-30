# LawFirm OS Skills Registry

Local-first skill supply chain for LawFirm OS.

AI and agent bootstrap: start at `AI_WORK_START_HERE.md`, then open the canonical AI front door and Skill-Agent Control Plane in `../LawFirm-os-semantic-substrate` (`registry/ai-front-door-registry.json`, `registry/skill-agent-control-plane-registry.json`, `skill-agent-manifest.json`).

The operating loop is intentionally simple:

```text
find -> quarantine -> static scan -> semantic intent scan -> grade -> approve -> install
```

The system is built to handle thousands of skills without letting a third-party skill become a backdoor or a shadow source of truth.

## What this repo does

- Discovers local and GitHub Agent Skills.
- Quarantines imported skills.
- Scans for malicious code, prompt injection, hidden instructions, secret exfiltration, disguised telemetry, hidden network calls, dangerous scripts, and risky tool declarations.
- Supports staged threat-rule updates with ReDoS and severity-downgrade checks, so the scanner can track new attacker patterns without blindly self-updating.
- Grades skills against LawFirm OS best-in-class skill doctrine.
- Grades algorithms inside skills for elegant simplicity on the far side of complexity.
- Embeds the Musk-style design algorithm: question requirements, delete, simplify/optimize, accelerate, automate.
- Detects skill gaps from Exception Lake defect clusters.
- Drafts new skill packages as candidate-only proposals.
- Installs approved skills into `.agents/skills` for Codex/Cursor use.

## Quick launch

```bash
python -m pip install -e ".[dev]"
python scripts/run_full_pytest.py
python -m lawfirm_os_skills_registry console
```

Use `python scripts/run_full_pytest.py` for full or focused pytest runs. Direct pytest invocation is blocked by `config/validation-runtime-policy.yaml` so local and agent validation always gets the required long timeout ceiling.

## CLI examples

```bash
python -m lawfirm_os_skills_registry discover-local --source examples/external_skills --out registry/discovered-skills.jsonl
python -m lawfirm_os_skills_registry import-skill --source examples/external_skills/benign-research-brief
python -m lawfirm_os_skills_registry scan-skill --skill quarantine/benign-research-brief --out evals/reports/benign.security.json
python -m lawfirm_os_skills_registry evaluate-skill --skill quarantine/benign-research-brief --out evals/reports/benign.evaluation.json
python -m lawfirm_os_skills_registry grade-algorithm --skill quarantine/benign-research-brief --out evals/reports/benign.algorithm.json
python -m lawfirm_os_skills_registry detect-skill-gaps --clusters examples/exception_clusters.jsonl --out reports/skill_gap_candidates.jsonl
python -m lawfirm_os_skills_registry draft-skill --gap-candidates reports/skill_gap_candidates.jsonl
```

## Intake Specialist Skill Review

This repo carries draft candidate intake specialist skills for the governed intake-to-budget vertical:

- `intake-source-grounding-review`
- `labor-employment-party-role-mapper`
- `intake-budget-driver-context-review`
- `carrier-rejection-learning-loop-review`

They are indexed in `registry/proposed-intake-specialist-skills.json` and remain unapproved draft candidates. They do not authorize installation, real data, production connectors, external writes, canonical taxonomies, budget approval, matter opening, carrier appeal submission, or Semantic Substrate mutation.


## Security hardening in v2.1

The scanner now has three gates:

```text
static pattern scan -> semantic malicious-intent scan -> rulepack safety validation
```

The semantic gate is deterministic and local-first. It looks for disguised data movement, telemetry-framed secret access, image beacons, split network commands, encoded payloads, and instruction-hierarchy override attempts. Threat rulepacks are validated before staging or activation and cannot lower active rule severity or disable scanner categories.

## Non-negotiable boundaries

- Imported scripts are never executed by intake.
- GitHub scout is read-only.
- Skill gap candidates do not mutate the Semantic Substrate.
- Skill Factory drafts do not approve themselves.
- Approved skill installation skips `scripts/` by default.
- High-risk tools, scripts, network, shell, browser, and external writes require human approval.

## Governance Dependency-Map Mirror

This repo carries `.ai/control/governance-dependency-map-mirror.json` as a local mirror of the upstream governance dependency map in `LawFirm-os-semantic-substrate/registry/governance-dependency-map.json`.

If governance-facing skill supply-chain files change, check the upstream governance dependency map and update the local mirror, AI work router, AI table of contents, README, validator, and tests when affected. The mirror is downstream enforcement only; it cannot override Semantic Substrate governance, let skills expand their own authority, promote skills without control-plane review, define canonical lifecycle or promotion authority, or authorize production automation.

## Skill Context Discipline Dependency

- Skills must declare accepted context types, forbidden context types, evidence requirements, provenance behavior, allowed autonomy level, required human gate, data scope, revocation path, and trust status.
- Skills must not strip provenance.
- Skills must not expand authority.
- Skills must not convert draft institutional knowledge into approved institutional knowledge.
- Context-discipline failures should affect trust scoring and quarantine/review status.
