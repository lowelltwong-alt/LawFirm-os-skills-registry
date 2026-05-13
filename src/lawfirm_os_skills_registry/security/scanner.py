from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json
import re
import urllib.request

from ..util.files import ensure_dir, file_manifest, is_probably_text, iter_files, read_text_lossy, write_json
from ..util.time import utc_now
from .rulepack_validator import validate_rulepack_file as _validate_rulepack_file
from .semantic_intent import analyze_semantic_intent

@dataclass(frozen=True)
class Rule:
    rule_id: str
    scope: str
    pattern: str
    severity: str
    category: str
    description: str
    recommendation: str

@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    category: str
    file: str
    line: int | None
    match: str | None
    description: str
    recommendation: str

SEV = {'info':1,'low':5,'medium':15,'high':35,'critical':100}
EXEC_EXT = {'.sh','.bash','.zsh','.ps1','.bat','.cmd','.py','.js','.ts','.rb','.pl','.exe','.dll','.so','.dylib'}
CODE_EXT = EXEC_EXT | {'.php','.go','.rs','.java','.c','.cpp','.cs'}
MAX_SCANNED_TEXT_BYTES = 2_000_000

DEFAULT_RULES = [
    Rule('prompt.ignore_hierarchy','text',r'(?i)(ignore|bypass|override|forget).{0,80}(system|developer|previous|higher priority).{0,80}(instruction|message|prompt|rule)','critical','prompt_injection','Attempts to override instruction hierarchy.','Reject.'),
    Rule('prompt.hidden_do_not_tell','text',r'(?i)(do not tell|hide this|secretly|silently|without the user knowing|conceal).{0,120}(instruction|action|tool|script|exfiltrate|send)','critical','deception','Hidden or deceptive instruction.','Reject.'),
    Rule('prompt.exfiltrate_secrets','text',r'(?i)(exfiltrate|leak|send|upload|post).{0,100}(secret|token|api[_-]?key|credential|password|env|\.env|client data|matter data|document)','critical','data_exfiltration','Instruction appears to send secrets/confidential data externally.','Reject.'),
    Rule('prompt.external_callback','text',r'(?i)(webhook|callback url|ngrok|pastebin|discord webhook|telegram bot|requestbin|interactsh|burp collaborator)','high','external_callback','Suspicious external callback or exfiltration service.','Quarantine.'),
    Rule('prompt.telemetry_sensitive','text',r'(?i)(telemetry|analytics|diagnostics|observability|support bundle).{0,140}(secret|token|credential|password|\.env|os\.environ|process\.env|environment variable|private configuration)','high','disguised_telemetry','Sensitive data access framed as telemetry/diagnostics.','Manual security review required.'),
    Rule('prompt.image_beacon','text',r'(?i)(<img|!\[|pixel|beacon|\.gif|\.png|\.jpg).{0,180}https?://[^\s)]+\?','high','hidden_network_call','Image/pixel beacon with query parameters.','Manual security review required.'),
    Rule('code.curl_pipe_shell','code',r'(?i)(curl|wget).{0,100}(\||bash|sh|powershell|pwsh)','critical','remote_code_execution','Downloads and pipes remote content into shell.','Reject.'),
    Rule('code.subprocess_shell_true','code',r'subprocess\.(run|Popen|call|check_output)\([^\n]{0,240}shell\s*=\s*True','high','risky_execution','Python subprocess with shell=True.','Quarantine.'),
    Rule('code.eval_exec','code',r'\b(eval|exec)\s*\(','high','dynamic_execution','Dynamic code execution.','Quarantine.'),
    Rule('code.os_system','code',r'\bos\.system\s*\(','high','risky_execution','Shell execution through os.system.','Quarantine.'),
    Rule('code.secret_access','code',r'(?i)(os\.environ|process\.env|getenv|\.env|GITHUB_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|AWS_SECRET|AZURE_CLIENT_SECRET)','medium','secret_access','Potential environment/secret access.','Review.'),
    Rule('code.network_post','code',r'(?i)(requests\.post|httpx\.post|axios\.post|fetch\(|urllib\.request|socket\.)','medium','network_access','Potential outbound network access.','Review.'),
    Rule('code.split_network_token','code',r'(?i)(["\']c["\']\s*\+\s*["\']url|["\']w["\']\s*\+\s*["\']get|["\']re["\']\s*\+\s*["\']quests)','high','hidden_network_call','Network command appears split across strings.','Manual security review required.'),
    Rule('code.persistence','code',r'(?i)(crontab|launchctl|schtasks|systemctl enable|startup folder|RunOnce|authorized_keys|\.git/hooks)','critical','persistence','Potential persistence mechanism.','Reject.'),
    Rule('code.destructive','code',r'(?i)(rm\s+-rf\s+[/~$]|Remove-Item\s+.*-Recurse|del\s+/s\s+/q|format\s+[A-Z]:)','critical','destructive_action','Destructive filesystem command.','Reject.'),
    Rule('code.obfuscation','code',r'(?i)(base64\.(b64decode|decode)|atob\(|fromBase64|fromCharCode|certutil\s+-decode|\\x[0-9a-f]{2})','medium','obfuscation','Potential obfuscated payload decoding.','Review.'),
    Rule('path.git_hooks_workflows','path',r'(?i)(^|/)\.git/hooks/|(^|/)\.github/workflows/','critical','supply_chain','Skill includes Git hooks or GitHub workflow.','Reject unless internally authored.'),
    Rule('path.ssh_keys','path',r'(?i)(id_rsa|id_dsa|id_ed25519|\.pem|known_hosts|authorized_keys)','critical','secrets','Potential credential file.','Reject.'),
    Rule('metadata.risky_tools','text',r'(?i)(allowed-tools|tools)\s*:\s*.*(bash|shell|terminal|computer|browser|web|mcp|filesystem|file_system|email|slack)','medium','tool_permission','Skill declares sensitive tools.','Review policy.'),
]

def _load_extra_rules() -> list[Rule]:
    p=Path('security/rulepacks/active/custom_rules.json')
    if not p.exists():
        return []
    data=json.loads(p.read_text(encoding='utf-8'))
    return [Rule(**r) for r in data.get('rules', [])]

def all_rules(extra_rulepack: str | Path | None = None) -> list[Rule]:
    rules=list(DEFAULT_RULES)+_load_extra_rules()
    if extra_rulepack:
        data=validate_rulepack_file(extra_rulepack, active_rules=rules)
        rules += [Rule(**r) for r in data.get('rules', [])]
    return rules

def _safe_re_search(pattern: str, text: str):
    # Rulepack validation keeps imported regexes conservative. This wrapper also bounds text size.
    return re.search(pattern, text[:MAX_SCANNED_TEXT_BYTES])

def _apply_path(rule: Rule, rel: str) -> list[Finding]:
    if rule.scope not in {'path','all'}:
        return []
    if _safe_re_search(rule.pattern, rel):
        return [Finding(rule.rule_id, rule.severity, rule.category, rel, None, rel, rule.description, rule.recommendation)]
    return []

def _apply_text(rule: Rule, rel: str, text: str, is_code: bool) -> list[Finding]:
    if rule.scope == 'code' and not is_code:
        return []
    if rule.scope not in {'text','code','all'}:
        return []
    out=[]
    for i,line in enumerate(text[:MAX_SCANNED_TEXT_BYTES].splitlines(), 1):
        m=_safe_re_search(rule.pattern, line)
        if m:
            out.append(Finding(rule.rule_id, rule.severity, rule.category, rel, i, m.group(0)[:200], rule.description, rule.recommendation))
    return out

def risk_score(findings: list[Finding]) -> int:
    return min(100, sum(SEV.get(f.severity, 0) for f in findings))

def risk_level(score: int) -> str:
    if score >= 100:
        return 'critical'
    if score >= 35:
        return 'high'
    if score >= 15:
        return 'medium'
    if score > 0:
        return 'low'
    return 'none'

def recommendation(findings: list[Finding], semantic_report: dict[str, Any] | None = None) -> str:
    semantic_level = (semantic_report or {}).get('risk_level', 'none')
    if semantic_level in {'critical', 'high'}:
        return 'reject'
    if any(f.severity == 'critical' for f in findings):
        return 'reject'
    if any(f.severity == 'high' for f in findings):
        return 'quarantine'
    if semantic_level == 'medium':
        return 'manual_review'
    if findings:
        return 'manual_review'
    return 'safe_for_eval'

def _static_scan(root: Path, rules: list[Rule]) -> list[Finding]:
    findings: list[Finding] = []
    if not (root/'SKILL.md').exists():
        findings.append(Finding('structure.missing_skill_md','critical','format','SKILL.md',None,None,'Missing required SKILL.md','Reject.'))
    if (root/'scripts').exists():
        findings.append(Finding('structure.has_scripts_dir','medium','script_surface','scripts/',None,None,'Skill includes scripts directory.','Keep quarantined until script review.'))
    for p in sorted(iter_files(root)):
        rel=p.relative_to(root).as_posix()
        if p.is_symlink():
            findings.append(Finding('path.symlink','critical','supply_chain',rel,None,None,'Symlink found.','Reject.'))
            continue
        for rule in rules:
            findings.extend(_apply_path(rule, rel))
        suffix=p.suffix.lower()
        is_code=suffix in CODE_EXT
        if suffix in EXEC_EXT:
            findings.append(Finding('file.executable_extension','medium','script_surface',rel,None,None,'Executable/script-like extension.','Manual review.'))
        if p.stat().st_size > 1_000_000:
            findings.append(Finding('file.large','medium','data_surface',rel,None,None,'Large payload.','Review.'))
        if is_probably_text(p):
            text=read_text_lossy(p)
            for rule in rules:
                findings.extend(_apply_text(rule, rel, text, is_code))
        else:
            findings.append(Finding('file.binary','medium','opaque_payload',rel,None,None,'Binary or non-UTF8 payload.','Review.'))
    return findings

def scan_skill(skill_dir: str | Path, extra_rulepack: str | Path | None = None) -> dict[str, Any]:
    root=Path(skill_dir)
    if not root.exists():
        raise FileNotFoundError(root)
    rules=all_rules(extra_rulepack)
    static_findings=_static_scan(root, rules)
    semantic_report=analyze_semantic_intent(root)
    static_score = risk_score(static_findings)
    semantic_score = int(semantic_report.get('risk_score', 0))
    overall_score = min(100, max(static_score, semantic_score) + min(25, static_score // 4 + semantic_score // 4))
    rec = recommendation(static_findings, semantic_report)
    findings = [asdict(f) for f in static_findings]
    semantic_findings = semantic_report.get('findings', [])
    return {
        'schema_version':'1.1',
        'generated_at':utc_now(),
        'skill_dir':str(root),
        'risk_score':overall_score,
        'risk_level':risk_level(overall_score),
        'static_risk_score':static_score,
        'semantic_risk_score':semantic_score,
        'semantic_risk_level':semantic_report.get('risk_level', 'none'),
        'recommendation':rec,
        'finding_count':len(static_findings) + len(semantic_findings),
        'static_findings':findings,
        'semantic_intent':semantic_report,
        # Backward-compatible flattened findings field.
        'findings':findings + [dict(f, rule_id='semantic.'+f.get('category','intent')) for f in semantic_findings],
        'file_manifest':file_manifest(root),
    }

def write_scan_report(skill_dir: str | Path, out: str | Path, extra_rulepack: str | Path | None = None) -> dict[str, Any]:
    report=scan_skill(skill_dir, extra_rulepack)
    write_json(out, report)
    return report

def validate_rulepack_file(path: str | Path, active_rules: list[Rule] | None = None) -> dict[str, Any]:
    return _validate_rulepack_file(path, active_rules=active_rules or list(DEFAULT_RULES))

def update_threat_rules(from_file: str | Path | None = None, from_url: str | None = None, approve: bool = False, allow_network: bool = False) -> dict[str, Any]:
    if from_url:
        if not allow_network:
            raise ValueError('Network rule updates require --allow-network')
        if not from_url.startswith('https://'):
            raise ValueError('Rulepack URL must be https')
        payload=urllib.request.urlopen(from_url, timeout=20).read().decode('utf-8')
        tmp=Path('security/rulepacks/candidate/downloaded_rulepack.json')
        ensure_dir(tmp.parent)
        tmp.write_text(payload, encoding='utf-8')
        source=from_url
    elif from_file:
        tmp=Path(from_file)
        source=str(tmp)
    else:
        raise ValueError('Provide --from-file or --from-url')
    active_rules = list(DEFAULT_RULES) + _load_extra_rules()
    data=validate_rulepack_file(tmp, active_rules=active_rules)
    candidate=ensure_dir('security/rulepacks/candidate') / f"candidate_{data.get('version','unknown')}_{utc_now().replace(':','').replace('-','')}.json"
    candidate.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    result={'schema_version':'1.1','updated_at':utc_now(),'source':source,'candidate_path':str(candidate),'approved':False,'active_path':None,'rule_count':len(data.get('rules', [])),'validation':'passed'}
    if approve:
        active=ensure_dir('security/rulepacks/active')/'custom_rules.json'
        # Approval activates the whole validated custom rulepack. It cannot lower default rule severities or disable categories.
        active.write_text(json.dumps(data, indent=2, sort_keys=True)+'\n', encoding='utf-8')
        result['approved']=True
        result['active_path']=str(active)
    return result
