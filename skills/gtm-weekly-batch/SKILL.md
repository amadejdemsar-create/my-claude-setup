---
name: gtm-weekly-batch
description: |
  Run Phase 2 + 3 of the GTM workflow end to end for a campaign. Pull Apollo list, dedupe, enrich, load to Attio, prepare Instantly campaign, load HeyReach leads, draft-and-confirm both sends, launch. Accepts an optional campaign slug argument; defaults to ~/.claude/gtm-campaigns.json `.default`.
---

# GTM Weekly Batch

Runs the weekly outbound prep-and-launch flow for one campaign. Typically invoked Monday afternoon.

## Arguments

- `$ARGUMENTS` optional campaign slug. If omitted, use `.default` from `~/.claude/gtm-campaigns.json`.
- If the argument is invalid (slug not in registry), print the list of valid campaigns and ask which one.

## Pre-flight: campaign context

1. Read `~/.claude/gtm-campaigns.json`. Resolve campaign slug.
2. Resolve campaign path. Confirm all 7 files exist: `icp.md`, `pricing.md`, `email-copy.md`, `linkedin-copy.md`, `reply-playbook.md`, `pipeline-stages.md`, `config.json`.
3. Parse `config.json`. Verify the following are non-empty:
   - `apollo.saved_search_id`
   - `instantly.master_campaign_id`
   - `heyreach.master_campaign_id`
   - `attio.pipeline_slug`
4. If any are empty, stop and tell the user exactly which IDs to configure (via respective tool UIs) before re-running.
5. Derive batch_tag = ISO year + week (e.g., `2026-W17`).

Announce plainly: "Running weekly batch for [campaign_slug], tag [batch_tag], target size [batch_size]."

## Step 1: Apollo pull

Delegate to `gtm-apollo-prospector` via the Task tool, `model: opus`:

```
op: weekly_batch_pull
campaign_slug: <slug>
batch_size: <from config, default 200>
batch_tag: <derived>
```

Expect: `{batch_tag, csv_path, total_found, already_in_attio, enriched, credits_spent, credits_remaining}`.

Report the output, especially credit burn and already-in-Attio skip count.

## Step 2: Attio upload

Delegate to `gtm-attio-librarian`:

```
op: bulk_upload
campaign_slug: <slug>
batch_tag: <tag>
csv_path: <from step 1>
```

Expect: `{companies_upserted, people_upserted, duplicates_skipped, errors}`.

## Step 3: Instantly campaign prep

Delegate to `gtm-instantly-operator`:

```
op: create_batch_campaign
campaign_slug: <slug>
batch_tag: <tag>
csv_path: <from step 1>
region: <optional from user>
```

The specialist loads leads into a duplicate of the master campaign, leaves it paused, and shows a preview. It will ask the user "Proceed?" before starting. Relay that confirmation directly.

Expect: `{instantly_campaign_id, leads_loaded, scheduled_start}`.

## Step 4: HeyReach leads prep

Delegate to `gtm-heyreach-operator`:

```
op: add_leads_to_master
campaign_slug: <slug>
leads_from_csv: <csv_path from step 1>
```

Specialist validates LinkedIn URLs, dedupes against Attio (may re-check), respects weekly LinkedIn caps, and asks "Proceed?" before adding to the live master campaign. Relay the confirmation.

Expect: `{leads_added, skipped_dedupe, skipped_cap, errors}`.

## Step 5: Final report

Print a markdown summary:

```
## Weekly Batch Complete: <campaign_slug> / <batch_tag>

- Apollo: <N> found, <A> already in Attio, <E> enriched (<credits> credits, <remaining> left)
- Attio: <C> companies upserted, <P> people upserted, <D> duplicates
- Instantly: campaign <id> with <L> leads, first send <timestamp>
- HeyReach: <H> leads added, <S> skipped (cap/dedupe)

Next action: monitor replies. Run /gtm-reply-triage tomorrow and each following morning.
```

## Failure modes

- If any step fails and the user declines a Proceed, abort the workflow cleanly and report which step was reached.
- If Apollo returns <50% of batch_size, the saved search may be exhausted; flag this and suggest widening geography in `icp.md`.
- If Attio upload has errors on some records, continue with the successful ones but report the errors in the final summary.
