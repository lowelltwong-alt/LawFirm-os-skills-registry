from __future__ import annotations
from pathlib import Path
from .discovery.local import discover_local, write_discovered
from .discovery.github import scout_github, write_github_results, import_github_skill
from .intake.importer import import_skill
from .security.scanner import write_scan_report, update_threat_rules
from .evaluation.evaluator import write_evaluation
from .governance.design_algorithm import write_algorithm_grade
from .registry.store import approve_skill, list_approved, install_codex_skills
from .gap_detection.detector import detect_skill_gaps, write_skill_gaps
from .factory.drafter import draft_skill_from_gap_file

def ask(label, default=None):
    s=f' [{default}]' if default is not None else ''
    v=input(f'{label}{s}: ').strip()
    return v or (default or '')

def console():
    print('\nLawFirm OS Skills Registry Console')
    print('quarantine-first | malicious-skill scan | elegance gate | no script execution\n')
    while True:
        print('1. Discover local skills')
        print('2. Scout GitHub for SKILL.md')
        print('3. Import local skill into quarantine')
        print('4. Import GitHub skill into quarantine')
        print('5. Scan skill for malicious code/injection')
        print('6. Evaluate skill quality + elegance')
        print('7. Grade algorithm/design only')
        print('8. Approve skill')
        print('9. Detect skill gaps')
        print('10. Draft skill from gap')
        print('11. Update threat rules')
        print('12. Install approved skills into Codex/Cursor repo')
        print('13. List approved skills')
        print('0. Quit')
        c=ask('Choose')
        try:
            if c=='1':
                source=ask('Source folder','examples/external_skills'); out=ask('Output JSONL','registry/discovered-skills.jsonl')
                rows=discover_local(source); write_discovered(rows,out); print(f'Discovered {len(rows)} -> {out}')
            elif c=='2':
                q=ask('GitHub query','filename:SKILL.md "description:" "name:"'); out=ask('Output JSONL','registry/discovered-skills.jsonl')
                rows=scout_github(q); write_github_results(rows,out,append=True); print(f'Found {len(rows)} -> {out}')
            elif c=='3': print(import_skill(ask('Skill folder'), ask('Quarantine folder','quarantine')))
            elif c=='4': print({'imported_path': str(import_github_skill(ask('Repo owner/name'), ask('Skill directory path'), ask('Ref','main'), ask('Target quarantine folder','quarantine/imported-github-skill')))})
            elif c=='5':
                skill=ask('Skill folder'); out=ask('Security report',f'evals/reports/{Path(skill).name}.security.json')
                r=write_scan_report(skill,out); print(f"risk={r['risk_score']} recommendation={r['recommendation']} -> {out}")
            elif c=='6':
                skill=ask('Skill folder'); out=ask('Evaluation report',f'evals/reports/{Path(skill).name}.evaluation.json')
                r=write_evaluation(skill,out); print(f"overall={r['scores']['overall']} recommendation={r['recommendation']} -> {out}")
            elif c=='7':
                skill=ask('Skill folder'); out=ask('Algorithm grade',f'evals/reports/{Path(skill).name}.algorithm.json')
                r=write_algorithm_grade(skill,out); print(f"overall={r['scores']['overall']} recommendation={r['recommendation']} -> {out}")
            elif c=='8': print(approve_skill(ask('Skill folder'), ask('Evaluation report'), approve=(ask('Type APPROVE')=='APPROVE')))
            elif c=='9':
                clusters=ask('Exception clusters JSONL','examples/exception_clusters.jsonl'); out=ask('Output gaps','reports/skill_gap_candidates.jsonl')
                rows=detect_skill_gaps(clusters); write_skill_gaps(rows,out); print(f'Wrote {len(rows)} -> {out}')
            elif c=='10': print(draft_skill_from_gap_file(ask('Gap candidates JSONL','reports/skill_gap_candidates.jsonl'), ask('Gap id blank for first','') or None))
            elif c=='11': print(update_threat_rules(ask('Rulepack file'), None, approve=(ask('Type APPROVE to activate, blank to stage','')=='APPROVE')))
            elif c=='12': print(install_codex_skills('registry/approved-skills.json', ask('Target repo path')))
            elif c=='13': print(list_approved())
            elif c=='0': return 0
        except Exception as exc: print('ERROR:', exc)
        print()
