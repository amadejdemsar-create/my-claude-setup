---
name: gtm-write-copy
description: |
  Generate the campaign's email sequence and LinkedIn copy from its ICP, pricing, and positioning. Delegates to gtm-email-writer and gtm-linkedin-writer, presents drafts for confirmation, writes email-copy.md and linkedin-copy.md. Can be run standalone to refresh copy, and is also auto-invoked at the end of /gtm-new-campaign.
---

# GTM Write Copy

Produces the two copy artifacts a campaign needs before it can send outbound: `email-copy.md` and `linkedin-copy.md`.

## Arguments

- `$ARGUMENTS` optional campaign slug. If omitted, use `.default` from `~/.claude/gtm-campaigns.json`.
- Optional second arg: `mode=full` (default, regenerate both files) / `mode=email` / `mode=linkedin`. Only regenerate what is requested.
- Optional third arg: `email_index=N` (1-4) to regenerate one specific email only. Only valid with `mode=email`.

## Pre-flight

1. Resolve campaign slug. If invalid, list registered campaigns and ask.
2. Confirm all 4 campaign files exist: `icp.md`, `pricing.md`, `reply-playbook.md`, `pipeline-stages.md`, `config.json`. If any are blank or have unresolved `<PLACEHOLDER>` tokens, warn the user: "Copy generated from incomplete ICP or pricing will be weak. Proceed anyway? (yes/no)".
3. If `email-copy.md` or `linkedin-copy.md` already exist AND mode is `full`, show counts (e.g. "4 emails, 3 LinkedIn touchpoints already defined"). Ask: "Regenerate will overwrite. Backup first? (yes/no)". On yes, copy existing files to `<campaign_path>/.cache/copy/<YYYY-MM-DD>-<filename>.bak` before proceeding.

## Step 1: Generate email copy (if mode includes email)

Delegate to `gtm-email-writer` via the Task tool:

For a full regeneration:
```
op: generate_full_sequence
campaign_slug: <slug>
```

For a single email:
```
op: regenerate_one_email
campaign_slug: <slug>
email_index: <N>
reason: <optional user reason>
```

The specialist will load campaign context, generate the 4-email sequence with 3 subject variants each, present the draft, and ask `Accept draft? (yes / revise / skip)`. Relay the user's response directly.

On acceptance, specialist writes `email-copy.md` and returns `{status, file_path, emails_count, subject_variants_total, notes}`.

## Step 2: Generate LinkedIn copy (if mode includes linkedin)

Delegate to `gtm-linkedin-writer`:
```
op: generate_full_linkedin
campaign_slug: <slug>
```

Specialist reads the email copy that was just written (for tonal consistency), generates connection note (2 variants) + Day 4 message + Day 9 follow-up, verifies character counts, asks `Accept draft? (yes / revise / skip)`. Relay.

On acceptance, specialist writes `linkedin-copy.md` and returns `{status, file_path, touchpoints_generated, connection_note_char_counts, notes}`.

## Step 3: Final summary

Print:
```
## Copy generated for <campaign_slug>

Email sequence:
- 4 emails (Day 0, 3, 7, 12)
- 12 subject variants total
- File: <path>/email-copy.md
- Status: <status>

LinkedIn track:
- Connection note (2 variants, <A-count>/<B-count> chars)
- Day 4 first message
- Day 9 follow-up
- File: <path>/linkedin-copy.md
- Status: <status>

Next action:
- If this is a new campaign: /gtm-launch-check <slug> once you have built the master campaigns in Instantly and HeyReach UIs
- If this is a rewrite: push the new copy into the master campaigns in Instantly and HeyReach (manual step in each UI, since their APIs cannot edit campaign sequences)
```

## Modes of use

### Mode A: auto-invoked by /gtm-new-campaign
When called internally at the tail of the new-campaign skill, run mode=full, skip the "files already exist" branch, do NOT ask about backups (the files were just created blank).

### Mode B: manual refresh
User runs `/gtm-write-copy <slug>` to regenerate all copy from scratch. Backup existing, regenerate full.

### Mode C: targeted regeneration
User runs `/gtm-write-copy <slug> email 3` to regenerate only Email 3 because it is not converting. The email-writer patches that email only, preserves the other 3.

### Mode D: LinkedIn-only refresh
User runs `/gtm-write-copy <slug> linkedin` to regenerate only LinkedIn copy because they just changed the ICP. Keeps email copy untouched.

## Failure modes

- If `icp.md` or `pricing.md` contains unresolved placeholders, the agents will complain and produce weak copy. Catch this in pre-flight and abort if severe.
- If the user rejects both email and linkedin drafts, report: "No files were written. Run `/gtm-write-copy <slug>` again when ready."
- If the email-writer writes but the linkedin-writer fails, report partial success. Linkedin can be retried independently via `/gtm-write-copy <slug> linkedin`.

## Relationship to other skills

- Downstream from `/gtm-new-campaign`: auto-invoked at the end so new campaigns launch with first-draft copy.
- Upstream of `/gtm-launch-check`: launch check inspects `email-copy.md` and `linkedin-copy.md` for unresolved placeholders; running write-copy first is the canonical way to satisfy that check.
- Independent of `/gtm-weekly-batch` and `/gtm-reply-triage`: those read the finished copy files; they do not trigger copy regeneration.
