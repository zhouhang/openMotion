#!/usr/bin/env python3
"""Inspect and verify the local catalogue; never execute downloaded template code."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from pathlib import PurePosixPath
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def safe_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str):
        raise ValueError('Library path must be a string')
    rel=Path(relative)
    if not relative or rel.is_absolute() or '..' in rel.parts or '\\' in relative:
        raise ValueError(f'Invalid library-relative path: {relative!r}')
    p=root/rel
    if any(x.is_symlink() for x in [p, *p.parents] if x != root and root in x.parents) or root.resolve() not in p.resolve().parents:
        raise ValueError(f'Path leaves library or is a symlink: {relative!r}')
    return p

def load(root: Path) -> dict:
    d=json.loads((root/'catalogs/templates.json').read_text())
    if d.get('schema')!='openmotion-catalog-v1': raise ValueError('Unsupported catalogue schema')
    rows=d.get('templates',[])
    if len({str(x['id']) for x in rows})!=len(rows): raise ValueError('Duplicate template IDs')
    return d

def verify(root: Path, data: dict) -> dict:
    errors=[];variants=0;files=0;obtained=0
    for row in data['templates']:
        if not row.get('source_obtained'): continue
        obtained+=1
        if not isinstance(row.get('license'),dict) or row['license'].get('redistribution_allowed') is not True:
            errors.append(f"{row['id']}: mirrored source lacks redistribution permission")
        source_variants=row.get('variants',[row])
        if not isinstance(source_variants,list) or not source_variants:
            errors.append(f"{row['id']}: mirrored source requires nonempty variants")
            continue
        for v in source_variants:
            try:
                if not isinstance(v,dict): raise ValueError('Variant must be an object')
                base=safe_path(root,v['source_path']);archive=safe_path(root,v['package_path'])
                if digest(archive)!=v['package_sha256']: raise ValueError('Original package hash differs')
                entry_path=safe_path(base,v['source_entry'])
                if not entry_path.is_file(): raise ValueError('Runtime entry is absent')
                license_path=safe_path(root,v['license_path'])
                if not license_path.is_file() or base.resolve() not in license_path.resolve().parents:
                    raise ValueError('License file is absent or outside source')
                p=safe_path(root,v['provenance_path']);source=json.loads(p.read_text())
                if source['package_sha256']!=v['package_sha256']: raise ValueError('Provenance/package mismatch')
                if source.get('schema')!='openmotion-source-provenance-v1': raise ValueError('Unsupported provenance schema')
                identity={'template_id':row['id']}
                for key in ('language','version','upstream_commit','package_path','source_path','source_entry','license_path','runtime'):
                    identity[key]=v.get(key,row.get(key))
                for key,value in identity.items():
                    if value is None or source.get(key)!=value: raise ValueError(f'Provenance identity differs: {key}')
                listed=source['files']
                if not isinstance(listed,list) or not listed: raise ValueError('Source file list is empty or invalid')
                expected={x['path']:x for x in listed}
                if len(expected)!=len(listed): raise ValueError('Duplicate provenance file paths')
                paths=list(base.rglob('*'))
                if any(x.is_symlink() for x in paths): raise ValueError('Extracted source contains a symlink')
                actual={x.relative_to(base).as_posix() for x in paths if x.is_file() and x!=p}
                if actual!=set(expected): raise ValueError('Extracted source membership differs')
                for name,entry in expected.items():
                    f=safe_path(base,name)
                    if not f.is_file() or f.stat().st_size!=entry['bytes'] or digest(f)!=entry['sha256']:
                        raise ValueError(f'Extracted file differs: {name}')
                # Compare to the unchanged original ZIP, not just a rewritable receipt.
                with zipfile.ZipFile(archive) as z:
                    archived={}
                    for info in z.infolist():
                        name=info.filename
                        parts=PurePosixPath(name).parts
                        if not name or name.startswith('/') or '..' in parts or '\\' in name or any(ord(c)<32 for c in name):
                            raise ValueError('Unsafe original ZIP member')
                        if stat.S_ISLNK(info.external_attr >> 16): raise ValueError('Original ZIP contains symlink')
                        if info.is_dir(): continue
                        if name in archived: raise ValueError('Duplicate original ZIP member')
                        archived[name]=info
                    if set(archived)!=set(expected): raise ValueError('Original ZIP/source membership differs')
                    for name,info in archived.items():
                        h=hashlib.sha256()
                        with z.open(info) as f:
                            for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
                        if info.file_size!=expected[name]['bytes'] or h.hexdigest()!=expected[name]['sha256']:
                            raise ValueError(f'Original ZIP/source differs: {name}')
                if source.get('manifest_sha256')!=digest(safe_path(base,'motion.json')):
                    raise ValueError('Template manifest hash differs')
                variants+=1;files+=len(expected)
            except (OSError,ValueError,KeyError,TypeError,AttributeError,zipfile.BadZipFile,RuntimeError) as e:
                language=v.get('language','default') if isinstance(v,dict) else 'invalid'
                errors.append(f"{row['id']}/{language}: {e}")
    return {'schema':'openmotion-library-check-v1','passed':not errors,'catalogue_templates':len(data['templates']),
            'mirrored_templates':obtained,'source_variants':variants,'verified_source_files':files,
            'runtime_render_verified':False,'template_code_executed':False,'errors':errors}

def card(row: dict) -> str:
    runtime=row.get('runtime') or '未取得源码，运行环境未核验'
    return '\n'.join([f"### {row['title']} · #{row['id']}", '',
        f"![{row['title']}]({row.get('thumbnail_url') or row.get('preview_url')})",'',
        f"- 源码已取得：{'是' if row.get('source_obtained') else '否'}；状态：{row['availability']}",
        f"- 版本：{row.get('version') or '未知'}；运行环境：{json.dumps(runtime,ensure_ascii=False)}",
        f"- 许可：{json.dumps(row.get('license'),ensure_ascii=False)}",
        f"- 官网：{row['origin_url']}",
        *[f"- Demo（{v.get('language','default')}）：{v['url']}" for v in row.get('demos',[])],
        f"- 本地源码：{row.get('source_path') or '尚未取得；不能将Demo当模板运行'}",''])

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=ROOT)
    sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('list');p.add_argument('--ready',action='store_true',help='Only sources actually acquired; not a render qualification')
    p.add_argument('--json',action='store_true');p=sub.add_parser('show');p.add_argument('template_id');p.add_argument('--json',action='store_true')
    sub.add_parser('verify');args=ap.parse_args();root=args.root.resolve();d=load(root)
    if args.command=='verify':
        r=verify(root,d);print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['passed'] else 1
    rows=d['templates']
    if args.command=='list':
        rows=[x for x in rows if x.get('source_obtained')] if args.ready else rows
        if args.json: print(json.dumps(rows,ensure_ascii=False,indent=2))
        else:
            for x in rows:print(f"{x['id']}\t{x['title']}\t{x['availability']}\t{x.get('version') or '?'}")
        return 0
    found=[x for x in rows if x['id']==args.template_id]
    if len(found)!=1:ap.error('Unknown or ambiguous template ID')
    print(json.dumps(found[0],ensure_ascii=False,indent=2) if args.json else card(found[0]));return 0
if __name__=='__main__':raise SystemExit(main())
