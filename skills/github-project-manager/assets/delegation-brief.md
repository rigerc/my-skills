# Delegation brief for issue #<N>

> Insert this entire brief into T3 `delegate_task.task`. T3 child agents do **not** automatically inherit parent chat history.

**Role:** <research | design | implementation | test | review | general>
**Selected provider instance:** <real providerInstanceId from `orchestrator_capabilities`, or user-chosen inherit>
**Selected model:** <real model ID from the matching provider, or user-chosen inherit>
**Selected model options:** <advertised values if user chose them; otherwise none/inherited>
**Role handoff:** <upstream role artifact/decision; downstream verification role or coordinator gate>
**Repository:** <OWNER/REPO and workspace path>
**Issue:** <issue URL>
**Base:** <branch/commit; whether worktree isolation applies>
**Objective:** <one bounded deliverable>

## Background / decisions
<Relevant design decisions, constraints, earlier attempts, and links; no secrets>

## Scope and non-goals
- Do: <specific boundaries>
- Do not: <anything excluded, conflicting files, risky external actions>

## Acceptance and verification
- [ ] <criterion #1>
- [ ] <criterion #2>
- [ ] Run: `<repo-specific commands>`

## Role-specific boundaries
- <Explicit role deliverable and exit gate from references/role-orchestration.md>
- <Read-only for research/review; approved scoped code for implementation; independent evidence for test>

## Collaboration rules
- Respect repository AGENTS.md / CLAUDE.md / CONTRIBUTING.md and branch protections.
- Do not merge, deploy, close issues, rewrite the roadmap, or broaden permissions.
- If blocked or needing approval, raise a specific question rather than silently guessing.
- Do not change files owned by a parallel agent unless coordinated.
- Keep changes narrowly scoped; provide a reviewable branch / PR only if authorized.

## Return format
1. Status: completed / blocked / partial / failed (with reason).
2. Summary of actual work and paths changed.
3. Branch, commit SHA, worktree details, PR URL (if any).
4. Commands/tests run and exact results; state what was not run.
5. Acceptance checklist with evidence, review findings, risks and open questions.
