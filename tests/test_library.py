"""Offline integrity fixtures: never import/run any code under templates/."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


TOOL = Path(__file__).resolve().parents[1] / 'scripts/library.py'
SPEC = importlib.util.spec_from_file_location('openmotion_library_under_test', TOOL)
LIB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LIB)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LibraryIntegrityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='openmotion-offline-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'library'
        self.base = self.root / 'templates/fixture/zh'
        (self.base / 'src').mkdir(parents=True)
        (self.base / 'licenses').mkdir()
        self.entry = self.base / 'src/main.py'
        # Read/hash only. Execution would fail, and is never part of these tests.
        self.entry.write_text('raise AssertionError("FIXTURE MUST NEVER EXECUTE")\n')
        (self.base / 'licenses/MIT.txt').write_text('MIT fixture license only\n')
        (self.base / 'motion.json').write_text('{"runtime":{"entry":"src/main.py"}}\n')
        self.archive = self.root / 'templates/fixture/archives/source.motion'
        self.archive.parent.mkdir()
        with zipfile.ZipFile(self.archive, 'w') as z:
            for file in sorted(self.base.rglob('*')):
                if file.is_file():
                    z.write(file, file.relative_to(self.base).as_posix())
        self.variant = {
            'language': 'zh', 'version': '1.0-fixture',
            'source_path': 'templates/fixture/zh',
            'source_entry': 'src/main.py',
            'package_path': 'templates/fixture/archives/source.motion',
            'package_sha256': sha(self.archive),
            'provenance_path': 'templates/fixture/zh/_openmotion-provenance.json',
            'license_path': 'templates/fixture/zh/licenses/MIT.txt',
            'runtime': {'profile': 'fixture-read-only/1', 'entry': 'src/main.py'},
        }
        self.row = {
            'id': 'fixture', 'title': 'Offline source fixture',
            'source_obtained': True, 'availability': 'mirrored_public',
            'version': '1.0-fixture', 'upstream_commit': 'fixture-commit',
            'origin_url': 'https://example.invalid/fixture',
            'license': {'type': 'MIT', 'redistribution_allowed': True},
            **self.variant, 'variants': [self.variant],
        }
        self.data = {'schema': 'openmotion-catalog-v1', 'templates': [self.row]}
        self.provenance = {
            'schema': 'openmotion-source-provenance-v1',
            'template_id': 'fixture', 'language': 'zh', 'version': '1.0-fixture',
            'upstream_commit': 'fixture-commit',
            'package_path': self.variant['package_path'],
            'package_sha256': self.variant['package_sha256'],
            'source_path': self.variant['source_path'],
            'source_entry': self.variant['source_entry'],
            'runtime': self.variant['runtime'],
            'license_path': self.variant['license_path'],
            'manifest_sha256': sha(self.base / 'motion.json'),
            'template_code_executed': False, 'dependencies_installed': False,
            'files': [
                {'path': f.relative_to(self.base).as_posix(),
                 'bytes': f.stat().st_size, 'sha256': sha(f)}
                for f in sorted(self.base.rglob('*')) if f.is_file()
            ],
        }
        self.write_provenance()
        (self.root / 'catalogs').mkdir()
        self.write_catalog()

    def write_provenance(self):
        (self.root / self.variant['provenance_path']).write_text(json.dumps(self.provenance))

    def write_catalog(self):
        (self.root / 'catalogs/templates.json').write_text(json.dumps(self.data))

    def check(self):
        return LIB.verify(self.root, self.data)

    def assert_rejected(self, result, contains=None):
        self.assertFalse(result['passed'], result)
        self.assertTrue(result['errors'], result)
        if contains:
            self.assertIn(contains, ' '.join(result['errors']))

    def test_real_files_original_package_and_provenance_pass_without_execution(self):
        result = LIB.verify(self.root, LIB.load(self.root))
        self.assertTrue(result['passed'], result['errors'])
        self.assertEqual(result['source_variants'], 1)
        self.assertEqual(result['verified_source_files'], 3)
        self.assertFalse(result['template_code_executed'])
        self.assertFalse(result['runtime_render_verified'])

    def test_same_length_source_tamper_is_detected_by_hash(self):
        original = self.entry.read_bytes()
        self.entry.write_bytes(original.replace(b'FIXTURE', b'MUTATED'))
        self.assertEqual(self.entry.stat().st_size, len(original))
        self.assert_rejected(self.check(), 'Extracted file differs')

    def test_missing_source_file_is_rejected(self):
        (self.base / 'motion.json').unlink()
        self.assert_rejected(self.check(), 'membership differs')

    def test_added_source_file_is_rejected(self):
        (self.base / 'extra.txt').write_text('Unrecorded extra file')
        self.assert_rejected(self.check(), 'membership differs')

    def test_original_package_tamper_is_rejected(self):
        with self.archive.open('ab') as f:
            f.write(b'tamper')
        self.assert_rejected(self.check(), 'package hash differs')

    def test_provenance_package_digest_mismatch_is_rejected(self):
        self.provenance['package_sha256'] = '0' * 64
        self.write_provenance()
        self.assert_rejected(self.check(), 'Provenance/package mismatch')

    def test_changed_source_and_rewritten_provenance_cannot_replace_original_package(self):
        self.entry.write_text('# Joint source/receipt tamper, never executed\n')
        for entry in self.provenance['files']:
            if entry['path'] == 'src/main.py':
                entry.update(bytes=self.entry.stat().st_size, sha256=sha(self.entry))
        self.write_provenance()
        self.assertEqual(sha(self.archive), self.variant['package_sha256'])
        self.assert_rejected(self.check())

    def test_no_redistribution_permission_is_rejected(self):
        for value in (False, None):
            with self.subTest(value=value):
                self.row['license'] = {'type': 'MIT', 'redistribution_allowed': value}
                self.assert_rejected(self.check(), 'redistribution permission')

    def test_invalid_license_or_variant_returns_failure_without_crashing(self):
        for bad in ('null-license', 'invalid-variant'):
            with self.subTest(case=bad):
                data = copy.deepcopy(self.data)
                if bad == 'null-license':
                    data['templates'][0]['license'] = None
                else:
                    data['templates'][0]['variants'] = ['not-a-variant-record']
                self.assert_rejected(LIB.verify(self.root, data))

    def test_empty_variants_cannot_report_success_for_obtained_source(self):
        self.row['variants'] = []
        self.assert_rejected(self.check())

    def test_library_paths_reject_absolute_parent_and_symlink_escape(self):
        outside = self.root.parent / 'outside.txt'
        outside.write_text('Outside fixture')
        (self.root / 'escape').symlink_to(self.root.parent, target_is_directory=True)
        for name in ('', '.', '../outside.txt', 'a/../../outside.txt', str(outside),
                     'a\\outside.txt', 'escape/outside.txt'):
            with self.subTest(path=name):
                with self.assertRaises(ValueError):
                    LIB.safe_path(self.root, name)

    def test_declared_package_escape_fails_closed(self):
        self.variant['package_path'] = '../outside.motion'
        self.assert_rejected(self.check(), 'Invalid library-relative path')

    def test_runtime_entry_cannot_point_outside_source(self):
        outside = self.base.parent / 'outside.py'
        outside.write_text('# Fixture never executed\n')
        for entry in ('../outside.py', str(outside)):
            with self.subTest(entry=entry):
                self.variant['source_entry'] = entry
                self.assert_rejected(self.check())

    def test_provenance_identity_cannot_change_while_package_stays_same(self):
        original = copy.deepcopy(self.provenance)
        for key, bad_value in (
            ('template_id', 'other-template'), ('version', 'wrong-version'),
            ('source_path', 'templates/other/zh'), ('source_entry', 'other.py'),
            ('upstream_commit', 'other-commit'),
        ):
            with self.subTest(field=key):
                self.provenance = {**original, key: bad_value}
                self.write_provenance()
                self.assert_rejected(self.check())

    def test_extracted_symlink_file_is_rejected_even_with_matching_bytes(self):
        original = self.entry.read_bytes()
        outside = self.root.parent / 'same-bytes.py'
        outside.write_bytes(original)
        self.entry.unlink()
        self.entry.symlink_to(outside)
        self.assert_rejected(self.check(), 'symlink')

    def test_unrecorded_directory_and_dangling_symlinks_are_rejected(self):
        outside = self.root.parent / 'outside-directory'
        outside.mkdir()
        for name, target in (('extra-directory', outside), ('dangling-link', outside / 'absent')):
            with self.subTest(name=name):
                link = self.base / name
                link.symlink_to(target, target_is_directory=(name == 'extra-directory'))
                self.assert_rejected(self.check())
                link.unlink()

    def test_duplicate_provenance_file_paths_are_rejected(self):
        original = self.provenance['files'][0]
        self.provenance['files'].insert(0, {**original, 'sha256': '0' * 64})
        self.write_provenance()
        self.assert_rejected(self.check())

    def test_duplicate_catalogue_ids_are_rejected(self):
        self.data['templates'].append(copy.deepcopy(self.row))
        self.write_catalog()
        with self.assertRaisesRegex(ValueError, 'Duplicate template IDs'):
            LIB.load(self.root)


if __name__ == '__main__':
    unittest.main()
