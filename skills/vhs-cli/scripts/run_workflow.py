#!/usr/bin/env python3
"""Run simple preflight or expanded VHS render-and-inspect workflow."""
import argparse
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from validate_tape import lint
from inspect_render import inspect


def artifacts_in(tape, seen=None, render_dir=None):
    """Collect Output and Screenshot targets, including local Source tapes."""
    tape = tape.resolve()
    render_dir = render_dir or tape.parent
    seen = set() if seen is None else seen
    if tape in seen:
        return []
    seen.add(tape)
    paths = []
    for line_no, line in enumerate(tape.read_text(encoding='utf-8').splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            raise ValueError(f'{tape}:{line_no}: invalid directive: {exc}') from exc
        if not parts or parts[0] not in ('Output', 'Screenshot', 'Source'):
            continue
        if len(parts) != 2 or not parts[1]:
            raise ValueError(f'{tape}:{line_no}: {parts[0]} needs exactly one path')
        name, value = parts
        if name == 'Source':
            if value.startswith(('http:', 'https:')) or '$' in value:
                raise ValueError(f'{tape}:{line_no}: cannot inspect dynamic or remote Source: {value}')
            source = (tape.parent / value).resolve()
            if not source.is_file():
                raise ValueError(f'{tape}:{line_no}: Source file not found: {source}')
            paths.extend(artifacts_in(source, seen, render_dir))
        else:
            paths.append((render_dir / value).resolve())
    # Two directives may name the same destination: inspect it once.
    return list(dict.fromkeys(paths))


def outputs_in(tape):
    """Compatibility helper: includes declared screenshots as well as outputs."""
    return artifacts_in(tape)


def fingerprint(path):
    """Record prior artifacts without deleting potentially user-owned files."""
    if not path.exists():
        return None
    if path.is_dir():
        return tuple(
            (str(p.relative_to(path)), p.stat().st_size, p.stat().st_mtime_ns)
            for p in sorted(path.glob('*.png')) if p.is_file()
        )
    st = path.stat()
    return st.st_size, st.st_mtime_ns


def git_root(directory):
    proc = subprocess.run(
        ['git', '-c', 'core.quotePath=false', '-C', str(directory), 'rev-parse', '--show-toplevel'],
        text=True, capture_output=True, check=False,
    )
    if proc.returncode or not proc.stdout.strip():
        raise ValueError('--audit requires a Git repository (run from inside the target repository)')
    return Path(proc.stdout.strip()).resolve()


def ensure_ignored(root):
    path = root / '.gitignore'
    if path.is_symlink() or (root / '.tui-audit').is_symlink():
        raise ValueError('Refusing symlinked .gitignore or .tui-audit directory')
    existing = path.read_text(encoding='utf-8') if path.exists() else ''
    if '/.tui-audit/' not in existing.splitlines():
        with path.open('a', encoding='utf-8') as f:
            if existing and not existing.endswith('\n'):
                f.write('\n')
            f.write('/.tui-audit/\n')


def archive_artifact(path, root, destination):
    """Relocate only generated files, never arbitrary files inside frames directories."""
    if path.is_relative_to(root / '.tui-audit'):
        return path
    if not path.is_relative_to(root):
        raise ValueError(f'Cannot archive artifact outside Git repository: {path}')
    target = destination / path.relative_to(root)
    if path.is_dir():
        target.mkdir(parents=True, exist_ok=True)
        for frame in path.glob('*.png'):
            shutil.move(str(frame), str(target / frame.name))
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    path.replace(target)
    return target


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['simple', 'expanded'])
    p.add_argument('tape', type=Path)
    p.add_argument('--strict', action='store_true')
    p.add_argument('--contact-sheet', type=Path)
    p.add_argument('--audit', action='store_true',
                   help='Move expanded render artifacts into the Git-ignored <repo>/.tui-audit/<tape>/')
    args = p.parse_args()
    issues = lint(args.tape)
    for issue in issues:
        print(f"{issue['file']}:{issue['line']} {issue['level']}: {issue['message']}")
    if any(i['level'] == 'error' or (args.strict and i['level'] == 'warning') for i in issues):
        print('FAILED: tape preflight')
        return 1
    print('PASS: tape preflight (heuristic, not VHS parser)')
    if args.mode == 'simple':
        print('COMPLETE: simple validation only; no recording was rendered')
        return 0
    for executable in ('vhs', 'ttyd', 'ffmpeg'):
        if not shutil.which(executable):
            print(f'BLOCKED: {executable} missing from PATH; nothing rendered')
            return 2
    try:
        tape = args.tape.resolve()
        artifacts = artifacts_in(tape)
        if not artifacts:
            raise ValueError('No Output or Screenshot directives declared')
        root = git_root(tape.parent) if args.audit else None
        if root is not None:
            # Do not invoke VHS if any declared artifact would escape the repo.
            for artifact in artifacts:
                if not artifact.is_relative_to(root):
                    raise ValueError(f'Audit artifact escapes repository: {artifact}')
            ensure_ignored(root)
        before = {path: fingerprint(path) for path in artifacts}
        proc = subprocess.run(['vhs', tape.name], cwd=tape.parent, check=False)
    except (OSError, ValueError) as exc:
        print(f'BLOCKED: {exc}')
        return 2
    if proc.returncode:
        print(f'FAILED: VHS exited {proc.returncode}')
        return proc.returncode

    failed = False
    for artifact in artifacts:
        sheet = (args.contact_sheet if args.contact_sheet and
                 artifact.suffix.lower() in ('.gif', '.png') and len(artifacts) == 1 else None)
        result = inspect(artifact, sheet)
        if fingerprint(artifact) == before[artifact]:
            result['issues'].append('Stale artifact: VHS did not update this output')
            result['ok'] = False
        print(f'{"PASS" if result["ok"] else "REVIEW"}: {artifact}: {result["metadata"]}')
        for problem in result['issues']:
            print('  - ' + problem)
        failed |= not result['ok']
    if failed:
        print('FAILED: incomplete, invalid, or stale recording artifacts')
        return 3

    if root is not None:
        destination = root / '.tui-audit' / tape.stem
        for artifact in artifacts:
            archived = archive_artifact(artifact, root, destination)
            print(f'AUDIT: {archived}')
    print('Inspection metadata cannot prove visual quality: inspect sampled frames manually for clipping, secrets, and timing.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
