from __future__ import annotations
import base64, json, os, urllib.parse, urllib.request
from pathlib import Path
from typing import Any
from ..util.files import append_jsonl, ensure_dir
from ..util.time import utc_now
API='https://api.github.com'

def _headers():
    h={'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'lawfirm-os-skills-registry'}
    if os.environ.get('GITHUB_TOKEN'): h['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    return h

def _get(url):
    req=urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=30) as resp: return json.loads(resp.read().decode('utf-8'))

def scout_github(query: str, max_results: int=25):
    url=API+'/search/code?'+urllib.parse.urlencode({'q':query,'per_page':min(max_results,100)})
    data=_get(url); rows=[]
    for item in data.get('items', [])[:max_results]:
        repo=item.get('repository', {})
        rows.append({'schema_version':'1.0','discovered_at':utc_now(),'source_type':'github_code_search','query':query,'repo_full_name':repo.get('full_name'),'repo_html_url':repo.get('html_url'),'repo_default_branch':repo.get('default_branch'),'path':item.get('path'),'html_url':item.get('html_url'),'api_url':item.get('url'),'skill_name':Path(item.get('path','')).parent.name,'description':'','status':'discovered'})
    return rows

def write_github_results(rows, out, append=True):
    p=Path(out)
    if p.exists() and not append: p.unlink()
    for r in rows: append_jsonl(p,r)

def _contents_url(repo, path, ref):
    url=f"{API}/repos/{repo}/contents/{urllib.parse.quote(path.strip('/'))}"
    if ref: url += '?' + urllib.parse.urlencode({'ref':ref})
    return url

def import_github_skill(repo: str, path: str, ref: str | None, target_dir: str | Path):
    target=Path(target_dir); ensure_dir(target.parent)
    if target.exists(): raise FileExistsError(target)
    target.mkdir(parents=True)
    def fetch(remote, local):
        listing=_get(_contents_url(repo, remote, ref))
        if isinstance(listing, dict): listing=[listing]
        for item in listing:
            typ=item.get('type'); name=item.get('name')
            if typ=='dir': fetch(item['path'], local/name)
            elif typ=='file':
                data=_get(item['url']); content=base64.b64decode(data.get('content',''))
                ensure_dir(local); (local/name).write_bytes(content)
            else: raise ValueError(f'Refusing unsupported GitHub content type {typ}')
    fetch(path, target)
    (target/'_source.json').write_text(json.dumps({'source_type':'github_contents_api','repo':repo,'path':path,'ref':ref,'imported_at':utc_now()}, indent=2)+'\n', encoding='utf-8')
    if not (target/'SKILL.md').exists(): raise FileNotFoundError('Imported folder did not contain SKILL.md')
    return target
