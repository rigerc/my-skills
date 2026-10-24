# Serena Usage — Project-Specific Guide

Reference for [SKILL.md](../SKILL.md): the memory inventory, naming table, and update/create decision guide for the active project.

## Project-Specific Guide (Recipe Sharing System)

**Current Memory Structure (10 active memories):**

| Memory | Purpose | Notes |
|---------|---------|--------|
| `project-overview` | Project status, tech stack, next steps | Central reference, read first |
| `database-integration-implementation-plan-task` | 138-task plan v2.0 status | 38% complete (Phases 1-3 done) |
| `csx3006-sql-fixes-2026-02-13` | SQL script corrections | Keep for debugging |
| `notion-implementation-tracking` | Notion sync protocol | Update when completing tasks |
| `admin-features` | Admin workflow, moderation, user management | Feature specs only |
| `recipe-features` | Recipe CRUD, search, reviews, engagement | Feature specs only |
| `auth-context` | Session-based authentication flow | Phase 4 backend, Phase 5 integration |
| `routing-layouts` | Route configuration and page layouts | HashRouter with layout guards |
| `storage-data-model` | Pre-Phase 5 localStorage structure | Will be replaced by API |
| `ui-components-and-styling` | Component library and Tailwind v4 | Reusable components |

**Session-Start Pattern (Phase 4 — Backend Pending):**
1. `get_current_config` → verify project is activated
2. If not activated, `activate_project` with current workspace path
3. `check_onboarding_performed` → verify onboarding status
4. Complete onboarding if needed using standard workflow
5. `list_memories` → verify 10 memories available
6. Read `project-overview` → current status (38% complete, Phases 1-3 done)
7. Read `database-integration-implementation-plan-task` → Phase 4 tasks (TASK-057 to TASK-092)
8. Begin PHP backend development: `backend/config/database.php`, `backend/helpers/`, then `backend/api/`

**Project-Specific Best Practices:**

**Database Conventions:**
- Database: `cookhub` (utf8mb4_unicode_ci)
- Tables: singular (user, recipe, ingredient, etc.)
- Columns: snake_case, `id` PKs
- PK access: `WHERE id = ?` on parent tables, FK references on child tables
- FKs: `{table}_id` columns

**Architecture:**
- Plain PHP (no frameworks, no Composer)
- Structure: `backend/{config, helpers, api}/`
- Each API file handles routing via `$_SERVER['REQUEST_METHOD']`
- Auth: Session-based (HttpOnly cookies, `session` table)
- HTTP: Native `fetch()` with `credentials: 'include'`

**Documentation Flow:**
- SQL fixes → Check if `{topic}-fixes-{date}.md` exists → update OR create new memory
- Major milestones → update `project-overview.md` with new timestamp
- Phase completion → update `database-integration-implementation-plan-task.md` with progress
- Notion sync → update `notion-implementation-tracking.md` with sync status
- **ALL updates** → Include current timestamp in format: "Updated: YYYY-MM-DD HH:MM"

**Naming Patterns Used:**
- Feature memories: lowercase kebab-case (admin-features, recipe-features, auth-context)
- Fix memories: `{name}-fixes-{date}.md`
- Status memories: `{project}-updates.md` or `{plan}-task.md`

---

## Memory Reference Table (CSX3006 Project)

| Category | Memory Name | Update Frequency | When to Read |
|----------|---------------|------------------|--------------|
| **Status & Plan** | `project-overview` | After phase completion, architecture decisions | Always first when starting session |
| **Task Tracking** | `database-integration-implementation-plan-task` | After phase completion | When starting backend/frontend work |
| **SQL Fixes** | `csx3006-sql-fixes-2026-02-13.md` | When fixing database issues | During SQL/database work |
| **Notion Sync** | `notion-implementation-tracking` | When Notion sync pattern changes | Before updating Notion pages |
| **Feature Specs** | `admin-features`, `recipe-features`, `auth-context` | Feature changes/improvements | Implementing related features |
| **Reference** | `routing-layouts`, `storage-data-model`, `ui-components-and-styling` | Rarely changes | Quick lookup for these topics |

## Scripts
- [Memory Backup](./scripts/serena-memory-backup.ps1) — PowerShell script to backup Serena memory files with timestamps

## Examples
- [Refactoring Workflow](./examples/refactoring-workflow.md) — 13-step refactoring walkthrough using Serena tools

---

## Memory Management Strategy for This Project

**Why 10 memories (not 15 from Memory Bank standard):**
- Project tracks implementation plan via `plan/upgrade-database-integration-1.md` (138 tasks) instead of task memories
- No individual `task-{id}` memories needed (tasks are in plan file)
- No `task-index` or `progress` memories (status in `project-overview.md`)
- Feature specs kept concise (admin-features, recipe-features, auth-context at ~500 bytes each)
- One-line reference memories for quick lookups (routing-layouts, storage-data-model, ui-components-and-styling)

**When to create new memories:**
- SQL/script fixes: `{topic}-fixes-{date}.md` (e.g., csx3006-sql-fixes-2026-02-13.md)
- Feature documentation: `{feature-name}.md` (e.g., admin-features.md)
- Major milestones: Update `project-overview.md` (status changes, architecture decisions)

**When NOT to create memories:**
- Individual tasks (use `upgrade-database-integration-1.md` task list)
- Everyday progress (project status tracked in `project-overview.md`)
- Code samples (code is in actual files, not memories)
- Historical one-time events (delete when obsolete)
- **INFORMATION THAT SHOULD UPDATE AN EXISTING MEMORY instead of creating a new one**

---

## Memory Update vs Creation Quick Reference

## Decision Tree

```
Need to store information?
│
├─ Check: `list_memories`
│  │
│  ├─ Existing memory covers this topic?
│  │  │
│  │  ├─ YES → Use `edit_memory` with new info + updated timestamp
│  │  │
│  │  └─ NO → Use `write_memory` to create new memory
│  │
│  └─ Proceed with work
```

## Common Match Patterns

| When adding info about... | Check memory... | If exists... | If not... |
|--------------------------|-----------------|--------------|-----------|
| Admin features/moderation | `admin-features` | Update it | Create `admin-features` |
| Recipe CRUD/search | `recipe-features` | Update it | Create `recipe-features` |
| Authentication/session | `auth-context` | Update it | Create `auth-context` |
| SQL fixes today | `{topic}-fixes-{date}` | Update it | Create new with today's date |
| Architecture decisions | `system-patterns` | Update it | Create `system-patterns` |
| Overall project status | `project-overview` | ALWAYS update it | Create `project-overview` |
| Component specs | `ui-components-and-styling` | Update it | Create if different topic |

## Edit Memory Pattern

```bash
# Always use this format when updating existing memories
edit_memory(
  memory_file_name="existing-memory-name",
  needle="section or content to replace or append after",
  repl="new information with timestamp:\n\n## [Section] — Updated YYYY-MM-DD HH:MM\n\n- [new info]",
  mode="literal" # or "regex" as appropriate
)
```
