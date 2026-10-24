# README Section Guidance

Per-section rules for drafting a README. Companion to `SKILL.md`; read the
entries for the sections you are writing.

## Section Guidance

**Title + One-liner**

- Must pass the 3-second test: a stranger should know what the project does
- Frame around the problem solved, not the implementation details
- Prefer concrete value over architecture jargon

**Badges**

- Include only badges that carry useful meaning
- Keep one consistent badge style
- Minimum useful set is usually license + language/runtime + package/store status
- For research projects, paper and venue badges may matter
- For extension or consumer products, compatibility or store links may matter
- Never add decorative badge clutter

**Installation**

- Must be copy-paste ready
- Extract actual commands from package/build/config files
- Put the shortest path first
- Separate multiple installation methods with clear headings
- Include prerequisites only when they are non-obvious or blocking

**Usage / Quick Start**

- Use real, runnable examples from source, tests, or examples when possible
- Show input and output when that increases trust
- Start with the smallest successful example
- Do not dump the entire API surface into README

For distribution posture, public API/import paths, and config parity, follow
`{baseDir}/references/repo-integrity.md`.

**Highlights / Features**

- Demonstrate, do not merely list
- Limit to 3-7 highlights
- Make each highlight answer "why should this reader care?"

**Terminal Showcase Assets**

Applies only when the Terminal Showcase temperament is selected. Full rules,
format handling, and layout snippets are in
`{baseDir}/references/style-guide.md` (section 5).

- **Logo is the header.** It replaces the text H1 as the centered title. Keep
  the project name in the image `alt` text. If the logo is icon-only, put the
  text H1 directly under it. If no logo exists, use a plain H1 and recommend
  one; never draw or invent a logo.
- **Exactly one screen recording**, placed right after the one-liner, badges,
  and nav links, before Install. If the repo has several, pick one by the
  selection order in the style guide and tell the user which others were left
  out.
- **Screenshots only if present.** Include real screenshots found in the repo
  in a short section after Usage. If there are none, omit the section with no
  placeholder.
- Install and first-run commands stay as copyable text; the recording supports
  them, it does not replace them.

**Architecture / How It Works**

- Include only if architecture is a selling point or required orientation
- Keep it high-level and route detail to deeper docs

**Visuals and Visual Hierarchy**

Visual hierarchy separates a polished README from a plain one. Use these
elements to create scannable, professional pages.

Diagrams — generate directly in Mermaid (GitHub renders natively):

- Flowchart for architecture overviews and data flows
- Sequence diagram for API or interaction flows
- Class or ER diagram for data models
- Mindmap for feature overviews or concept maps
- Use ASCII diagrams only for very simple structures (five or fewer boxes)

Badges — generate shields.io badge URLs directly:

- Pick one consistent style per README (`flat-square` for utilities,
  `for-the-badge` for products and research)
- Include only badges that carry real information: CI, version, license,
  downloads, or platform compatibility
- Match badge colors to project branding when possible
- See `{baseDir}/references/style-guide.md` for per-temperament badge
  strategies

HTML layout — use allowed GitHub HTML for visual structure:

- `<div align="center">` for centered headers and hero sections
- `<picture>` with `<source media="(prefers-color-scheme: ...)">` for
  dark/light mode images
- `<details>` and `<summary>` for collapsible advanced content
- HTML tables when markdown tables are insufficient

GitHub Alerts — use for important callouts:

- `> [!NOTE]` for supplementary information
- `> [!TIP]` for helpful suggestions
- `> [!IMPORTANT]` for critical setup information
- `> [!WARNING]` for potential pitfalls
- `> [!CAUTION]` for destructive actions

Never reference or fake a visual asset that does not exist. Embed only files
that are in the repo (or URLs the user supplied), and do not mock up terminal
screenshots as images or code blocks presented as screenshots.

When a visual asset would add clear value but the agent cannot generate it
directly (product screenshot, CLI GIF, logo, polished exported diagram),
recommend it to the user with:

1. what it should show
2. where it should be placed in the README
3. recommended format and dimensions
4. a tool suggestion appropriate to the user's likely skill level

**AI / Automation Section**

Only add an AI/automation-oriented section when it is materially useful:

- the project is AI-native, agent-facing, or automation-heavy
- the repo already ships machine-readable assets such as `AGENTS.md`,
  `CLAUDE.md`, or `llms.txt`
- the target audience includes AI agents or tool integrators

Even then, keep it below the main install and usage path for human readers.

**Contributing / Community**

- Keep contributing guidance brief in README
- Link to `CONTRIBUTING.md` for detail
- Include community channels only if they exist and matter
