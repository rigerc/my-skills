# GitHub Projects v2: field editing and board workflows

A Project owner (user/org) and project number determine the board. The repository and board can have different owners. Project fields may be customized. **Inspect options first** and use those names verbatim.

## Read the board

```bash
gh project list --owner ORG
gh project view 7 --owner ORG --format json
gh project field-list 7 --owner ORG --format json --limit 100
gh project item-list 7 --owner ORG --format json --limit 500
# Newer gh also supports query + selected columns:
gh project item-list 7 --owner ORG --query 'status:"In Progress"' \
  --field Status --field Priority --format json --limit 500
```

A project number is **not** a GraphQL project ID. Project item IDs are distinct from issue numbers:

| Identifier | Example | Where to get it |
| --- | --- | --- |
| Project number | `7` | `gh project list` |
| Project node ID | `PVT_...` | `gh project view 7 --owner ORG --format json --jq .id` |
| Item node ID | `PVTI_...` | `gh project item-list` (`.items[].id`) |
| Field node ID | `PVTSSF_...`, `PVTF_...` | `gh project field-list` (`.fields[].id`) |
| Option/iteration ID | opaque string | `gh project field-list`, sometimes GraphQL |

## Add and move a card

```bash
gh project item-add 7 --owner ORG --url 'https://github.com/ORG/REPO/issues/42'
# Newer gh: preferred readable single-select interface
gh project item-edit 7 --owner ORG \
  --url 'https://github.com/ORG/REPO/issues/42' --field Status --value 'In Progress'
```

For reusable, version-aware scripts, use the bundled helper:

```bash
bash scripts/project_set_field.sh --owner ORG --project 7 --repo ORG/REPO \
  --issue 42 --field Status --value 'In Progress' --dry-run
# Remove --dry-run after reviewing the plan and authorizing the write.
```

The helper validates the field/option names then uses resolved GitHub node IDs, which also works on CLI builds predating the named item-edit interface. For a quick interactive single-select change, use the documented modern `--url --field --value` command directly. For number/date/text fields use `--as number|date|text` if the CLI does not expose a field data type. The helper will not infer types from values (e.g. `123` might be text). For iteration fields, it resolves an iteration by **exact name** when `field-list` exposes the IDs; otherwise use GraphQL and `--iteration-id` directly (see below). Never create a missing field or value without authorization.

## Explicit machine-level edits

```bash
gh project item-edit --id PVTI_ITEM --project-id PVT_PROJECT \
  --field-id PVTSSF_FIELD --single-select-option-id OPTION_ID

gh project item-edit --id PVTI_ITEM --project-id PVT_PROJECT \
  --field-id PVTF_FIELD --text 'a value'

gh project item-edit --id PVTI_ITEM --project-id PVT_PROJECT \
  --field-id PVTF_FIELD --number 5

gh project item-edit --id PVTI_ITEM --project-id PVT_PROJECT \
  --field-id PVTF_FIELD --date '2026-11-30'

gh project item-edit --id PVTI_ITEM --project-id PVT_PROJECT \
  --field-id PVTIF_FIELD --iteration-id ITERATION_ID

gh project item-edit --id PVTI_ITEM --project-id PVT_PROJECT \
  --field-id FIELD_ID --clear
```

Built-in fields including Assignees, Labels and Milestone are commonly managed through the underlying issue/PR rather than this command (`gh issue edit`). Confirm available CLI flags because gh versions change.

## Iteration ID GraphQL fallback

If the field listing omits iteration IDs:

```bash
gh api graphql -f query='
query($org:String!, $num:Int!) {
  organization(login:$org) {
    projectV2(number:$num) {
      fields(first:50) { nodes {
        ... on ProjectV2IterationField {
          name
          configuration { iterations { id title startDate duration } }
        }
      } }
    }
  }
}' -f org=ORG -F num=7
```

Substitute `user(login:$org)` for user-owned boards. Select by observed `title`, pass the exact ID to `gh project item-edit --iteration-id`, and verify the post-edit item. To inspect past iterations, check the current API schema and `field-list` output rather than assuming the example returns historical ones.

## Parent/child issues

```bash
CHILD_DB_ID=$(gh api repos/OWNER/REPO/issues/CHILD_NUMBER --jq .id)
gh api repos/OWNER/REPO/issues/PARENT_NUMBER/sub_issues \
  -F sub_issue_id="$CHILD_DB_ID"
gh api repos/OWNER/REPO/issues/PARENT_NUMBER/sub_issues \
  --jq '.[] | "#\(.number) \(.title)"'
```

Issue database IDs and issue numbers are **different**. Creating relationships is a write operation; preview parents/children first.

## Limits and recovery

Some board view/layout/workflow settings are not exposed via `gh project` in every version. Do not mutate board schema through undocumented calls; use project Settings/Workflows UI when needed. `gh project field-create` can add simple fields, but doing so affects every project user and needs approval. Board item lists default to a small limit; set `--limit` and disclose if truncated.

Official manual: https://cli.github.com/manual/gh_project_item-edit
