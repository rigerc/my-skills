# Rezi agent skill

A single, portable skill for AI coding assistants working with the **Rezi TypeScript terminal UI framework** (`@rezi-ui/core`, `@rezi-ui/node`). Built from the user-provided `Rezi-main.zip` repository snapshot.

## Contents

- `SKILL.md`: general Rezi skill, workflow selection, minimal app sample, and verification protocol.
- `references/workflows/`: the repository's 10 original task-specific Codex skill documents, retained as reference material.
- `references/docs/`: focused copies of the repository's original guides (API, UI patterns, testing, accessibility/focus, routing, etc.).
- `examples/hello-counter.ts`: known-good starter from the repository.

## Install

Extract this archive into your agent's skills folder so the path ends in `rezi/SKILL.md`.

For this repository's conventions, for example:

```bash
# From the parent directory of rezi-skill.zip:
unzip rezi-skill.zip -d .claude/skills/
# OR
unzip rezi-skill.zip -d .codex/skills/
```

For user-global installation, use the corresponding global skills folder supported by your agent.

## Example tasks

- "Using Rezi, build a terminal dashboard with counters and a sortable table."
- "Add a routed settings screen and a keyboard shortcut."
- "Debug why my Rezi modal does not restore focus."
- "Add a new `ui.*` widget to the Rezi monorepo and cover it with tests."

## Source and currency

Generated from the supplied **Rezi** repository snapshot (`@rezi-ui/core` **0.1.0-beta.3** at packaging). This skill does **not** include the entire framework or npm dependencies. Use the live local type definitions and repository docs as source of truth if they differ from the snapshots bundled here.

The bundled sources are part of the Rezi project, distributed under its **Apache-2.0** license (included as `LICENSE-rezi`).
