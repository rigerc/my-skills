# AgentsMesh canonical file formats

Canonical files are stored under `.agentsmesh/`; `agentsmesh.yaml` is at project root. Use the actual installed AgentsMesh version as the ultimate validator. These concise patterns are based on the project's published canonical-config documentation.

## Root rule: `rules/_root.md`

```md
---
root: true
---
# Project instructions

- Keep dependencies and lint scripts consistent with this repository.
```

The filename is special and mandatory. It is always applied; do not use path globs to try to disable it.

## Additional rule: `rules/<name>.md`

```md
---
description: TypeScript source conventions
globs: ["src/**/*.ts", "src/**/*.tsx"]
targets: [claude-code, cursor]
---

- Keep exported public functions typed.
- Update adjacent tests when changing behavior.
```

Rule frontmatter: `root?: boolean`, `description?: string`, `targets?: string[]`, `globs?: string[]`, `trigger?: always_on|model_decision|glob|manual` (Windsurf-oriented), `codex_emit?: advisory|execution`, `codex_instruction?: override`. Claude emits `globs` as `paths`. Target-scoped rules can widen when projected into a shared AGENTS.md.

## Hooks: `hooks.yaml`

```yaml
PreToolUse:
  - matcher: "Bash"
    type: prompt
    prompt: "Review the proposed command for destructive or secret-leaking behavior."
PostToolUse:
  - matcher: "Edit|Write"
    type: command
    command: "npm run lint --if-present"
    timeout: 60
```

Supported event names: `PreToolUse`, `PostToolUse`, `Notification`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`. Every hook needs `matcher` and `type`; command hooks require `command`, prompt hooks require `prompt`. Seconds for timeout. Only use `$FILE` and `$TOOL` when supported by the specific destination and event. Scripts referenced in hook commands are not automatically copied for most targets.

## Permissions: `permissions.yaml`

```yaml
allow:
  - Read
  - Grep
  - Glob
deny:
  - Read(.env)
  - Read(.env.*)
  - Bash(rm -rf:*)
ask:
  - Bash(git push:*)
```

`deny` takes priority over `allow`. `ask` is only enforced by target tools supporting approval prompts; permission patterns (e.g. `Bash(cmd:*)`) are not universal shell policies.

## MCP servers: `mcp.json`

```json
{
  "mcpServers": {
    "example-stdio": {
      "type": "stdio",
      "command": "node",
      "args": ["./scripts/mcp-server.js"],
      "env": { "API_TOKEN": "$API_TOKEN" }
    }
  }
}
```

The command above is a placeholder and **requires that the referenced server exists**. An HTTP alternative uses `"type": "url"` and `"url": "https://..."`, optionally `"headers"`. No embedded plaintext secrets; use `$VAR_NAME` references.

## Commands: `commands/<name>.md`

```md
---
description: Review current changes
allowed-tools:
  - Read
  - Grep
  - Bash(git diff)
---

Review the current diff for correctness, tests, and regressions. Report findings by severity.
```

Optional `outputStyle: true`. Filename supplies command name.

## Agents: `agents/<name>.md`

```md
---
name: reviewer
description: Read-only code reviewer
tools: [Read, Grep, Glob]
maxTurns: 12
---

Review changes and report actionable findings. Do not edit files.
```

Optional `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `skills`, `memory`, `outputStyle`. Scope and translation differ by target. Agent hooks use the same event-entry shape as project hooks.

## Skills: `skills/<name>/SKILL.md`

```md
---
description: Review authentication logic for regressions
---

Inspect login and session validation changes. Use [checklist](./checklist.md).
```

Supporting files live within the skill directory, are copied on projection, and must be referenced with relative `./` paths.

## Ignore: `ignore`

```gitignore
node_modules/
dist/
.env
.env.*
*.pem
```

Gitignore-style syntax; distinct from `.gitignore` and not a hard security boundary.

## Project config: `agentsmesh.yaml`

```yaml
version: 1
targets:
  - claude-code
  - cursor
  - copilot
# Omit features to enable all features.
```

Optional: `features: [rules, commands, agents, skills, mcp, hooks, ignore, permissions]`, `extends`, `overrides`, `collaboration`, `conversions`. A specified feature list excludes all omitted feature categories; override features must be a subset of top-level features.

## Links to detailed specifications

- https://samplexbro.github.io/agentsmesh/configuration/agentsmesh-yaml/
- https://samplexbro.github.io/agentsmesh/canonical-config/rules/
- https://samplexbro.github.io/agentsmesh/canonical-config/hooks/
- https://samplexbro.github.io/agentsmesh/canonical-config/commands/
- https://samplexbro.github.io/agentsmesh/canonical-config/agents/
- https://samplexbro.github.io/agentsmesh/canonical-config/skills/
- https://samplexbro.github.io/agentsmesh/canonical-config/mcp-servers/
- https://samplexbro.github.io/agentsmesh/canonical-config/permissions/
- https://samplexbro.github.io/agentsmesh/canonical-config/ignore-patterns/
