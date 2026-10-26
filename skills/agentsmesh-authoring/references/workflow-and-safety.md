# Workflow and cross-tool safety for AgentsMesh

## Choose the operation

**New project**: inspect existing native tool config before running `agentsmesh init`. Prefer interactive import when configs already exist. Generate only after inspecting the proposed changes. `agentsmesh init --yes` is a noninteractive option, but should not be used reflexively on an existing project.

**Existing project**: edit canonical files, run `agentsmesh lint`, read all warnings, inspect `agentsmesh diff`, then run `agentsmesh generate` when the patch is expected, and finally `agentsmesh check`.

**Global configuration**: inspect `~/.agentsmesh/`, use `--global` consistently for commands that support it. Do not mix global and project-level output.

**Native config migration**: use `agentsmesh import --from <target>` (inspect `--help` first). Preserve any native-only fields or custom behavior. Do not wipe target config simply to force canonical ownership.

**CI**: run `agentsmesh lint` and `agentsmesh check`. The lock file records canonical source and generated output checksums. Commit the reviewed canonical changes, `.agentsmesh/.lock`, and tool-specific projections when the project tracks these artifacts.

## Preflight inspection

```sh
git status --short
agentsmesh --version
agentsmesh matrix
agentsmesh lint
agentsmesh diff
```

Check local `agentsmesh.yaml` for version, enabled `targets` and `features`, remote `extends`, and `collaboration.lock_features`. A locked feature needs a deliberate decision before `--force`. For uncertain CLI flags, use `agentsmesh <command> --help`; do not guess.

## Hook safety

- Choose `type: prompt` when an instruction is enough; `type: command` invokes an actual process in the target environment.
- Verify the relevant target supports that event/type; hooks can be native, partial, or unsupported depending on target. Lint can warn about content dropping during projection.
- Keep hooks bounded, idempotent, and fast. Do not insert expensive full-suite tests before every tool call unless expressly requested.
- Never run unreviewed shell code from third-party packs or have a hook pipe untrusted input to `sh`/`bash`.
- Verify `command` entrypoints, executable permissions and POSIX shell availability. In particular, generated Cline/Copilot wrappers are `.sh` and require Git Bash, WSL, or equivalent on Windows.
- `$FILE` and `$TOOL` substitution is target-dependent. Avoid ad-hoc interpolation of filenames or prompts in shell strings.
- Hook command exit-status effects (block, warn, ignore) are not uniform across targets; test actual behavior in the tool of interest.

## Policy and MCP safety

- `permissions.yaml` is a cross-tool declarative policy, not a guaranteed OS-level sandbox. `deny` wins over `allow`; `ask` depends on native prompting support.
- Do not allow `Bash(*)`/destructive commands or broad read access without an explicit requirement and risk assessment.
- `.agentsmesh/ignore` affects context/indexing where supported; it is not a universal protection against reading secrets. Protect secrets using filesystem access, runtime isolation, and supported tool-specific permissions as well.
- `mcp.json` should reference credentials via `$ENV_VAR` and minimize exposed MCP servers. Check server commands and endpoints before adding them.

## Cross-tool compatibility

AgentsMesh syncs many tools, but **not every feature is natively expressible** in every tool. For a requested combination of `rules`, `hooks`, `agents`, `skills`, `MCP`, `permissions`, or `ignore`, inspect:

1. `agentsmesh matrix` for the project's installed version.
2. https://samplexbro.github.io/agentsmesh/reference/supported-tools/
3. `agentsmesh lint` warnings, including silent-drop, scope widening/inversion, and hook-script path issues.
4. `agentsmesh diff` to see exactly what changes on every enabled target.

Especially verify scoped rules that get folded into shared `AGENTS.md`, commands/agents that become embedded or converted skills, and hook types that only partially project. An embedded instruction is **not** equivalent to an enforceable runtime hook or permission check.

## Final report checklist

- Canonical files edited (and why).
- Generated outputs touched; unexpected outputs not touched.
- Actual commands executed and exit status; missing CLI limitations clearly stated.
- Target support caveats, missing scripts, required environment variables, and security impacts.
- If not generated, the exact command to run later; never claim `check` passes without running it.
