#!/usr/bin/env bash
# Safely preview or change ONE GitHub Projects v2 field on an existing issue/PR card.
# Reads with gh + jq, writes only after arguments and field value are validated.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  project_set_field.sh --owner OWNER --project NUMBER --field NAME \
    (--value VALUE | --clear) (--item PVTI_ID | --issue N --repo OWNER/REPO | --pr N --repo OWNER/REPO) \
    [--as text|number|date] [--dry-run]

--issue / --pr  Select a GitHub issue or PR card already on the board.
--item          Select a known Projects v2 item node ID.
--value         Single-select option, iteration title, or typed value.
--clear         Remove the field's value (mutually exclusive with --value).
--as            Specify text, number or date for simple fields. Inferred from
                the field metadata when available, otherwise required.
--dry-run       Show the exact planned mutation; make read-only gh calls only.

This helper never creates a missing field, option, project, or item.
If the issue/PR is not on the board, add it separately with:
  gh project item-add PROJECT --owner OWNER --url https://github.com/OWNER/REPO/issues/N
EOF
}
die() { printf 'error: %s\n' "$*" >&2; exit 1; }
require_arg() { [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || die "expected a value for $1"; }

OWNER='' PROJECT='' FIELD='' VALUE='' REPO='' ITEM='' ISSUE='' PR='' KIND=''
CLEAR=0 DRY=0 HAS_VALUE=0
while (( $# > 0 )); do
  case "$1" in
    --owner|--project|--field|--value|--repo|--item|--issue|--pr|--as)
      require_arg "${1}" "${2:-}"
      case "$1" in
        --owner) OWNER=$2;; --project) PROJECT=$2;; --field) FIELD=$2;;
        --value) VALUE=$2; HAS_VALUE=1;; --repo) REPO=$2;;
        --item) ITEM=$2;; --issue) ISSUE=$2;; --pr) PR=$2;; --as) KIND=$2;;
      esac
      shift 2;;
    --clear) CLEAR=1; shift;;
    --dry-run) DRY=1; shift;;
    -h|--help) usage; exit 0;;
    *) die "unknown argument: $1";;
  esac
done

command -v gh >/dev/null || die 'gh is not installed'
command -v jq >/dev/null || die 'jq is not installed'
[[ -n "$OWNER" && -n "$PROJECT" && -n "$FIELD" ]] || die '--owner, --project, and --field are required'
[[ "$PROJECT" =~ ^[1-9][0-9]*$ ]] || die 'project must be a positive integer'
(( CLEAR + HAS_VALUE == 1 )) || die 'choose exactly one of --value or --clear'
if [[ -n "$KIND" ]]; then
  [[ "$KIND" =~ ^(text|number|date)$ ]] || die '--as must be text, number, or date'
fi
if [[ -n "$ITEM" ]]; then
  [[ -z "$ISSUE" && -z "$PR" ]] || die 'use --item or --issue/--pr, not both'
else
  [[ -n "$REPO" ]] || die '--repo is required with --issue or --pr'
  [[ "$REPO" =~ ^[[:alnum:]_.-]+/[[:alnum:]_.-]+$ ]] || die 'repo must be OWNER/REPO'
  [[ -z "$ISSUE" || -z "$PR" ]] || die 'choose --issue or --pr'
  [[ -n "$ISSUE" || -n "$PR" ]] || die 'select an item with --item, --issue, or --pr'
  [[ "${ISSUE:-${PR}}" =~ ^[1-9][0-9]*$ ]] || die 'issue/PR number must be a positive integer'
fi

FIELD_LIST=$(gh project field-list "$PROJECT" --owner "$OWNER" --format json --limit 200) || die 'field-list failed'
FIELD_JSON=$(jq -ce --arg f "$FIELD" '[.fields[] | select((.name | ascii_downcase) == ($f | ascii_downcase))] | if length == 1 then .[0] else empty end' <<<"$FIELD_LIST") \
  || die "field '$FIELD' not found uniquely; inspect gh project field-list"
FIELD_ID=$(jq -r '.id // empty' <<<"$FIELD_JSON")
FIELD_TYPE=$(jq -r '.type // "" | ascii_downcase' <<<"$FIELD_JSON")
FIELD_DATA_TYPE=$(jq -r '.dataType // .data_type // "" | ascii_downcase' <<<"$FIELD_JSON")
[[ -n "$FIELD_ID" ]] || die "no ID for field '$FIELD'"

URL=''
if [[ -n "$ISSUE" ]]; then URL="https://github.com/$REPO/issues/$ISSUE"; fi
if [[ -n "$PR" ]]; then URL="https://github.com/$REPO/pull/$PR"; fi

if [[ -z "$ITEM" ]]; then
  ITEMS=$(gh project item-list "$PROJECT" --owner "$OWNER" --format json --limit 1000) || die 'item-list failed'
  ITEM=$(jq -r --arg url "$URL" '[.items[] | select((.content.url // "") == $url)] | if length == 1 then .[0].id else empty end' <<<"$ITEMS")
  [[ -n "$ITEM" ]] || die "project item for $URL not found uniquely in first 1000 results (or not on board)"
fi

PROJECT_JSON=$(gh project view "$PROJECT" --owner "$OWNER" --format json) || die 'project view failed'
PROJECT_ID=$(jq -r '.id // empty' <<<"$PROJECT_JSON")
[[ -n "$PROJECT_ID" ]] || die 'missing project node ID'

EDIT=(gh project item-edit --id "$ITEM" --project-id "$PROJECT_ID" --field-id "$FIELD_ID")

if (( CLEAR )); then
  EDIT+=(--clear)
elif [[ "$FIELD_TYPE" == *singleselect* || "$FIELD_TYPE" == *single_select* || "$FIELD_TYPE" == *single-select* ]]; then
  [[ -z "$KIND" ]] || die '--as is not supported for single-select fields'
  OPTION_ID=$(jq -r --arg v "$VALUE" '[.options[]? | select(.name == $v)] | if length == 1 then .[0].id else empty end' <<<"$FIELD_JSON")
  [[ -n "$OPTION_ID" ]] || die "single-select option '$VALUE' not found uniquely; inspect field-list"
  EDIT+=(--single-select-option-id "$OPTION_ID")
elif [[ "$FIELD_TYPE" == *iteration* ]]; then
  [[ -z "$KIND" ]] || die '--as is not supported for iteration fields'
  ITER_ID=$(jq -r --arg v "$VALUE" '
    [(.configuration.iterations // [])[], (.configuration.completedIterations // [])[], (.iterations // [])[]]
    | map(select(.title == $v)) | unique_by(.id) | if length == 1 then .[0].id else empty end' <<<"$FIELD_JSON")
  [[ -n "$ITER_ID" ]] || die "iteration '$VALUE' is not in field-list metadata; resolve its ID with GraphQL"
  EDIT+=(--iteration-id "$ITER_ID")
else
  # Never guess a field's type from its value. "42" can be text, not a number.
  case "$FIELD_DATA_TYPE:$FIELD_TYPE" in
    text:*|*:text*) EXPECTED=text;; number:*|*:number*) EXPECTED=number;; date:*|*:date*) EXPECTED=date;;
    *) EXPECTED='';;
  esac
  KIND=${KIND:-$EXPECTED}
  [[ -n "$KIND" ]] || die 'cannot infer field type; supply --as text|number|date'
  [[ -z "$EXPECTED" || "$KIND" == "$EXPECTED" ]] || die "field type is '$EXPECTED', not '$KIND'"
  case "$KIND" in
    number) [[ "$VALUE" =~ ^-?[0-9]+([.][0-9]+)?$ ]] || die 'number must be numeric';;
    date) [[ "$VALUE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || die 'date must be YYYY-MM-DD';;
  esac
  EDIT+=("--$KIND" "$VALUE")
fi

if (( DRY )); then
  printf 'DRY RUN: '; printf '%q ' "${EDIT[@]}"; printf '\n'
  exit 0
fi
"${EDIT[@]}"
printf 'Updated %s on item %s (project %s/%s). Verify with gh project item-list.\n' "$FIELD" "$ITEM" "$OWNER" "$PROJECT"
