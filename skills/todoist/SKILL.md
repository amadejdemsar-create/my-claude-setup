---
name: todoist
description: "Todoist project management integration. Use when the user mentions tasks, todos, Todoist, backlog, priorities, bugs, or wants to create/update/query/complete tasks. Contains pre-resolved project IDs, section IDs, labels, and correct MCP tool usage patterns."
---

# Todoist Integration Reference

## MCP Tools Available

The Todoist MCP server is already connected. Tools use the `mcp__todoist__` prefix.

**IMPORTANT**: Tools must be loaded via ToolSearch before first use in a session. Load them with:
```
ToolSearch query: "+todoist add tasks" (for creating)
ToolSearch query: "+todoist find tasks" (for querying)
ToolSearch query: "+todoist complete" (for completing)
ToolSearch query: "+todoist update" (for updating)
```

### Key Tools
| Tool | Purpose |
|------|---------|
| `mcp__todoist__add-tasks` | Create one or more tasks (batch supported) |
| `mcp__todoist__update-tasks` | Modify existing tasks |
| `mcp__todoist__complete-tasks` | Mark tasks as done |
| `mcp__todoist__find-tasks` | Search/filter tasks |
| `mcp__todoist__find-tasks-by-date` | Get tasks by date range |
| `mcp__todoist__find-completed-tasks` | View completed tasks |
| `mcp__todoist__add-sections` | Create new sections |
| `mcp__todoist__find-sections` | List sections in a project |
| `mcp__todoist__add-projects` | Create new projects |
| `mcp__todoist__find-projects` | Search projects |
| `mcp__todoist__get-overview` | Full markdown overview of account or project |
| `mcp__todoist__delete-object` | Remove tasks, projects, sections, comments |
| `mcp__todoist__fetch-object` | Get a single task/project/section by ID |

## Project Structure (Pre-resolved IDs)

**NEVER call find-projects or find-sections to look these up. Use the IDs directly.**

Configure your project structure below. Run `mcp__todoist__find-projects` once to get your IDs, then hardcode them here for fast access.

```
# Example structure - replace with your actual projects and IDs:
My Project (board)                     PROJECT_ID_HERE
├── Feature Work (list)                SUBPROJECT_ID_1
│   ├── P0: Critical Bugs             SECTION_ID_1
│   ├── P1: Core Functionality         SECTION_ID_2
│   ├── P2: Frontend & UX             SECTION_ID_3
│   └── P3: Future Ideas              SECTION_ID_4
└── Side Projects (list)               SUBPROJECT_ID_2
```

### Inbox
- **Project ID:** `YOUR_INBOX_ID`
- **Purpose:** Quick capture, unsorted tasks

## Labels (use exact strings)

Configure your labels here. Common examples:
- `bug` : Bug reports and fixes
- `backend` : Server side work
- `frontend` : Client side work
- `feature` : New features
- `testing` : Test related tasks
- `design` : UI/UX design work
- `database` : Database changes
- `devops` : Infrastructure/deployment
- `research` : Research/investigation tasks

## Task Creation Patterns

### Creating tasks in a project
```json
{
  "tasks": [{
    "content": "Verb-first task title",
    "description": "Details, file paths, acceptance criteria",
    "projectId": "YOUR_PROJECT_ID",
    "sectionId": "YOUR_SECTION_ID",
    "priority": "<p1|p2|p3|p4>",
    "labels": ["backend", "feature"]
  }]
}
```

### Batch creation (up to 10 per call)
Pass an array of task objects to `mcp__todoist__add-tasks`. All tasks in one call.

### Completing tasks
```json
{
  "taskIds": ["task_id_1", "task_id_2"]
}
```

### Finding tasks by project
```json
{
  "projectId": "YOUR_PROJECT_ID"
}
```
Filter further with `sectionId`, `labels`, `searchText`.

## Conventions
- Task titles: Start with a verb ("Fix...", "Add...", "Implement...", "Verify...", "Review...")
- Bug tasks: Always include `bug` label and file path in description
- Code tasks: Include relevant file path(s) in description
- When working on a task: find it, check its description, then complete it when done

## Adding New Projects

When you create a new project or sub-project in Todoist, update this skill file with the new project ID and section IDs so they are pre-resolved for future sessions.
