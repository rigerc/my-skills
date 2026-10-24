---
name: serena-usage
version: "2.0"
last_updated: 2026-09-08
tags: [serena, usage, workflow, automation, guidance]
description: "Serena MCP for project memory and code navigation. Use when managing Serena memories, navigating symbols, performing intelligent refactoring, or maintaining context/continuity across AI agent sessions."
---
# Serena Usage

Effective usage of the Serena MCP Server for project memory management, code intelligence, and maintaining continuity across AI agent sessions.

- Leverage native parallel subagent dispatch and 200k+ context windows where available.



## Activation Conditions

Use symptom -> action triggers: when one matches, apply this skill and verify with the protocol below.

**MUST activate when:**
- Serena is available for the project
- Task requires project memory continuity
- Task requires symbol navigation or Serena refactoring workflow
- Managing project memories for AI session continuity
- Navigating codebases using symbol-based tools
- Performing code refactoring with Serena's symbol management
- Setting up Serena onboarding for new projects
- Using Serena's memory system for project context preservation

**Critical: Always verify project activation FIRST with `get_current_config` before any Serena operations**

## Prerequisites

- Serena MCP Server configured and running
- Project activated (use `get_current_config` to verify, or `activate_project` if not activated)
- Onboarding completed for the target project (use `check_onboarding_performed` first)
- If not activated, run `activate_project` with project name or path
- If not onboarded, run `onboarding` tool after activation

---

## Onboarding Workflow

### First-Time Project Setup
1. **Check activation**: Call `get_current_config` to verify if project is activated
2. **Activate if needed**: If not activated, call `activate_project` with project name or path
3. **Check onboarding**: Call `check_onboarding_performed` to verify onboarding status
4. **Read manual**: If not onboarded, call `initial_instructions` to read the Serena Instructions Manual
5. **Initialize**: Call `onboarding` to complete project setup
6. Serena analyzes the project structure and creates initial context

### What Onboarding Captures
- Project language and framework detection
- Directory structure analysis
- Key file identification
- Symbol index creation
- Initial memory scaffolding

### Activation Check Pattern
```bash
# Always verify activation first
get_current_config
# If no active project, activate it
activate_project project="path/to/project"
# Then proceed with onboarding check
check_onboarding_performed
```

## Project Activation

### Why Activation Matters
Project activation is the first step when working with Serena. It tells Serena which project to work with and initializes the workspace context.

### Activation Workflow
1. **Check current status**: Call `get_current_config` to see if a project is already activated
2. **Activate if needed**: If no active project, call:
   ```
   activate_project project="project-name"
   # OR with path:
   activate_project project="path/to/project/directory"
   ```
3. **Verify activation**: Call `get_current_config` again to confirm activation succeeded
4. **Proceed with onboarding**: Once activated, check if onboarding is needed

### Activation Best Practices
- Always check `get_current_config` before attempting any Serena operations
- Use the workspace root path when activating
- Activation is session-specific — you may need to reactivate in new sessions
- After activation, the project context is available for all subsequent Serena operations

---

## Memory Management

### Core Concepts
Serena memories persist between sessions, providing continuity for AI agents across work sessions.

### Memory Operations

| Operation | Tool | Purpose |
|-----------|------|---------|
| List all | `list_memories` | See available memories |
| Read one | `read_memory` | Access specific memory content |
| Create | `write_memory` | Store new information |
| Update | `edit_memory` | Modify existing memory |
| Remove | `delete_memory` | Clean up obsolete information |

### Memory Structure

Serena memories use the Memory Bank naming convention for consistency and clarity. This structure organizes project intelligence into core files and tasks.

#### Core Files

| Memory Name | Purpose |
|-------------|---------|
| `project-brief` | Foundation document defining core requirements and goals. Shapes all other memories. Created at project start. |
| `product-context` | Why this project exists, problems it solves, how it should work, and user experience goals |
| `active-context` | Current work focus, recent changes, and next steps with active decisions and considerations |
| `system-patterns` | System architecture, key technical decisions, design patterns in use, and component relationships |
| `tech-context` | Technologies used, development setup, technical constraints, and dependencies |
| `progress` | What works, what's left to build, current status, and known issues |

#### Task Management Memories

Tasks are managed with dedicated memory files for tracking progress and history.

| Memory Name | Purpose |
|-------------|---------|
| `task-{id}` | Individual task tracking (e.g., TASK001-implement-login.md) with original request, thought process, implementation plan, and progress logs |
| `task-index` | Master list of all tasks with IDs, names, statuses (Pending/In Progress/Completed/Abandoned), and last updated dates |

#### Templates And Write Guidelines

The task-memory template, the memory-write templates, the update patterns, and the full memory creation workflow live in [memory-templates](./references/memory-templates.md). Read it before creating or rewriting a memory file.

---

## Code Navigation

### Symbol-Based Navigation

| Tool | Use Case |
|------|----------|
| `find_symbol` | Locate specific classes, functions, variables by name path |
| `find_referencing_symbols` | Find all usages of a symbol across the codebase |
| `get_symbols_overview` | High-level summary of symbols in a file |

### Navigation Workflow
1. Use `get_symbols_overview` on a file to understand its structure
2. Use `find_symbol` to locate a specific definition
3. Use `find_referencing_symbols` to understand impact before changes

---

## Code Refactoring

### Safe Refactoring with Serena

| Tool | Operation |
|------|-----------|
| `rename_symbol` | Rename across all references |
| `replace_symbol_body` | Replace implementation of a function/method |
| `insert_after_symbol` | Add new code after a definition |
| `insert_before_symbol` | Add new code before a definition |

### Refactoring Workflow
1. **Understand**: Use `find_symbol` and `get_symbols_overview`
2. **Assess Impact**: Use `find_referencing_symbols` to see all usages
3. **Plan**: Think through the changes needed
4. **Execute**: Use rename/replace/insert tools
5. **Verify**: Re-check references to confirm correctness
6. **Document**: Update memories with the change rationale

---

## File Search

| Tool | Purpose |
|------|---------|
| `find_file` | Locate files matching a name pattern |
| `list_dir` | Browse directory contents |
| `search_for_pattern` | Search for text/regex patterns across codebase |

---

## Task Adherence

Serena provides reflection tools to maintain focus:

| Tool | When to Use |
|------|------------|
| `think_about_collected_information` | After gathering context — is it sufficient? |
| `think_about_task_adherence` | After many interactions — am I still on track? |
| `think_about_whether_you_are_done` | Before concluding — have I completed everything? |

---

## Session Workflow

### Starting a Session
1. **Verify activation**: `get_current_config` → check if project is activated
2. **Activate if needed**: If no active project, `activate_project` → activate the workspace
3. **Check onboarding**: `check_onboarding_performed` → verify onboarding status
4. Complete onboarding if needed using onboarding workflow
5. `list_memories` → review all 10 available project memories
6. `read_memory` → load relevant memories for current work phase:
   - **Always:** Read `project-overview` (current status, tech stack, next steps)
   - **Phase 4 (Backend):** Read `database-integration-implementation-plan-task` (TASK-057 to TASK-092)
   - **Feature work:** Read specific feature memory (admin-features, recipe-features, auth-context)
   - **SQL work:** Read `csx3006-sql-fixes-2026-02-13.md` (column conventions, FK patterns)
   - **Notion sync:** Read `notion-implementation-tracking.md` (update protocol)
7. Begin work with current phase context

### During a Session
- **SQL/database work:** Check if `{topic}-fixes-{date}.md` exists → update OR create new memory for bug fixes
- **Feature implementation:** Check if `{feature-name}.md` exists → update OR create new memory for feature specs
- **Phase completion:** Update `project-overview.md` with new status percentage and current timestamp
- **Notion updates:** Use `notion-update-page` after completing plan tasks (TASK-001 → TASK-138)
- **Code navigation:** Use symbol tools to explore React components and future PHP backend files
- **NEW information flow:**
  1. Use `list_memories` to review all existing memories
  2. Identify if any existing memory covers the topic
  3. If relevant memory exists: Use `edit_memory` with new information + updated timestamp
  4. If no relevant memory: Use `write_memory` to create new memory

---

## Best Practices

- **ALWAYS check activation before any Serena operations using `get_current_config`**
- **ALWAYS check for relevant existing memories with `list_memories` before creating new ones**
- **CRITICAL: Use `edit_memory` to update existing memories with new timestamp rather than creating duplicates**
- Activate project first if not already activated using `activate_project`
- Check onboarding after activation, before first use on a project
- Keep memories concise — prefer structured data over prose
- Update memories incrementally, not in bulk rewrites
- Use consistent naming for memories across projects (Memory Bank convention)
- Leverage `think_about_*` tools for self-reflection on complex tasks
- For task tracking: Always update both subtask table AND progress log in task memories
- Keep `task-index` synchronized with task memory status changes
- Delete obsolete memories to prevent confusion
- Use task IDs from `task-index` as reference when discussing work
- When adding information to existing memories, update timestamp to YYYY-MM-DD HH:MM format

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Project not activated | Run `get_current_config` to verify, then `activate_project` with project path |
| Onboarding not detected | After activation, run `onboarding` tool explicitly |
| Memory not found | Check exact name with `list_memories` |
| Symbol not found | Ensure file is indexed; try broader name |
| Stale memories | Use `edit_memory` to update with current state and timestamp |
| Conflicting memories | Delete outdated entry, merge into single memory with consolidated content |
| Duplicate memories | Avoid by ALWAYS checking `list_memories` before creating new ones; use `edit_memory` to update existing |
| Unsure which memory to update | Use `list_memories` → review purpose of each → read relevant memories → update the most appropriate one |

---

<!-- MCP:START -->

<!-- PORTABILITY:START -->
## Cross-Client Portability

This skill is written to stay usable across GitHub Copilot, Claude Code, and Codex.

- GitHub Copilot: keep the folder in a Copilot-visible skill path or wrap the
  workflow in project instructions when folder discovery is unavailable.
- Claude Code: keep the folder in a local skills directory or a compatible plugin source.
- Codex: install or sync the folder into
  `$CODEX_HOME/skills/serena-usage` and restart Codex after major changes.

<!-- PORTABILITY:END -->

## MCP Availability And Fallback

Preferred MCP Server: Serena MCP

- Fallback prompt: "Use the Serena Usage skill without MCP. Follow the documented local or manual fallback, show the selected tool surface, and report the verification evidence."
- Use `rg`, `git diff`, targeted file reads, and local Markdown memory files when Serena is unavailable.
- Keep a lightweight Memory Bank in repo docs or notes so project continuity still survives across sessions.
- Do not claim an MCP operation was used when the active host does not expose it.

<!-- MCP:END -->

## Anti-Patterns

- Starting without a clear success condition: The skill becomes advice-shaped instead of workflow-shaped.
- Skipping the bundled references or scripts: You lose the proven path the catalog is trying to preserve.
- Claiming completion without concrete evidence: A future agent or reviewer cannot trust the result or resume the work safely.

## Verification Protocol

Before claiming "skill applied successfully":

1. Pass/fail: The Serena Usage workflow names the agent boundary, delegated scope, and expected return artifact.
2. Pass/fail: Context passed to helpers is minimal, task-local, and free of hidden expected answers.
3. Pass/fail: Results are integrated only after evidence, diffs, or citations are checked by the controller.
4. Pressure-test scenario: Run the workflow on two similar tasks that must not share assumptions or leaked context.
5. Success metric: Zero context leakage; every delegated output is independently reviewable.

## References & Resources

### Documentation
- [Memory Management](./references/memory-management.md) — Memory naming conventions, lifecycle, and maintenance best practices
- [Symbol Navigation](./references/symbol-navigation.md) — find_symbol and find_referencing_symbols patterns and workflows

The memory inventory, naming table, and update/create decision guide for the active project live in [project-specific-guide](./references/project-specific-guide.md). Read it before touching project memories.
