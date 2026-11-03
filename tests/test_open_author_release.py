"""Offline author-release fixtures; no template source is ever executed."""
from __future__ import annotations

import hashlib
import json
import unittest
import zipfile

import test_library as legacy

LIB = legacy.LIB
sha = legacy.sha


class OpenAuthorReleaseIntegrityTest(unittest.TestCase):
    write_provenance = legacy.LibraryIntegrityTest.write_provenance
    write_catalog = legacy.LibraryIntegrityTest.write_catalog
    check = legacy.LibraryIntegrityTest.check
    assert_rejected = legacy.LibraryIntegrityTest.assert_rejected

    def setUp(self):
        legacy.LibraryIntegrityTest.setUp(self)
        self.proof_path = self.root / 'templates/fixture/redacted-delivery-evidence.json'
        self.manifest = {
            'format': 'motiongit-template',
            'template': {'id': 'fixture-template', 'version': '1.0-fixture'},
            'runtime': self.variant['runtime'],
            'license': {'file': 'licenses/MIT.txt'},
            'integrity': 'integrity.json',
        }
        # The first line is intentionally not "MIT License": real packages may
        # prepend a translated heading, while preserving the actual MIT grant.
        (self.base / 'licenses/MIT.txt').write_text(
            'Fixture source license\nMIT License\nCopyright (c) Fixture\n'
            'Permission is hereby granted, free of charge, to any person obtaining '
            'a copy of this software to use, copy, modify, merge, publish, '
            'distribute, sublicense, and/or sell copies.\n')
        fields = {
            'source_kind': 'verified_open_author_release',
            'upstream_commit': None,
            'template_slug': 'fixture-template',
            'publisher_template_id': 123,
            'publisher_release_id': 456,
            'release_archive_sha256': self.variant['package_sha256'],
            'release_archive_bytes': self.archive.stat().st_size,
            'content_protection': 'open',
            'source_url': 'https://motiongit.com/@fixture/fixture-template',
            'envelope_manifest_sha256': hashlib.sha256(b'fixture envelope').hexdigest(),
            'delivery_receipt_sha256': hashlib.sha256(b'fixture receipt').hexdigest(),
            'delivery_evidence_path': self.proof_path.relative_to(self.root).as_posix(),
            'delivery_evidence_sha256': '0' * 64,
        }
        for record in (self.row, self.variant, self.provenance):
            record.update(fields)
        self.provenance['personal_envelope_included'] = False
        self.proof = {
            'schema': 'openmotion-redacted-delivery-evidence-v1',
            'template_id': 'fixture',
            'publisher_template_id': 123,
            'publisher_release_id': 456,
            'version': '1.0-fixture',
            'template_slug': 'fixture-template',
            'content_protection': 'open',
            'release_archive_sha256': fields['release_archive_sha256'],
            'release_archive_bytes': fields['release_archive_bytes'],
            'envelope_manifest_sha256': fields['envelope_manifest_sha256'],
            'delivery_receipt_sha256': fields['delivery_receipt_sha256'],
            'personal_envelope_included': False,
            'source_url': fields['source_url'],
            'official_helper_signature_verified': True,
            'official_helper_sha256': hashlib.sha256(b'fixture official helper').hexdigest(),
        }
        self.rebuild()

    def set_identity(self, key, value):
        for record in (self.row, self.variant, self.provenance):
            record[key] = value
        if key in self.proof:
            self.proof[key] = value

    def write_proof(self):
        self.proof_path.write_text(json.dumps(self.proof))
        self.set_identity('delivery_evidence_sha256', sha(self.proof_path))

    def rebuild(self, regenerate_integrity=True):
        """Build a coherent fixture ZIP so semantic tests reach semantic checks."""
        (self.base / 'motion.json').write_text(json.dumps(self.manifest))
        provenance_path = self.root / self.variant['provenance_path']
        integrity_path = self.base / 'integrity.json'
        if regenerate_integrity:
            hashes = {f.relative_to(self.base).as_posix(): sha(f)
                      for f in sorted(self.base.rglob('*'))
                      if f.is_file() and f not in {provenance_path, integrity_path}}
            integrity_path.write_text(json.dumps({'algorithm': 'sha256', 'files': hashes}))
        files = [f for f in sorted(self.base.rglob('*')) if f.is_file() and f != provenance_path]
        with zipfile.ZipFile(self.archive, 'w') as archive:
            for f in files:
                archive.write(f, f.relative_to(self.base).as_posix())
        self.set_identity('package_sha256', sha(self.archive))
        self.set_identity('release_archive_sha256', sha(self.archive))
        self.set_identity('release_archive_bytes', self.archive.stat().st_size)
        self.provenance['manifest_sha256'] = sha(self.base / 'motion.json')
        self.provenance['files'] = [
            {'path': f.relative_to(self.base).as_posix(), 'bytes': f.stat().st_size, 'sha256': sha(f)}
            for f in files]
        self.write_proof()
        self.write_provenance()
        self.write_catalog()

    def test_valid_open_author_release_passes_without_a_git_commit_or_execution(self):
        result = self.check()
        self.assertTrue(result['passed'], result['errors'])
        self.assertEqual(result['source_variants'], 1)
        self.assertEqual(result['verified_source_files'], 4)
        self.assertFalse(result['template_code_executed'])
        self.assertIsNone(self.provenance['upstream_commit'])

    def test_protected_delivery_is_rejected_even_when_metadata_and_proof_agree(self):
        self.set_identity('content_protection', 'encrypted')
        self.write_proof()
        self.write_provenance()
        self.assert_rejected(self.check(), 'must be open')

    def test_personal_outer_manifest_cannot_masquerade_as_author_source(self):
        self.manifest['format'] = 'personal-download-v1'
        self.rebuild()
        self.assert_rejected(self.check(), 'personal/protected')

    def test_personal_or_credential_paths_are_rejected_with_coherent_hashes(self):
        for name in ('.env', 'keys/personal-key.json', 'license/api-key.json', 'api_key.txt'):
            with self.subTest(name=name):
                target = self.base / name
                target.parent.mkdir(exist_ok=True)
                target.write_text('Fixture only, contains no real credential\n')
                self.rebuild()
                self.assert_rejected(self.check(), 'Personal or credential file')
                target.unlink()

    def test_private_key_marker_is_rejected_without_a_sensitive_filename(self):
        (self.base / 'innocent.txt').write_text('-----BEGIN PRIVATE KEY-----\nfixture\n-----END PRIVATE KEY-----\n')
        self.rebuild()
        self.assert_rejected(self.check(), 'Private key material')

    def test_redacted_proof_rejects_extra_personal_fields(self):
        self.proof['personal_account'] = 'fixture account, not a real identity'
        self.write_proof()
        self.write_provenance()
        self.assert_rejected(self.check(), 'unexpected or personal fields')

    def test_redacted_delivery_identity_must_match_the_author_release(self):
        self.proof['publisher_release_id'] += 1
        self.write_proof()
        self.write_provenance()
        self.assert_rejected(self.check(), 'Redacted delivery identity differs')

    def test_plain_manifest_cannot_hide_a_protected_content_declaration(self):
        self.manifest['content'] = {'protection': 'encrypted'}
        self.rebuild()
        self.assert_rejected(self.check(), 'declares protected content')

    def test_missing_or_changed_delivery_evidence_is_rejected(self):
        self.proof_path.write_text('{}')
        self.assert_rejected(self.check(), 'delivery evidence hash differs')
        self.proof_path.unlink()
        self.assert_rejected(self.check())

    def test_missing_official_helper_signature_evidence_is_rejected(self):
        self.proof['official_helper_signature_verified'] = False
        self.write_proof()
        self.write_provenance()
        self.assert_rejected(self.check(), 'official-helper')

    def test_missing_publisher_identity_is_rejected(self):
        self.set_identity('publisher_release_id', None)
        self.write_proof()
        self.write_provenance()
        self.assert_rejected(self.check(), 'publisher_release_id')

    def test_missing_version_is_rejected(self):
        for record in (self.row, self.variant, self.provenance):
            record.pop('version')
        self.write_provenance()
        self.assert_rejected(self.check(), 'version')

    def test_invented_source_commit_is_rejected(self):
        self.set_identity('upstream_commit', 'not-an-author-source-commit')
        self.write_provenance()
        self.assert_rejected(self.check(), 'must not invent')

    def test_manifest_identity_cannot_be_rewritten_into_another_version(self):
        self.manifest['template']['version'] = 'different-version'
        self.rebuild()
        self.assert_rejected(self.check(), 'manifest template identity/version differs')

    def test_manifest_runtime_must_match_catalogue(self):
        self.manifest['runtime'] = {'profile': 'other/1', 'entry': 'src/main.py'}
        self.rebuild()
        self.assert_rejected(self.check(), 'manifest runtime identity differs')

    def test_author_integrity_hashes_are_checked_not_just_provenance_hashes(self):
        path = self.base / 'integrity.json'
        integrity = json.loads(path.read_text())
        integrity['files']['src/main.py'] = '0' * 64
        path.write_text(json.dumps(integrity))
        self.rebuild(regenerate_integrity=False)
        self.assert_rejected(self.check(), 'Author integrity hash differs')

    def test_author_integrity_must_cover_all_source_members(self):
        path = self.base / 'integrity.json'
        integrity = json.loads(path.read_text())
        integrity['files'].pop('src/main.py')
        path.write_text(json.dumps(integrity))
        self.rebuild(regenerate_integrity=False)
        self.assert_rejected(self.check(), 'Author integrity membership differs')

    def test_source_hash_and_membership_tamper_are_still_rejected(self):
        old = self.entry.read_bytes()
        self.entry.write_bytes(old.replace(b'FIXTURE', b'MUTATED'))
        self.assert_rejected(self.check(), 'Extracted file differs')
        self.entry.write_bytes(old)
        (self.base / 'extra.py').write_text('# Not part of the author release\n')
        self.assert_rejected(self.check(), 'membership differs')

    def test_archive_identity_and_size_must_match_release_identity(self):
        self.set_identity('release_archive_bytes', self.archive.stat().st_size + 1)
        self.write_proof()
        self.write_provenance()
        self.assert_rejected(self.check(), 'archive identity differs')

    def test_manifest_license_must_be_the_actual_included_license(self):
        (self.base / 'licenses/other.txt').write_text('Other license\n')
        self.manifest['license']['file'] = 'licenses/other.txt'
        self.rebuild()
        self.assert_rejected(self.check(), 'manifest license path differs')

    def test_unknown_source_kind_does_not_skip_commit_or_release_checks(self):
        self.set_identity('source_kind', 'some-open-source')
        self.write_provenance()
        self.assert_rejected(self.check(), 'Unsupported source kind')


if __name__ == '__main__':
    unittest.main()
