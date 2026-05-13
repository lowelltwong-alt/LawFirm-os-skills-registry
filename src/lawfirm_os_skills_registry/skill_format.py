from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass(frozen=True)
class SkillDocument:
    path: Path
    frontmatter: dict
    body: str
    name: str | None
    description: str | None


def _parse_scalar(v: str):
    v=v.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")): return v[1:-1]
    if v.lower() == 'true': return True
    if v.lower() == 'false': return False
    return v


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith('---'):
        return {}, text
    end = text.find('\n---', 3)
    if end == -1:
        return {}, text
    fm_text = text[3:end].strip('\n')
    body = text[end+4:].lstrip('\n')
    root: dict = {}
    current_key = None
    for raw in fm_text.splitlines():
        if not raw.strip() or raw.strip().startswith('#'): continue
        if raw.startswith('  ') and current_key:
            k, _, v = raw.strip().partition(':')
            root.setdefault(current_key, {})[k.strip()] = _parse_scalar(v)
        else:
            k, _, v = raw.partition(':')
            k=k.strip(); v=v.strip()
            if v == '':
                root[k] = {}; current_key=k
            else:
                root[k] = _parse_scalar(v); current_key=k
    return root, body


def parse_skill_md(path: str | Path) -> SkillDocument:
    p=Path(path)
    fm, body = parse_frontmatter(p.read_text(encoding='utf-8', errors='replace'))
    return SkillDocument(path=p, frontmatter=fm, body=body, name=fm.get('name'), description=fm.get('description'))


def load_skill(skill_dir: str | Path) -> SkillDocument:
    p=Path(skill_dir)/'SKILL.md'
    if not p.exists(): raise FileNotFoundError(f'Missing SKILL.md in {skill_dir}')
    return parse_skill_md(p)


def validate_skill_name(name: str | None, folder_name: str | None = None) -> list[str]:
    errors=[]
    if not name: return ['missing name']
    if not re.match(r'^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$', name): errors.append('name must be lowercase kebab-case')
    if folder_name and name != folder_name: errors.append('name should match folder name')
    return errors
