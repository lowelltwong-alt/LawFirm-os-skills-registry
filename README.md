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
python -m pytest
python -m lawfirm_os_skills_registry console
```

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
