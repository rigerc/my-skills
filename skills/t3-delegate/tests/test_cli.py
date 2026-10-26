"""Unit tests for the local provider/config and top-level-thread wrapper."""
import importlib.util
import io
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

FILE = Path(__file__).resolve().parents[1] / "scripts" / "t3_delegate.py"
spec = importlib.util.spec_from_file_location("t3_delegate", FILE)
delegate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(delegate)


class DelegateCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config_file = Path(self.tmp.name) / "config" / "config.json"
        env = patch.dict(os.environ, {"T3_DELEGATE_CONFIG": str(self.config_file)})
        env.start()
        self.addCleanup(env.stop)

    def test_start_uses_stdin_and_worktree_with_explicit_override(self):
        parsed = delegate.parse_args([
            "start", "--project", ".", "--title", "Test", "--worktree", "main",
            "--branch", "agent/test", "--provider", "claude", "--model", "sonnet",
            "--task", "Write a test",
        ])
        argv, inp = delegate.build_command(parsed)
        self.assertEqual(inp, "Write a test")
        self.assertEqual(argv[:5], ["t3", "thread", "start", ".", "-"])
        self.assertEqual(argv[-1], "--json")
        self.assertIn("--worktree", argv)
        self.assertIn("agent/test", argv)
        self.assertEqual(argv[argv.index("--provider") + 1], "claude")
        self.assertEqual(argv[argv.index("--model") + 1], "sonnet")
        self.assertFalse(self.config_file.exists(), "Per-call override must not write config")

    def test_model_provider_must_be_paired(self):
        parsed = delegate.parse_args(["start", "--task", "Hello", "--model", "foo"])
        with self.assertRaisesRegex(ValueError, "together"):
            delegate.build_command(parsed)

    def test_branch_needs_worktree(self):
        parsed = delegate.parse_args(["start", "--task", "Hello", "--branch", "feature"])
        with self.assertRaisesRegex(ValueError, "requires"):
            delegate.build_command(parsed)

    def test_empty_task_refused(self):
        parsed = delegate.parse_args(["send", "thread-abc", "--task", "   "])
        with self.assertRaisesRegex(ValueError, "empty"):
            delegate.build_command(parsed)

    def test_task_file_and_persisted_model(self):
        delegate.save_config("codex-work", "gpt-test")
        path = Path(self.tmp.name) / "task.txt"
        path.write_text("Task with\nmultiple lines", encoding="utf-8")
        parsed = delegate.parse_args(["start", "--task-file", str(path)])
        argv, inp = delegate.build_command(parsed)
        self.assertEqual(inp, "Task with\nmultiple lines")
        self.assertEqual(argv[argv.index("--provider") + 1], "codex-work")
        self.assertEqual(argv[argv.index("--model") + 1], "gpt-test")
        self.assertIn("--title", argv)

    def test_config_set_show_clear(self):
        with patch.object(delegate.sys, "stdout", new_callable=io.StringIO):
            self.assertEqual(delegate.main(["config", "set", "--provider", "codex", "--model", "gpt-a"]), 0)
        self.assertEqual(json.loads(self.config_file.read_text()), {
            "version": 1, "providerInstanceId": "codex", "model": "gpt-a"
        })
        with patch.object(delegate.sys, "stdout", new_callable=io.StringIO) as out:
            self.assertEqual(delegate.main(["config", "show"]), 0)
        self.assertEqual(json.loads(out.getvalue())["selection"]["model"], "gpt-a")
        with patch.object(delegate.sys, "stdout", new_callable=io.StringIO):
            self.assertEqual(delegate.main(["config", "clear"]), 0)
        self.assertFalse(self.config_file.exists())

    def test_config_interactive_init_and_update(self):
        fake_stdin = Mock()
        fake_stdin.isatty.return_value = True
        with patch.object(delegate.sys, "stdin", fake_stdin), patch("builtins.input", side_effect=["provider-1", "model-1"]):
            with patch.object(delegate.sys, "stdout", new_callable=io.StringIO), patch.object(delegate.sys, "stderr", new_callable=io.StringIO):
                self.assertEqual(delegate.main(["config", "init"]), 0)
        self.assertEqual(delegate.load_config()["model"], "model-1")
        with patch.object(delegate.sys, "stdin", fake_stdin), patch("builtins.input", side_effect=["provider-2", "model-2"]):
            with patch.object(delegate.sys, "stdout", new_callable=io.StringIO), patch.object(delegate.sys, "stderr", new_callable=io.StringIO):
                self.assertEqual(delegate.main(["config", "init"]), 0)
        self.assertEqual(delegate.load_config()["providerInstanceId"], "provider-2")

    def test_start_interactively_asks_and_saves_when_not_configured(self):
        fake_stdin = Mock()
        fake_stdin.isatty.return_value = True
        args = delegate.parse_args(["start", "--task", "Implement tests"])
        with patch.object(delegate.sys, "stdin", fake_stdin), patch("builtins.input", side_effect=["my-provider", "my-model"]):
            with patch.object(delegate.sys, "stderr", new_callable=io.StringIO):
                argv, inp = delegate.build_command(args)
        self.assertEqual(inp, "Implement tests")
        self.assertIn("my-model", argv)
        self.assertEqual(delegate.load_config()["providerInstanceId"], "my-provider")

    def test_first_interactive_start_keeps_stdout_valid_json(self):
        terminal = io.StringIO("my-provider\nmy-model\n")
        terminal.isatty = lambda: True
        finished = __import__("subprocess").CompletedProcess(
            args=[], returncode=0, stdout='{"threadId":"abc"}\n', stderr=""
        )
        with patch.object(delegate.sys, "stdin", terminal), \
                patch.object(delegate.sys, "stdout", new_callable=io.StringIO) as out, \
                patch.object(delegate.sys, "stderr", new_callable=io.StringIO) as err, \
                patch.object(delegate.subprocess, "run", return_value=finished) as runner:
            result = delegate.main(["start", "--task", "Review the parser"])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(out.getvalue()), {"threadId": "abc"})
        self.assertIn("Provider instance ID:", err.getvalue())
        self.assertIn("Model slug:", err.getvalue())
        self.assertEqual(delegate.load_config()["model"], "my-model")
        command = runner.call_args.args[0]
        self.assertEqual(command[command.index("--provider") + 1], "my-provider")
        self.assertEqual(command[command.index("--model") + 1], "my-model")

    def test_task_limit_counts_utf16_units(self):
        for task in ("a" * 120_000, "\U0001f600" * 60_000, "\U0001f600" * 59_999 + "ab"):
            with self.subTest(length=len(task)):
                args = delegate.parse_args(["send", "thread-abc", "--task", task])
                self.assertEqual(delegate.build_command(args)[1], task)
        for task in ("a" * 120_001, "\U0001f600" * 60_001, "\U0001f600" * 60_000 + "a"):
            with self.subTest(length=len(task)):
                args = delegate.parse_args(["send", "thread-abc", "--task", task])
                with self.assertRaisesRegex(ValueError, "UTF-16"):
                    delegate.build_command(args)

    def test_start_noninteractive_requires_config(self):
        fake_stdin = Mock()
        fake_stdin.isatty.return_value = False
        args = delegate.parse_args(["start", "--task", "Implement tests"])
        with patch.object(delegate.sys, "stdin", fake_stdin):
            with self.assertRaisesRegex(ValueError, "non-interactive"):
                delegate.build_command(args)
        self.assertFalse(self.config_file.exists())

    def test_explicit_pair_overrides_saved_model_temporarily(self):
        delegate.save_config("old", "old-model")
        args = delegate.parse_args(["start", "--task", "Task", "--provider", "new", "--model", "new-model"])
        argv, _ = delegate.build_command(args)
        self.assertIn("new-model", argv)
        self.assertEqual(delegate.load_config()["model"], "old-model")

    def test_corrupt_or_outdated_config_rejected(self):
        self.config_file.parent.mkdir(parents=True)
        self.config_file.write_text("{invalid", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Cannot load config"):
            delegate.load_config()
        self.config_file.write_text('{"version":99,"providerInstanceId":"p","model":"m"}')
        with self.assertRaisesRegex(ValueError, "unsupported"):
            delegate.load_config()

    def test_invalid_selection_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonempty"):
            delegate.save_config("", "model")
        with self.assertRaisesRegex(ValueError, "control"):
            delegate.save_config("provider", "bad\nmodel")
        self.assertFalse(self.config_file.exists())

    @unittest.skipIf(os.name == "nt", "POSIX file permissions")
    def test_config_owner_only_permissions(self):
        path = delegate.save_config("provider", "model")
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        delegate.save_config("provider2", "model2")
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_show_and_list(self):
        self.assertEqual(
            delegate.build_command(delegate.parse_args(["show", "id", "--messages", "3"]))[0],
            ["t3", "thread", "show", "id", "--messages", "3", "--json"],
        )
        self.assertEqual(
            delegate.build_command(delegate.parse_args(["list", "--project", "."]))[0],
            ["t3", "thread", "list", "--project", ".", "--json"],
        )

    def test_wait_preserves_exit_code_and_json(self):
        finished = __import__("subprocess").CompletedProcess(
            args=[], returncode=2, stdout='{"threadId":"abc","status":"waiting"}\n',
            stderr="Needs approval.\n",
        )
        with patch.object(delegate.subprocess, "run", return_value=finished) as runner:
            with patch.object(delegate.sys, "stdout", new_callable=io.StringIO) as out:
                with patch.object(delegate.sys, "stderr", new_callable=io.StringIO) as err:
                    result = delegate.main(["send", "abc", "--task", "Continue", "--wait"])
        self.assertEqual(result, 2)
        self.assertIn('"status":"waiting"', out.getvalue())
        self.assertIn("Needs approval", err.getvalue())
        args, kwargs = runner.call_args
        self.assertEqual(args[0], ["t3", "thread", "send", "abc", "-", "--wait", "--json"])
        self.assertEqual(kwargs["input"], "Continue")
        self.assertFalse(kwargs["check"])

    def test_missing_cli_reports_error(self):
        with patch.object(delegate.subprocess, "run", side_effect=FileNotFoundError()):
            with patch.object(delegate.sys, "stderr", new_callable=io.StringIO) as err:
                result = delegate.main(["list"])
        self.assertEqual(result, 127)
        self.assertIn("not found", err.getvalue())

    def test_config_override_env_resolved(self):
        with patch.dict(os.environ, {"T3_DELEGATE_CONFIG": "relative.json"}):
            self.assertEqual(delegate.config_path(), (Path.cwd() / "relative.json").absolute())


if __name__ == "__main__":
    unittest.main()
