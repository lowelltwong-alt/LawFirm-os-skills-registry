from __future__ import annotations
import argparse, json
from pathlib import Path
from .console import console
from .discovery.local import discover_local, write_discovered
from .discovery.github import scout_github, write_github_results, import_github_skill
from .intake.importer import import_skill
from .security.scanner import write_scan_report, update_threat_rules
from .evaluation.evaluator import write_evaluation
from .governance.design_algorithm import write_algorithm_grade
from .registry.store import approve_skill, list_approved, install_codex_skills
from .gap_detection.detector import detect_skill_gaps, write_skill_gaps
from .factory.drafter import draft_skill_from_gap_file
from .factory.first_party_reactor import react_to_skill_gaps
from .evaluation.fixture_harness import write_fixture_evaluation

def pj(obj): print(json.dumps(obj, indent=2, sort_keys=True))

def parser():
    p=argparse.ArgumentParser(prog='lawfirm-os-skills')
    s=p.add_subparsers(dest='cmd', required=True)
    s.add_parser('console')
    a=s.add_parser('discover-local'); a.add_argument('--source', required=True); a.add_argument('--out', default='registry/discovered-skills.jsonl')
    a=s.add_parser('scout-github'); a.add_argument('--query', required=True); a.add_argument('--max-results', type=int, default=25); a.add_argument('--out', default='registry/discovered-skills.jsonl'); a.add_argument('--replace', action='store_true')
    a=s.add_parser('import-github-skill'); a.add_argument('--repo', required=True); a.add_argument('--path', required=True); a.add_argument('--ref', default='main'); a.add_argument('--target', default=None)
    a=s.add_parser('import-skill'); a.add_argument('--source', required=True); a.add_argument('--quarantine', default='quarantine')
    a=s.add_parser('scan-skill'); a.add_argument('--skill', required=True); a.add_argument('--out', required=True); a.add_argument('--extra-rulepack')
    a=s.add_parser('update-threat-rules'); a.add_argument('--from-file'); a.add_argument('--from-url'); a.add_argument('--allow-network', action='store_true'); a.add_argument('--approve', action='store_true')
    a=s.add_parser('evaluate-skill'); a.add_argument('--skill', required=True); a.add_argument('--out', required=True)
    a=s.add_parser('grade-algorithm'); a.add_argument('--skill', required=True); a.add_argument('--out', required=True)
    a=s.add_parser('approve-skill'); a.add_argument('--skill', required=True); a.add_argument('--evaluation', required=True); a.add_argument('--approved-dir', default='skills/approved'); a.add_argument('--registry', default='registry/approved-skills.json'); a.add_argument('--approve', action='store_true')
    a=s.add_parser('list-approved'); a.add_argument('--registry', default='registry/approved-skills.json')
    a=s.add_parser('install-codex-skills'); a.add_argument('--registry', default='registry/approved-skills.json'); a.add_argument('--target-repo', required=True); a.add_argument('--include-scripts', action='store_true'); a.add_argument('--approve-scripts', action='store_true')
    a=s.add_parser('detect-skill-gaps'); a.add_argument('--clusters', required=True); a.add_argument('--out', default='reports/skill_gap_candidates.jsonl'); a.add_argument('--min-support', type=int, default=3)
    a=s.add_parser('draft-skill'); a.add_argument('--gap-candidates', required=True); a.add_argument('--gap-id'); a.add_argument('--drafts-dir', default='skills/draft')
    a=s.add_parser('react-skill-gap'); a.add_argument('--gap-candidates', required=True); a.add_argument('--drafts-dir', default='skills/draft'); a.add_argument('--reports-dir', default='reports'); a.add_argument('--evals-dir', default='evals/reports'); a.add_argument('--reference-jsonl'); a.add_argument('--max-gaps', type=int, default=3); a.add_argument('--max-refs-per-gap', type=int, default=5); a.add_argument('--min-support', type=int, default=3); a.add_argument('--allow-network', action='store_true'); a.add_argument('--dry-run', action='store_true')
    a=s.add_parser('evaluate-skill-fixtures'); a.add_argument('--skill', required=True); a.add_argument('--out', required=True)
    return p

def main(argv=None):
    args=parser().parse_args(argv)
    if args.cmd=='console': return console()
    if args.cmd=='discover-local': rows=discover_local(args.source); write_discovered(rows,args.out); pj({'discovered_count':len(rows),'out':args.out}); return 0
    if args.cmd=='scout-github': rows=scout_github(args.query,args.max_results); write_github_results(rows,args.out,append=not args.replace); pj({'discovered_count':len(rows),'out':args.out}); return 0
    if args.cmd=='import-github-skill': target=args.target or f"quarantine/{Path(args.path).name}"; p=import_github_skill(args.repo,args.path,args.ref,target); pj({'imported_path':str(p)}); return 0
    if args.cmd=='import-skill': pj(import_skill(args.source,args.quarantine)); return 0
    if args.cmd=='scan-skill': r=write_scan_report(args.skill,args.out,args.extra_rulepack); pj({'out':args.out,'risk_score':r['risk_score'],'recommendation':r['recommendation'],'finding_count':r['finding_count']}); return 0
    if args.cmd=='update-threat-rules': pj(update_threat_rules(args.from_file,args.from_url,args.approve,args.allow_network)); return 0
    if args.cmd=='evaluate-skill': r=write_evaluation(args.skill,args.out); pj({'out':args.out,'passed':r['passed'],'recommendation':r['recommendation'],'overall':r['scores']['overall'],'algorithmic_elegance':r['scores']['algorithmic_elegance']}); return 0
    if args.cmd=='grade-algorithm': r=write_algorithm_grade(args.skill,args.out); pj({'out':args.out,'recommendation':r['recommendation'],'overall':r['scores']['overall'],'penalties':r['penalties']}); return 0
    if args.cmd=='approve-skill': pj(approve_skill(args.skill,args.evaluation,args.approved_dir,args.registry,args.approve)); return 0
    if args.cmd=='list-approved': pj(list_approved(args.registry)); return 0
    if args.cmd=='install-codex-skills': pj(install_codex_skills(args.registry,args.target_repo,args.include_scripts,args.approve_scripts)); return 0
    if args.cmd=='detect-skill-gaps': rows=detect_skill_gaps(args.clusters,args.min_support); write_skill_gaps(rows,args.out); pj({'candidate_count':len(rows),'out':args.out}); return 0
    if args.cmd=='draft-skill': pj(draft_skill_from_gap_file(args.gap_candidates,args.gap_id,args.drafts_dir)); return 0
    if args.cmd=='react-skill-gap': pj(react_to_skill_gaps(args.gap_candidates,drafts_dir=args.drafts_dir,reports_dir=args.reports_dir,evals_dir=args.evals_dir,reference_jsonl=args.reference_jsonl,max_gaps=args.max_gaps,max_refs_per_gap=args.max_refs_per_gap,min_support=args.min_support,allow_network=args.allow_network,dry_run=args.dry_run)); return 0
    if args.cmd=='evaluate-skill-fixtures': r=write_fixture_evaluation(args.skill,args.out); pj({'out':args.out,'passed':r['passed'],'recommendation':r['recommendation'],'overall':r['scores']['overall']}); return 0
    return 1
