# First-Party Skill Scout + Gap Reactor

## Why this exists

Public agent skills are useful for learning patterns, but direct installation creates supply-chain risk. The safer LawFirm OS path is:

```text
external skill ecosystem -> reference patterns -> first-party draft -> scan -> eval -> fixture harness -> human approval
```

## Authority model

| Plane | Role |
|---|---|
| Semantic Substrate | Owns canonical meaning, schemas, registries, governance boundaries, validation contracts. |
| Exceptions Lake Runtime | Owns append-only runtime evidence and governed learning candidates. |
| Orchestrator | Owns bounded execution, approval gates, ledgers, and evidence packets. |
| Skills Registry | Owns skill discovery, quarantine, scan, evaluation, draft generation, and approval records. |

The reactor belongs in the Skills Registry. It does not mutate the other planes.

## What it does

1. Reads skill-gap candidates from a local JSONL file.
2. Optionally performs read-only GitHub `SKILL.md` reference scouting.
3. Extracts structural patterns only.
4. Drafts a new first-party skill.
5. Writes provenance and pattern notes.
6. Runs security scan, skill evaluator, and fixture harness.
7. Writes a review packet.

## What it never does

- No direct third-party installs.
- No script execution.
- No cloning public repos for execution.
- No auto-approval.
- No Substrate writes.
- No Exceptions Lake writes.
- No Orchestrator execution.
- No scheduled jobs.
- No external writes.

## Commands

```bash
python -m lawfirm_os_skills_registry react-skill-gap \
  --gap-candidates reports/skill_gap_candidates.jsonl \
  --drafts-dir skills/draft \
  --reports-dir reports \
  --evals-dir evals/reports
```

Optional network reference search:

```bash
python -m lawfirm_os_skills_registry react-skill-gap \
  --gap-candidates reports/skill_gap_candidates.jsonl \
  --allow-network \
  --max-refs-per-gap 5
```

Offline reference patterns:

```bash
python -m lawfirm_os_skills_registry react-skill-gap \
  --gap-candidates reports/skill_gap_candidates.jsonl \
  --reference-jsonl examples/reference_skill_patterns.jsonl
```

## Review packet fields

```json
{
  "record_type": "skill_gap_reactor_report",
  "candidate_count": 0,
  "items": [
    {
      "gap_id": "",
      "recommended_skill_id": "",
      "draft_path": "",
      "security_report": "",
      "evaluation_report": "",
      "fixture_report": "",
      "approval_status": "candidate_only",
      "next_gate": "human_review"
    }
  ]
}
```
