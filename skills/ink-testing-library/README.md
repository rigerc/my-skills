# Agent Skill: ink-testing-library

Portable agent instructions for adding and troubleshooting tests of Ink-based React CLI components.

**Library source:** https://github.com/vadimdemedes/ink-testing-library

## Contents

- `SKILL.md` — skill metadata and operational workflow
- `references/api.md` — source-checked v4 API reference
- `references/recipes.md` — assertions, input, async tests, debugging
- `examples/counter.test.tsx` — adaptable Vitest example

## Install the skill

Copy this **entire `ink-testing-library/` directory** to the skills location supported by your coding agent, for example:

```bash
mkdir -p .agents/skills
cp -R ink-testing-library .agents/skills/
```

For agent products using another skills path, follow that product's configuration. The skill is not an npm package and does not install the library.

In the tested project, install the library if needed:

```bash
npm install --save-dev ink-testing-library
```

A runnable test also needs React, Ink, and the project's configured test runner/JSX transform. Adapt the `examples/` code to the installed versions and project conventions.

## Example tasks for the agent

- “Add tests for the confirmation prompt in this Ink CLI.”
- “Use ink-testing-library to simulate the `q` key and assert the exit message.”
- “Fix flaky tests caused by asynchronous Ink component output.”
- “Verify that a spinner transitions to success text.”

## Provenance

Guidance built from the upstream README, `source/index.ts`, and `package.json` (reviewed against upstream version 4.0.0), plus the Agent Skills specification at https://agentskills.io. This skill is independent documentation, not an official upstream release.
