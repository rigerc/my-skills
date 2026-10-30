#!/usr/bin/env python3
"""Plan, render, and inventory VHS-based screenshot audits of terminal UIs.

No third-party dependencies are needed for planning and PNG metadata inspection.
Pillow is optional for contact sheets and basic image diagnostics.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SLUG = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")
KEY = re.compile(r"^(?:Enter|Escape|Tab|Backspace|Delete|Insert|Space|Up|Down|Left|Right|PageUp|PageDown|ScrollUp|ScrollDown|(?:Ctrl|Alt|Shift)\+[A-Za-z0-9+]+)$")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class PlanError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise PlanError(message)


def slug(value, label):
    require(isinstance(value, str) and bool(SLUG.fullmatch(value)),
            f"{label} must use 1-64 letters, digits, '_' or '-', starting with a letter/digit")
    return value


def one_line(value, label):
    require(isinstance(value, str) and bool(value) and "\n" not in value and "\r" not in value and "\x00" not in value,
            f"{label} must be a non-empty, single-line string")
    return value


def type_lines(value):
    """Type literal text using VHS delimiters, which do not support escapes."""
    one_line(value, "Type text")
    for delimiter in ('"', "'", "`"):
        if delimiter not in value:
            return [f"Type {delimiter}{value}{delimiter}"]
    # Separate Type commands add no spaces; split text containing all delimiters.
    lines = []
    for fragment in re.findall(r'[^"]+|"', value):
        delimiter = "'" if fragment == '"' else '"'
        lines.append(f"Type {delimiter}{fragment}{delimiter}")
    return lines


def wait_literal(value):
    # VHS uses Go's regexp syntax: Python re.escape() emits unsupported escapes
    # for spaces/punctuation. Hex-encode '/' to avoid ending the tape delimiter.
    one_line(value, "wait_for")
    return re.sub(r"([\\.+*?()|\[\]{}^$])", r"\\\1", value).replace("/", r"\x2f")


def validate_actions(actions, context):
    require(isinstance(actions, list), f"{context} actions must be a list")
    for i, action in enumerate(actions):
        loc = f"{context} action {i + 1}"
        require(isinstance(action, dict), f"{loc} must be an object")
        require(set(action) in ({"key"}, {"key", "repeat"}, {"text"}),
                f"{loc} must have exactly 'key' (optionally 'repeat') or 'text'")
        if "key" in action:
            require(isinstance(action["key"], str) and bool(KEY.fullmatch(action["key"])),
                    f"{loc}: unsupported key {action['key']!r}")
            require(isinstance(action.get("repeat", 1), int) and not isinstance(action.get("repeat", 1), bool)
                    and 1 <= action.get("repeat", 1) <= 30, f"{loc}: repeat must be 1..30")
        else:
            one_line(action["text"], f"{loc}.text")


def validate_plan(plan, plan_file):
    require(isinstance(plan, dict), "Plan root must be an object")
    slug(plan.get("app_id"), "app_id")
    one_line(plan.get("launch"), "launch")
    cwd_raw = plan.get("cwd", ".")
    one_line(cwd_raw, "cwd")
    cwd = (plan_file.parent / cwd_raw).resolve()
    require(cwd.is_dir(), f"cwd does not exist: {cwd}")
    viewports = plan.get("viewports")
    scenarios = plan.get("scenarios")
    require(isinstance(viewports, list) and viewports, "viewports must be a non-empty list")
    require(isinstance(scenarios, list) and scenarios, "scenarios must be a non-empty list")
    names = set()
    for vp in viewports:
        require(isinstance(vp, dict), "Each viewport must be an object")
        name = slug(vp.get("id"), "viewport id")
        require(name not in names, f"Duplicate viewport id: {name}")
        names.add(name)
        for k, lo, hi in (("width", 480, 4096), ("height", 260, 2160), ("font_size", 9, 48)):
            v = vp.get(k)
            require(type(v) is int and lo <= v <= hi, f"viewport {name}: {k} must be {lo}..{hi}")
    names = set()
    for scenario in scenarios:
        require(isinstance(scenario, dict), "Each scenario must be an object")
        name = slug(scenario.get("id"), "scenario id")
        require(name not in names, f"Duplicate scenario id: {name}")
        names.add(name)
        steps = scenario.get("steps")
        require(isinstance(steps, list) and steps, f"scenario {name} requires at least one step")
        step_ids = set()
        for step in steps:
            require(isinstance(step, dict), f"scenario {name}: step must be object")
            sid = slug(step.get("id"), "step id")
            require(sid not in step_ids, f"scenario {name}: duplicate step {sid}")
            step_ids.add(sid)
            validate_actions(step.get("actions", []), f"{name}/{sid}")
            if "wait_for" in step:
                wait_literal(step["wait_for"])
            if "settle_ms" in step:
                require(type(step["settle_ms"]) is int and 0 <= step["settle_ms"] <= 30000,
                        f"{name}/{sid}: settle_ms must be 0..30000")
            require(type(step.get("screenshot", True)) is bool, f"{name}/{sid}: screenshot must be boolean")
            if "inspect_for" in step:
                one_line(step["inspect_for"], f"{name}/{sid}.inspect_for")
        validate_actions(scenario.get("exit_actions", [{"key": "Ctrl+C"}]), f"{name}/exit")
    require(any(step.get("screenshot", True) for scenario in scenarios for step in scenario["steps"]),
            "Plan must capture at least one screenshot")
    run_ids = set()
    for vp in viewports:
        for scenario in scenarios:
            run_id = f"{scenario['id']}--{vp['id']}"
            require(run_id not in run_ids,
                    f"Scenario/viewport ids produce a duplicate run directory: {run_id}; rename an id")
            run_ids.add(run_id)
    return cwd


def action_lines(actions):
    lines = []
    for action in actions:
        if "text" in action:
            lines += type_lines(action["text"])
        else:
            key = action["key"]
            repeat = action.get("repeat", 1)
            # Repetition is explicit for reliable modifier-key handling.
            lines += [key] * repeat
    return lines


def generate_tape(plan, cwd, vp, scenario, rel_paths):
    """Return tape source; paths in rel_paths are relative to tape cwd."""
    lines = [
        "# Generated by tui-vhs-audit. Review the launch command before executing.",
        "Output recording.gif",
        "Set Shell bash",
        f"Set Width {vp['width']}",
        f"Set Height {vp['height']}",
        f"Set FontSize {vp['font_size']}",
        "Set Framerate 15",
        "Set TypingSpeed 1ms",
        "Set Theme \"Catppuccin Mocha\"",
        "",
        "# Start from an explicit workspace; only run trusted fixture commands.",
    ]
    lines += type_lines('cd ' + shlex.quote(str(cwd)) + ' && ' + plan['launch'])
    lines.append("Enter")
    for step in scenario["steps"]:
        lines += ["", f"# State: {step['id']}"]
        lines += action_lines(step.get("actions", []))
        if step.get("settle_ms", 250):
            lines.append(f"Sleep {step.get('settle_ms', 250)}ms")
        if "wait_for" in step:
            lines.append(f"Wait+Screen /{wait_literal(step['wait_for'])}/")
        if step.get("screenshot", True):
            lines.append(f"Screenshot {rel_paths[step['id']]}")
            # VHS queues the next video frame; hold the state before more input or exit.
            lines.append("Sleep 250ms")
    exit_actions = scenario.get("exit_actions", [{"key": "Ctrl+C"}])
    if exit_actions:
        lines += ["", "# Exit without altering the recorded screenshots."] + action_lines(exit_actions)
    lines.append("")
    return "\n".join(lines)


def discard_capture_artifacts(out, manifest):
    """Remove only recorded artifact paths strictly beneath the audit directory."""
    for run in manifest.get("runs", []):
        for rel in [run.get("recording")] + [c.get("path") for c in run.get("captures", [])]:
            if not isinstance(rel, str):
                continue
            path = (out / rel).resolve()
            if path.is_relative_to(out.resolve()) and path.is_file():
                path.unlink()


def repo_root(directory):
    """Find the audited application's Git root, including in Git worktrees."""
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=False,
        )
    except FileNotFoundError as exc:
        raise PlanError("Git is required for the default .tui-audit location") from exc
    require(result.returncode == 0 and bool(result.stdout.strip()),
            f"Not inside a Git repository: {directory} (or pass --out explicitly)")
    return Path(result.stdout.strip()).resolve()


def audit_output(args, directory):
    """Default to the audited repository's private artifacts directory."""
    if args.out is not None:
        return args.out.resolve()
    out = repo_root(directory) / ".tui-audit"
    require(not out.is_symlink(), f"Refusing symlinked audit directory: {out}")
    return out


def ensure_gitignore(out):
    """Ignore generated screenshots at the target repo root without overwriting rules."""
    ignore = out.parent / ".gitignore"
    require(not ignore.is_symlink(), f"Refusing symlinked .gitignore: {ignore}")
    existing = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    if "/.tui-audit/" not in existing.splitlines():
        with ignore.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write("/.tui-audit/\n")


def cmd_prepare(args):
    plan_file = args.plan.resolve()
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    cwd = validate_plan(plan, plan_file)
    out = audit_output(args, cwd)
    require(out != cwd, "Audit output must not overwrite the app's working directory")
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        if not args.force:
            raise PlanError(f"Audit already exists: {manifest_path} (use --force to regenerate)")
        discard_capture_artifacts(out, json.loads(manifest_path.read_text(encoding="utf-8")))
        for stale in ("render-results.json", "inspection.json", "contact-sheet.png", "audit-report.new.md"):
            path = out / stale
            if path.is_file():
                path.unlink()
    # Auto-ignore the default output in the target repository, not the skill install.
    if args.out is None:
        ensure_gitignore(out)
    out.mkdir(parents=True, exist_ok=True)
    runs = []
    for vp in plan["viewports"]:
        for scenario in plan["scenarios"]:
            run_id = f"{scenario['id']}--{vp['id']}"
            run_dir = out / run_id
            screenshots = run_dir / "screens"
            screenshots.mkdir(parents=True, exist_ok=True)
            rel_paths = {}
            captures = []
            for n, step in enumerate(scenario["steps"], start=1):
                if step.get("screenshot", True):
                    relpath = f"screens/{n:02d}-{step['id']}.png"
                    rel_paths[step["id"]] = relpath
                    captures.append({
                        "step": step["id"], "path": f"{run_id}/{relpath}",
                        "wait_for": step.get("wait_for"),
                        "inspect_for": step.get("inspect_for", "Review layout, focus, clipping, and contrast"),
                    })
            (run_dir / "audit.tape").write_text(generate_tape(plan, cwd, vp, scenario, rel_paths), encoding="utf-8")
            runs.append({
                "id": run_id, "viewport": vp, "scenario": scenario["id"],
                "description": scenario.get("description", ""),
                "tape": f"{run_id}/audit.tape", "recording": f"{run_id}/recording.gif",
                "captures": captures,
            })
    manifest = {
        "app_id": plan["app_id"], "cwd": str(cwd), "launch": plan["launch"],
        "source_plan": str(plan_file), "created_utc": datetime.now(timezone.utc).isoformat(),
        "runs": runs,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(runs)} tapes and {sum(len(r['captures']) for r in runs)} screenshot targets in {out}")
    print("No target command or VHS recording was executed. Review each tape before running.")
    return 0


def read_manifest(out):
    path = out / "manifest.json"
    require(path.exists(), f"Manifest missing: {path} (run prepare first)")
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_run(args):
    out = audit_output(args, Path.cwd())
    require(args.timeout_sec > 0, "--timeout-sec must be greater than zero")
    manifest = read_manifest(out)
    missing = [binary for binary in ("vhs", "ttyd", "ffmpeg") if shutil.which(binary) is None]
    if missing:
        print(f"BLOCKED: missing recording dependencies: {', '.join(missing)}", file=sys.stderr)
        return 2
    if not args.yes:
        print("Refusing to execute unreviewed launch commands; use --yes after inspecting tapes.", file=sys.stderr)
        return 2
    # Clear the whole batch before rendering: an early failure skips later runs.
    discard_capture_artifacts(out, manifest)
    for stale in ("render-results.json", "inspection.json", "contact-sheet.png"):
        (out / stale).unlink(missing_ok=True)
    results = {}
    for run in manifest["runs"]:
        tape = out / run["tape"]
        print(f"RUN: {run['id']}", flush=True)
        try:
            proc = subprocess.run(["vhs", tape.name], cwd=tape.parent, timeout=args.timeout_sec,
                                  check=False)
            results[run["id"]] = {"exit_code": proc.returncode}
        except subprocess.TimeoutExpired:
            results[run["id"]] = {"error": f"timed out after {args.timeout_sec}s"}
        if results[run["id"]].get("exit_code") != 0:
            print(f"FAILED: {run['id']} {results[run['id']]}", file=sys.stderr)
            if not args.keep_going:
                break
    (out / "render-results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 0 if len(results) == len(manifest["runs"]) and all(x.get("exit_code") == 0 for x in results.values()) else 1


def png_info(path):
    if not path.exists():
        return {"status": "missing"}
    if path.stat().st_size < 24:
        return {"status": "invalid", "reason": "PNG too small"}
    with path.open("rb") as f:
        header = f.read(24)
    if not header.startswith(PNG_MAGIC) or header[12:16] != b"IHDR":
        return {"status": "invalid", "reason": "bad PNG signature/IHDR"}
    w, h = struct.unpack(">II", header[16:24])
    if not 0 < w <= 10000 or not 0 < h <= 10000:
        return {"status": "invalid", "reason": "implausible dimensions"}
    result = {"status": "captured", "bytes": path.stat().st_size, "width": w, "height": h}
    try:
        from PIL import Image, ImageStat
        with Image.open(path) as img:
            img.load()
            rgb = img.convert("RGB")
            stat = ImageStat.Stat(rgb)
            if max(stat.stddev) < 1.0:
                result["warning"] = "Nearly uniform frame; check for blank screen"
    except ImportError:
        pass
    except Exception as e:
        result = {"status": "invalid", "reason": f"Pillow could not decode PNG: {e}"}
    return result


def make_contact_sheet(out, manifest, results):
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        return "Pillow not installed: contact sheet skipped"
    captures = [(run, cap) for run in manifest["runs"] for cap in run["captures"]
                if results[cap["path"]]["status"] == "captured"]
    if not captures:
        return "No valid screenshots: contact sheet skipped"
    tile_w, img_h, label_h, margin = 550, 330, 44, 12
    cols = 2
    rows = (len(captures) + cols - 1) // cols
    image = Image.new("RGB", (cols * tile_w, rows * (img_h + label_h)), "#f2f2f2")
    draw = ImageDraw.Draw(image)
    for i, (run, cap) in enumerate(captures):
        x = (i % cols) * tile_w
        y = (i // cols) * (img_h + label_h)
        label = f"{run['id']} / {cap['step']}"
        draw.text((x + margin, y + 9), label[:72], fill="#1c1c1c")
        with Image.open(out / cap["path"]) as src:
            thumb = ImageOps.contain(src.convert("RGB"), (tile_w - 2 * margin, img_h - 2 * margin))
            image.paste(thumb, (x + (tile_w - thumb.width) // 2, y + label_h + (img_h - thumb.height) // 2))
    image.save(out / "contact-sheet.png")
    return "contact-sheet.png"


def cmd_inspect(args):
    out = audit_output(args, Path.cwd())
    manifest = read_manifest(out)
    statuses = {}
    for run in manifest["runs"]:
        for cap in run["captures"]:
            statuses[cap["path"]] = png_info(out / cap["path"])
    report = {"application": manifest["app_id"], "captures": statuses,
              "captured": sum(v["status"] == "captured" for v in statuses.values()),
              "total": len(statuses),
              "visual_reviewed": False}
    (out / "inspection.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    contact_sheet = make_contact_sheet(out, manifest, statuses) if not args.no_contact_sheet else "Not requested"
    lines = [
        f"# TUI visual audit: {manifest['app_id']}", "",
        "## Evidence status", "",
        f"- **Screenshot inventory:** {report['captured']}/{report['total']} valid PNG headers (decoded when Pillow is available).",
        f"- **Contact sheet:** {contact_sheet}",
        "- **Visual review:** PENDING. Artifact checks do not establish visual or functional correctness.",
        "- **VHS execution:** Consult `render-results.json` if present; screenshots alone do not prove all test steps passed.",
        "", "## Coverage", "",
        "| Scenario | Viewport | State | Screenshot | Capture | Review focus |",
        "|---|---|---|---|---|---|",
    ]
    for run in manifest["runs"]:
        vp = run["viewport"]
        for cap in run["captures"]:
            status = statuses[cap["path"]]["status"]
            focus = cap["inspect_for"].replace("|", "\\|")
            path = cap["path"]
            lines.append(f"| {run['scenario']} | {vp['id']} ({vp['width']}×{vp['height']}) | {cap['step']} | [PNG]({path}) | {status} | {focus} |")
    lines += [
        "", "## Review checklist (inspect actual PNGs)", "",
        "- [ ] Text does not wrap, overflow, clip, or collide at each viewport.",
        "- [ ] Selected and focused controls are distinguishable; keyboard navigation behaves as expected.",
        "- [ ] Foreground/background contrast, states and status messages are legible.",
        "- [ ] Empty, error, loading, help, modal, and long-content states are covered where applicable.",
        "- [ ] Labels, hints, borders and table columns align and remain consistent across screens.",
        "- [ ] No credentials, personal data or production information appear in captures.",
        "", "## Findings", "",
        "No findings verified yet. After reviewing screenshots, record each issue with severity, screenshot, reproduction steps, expected versus observed behavior, and a suggested fix.",
        "", "### Finding format", "",
        "**ID / Severity / State / Viewport:** …  ",
        "**Evidence:** `relative/path.png`  ",
        "**Steps to reproduce:** …  ",
        "**Expected:** …  ",
        "**Observed:** …  ",
        "**Recommendation:** …", "",
    ]
    report_target = out / "audit-report.md"
    if report_target.exists() and not getattr(args, "overwrite_report", False):
        report_target = out / "audit-report.new.md"
    report_target.write_text("\n".join(lines), encoding="utf-8")
    print(f"Inspected {report['captured']}/{report['total']} screenshots. Visual review remains pending.")
    print(f"Report: {report_target}")
    print(f"Contact sheet: {contact_sheet}")
    return 0 if report["captured"] == report["total"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    prep = subs.add_parser("prepare", help="Generate reproducible VHS tapes and screenshot manifest (no app execution)")
    prep.add_argument("plan", type=Path)
    prep.add_argument("--out", type=Path, help="Override the default <app Git root>/.tui-audit")
    prep.add_argument("--force", action="store_true")
    run = subs.add_parser("run", help="Execute generated tapes with local VHS; requires explicit --yes")
    run.add_argument("--out", type=Path, help="Override the default <current Git root>/.tui-audit")
    run.add_argument("--yes", action="store_true", help="I have reviewed and trust all shell commands in the tapes")
    run.add_argument("--timeout-sec", type=int, default=120)
    run.add_argument("--keep-going", action="store_true")
    inspect = subs.add_parser("inspect", help="Inventory captures and generate contact sheet/report skeleton")
    inspect.add_argument("--out", type=Path, help="Override the default <current Git root>/.tui-audit")
    inspect.add_argument("--no-contact-sheet", action="store_true")
    inspect.add_argument("--overwrite-report", action="store_true", help="Replace an existing audit-report.md")
    args = parser.parse_args()
    try:
        return {"prepare": cmd_prepare, "run": cmd_run, "inspect": cmd_inspect}[args.command](args)
    except (PlanError, json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
