#!/usr/bin/env python3
"""Manage a saved T3 provider/model selection and T3 *top-level* threads.

This CLI uses `t3 thread ...` and does NOT create native `delegate_task` children.
Use the T3 MCP `delegate_task` tool for true parent-linked subagents.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_TASK_CHARS = 120_000
CONFIG_VERSION = 1


def config_path() -> Path:
    """Stable user-level config, independent of installed skill directory."""
    explicit = os.environ.get("T3_DELEGATE_CONFIG")
    if explicit:
        return Path(explicit).expanduser().absolute()
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(config_home).expanduser() if config_home else Path.home() / ".config"
    return (base / "t3-delegate" / "config.json").absolute()


def validate_selection(provider: object, model: object) -> dict[str, object]:
    for name, value in (("providerInstanceId", provider), ("model", model)):
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise ValueError(f"{name} must be a nonempty string without surrounding whitespace.")
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError(f"{name} may not contain control characters.")
    return {"version": CONFIG_VERSION, "providerInstanceId": provider, "model": model}


def load_config() -> dict[str, object] | None:
    path = config_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot load config at {path}: {error}") from error
    if not isinstance(data, dict) or data.get("version") != CONFIG_VERSION:
        raise ValueError(f"Invalid or unsupported t3-delegate config at {path}.")
    return validate_selection(data.get("providerInstanceId"), data.get("model"))


def save_config(provider: str, model: str) -> Path:
    selection = validate_selection(provider, model)
    path = config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Temp file is created mode 0600 and atomically replaces the destination.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".config-", suffix=".tmp", delete=False,
        ) as file:
            temporary = Path(file.name)
            try:
                json.dump(selection, file, indent=2)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
        try:
            os.chmod(temporary, 0o600)
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    except OSError as error:
        raise ValueError(f"Cannot save config at {path}: {error}") from error
    return path


def prompt_selection() -> dict[str, object]:
    if not sys.stdin.isatty():
        raise ValueError(
            "Provider/model not configured and stdin is non-interactive. "
            "Run 't3_delegate.py config set --provider INSTANCE --model SLUG' "
            "or 't3_delegate.py config init' in a terminal."
        )
    print("Choose a T3 provider instance ID and model slug to save as the default.", file=sys.stderr)
    print("Find exact values with orchestrator_capabilities or T3 Settings > Providers.", file=sys.stderr)
    try:
        print("Provider instance ID: ", end="", file=sys.stderr, flush=True)
        provider = input().strip()
        print("Model slug: ", end="", file=sys.stderr, flush=True)
        model = input().strip()
    except (EOFError, KeyboardInterrupt) as error:
        raise ValueError("Provider/model selection cancelled.") from error
    return validate_selection(provider, model)


def selected_provider_model(args: argparse.Namespace) -> tuple[str, str]:
    # Explicit flags override the persisted default for this one launch only.
    if bool(args.provider) != bool(args.model):
        raise ValueError("--provider and --model must be passed together.")
    if args.provider:
        selection = validate_selection(args.provider, args.model)
    else:
        selection = load_config()
        if selection is None:
            selection = prompt_selection()
            save_config(selection["providerInstanceId"], selection["model"])
            print(f"Saved provider/model defaults at {config_path()}", file=sys.stderr)
    return str(selection["providerInstanceId"]), str(selection["model"])


def read_task(args: argparse.Namespace) -> str:
    if args.task is not None:
        task = args.task
    elif args.task_file is not None:
        try:
            task = Path(args.task_file).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ValueError(f"Cannot read task file: {error}") from error
    elif not sys.stdin.isatty():
        task = sys.stdin.read()
    else:
        raise ValueError("Pass --task, --task-file, or pipe a task through stdin.")

    if not task.strip():
        raise ValueError("Task text cannot be empty.")
    # T3's JavaScript contract measures UTF-16 code units, not Python code points.
    utf16_units = sum(2 if ord(char) > 0xFFFF else 1 for char in task)
    if utf16_units > MAX_TASK_CHARS:
        raise ValueError(f"Task is longer than {MAX_TASK_CHARS:,} UTF-16 code units.")
    return task


def build_command(args: argparse.Namespace) -> tuple[list[str], str | None]:
    command = ["t3", "thread", args.action]
    stdin: str | None = None
    if args.action == "start":
        if bool(args.provider) != bool(args.model):
            raise ValueError("--provider and --model must be passed together.")
        if args.branch and not args.worktree:
            raise ValueError("--branch requires --worktree BASE_REF.")
        stdin = read_task(args)
        provider, model = selected_provider_model(args)
        command += [args.project, "-", "--title", args.title or stdin.strip().splitlines()[0][:80]]
        if args.worktree:
            command += ["--worktree", args.worktree]
        if args.branch:
            command += ["--branch", args.branch]
        command += ["--provider", provider, "--model", model]
        if args.wait:
            command.append("--wait")
    elif args.action == "send":
        stdin = read_task(args)
        command += [args.thread, "-"]
        if args.wait:
            command.append("--wait")
    elif args.action == "show":
        if args.messages < 0:
            raise ValueError("--messages must be nonnegative.")
        command += [args.thread, "--messages", str(args.messages)]
    elif args.action == "list":
        command += ["--project", args.project]
    else:
        raise ValueError(f"Unknown action: {args.action}")
    return command + ["--json"], stdin


def handle_config(args: argparse.Namespace) -> int:
    if args.config_action == "show":
        selection = load_config()
        print(json.dumps({"path": str(config_path()), "configured": selection is not None,
                          "selection": selection}, indent=2))
    elif args.config_action == "clear":
        try:
            config_path().unlink(missing_ok=True)
        except OSError as error:
            raise ValueError(f"Cannot clear config at {config_path()}: {error}") from error
        print(f"Cleared provider/model defaults at {config_path()}")
    else:
        if args.config_action == "init":
            selection = prompt_selection()
        elif args.config_action == "set":
            selection = validate_selection(args.provider, args.model)
        else:
            raise ValueError(f"Unknown config action: {args.config_action}")
        path = save_config(selection["providerInstanceId"], selection["model"])
        print(f"Saved provider={selection['providerInstanceId']} model={selection['model']} to {path}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Configure T3 provider/model and manage top-level threads (not native children)."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)

    def add_task_arguments(p: argparse.ArgumentParser) -> None:
        source = p.add_mutually_exclusive_group()
        source.add_argument("--task", help="Task text (may be multiline).")
        source.add_argument("--task-file", help="UTF-8 file containing task text.")

    config = subparsers.add_parser("config", help="Manage persistent provider/model defaults.")
    config_sub = config.add_subparsers(dest="config_action", required=True)
    config_sub.add_parser("show", help="Show config path and saved provider/model.")
    config_sub.add_parser("init", help="Interactively ask and save provider/model.")
    config_sub.add_parser("clear", help="Remove saved defaults.")
    setting = config_sub.add_parser("set", help="Save provider/model (non-interactive).")
    setting.add_argument("--provider", required=True, help="Exact T3 provider instance ID.")
    setting.add_argument("--model", required=True, help="Exact T3 model slug.")

    start = subparsers.add_parser("start", help="Start a new top-level T3 thread.")
    start.add_argument("--project", default=".", help="Registered project ID or path within it.")
    start.add_argument("--title", help="Thread title.")
    start.add_argument("--worktree", help="New worktree's base branch, tag or commit.")
    start.add_argument("--branch", help="Optional branch name for the new worktree.")
    start.add_argument("--provider", help="Override saved provider ID for this launch (requires --model).")
    start.add_argument("--model", help="Override saved model for this launch (requires --provider).")
    start.add_argument("--wait", action="store_true", help="Wait and print agent's reply.")
    add_task_arguments(start)

    send = subparsers.add_parser("send", help="Queue a follow-up to a T3 thread.")
    send.add_argument("thread", help="Thread ID returned by start.")
    send.add_argument("--wait", action="store_true", help="Wait and print agent's reply.")
    add_task_arguments(send)

    show = subparsers.add_parser("show", help="Show a thread and its latest messages.")
    show.add_argument("thread")
    show.add_argument("--messages", type=int, default=10)

    listed = subparsers.add_parser("list", help="List a project's threads.")
    listed.add_argument("--project", default=".")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.action == "config":
            return handle_config(args)
        command, task_input = build_command(args)
        result = subprocess.run(
            command, input=task_input, capture_output=True, text=True, check=False
        )
    except ValueError as error:
        print(f"t3-delegate: {error}", file=sys.stderr)
        return 64
    except FileNotFoundError:
        print("t3-delegate: t3 CLI not found on PATH. Install T3 Code first.", file=sys.stderr)
        return 127
    except OSError as error:
        print(f"t3-delegate: failed to run t3: {error}", file=sys.stderr)
        return 1

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
