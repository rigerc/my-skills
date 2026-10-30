import copy
import importlib.util
import json
import re
import shlex
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_tui.py"
spec = importlib.util.spec_from_file_location("audit_tui", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def plan():
    return {
        "app_id": "demo", "cwd": ".", "launch": "printf 'hi'",
        "viewports": [{"id": "small", "width": 720, "height": 400, "font_size": 18}],
        "scenarios": [{"id": "main", "steps": [
            {"id": "start", "wait_for": "Ready (1/2)", "actions": [{"key": "Down", "repeat": 2}]},
            {"id": "help", "actions": [{"text": "?"}], "wait_for": "Help", "settle_ms": 0},
        ]}],
    }


def create_png(path):
    """Construct a small valid RGB PNG with standard-library only."""
    def chunk(name, data):
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data))
    w, h = 4, 2
    data = (b"\x00" + b"\x00\x99\xff" * w) * h
    path.write_bytes(mod.PNG_MAGIC + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
                     chunk(b"IDAT", zlib.compress(data)) + chunk(b"IEND", b""))


class AuditTests(unittest.TestCase):
    def test_wait_literal_is_go_regex_compatible(self):
        # re.escape inserts '\\ ' and '\\/' that Go regexp does not accept.
        cases = {
            "Ready (1/2)": r"Ready \\(1\\x2f2\\)",
            "Done: 100%! #1": "Done: 100%! #1",
            r"Path\\name [ok]?": r"Path\\\\name \\[ok\\]\\?",
        }
        for literal, expected in cases.items():
            with self.subTest(literal=literal):
                regex = mod.wait_literal(literal)
                self.assertEqual(regex, expected)
                self.assertIsNotNone(re.fullmatch(regex, literal))

    @unittest.skipUnless(shutil.which("git"), "Git required for repo-root default")
    def test_default_output_is_repo_local_and_gitignored(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "app"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            nested = repo / "ui"
            nested.mkdir()
            source = repo / "plan.json"
            data = plan()
            data["cwd"] = "ui"
            source.write_text(json.dumps(data))
            ignore = repo / ".gitignore"
            ignore.write_text("# Existing ignores\\n__pycache__/\\n")
            args = SimpleNamespace(plan=source, out=None, force=False)
            self.assertEqual(mod.cmd_prepare(args), 0)
            out = repo / ".tui-audit"
            self.assertTrue((out / "main--small" / "audit.tape").exists())
            self.assertIn("Screenshot screens/01-start.png",
                          (out / "main--small" / "audit.tape").read_text())
            self.assertEqual(ignore.read_text(), "# Existing ignores\\n__pycache__/\\n/.tui-audit/\\n")
            self.assertEqual(mod.repo_root(nested), repo.resolve())

            report = out / "audit-report.md"
            report.write_text("Reviewed findings")
            args.force = True
            self.assertEqual(mod.cmd_prepare(args), 0)
            self.assertEqual(report.read_text(), "Reviewed findings")
            self.assertEqual(ignore.read_text().count("/.tui-audit/"), 1)
            with patch.object(mod.Path, "cwd", return_value=nested):
                self.assertEqual(mod.cmd_inspect(SimpleNamespace(out=None, no_contact_sheet=True)), 1)
            self.assertEqual(report.read_text(), "Reviewed findings")
            self.assertTrue((out / "audit-report.new.md").exists())
            self.assertIn("navigation", json.dumps(data["scenarios"]))

    def test_rejects_plan_with_no_screenshots(self):
        with tempfile.TemporaryDirectory() as td:
            data = plan()
            for step in data["scenarios"][0]["steps"]:
                step["screenshot"] = False
            with self.assertRaisesRegex(mod.PlanError, "at least one screenshot"):
                mod.validate_plan(data, Path(td) / "plan.json")

    def test_rejects_nonpositive_run_timeout(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(mod.PlanError, "greater than zero"):
                mod.cmd_run(SimpleNamespace(out=Path(td), timeout_sec=0))

    def test_type_commands_preserve_launch_and_input(self):
        # VHS strings end at the next matching delimiter; backslashes are literal.
        def typed_text(source):
            fragments = []
            for line in source.splitlines():
                if line.startswith("Type "):
                    match = re.fullmatch(r'''Type (["'`])(.*)\1''', line)
                    self.assertIsNotNone(match, line)
                    delimiter, content = match.groups()
                    self.assertNotIn(delimiter, content)
                    fragments.append(content)
            return "".join(fragments)

        texts = ['plain', './app --data "fixture path"', "'single quotes'",
                 r"back\slash", "日本語 café 🐱", "mix 'single' \"double\" `ticks`",
                 "\"'`", "\tindented"]
        with tempfile.TemporaryDirectory() as td:
            # Shell quoting this directory also exercises mixed VHS delimiters.
            cwd = Path(td) / "café 'single' \"double\" `ticks`"
            for text in texts:
                with self.subTest(text=text):
                    data = plan()
                    data["launch"] = text
                    data["scenarios"][0]["steps"] = [
                        {"id": "input", "actions": [{"text": text}]},
                    ]
                    tape = mod.generate_tape(data, cwd, data["viewports"][0],
                                             data["scenarios"][0], {"input": "screens/input.png"})
                    launch, actions = tape.split("\nEnter\n", 1)
                    self.assertEqual(typed_text(launch), f"cd {shlex.quote(str(cwd))} && {text}")
                    self.assertEqual(typed_text(actions), text)

    def test_colliding_run_ids_fail_before_writing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "plan.json"
            source.write_text(json.dumps(plan()))
            existing = root / "existing"
            mod.cmd_prepare(SimpleNamespace(plan=source, out=existing, force=False))
            manifest_before = (existing / "manifest.json").read_bytes()
            tape_path = existing / "main--small" / "audit.tape"
            tape_before = tape_path.read_bytes()
            screenshot = existing / "main--small" / "screens" / "01-start.png"
            create_png(screenshot)
            screenshot_before = screenshot.read_bytes()

            data = plan()
            data["viewports"][0]["id"] = "c"
            data["viewports"].append(dict(data["viewports"][0], id="b--c"))
            data["scenarios"][0]["id"] = "a--b"
            other = copy.deepcopy(data["scenarios"][0])
            other["id"] = "a"
            data["scenarios"].append(other)
            source.write_text(json.dumps(data))
            for out, force in ((root / "new", False), (existing, True)):
                with self.subTest(force=force):
                    with self.assertRaisesRegex(mod.PlanError, "duplicate run directory"):
                        mod.cmd_prepare(SimpleNamespace(plan=source, out=out, force=force))
            self.assertFalse((root / "new").exists())
            self.assertEqual((existing / "manifest.json").read_bytes(), manifest_before)
            self.assertEqual(tape_path.read_bytes(), tape_before)
            self.assertEqual(screenshot.read_bytes(), screenshot_before)

    def test_failed_rerun_clears_all_previous_captures(self):
        for timeout in (False, True):
            with self.subTest(timeout=timeout), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                data = plan()
                data["viewports"].append(dict(data["viewports"][0], id="desktop"))
                source = root / "plan.json"
                source.write_text(json.dumps(data))
                out = root / "audit"
                mod.cmd_prepare(SimpleNamespace(plan=source, out=out, force=False))
                manifest = json.loads((out / "manifest.json").read_text())
                artifacts = []
                for run in manifest["runs"]:
                    recording = out / run["recording"]
                    recording.write_bytes(b"old GIF")
                    artifacts.append(recording)
                    for cap in run["captures"]:
                        capture = out / cap["path"]
                        create_png(capture)
                        artifacts.append(capture)
                stale = [out / name for name in
                         ("render-results.json", "inspection.json", "contact-sheet.png")]
                for artifact in stale:
                    artifact.write_bytes(b"old result")
                report = out / "audit-report.md"
                report.write_text("Reviewed findings")
                unrelated = out / "notes.txt"
                unrelated.write_text("Keep me")

                def fail_first(*args, **kwargs):
                    self.assertTrue(all(not artifact.exists() for artifact in artifacts + stale))
                    if timeout:
                        raise mod.subprocess.TimeoutExpired(args[0], kwargs["timeout"])
                    return SimpleNamespace(returncode=1)

                with patch.object(mod.shutil, "which", return_value="/mock/binary"), \
                        patch.object(mod.subprocess, "run", side_effect=fail_first) as render:
                    self.assertEqual(mod.cmd_run(SimpleNamespace(
                        out=out, yes=True, timeout_sec=5, keep_going=False)), 1)
                render.assert_called_once()
                results = json.loads((out / "render-results.json").read_text())
                self.assertEqual(list(results), [manifest["runs"][0]["id"]])
                self.assertTrue(all(not artifact.exists() for artifact in artifacts))
                self.assertEqual(mod.cmd_inspect(SimpleNamespace(out=out, no_contact_sheet=True)), 1)
                inspection = json.loads((out / "inspection.json").read_text())
                self.assertEqual(inspection["captured"], 0)
                self.assertEqual(inspection["total"], 4)
                self.assertEqual(report.read_text(), "Reviewed findings")
                self.assertEqual(unrelated.read_text(), "Keep me")

    def test_tape_generation_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "plan.json"
            source.write_text(json.dumps(plan()))
            out = root / "audit"
            self.assertEqual(mod.cmd_prepare(type("Args", (), {"plan": source, "out": out, "force": False})()), 0)
            data = json.loads((out / "manifest.json").read_text())
            self.assertEqual(len(data["runs"]), 1)
            tape = (out / "main--small" / "audit.tape").read_text()
            self.assertIn("Screenshot screens/01-start.png", tape)
            self.assertIn("Screenshot screens/02-help.png", tape)
            self.assertIn(r"Wait+Screen /Ready\ \(1\/2\)/", tape)
            self.assertEqual(tape.splitlines().count("Down"), 2)
            self.assertIn('Type "?"', tape)
            with self.assertRaises(mod.PlanError):
                mod.cmd_prepare(type("Args", (), {"plan": source, "out": out, "force": False})())

    def test_rejects_invalid_actions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bad = plan()
            bad["scenarios"][0]["steps"][0]["actions"] = [{"key": "Down; rm -rf"}]
            with self.assertRaises(mod.PlanError):
                mod.validate_plan(bad, root / "plan.json")

    def test_inspection_missing_and_valid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "plan.json"
            source.write_text(json.dumps(plan()))
            out = root / "audit"
            mod.cmd_prepare(type("Args", (), {"plan": source, "out": out, "force": False})())
            args = type("Args", (), {"out": out, "no_contact_sheet": True})()
            self.assertEqual(mod.cmd_inspect(args), 1)
            self.assertIn("missing", (out / "audit-report.md").read_text())
            for run in json.loads((out / "manifest.json").read_text())["runs"]:
                for capture in run["captures"]:
                    create_png(out / capture["path"])
            self.assertEqual(mod.cmd_inspect(args), 0)
            report = json.loads((out / "inspection.json").read_text())
            self.assertEqual(report["captured"], 2)
            self.assertFalse(report["visual_reviewed"])
            self.assertEqual(mod.png_info(out / "main--small" / "screens" / "01-start.png")["width"], 4)

    def test_inspection_rejects_corrupted_png(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.png"
            p.write_bytes(b"garbage")
            self.assertEqual(mod.png_info(p)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
