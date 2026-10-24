#!/usr/bin/env python3
"""Run simple preflight or expanded VHS render-and-inspect workflow."""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from validate_tape import lint
from inspect_render import inspect


def outputs_in(tape):
    outputs=[]
    for line in tape.read_text(encoding='utf-8').splitlines():
        match=re.match(r'^\s*Output\s+(.+?)\s*$',line)
        if match:
            name=match.group(1).strip().strip('"\'')
            outputs.append((tape.parent / name).resolve())
    return outputs


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['simple','expanded'])
    p.add_argument('tape',type=Path)
    p.add_argument('--strict',action='store_true')
    p.add_argument('--contact-sheet',type=Path)
    args=p.parse_args()
    issues=lint(args.tape)
    for issue in issues: print(f"{issue['file']}:{issue['line']} {issue['level']}: {issue['message']}")
    if any(i['level']=='error' or (args.strict and i['level']=='warning') for i in issues):
        print('FAILED: tape preflight'); return 1
    print('PASS: tape preflight (heuristic, not VHS parser)')
    if args.mode=='simple':
        print('COMPLETE: simple validation only; no recording was rendered')
        return 0
    for executable in ('vhs','ttyd','ffmpeg'):
        if not shutil.which(executable):
            print(f'BLOCKED: {executable} missing from PATH; nothing rendered')
            return 2
    outputs=outputs_in(args.tape)
    if not outputs:
        print('BLOCKED: no outputs declared')
        return 2
    # VHS can write relative outputs according to its working directory.
    # Run with cwd=tape.parent, using a basename, so output location is predictable.
    proc=subprocess.run(['vhs',args.tape.name],cwd=args.tape.resolve().parent)
    if proc.returncode:
        print(f'FAILED: VHS exited {proc.returncode}')
        return proc.returncode
    failed=False
    for output in outputs:
        sheet=args.contact_sheet if args.contact_sheet and output.suffix.lower() in ('.gif','.png') and len(outputs)==1 else None
        result=inspect(output,sheet)
        print(f'{"PASS" if result["ok"] else "REVIEW"}: {output}: {result["metadata"]}')
        for problem in result['issues']: print('  - '+problem)
        failed |= not result['ok']
    print('Inspection metadata cannot prove visual quality: inspect sampled frames manually for clipping, secrets, and timing.')
    return 3 if failed else 0

if __name__=='__main__':sys.exit(main())
