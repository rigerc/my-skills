# Serena Usage — Memory Templates And Write Guidelines

Reference for [SKILL.md](../SKILL.md): the task-memory template, the memory write templates, and the full memory creation workflow.

### Task Memory Structure

Each task memory follows this format:

```markdown
# [Task ID] - [Task Name]

**Status:** [Pending/In Progress/Completed/Abandoned]
**Added:** [Date Added]
**Updated:** [Date Last Updated]

## Original Request
[The original task description as provided by the user]

## Thought Process
[Documentation of the discussion and reasoning that shaped the approach]

## Implementation Plan
- [Step 1]
- [Step 2]
- [Step 3]

## Progress Tracking

**Overall Status:** [Not Started/In Progress/Blocked/Completed] - [Completion Percentage]

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | [Subtask description] | [Complete/In Progress/Not Started/Blocked] | [Date] | [Relevant notes] |

## Progress Log
### [Date]
- Updated subtask 1.1 status to Complete
- Started work on subtask 1.2
- Encountered issue with [specific problem]
- Made decision to [approach/solution]
```

### Task Index Structure

The task-index memory maintains a structured record:

```markdown
# Tasks Index

## In Progress
- [TASK003] Implement user authentication -Working on OAuth integration
- [TASK005] Create dashboard UI -Building main components

## Pending
- [TASK006] Add export functionality -Planned for next sprint

## Completed
- [TASK001] Project setup -Completed on 2025-03-15
- [TASK002] Create database schema -Completed on 2025-03-17
```

### Commands

When you request **add task** or **create task**, the agent will:
1. Create a new task memory with a unique Task ID
2. Document the thought process about the approach
3. Develop an implementation plan
4. Set an initial status
5. Update the task-index memory

To view tasks, the command **show tasks [filter]** will display filtered lists with valid filters:
- **all** - Show all tasks regardless of status
- **active** - Show only "In Progress" tasks
- **pending** - Show only "Pending" tasks
- **completed** - Show only "Completed" tasks
- **blocked** - Show only "Blocked" tasks
- **recent** - Show tasks updated in the last week

## When to Update Memories

**Update core memories when:**
- After completing significant features or functionality
- When making architectural decisions
- Discovering new project patterns or conventions
- Changing technical stack or dependencies
- Modifying data models or schemas
- At the start and end of each work session

**Update task memories when:**
- Creating new tasks via "create task" command
- Making progress on existing tasks
- Completing subtasks or entire tasks
- Encountering blockers or issues
- Changing task status (Pending → In Progress → Completed/Abandoned)

## Memory Creation Workflow

**CRITICAL: ALWAYS check for relevant existing memories before creating new ones**

### Step-by-Step Process

1. **List available memories**: Use `list_memories` to see all existing memories
2. **Analyze relevance**: Identify if any existing memory covers the same topic/concept
3. **Check memory content**: If relevant memories found, use `read_memory` to examine their content
4. **Match criteria**:
   - Same feature/technology/topic domain
   - Overlapping purpose or scope
   - Related architectural decisions
   - Similar problem space or concern
5. **Decision**:
   - **IF relevant memory exists**: Update the existing memory using `edit_memory` with new information and current timestamp
   - **IF no relevant memory exists**: Create new memory using `write_memory`

### Matching Guidelines

A new memory entry is relevant to an existing memory if:

| Criteria | Example |
|----------|---------|
| Same feature area | "admin-features" already covers admin workflows → add new admin task details to it |
| Same technology | "auth-context" already covers authentication → add new auth implementation details to it |
| Related architecture | "system-patterns" covers architecture decisions → add new architectural choices to it |
| Same domain concern | "ui-components-and-styling" covers component library → add new component specs to it |
| Project-wide update | "project-overview" covers overall status → add general project updates to it |

### Update Pattern for Existing Memories

When updating existing memories, follow this structure:

```markdown
## {Topic} — Updated [YYYY-MM-DD HH:MM]

### [Date] - Update
- [New information or decision]
- [Implementation details or findings]
- [Related changes or impacts]
- [Next actions or considerations]

### Previous Context
[Preserve existing relevant information]
```

### Examples of Memory Consolidation

**Scenario 1: Adding new admin feature specs**
```
Existing: admin-features.md (500 bytes)
New info: New user moderation workflow specs
Action: Update admin-features.md with new section, update timestamp
```

**Scenario 2: Fixing SQL bug**
```
Existing: csx3006-sql-fixes-2026-02-13.md
New info: Another SQL bug related to same issue
Action: Update csx3006-sql-fixes-2026-02-13.md, add new fix details, update timestamp
```

**Scenario 3: New authentication implementation detail**
```
Existing: auth-context.md
New info: Session management implementation specifics
Action: Update auth-context.md with new implementation section, update timestamp
```

**Scenario 4: New database-fix memory for different issue**
```
Existing: csx3006-sql-fixes-2026-02-13.md (column name fixes)
New info: Index optimization fixes (different topic)
Action: Create NEW memory: csx3006-index-fixes-2026-02-16.md
```

### When to Create New Memories

Create a NEW memory only when:

- **Different domain**: Topic is fundamentally different from existing memories
- **Major milestone**: New phase or significant project shift
- **New technology stack**: Unrelated to existing technical context
- **Time-based tracking**: Fix memories, daily updates, or dated logs
- **Overwhelming size**: Existing memory would exceed 5-10 KB with additions

**Examples of when to create new memories:**
```
Existing: admin-features.md
New: Performance analysis reports → Create NEW: performance-analysis.md

Existing: ui-components-and-styling.md
New: Mobile responsiveness specifications → Create NEW: mobile-responsive.md

Existing: csx3006-sql-fixes-2026-02-13.md (database schema corrections)
New: API endpoint bug fixes → Create NEW: api-fixes-2026-02-16.md
```

## Memory Bank Documentation Guidelines

The Serena memories follow the Memory Bank structure for comprehensive project intelligence. Key guidelines:

**Task Progress Updates:**
- Always update both the subtask status table AND the progress log when making progress
- The subtask table provides quick visual reference of current status
- The progress log captures the narrative and details of the work process
- Each progress log entry should include date, accomplishments, challenges, and decisions
- Update task status in `task-index` to reflect current progress

**Documentation Flow:**
```
New Task → Create task-{id}.py memory → Update task-index
Progress → Update task-{id}.py log table → Update task-index
Discovery → Create/ update appropriate core memory
Architecture Decision → Update system-patterns memory
Completion → Update progress memory → Clear from active tasks
```

**Active-Context Format:**
```markdown
## Active Context — Updated [Date]

### Current Focus
- Implementing user authentication with NextAuth.js
- Building recipe CRUD API routes

### Recent Decisions
- Chose MongoDB Atlas over Cosmos DB for cost
- Using server components for recipe listing page

### Blockers
- Image upload size limit needs investigation

### Next Steps
1. Complete login/signup UI
2. Add recipe creation form
3. Set up image upload to Blob Storage
```

## Memory Writing Guidelines
```markdown
## Active Context — Updated [Date]

### Current Focus
- Implementing user authentication with NextAuth.js
- Building recipe CRUD API routes

### Recent Decisions
- Chose MongoDB Atlas over Cosmos DB for cost
- Using server components for recipe listing page

### Blockers
- Image upload size limit needs investigation

### Next Steps
1. Complete login/signup UI
2. Add recipe creation form
3. Set up image upload to Blob Storage
```
