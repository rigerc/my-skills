# Role-based orchestration update (2026-10-24)

- Converted skill instructions from generic issue-based delegation to **parent coordinator → specialized role → stage-gated handoff** orchestration.
- Added a **mandatory user provider/model question** before child dispatch, with support for a single pair across active roles, per-role overrides, explicitly requested inheritance, or explicit permission for the coordinator to choose.
- Added live `orchestrator_capabilities` validation for provider instance, model ID, advertised options, capability/constraints, mismatch detection and no-silent-fallback rule.
- Defined `research`, `design`, `implementation`, `test`, `review`, and exceptional `general` role boundaries, independent test/review gates and artifact-based handoffs.
- Added `references/role-orchestration.md`, `assets/role-assignment.md`, role metadata in delegation briefs and provider/model columns in the task ledger.
- Updated README and sprint delegation recipes to use role-specific dispatch and explicit model selection.
- Preserved `gh` helper scripts, their prior smoke checks and authorization/worktree/CI safety controls.

# Changes in improved skill (2026-10-24)

Compared with `gh-project-management.skill` and the earlier `github-project-manager`:

- Merged `gh` triage, milestones, Projects v2, release and report workflows with T3 Code implementation/review delegation.
- Grounded T3's actual `delegate_task`, `orchestrator_capabilities`, `task_status`, `task_cancel`, `t3_thread_send`, `t3_thread_launch`, pending approval and scheduling semantics in `apps/server/src/mcp/toolkits/orchestrator/tools.ts` and `packages/contracts/src/orchestratorMcp.ts`.
- Documented worktree isolation (based on committed local HEAD), model and option inheritance, distinct review-round `clientRequestId`s, async completion notifications, timeout semantics, and child question/approval safety.
- Clarified that GitHub delivery state and T3 task state are independent; a completed agent is not proof of a merged PR or CI success.
- Reworked `project_set_field.sh` to preview with `--dry-run`, validate field/option/iteration values, support issues and PRs, resolve IDs safely, and reject ambiguous values without a guessed field type.
- Reworked `status_report.sh` to read GitHub only, include issue/PR URLs and milestone summaries, fail on read errors, and flag capped counts.
- Added five isolated fake-CLI smoke tests. No GitHub writes are performed by tests or dry-run mode.

## Compatibility

- This is an agent skill folder, not a plugin that installs new MCP tools or credentials.
- T3 orchestration requires an active T3 parent agent session exposing the MCP toolkit; helper scripts only use `gh`.
- `gh` flags and project field metadata may vary with installed versions; inspect live CLI help/schema. No live T3/GitHub integration was exercised in this build.
