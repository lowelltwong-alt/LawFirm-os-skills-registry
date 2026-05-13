from pathlib import Path
from lawfirm_os_skills_registry.governance.design_algorithm import grade_algorithm_text, grade_skill_algorithm


def test_musk_order_rewards_delete_before_automate():
    text='Question every requirement. Delete unnecessary steps. Simplify and optimize. Accelerate cycle time. Automate last. Keep invariants, schema validators, evidence hashes, JSON output.'
    r=grade_algorithm_text(text)
    assert r['scores']['overall'] >= 70
    assert not r['penalties']


def test_automation_before_control_penalized():
    text='Fully autonomous. Automate everything. Skip approval. Use any tool and all available context.'
    r=grade_algorithm_text(text)
    assert r['scores']['overall'] < 50
    assert 'automation_before_control' in r['penalties']


def test_grade_skill_algorithm(tmp_path: Path):
    d=tmp_path/'good-skill'; d.mkdir()
    (d/'SKILL.md').write_text('---\nname: good-skill\ndescription: Use when reviewing a workflow. Produces JSON output.\n---\nQuestion every requirement. Delete unnecessary steps. Simplify and optimize. Accelerate cycle time. Automate last. Invariant: fail closed. Deterministic schema validator. Evidence refs. Output contract JSON.', encoding='utf-8')
    r=grade_skill_algorithm(d)
    assert r['recommendation'] in {'excellent','approve_for_review'}
