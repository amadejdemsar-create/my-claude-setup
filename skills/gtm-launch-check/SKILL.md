---
name: gtm-launch-check
description: |
  Verify every launch checklist item against live data for a campaign. Runs before the very first outbound send. Delegates to each specialist for real connection tests. Outputs pass/fail per item with a LAUNCH BLOCKED banner if any fail.
---

# GTM Launch Check

The single gate between preparation and the first outbound send.

## Arguments

- `$ARGUMENTS` optional campaign slug. Else default.

## Pre-flight

Resolve campaign, load all context files. If any is missing, that is already a fail.

## Checks (ordered)

### A. Campaign config completeness

Read `config.json`. Each must be non-empty:
1. `apollo.saved_search_id` — Apollo saved search exists and returns results
2. `instantly.master_campaign_id` — Instantly master campaign exists and is ready to duplicate
3. `instantly.mailboxes` — at least 3 mailboxes listed
4. `heyreach.master_campaign_id` — HeyReach master campaign exists and is paused
5. `heyreach.linkedin_accounts` — at least 1 LinkedIn account listed
6. `attio.pipeline_slug` — Attio pipeline exists and has all stages from `pipeline-stages.md`
7. `kpi_targets` — all 5 floors defined

### B. Product-level checks

Only applicable if this campaign is selling a SaaS product:
1. Stripe prices configured in the currency declared in `config.json.currency`
2. Any product-gating features (e.g. conversation caps) enforced in code, not just displayed
3. Multi-tenant authorization checks on every tenant-scoped API route
4. Instant demo works on 3 sample URLs drawn from `icp.md` (if the product has a demo-on-URL feature)

If the user cannot self-verify these, ask explicitly before continuing. Do not silently skip.

### C. Infrastructure checks

Delegate in parallel:

1. `gtm-instantly-operator` {op: deliverability_check}: all mailboxes green, warmup ≥10 days, SPF/DKIM/DMARC valid.
2. `gtm-apollo-prospector` {op: saved_search_health}: saved search returns ≥200 results AND ≥60% have verified emails.
3. `gtm-heyreach-operator` {op: campaign_health}: master campaign exists, is paused, sequence has all 4 steps, connection note under 280 chars.
4. `gtm-attio-librarian` {op: pipeline_health}: pipeline has all stages named in `pipeline-stages.md`, lists exist (companies, people), initial stage is "Not Contacted".

### D. Copy checks

Read `email-copy.md` and `linkedin-copy.md`:
1. Every email has 3 subject variants
2. Every email has a body with required variables: [First], [Hotel Name] (or equivalent product variables)
3. No unresolved placeholder text (e.g. "TODO", "FIXME", "<Product Name>")
4. LinkedIn connection note ≤280 characters

### E. Data pipe dry run

1. Construct a synthetic CSV of 10 fake targets that match ICP shape.
2. Send through the pipe (Apollo not needed for dry run, go straight to Attio → Instantly → HeyReach with a synthetic batch_tag `dryrun-YYYYMMDD`).
3. Verify all three tools accept the records.
4. Delete the synthetic records afterward.

## Output

```
## Launch Check: <campaign_slug>

### Results

| # | Check | Status | Detail |
|---|---|---|---|
| A1 | Apollo saved_search_id | ok / fail | <detail> |
| A2 | Instantly master_campaign_id | ... |
...
| E  | Dry run | ... |

### Pass rate: <X> / <N>
```

## Banner logic

- All `ok`: print big banner "LAUNCH READY. Run /gtm-weekly-batch to send the first batch."
- Any `fail`: print banner "LAUNCH BLOCKED. Fix the failures above before first send."
- Any `skip` (user-unverified): print banner "LAUNCH PENDING VERIFICATION. Confirm the skipped items, then re-run."

## Failure modes

- If any MCP is not configured, prompt the user with the exact jq command to add it (reference `gtm-framework/setup-audit.md`).
- If a master campaign does not exist in the tool, pause and instruct the user to create it in the UI first, with copy pasted from `email-copy.md` or `linkedin-copy.md`.
