from pathlib import Path
import json, pytest
from lawfirm_os_skills_registry.domain.skill_trust_record import SkillTrustError
from lawfirm_os_skills_registry.registry.store import approve_skill
from lawfirm_os_skills_registry.gap_detection.detector import detect_skill_gaps
from lawfirm_os_skills_registry.factory.drafter import draft_skill_from_gap


def test_approve_requires_flag(tmp_path: Path):
    d=tmp_path/'ok-skill'; d.mkdir()
    (d/'SKILL.md').write_text('---\nname: ok-skill\ndescription: Use when testing approval. Produces JSON output.\n---\nOutput JSON.', encoding='utf-8')
    report=tmp_path/'eval.json'; report.write_text(json.dumps({'passed':True,'security':{'risk_score':0}}), encoding='utf-8')
    with pytest.raises(PermissionError):
        approve_skill(d, report, approved_dir=tmp_path / "approved", registry_path=tmp_path / "reg.json", approve=False)
    with pytest.raises(SkillTrustError):
        approve_skill(
            d,
            report,
            approved_dir=tmp_path / "approved",
            registry_path=tmp_path / "reg.json",
            approve=True,
        )


def test_gap_candidate_only_and_draft_not_approved(tmp_path: Path):
    f=tmp_path/'clusters.jsonl'
    f.write_text('{"cluster_id":"c1","observed_pattern":"Repeated evidence packets missing source refs.","support_count":5}\n', encoding='utf-8')
    rows=detect_skill_gaps(f)
    assert rows[0]['candidate_only'] is True
    out=draft_skill_from_gap(rows[0], tmp_path/'drafts')
    assert out['skillcard']['status'] == 'draft'
