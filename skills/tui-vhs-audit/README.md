# tui-vhs-audit skill

A portable agent skill that extends a VHS recording workflow into a reproducible TUI visual audit: plan states, capture screenshots, inventory PNGs, review visual defects and report findings with evidence.

## Quick start

```sh
# Run from this skill's root directory.
python3 scripts/audit_tui.py prepare examples/demo-plan.json --out /tmp/tui-audit

# Review the generated audit.tape files, then run with VHS installed:
python3 scripts/audit_tui.py run --out /tmp/tui-audit --yes

# Create contact sheet and report scaffold:
python3 scripts/audit_tui.py inspect --out /tmp/tui-audit
```

Modify `examples/demo-plan.json` to launch your own application in a fixture environment. The example uses `examples/demo_tui.py` so it can run without external application dependencies on Unix-like systems. The tool does not automatically evaluate screenshots as visually correct: inspect the PNGs and complete `audit-report.md` using `references/audit-rubric.md`.

**Dependencies:** Python 3.10+; VHS, ttyd and ffmpeg for rendering; Pillow optionally for contact sheets. No pip packages needed for plan generation or basic screenshot inventory.

A second `inspect` preserves existing `audit-report.md` and writes `audit-report.new.md`; pass `--overwrite-report` to replace it intentionally.

An authorized `run` clears the whole batch's previous screenshots, recordings, and generated inventory before capturing again, so skipped runs cannot retain stale evidence. Edited reports are preserved; inspect the new captures and update the report after each rerun.

**Testing:** `python3 -m unittest discover -s tests -v`
