---
name: gtm-pipeline-review
description: |
  Weekly pipeline health check for one campaign. Reads Attio deals, groups by stage, computes KPIs vs floors defined in pipeline-stages.md, identifies stuck deals, recommends one action. Read-only, no confirmations.
---

# GTM Pipeline Review

Run this weekly (typically Friday afternoon or Monday morning before /gtm-weekly-batch).

## Arguments

- `$ARGUMENTS` optional campaign slug.

## Pre-flight

Resolve campaign. Load `pipeline-stages.md` and `config.json`.

## Step 1: Pipeline snapshot

Delegate to `gtm-attio-librarian`:
```
op: pipeline_snapshot
campaign_slug: <slug>
```

Returns:
```
{
  "stages": {"Not Contacted": N, "Contacted": N, ...},
  "stages_delta_7d": {"Contacted": +N, ...},
  "kpis": {
    "contact_to_reply": {value, target_range, status},
    "reply_to_meeting": {value, target_range, status},
    "meeting_to_trial": {value, target_range, status},
    "trial_to_paid": {value, target_range, status},
    "paid_to_activated": {value, target_range, status}
  },
  "stuck": [{person_id, stage, days_in_stage, company, reason}]
}
```

## Step 2: KPI comparison

For each KPI, compare value to the floor in `config.json.kpi_targets` (authoritative) or `pipeline-stages.md` (fallback).

Mark each KPI:
- `ok`: at or above floor
- `below_1w`: below floor this week only
- `below_2w`: below floor for 2+ consecutive weeks (this is the one to fix)

Determine the weakest stage: the one with the worst ratio vs target that has been below for 2+ weeks.

## Step 3: Stuck deal identification

Rules per `pipeline-stages.md` define "stuck":
- Not Contacted >7 days after upload
- Contacted >14 days with no reply
- Engaged >7 days with no advance
- Meeting Booked with meeting date in the past
- Trial Activated with no widget install after 5 days

For each stuck deal, suggest an action:
- Not Contacted stuck: launch the campaign or delete the record
- Contacted stuck: move to Lost (no response) or extend Email 4 window
- Engaged stuck: re-reply within 24 hours
- Meeting Booked missed: reschedule or Lost (no-show)
- Trial no-install: white-glove outreach to install the widget

## Step 4: Output markdown report

```
## Pipeline Review: <campaign_slug> / <YYYY-MM-DD>

### Stage distribution (7-day delta)
| Stage | Current | Δ 7d |
|---|---|---|
| Not Contacted | N | +/- |
| Contacted | N | +/- |
| Engaged | N | +/- |
| Meeting Booked | N | +/- |
| Trial Activated | N | +/- |
| Won | N | +/- |

### KPIs vs floors
| KPI | Value | Floor | Status |
|---|---|---|---|
| Contact to reply | X% | 4% | ok / below_1w / below_2w |
| ... |

### Below floor for 2+ weeks
(list or "none")

### Weakest stage
<stage>: suggested action: <one concrete thing>

### Stuck deals (N total)
| Person | Company | Stage | Days stuck | Suggested action |
|---|---|---|---|---|

### Recommendation for the week
<single, concrete, specific action>
```

## Step 5: Offer follow-up

After the report, ask: "Want to apply any of the suggested actions now? I can run them in bulk."

If yes, for each action type, delegate to appropriate specialist with confirmation.

## Failure modes

- If `gtm-attio-librarian` returns empty pipeline, check `attio.pipeline_slug` in config.json.
- If KPI data is incomplete (e.g., no replies this week), note "insufficient data" rather than computing misleading numbers.
