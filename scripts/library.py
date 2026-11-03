#!/usr/bin/env python3
"""Inspect and verify the local catalogue; never execute downloaded template code."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from pathlib import PurePosixPath
import stat
from urllib.parse import urlparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_RELEASE_KIND = 'verified_open_author_release'
SHA256 = re.compile(r'[0-9a-f]{64}\Z')

def read_object(path: Path) -> dict:
    """Do not let duplicate JSON keys conceal a second manifest identity."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    value = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)
    if not isinstance(value, dict):
        raise ValueError(f'Expected JSON object: {path.name}')
    return value

def valid_sha(value) -> bool:
    return isinstance(value, str) and SHA256.fullmatch(value) is not None

def sensitive_member(name: str) -> bool:
    """Reject personal delivery/credential files, not words such as keyframes."""
    for part in PurePosixPath(name.lower()).parts:
        if (part == '.env' or part.startswith('.env.') or
            re.fullmatch(r'(?:personal[-_]?key|api[-_]?key|private[-_]?key|credentials?)(?:\.(?:json|txt|toml|ya?ml|env))?', part) or
            part in {'personal', 'personal.json', 'personal-key.json', 'credentials',
                     'credentials.json', 'credential.json', 'api-key.json', 'api_key.json',
                     'private-key.json', 'private_key.json', 'id_rsa', 'id_ed25519'} or
            part.endswith(('.pem', '.p12', '.pfx', '.key'))):
            return True
    return name.lower() in {'content/release.bin', 'license/api-key.json'}

def verify_author_release(root: Path, row: dict, variant: dict, source: dict,
                          base: Path, archive: Path, expected: dict) -> None:
    """Bind an unchanged open author ZIP to a redacted inspected delivery record.

    The personal signed envelope is deliberately not distributed. Its signature
    was checked by the official helper during acquisition; this offline check
    binds that record and hashes, rather than claiming to re-verify an absent
    personal signature or using a landing-page Git commit as source identity.
    """
    identity_keys = ('source_kind', 'version', 'template_slug', 'publisher_template_id',
        'publisher_release_id', 'release_archive_sha256', 'release_archive_bytes',
        'content_protection', 'source_url', 'envelope_manifest_sha256',
        'delivery_receipt_sha256', 'delivery_evidence_path', 'delivery_evidence_sha256')
    for key in identity_keys:
        value = variant.get(key, row.get(key))
        if value is None or source.get(key) != value or row.get(key) != value:
            raise ValueError(f'Author release identity differs: {key}')
    if source['source_kind'] != AUTHOR_RELEASE_KIND:
        raise ValueError('Unsupported author release source kind')
    if any(record.get('upstream_commit') is not None for record in (row, variant, source)):
        raise ValueError('Author release must not invent an upstream Git commit')
    for key in ('template_slug', 'version'):
        if not isinstance(source.get(key), str) or not source[key].strip():
            raise ValueError(f'Missing author release identity: {key}')
    for key in ('publisher_template_id', 'publisher_release_id', 'release_archive_bytes'):
        if type(source.get(key)) is not int or source[key] <= 0:
            raise ValueError(f'Invalid author release identity: {key}')
    for key in ('release_archive_sha256', 'envelope_manifest_sha256',
                'delivery_receipt_sha256', 'delivery_evidence_sha256'):
        if not valid_sha(source.get(key)):
            raise ValueError(f'Invalid author release digest: {key}')
    if source['release_archive_sha256'] != source['package_sha256'] or source['release_archive_bytes'] != archive.stat().st_size:
        raise ValueError('Author release archive identity differs')
    if source['content_protection'] != 'open' or source.get('personal_envelope_included') is not False:
        raise ValueError('Author release must be open and exclude its personal envelope')
    parsed = urlparse(source['source_url'])
    if (parsed.scheme != 'https' or parsed.netloc not in {'motiongit.com', 'www.motiongit.com'}
        or not parsed.path.startswith('/@') or parsed.query or parsed.fragment):
        raise ValueError('Author release source must be a credential-free official detail URL')
    proof_path = safe_path(root, source['delivery_evidence_path'])
    if base.resolve() in proof_path.resolve().parents:
        raise ValueError('Redacted delivery evidence must remain outside unchanged author source')
    if digest(proof_path) != source['delivery_evidence_sha256']:
        raise ValueError('Redacted delivery evidence hash differs')
    proof = read_object(proof_path)
    allowed = {'schema', 'template_id', 'publisher_template_id', 'publisher_release_id',
        'version', 'template_slug', 'content_protection', 'release_archive_sha256',
        'release_archive_bytes', 'envelope_manifest_sha256', 'delivery_receipt_sha256',
        'personal_envelope_included', 'source_url', 'official_helper_signature_verified',
        'official_helper_sha256'}
    if set(proof) - allowed:
        raise ValueError('Redacted delivery evidence contains unexpected or personal fields')
    if proof.get('schema') != 'openmotion-redacted-delivery-evidence-v1':
        raise ValueError('Unsupported redacted delivery evidence schema')
    proof_identity = {'template_id': row['id'], 'personal_envelope_included': False}
    for key in allowed - {'schema', 'template_id', 'personal_envelope_included',
                          'official_helper_signature_verified', 'official_helper_sha256'}:
        proof_identity[key] = source.get(key)
    for key, value in proof_identity.items():
        if value is None or proof.get(key) != value:
            raise ValueError(f'Redacted delivery identity differs: {key}')
    if proof.get('official_helper_signature_verified') is not True or not valid_sha(proof.get('official_helper_sha256')):
        raise ValueError('Missing inspected official-helper delivery signature evidence')
    manifest = read_object(safe_path(base, 'motion.json'))
    if manifest.get('format') != 'motiongit-template':
        raise ValueError('Author archive is not a plain template; personal/protected packages are excluded')
    protection = manifest.get('content', {}).get('protection') if isinstance(manifest.get('content'), dict) else None
    if protection not in {None, 'open'} or manifest.get('contentProtection') not in {None, 'open'}:
        raise ValueError('Author manifest declares protected content')
    template = manifest.get('template', {})
    if (not isinstance(template, dict) or template.get('id') != source['template_slug']
        or template.get('version') != source['version']):
        raise ValueError('Author manifest template identity/version differs')
    if manifest.get('runtime') != source['runtime'] or source['runtime'].get('entry') != source['source_entry']:
        raise ValueError('Author manifest runtime identity differs')
    license_spec = manifest.get('license', {})
    if not isinstance(license_spec, dict):
        raise ValueError('Author manifest license declaration is invalid')
    license_file = safe_path(base, license_spec.get('file', ''))
    if license_file.resolve() != safe_path(root, source['license_path']).resolve():
        raise ValueError('Author manifest license path differs')
    license_text = ' '.join(license_file.read_text(encoding='utf-8').lower().split())
    if (row.get('license', {}).get('type') != 'MIT' or 'mit' not in license_text
        or 'permission is hereby granted, free of charge' not in license_text
        or 'distribute, sublicense, and/or sell' not in license_text):
        raise ValueError('Author release lacks the inspected redistributable MIT license')
    integrity_name = manifest.get('integrity')
    if not isinstance(integrity_name, str) or integrity_name not in expected:
        raise ValueError('Author manifest integrity file is missing')
    integrity = read_object(safe_path(base, integrity_name))
    hashes = integrity.get('files')
    if integrity.get('algorithm') != 'sha256' or not isinstance(hashes, dict) or not hashes:
        raise ValueError('Invalid author integrity manifest')
    if set(hashes) != set(expected) - {integrity_name}:
        raise ValueError('Author integrity membership differs')
    for name, item in expected.items():
        if type(item.get('bytes')) is not int or item['bytes'] < 0 or not valid_sha(item.get('sha256')):
            raise ValueError(f'Invalid author source file metadata: {name}')
    for name, value in hashes.items():
        if not valid_sha(value) or expected[name]['sha256'] != value:
            raise ValueError(f'Author integrity hash differs: {name}')
    private_key = re.compile(rb'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----')
    for name in expected:
        if sensitive_member(name):
            raise ValueError(f'Personal or credential file in author archive: {name}')
        payload = safe_path(base, name).read_bytes()
        if private_key.search(payload):
            raise ValueError(f'Private key material in author archive: {name}')

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
                source_kind=v.get('source_kind',row.get('source_kind'))
                if source_kind not in {None, AUTHOR_RELEASE_KIND}:
                    raise ValueError(f'Unsupported source kind: {source_kind}')
                if source.get('source_kind') != source_kind:
                    raise ValueError('Provenance source kind differs')
                identity={'template_id':row['id']}
                identity_keys=('language','version','package_path','source_path','source_entry','license_path','runtime')
                if source_kind is None:
                    identity_keys+=('upstream_commit',)
                for key in identity_keys:
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
                        if source_kind == AUTHOR_RELEASE_KIND:
                            if ':' in name or any(part in {'', '.'} for part in name.rstrip('/').split('/')):
                                raise ValueError('Unsafe author ZIP member')
                            mode=stat.S_IFMT(info.external_attr >> 16)
                            if mode not in {0,stat.S_IFREG,stat.S_IFDIR}:
                                raise ValueError('Author ZIP contains unsupported special member')
                            if info.flag_bits & 1:
                                raise ValueError('Author ZIP contains encrypted/protected member')
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
                if source_kind == AUTHOR_RELEASE_KIND:
                    verify_author_release(root,row,v,source,base,archive,expected)
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
