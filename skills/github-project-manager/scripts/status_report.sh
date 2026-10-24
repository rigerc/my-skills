#!/usr/bin/env bash
# Read-only, noninteractive GitHub issue/PR/milestone status summary.
set -euo pipefail
usage() {
  cat <<'EOF'
Usage: status_report.sh [-R OWNER/REPO] [--days N] [--stale N]
  -R, --repo  Repo (default: current checkout)
  --days      Days in completed-work window (default 7)
  --stale     Days since issue update for stale section (default 14)
This is a GitHub snapshot, NOT a T3 delegated-task status report.
EOF
}
die() { printf 'error: %s\n' "$*" >&2; exit 1; }
REPO='' DAYS=7 STALE=14
while (( $# > 0 )); do
  case "$1" in
    -R|--repo) [[ $# -ge 2 ]] || die "missing value for $1"; REPO=$2; shift 2;;
    --days) [[ $# -ge 2 ]] || die "missing value for $1"; DAYS=$2; shift 2;;
    --stale) [[ $# -ge 2 ]] || die "missing value for $1"; STALE=$2; shift 2;;
    -h|--help) usage; exit 0;;
    *) die "unknown argument: $1";;
  esac
done
command -v gh >/dev/null || die 'gh is not installed'
command -v jq >/dev/null || die 'jq is not installed'
[[ "$DAYS" =~ ^[0-9]+$ && "$STALE" =~ ^[0-9]+$ ]] || die '--days and --stale must be non-negative integers'
if [[ -z "$REPO" ]]; then
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner) || die 'not in a GitHub repo: pass -R OWNER/REPO'
fi
[[ "$REPO" =~ ^[[:alnum:]_.-]+/[[:alnum:]_.-]+$ ]] || die 'repo must be OWNER/REPO'
SINCE=$(date -u -d "-$DAYS days" +%F 2>/dev/null || date -u -v-"$DAYS"d +%F) || die 'cannot calculate date window'
TODAY=$(date -u +%FT%TZ)

# Fail closed: do not print a plausible partial report after a gh read error.
ISSUES=$(gh issue list -R "$REPO" --state open --limit 500 --json number,title,url,assignees,labels,updatedAt,milestone) || die 'cannot read open issues'
PRS=$(gh pr list -R "$REPO" --state open --limit 500 --json number,title,url,author,isDraft,reviewDecision,updatedAt) || die 'cannot read open PRs'
CLOSED=$(gh issue list -R "$REPO" --state closed --search "closed:>=$SINCE" --limit 200 --json number,title,url) || die 'cannot read closed issues'
MERGED=$(gh pr list -R "$REPO" --state merged --search "merged:>=$SINCE" --limit 200 --json number,title,url) || die 'cannot read merged PRs'
# The REST pagination can return all pages. slurp produces an array of page arrays.
MILESTONES=$(gh api --paginate --slurp "repos/$REPO/milestones?state=open&per_page=100") || die 'cannot read milestones'

printf '# GitHub status: %s\n_Generated %s · closed/merged since %s (UTC)._\n\n' "$REPO" "$TODAY" "$SINCE"
printf '## Backlog\n'
jq -r '"- Open issues (in first 500): **\(length)**\n- Unassigned: **\([.[] | select((.assignees | length) == 0)] | length)**\n- Unlabeled: **\([.[] | select((.labels | length) == 0)] | length)**"' <<<"$ISSUES"
printf '\n### Stale issues (older than %s days, up to 15 shown)\n' "$STALE"
STALE_ITEMS=$(jq -r --argjson d "$STALE" '
  [.[] | select((now - (.updatedAt | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601)) >= ($d * 86400))]
  | sort_by(.updatedAt) | .[:15][] | "- [#\(.number) \(.title)](\(.url)) · last update \(.updatedAt[:10])"' <<<"$ISSUES")
printf '%s\n\n' "${STALE_ITEMS:-_None in fetched results_}"

printf '## Pull requests\n'
jq -r '"- Open PRs (in first 500): **\(length)**\n- Drafts: **\([.[] | select(.isDraft == true)] | length)**"' <<<"$PRS"
printf '\n### Ready for review (up to 15 shown)\n'
WAITING=$(jq -r '[.[] | select((.isDraft | not) and ((.reviewDecision // "") == "REVIEW_REQUIRED" or (.reviewDecision // "") == ""))] | .[:15][] | "- [#\(.number) \(.title)](\(.url))"' <<<"$PRS")
printf '%s\n\n' "${WAITING:-_None in fetched results_}"
printf '### Changes requested (up to 15 shown)\n'
CHANGES=$(jq -r '[.[] | select(.reviewDecision == "CHANGES_REQUESTED")] | .[:15][] | "- [#\(.number) \(.title)](\(.url))"' <<<"$PRS")
printf '%s\n\n' "${CHANGES:-_None in fetched results_}"

printf '## Closed issues since %s\n' "$SINCE"
CLOSED_LIST=$(jq -r '.[] | "- [#\(.number) \(.title)](\(.url))"' <<<"$CLOSED")
printf '%s\n\n' "${CLOSED_LIST:-_None in fetched results_}"
printf '## Merged pull requests since %s\n' "$SINCE"
MERGED_LIST=$(jq -r '.[] | "- [#\(.number) \(.title)](\(.url))"' <<<"$MERGED")
printf '%s\n\n' "${MERGED_LIST:-_None in fetched results_}"

printf '## Open milestones\n'
MILESTONE_LIST=$(jq -r '.[][] | "- **\(.title)**: \(.closed_issues)/\(.closed_issues + .open_issues) closed" + (if .due_on then " · due \(.due_on[:10])" else "" end)' <<<"$MILESTONES")
printf '%s\n\n' "${MILESTONE_LIST:-_None_}"

WARNINGS=''
for pair in 'open issues:500' 'open PRs:500' 'recently closed issues:200' 'recently merged PRs:200'; do
  kind=${pair%%:*}; cap=${pair##*:}
  case "$kind" in
    'open issues') n=$(jq 'length' <<<"$ISSUES");;
    'open PRs') n=$(jq 'length' <<<"$PRS");;
    'recently closed issues') n=$(jq 'length' <<<"$CLOSED");;
    'recently merged PRs') n=$(jq 'length' <<<"$MERGED");;
  esac
  if (( n >= cap )); then WARNINGS+="- $kind reached its $cap-record limit; counts may be incomplete.\n"; fi
done
printf '## Report scope\n'
printf -- '- GitHub-only snapshot; does not query T3 orchestration status or guarantee passing CI.\n'
if [[ -n "$WARNINGS" ]]; then printf '%b' "$WARNINGS"; fi
