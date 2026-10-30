"""Regression tests for VHS artifact verification and gitignored audit evidence."""
import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_workflow


class WorkflowTests(unittest.TestCase):
    def invoke(self, tape, arguments, renderer):
        argv = ['run_workflow.py', 'expanded', str(tape)] + arguments
        stdout = io.StringIO()
        with patch.object(sys, 'argv', argv), \
                patch.object(run_workflow.shutil, 'which', return_value='/mock/vhs'), \
                patch.object(run_workflow.subprocess, 'run', side_effect=renderer), \
                patch.object(run_workflow, 'inspect', side_effect=self.fake_inspect), \
                contextlib.redirect_stdout(stdout):
            status = run_workflow.main()
        return status, stdout.getvalue()

    @staticmethod
    def fake_inspect(path, contact_sheet=None):
        exists = path.exists()
        return {'ok': exists, 'metadata': {}, 'issues': [] if exists else ['Missing artifact']}

    def test_artifacts_include_screenshots_and_sources(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            tape = root / 'audit.tape'
            (root / 'child.tape').write_text('Screenshot "screens/help screen.png"\n')
            tape.write_text(
                'Output demo.gif\nScreenshot screens/start.png\nSource child.tape\n'
                'Type "an embedded command that is not an artifact"\n'
            )
            self.assertEqual(run_workflow.artifacts_in(tape), [
                root / 'demo.gif', root / 'screens/start.png', root / 'screens/help screen.png',
            ])

    def test_missing_screenshot_fails_even_when_output_exists(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            tape = root / 'audit.tape'
            tape.write_text('Output demo.gif\nScreenshot screens/start.png\n')

            def render(args, **kwargs):
                (root / 'demo.gif').write_bytes(b'new recording')
                return SimpleNamespace(returncode=0)

            status, output = self.invoke(tape, [], render)
            self.assertEqual(status, 3)
            self.assertIn('screens/start.png', output)
            self.assertIn('Missing artifact', output)

    def test_old_file_cannot_satisfy_freshness(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            tape = root / 'audit.tape'
            tape.write_text('Output demo.gif\n')
            recording = root / 'demo.gif'
            recording.write_bytes(b'old recording')
            status, output = self.invoke(
                tape, [], lambda args, **kwargs: SimpleNamespace(returncode=0)
            )
            self.assertEqual(status, 3)
            self.assertEqual(recording.read_bytes(), b'old recording')
            self.assertIn('Stale artifact', output)

    @unittest.skipUnless(shutil.which('git'), 'Git required for --audit')
    def test_audit_archives_rendered_artifacts_in_gitignored_dir(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            tape_dir = repo / 'tapes'
            tape_dir.mkdir()
            tape = tape_dir / 'audit-demo.tape'
            tape.write_text('Output demo.gif\nScreenshot screen.png\n')

            def execute(args, **kwargs):
                if args[0] == 'git':
                    return original_run(args, **kwargs)
                (tape_dir / 'demo.gif').write_bytes(b'new gif')
                (tape_dir / 'screen.png').write_bytes(b'new png')
                return SimpleNamespace(returncode=0)

            original_run = subprocess.run
            status, output = self.invoke(tape, ['--audit'], execute)
            destination = repo / '.tui-audit' / tape.stem / 'tapes'
            self.assertEqual(status, 0, output)
            self.assertEqual((destination / 'demo.gif').read_bytes(), b'new gif')
            self.assertEqual((destination / 'screen.png').read_bytes(), b'new png')
            self.assertFalse((tape_dir / 'screen.png').exists())
            self.assertIn('/.tui-audit/', (repo / '.gitignore').read_text().splitlines())
            checked = subprocess.run(
                ['git', '-C', str(repo), 'check-ignore', '-q',
                 str((destination / 'screen.png').relative_to(repo))], check=False)
            self.assertEqual(checked.returncode, 0)

    @unittest.skipUnless(shutil.which('git'), 'Git required for --audit')
    def test_audit_rejects_artifacts_outside_repo(self):
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as other:
            root = Path(td)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            tape = root / 'demo.tape'
            tape.write_text(f'Output {other}/outside.gif\n')
            original_run = subprocess.run

            def execute(args, **kwargs):
                if args[0] == 'git':
                    return original_run(args, **kwargs)
                self.fail('VHS should not execute with out-of-repo audit artifact')

            status, output = self.invoke(tape, ['--audit'], execute)
            self.assertEqual(status, 2)
            self.assertIn('escapes repository', output)


if __name__ == '__main__':
    unittest.main()
