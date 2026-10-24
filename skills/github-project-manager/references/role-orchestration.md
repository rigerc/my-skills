# Role-based orchestration and provider/model selection

The **parent coordinator** manages GitHub planning, assignments, dependencies, approvals, and integration. Child agents own bounded role-specific deliverables, not the whole project. T3's `delegate_task.role` is an execution label and does **not** choose a provider, model, workspace, or permission mode automatically.

## 1. Mandatory pre-dispatch provider/model question

**Do not call `delegate_task` until the user has chosen provider/model handling for every role being dispatched.** This gate applies at the start of each new delegation plan, not to purely read-only `gh` work that needs no child. The parent must:

1. Identify the **active roles** required by the request (not all possible roles), dependencies and anticipated number of children. Present a compact role map so the user knows what is being assigned.
2. Call live `orchestrator_capabilities` in the actual T3 parent session. Display concrete `displayName`/`providerInstanceId`, supported `models[].id`, relevant options and any constraints for providers with `canRunChildTask: true`. Use `orchestrator_capabilities({"search":"<user model term>"})` if a requested model is absent from the short list; `omittedModels` means the default list is not exhaustive. Do not invent provider/model IDs or imply an unlisted provider is configured.
3. Ask one direct question, for example:

   > **Which provider and model should handle each role?** You can give **one provider + model for all roles**, or overrides for **research, design, implementation, test, and review**. You may explicitly say **"inherit the parent"** for a role. Should I apply any of the available model options? I will not dispatch agents until the mapping is clear.

4. Accept **one pair for all active roles**, **a per-role mapping**, or **an explicit instruction for the coordinator to choose**. If a user already specified a complete mapping, don't ask again; still validate against live capabilities. If only part is specified, ask about the missing active roles before dispatching them. Do **not** treat an omitted model/role as implicit consent to inherit defaults, and do **not** add a preset model preference. Treat `inherit parent` as an explicit choice and validate the inherited provider/model can run the intended child task.
5. When a chosen pair is unavailable or constrained, explain the specific incompatibility and **ask the user for a replacement** (unless they expressly delegated the choice to the coordinator). It is fine to finish read-only planning while awaiting the mapping; **do not dispatch**.
6. Resolve each approved selection to a real `providerInstanceId` and `models[].id`; optionally validate advertised option IDs/values. Persist the choices in the session's role map; re-check capabilities immediately before dispatch when stale. Ask again when new roles are introduced or an assignment must change, but not on every task if an existing explicit mapping still applies.

Use [role assignment worksheet](../assets/role-assignment.md) as a concise operator checklist, not a requirement to expose a large form.

## 2. Role contract and handoff gates

| Role | Responsible for | Deliverable and exit gate | Boundary |
| --- | --- | --- | --- |
| **Parent coordinator** (no `role` field) | Backlog and dependency graph; provider/model selection; scoped brief dispatch; task/PR ledger; approvals and GitHub reconciliation | Prioritized work plan, accepted assignment map, verified stage results and handoffs | Does not claim child completion is CI approval or merging; human authorization still governs writes |
| `research` | Investigate issue, repository constraints, dependencies, reproducibility | Evidence-backed investigation, unknowns, proposed acceptance criteria and tests | No code, issue or board writes; do not decide implementation scope for the user |
| `design` | Architecture, interfaces, UX / technical approach when genuinely needed | Design proposal with trade-offs, affected files and acceptance tests, approved/accepted by parent as appropriate | Design-only unless a separately authorized editing brief exists |
| `implementation` | Build one independent vertical slice within allowed paths | Reviewable commit/branch, changed paths, test commands/results, exact acceptance mapping | No merge, release, deploy, broad status edits or shared parallel file ownership |
| `test` | Independent verification against implementation artifact and acceptance criteria | Test evidence, results, coverage gaps, reproductions and failures tied to immutable SHA/PR | No rewriting implementation; no self-approval |
| `review` | Independent review of security, design conformance, correctness and regressions | Findings with severity and file/line evidence, verdict and unresolved objections | Read-only; cannot approve, merge or certify without verified evidence |
| `general` | One explicitly unclassified bounded task | Named artifact and independent verification criteria | Not an automatic fallback when a selected specialist/model is unavailable |

### Dependency-aware workflow

1. **Intake/plan:** coordinator inspects GitHub and repository policies, selects the *minimum necessary roles*, sizes work, defines ownership and dependency edges. Pure triage may end here without delegation/model selection.
2. **Discovery:** `research` and/or `design` receive read-only focused briefs when needed. Coordinator checks output, resolves ambiguous acceptance criteria with the user where material, and produces a confirmed implementation contract.
3. **Build:** `implementation` receives a sealed, self-contained brief: base committed SHA, owned paths, isolation mode, exact scope and tests. Limit active writers to 2–3 nonoverlapping worktrees by default; serialize if safe isolation is unavailable. Return actual commits and branch info.
4. **Verify:** once candidate commit/PR is known, `test` and `review` independently inspect **the same identified artifact**. They can run concurrently if no file writes/conflicting resources. Each receives acceptance criteria and provenance, not just implementation's self-report. No review role may self-certify its own changes.
5. **Rework:** coordinator routes actionable test/review findings back to `implementation` as a bounded follow-up with fresh attempt identity where appropriate; once a new candidate SHA exists, commission new independent verification/review rounds with fresh IDs and previous findings included.
6. **Integrate:** coordinator verifies GitHub PR state, CI, human review and branch protection, records what is actually done, and seeks authorization for merge/release/board mutations as required. Update the ledger and report remaining blockers.

Small or noncode requests may legitimately omit design, research, implementation or either verification role; do not invent needless children. Existing mandatory repo checks still apply. Stage completion is a **handoff**, not permission to perform a privileged GitHub action.

## 3. Dispatch contract: role paired to explicit target

Use the exact installed MCP schema as source of truth. For a configured pair, T3's current contract allows:

```json
{
  "title": "Implement issue #42",
  "role": "implementation",
  "target": {
    "providerInstanceId": "<real instance ID from capabilities>",
    "model": "<real model ID for that instance>"
  },
  "isolation": "worktree",
  "mode": "async",
  "clientRequestId": "pm-owner-repo-42-implementation-r1",
  "task": "<self-contained role-specific brief with permissions, paths, acceptance criteria and test plan>"
}
```

This JSON is **illustrative**, not a command or a valid dispatch until placeholders are replaced and live tool support is confirmed. Set `target.options` only to explicitly selected, advertised settings. If the user **explicitly chose inherit parent**, omit `target` (including for that role only); record that inheritance decision. Validate after dispatch that returned `providerInstanceId`, `model` and `options` match expectations. On mismatch, do not quietly accept it as the chosen assignment: report the issue and stop any further dispatch to that target until resolved. Do not cancel automatically if work is already running without considering consequences.

A selection for a **role** applies to all its tasks in this plan unless the user changes it. Keep retry IDs identical for a retry of the **same request**, and use a new ID for a new attempt or independent review. If a requested model cannot execute a child, ask the user to choose another; never substitute a provider, model, option or a native subagent without consent. Runtime mode inherits by default; changing permissions requires separate authorization.

## 4. Role-aware ledger

At minimum, track:

| Issue / artifact | Role | Selected provider instance | Selected model | Options / inherit? | Actual provider + model | Attempt / taskId / childThreadId | Base / commit / PR | State / verification / next owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #42 | implementation | selected ID | selected model ID | explicit option set | returned ID + model | r1 / actual returned IDs | actual SHA/PR | running / test next |

Record **actual** observed GitHub status separately from the child's lifecycle state. Never fabricate identifiers or silently persist the mapping to GitHub without authorization. Pass the selected role, scope and acceptance handoff context to each child, because T3 children do not inherit the parent's chat history.
