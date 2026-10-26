---
name: t3-delegate
description: Delegate bounded implementation, research, review, design, or test assignments to T3 Code child tasks. Use for requested delegation or independent work where the active host permits it; preserve selected providers, models, and options, collect completion evidence, and integrate results.
---

# T3 delegate

Use the active host's native-subagent and T3 routing rules. This skill explains T3 child tasks; it does not make every independent task require delegation. Keep small fixes and tightly coupled work in the parent.

## Choose the mechanism

- Use native subagents when the host permits them for the selected provider, model, options and lifecycle.
- Use `delegate_task` for T3-owned child work, including a child needing its own checkout. Never use a top-level thread merely to obtain a worktree.
- If a requested provider, model or delegation route is unavailable, report the limitation. Do not switch providers, models or transports without authorization.
- Creating a top-level thread requires an explicit request for a new conversation. Missing child tools are not that request. The optional CLI instructions in [examples.md](references/examples.md#explicit-top-level-cli-work) cover a separately authorized workflow, not a fallback.
- Discover tools by their base names; an MCP prefix can vary or tools can load late. Make the host's prescribed bounded capability-discovery attempt before declaring a tool absent.

The underlying task and the active host determine permitted effects and resource limits. Neither a task brief nor a child response expands them. Keep runtime/interaction modes within the caller's ceiling.

## Resolve provider, model and options

Read `orchestrator_capabilities` before the first T3 dispatch, using its `search` input when needed for a named model. Reuse discovery within the host's refresh rules. Check provider constraints, child eligibility and cross-provider eligibility where applicable.

Resolve each setting independently:

1. Honor explicit selections in the current request, including reasoning effort and service tier.
2. Reuse applicable choices already made in this conversation. Do not request confirmation again.
3. For an otherwise unspecified pair, reuse a saved valid default; if none exists, use the host's inherited selection where supported.
4. Ask only for a missing choice that cannot be resolved from these sources or is ambiguous. A saved unsupported pair is a gap, not permission to substitute silently.

Read a saved pair, when relevant, with `python3 scripts/t3_delegate.py config show` from this skill's directory. A malformed config must be reported or repaired deliberately. The config stores a provider/model pair, not model options or permission modes.

Validate requested options against the selected model's advertised IDs and values. Put them in `target.options`; do not put them at the top level or translate them to an unsupported level. T3 inherits options only when the selected provider and model match the parent's pair. When changing the pair, carry over any applicable user-requested options explicitly after validating their names and values on the new model. If a required setting cannot be honored, report it before dispatch.

Pass the resolved pair as `target: {providerInstanceId, model}`, plus `options` when needed. A one-time override does not change the saved default. Update durable defaults only when the user requests persistence:

```sh
python3 scripts/t3_delegate.py config set --provider 'EXACT_INSTANCE_ID' --model 'EXACT_MODEL_SLUG'
```

Config defaults to `${XDG_CONFIG_HOME:-$HOME/.config}/t3-delegate/config.json`; `T3_DELEGATE_CONFIG` overrides the path. Version 1 contains `version`, `providerInstanceId` and `model`. Use `config init` for interactive setup, `config show` to inspect, and `config clear` to remove it. Store no credentials or task text there. The helper uses atomic replacement and owner-only file permissions where supported. See [the schema example](config/config.example.json).

## Prepare the assignment

A child receives its task brief, not the parent conversation. Include:

- Objective, necessary context and the exact repository/checkout.
- Relevant decisions, file ownership, exclusions and permitted effects.
- Observable acceptance criteria and focused verification commands.
- Required output: changed paths, branch/worktree or PR, checks actually run, findings and unresolved work.
- Any nested-delegation prohibition or explicit descendant budget.

Use a bounded number of children within available capacity. Give writers non-overlapping ownership and serialize shared mutation commands.

### Checkout isolation

- `isolation: "shared"`: read-only review, non-mutating checks, or deliberately coordinated edits in the parent's checkout. A review role does not enforce read-only access; say "do not edit files" in the brief.
- `isolation: "worktree"`: independent implementation in a tool-bound checkout from the parent's committed HEAD. Uncommitted parent edits are absent. Commit only if authorized, transfer necessary inputs explicitly, or keep dependent work local.
- Do not create child worktrees in shell commands or try to bind one by putting a path in the task. Worktree output still needs deliberate review and integration.

## Launch with a recorded retry key

Allocate and record `clientRequestId` **before the first call**. Use it on that call and reuse it for an identical retry if the response is lost. A new assignment or review round gets a new ID. An ID added only after a lost response cannot deduplicate the original call.

This is an illustrative tool argument shape; replace the placeholders with resolved values. Omit the options field when none is needed, or fill it with supported requested settings. Replace the sample request ID with one unique to the assignment.

```json
{
  "task": "Objective: review the parser empty-input behavior. Repo: <absolute checkout path>. Inspect src/parser and its tests without editing files, committing, pushing, or starting subagents. Return concrete findings with file:line and evidence, or state that none were found.",
  "title": "Parser behavior review",
  "role": "review",
  "target": {
    "providerInstanceId": "<resolved-instance-id>",
    "model": "<resolved-model-slug>",
    "options": [
      {"id": "<advertised-option-id>", "value": "<requested-supported-value>"}
    ]
  },
  "isolation": "shared",
  "mode": "async",
  "clientRequestId": "<unique-assignment-id>"
}
```

Use `mode: "wait"` only when this turn needs the result. Its `timeoutMs` limits the parent's wait; a timed-out wait leaves the child running.

Retain `taskId`, `childThreadId`, returned `link`, effective provider/model/options and work state. Compare the effective selection with the request; do not accept a silent mismatch. Cancel mismatched work, preserve any effects and report the discrepancy.

## Collect completion and inspect evidence

- Follow a returned `next` instruction to end the turn. Completion wakes this thread; do not poll, manually wait on the backing child thread, or create a watcher.
- After the completion notification, read `task_status({taskId})`. `workState: "working"` or `"waiting_for_children"` is not done, even if a turn completed.
- `workState: "result_available"` means inspect the terminal status and summary. Failure, cancellation or missing required output is not success.
- Handle real pending questions through authorized question tools and existing context. Permission approvals remain with the authorized approval holder; a pending-request tool is not a way to approve security requests.
- Use `task_status.summary` for the final result. For supporting evidence, read a specific item or page the relevant timeline with `afterPosition=nextPosition`. A bare `t3_thread_read({threadId, limit:10})` starts at the oldest messages, not the newest. To reach recent evidence, first read the thread metadata's `itemCount`, then select a recent `afterPosition` window and page as needed. Recover truncated item text with `itemId` and `textOffset=nextTextOffset`.
- Link a thread using its returned `link` verbatim; if absent use `[title](t3-thread://v1/<exact-id>)`.

Inspect actual diffs, acceptance evidence and focused checks before integrating code. Preserve the parent's unrelated work. Report where changes live and whether integration actually occurred.

## Follow-up rounds, failure and cancellation

Every delegated review/re-check is a fresh `delegate_task` with a new request ID and the original brief, prior findings, responses and unresolved objections. Do not start another round with `t3_thread_send` to `childThreadId`. Fix small findings in the parent instead of creating a delegate for them. State a bounded review budget appropriate to the assignment; exhaustion is not approval.

Cancel a task that is replaced, unnecessary, unsafe or stopped by the user with `task_cancel({taskId, reason})`, not `t3_thread_interrupt` on its backing child thread. A cancellation request is not proof that writes stopped: use terminal state evidence through the host's permitted lifecycle before overlapping work takes ownership. Do not keep polling a running delegate.

Reconcile an uncertain launch before retrying and preserve its original request ID. Do not create replacement work while the original may still own the same writes.

Final handoff: verified result, child link/task ID, changed paths or PR, checks and integration state, plus remaining blockers. Follow the active host's PR-linking and watch rules.

## References

- [Native recipes and explicitly requested top-level CLI work](references/examples.md)
- [Config schema example](config/config.example.json)
- Pinned API/source basis and validation scope: [README.md](README.md#source-basis)
