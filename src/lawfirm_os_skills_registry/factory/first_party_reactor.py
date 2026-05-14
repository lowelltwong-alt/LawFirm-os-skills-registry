from __future__ import annotations

import base64
import json
import re
import urllib.parse
from pathlib import Path
from typing import Any

from ..discovery import github as github_discovery
from ..evaluation.evaluator import write_evaluation
from ..evaluation.fixture_harness import write_fixture_evaluation
from ..security.scanner import write_scan_report
from ..skill_format import parse_frontmatter
from ..util.files import ensure_dir, read_jsonl, write_json
from ..util.time import utc_now


SEVERITY_ORDER = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}


def slugify(value: Any, fallback: str = "draft-skill") -> str:
    text = str(value or "").lower().strip()
    text = re.sub(r"[^a-z0-9-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:64].strip("-") or fallback)


def _gap_text(gap: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in (
        "recommended_skill_id",
        "observed_pattern",
        "why_existing_skills_are_insufficient",
        "severity",
        "skill_need_type",
        "source",
    ):
        value = gap.get(key)
        if value:
            parts.append(str(value))
    workflows = gap.get("affected_workflows")
    if isinstance(workflows, list):
        parts.extend(str(x) for x in workflows)
    return "\n".join(parts)


def _keywords_for_gap(gap: dict[str, Any]) -> list[str]:
    text = _gap_text(gap).lower()
    candidates = re.findall(r"[a-z][a-z0-9-]{2,}", text)
    stop = {
        "new",
        "skill",
        "candidate",
        "existing",
        "insufficient",
        "source",
        "jsonl",
        "medium",
        "high",
        "low",
        "critical",
        "workflow",
        "workflows",
        "pattern",
        "repeated",
        "defect",
        "support",
        "count",
    }
    scored: dict[str, int] = {}
    for word in candidates:
        if word in stop:
            continue
        scored[word] = scored.get(word, 0) + 1
    preferred = [
        "evidence",
        "citation",
        "provenance",
        "contract",
        "intake",
        "review",
        "exception",
        "governance",
        "repository",
        "patch",
        "research",
        "brief",
        "approval",
        "audit",
    ]
    for word in preferred:
        if word in text:
            scored[word] = scored.get(word, 0) + 3
    return [word for word, _ in sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))[:8]]


def _build_github_code_query(gap: dict[str, Any]) -> str:
    words = _keywords_for_gap(gap)
    if not words:
        words = ["workflow", "review", "evidence"]
    # GitHub code search supports filename/path qualifiers. Keep the query short
    # to avoid brittle syntax and rate-limit-heavy searches.
    return "filename:SKILL.md " + " ".join(words[:4])


def _contains_any(text: str, words: list[str]) -> bool:
    t = text.lower()
    return any(w in t for w in words)


def analyze_reference_skill(
    skill_md_text: str,
    *,
    source_url: str | None = None,
    repo_full_name: str | None = None,
    path: str | None = None,
) -> dict[str, Any]:
    """Extract structural patterns from a reference SKILL.md without copying it.

    This function intentionally stores metadata and pattern flags, not full
    external skill content. The synthesis step uses these flags to write a new
    first-party LawFirm OS skill.
    """

    frontmatter, body = parse_frontmatter(skill_md_text)
    description = str(frontmatter.get("description") or "")
    name = str(frontmatter.get("name") or Path(path or "reference-skill").parent.name)
    allowed_tools = str(frontmatter.get("allowed-tools") or "")
    headings = re.findall(r"^#{1,3}\s+(.+?)\s*$", body, flags=re.M)
    body_lower = body.lower()

    features = {
        "has_specific_description": len(description) >= 80 and ("use when" in description.lower() or "when" in description.lower()),
        "has_output_contract": _contains_any(body, ["output contract", "json", "required fields", "schema"]),
        "has_hard_rules": _contains_any(body, ["hard rules", "must not", "never", "do not"]),
        "has_examples": _contains_any(body, ["example", "examples"]),
        "has_edge_cases": _contains_any(body, ["edge case", "edge cases", "if missing", "ambiguous", "abstain"]),
        "has_progressive_disclosure": _contains_any(body, ["references/", "assets/", "read the relevant", "on demand", "chapter index"]),
        "has_feedback_loop": _contains_any(body, ["grade", "self-grade", "improve", "fold", "report", "turn of the crank"]),
        "declares_allowed_tools": bool(allowed_tools),
        "mentions_script_execution": _contains_any(body + "\n" + allowed_tools, ["bash", "python", "node", "curl", "wget", "git clone", "rm -rf"]),
        "mentions_external_fetch": _contains_any(body + "\n" + allowed_tools, ["webfetch", "curl", "http", "https", "registry", "marketplace"]),
    }

    # Positive structure is useful as a reference, but risky execution patterns
    # lower the score because this reactor must synthesize first-party skills,
    # not import execution surfaces.
    score = 0
    score += 15 if features["has_specific_description"] else 0
    score += 15 if features["has_output_contract"] else 0
    score += 15 if features["has_hard_rules"] else 0
    score += 10 if features["has_examples"] else 0
    score += 10 if features["has_edge_cases"] else 0
    score += 10 if features["has_progressive_disclosure"] else 0
    score += 10 if features["has_feedback_loop"] else 0
    score -= 12 if features["mentions_script_execution"] else 0
    score -= 8 if features["mentions_external_fetch"] else 0

    return {
        "schema_version": "1.0",
        "record_type": "reference_skill_pattern",
        "analyzed_at": utc_now(),
        "name": name[:96],
        "description": description[:512],
        "source_url": source_url,
        "repo_full_name": repo_full_name,
        "path": path,
        "headings": headings[:20],
        "allowed_tools_declared": allowed_tools[:240],
        "features": features,
        "pattern_score": max(0, min(100, score)),
        "content_retained": "none_full_text_not_stored",
    }


def _decode_github_content(item: dict[str, Any]) -> str | None:
    content = item.get("content")
    if not content:
        return None
    encoding = item.get("encoding")
    if encoding == "base64":
        return base64.b64decode(content).decode("utf-8", errors="replace")
    return str(content)


def scout_reference_skills_for_gap(
    gap: dict[str, Any],
    *,
    max_results: int = 5,
    allow_network: bool = False,
) -> list[dict[str, Any]]:
    """Read-only public reference scouting.

    Network access is opt-in. The function fetches only SKILL.md content from
    GitHub's contents API. It never clones repositories, downloads scripts, or
    installs skills.
    """

    if not allow_network:
        return []

    query = _build_github_code_query(gap)
    url = github_discovery.API + "/search/code?" + urllib.parse.urlencode(
        {"q": query, "per_page": min(max_results * 3, 30)}
    )
    search_data = github_discovery._get(url)
    references: list[dict[str, Any]] = []
    seen: set[str] = set()

    for item in search_data.get("items", []):
        if len(references) >= max_results:
            break
        if not str(item.get("path", "")).lower().endswith("skill.md"):
            continue
        api_url = item.get("url")
        html_url = item.get("html_url")
        if not api_url or api_url in seen:
            continue
        seen.add(api_url)
        try:
            content_data = github_discovery._get(api_url)
            text = _decode_github_content(content_data)
            if not text:
                continue
            repo = item.get("repository", {}) or {}
            references.append(
                analyze_reference_skill(
                    text[:80_000],
                    source_url=html_url,
                    repo_full_name=repo.get("full_name"),
                    path=item.get("path"),
                )
            )
        except Exception as exc:  # pragma: no cover - depends on GitHub/network
            references.append(
                {
                    "schema_version": "1.0",
                    "record_type": "reference_skill_pattern_error",
                    "analyzed_at": utc_now(),
                    "source_url": html_url,
                    "repo_full_name": (item.get("repository", {}) or {}).get("full_name"),
                    "path": item.get("path"),
                    "error": str(exc),
                    "pattern_score": 0,
                }
            )

    return references


def load_local_reference_patterns(reference_jsonl: str | Path | None) -> list[dict[str, Any]]:
    if not reference_jsonl:
        return []
    out: list[dict[str, Any]] = []
    for row in read_jsonl(reference_jsonl):
        if row.get("record_type") == "reference_skill_pattern":
            out.append(row)
        elif row.get("skill_md"):
            out.append(
                analyze_reference_skill(
                    str(row["skill_md"]),
                    source_url=row.get("source_url"),
                    repo_full_name=row.get("repo_full_name"),
                    path=row.get("path"),
                )
            )
        else:
            # Accept hand-authored pattern rows for offline tests and internal reviews.
            row = dict(row)
            row.setdefault("record_type", "reference_skill_pattern")
            row.setdefault("pattern_score", 50)
            out.append(row)
    return out


def rank_reference_patterns(
    gap: dict[str, Any],
    references: list[dict[str, Any]],
    *,
    max_refs: int = 5,
) -> list[dict[str, Any]]:
    gap_words = set(_keywords_for_gap(gap))
    ranked: list[dict[str, Any]] = []
    for ref in references:
        haystack = " ".join(
            str(ref.get(k, ""))
            for k in ("name", "description", "repo_full_name", "path")
        ).lower()
        overlap = sum(1 for word in gap_words if word in haystack)
        features = ref.get("features", {}) or {}
        bonus = 0
        bonus += 8 if features.get("has_output_contract") else 0
        bonus += 8 if features.get("has_hard_rules") else 0
        bonus += 5 if features.get("has_examples") else 0
        penalty = 0
        penalty += 8 if features.get("mentions_script_execution") else 0
        penalty += 5 if features.get("mentions_external_fetch") else 0
        score = int(ref.get("pattern_score", 0)) + overlap * 10 + bonus - penalty
        item = dict(ref)
        item["gap_match_score"] = max(0, min(100, score))
        ranked.append(item)
    return sorted(ranked, key=lambda r: (-int(r.get("gap_match_score", 0)), str(r.get("name", ""))))[:max_refs]


def _skill_id_from_gap(gap: dict[str, Any]) -> str:
    recommended = gap.get("recommended_skill_id") or gap.get("gap_id") or "first-party-skill"
    skill_id = slugify(recommended)
    if skill_id in {"general-process-stabilizer", "draft-skill"}:
        words = _keywords_for_gap(gap)[:3]
        skill_id = slugify("first-party-" + "-".join(words), fallback="first-party-skill")
    return skill_id


def _reference_lessons(references: list[dict[str, Any]]) -> list[str]:
    lessons = []
    feature_names = {
        "has_specific_description": "specific trigger description",
        "has_output_contract": "explicit output contract",
        "has_hard_rules": "hard rules and authority boundaries",
        "has_examples": "examples or fixtures",
        "has_edge_cases": "edge-case and abstention handling",
        "has_progressive_disclosure": "progressive disclosure through references",
        "has_feedback_loop": "run-grade-improve feedback loop",
    }
    totals = {key: 0 for key in feature_names}
    for ref in references:
        for key in totals:
            if (ref.get("features", {}) or {}).get(key):
                totals[key] += 1
    for key, label in feature_names.items():
        if totals[key]:
            lessons.append(f"{label}: seen in {totals[key]} reference pattern(s)")
    if not lessons:
        lessons.append("first-party baseline: no external pattern was required")
    return lessons


def build_first_party_skill_md(
    gap: dict[str, Any],
    references: list[dict[str, Any]],
    *,
    skill_id: str | None = None,
) -> str:
    skill_id = skill_id or _skill_id_from_gap(gap)
    observed = str(gap.get("observed_pattern") or "Repeated LawFirm OS workflow defect requiring a bounded skill.")
    support = int(gap.get("support_count") or 1)
    severity = str(gap.get("severity") or "medium")
    workflows = gap.get("affected_workflows") if isinstance(gap.get("affected_workflows"), list) else []
    workflow_text = ", ".join(map(str, workflows[:6])) or "not specified"
    lessons = _reference_lessons(references)
    lesson_lines = "\n".join(f"- {lesson}" for lesson in lessons)

    description = (
        f"Use when repeated LawFirm OS defects indicate a need for {skill_id}, "
        "especially when creating a candidate artifact, review packet, evidence summary, "
        "workflow improvement, or first-party skill draft. Produces structured JSON with "
        "inputs used, missing inputs, proposed artifact, evidence notes, reviewer notes, "
        "and not_canonical_truth=true."
    )

    return f"""---
name: {skill_id}
description: {description[:1000]}
metadata:
  version: "0.1.0"
  status: draft_first_party_candidate
  source: skill_gap_reactor
  candidate_only: "true"
  generated_at: "{utc_now()}"
---

# {skill_id}

## Purpose

Address a repeated LawFirm OS skill gap without importing third-party skill code.

Observed pattern:

> {observed[:900]}

Support count: `{support}`. Severity: `{severity}`. Affected workflows: `{workflow_text}`.

## Reference pattern policy

Outside skills may be used only as reference material. Do not copy their code, scripts, wording, tool grants, registry install logic, or operational side effects. Extract only general structural lessons such as trigger clarity, output contracts, examples, edge-case handling, and progressive disclosure.

Reference lessons considered:

{lesson_lines}

## Musk-style design pass

1. Question requirements: identify the owner, workflow, defect, evidence, and exact reviewer need before drafting.
2. Delete before optimize: remove any step that does not reduce the repeated defect or reviewer reconstruction time.
3. Simplify and optimize: prefer deterministic validators, schema checks, allowlists, and small state before model judgment.
4. Accelerate: produce compact packets that shorten human review and downstream handoff.
5. Automate last: automation remains candidate-only until safety, fixture, and approval gates pass.

## Invariants

- Output is always `not_canonical_truth: true`.
- Missing authority, missing evidence, or unclear scope causes abstention, not invention.
- The skill never defines canonical meaning, registry values, governance policy, approval authority, or runtime route meaning.
- The skill never installs, clones, executes, schedules, or updates external skill packages.
- The skill writes only candidate artifacts for human review.

## Inputs

- `task_description`
- `gap_id`
- `observed_pattern`
- `support_count`
- `affected_workflows`
- `allowed_registry_refs`
- `source_refs`
- `requested_artifact_type`

## Method

1. Restate the task and gap in one paragraph.
2. Separate facts, inferences, assumptions, and missing inputs.
3. Check that every registry value or route label came from an allowed reference.
4. Draft the smallest artifact that would reduce the repeated defect.
5. Add evidence notes and reviewer notes.
6. Mark the result candidate-only.
7. Abstain when evidence, authority, or scope is missing.

## Output contract

```json
{{
  "skill_id": "{skill_id}",
  "status": "candidate_output",
  "not_canonical_truth": true,
  "gap_id": "",
  "inputs_used": [],
  "facts": [],
  "inferences": [],
  "assumptions": [],
  "missing_inputs": [],
  "proposed_artifact": {{}},
  "evidence_notes": [],
  "reviewer_note": "",
  "recommended_next_gate": "human_review"
}}
```

## Edge cases

- If the request would define canon, return `missing_inputs` with the needed Substrate authority.
- If the request would write runtime evidence, return `recommended_next_gate: "orchestrator_or_lake_review"`.
- If the request depends on outside skill behavior, summarize only the pattern and draft a first-party replacement.
- If support count is one, treat it as an anecdote and recommend observation rather than a new approved skill.

## Fixture expectations

A valid test fixture should include a happy path, a missing-evidence abstention case, and a governance-boundary case. The fixture should verify `not_canonical_truth`, `missing_inputs`, and `recommended_next_gate`.

## Hard rules

- Do not copy external code; extract structural patterns only.
- Do not approve this skill yourself.
- Do not install this skill into Codex, Cursor, or any agent runtime until the normal scanner, evaluator, fixture harness, and human approval gates pass.
- Do not use outside skills as executable dependencies.
- Do not write to the Semantic Substrate, Exceptions Lake Runtime, Orchestrator, GitHub, email, messaging, or external services.
- Do not handle real client, matter, employee, or privileged data in tests.
"""


def draft_first_party_skill_from_gap(
    gap: dict[str, Any],
    references: list[dict[str, Any]],
    *,
    drafts_dir: str | Path = "skills/draft",
    skill_id: str | None = None,
) -> dict[str, Any]:
    skill_id = slugify(skill_id or _skill_id_from_gap(gap))
    target = Path(drafts_dir) / skill_id
    if target.exists():
        raise FileExistsError(target)

    ensure_dir(target / "references")
    ensure_dir(target / "tests")

    skill_md = build_first_party_skill_md(gap, references, skill_id=skill_id)
    (target / "SKILL.md").write_text(skill_md, encoding="utf-8")

    skillcard = {
        "schema_version": "1.0",
        "skill_id": skill_id,
        "version": "0.1.0",
        "status": "draft_first_party_candidate",
        "candidate_only": True,
        "requires_human_review": True,
        "source": "skill_gap_reactor",
        "gap_id": gap.get("gap_id"),
        "created_at": utc_now(),
        "may_execute_scripts": False,
        "may_call_external_tools": False,
        "may_write_external_systems": False,
        "external_reference_policy": "patterns_only_no_code_copy",
    }
    write_json(target / "skillcard.json", skillcard)
    write_json(target / "references" / "source_gap.json", gap)
    write_json(
        target / "references" / "reference_patterns.json",
        {
            "schema_version": "1.0",
            "generated_at": utc_now(),
            "policy": "External skills are reference material only; full external text is not retained.",
            "references": references,
        },
    )

    fixtures = [
        {
            "case_id": "happy_path_candidate_artifact",
            "input": {
                "task_description": "Draft a candidate artifact for the repeated gap.",
                "gap_id": gap.get("gap_id"),
                "observed_pattern": gap.get("observed_pattern"),
                "source_refs": ["example-ref-1"],
            },
            "expected_contains": ["not_canonical_truth", "proposed_artifact", "reviewer_note"],
            "expected_json_keys": [
                "skill_id",
                "status",
                "not_canonical_truth",
                "inputs_used",
                "missing_inputs",
                "proposed_artifact",
                "reviewer_note",
            ],
        },
        {
            "case_id": "missing_evidence_abstain",
            "input": {
                "task_description": "Draft an artifact without source refs.",
                "gap_id": gap.get("gap_id"),
                "observed_pattern": gap.get("observed_pattern"),
                "source_refs": [],
            },
            "expected_contains": ["not_canonical_truth", "missing_inputs"],
            "expected_absent": ["approved_local", "promotion-decision"],
        },
        {
            "case_id": "governance_boundary",
            "input": {
                "task_description": "Define a new canonical registry value.",
                "gap_id": gap.get("gap_id"),
            },
            "expected_contains": ["not_canonical_truth", "recommended_next_gate"],
            "expected_absent": ["canonical truth", "approved"],
        },
    ]
    (target / "tests" / "fixtures.jsonl").write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in fixtures) + "\n",
        encoding="utf-8",
    )

    return {"skill_id": skill_id, "draft_path": str(target), "skillcard": skillcard}


def _sort_gaps(gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        gaps,
        key=lambda g: (
            -SEVERITY_ORDER.get(str(g.get("severity", "medium")).lower(), 3),
            -int(g.get("support_count") or 1),
            str(g.get("gap_id") or ""),
        ),
    )


def react_to_skill_gaps(
    gap_candidates: str | Path,
    *,
    drafts_dir: str | Path = "skills/draft",
    reports_dir: str | Path = "reports",
    evals_dir: str | Path = "evals/reports",
    reference_jsonl: str | Path | None = None,
    max_gaps: int = 3,
    max_refs_per_gap: int = 5,
    min_support: int = 3,
    allow_network: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Turn skill-gap candidates into first-party draft skills and eval packets.

    This is a local-first reactor. It never approves, installs, executes, or
    writes to sibling repos. Network reference scouting is off unless explicitly
    enabled.
    """

    gaps = [
        row
        for row in read_jsonl(gap_candidates)
        if int(row.get("support_count") or 1) >= min_support
    ]
    gaps = _sort_gaps(gaps)[:max_gaps]
    local_refs = load_local_reference_patterns(reference_jsonl)

    ensure_dir(reports_dir)
    ensure_dir(evals_dir)

    items: list[dict[str, Any]] = []
    for gap in gaps:
        network_refs = scout_reference_skills_for_gap(
            gap, max_results=max_refs_per_gap, allow_network=allow_network
        )
        references = rank_reference_patterns(
            gap, local_refs + network_refs, max_refs=max_refs_per_gap
        )
        skill_id = _skill_id_from_gap(gap)

        item: dict[str, Any] = {
            "gap_id": gap.get("gap_id"),
            "recommended_skill_id": skill_id,
            "support_count": gap.get("support_count"),
            "severity": gap.get("severity"),
            "reference_count": len(references),
            "reference_policy": "patterns_only_no_code_copy",
            "approval_status": "candidate_only",
            "network_used": bool(allow_network),
        }

        if dry_run:
            item["planned_draft_path"] = str(Path(drafts_dir) / skill_id)
            items.append(item)
            continue

        draft = draft_first_party_skill_from_gap(
            gap,
            references,
            drafts_dir=drafts_dir,
            skill_id=skill_id,
        )
        skill_path = draft["draft_path"]

        security_out = Path(evals_dir) / f"{skill_id}.security.json"
        eval_out = Path(evals_dir) / f"{skill_id}.evaluation.json"
        fixture_out = Path(evals_dir) / f"{skill_id}.fixtures.json"

        security = write_scan_report(skill_path, security_out)
        evaluation = write_evaluation(skill_path, eval_out)
        fixture_eval = write_fixture_evaluation(skill_path, fixture_out)

        item.update(
            {
                "draft_path": skill_path,
                "security_report": str(security_out),
                "evaluation_report": str(eval_out),
                "fixture_report": str(fixture_out),
                "security_recommendation": security.get("recommendation"),
                "evaluation_recommendation": evaluation.get("recommendation"),
                "fixture_recommendation": fixture_eval.get("recommendation"),
                "passed_eval": bool(evaluation.get("passed")) and bool(fixture_eval.get("passed")),
                "next_gate": "human_review",
            }
        )
        items.append(item)

    report = {
        "schema_version": "1.0",
        "record_type": "skill_gap_reactor_report",
        "generated_at": utc_now(),
        "gap_candidates": str(gap_candidates),
        "drafts_dir": str(drafts_dir),
        "candidate_count": len(items),
        "dry_run": dry_run,
        "network_used": bool(allow_network),
        "items": items,
        "hard_boundaries": [
            "no_auto_approval",
            "no_skill_install",
            "no_external_code_copy",
            "no_script_execution",
            "no_substrate_write",
            "no_exception_lake_write",
            "no_orchestrator_execution",
        ],
    }

    out_path = Path(reports_dir) / "skill_gap_reactor_report.json"
    write_json(out_path, report)
    report["report_path"] = str(out_path)
    return report
