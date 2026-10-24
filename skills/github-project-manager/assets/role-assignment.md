# Role-to-provider/model assignment (fill before delegation)

**Repository / issue(s):** <OWNER/REPO, URLs>  
**Coordinator:** parent T3 agent (not a child role)  
**Available choices:** <copy real provider display names, providerInstanceIds, model IDs and relevant advertised options from `orchestrator_capabilities`>

Ask the user:

> **Which provider and model should I use for the active roles below?** You can choose one pair for every role, specify separate pairs per role, or explicitly request "inherit parent". Tell me if you want particular advertised model options. I won't launch a child until its role has a valid selection.

| Active? | Role | Provider instance (`providerInstanceId` or explicit inherit) | Model ID (or explicit inherit) | Advertised options, if chosen | User-confirmed? |
| --- | --- | --- | --- | --- | --- |
| <yes/no> | `research` | <selection> | <selection> | <selection/none> | <yes/no> |
| <yes/no> | `design` | <selection> | <selection> | <selection/none> | <yes/no> |
| <yes/no> | `implementation` | <selection> | <selection> | <selection/none> | <yes/no> |
| <yes/no> | `test` | <selection> | <selection> | <selection/none> | <yes/no> |
| <yes/no> | `review` | <selection> | <selection> | <selection/none> | <yes/no> |
| <yes/no> | `general` (exception) | <selection> | <selection> | <selection/none> | <yes/no> |

**Gate:** every active row has an explicit choice or the user has instructed the coordinator to choose and that choice is validated. An omitted value is **not** permission to inherit. Read-only GitHub planning may proceed while selection is pending; no `delegate_task` dispatch may proceed for an unassigned role. Newly introduced roles or provider/model substitutions require a new choice.
