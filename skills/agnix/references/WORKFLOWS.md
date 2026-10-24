# agnix reference workflows

This supplement is for configuration and automation requests. For ordinary linting, follow `../SKILL.md` without opening or changing any configuration.

## Choose scope and target

`agnix .` validates the current project, while `agnix path/to/file` validates a specific supported file. To select rules for one tool, use `--target <tool>` (for example, `claude-code`, `codex`, `cursor`, or `kiro`). `generic` does not mean "no validation"; it selects all applicable rules unless a project config says otherwise. Preserve an existing project's configured target unless the user asks to change it.

The `.agnix.toml` multi-tool setting can include values such as `claude-code`, `cursor`, `codex`, `kiro`, `github-copilot`, `cline`, `opencode`, `gemini-cli`, `amp`, `windsurf`, and `generic`; consult current upstream docs for the complete accepted set.

## Optional .agnix.toml examples

Do not create or change `.agnix.toml` without user intent. Example for a project with both Claude Code and Codex:

```toml
tools = ["claude-code", "codex"]

[files]
exclude = ["vendor/**", "generated/**"]

[rules.severity]
MCP-008 = "Error"
```

A narrowly scoped exception for a documented false positive:

```toml
[[overrides]]
paths = ["docs/agent-examples/*.md"]
disabled_rules = ["PE-005"]
```

Do not disable rules broadly to produce a green result. Prefer fixing problematic content or explaining the exception. Rule IDs can change between agnix versions; check `agnix explain <RULE-ID>` or the current rule catalog. Use `agnix schema` to output the current `.agnix.toml` JSON Schema.

## CI: GitHub Actions

The repository documents the following step within an existing GitHub Actions job:

```yaml
- name: Validate AI agent configurations
  uses: agent-sh/agnix@v0
  with:
    path: '.'
    target: 'generic'
    strict: 'true'
```

`@v0` is an upstream-documented major-version ref, not an immutable commit. For supply-chain-sensitive production workflows, pin actions to a reviewed full commit SHA and maintain update automation. Only add `strict: 'true'` if the user wants warnings to fail CI; otherwise omit it or set `'false'`.

For machine-readable checks, use `agnix --format json .` or `agnix --format sarif .`. agnix's Action documents `format: 'sarif'` and a `sarif-file` output for optional upload to code scanning. Do not claim successful upload or enforcement without checking workflow permissions and results.

## Pre-commit

The repository documents a self-installing Python-based pre-commit hook from release `v0.52.1` onward:

```yaml
repos:
  - repo: https://github.com/agent-sh/agnix
    rev: v0.52.1
    hooks:
      - id: agnix
```

The `agnix` hook validates in strict mode; `agnix-fix` is a separate, editing hook. Keep a reproducibly pinned release (or newer reviewed version) instead of automatically selecting `main`. Review the upstream pre-commit setup when upgrading.

## Useful diagnostic workflows

```bash
agnix .                               # Baseline
agnix --strict .                      # CI policy verification
agnix explain AS-001                  # Look up a specific rule ID
agnix --dry-run --show-fixes .         # Preview edits
agnix --fix-safe .                    # Apply safe fixes (requested only)
agnix .                               # Recheck
```

When results are requested for a dashboard, prefer `--format json`; for GitHub code scanning, `--format sarif`; for log annotations, `--format github`. Do not parse ANSI-colored human output when a structured format is available.

## Install the skill (not the agnix CLI)

Copy the folder containing `SKILL.md` and its `references/` directory to the skills location supported by the user's agent:

- Codex and other Agent Skills-compatible agents commonly use `.agents/skills/agnix/` in a project.
- Claude Code commonly uses `.claude/skills/agnix/` in a project.

The skill instructions are not executable software and do not install the `agnix` binary. The agent needs permission to execute the CLI in the target project.

## Upstream sources

- https://github.com/agent-sh/agnix
- https://github.com/agent-sh/agnix/blob/main/skills/agnix/SKILL.md (existing upstream skill)
- https://github.com/agent-sh/agnix/blob/main/plugin/skills/agnix/SKILL.md (Claude-specific variant)
- https://github.com/agent-sh/agnix/blob/main/docs/CONFIGURATION.md
- https://agent-sh.github.io/agnix/docs/installation
- https://agent-sh.github.io/agnix/docs/rules

Prepared against upstream project information retrieved 2026-10-22; verify version-sensitive options against the installed `agnix` version.
