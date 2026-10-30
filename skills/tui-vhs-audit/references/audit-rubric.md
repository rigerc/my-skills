# Visual audit rubric for TUIs

Examine screenshots at original resolution, not only on a resized contact sheet. Screenshots are visual evidence and do not by themselves establish full behavioral correctness.

## Test dimensions

**Layout and responsiveness** — truncated content, overflow beyond terminal boundaries, clipped labels, hard-coded dimensions, column misalignment, unusable narrow screens, unintended horizontal scrolling, broken borders, disappearing status/help lines and invisible cursor.

**Hierarchy and density** — clear app/page title, discernible active panel and selection, useful empty space, readable tables and lists, consistent padding, understandable nested menus, visually separated alerts, appropriately prominent key hints.

**Color and affordances** — sufficient *apparent* contrast across states and on small screens, clear focus and selection not conveyed solely by hue, distinguishable warnings/errors/success, legible disabled controls; explicit numeric contrast or colorblind compliance requires separate measurements and standards checks.

**Keyboard experience** — sensible starting focus, Up/Down/Tab order, Enter behavior, ability to leave overlays, visible focus changes, shortcut discoverability, reversible destructive actions. A screenshot cannot on its own establish full navigation behavior: pair evidence with the VHS actions and checks.

**State handling** — normal, empty, loading, error, oversized content, help, modal, confirm, success, validation errors, refresh and exit. Check only applicable states, never fabricate coverage.

**Robustness** — long UTF-8 labels, non-ASCII glyph fallback, Unicode width, wrapped descriptions, 80x24-style constraints, bright/dark themes if configurable, terminal resizes if supported by app and harness.

**Privacy and safety** — no keys, tokens, personal information or unintended internal paths appear in screenshots or tapes. Never upload unreviewed production captures.

## Findings and severity

- **Critical** — app's essential workflow unusable, or sensitive information exposed.
- **High** — primary workflow obstructed in a supported viewport; impossible to identify focus or complete a key action.
- **Medium** — significant clipping, overlap, unreadable important content, navigation confusion with workaround.
- **Low** — small alignment or spacing issue with limited functional impact.
- **Informational** — usability improvement or question not established as a defect.

A finding should be phrased in observable terms and backed by a directly linked screenshot and reproduction steps. Example: "At 720×420 px, the active selection label overlaps the status bar after Down twice" is evidence-ready; "UI looks bad" is not.

## Report completeness

An audit is complete only when a human or vision-capable assistant has examined every requested captured state and documented the outcome. If screenshots are missing, mark them **not captured**. If captured but not opened, mark them **captured, unreviewed**. If reviewed and no issue found, say **reviewed, no observed defect**, not "passed accessibility" or "bug-free".
