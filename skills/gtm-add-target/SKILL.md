---
name: gtm-add-target
description: |
  Add a single manually-found target to an active GTM campaign. Verifies ICP via Apollo, checks Attio dedupe, upserts to Attio, and optionally queues for active Instantly + HeyReach campaigns with draft-and-confirm.
---

# GTM Add Target

When you find a hotel (or any ICP target) outside the Apollo saved search and want to get it into the campaign.

## Arguments

- `$ARGUMENTS`: the lead identifier. Accepts one of:
  - Company domain (e.g. `hotel-example.com`)
  - Company name (e.g. "Boutique Hotel Example")
  - LinkedIn URL of a person or company
- Optional second argument: campaign slug. Else use default.

## Pre-flight

1. Resolve campaign and load context.
2. Parse `$ARGUMENTS` to determine input type.

## Step 1: Apollo lookup

Delegate to `gtm-apollo-prospector`:
```
op: single_target_lookup
campaign_slug: <slug>
input: { domain | company_name | linkedin_url }
```

Specialist does a FREE search first. Returns:
```
{
  found: true/false,
  apollo_record: {...},
  icp_match: { matches: true/false, signals_hit: [...], signals_miss: [...] },
  in_attio_already: true/false
}
```

## Step 2: Present match summary

Show the user:
- Name, company, title, location
- Website
- ICP fit: signals hit / miss from `icp.md`
- Already in Attio? If yes, stop here and report to avoid duplicate work.

Ask: "Add [Name, Company] to [campaign_slug]? (yes/no)".

## Step 3: Enrich (if needed) and upsert

On yes:

1. If Apollo record does not already have email, delegate to `gtm-apollo-prospector` for enrichment (1 credit). Confirm with user before enrichment.
2. Delegate to `gtm-attio-librarian`:
```
op: single_upsert
campaign_slug: <slug>
record: { person + company from Apollo }
batch_tag: "adhoc-YYYYMMDD"
source: "manual"
initial_stage: "Not Contacted"
```

## Step 4: Queue for active campaigns

Ask: "Queue for the active Instantly and HeyReach campaigns? (yes/no/email-only/linkedin-only)".

On yes, delegate to `gtm-instantly-operator` and `gtm-heyreach-operator` in parallel with `add_single_lead` ops. Each will request its own Proceed gate.

On email-only / linkedin-only, route accordingly.

## Step 5: Summary

```
Added <Name> at <Company> to <campaign_slug>.
- Attio record: <id>
- Email sequence: started / skipped
- LinkedIn track: started / skipped
```

## Failure modes

- If Apollo does not find the target, ask the user to paste basic info manually (email, name, title, LinkedIn URL) and skip enrichment.
- If the target does not match ICP (signals_miss > signals_hit), warn but still allow adding if user confirms. Tag as "manual_override" in Attio.
- If already in Attio in a different campaign, warn and ask if the user wants to move the record or add a parallel enrollment.
