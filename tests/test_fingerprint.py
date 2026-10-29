from pathlib import Path
import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/simulink-carsim-cosim/scripts/fingerprint.py'
SPEC = importlib.util.spec_from_file_location('fingerprint', SCRIPT)
fp = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fp)


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'src').mkdir()
        (self.root / 'src' / 'control.m').write_text('gain = 2;\n', encoding='utf8')
        (self.root / 'model.slx').write_bytes(b'synthetic fixture, not a real SLX')
        self.manifest = self.root / 'evidence' / 'source.json'

    def create(self, *includes):
        args = ['snapshot', '--root', str(self.root), '--out', str(self.manifest)]
        for name in includes or ('src', 'model.slx'):
            args += ['--include', name]
        return self.call(*args)

    def call(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fp.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def verify(self):
        return self.call('verify', '--root', str(self.root), '--manifest', str(self.manifest))

    def test_unchanged_and_manifest_does_not_embed_root(self):
        self.assertEqual(self.create()[0], 0)
        self.assertEqual(self.verify()[0], 0)
        self.assertNotIn(str(self.root), self.manifest.read_text(encoding='utf8'))

    def test_modify_same_size(self):
        self.create()
        (self.root / 'src/control.m').write_text('gain = 3;\n', encoding='utf8')
        code, output, _ = self.verify()
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)['modified'], ['src/control.m'])

    def test_added_file(self):
        self.create()
        (self.root / 'src/new.m').write_text('x=1;', encoding='utf8')
        code, output, _ = self.verify()
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)['added'], ['src/new.m'])

    def test_removed_selected_file(self):
        self.create()
        (self.root / 'model.slx').unlink()
        code, output, _ = self.verify()
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)['removed'], ['model.slx'])

    def test_removed_entire_selected_directory(self):
        self.create()
        shutil.rmtree(self.root / 'src')
        code, output, _ = self.verify()
        self.assertEqual(code, 1)
        self.assertIn('src/control.m', json.loads(output)['removed'])

    def test_change_outside_selection_not_claimed_as_covered(self):
        self.create('src')
        (self.root / 'outside.txt').write_text('not selected', encoding='utf8')
        self.assertEqual(self.verify()[0], 0)

    def test_overlapping_selections_are_deduplicated(self):
        value = fp.snapshot(self.root, ['src', 'src/control.m', 'src'])
        self.assertEqual(len(value['files']), 1)

    def test_missing_source_rejected(self):
        self.assertEqual(self.create('missing')[0], 2)

    def test_empty_directory_rejected(self):
        (self.root / 'empty').mkdir()
        self.assertEqual(self.create('empty')[0], 2)

    def test_path_traversal_and_absolute_paths_rejected(self):
        for name in ('../elsewhere', '/tmp/elsewhere', 'C:/elsewhere', '..\\elsewhere', '.', ''):
            with self.subTest(name=name), self.assertRaises(ValueError):
                fp.snapshot(self.root, [name])

    def test_manifest_inside_tracked_source_rejected(self):
        self.manifest = self.root / 'src' / 'source.json'
        self.assertEqual(self.create()[0], 2)
        self.assertFalse(self.manifest.exists())

    def test_existing_baseline_not_overwritten(self):
        self.create()
        raw = self.manifest.read_bytes()
        self.assertEqual(self.create()[0], 2)
        self.assertEqual(self.manifest.read_bytes(), raw)

    def test_corrupt_checksum_rejected(self):
        self.create()
        value = json.loads(self.manifest.read_text())
        value['files'][0]['sha256'] = '0' * 64
        self.manifest.write_text(json.dumps(value), encoding='utf8')
        self.assertEqual(self.verify()[0], 2)

    def test_duplicate_manifest_record_rejected(self):
        self.create()
        value = json.loads(self.manifest.read_text())
        value['files'].append(value['files'][0])
        payload = {k: value[k] for k in ('schema', 'includes', 'files')}
        value['signature'] = fp.signature(payload)
        self.manifest.write_text(json.dumps(value), encoding='utf8')
        self.assertEqual(self.verify()[0], 2)

    def test_missing_manifest_rejected(self):
        self.assertEqual(self.verify()[0], 2)

    def test_other_root_with_same_content_matches(self):
        self.create()
        moved = self.root / 'copied'
        moved.mkdir()
        shutil.copytree(self.root / 'src', moved / 'src')
        shutil.copyfile(self.root / 'model.slx', moved / 'model.slx')
        code, _, _ = self.call('verify', '--root', str(moved), '--manifest', str(self.manifest))
        self.assertEqual(code, 0)

    def test_unicode_and_space_paths(self):
        folder = self.root / '模型 文件'
        folder.mkdir()
        (folder / '控制.m').write_text('方向 = 1;', encoding='utf8')
        self.assertEqual(self.create('模型 文件')[0], 0)
        self.assertEqual(self.verify()[0], 0)

    def test_symlink_rejected_when_os_permits_creation(self):
        link = self.root / 'src' / 'linked.m'
        try:
            link.symlink_to(self.root / 'model.slx')
        except (OSError, NotImplementedError) as error:
            self.skipTest('OS does not permit creating test symlinks: ' + type(error).__name__)
        self.assertEqual(self.create()[0], 2)

    @unittest.skipUnless(os.name == 'nt', 'Windows junction fixture')
    def test_windows_junction_rejected_without_new_pathlib_api(self):
        import _winapi
        target = self.root / 'target'
        target.mkdir()
        (target / 'nested.m').write_text('x=1;', encoding='utf8')
        link = self.root / 'src' / 'junction'
        _winapi.CreateJunction(str(target), str(link))
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)
        self.assertEqual(self.create()[0], 2)


if __name__ == '__main__':
    unittest.main()
