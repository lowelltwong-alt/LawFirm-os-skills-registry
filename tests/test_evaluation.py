from pathlib import Path
from lawfirm_os_skills_registry.evaluation.evaluator import evaluate_skill


def test_missing_description_fails(tmp_path: Path):
    d=tmp_path/'no-description'; d.mkdir()
    (d/'SKILL.md').write_text('---\nname: no-description\n---\nBody', encoding='utf-8')
    r=evaluate_skill(d)
    assert not r['passed']
    assert 'missing description' in r['errors']


def test_evaluation_contains_elegance_score(tmp_path: Path):
    d=tmp_path/'review-skill'; d.mkdir()
    (d/'SKILL.md').write_text('---\nname: review-skill\ndescription: Use when reviewing evidence packets and workflow defects. Produces a JSON report with evidence refs and reviewer note.\n---\nQuestion every requirement. Delete unnecessary steps. Simplify and optimize. Accelerate cycle time. Automate last. Use schema validators, fail closed, preserve evidence hashes. Output contract JSON. Do not invent canonical truth. Edge case: missing evidence means abstain.', encoding='utf-8')
    r=evaluate_skill(d)
    assert 'algorithmic_elegance' in r['scores']
