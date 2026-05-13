from __future__ import annotations

import base64
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..util.files import is_probably_text, iter_files, read_text_lossy
from ..util.time import utc_now

SEVERITY_SCORE = {"info": 1, "low": 5, "medium": 15, "high": 35, "critical": 100}

ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\ufeff]")
BASE64_CANDIDATE = re.compile(r"(?<![A-Za-z0-9+/])(?:[A-Za-z0-9+/]{32,}={0,2})(?![A-Za-z0-9+/])")
HEX_ESCAPE = re.compile(r"(?:\\\\x[0-9a-fA-F]{2}){4,}")
CHAR_CODE = re.compile(r"(?i)(?:fromCharCode|chr)\s*\(([^)]{5,300})\)")

SECRET_TERMS = [
    "secret", "secrets", "credential", "credentials", "api key", "api_key", "apikey", "token",
    "password", ".env", "env file", "environment variable", "environment variables", "os.environ",
    "process.env", "getenv", "private configuration", "private config", "auth header", "session cookie",
    "github_token", "openai_api_key", "anthropic_api_key", "aws_secret", "client data", "matter data",
    "privileged document", "confidential document", "local files", "local file", "ssh key", "pem file",
]

DATA_TERMS = [
    "document", "documents", "file", "files", "payload", "data", "content", "attachment", "matter",
    "client", "transcript", "prompt", "conversation", "workspace", "repository", "config", "configuration",
]

MOVEMENT_TERMS = [
    "send", "post", "upload", "transmit", "deliver", "forward", "share", "report", "sync", "mirror",
    "copy", "export", "transfer", "publish", "log", "beacon", "ping", "callback", "phone home",
    "make available", "make them available", "collect", "gather", "harvest", "summarize and submit",
]

REMOTE_TERMS = [
    "http://", "https://", "url", "webhook", "endpoint", "remote", "external", "outside", "third party",
    "third-party", "network", "callback", "requestbin", "interactsh", "ngrok", "pastebin", "discord",
    "telegram", "cdn", "image", "pixel", "tracking", "analytics", "telemetry", "diagnostics", "support service",
    "maintenance service", "observability", "monitoring",
]

TELEMETRY_TERMS = [
    "telemetry", "analytics", "diagnostics", "observability", "monitoring", "support bundle", "health check",
    "usage report", "maintenance", "debug report", "crash report", "performance report",
]

OVERRIDE_TERMS = [
    "ignore", "bypass", "override", "forget", "disregard", "do not follow", "do not obey", "higher priority",
    "system instruction", "developer instruction", "security policy", "policy gate", "approval gate", "conceal",
    "do not tell", "hide this", "secretly", "silently", "without the user knowing", "do not inspect",
    "do not review", "skip review", "skip security", "future agent", "future reviewer", "do not mention",
]

EXECUTION_TERMS = [
    "subprocess", "os.system", "shell", "bash", "powershell", "eval(", "exec(", "python -c", "node -e",
    "chmod", "curl", "wget", "requests.post", "urllib.request", "fetch(", "axios.post", "socket.",
]

PERSISTENCE_TERMS = [
    "cron", "crontab", "launchctl", "schtasks", "systemctl enable", "startup folder", "runonce",
    "authorized_keys", ".git/hooks", "post-commit", "pre-commit", "github workflows", ".github/workflows",
]

ENCODING_TERMS = [
    "base64", "b64decode", "atob", "fromcharcode", "charcode", "hex", "\\x", "rot13", "certutil -decode",
]

@dataclass(frozen=True)
class SemanticIntentFinding:
    severity: str
    category: str
    file: str
    line: int | None
    evidence: str
    description: str
    recommendation: str


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _find_line(raw_text: str, needle: str) -> int | None:
    n = needle.lower()[:80]
    for i, line in enumerate(raw_text.splitlines(), 1):
        if n and n in line.lower():
            return i
    return None


def _compact(text: str) -> str:
    """Normalize text and undo simple token splitting such as 'c' + 'url'."""
    text = ZERO_WIDTH.sub("", text)
    lower = text.lower()
    # Remove common string-concatenation noise. This catches c + url, w + get, re + quests, etc.
    compact = re.sub(r"[\s'\"`+._\-\\/]+", "", lower)
    return compact


def _decode_base64_candidates(text: str) -> list[str]:
    decoded: list[str] = []
    seen = set()
    for match in BASE64_CANDIDATE.finditer(text):
        token = match.group(0)
        if token in seen or len(token) > 8000:
            continue
        seen.add(token)
        padded = token + "=" * ((4 - len(token) % 4) % 4)
        try:
            raw = base64.b64decode(padded, validate=False)
            if not raw:
                continue
            out = raw.decode("utf-8", errors="ignore")
            printable = sum(1 for c in out if c.isprintable() or c in "\r\n\t")
            if len(out) >= 8 and printable / max(len(out), 1) > 0.75:
                decoded.append(out[:2000])
        except Exception:
            continue
        if len(decoded) >= 20:
            break
    return decoded


def _decode_hex_escapes(text: str) -> list[str]:
    out = []
    for match in HEX_ESCAPE.finditer(text):
        seq = match.group(0).replace("\\x", "")
        try:
            out.append(bytes.fromhex(seq).decode("utf-8", errors="ignore")[:1000])
        except Exception:
            continue
    return out[:20]


def _decode_char_codes(text: str) -> list[str]:
    out = []
    for match in CHAR_CODE.finditer(text):
        nums = re.findall(r"\d{2,3}", match.group(1))
        if 3 <= len(nums) <= 200:
            try:
                out.append("".join(chr(int(n)) for n in nums if 0 <= int(n) <= 255)[:1000])
            except Exception:
                continue
    return out[:20]


def _augmented_text(raw: str) -> tuple[str, list[str]]:
    decoded = _decode_base64_candidates(raw) + _decode_hex_escapes(raw) + _decode_char_codes(raw)
    joined = raw + "\n" + "\n".join(decoded)
    return ZERO_WIDTH.sub("", joined).lower(), decoded


def _add(findings: list[SemanticIntentFinding], severity: str, category: str, rel: str, line: int | None, evidence: str, description: str, recommendation: str) -> None:
    findings.append(SemanticIntentFinding(severity, category, rel, line, evidence[:240], description, recommendation))


def _scan_text(rel: str, raw_text: str) -> list[SemanticIntentFinding]:
    findings: list[SemanticIntentFinding] = []
    text, decoded_payloads = _augmented_text(raw_text)
    compact = _compact(raw_text + "\n" + "\n".join(decoded_payloads))

    has_secret = _contains_any(text, SECRET_TERMS) or _contains_any(compact, [t.replace(" ", "") for t in SECRET_TERMS])
    has_data = _contains_any(text, DATA_TERMS)
    has_move = _contains_any(text, MOVEMENT_TERMS)
    has_remote = _contains_any(text, REMOTE_TERMS) or "http://" in text or "https://" in text
    has_telemetry = _contains_any(text, TELEMETRY_TERMS)
    has_exec = _contains_any(text, EXECUTION_TERMS) or _contains_any(compact, ["curl", "wget", "requestspost", "urllibrequest", "fetch(", "axiospost"])
    has_encoding = _contains_any(text, ENCODING_TERMS) or bool(decoded_payloads)

    if has_secret and has_move and (has_remote or has_telemetry):
        _add(findings, "critical", "secret_exfiltration", rel, None,
             "secret/data terms + movement terms + remote/telemetry terms",
             "Skill appears to move secrets, credentials, or private configuration outside the local trust boundary.",
             "Reject or require security-owner override.")
    elif has_data and has_move and has_remote:
        _add(findings, "high", "data_exfiltration", rel, None,
             "data terms + movement terms + remote terms",
             "Skill appears to move data to a remote destination.", "Manual security review required.")

    if has_telemetry and (has_secret or "os.environ" in text or "process.env" in text or ".env" in text or "local file" in text or "private" in text):
        _add(findings, "high", "disguised_telemetry", rel, None,
             "telemetry/diagnostics language combined with sensitive local state",
             "Potential social-engineering disguise: secret collection framed as telemetry or diagnostics.",
             "Reject or require security-owner override.")

    if re.search(r"(?i)(<img|!\[|image|pixel|beacon|\.gif|\.png|\.jpg|\.jpeg).{0,200}https?://[^\s)]+\?", raw_text, re.S):
        _add(findings, "high", "hidden_network_call", rel, None,
             "image/pixel/beacon URL with query parameters",
             "Potential image beacon or URL-query exfiltration channel.", "Manual security review required.")

    if has_encoding and (has_exec or has_secret or has_remote):
        _add(findings, "high", "encoded_payload", rel, None,
             "encoded payload indicators combined with execution/secret/network indicators",
             "Potential encoded or obfuscated payload hiding execution or exfiltration behavior.",
             "Manual security review required.")

    if any(token in compact for token in ["curlhttp", "wgethttp", "requestspost", "urllibrequest", "axiospost", "fetch(http"]):
        _add(findings, "high", "hidden_network_call", rel, None,
             "split or compacted network command token",
             "Potential command or network call constructed through token splitting.", "Manual security review required.")

    if _contains_any(text, OVERRIDE_TERMS):
        if any(term in text for term in ["system", "developer", "policy", "approval", "security", "review", "higher priority"]):
            _add(findings, "critical", "instruction_hierarchy_override", rel, None,
                 "instruction override or review-bypass language",
                 "Skill attempts to override higher-priority instructions or security review.", "Reject.")
        else:
            _add(findings, "high", "prompt_injection", rel, None,
                 "hidden/deceptive instruction language",
                 "Skill includes hidden or deceptive instructions that could manipulate future agents.",
                 "Manual security review required.")

    if has_exec and (has_remote or has_secret):
        _add(findings, "high", "code_execution", rel, None,
             "execution terms combined with remote or secret access",
             "Potential executable behavior touching network or secrets.", "Manual security review required.")

    if _contains_any(text, PERSISTENCE_TERMS):
        _add(findings, "critical", "persistence", rel, None,
             "persistence mechanism terms",
             "Skill appears to create persistence or alter repository automation hooks/workflows.", "Reject.")

    # Assign line numbers where possible after category-level detection.
    if findings:
        fixed = []
        for f in findings:
            candidate_terms = SECRET_TERMS + MOVEMENT_TERMS + REMOTE_TERMS + OVERRIDE_TERMS + EXECUTION_TERMS + PERSISTENCE_TERMS
            line = f.line
            for term in candidate_terms:
                if term in text:
                    line = _find_line(raw_text, term)
                    if line:
                        break
            fixed.append(SemanticIntentFinding(f.severity, f.category, f.file, line, f.evidence, f.description, f.recommendation))
        return fixed
    return findings


def risk_score(findings: list[SemanticIntentFinding]) -> int:
    return min(100, sum(SEVERITY_SCORE.get(f.severity, 0) for f in findings))


def risk_level(score: int) -> str:
    if score >= 100:
        return "critical"
    if score >= 35:
        return "high"
    if score >= 15:
        return "medium"
    if score > 0:
        return "low"
    return "none"


def analyze_semantic_intent(skill_dir: str | Path) -> dict[str, Any]:
    root = Path(skill_dir)
    findings: list[SemanticIntentFinding] = []
    if not root.exists():
        raise FileNotFoundError(root)
    for path in sorted(iter_files(root)):
        if path.is_symlink():
            continue
        rel = path.relative_to(root).as_posix()
        if not is_probably_text(path):
            continue
        # Bound input size for safety and determinism.
        text = read_text_lossy(path)
        if len(text) > 2_000_000:
            text = text[:2_000_000]
            findings.append(SemanticIntentFinding(
                "medium", "oversized_text_surface", rel, None, "file truncated for semantic scan",
                "Large text payload may hide malicious instructions after normal review depth.", "Manual review required."
            ))
        findings.extend(_scan_text(rel, text))
    score = risk_score(findings)
    level = risk_level(score)
    if level in {"critical", "high"}:
        recommendation = "reject_or_security_review"
    elif level == "medium":
        recommendation = "manual_review_required"
    else:
        recommendation = "allow_for_static_evaluation"
    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "skill_dir": str(root),
        "risk_score": score,
        "risk_level": level,
        "recommendation": recommendation,
        "finding_count": len(findings),
        "findings": [asdict(f) for f in findings],
    }
