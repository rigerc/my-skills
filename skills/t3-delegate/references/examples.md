# T3 delegation recipes

## Native MCP access

Inside T3 Code, use the callable tools under the active host's routing rules. Outside agents can connect to an authorized T3 environment over MCP, but may have no parent thread. The absence of parent context does not turn a top-level launch into a child task.

See the [official outside-agent connection instructions](https://github.com/pingdotgg/t3code/blob/220eb73524ca7882d53b6a12c824ccbcd97ad279/docs/user/outside-agents.md) for OAuth setup. Connect only when setup is requested; preserve existing credentials and scopes.

## Resolve settings once

Apply the skill's [selection rules](../SKILL.md#resolve-provider-model-and-options). Reuse an applicable session choice or valid saved default without another confirmation. Resolve all requested options against the chosen model's live catalog, including reasoning effort and service tier.

These native argument shapes use placeholders. Replace provider/model/options with actual validated values; omit options only when no explicit or applicable requested settings need forwarding. Generate each assignment's request ID before its first call.

## Native: two independent assignments

Task A, a read-only review:

```json
{
  "title": "Review auth edge cases",
  "role": "review",
  "target": {
    "providerInstanceId": "<resolved-instance-id>",
    "model": "<resolved-model>",
    "options": [{"id": "<advertised-option-id>", "value": "<requested-supported-value>"}]
  },
  "isolation": "shared",
  "mode": "async",
  "clientRequestId": "<unique-auth-review-id>",
  "task": "Review src/auth in <absolute checkout path> without editing files. Return security regressions with file:line and reproducible evidence. Do not edit, commit, push, deploy, or start subagents."
}
```

Task B, isolated test changes:

```json
{
  "title": "Add token parsing tests",
  "role": "test",
  "target": {
    "providerInstanceId": "<resolved-instance-id>",
    "model": "<resolved-model>",
    "options": [{"id": "<advertised-option-id>", "value": "<requested-supported-value>"}]
  },
  "isolation": "worktree",
  "mode": "async",
  "clientRequestId": "<unique-token-tests-id>",
  "task": "In the tool-prepared checkout, add token parsing tests in tests/auth only. Parent base: <committed SHA>. Do not change src/auth, merge, push, or start subagents. Run the focused test command declared in the repo. Return changed paths, exact checks, branch/worktree and blockers."
}
```

Dispatch independent assignments within actual capacity. Save IDs and effective settings; compare returned provider/model/options with what was requested. Follow the returned `next` and yield for completion. After notifications, collect each result with `task_status`. Check summaries, terminal status and diffs; do not confuse a finished turn with completed work.

## Native: re-review after fixes

Make straightforward small fixes in the parent. If another review is justified within the review budget, call `delegate_task` again with a **new** `clientRequestId`. The brief includes the original objective, scope and base, the current revision, earlier findings, fixed/disagreed items with evidence and unresolved objections. Do not send the next review to the prior `childThreadId`.

For supporting evidence, use a known item ID or the timeline cursor. An initial read without `afterPosition` begins at the oldest messages. Read `thread.itemCount`, choose a recent position window when that is relevant, and page using `nextPosition`. Recover truncated text separately. The completed result itself comes from `task_status.summary`.

## Native: blocked work and cancellation

A pending question can be answered from existing authorized context through question tools. Bring user-owned choices to the user. Permission approvals must be resolved by the approval holder; pending-request tools do not grant approval authority.

To stop a native child, call `task_cancel`:

```json
{"taskId": "<returned-task-id>", "reason": "Assignment was replaced"}
```

Reconcile the task's terminal state before overlapping writes or replacement work. A timeout or `cancel_requested` alone does not establish that the old task stopped.

## Explicit top-level CLI work

This section applies only when the user explicitly requests a separate top-level conversation **and** the active host permits CLI orchestration. Never use it automatically because child tools are unavailable or a native request was rejected.

The optional helper manages top-level threads on the local T3 host. It does not implement native delegation, child notifications or MCP retry keys. Before starting work:

1. Confirm the intended local environment and registered project.
2. Check the project's runtime/interaction defaults through an authorized project read. They must fit the task's authorization and any caller ceiling **before** sending work. If these cannot be verified, do not launch.
3. Confirm the requested provider/model is available.
4. Use MCP instead when the assignment requires explicit model options or mode overrides. This CLI surface cannot express reasoning effort, service tier, runtime mode or interaction mode; it must not silently discard them.
5. Keep launch identity and inspect the prepared thread's effective selection. On a lost response, reconcile with the thread list; CLI launch has no idempotency key. Do not blindly retry starts or sends.

The CLI uses project permission defaults and runs with machine-owner authentication. It does not inherit a calling thread's permission ceiling. A user request for a child or a configured pair does not authorize this separate workflow.

### Wrapper commands

After the checks above, use an existing saved pair or pass both explicit flags. These wrapper starts forward the saved/explicit pair:

```sh
# Inspect an existing saved pair; configure only if the user requests a saved default.
python3 scripts/t3_delegate.py config show

# Authorized top-level review; no model options or mode overrides required.
python3 scripts/t3_delegate.py start --project . --title "Review API" \
  --task "Read-only review of src/api; report issues without editing files"

# Authorized separate worktree, from a committed base.
python3 scripts/t3_delegate.py start --project . --worktree main \
  --branch agent/token-tests --title "Token tests" --task-file task.txt

python3 scripts/t3_delegate.py show THREAD_ID --messages 10
python3 scripts/t3_delegate.py list --project .
```

If no pair is saved, supply `--provider EXACT_INSTANCE --model EXACT_MODEL` for one launch or explicitly configure a default. Interactive `config init` and an unconfigured interactive `start` ask for and save a default. In non-interactive contexts an unconfigured start fails before launching.

### Raw CLI commands

Raw `t3` does **not** load this helper's config. Always pass both selected flags explicitly:

```sh
t3 thread start . - --provider EXACT_INSTANCE --model EXACT_MODEL \
  --worktree main --branch agent/cache-adapter \
  --title "Refactor cache adapter" --json <<'TASK'
Objective: refactor src/cache/adapter.ts without changing public behavior.
Scope: src/cache and tests/cache.
Run the focused tests. Do not merge or push. Return changes and blockers.
TASK

t3 thread show THREAD_ID --json --messages 10
```

For an authorized follow-up to this explicitly created **top-level** thread:

```sh
python3 scripts/t3_delegate.py send THREAD_ID \
  --task "Run focused checks and report exact results" --wait
```

`send` queues work; it is not a method for continuing native child review rounds. `--wait` can block until the run finishes or needs input; use it only where the host permits a foreground CLI wait. Exit 1 means a failed/stopped run; exit 2 means human input is required. CLI results and exit codes pass through the wrapper, whose JSON stdout stays separate from prompts and diagnostics on stderr.
