# GitHub CLI playbook (`gh`)

Always resolve repo context and use `-R OWNER/REPO` on issue/PR commands if uncertain. For `gh project`, resolve the **project owner** separately from the issue repository. Use JSON for machine output; URLs in the final report. Commands that write to GitHub require the authorization described in SKILL.md.

## Preflight and snapshots

```bash
gh --version
gh auth status
gh repo view --json nameWithOwner,url,defaultBranchRef
REPO=OWNER/REPO

gh issue list -R "$REPO" --state open --limit 100 \
  --json number,title,url,labels,assignees,milestone,updatedAt

gh pr list -R "$REPO" --state open --limit 100 \
  --json number,title,url,isDraft,reviewDecision,statusCheckRollup

gh label list -R "$REPO" --limit 100
```

Search existing and closed work for duplicates, e.g. `gh issue list -R "$REPO" --state all --search 'in:title authentication' --limit 100`. Lists have pagination caps: **do not call a bounded list complete if it reaches the cap**.

## Issue lifecycle

```bash
# Inspect before mutation
gh issue view 42 -R "$REPO" --json number,title,body,labels,assignees,milestone,url
# Create from a filled body file (avoid shell quoting issues)
gh issue create -R "$REPO" --title "Actionable title" --body-file issue.md
# Apply authorized, scoped edits
gh issue edit 42 -R "$REPO" --add-label "bug,p1" --add-assignee "@me"
gh issue comment 42 -R "$REPO" --body-file progress.md
# Closing/reopening requires policy/authorization checks
gh issue close 42 -R "$REPO" --reason completed --comment "Verified in merged PR #77"
gh issue reopen 42 -R "$REPO"
```

Use `gh issue develop 42 --checkout` if supported by the installed `gh` and linked-branch workflow; avoid creating a branch in a shared checkout being edited by other workers.

## Pull requests: review and delivery

```bash
gh pr list -R "$REPO" --search 'is:open review:required draft:false' --limit 100 \
  --json number,title,url,author,reviewDecision

gh pr view 77 -R "$REPO" --json url,state,isDraft,reviewDecision,mergeStateStatus

gh pr diff 77 -R "$REPO"
gh pr checks 77 -R "$REPO" --required
# Only if approved to publish a PR; provide real branch and title
gh pr create -R "$REPO" --base main --head feature/issue-42 \
  --title "Implement validation" --body-file pr.md --draft
# Merge requires explicit user authorization and required checks
gh pr merge 77 -R "$REPO" --squash
```

Inspect code and actual CI rather than treating green status in a list as comprehensive. Repository branch protection remains authoritative. Use a PR body line `Closes #42` only when closing that issue on merge is intended.

## Milestones via REST

```bash
# Read all open milestones with pagination
gh api --paginate --slurp 'repos/OWNER/REPO/milestones?state=open&per_page=100' \
  --jq '[.[][] | {number,title,open_issues,closed_issues,due_on}]'
# Write only with authorization
gh api 'repos/OWNER/REPO/milestones' -f title='v1.2' -f description='...'
# Closing a milestone is a separate, authorized operation
gh api --method PATCH 'repos/OWNER/REPO/milestones/3' -f state=closed
```

Milestone dates use UTC ISO 8601 when creating through REST (`due_on`), not local informal strings. Milestones and releases are different objects.

## Labels and releases

```bash
gh label list -R "$REPO" --limit 100
# Creating/updating labels may impact many issues: preview changes first
gh label create bug -R "$REPO" --color 'd73a4a' --description 'Something is broken'

gh release list -R "$REPO" --limit 10
gh issue list -R "$REPO" --milestone 'v1.2' --state open --limit 100
# Only after release approval and CI/readiness gates
gh release create v1.2.0 -R "$REPO" --generate-notes --draft
```

## Failure and rate limits

- `gh auth status` scopes missing: ask for a user-approved `gh auth refresh -s project`; for read-only Projects access some tokens use `read:project`, but confirm current `gh` requirements.
- `HTTP 403`: permissions, scopes, org SSO or branch policy. Do not circumvent.
- `gh project` "Could not resolve": verify exact project owner, number, and visibility.
- `gh` reports unknown JSON fields or flags: consult `gh ... --help` rather than guessing.
- Rate-limit large writes: target preview, bounded batches, pace writes (e.g. 1s between), and report partial success/failed IDs; never blindly retry potentially successful creates.
