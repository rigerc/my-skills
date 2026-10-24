# Project management recipes

Fill in `OWNER/REPO`, board owner/number, issue numbers, and real existing field values. Each mutating command requires the authorization policy in SKILL.md. Inspect `gh ... --help` when the installed version differs.

## Backlog triage (default: read-only)

```bash
REPO=OWNER/REPO
gh issue list -R "$REPO" --state open --search 'no:label' --limit 100 \
  --json number,title,url,updatedAt
gh issue list -R "$REPO" --state open --search 'no:assignee' --limit 100 \
  --json number,title,url,labels
gh issue view 123 -R "$REPO" --comments
```

Produce a proposed table: issue URL, current state, proposed priority/label, owner, dependency, and explanation. Only after the user requests these changes, apply the specific edits and reread resulting state:

```bash
gh issue edit 123 -R "$REPO" --add-label p1 --add-assignee alice
gh issue view 123 -R "$REPO" --json url,labels,assignees
```

## Bulk edits with explicit target preview

```bash
gh issue list -R "$REPO" --state open --label needs-info \
  --search 'updated:<2026-09-01' --limit 100 --json number,title,url
# Save verified issue numbers explicitly; do not pipe a fresh changing search into a write loop.
for n in 101 105 110; do
  gh issue edit "$n" -R "$REPO" --add-label stale || break
  sleep 1
done
```

`gh label create --force` **updates an existing label** too; avoid in bulk bootstrap unless authorized. For destructive operations and transfers, demand specific approval and keep an audit trail.

## Sprint planning / Projects v2

1. Read board fields/options and current iteration before editing. Select only ready, unblocked issues; respect WIP limits.
2. Preview each planned move with `scripts/project_set_field.sh --dry-run`.
3. Add missing cards using `gh project item-add N --owner ORG --url ISSUE_URL`.
4. Update Status/Priority/Iteration with the helper (or native `gh project item-edit`). Verify final item-list output after changes.
5. Record commitments and unresolved dependencies. At sprint end, identify rollover items instead of silently moving them.

```bash
bash scripts/project_set_field.sh --owner ORG --project 7 --repo OWNER/REPO \
  --issue 42 --field Status --value 'In Progress' --dry-run
# After authorization: remove --dry-run.
```

## Delegating a sprint

For each accepted issue:

1. Inspect issue, repo instructions, actual base commit and dependency order.
2. Fill `assets/delegation-brief.md` with acceptance criteria, tests, file ownership and non-goals.
3. Identify needed specialist roles and call `orchestrator_capabilities`. **Ask the user which provider/model to assign to each active role**; offer one pair for all roles, per-role overrides or explicit parent inheritance. Validate the chosen mapping. If it is missing, stop before dispatch, while read-only planning can continue.
4. Dispatch scoped tasks in the order `research/design (if needed) → implementation → independent test/review → coordinator integration`, using `delegate_task` with the user-selected per-role `target`, unique per-attempt IDs, and verified `isolation: "worktree"` for concurrent code writers.
5. Preserve returned task IDs, selected/actual provider-model pairs, and role handoffs in a ledger. Reconcile child results to actual branch, `gh pr view`, diffs, CI and reviews; keep GitHub issue/project status truthful.

## Standup or weekly status

```bash
bash scripts/status_report.sh -R OWNER/REPO --days 7 --stale 14
```

The script reports GitHub facts; augment manually with available T3 `task_status` results, risks and known blockers. It deliberately does **not** assume an agent succeeded because an issue is closed, or attempt to guess a child task ID.

## Pull request review queue

```bash
gh pr list -R "$REPO" --search 'is:open review:required draft:false' --limit 100 \
  --json number,title,url,reviewDecision,statusCheckRollup
gh pr view 45 -R "$REPO" --json url,state,isDraft,reviewDecision,mergeStateStatus
gh pr checks 45 -R "$REPO" --required
```

If a review finds blockers, annotate exact file paths and requested changes; delegate a follow-up implementation or independent review with a new `clientRequestId` and the previous evidence.

## Release-readiness audit

```bash
gh issue list -R "$REPO" --milestone 'v1.2' --state open --limit 100 \
  --json number,title,url
gh release list -R "$REPO" --limit 5
gh pr list -R "$REPO" --state merged --limit 100 \
  --json number,title,url,mergedAt
```

Check milestone scope, branch protections, migration and rollout/rollback plan, CI, security and documentation. If authorized, draft a release first:

```bash
gh release create v1.2.0 -R "$REPO" --generate-notes --draft
```

Publish and close milestones only upon separately authorized release completion.
