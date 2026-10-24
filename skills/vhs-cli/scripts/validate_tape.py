#!/usr/bin/env python3
"""Conservative VHS tape preflight linter; not a replacement for the VHS parser."""
import argparse
import json
import re
import sys
from pathlib import Path

SET_RE = re.compile(r'^Set\s+([A-Za-z]+)(?:\s+|$)')
DECL_RE = re.compile(r'^(Output|Require|Set|Env|Source)\b')
ACTION_RE = re.compile(r'^(Type(?:@\S+)?|Enter|Sleep|Wait(?:\+\w+)?(?:@\S+)?|Hide|Show|Screenshot|Copy|Paste|(?:Ctrl|Alt|Shift)\+\S+|Backspace|Tab|Space|Up|Down|Left|Right|PageUp|PageDown|ScrollUp|ScrollDown)\b')
DANGEROUS_RE = re.compile(r'\b(?:sudo\b|rm\s+-[rfRF]+\b|mkfs\b|curl\b[^\n]*\|\s*(?:sh|bash)\b|git\s+push\s+--force\b)')
SECRET_RE = re.compile(r'(?i)(?:api[_-]?key|secret|password|token)\s*[=:]\s*["\']?[^\s"\']{6,}')


def lint(path: Path, seen=None):
    seen = set() if seen is None else seen
    problems = []
    def add(level, line, message): problems.append({'level': level, 'line': line, 'message': message, 'file': str(path)})
    if not path.is_file():
        add('error', 0, 'Tape file does not exist')
        return problems
    resolved = path.resolve()
    if resolved in seen:
        add('warning', 0, 'Source cycle or repeated source; skipping recursive inspection')
        return problems
    seen.add(resolved)
    outputs, dims = [], set()
    interactive = False
    hidden = False
    source_paths = []
    for n, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        s = raw.strip()
        if not s or s.startswith('#'): continue
        m = SET_RE.match(s)
        if s.startswith('Output '):
            val = s[7:].strip().strip('"\'')
            if not val: add('error', n, 'Output requires a path')
            else: outputs.append(val)
        if m:
            setting = m.group(1)
            if interactive and setting != 'TypingSpeed':
                add('warning', n, f'Set {setting} appears after interaction and may be ignored')
            if setting in ('Width', 'Columns', 'Height', 'Rows'): dims.add(setting)
        if s.startswith('Require ') and interactive:
            add('warning', n, 'Require appears after interaction; move it to the header')
        if s == 'Hide':
            if hidden: add('warning', n, 'Repeated Hide without Show')
            hidden = True
        if s == 'Show':
            if not hidden: add('warning', n, 'Show without preceding Hide')
            hidden = False
        if s.startswith('Source '):
            value = s[7:].strip().strip('"\'')
            if value: source_paths.append((n, value))
        if SECRET_RE.search(s): add('warning', n, 'Possible embedded credential: use dummy fixtures; never record secrets')
        if s.startswith('Type') and DANGEROUS_RE.search(s):
            add('warning', n, 'Potentially destructive or remote-execution shell command: review before running')
        if ACTION_RE.match(s) and not s.startswith('Screenshot') and not s.startswith('Sleep') and not s.startswith('Wait') and not s.startswith('Hide') and not s.startswith('Show'):
            interactive = True
        if not DECL_RE.match(s) and not ACTION_RE.match(s) and not re.match(r'^\w+@\S+\b', s):
            add('warning', n, 'Unrecognized instruction (check against local `vhs manual`)')
    if not outputs: add('error', 0, 'No Output directive found (required for this workflow)')
    if 'Width' in dims and 'Columns' in dims: add('error', 0, 'Set Width conflicts with Set Columns')
    if 'Height' in dims and 'Rows' in dims: add('error', 0, 'Set Height conflicts with Set Rows')
    if hidden: add('warning', 0, 'Tape finishes while Hide is active; recording may be blank')
    for n, target in source_paths:
        if target.startswith(('http:', 'https:')):
            add('warning', n, 'Remote Source not inspected')
        elif '$' not in target:
            child = (path.parent / target)
            if not child.exists(): add('warning', n, f'Sourced tape not found relative to tape: {target}')
            else: problems.extend(lint(child, seen))
    return problems


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tape', type=Path)
    p.add_argument('--json', action='store_true')
    p.add_argument('--strict', action='store_true', help='Treat warnings as failures')
    args = p.parse_args()
    issues = lint(args.tape)
    if args.json: print(json.dumps({'tape': str(args.tape), 'issues': issues, 'valid': not any(i['level']=='error' for i in issues)}, indent=2))
    else:
        for i in issues: print(f"{i['file']}:{i['line']}: {i['level']}: {i['message']}")
        print(f'Preflight: {sum(i["level"]=="error" for i in issues)} error(s), {sum(i["level"]=="warning" for i in issues)} warning(s)')
    return 1 if any(i['level']=='error' or (args.strict and i['level']=='warning') for i in issues) else 0

if __name__ == '__main__': sys.exit(main())
