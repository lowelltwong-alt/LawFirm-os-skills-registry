from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SEVERITY_SCORE = {"info": 1, "low": 5, "medium": 15, "high": 35, "critical": 100}
ALLOWED_SCOPES = {"text", "code", "path", "all"}
ALLOWED_TOP_LEVEL = {"schema_version", "version", "name", "description", "source", "rules"}
ALLOWED_RULE_FIELDS = {"rule_id", "scope", "pattern", "severity", "category", "description", "recommendation"}
DISALLOWED_TOP_LEVEL = {
    "disabled_categories", "disable_categories", "allowlist", "global_allowlist", "allow_all", "scanner_disabled",
    "disable_scanner", "severity_overrides", "approval_policy", "auto_approve", "auto_promote", "bypass",
}
MAX_RULES = 250
MAX_PATTERN_LENGTH = 320
MAX_DESCRIPTION_LENGTH = 1200

@dataclass(frozen=True)
class RulepackValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    rule_count: int


def is_potentially_redos(pattern: str) -> bool:
    """Conservative heuristic for unsafe regexes.

    It intentionally catches obvious ReDoS-prone patterns rather than trying to prove safety.
    """
    if len(pattern) > MAX_PATTERN_LENGTH:
        return True
    # Backreferences can make matching much harder to reason about.
    if re.search(r"(?<!\\)\\[1-9]", pattern):
        return True
    # Complex lookarounds are disallowed for imported rulepacks.
    if any(x in pattern for x in ["(?=", "(?!", "(?<=", "(?<!"]):
        return True
    # Nested quantifiers: (a+)+, (.*)+, (.{0,10})*, ((abc)*)+, etc.
    if re.search(r"\([^)]*(?:\+|\*|\{\d*,?\d*\})[^)]*\)\s*(?:\+|\*|\{\d*,?\d*\})", pattern):
        return True
    # Ambiguous repeated wildcard / dot groups.
    if re.search(r"\((?:\.\*|\.\+|\[\^\]]+\]\*)\)\s*(?:\+|\*|\{)", pattern):
        return True
    # Repeated alternation group can be expensive, especially with overlapping alternatives.
    if re.search(r"\([^)]*\|[^)]*\)\s*(?:\+|\*|\{)", pattern):
        return True
    # Adjacent repeated wildcards are another common smell.
    if re.search(r"(?:\.\*|\.\+).{0,20}(?:\.\*|\.\+)", pattern):
        return True
    return False


def _time_smoke_test(compiled: re.Pattern[str]) -> bool:
    probes = [
        "a" * 500 + "!",
        "a" * 1000 + "!",
        ("abc" * 400) + "!",
        ("0" * 1000) + "!",
    ]
    start = time.perf_counter()
    for probe in probes:
        compiled.search(probe)
        if time.perf_counter() - start > 0.05:
            return False
    return True


def _active_severity_map(active_rules: Iterable[Any] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    if not active_rules:
        return out
    for rule in active_rules:
        rid = getattr(rule, "rule_id", None) or (rule.get("rule_id") if isinstance(rule, dict) else None)
        sev = getattr(rule, "severity", None) or (rule.get("severity") if isinstance(rule, dict) else None)
        if rid and sev:
            out[str(rid)] = str(sev)
    return out


def validate_rulepack_data(data: dict[str, Any], active_rules: Iterable[Any] | None = None) -> RulepackValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return RulepackValidationResult(False, ["Rulepack root must be an object"], [], 0)
    unknown_top = set(data) - ALLOWED_TOP_LEVEL
    bad_top = set(data) & DISALLOWED_TOP_LEVEL
    if unknown_top:
        errors.append(f"Unknown top-level fields are not allowed: {sorted(unknown_top)}")
    if bad_top:
        errors.append(f"Disallowed top-level scanner-control fields: {sorted(bad_top)}")
    rules = data.get("rules")
    if not isinstance(rules, list):
        errors.append("Rulepack requires rules list")
        return RulepackValidationResult(False, errors, warnings, 0)
    if len(rules) > MAX_RULES:
        errors.append(f"Rulepack has too many rules: {len(rules)} > {MAX_RULES}")
    active_sev = _active_severity_map(active_rules)
    seen: set[str] = set()
    for idx, rule in enumerate(rules):
        prefix = f"rules[{idx}]"
        if not isinstance(rule, dict):
            errors.append(f"{prefix} must be an object")
            continue
        unknown_rule = set(rule) - ALLOWED_RULE_FIELDS
        if unknown_rule:
            errors.append(f"{prefix} has unknown fields: {sorted(unknown_rule)}")
        for key in ALLOWED_RULE_FIELDS:
            if key not in rule:
                errors.append(f"{prefix} missing {key}")
        if errors and any(e.startswith(prefix) for e in errors):
            continue
        rid = str(rule["rule_id"])
        scope = str(rule["scope"])
        pattern = str(rule["pattern"])
        severity = str(rule["severity"])
        if rid in seen:
            errors.append(f"Duplicate rule_id in rulepack: {rid}")
        seen.add(rid)
        if scope not in ALLOWED_SCOPES:
            errors.append(f"{rid} has invalid scope: {scope}")
        if severity not in SEVERITY_SCORE:
            errors.append(f"{rid} has invalid severity: {severity}")
        if rid in active_sev and SEVERITY_SCORE.get(severity, 0) < SEVERITY_SCORE.get(active_sev[rid], 0):
            errors.append(f"{rid} attempts to lower active severity from {active_sev[rid]} to {severity}")
        if len(pattern) > MAX_PATTERN_LENGTH:
            errors.append(f"{rid} pattern exceeds max length {MAX_PATTERN_LENGTH}")
        if len(str(rule.get("description", ""))) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"{rid} description exceeds max length {MAX_DESCRIPTION_LENGTH}")
        if is_potentially_redos(pattern):
            errors.append(f"{rid} pattern rejected as potentially ReDoS-prone or too complex")
            continue
        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            errors.append(f"{rid} regex compile failed: {exc}")
            continue
        if not _time_smoke_test(compiled):
            errors.append(f"{rid} regex failed time-budget smoke test")
    return RulepackValidationResult(not errors, errors, warnings, len(rules))


def validate_rulepack_file(path: str | Path, active_rules: Iterable[Any] | None = None) -> dict[str, Any]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    result = validate_rulepack_data(data, active_rules=active_rules)
    if not result.valid:
        raise ValueError("Invalid rulepack: " + "; ".join(result.errors))
    return data
