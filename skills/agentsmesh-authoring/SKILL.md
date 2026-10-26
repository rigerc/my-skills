---
name: agentsmesh-authoring
description: Author, edit, migrate, troubleshoot, and validate AgentsMesh canonical configuration (.agentsmesh rules, hooks, commands, agents, skills, MCP servers, permissions, ignore, lessons, and agentsmesh.yaml) for multiple AI coding tools.
---

# AgentsMesh configuration authoring

Use this skill when someone asks to create or change **AgentsMesh** configuration, including rules, hooks, permissions, MCP servers, commands, subagents, skills, ignore patterns, project targets, or their generated-tool projections. This skill is for the [`sampleXbro/agentsmesh`](https://github.com/sampleXbro/agentsmesh) CLI, **not** for hand-authoring one tool's unrelated native settings.

## Operating contract

- Treat `agentsmesh.yaml` plus `.agentsmesh/` as the canonical source. Unless explicitly asked to troubleshoot a generated artifact, edit canonical files rather than `CLAUDE.md`, `AGENTS.md`, `.cursor/`, `.claude/`, etc. A generation pass owns its outputs and may replace direct edits.
- Make the **smallest change** that achieves the requested behavior. Preserve existing rules, event handlers, inheritance, local preferences, permissions, scripts, and comments where possible. Do not replace whole files to add one entry.
- Read the applicable reference before writing: [file formats](./references/file-formats.md), [workflow and safety](./references/workflow-and-safety.md). Consult [examples](./examples/) as starting points, not unconditional defaults.
- Do not invent target IDs, hook events, YAML keys, implicit hook variables, tool permissions, or unsupported cross-tool behavior. Verify the installed CLI's capabilities with `agentsmesh matrix`, `agentsmesh <command> --help`, official docs, and/or the project's pinned version.
- Never place real tokens, passwords, or credential values in tracked files. For MCP credentials reference environment variables (`$TOKEN_NAME`); check permissions and hook scripts for privilege or exfiltration risks.

## 1. Inspect before changing anything

1. Determine whether the request concerns project scope (`./agentsmesh.yaml` and `./.agentsmesh/`) or global scope (`~/.agentsmesh/`). Project scope is the default.
2. Inspect `agentsmesh.yaml`, `agentsmesh.local.yaml` if present (do not commit machine-specific secrets), `.agentsmesh/` and existing generated files. Inspect `git status` to protect uncommitted work; **do not erase changes**.
3. Identify configured `targets`, optional `features`, per-target `overrides`, remote `extends`, `collaboration` locks, and the tool version. Omitted `features` means all are enabled; per-target overrides can only narrow enabled features.
4. If AgentsMesh is not initialized, explain which config must be initialized and adopt existing configurations using its `init`/`import` workflow rather than overwriting native config. Do not run a potentially overwriting initialization without verifying existing files and intent.
5. For a target-specific requirement, examine `agentsmesh matrix` or the [support matrix](https://samplexbro.github.io/agentsmesh/reference/supported-tools/) first. Native, embedded, partial and unsupported capabilities differ by feature and target. Warn when exact activation or hook semantics cannot be preserved.

## 2. Route the request to the right canonical file

| Intent | Canonical file |
| --- | --- |
| Always-on project instructions | `.agentsmesh/rules/_root.md` |
| Task-specific or path-scoped guidance | `.agentsmesh/rules/<kebab-name>.md` |
| Event-driven shell command or prompt | `.agentsmesh/hooks.yaml` |
| Tool allow/deny/approval policy | `.agentsmesh/permissions.yaml` |
| Reusable slash prompt | `.agentsmesh/commands/<kebab-name>.md` |
| Specialist subagent | `.agentsmesh/agents/<kebab-name>.md` |
| Reusable agent capability and supporting files | `.agentsmesh/skills/<kebab-name>/SKILL.md` |
| MCP server definitions | `.agentsmesh/mcp.json` |
| Files excluded from AI context | `.agentsmesh/ignore` |
| Targets, features, overrides, extends, collaboration | `agentsmesh.yaml` |
| Shared failure lessons | `agentsmesh lessons ...` CLI; do not invent the internal lessons JSON schema |

If a task involves multiple features, update each canonical file independently. Do not conflate *rules* (instructions) with *hooks* (runtime execution), or *permissions* (access policy) with *ignore* (context exclusion).

## 3. Author correctly

### Rules

- `_root.md` is required and always on; keep its `root: true` frontmatter. Put narrow instructions into separate kebab-case `.md` files instead of inflating the root rule.
- Optional rule frontmatter: `description`, `targets` (target IDs), `globs` (gitignore-style patterns), `trigger` (`always_on`, `model_decision`, `glob`, `manual`), `codex_emit` (`advisory` or `execution`), `codex_instruction` (`override`). Add fields only when necessary.
- A `targets:` filter does not guarantee strict isolation on tools sharing a single root `AGENTS.md`; lint may report widened scope. Explain this when it matters.
- Express operational, testable instructions. Avoid vague mandates, conflicting rules, or hardcoded machine-specific paths.

### Hooks

- Place project hooks in `.agentsmesh/hooks.yaml`, grouped by supported event: `PreToolUse`, `PostToolUse`, `Notification`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`.
- Each entry has `matcher` (quoted string) and `type: command` **with `command`**, or `type: prompt` **with `prompt`**. Optional `timeout` is in seconds. For example, see [hooks.yaml](./examples/hooks.yaml).
- The documented `matcher: "*"` covers all tools/events; narrower patterns such as `Edit|Write` match selected tools. Validate against target semantics.
- `$FILE` and `$TOOL` are documented for certain Pre/Post tool command hooks only; support varies. Never assume other variables such as `$NOTIFICATION` exist across targets. Avoid interpolating untrusted data directly into shell commands.
- Prefer bounded, non-destructive commands; verify a referenced script exists, is executable where needed, and resolves relative to the actual hook working directory. Generated Cline/Copilot script wrappers require a POSIX shell on Windows. Do not assume hook command failures have consistent blocking semantics across all tools.

### All other files

- Commands: Markdown with `description` and optional `allowed-tools`; filename becomes the command identifier.
- Agents: Markdown frontmatter with `name` and `description`, plus optional `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `mcpServers`, `hooks`, `skills`, `memory`, `outputStyle`. `disallowedTools` wins over `tools`. Do not assume model aliases or permission modes work equivalently for every target.
- Skills: `.agentsmesh/skills/<name>/SKILL.md` with a short `description` in YAML frontmatter; include supporting files alongside it and link to them with paths beginning `./` within the skill directory.
- MCP: `.agentsmesh/mcp.json` has an `mcpServers` object. Each entry is `type: "stdio"` with `command`, optional `args`/`env`, or `type: "url"` with `url` and optional `headers`. Use environment-variable references for secrets, not literal values.
- Permissions: `.agentsmesh/permissions.yaml` has `allow`, `deny`, `ask` arrays; `deny` wins. Approval prompts and operation patterns are target dependent. Avoid broad allows such as unrestricted shell access unless requested and assessed.
- Ignore: `.agentsmesh/ignore` is gitignore-style syntax, **separate from `.gitignore`**. Do not represent it as a substitute for permission enforcement.
- Main config: `version: 1`, `targets: [...]`; optional `features`, `extends`, `overrides`, `collaboration`, `conversions`. Never assume a feature exists on a target just because it is enabled in YAML.

## 4. Validate, preview, then generate

From the project root, when CLI is installed:

```sh
agentsmesh lint           # validate canonical syntax and target constraints; inspect warnings
agentsmesh diff           # inspect exactly what generation would modify/delete
agentsmesh generate --dry-run  # optional path/status preview; no writes
agentsmesh generate       # only when approved/appropriate and diff is safe
agentsmesh check          # verify canonical source AND generated output drift
```

- If changing a single target, `lint --targets <csv>` and `diff --targets <csv>` are available; prefer a **full generate** before final project-wide `check` when canonical sources affect other targets.
- Stop and report unexpected deletions, ownership conflicts, locked features, silently dropped features, widened rule scopes, hook-script path warnings, malformed files, or a failed command. Do not automatically use `--force` to bypass locks.
- If only requested to **draft** a file, provide it without running `generate`. If CLI is unavailable, do not claim `lint` or `check` passed; perform basic YAML/JSON checks if possible, and say cross-target validation remains unverified.
- Include `.agentsmesh/.lock` and the generated tool outputs in the reviewed changes when your repository tracks them. Preserve unrelated changes.

## 5. Deliver the result

State: (1) canonical paths created/edited, (2) why each belongs there, (3) which targets and limitations apply, (4) exact validation commands run and their results, and (5) any follow-up needed (e.g. environment variables or an executable hook script). If an action is unsupported by a requested target, describe the limitation rather than silently substituting a non-equivalent behavior.

## Official references

- [AgentsMesh repository](https://github.com/sampleXbro/agentsmesh)
- [Canonical config](https://samplexbro.github.io/agentsmesh/canonical-config/)
- [Rules](https://samplexbro.github.io/agentsmesh/canonical-config/rules/)
- [Hooks](https://samplexbro.github.io/agentsmesh/canonical-config/hooks/)
- [Supported tool matrix](https://samplexbro.github.io/agentsmesh/reference/supported-tools/)
- [CLI lint](https://samplexbro.github.io/agentsmesh/cli/lint/)
- [CLI diff](https://samplexbro.github.io/agentsmesh/cli/diff/)
- [CLI check](https://samplexbro.github.io/agentsmesh/cli/check/)
