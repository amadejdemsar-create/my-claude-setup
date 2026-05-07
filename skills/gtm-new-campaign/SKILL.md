---
name: gtm-new-campaign
description: |
  Register a new campaign. Guided setup that copies the campaign template, walks through ICP / pricing / copy input, records IDs for Apollo saved search, Instantly master, HeyReach master, and Attio pipeline, and registers the campaign in the registry. Makes the framework repeatable for any new product.
---

# GTM New Campaign

Use this when adding a second, third, or Nth campaign to the framework.

## Arguments

- `$ARGUMENTS` optional slug to pre-fill. Else ask.

## Step 1: Identify the campaign

Ask in order:
1. Campaign slug (kebab-case, e.g. `nevron-core`, `native-ai-clients`, `product-launch-2026`). Validate unique vs existing campaigns in `~/.claude/gtm-campaigns.json`.
2. Product name (human readable).
3. Company or owner (the brand this outbound is run under).
4. Target folder for campaign config. Default: `/Users/Shared/Domain/Context/Business/<company>/<slug>/campaign/`. Confirm or override.

## Step 2: Copy the template

Copy every file from `~/.claude/gtm-framework/campaign-template/` to the target folder. Preserve structure. If the target folder already exists and is non-empty, abort unless the user explicitly asks to overwrite.

## Step 3: Guided content input

Collect inputs one at a time. After each, write into the right file.

### 3a. ICP summary
Ask for:
- Primary ICP one-liner
- Company size range
- Target geographies (priority order)
- Key titles / buying roles
- 3-5 qualification signals
- 3-5 deprioritize criteria

Write into `icp.md` in the target folder.

### 3b. Pricing tiers
Ask for: number of tiers, name + monthly + annual + main inclusion per tier, currency. Also: trial length, free-trial rules.

Write into `pricing.md`.

### 3c. Positioning
Ask for: category name, one-sentence positioning, 3-4 differentiators, main 3-5 competitors with a one-line compare.

Write to `pricing.md` bottom OR create a short competitive section.

### 3d. Email copy (SKIPPED at this stage)

Do NOT ask for email copy here. The `/gtm-write-copy` skill will generate the full 4-email sequence automatically from ICP and pricing at Step 7. Leave the template `email-copy.md` in place for now.

### 3e. LinkedIn copy (SKIPPED at this stage)

Same reason. `/gtm-write-copy` generates the connection note plus 2 messages at Step 7. Leave `linkedin-copy.md` template in place.

### 3f. Reply playbook
Use the 6-scenario template. For each, ask for the preferred response style (short, formal, casual). Fill in with boilerplate the user can edit.

Write into `reply-playbook.md`.

### 3g. Pipeline stages
Default to the 6-stage template (Not Contacted → Contacted → Engaged → Meeting Booked → Trial Activated → Won). Ask if the user wants to add/remove/rename any. Capture KPI targets per stage.

Write into `pipeline-stages.md` and into `config.json.kpi_targets`.

## Step 4: Tool IDs

Now collect the external IDs. Each one the user either has, or needs to create in the tool's UI first. Offer both paths.

### 4a. Apollo saved search
Ask: "Do you have an Apollo saved search for this ICP already? If yes, paste the ID. If no, open Apollo, create a saved search with the filters from `icp.md`, then paste the ID."

Write into `config.json.apollo.saved_search_id`.

### 4b. Instantly master campaign
Ask: "Create a master email campaign in Instantly UI with the 4-step sequence from `email-copy.md`. Paste the campaign ID when ready. Also list the mailboxes you will send from."

Write into `config.json.instantly.master_campaign_id` and `.mailboxes`.

### 4c. HeyReach master campaign
Ask: "Create a master LinkedIn campaign in HeyReach UI with the 4-step sequence from `linkedin-copy.md` (Day 0 profile view, Day 1 connection + note, Day 4 first message, Day 9 follow-up). Paste the campaign ID when ready. Also list the LinkedIn accounts you will use."

Write into `config.json.heyreach.master_campaign_id` and `.linkedin_accounts`.

### 4d. Attio pipeline
Ask: "Create an Attio pipeline with these stages: <list from pipeline-stages.md>. Paste the pipeline slug, plus the Companies list slug and People list slug you will use."

Write into `config.json.attio.pipeline_slug`, `.companies_list_slug`, `.people_list_slug`.

## Step 5: Register the campaign

Update `~/.claude/gtm-campaigns.json`:
1. Add the new campaign under `.campaigns.<slug>` with `{path: <target folder>, status: "pre_launch", created: "<today>"}`.
2. Ask: "Make this the default campaign? (yes/no)". On yes, update `.default`.

## Step 6: Announce registration

Print:
```
Campaign <slug> registered at <path>.
Email copy and LinkedIn copy will be generated next from your ICP and pricing.
```

## Step 7: Auto-invoke /gtm-write-copy

Immediately invoke the `/gtm-write-copy` skill for the freshly registered campaign in mode `full`. This is the canonical flow: registration is not considered complete without copy generation.

Pass the slug as argument:
```
/gtm-write-copy <slug>
```

Inside that skill:
- `gtm-email-writer` reads ICP, pricing, positioning and produces the 4-email sequence (12 subject variants + 4 bodies).
- `gtm-linkedin-writer` reads ICP, email sequence (for tonal consistency), and produces connection note (2 variants) + Day 4 message + Day 9 follow-up.
- User confirms each draft (Accept / Revise / Skip).

If the user skips either draft, the skill leaves the template file in place and notes in the handover that copy needs manual completion before launch. If the user accepts both, the campaign has real first-draft copy by the time this skill returns.

## Step 8: Next steps

Print (adapt the wording based on which copy was accepted in Step 7):
```
Campaign <slug> ready for setup verification.

State:
- ICP, pricing, positioning, reply playbook, pipeline: defined
- Email copy (email-copy.md): <accepted | skipped, fill manually before launch>
- LinkedIn copy (linkedin-copy.md): <accepted | skipped, fill manually before launch>

Next actions:
1. Build the master Instantly campaign in the Instantly UI using email-copy.md as the source (API cannot edit sequence copy).
2. Build the master HeyReach campaign in the HeyReach UI using linkedin-copy.md (HeyReach API cannot create campaigns).
3. Paste the master campaign IDs into config.json (instantly.master_campaign_id, heyreach.master_campaign_id).
4. Run /gtm-launch-check <slug> to verify the full setup against live data.
5. When launch check passes green, run /gtm-weekly-batch <slug> to pull and send the first batch.

To regenerate copy later: /gtm-write-copy <slug>
```

## Failure modes

- If the target folder path is not writeable, stop and ask for a different folder.
- If the user wants to skip too many steps (no copy, no IDs, no KPIs), warn that /gtm-launch-check will block and offer to save a partial draft with a TODO list.
- If the slug collides with an existing campaign, require a different slug or confirm overwrite (which wipes the existing campaign config; never default to overwrite).
