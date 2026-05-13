from __future__ import annotations
import hashlib, json, os, shutil
from pathlib import Path
from typing import Any, Iterable


def ensure_dir(path: str | Path) -> Path:
    p = Path(path); p.mkdir(parents=True, exist_ok=True); return p


def read_json(path: str | Path, default=None):
    p = Path(path)
    if not p.exists(): return default
    return json.loads(p.read_text(encoding='utf-8'))


def write_json(path: str | Path, data: Any) -> None:
    p = Path(path); ensure_dir(p.parent); p.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def append_jsonl(path: str | Path, row: dict[str, Any]) -> None:
    p = Path(path); ensure_dir(p.parent); p.write_text('', encoding='utf-8') if not p.exists() else None
    with p.open('a', encoding='utf-8') as f: f.write(json.dumps(row, sort_keys=True) + '\n')


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists(): return []
    rows=[]
    for line in p.read_text(encoding='utf-8').splitlines():
        if line.strip(): rows.append(json.loads(line))
    return rows


def sha256_file(path: str | Path) -> str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()


def iter_files(root: str | Path) -> Iterable[Path]:
    r=Path(root)
    for p in r.rglob('*'):
        if p.is_file() or p.is_symlink(): yield p


def file_manifest(root: str | Path) -> list[dict[str, Any]]:
    r=Path(root); rows=[]
    for p in sorted(iter_files(r)):
        rel=p.relative_to(r).as_posix()
        rows.append({'path': rel, 'sha256': None if p.is_symlink() else sha256_file(p), 'size_bytes': 0 if p.is_symlink() else p.stat().st_size, 'symlink': p.is_symlink()})
    return rows


def safe_copytree(source: str | Path, target: str | Path) -> None:
    s=Path(source); t=Path(target)
    if t.exists(): raise FileExistsError(f'Target exists: {t}')
    def ignore(dir, names):
        return {n for n in names if n in {'.git', '.hg', '.svn', '__pycache__', '.pytest_cache'}}
    shutil.copytree(s, t, ignore=ignore, symlinks=False)


def read_text_lossy(path: str | Path) -> str:
    return Path(path).read_text(encoding='utf-8', errors='replace')


def is_probably_text(path: str | Path) -> bool:
    data = Path(path).read_bytes()[:4096]
    if b'\x00' in data: return False
    return True
