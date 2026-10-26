# t3-delegate

An Agent Skills package for scoped T3 Code child delegation, verified completion and deliberate integration. The native MCP workflow preserves requested providers, models and options. Missing child tools produce a reported limitation, not an automatic top-level-thread fallback.

## Install

Copy the package into the project's agent skills:

```sh
mkdir -p .agents/skills
cp -R t3-delegate .agents/skills/
```

For Claude Code, use the configured Claude skills directory instead. Installation does not connect T3 or grant orchestration permissions.

Start with [SKILL.md](SKILL.md). Native delegation requires callable T3 MCP tools and an authorized parent thread. The active host decides when native subagents or T3 delegates are appropriate.

## Settings and persistence

Explicit request settings take precedence over session choices and saved defaults. Reuse a valid existing selection without asking again. With no chosen/saved pair, use supported inherited settings; ask only when a meaningful choice is missing or ambiguous.

Native calls validate requested model options against the live catalog and forward them in `target.options`. A provider/model change does not automatically carry the parent's options. Check the returned effective selection.

The optional Python helper stores a provider/model preference outside the installed package:

```text
~/.config/t3-delegate/config.json
```

`XDG_CONFIG_HOME` changes the config directory; `T3_DELEGATE_CONFIG` overrides the full path. Existing version-1 files remain compatible:

```json
{
  "version": 1,
  "providerInstanceId": "EXACT_T3_PROVIDER_ID",
  "model": "EXACT_T3_MODEL_SLUG"
}
```

Model options and permission modes are not stored in this schema. See [config/config.example.json](config/config.example.json).

When the user requests a saved default:

```sh
python3 scripts/t3_delegate.py config init
# Or set exact discovered values without an interactive prompt:
python3 scripts/t3_delegate.py config set --provider EXACT_INSTANCE --model EXACT_MODEL
python3 scripts/t3_delegate.py config show
python3 scripts/t3_delegate.py config clear
```

`config init` and an unconfigured interactive helper `start` explicitly set a default. A one-time `start --provider ... --model ...` overrides it without writing config. An unconfigured non-interactive start fails before launching. Config writes use atomic replacement and restrictive file permissions where supported; never store credentials or task text in the config.

## Native workflow

- Give each assignment a self-contained brief, ownership boundaries and acceptance evidence.
- Use tool-bound `isolation: "worktree"` for separate child checkouts; uncommitted parent changes are absent.
- Record a unique `clientRequestId` before the initial dispatch and reuse it only for an identical retry.
- Follow completion notifications rather than polling. Inspect terminal status, `workState`, summary and actual output.
- Start fresh delegated review rounds with prior findings and objections; keep small fixes in the parent.
- Read supporting thread evidence by item ID/cursor. A bare message limit starts at the oldest messages.

[Examples](references/examples.md) include native argument shapes and follow-up handling.

## Optional top-level CLI helper

Python 3.9+ is required only for the helper. It wraps `t3 thread start/send/show/list` on the local T3 host; it does not create native children.

Use it only for an explicitly requested top-level-thread workflow allowed by the host. Verify project permission defaults fit the task and caller ceiling before launch. The CLI uses machine-owner authentication and project modes, not an inherited parent ceiling. If defaults cannot be verified, do not launch.

This CLI cannot express model options or mode overrides. Use MCP for assignments requiring reasoning effort, service tier, runtime or interaction settings. Raw `t3 thread start` does not read the helper's config and needs both selected model flags. See the [CLI prerequisites and examples](references/examples.md#explicit-top-level-cli-work).

Prompts and diagnostics go to stderr, leaving thread-command stdout parseable as JSON. Task length is checked in UTF-16 code units to match T3. CLI launches/sends have no helper-provided retry deduplication; reconcile uncertain effects before retrying.

## Validate

```sh
python3 -m unittest discover -s tests -v
```

Tests cover config persistence, temporary overrides, command forwarding, first-run JSON output, UTF-16 length boundaries and exit-code handling. They mock T3 execution and do not establish live server behavior.

## Source basis

Checked against T3 commit [220eb73524ca7882d53b6a12c824ccbcd97ad279](https://github.com/pingdotgg/t3code/commit/220eb73524ca7882d53b6a12c824ccbcd97ad279), reviewed 2026-10-26:

- [Outside-agent and host CLI documentation](https://github.com/pingdotgg/t3code/blob/220eb73524ca7882d53b6a12c824ccbcd97ad279/docs/user/outside-agents.md)
- [Thread CLI implementation](https://github.com/pingdotgg/t3code/blob/220eb73524ca7882d53b6a12c824ccbcd97ad279/apps/server/src/cli/thread.ts)
- [MCP input/result contracts](https://github.com/pingdotgg/t3code/blob/220eb73524ca7882d53b6a12c824ccbcd97ad279/packages/contracts/src/orchestratorMcp.ts)
- [Target inheritance, retry and timeline implementation](https://github.com/pingdotgg/t3code/blob/220eb73524ca7882d53b6a12c824ccbcd97ad279/apps/server/src/mcp/OrchestratorMcpService.ts)

Installed versions can differ. Active host instructions and callable tool schemas take precedence. Inspect local CLI help before assuming support. No live thread launch is required to validate this package's unit tests.
