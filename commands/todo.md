Manage a unified todo system. Read, add, complete, or remove tasks. Supports nested projects.

## Data Files

- **Source of truth:** `{YOUR_DATA_PATH}/todos.json`
- **Dashboard HTML:** `{YOUR_DATA_PATH}/index.html`

Configure these paths for your own setup. The dashboard HTML contains an embedded `DATA` block between `// __DATA_START__` and `// __DATA_END__` sentinels that mirrors `todos.json` in minified form.

## Data Structure

The system uses nested projects. Structure:

```json
{
  "categories": [...],
  "projects": [
    {
      "id": "project-slug",
      "name": "Project Name",
      "category": "work|personal|finance|side-project",
      "projects": [
        {
          "id": "sub-project-slug",
          "name": "Sub Project Name",
          "projects": [],
          "todos": [...]
        }
      ],
      "todos": [
        {
          "id": "todo-slug",
          "title": "Todo title",
          "priority": "high|medium|low",
          "due": "2026-03-28",
          "note": "Optional",
          "done": false,
          "createdAt": "2026-03-25"
        }
      ]
    }
  ]
}
```

Sub-projects inherit the category from their parent project.

## Step 1: Read Current State

Read `todos.json` to see all current projects and tasks.

## Step 2: Interpret User Intent

Based on the user's message (passed as $ARGUMENTS), determine the action:

- **No arguments or "show":** Display all open tasks grouped by project. Show counts per project and category.
- **"add [task]":** Add a new task to the appropriate project. Infer category and project from context. If no matching project exists, create one or ask.
- **"add project [name]":** Create a new project under the appropriate category.
- **"done [task]" or "complete [task]":** Mark a task as done. Search across all projects/sub-projects.
- **"remove [task]":** Remove a task entirely.
- **"clear done":** Remove all completed tasks from all projects.
- **"open":** Open the dashboard in your default browser.
- **A plain task description:** Treat as "add" with that description.

## Step 3: Adding Tasks

When adding a task:
1. Determine the category from context (see inference rules below)
2. Find the best matching project within that category
3. If the project has sub-projects, pick the right sub-project
4. Add the todo to that project's `todos` array

Task structure:
- `id`: lowercase, hyphenated, unique
- `priority`: default "medium" unless user specifies urgency
- `due`: set if user mentions a date. Convert relative dates to absolute.
- `note`: only if user provides extra context
- `createdAt`: today's date
- `done`: false

## Step 4: Update Files

After modifying `todos.json`:

1. Write the updated JSON back to `todos.json`
2. Update the HTML dashboard by replacing the DATA block between `// __DATA_START__` and `// __DATA_END__` in `index.html` with the new minified JSON. Format:
   ```
   // __DATA_START__
   const DATA = <full JSON on one line>;
   // __DATA_END__
   ```
3. Confirm the action to the user with a brief summary.

## Step 5: Open Dashboard (Optional)

If the user asks to see the dashboard or says "open", open `index.html` in their default browser.

## Category Inference Rules (customize for your setup)

Add categories that map to your projects. Examples:

- **Work:** client work, company projects, business tasks
- **Personal:** errands, admin, appointments, documents, chores, life stuff
- **Finance:** portfolio, trades, investing, budget
- **Side project:** a specific named side project you are building
- **Things to buy:** buy, purchase, order, get, need to pick up

Update this list with keywords your own categories commonly include.
