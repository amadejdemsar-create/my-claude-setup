---
name: calendar
description: "Personal calendar management. Plan a whole week, edit a specific day, add or move events, view the schedule. Integrates with a task manager for priorities. Use when the user wants to plan, schedule, review, or modify their calendar."
---

# Calendar

Manage a personal Google Calendar: plan weeks, edit days, add events, view schedule.

This skill is a template. Replace the placeholders in the **Schedule Configuration** section with your own timing, rotation, and habits. The framework (week planning, day templates, event formatting) stays the same.

## Subcommands

| Command | What it does |
|---------|-------------|
| `/calendar week` | Plan the current week (Mon to Sun). Same as `/calendar week current`. |
| `/calendar week next` | Plan next week (upcoming Mon to Sun). |
| `/calendar week YYYY-MM-DD` | Plan the week containing that date. |
| `/calendar today` | View and edit today's schedule. |
| `/calendar tomorrow` | View and edit tomorrow's schedule. |
| `/calendar monday` (or any day name) | View and edit that day this week. |
| `/calendar YYYY-MM-DD` | View and edit a specific date. |
| `/calendar view` | Show this week's full schedule (read only). |
| `/calendar clear <day>` | Remove all template blocks from a specific day. |
| `/calendar add <day> <event> <time>` | Add a one-off event to a day. |
| `/calendar move <event> <from> <to>` | Move an event from one time/day to another. |

If no subcommand is given, show today's schedule and ask what the user wants to do.

## MCP Tools

Load via ToolSearch before first use in a session:
- `mcp__claude_ai_Google_Calendar__gcal_create_event` for creating events
- `mcp__claude_ai_Google_Calendar__gcal_list_events` for viewing events
- `mcp__claude_ai_Google_Calendar__gcal_update_event` for modifying events
- `mcp__claude_ai_Google_Calendar__gcal_delete_event` for removing events
- `mcp__claude_ai_Google_Calendar__gcal_list_calendars` for calendar info

All events should use:
- calendarId: `{YOUR_CALENDAR_ID}` (usually your Gmail address)
- timeZone in start/end: `{YOUR_TIMEZONE}` (e.g., `Europe/Ljubljana`, `America/New_York`)
- sendUpdates: `none`
- reminders: `{ "useDefault": false }`

---

## Planning a Week (`/calendar week`)

### Process

1. **Determine dates.** Calculate Monday through Sunday for the target week.

2. **Check existing events.** List events for that week. If template blocks already exist, show the user and ask: add alongside, or clear and recreate?

3. **Ask for exceptions.** "Any changes this week?" Examples: a side gig on Saturday, skip gym on a day, longer work day, special events, different workout split.

4. **Ask for priorities (optional).** "Any tasks to assign to work blocks?" If the user provides them, add as event descriptions in the Deep Focus and Light Tasks blocks. Can also pull from the user's task manager if integrated.

5. **Ask detail level.** "Full detail (commute + shower events) or clean (work, gym, cooking, habits only)?" Default: clean.

6. **Present the schedule.** Show a day-by-day table. Do NOT create events until approved.

7. **Get approval.** Wait for confirmation or adjustments.

8. **Create events.** Create in parallel across days for speed.

9. **Confirm.** Show total created and a compact summary.

### Editing a Day (`/calendar <day>`)

1. **List current events** for that day.
2. **Show the default template** for that day type (weekday gym, weekday rest, weekend gym).
3. **Ask what to change.** Add, remove, move, or replace events.
4. **Apply changes.** Create/update/delete as needed.

---

## Schedule Configuration (customize for your life)

### Timing

Replace with your own defaults:

| Parameter | Example Value |
|-----------|-------|
| Wake up | 08:20 |
| Leave home | 08:40 |
| Arrive at work | 09:00 |
| Work day length | 8h default (09:00 to 17:00) |
| Commute (each way) | 20min |
| Commute to gym | 20min |
| Commute gym to home | 15min |
| Gym session | 1h 30min |
| Shower (post-gym only) | 30min |
| Cooking | 1h daily (dinner today + lunch tomorrow) |
| Sleep target | 23:00 |

### Gym Rotation (example, weekly)

| Day | Workout |
|-----|---------|
| Mon | Rest |
| Tue | Push |
| Wed | Pull |
| Thu | Legs |
| Fri | Rest |
| Sat | Upper |
| Sun | Legs |

### Habits (example)

| Habit | Duration | Days | Placement |
|-------|----------|------|-----------|
| Meditation | 10min | Daily | Afternoon, after work/gym |
| Skincare | 10min | Tue, Thu, Sat | After gym or close to end of day |
| Mobility work | 15min | Wed, Fri, Sun | After gym |
| Side project | 40min | Wed, Sat | Flexible timing |

### Habit Load Per Day (auto-derived)

Sum the habit durations for each day so you know how much evening time to reserve. Days with 60+ min of habits need tighter scheduling.

---

## Day Templates

All times calculated from configuration above. If parameters change (longer work day, different gym time), recalculate accordingly.

### WEEKDAY GYM DAY (Tue, Wed, Thu)

| Time | Event | Color |
|------|-------|-------|
| 09:00 to 14:00 | Work: Deep Focus | 3 (Grape) |
| 14:00 to 17:00 | Work: Light Tasks | 3 (Grape) |
| 17:20 to 18:50 | Gym: [Push/Pull/Legs] | 2 (Sage) |
| 19:35 to 20:35 | Cooking | 6 (Tangerine) |
| 20:35 to [end] | Habits | 4 (Flamingo) |

Optional (full detail mode):
| 17:00 to 17:20 | Commute to Gym | 8 (Graphite) |
| 18:50 to 19:05 | Commute Home | 8 (Graphite) |
| 19:05 to 19:35 | Shower | 8 (Graphite) |

### WEEKDAY REST DAY (Mon, Fri)

| Time | Event | Color |
|------|-------|-------|
| 09:00 to 14:00 | Work: Deep Focus | 3 (Grape) |
| 14:00 to 17:00 | Work: Light Tasks | 3 (Grape) |
| 17:20 to 18:20 | Cooking | 6 (Tangerine) |
| 18:20 to [end] | Habits | 4 (Flamingo) |

Optional (full detail mode):
| 17:00 to 17:20 | Commute Home | 8 (Graphite) |

Rest days have the most free evening time. Optionally use for side-project work.

### WEEKEND GYM DAY (Sat, Sun)

| Time | Event | Color |
|------|-------|-------|
| 10:00 to 13:00 | Side project: Deep Focus | 9 (Blueberry) |
| 13:30 to 15:00 | Side project: Light Tasks | 9 (Blueberry) |
| 15:20 to 16:50 | Gym: [Upper/Legs] | 2 (Sage) |
| 17:35 to 18:35 | Cooking | 6 (Tangerine) |
| 18:35 to [end] | Habits | 4 (Flamingo) |
| [after habits] to [+1.5h] | Side project: Evening Session | 9 (Blueberry) |

Weekend template assumes you use Saturdays and Sundays for a personal side project or focused learning. Adjust or remove if weekends are unstructured for you.

---

## Event Formatting

### Event Names
Plain names, no emojis. Adapt the category prefixes to your own work:
- `Work: Deep Focus`, `Work: Light Tasks`
- `Side project: Deep Focus`, `Side project: Light Tasks`, `Side project: Evening Session`
- `Gym: Push`, `Gym: Pull`, `Gym: Legs`, `Gym: Upper`
- `Cooking`, `Shower`, `Commute`
- `Meditation`, `Skincare`, `Mobility`

### Color Coding

| Category | Color ID | Name |
|----------|----------|------|
| Main work | 3 | Grape |
| Side project | 9 | Blueberry |
| Gym | 2 | Sage |
| Cooking | 6 | Tangerine |
| Habits | 4 | Flamingo |
| Routine (commute, shower) | 8 | Graphite |

### Grouping habits
If the user prefers fewer events, group habits into one per day:
- Event name: `Habits: Meditation, Skincare` (list what's included)
- Duration: sum of individual habit durations
- Color: 4 (Flamingo)

Default: individual habit events. Ask if unsure.

### Event descriptions
For work blocks with priorities:
```
Priorities:
1. [Task name]
2. [Task name]
```

### Events NOT to create
- Wake up / alarm
- Slow morning on weekends
- Free time / dinner time
- Sleep

---

## Edge Cases

### Longer work day
Shift everything after work by the extra hours. Warn the user if free time drops below 1h on heavy habit days.

### Gym schedule changes
For one-off changes, apply to that week only. For permanent changes, update the gym rotation table in this file.

### Skip gym
Use the rest day template for that day instead.

### Overlapping events
Flag conflicts and ask the user how to resolve.

---

## Priority Integration (task manager)

If the user uses a task manager with an MCP or API (e.g., Todoist, Notion, Linear), wire it up to pull weekly priorities:

1. Load the task manager's tools via ToolSearch.
2. Query tasks from the projects the user cares about.
3. Sort by priority and due date.
4. Assign high-priority tasks to Deep Focus blocks, lower-priority to Light Tasks.
5. Add task names as event descriptions.

This works best when the user has set weekly priorities in their task manager. See the `/todoist` skill for an example integration.
