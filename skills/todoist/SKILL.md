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

```
Nevron (board)                        6g2wX8hQwGGGmVP3
├── Scrape (list)                     6g2wXCwc87RPvXGM
│   ├── P0: Critical Bugs & Blockers  6g2wjxVRJ6c8f26v
│   ├── P1: MVP Core Functionality    6g2wjxQmwvfhhm9v
│   ├── P2: Frontend & UX             6g2wjxV8H8pWh9MM
│   ├── P3: Quality & Reliability     6g2wjxQpWX6G4HMM
│   ├── P4: DevOps & Deployment       6g2wjxRcvMqVgGpM
│   └── P5: Future / Self-Service     6g2wjxQjchMMmMXM
├── Nevron NativeAI (list)            6g37WWh9P8Qh9wFg
│   └── (no sections yet)
└── Context (list)                    6g37WqHm5pqr3rmH
    └── (no sections yet)
```

### Nevron (Parent Project)
- **Project ID:** `6g2wX8hQwGGGmVP3`
- **View:** Board
- **Purpose:** Top-level container for all Nevron related work

### Nevron > Scrape (Sub-project)
- **Project ID:** `6g2wXCwc87RPvXGM`
- **View:** List
- **Purpose:** Web scraping product (MVP focus)
- **Sections:**

| Section | ID | Todoist Priority | Description |
|---------|-----|-----------------|-------------|
| P0: Critical Bugs & Blockers | `6g2wjxVRJ6c8f26v` | p1 (highest) | Showstoppers, crashes, data loss |
| P1: MVP Core Functionality | `6g2wjxQmwvfhhm9v` | p1 (highest) | Must work for MVP launch |
| P2: Frontend & UX | `6g2wjxV8H8pWh9MM` | p2 (high) | UI polish, UX improvements |
| P3: Quality & Reliability | `6g2wjxQpWX6G4HMM` | p3 (medium) | Error handling, monitoring, testing |
| P4: DevOps & Deployment | `6g2wjxRcvMqVgGpM` | p3 (medium) | CI/CD, hosting, infrastructure |
| P5: Future / Self-Service | `6g2wjxQjchMMmMXM` | p4 (lowest) | Post-MVP features, self-service vision |

### Nevron > Nevron NativeAI (Sub-project)
- **Project ID:** `6g37WWh9P8Qh9wFg`
- **View:** List
- **Purpose:** NativeAI product development
- **Sections:** None yet (add as needed with `mcp__todoist__add-sections`)

### Nevron > Context (Sub-project)
- **Project ID:** `6g37WqHm5pqr3rmH`
- **View:** List
- **Purpose:** Context/content management work
- **Sections:** None yet (add as needed with `mcp__todoist__add-sections`)

### Inbox
- **Project ID:** `6fXXg25grqx9RQPM`
- **View:** List
- **Purpose:** Quick capture, unsorted tasks

## Labels (use exact strings)
- `bug` : Bug reports and fixes
- `backend` : Server side work
- `frontend` : Client side work
- `mvp` : MVP scope items
- `testing` : Test related tasks
- `feature` : New features
- `design` : UI/UX design work
- `database` : Database changes
- `config` : Configuration tasks
- `n8n` : n8n integration work
- `ai` : AI/LLM related
- `devops` : Infrastructure/deployment
- `deployment` : Deployment specific
- `security` : Security related
- `performance` : Performance optimization
- `quality` : Quality assurance
- `reliability` : Reliability improvements
- `monitoring` : Monitoring/alerting
- `enhancement` : Improvements to existing features
- `research` : Research/investigation tasks
- `integration` : External integrations
- `self-service` : Self-service features
- `payments` : Payment integration
- `ci-cd` : CI/CD pipeline
- `admin` : Admin dashboard

## Task Creation Patterns

### Creating tasks in Nevron Scrape (most common for scraping work)
```json
{
  "tasks": [{
    "content": "Verb-first task title",
    "description": "Details, file paths, acceptance criteria",
    "projectId": "6g2wXCwc87RPvXGM",
    "sectionId": "<section_id from table above>",
    "priority": "<p1|p2|p3|p4>",
    "labels": ["backend", "mvp"]
  }]
}
```

### Creating tasks in NativeAI
```json
{
  "tasks": [{
    "content": "Verb-first task title",
    "description": "Details",
    "projectId": "6g37WWh9P8Qh9wFg",
    "priority": "<p1|p2|p3|p4>",
    "labels": ["feature"]
  }]
}
```

### Creating tasks in Context
```json
{
  "tasks": [{
    "content": "Verb-first task title",
    "description": "Details",
    "projectId": "6g37WqHm5pqr3rmH",
    "priority": "<p1|p2|p3|p4>",
    "labels": ["research"]
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
  "projectId": "<project_id>"
}
```
Filter further with `sectionId`, `labels`, `searchText`.

## Conventions
- Task titles: Start with a verb ("Fix...", "Add...", "Implement...", "Verify...", "Review...")
- Bug tasks: Always include `bug` label and file path in description
- Code tasks: Include relevant file path(s) in description
- When working on a task: find it, check its description, then complete it when done
- Default project for Nevron scraping work: `6g2wXCwc87RPvXGM` (Scrape sub-project)
- Default project for NativeAI work: `6g37WWh9P8Qh9wFg`
- Default project for content/context work: `6g37WqHm5pqr3rmH`

## Adding New Projects

When the user creates a new project or sub-project in Todoist, update this skill file with the new project ID and section IDs so they are pre-resolved for future sessions.
