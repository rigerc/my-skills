# GitHub Project Manager — Role-based T3 Orchestration

An upgraded `SKILL.md` that combines the user's **gh-project-management** skill (GitHub CLI, Projects v2, recipes and shell helpers) with **github-project-manager** (role-based T3 MCP orchestration, user-selected provider/models, worktree safety, acceptance gates and integration tracking).

## What it does

- Read, triage, create and track issues, labels and milestones with `gh`.
- Work with Projects v2 and named Status/Priority/Iteration fields, including a dry-run helper.
- Generate read-only GitHub standup/weekly Markdown reports.
- Split work by agent roles (`research`, `design`, `implementation`, `test`, `review`), with the parent coordinating handoffs and delivery gates.
- **Ask the user which provider/model to use for each active role before delegation.** Offer one selection for all roles, a per-role mapping, or explicitly chosen parent inheritance. Resolve choices through live T3 `orchestrator_capabilities`; dispatch with role-specific `delegate_task.target` only after validation.
- Track child task IDs, isolated branches, PR verification, review gates and actual delivery.

## Install

Unzip the archive **from your repository root**:

```bash
mkdir -p .agents/skills
unzip github-project-manager-role-based.zip -d .agents/skills/
# Expects: .agents/skills/github-project-manager/SKILL.md
```

Or copy the `github-project-manager` folder to `.agents/skills/`. For a personal skill rather than repository-scoped skill, use the provider's supported global skill directory. T3 recognizes skills for the selected provider; after adding skills, use **Restart agent session** in T3's command palette if the skill doesn't appear immediately. In the composer type `$` to select a skill or `/` if skill suggestions are enabled.

## Prerequisites

- `gh` authenticated for the **target** repository; `jq` and `bash` for shell helpers.
- GitHub Project scope for editing Projects v2. Authentication and scopes remain under the user's control.
- An active T3 Code agent session with app-owned MCP orchestration tools to delegate. Standard CLI sessions outside T3 may not expose them.
- A real repo checkout for code edits, repo instructions and test dependencies.

## Usage

> Use the github-project-manager skill. Audit the backlog for `OWNER/REPO`, group issues by priority/dependencies and propose a one-week sprint. Do not modify GitHub yet.

> Use github-project-manager to plan implementation of issues #12 and #13. First show me active agent roles and ask which available provider/models to assign to each role. Then use isolated worktrees, independent test/review, and draft PRs. Do not merge.

> Make a standup report for `OWNER/REPO`, combining fresh GitHub state with T3 task statuses known to this parent run.

For helper help:

```bash
bash .agents/skills/github-project-manager/scripts/project_set_field.sh --help
bash .agents/skills/github-project-manager/scripts/status_report.sh --help
```

The shell scripts can be invoked from any working directory; pass `-R`/`--repo` or `--owner`, `--repo` explicitly. Scripts do not delegate T3 tasks themselves.

## Package contents

- `SKILL.md`: selection triggers, preflight, authorization rules and project-delivery workflow.
- `references/gh-workflows.md`: `gh` recipes, PR checks, milestones.
- `references/projects-v2.md`: fields, project IDs, iterations and new CLI forms.
- `references/recipes.md`: triage, sprint, standup, release playbooks.
- `references/role-orchestration.md`: role responsibilities, handoff gates, mandatory provider/model selection and mapping.
- `references/t3-delegation.md`: role-targeted MCP dispatch, lifecycle, worktrees and ledgers.
- `assets/`: issue and child-task briefs plus a provider/model role-assignment worksheet.
- `scripts/`: `project_set_field.sh` and `status_report.sh`.
- `tests/`: mocked CLI smoke tests and offline role-orchestration documentation checks with no GitHub writes. Run `python3 -m unittest discover -s tests -v` from the skill directory.
- `CHANGELOG.md`: what changed from both original skills.

## Safety / compatibility

The scripts never change a GitHub account's authentication. Preview before bulk writes. The `--dry-run` flag prevents field mutation but may still perform **read** commands. A provider/model choice is required for each delegated role; lack of a choice blocks delegation, not read-only planning. T3 `isolation: "worktree"` is available in the linked current server contract but is used only if exposed by the installed MCP schema; older installations may not support it. No task is considered delivered until its GitHub/CI evidence is checked. No execution against an actual user repository is included with this package.

## Documentation

- T3 orchestrator tool definitions (source of truth): https://github.com/pingdotgg/t3code/blob/main/apps/server/src/mcp/toolkits/orchestrator/tools.ts
- T3 contract types: https://github.com/pingdotgg/t3code/blob/main/packages/contracts/src/orchestratorMcp.ts
- T3 orchestrator MCP docs: https://github.com/pingdotgg/t3code/blob/main/docs/orchestration-v2/orchestrator-mcp-server.md
- T3 delegated worktree discussion: https://github.com/pingdotgg/t3code/discussions/16460
- gh project item-edit: https://cli.github.com/manual/gh_project_item-edit
