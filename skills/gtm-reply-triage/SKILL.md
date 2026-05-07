---
name: gtm-reply-triage
description: |
  Clear the Instantly inbox and HeyReach inbox for the active campaign. Classify every reply per the reply playbook, draft a response, confirm per reply, send, log to Attio, and advance stages. Accepts optional campaign slug.
---

# GTM Reply Triage

Daily habit during an active campaign. Handles email + LinkedIn replies in one pass.

## Arguments

- `$ARGUMENTS` optional campaign slug. Else use default.
- Optional second argument: `since=24h` (default) or `since=YYYY-MM-DD`.

## Pre-flight

1. Resolve campaign from registry.
2. Read the campaign's `reply-playbook.md` (source of classification rules and response templates) and `pipeline-stages.md` (for stage advances).
3. Read `config.json` for master campaign IDs.

## Step 1: Pull new replies in parallel

Delegate both in one message (parallel Task calls):

1. `gtm-instantly-operator`:
```
op: pull_replies
campaign_slug: <slug>
since_timestamp: <derived from since arg>
```

2. `gtm-heyreach-operator`:
```
op: pull_inbox
campaign_slug: <slug>
since_timestamp: <same>
```

Each returns an array of `{id, lead_name, lead_email_or_url, classification, body, suggested_response, playbook_scenario}`.

## Step 2: Merge and sort

Merge the two arrays. Sort by classification priority:
1. positive_meeting (highest)
2. interested
3. question
4. wrong_person
5. not_now
6. unsubscribe (lowest)

## Step 3: Per-reply triage loop

For each reply in priority order:

1. Display:
   - Source (email / LinkedIn)
   - Lead context (name, company, stage in Attio if available)
   - Reply body (verbatim)
   - Classification
   - Matched reply playbook scenario
   - Suggested response (from reply-playbook.md)

2. Ask: "Send this response? (yes / no / edit)".

3. On `yes`:
   - Delegate send back to the right specialist:
     - Email: `gtm-instantly-operator` `{op: send_reply, reply_id, response_body}`
     - LinkedIn: `gtm-heyreach-operator` `{op: send_message, conversation_id, response_body}`
   - Specialist will also hand off to `gtm-attio-librarian` to log the reply and advance stage. Confirm both actions happened.

4. On `edit`:
   - Prompt: "Provide the revised response:".
   - After the user pastes, repeat the confirm step.

5. On `no`:
   - Log the classification to Attio via `gtm-attio-librarian` {op: log_reply, ... new_stage: null} so the reply is recorded but no stage advance.
   - Move to next reply.

## Step 4: Batch summary

At the end:

```
## Reply triage complete: <campaign_slug>

- <N> replies handled
- <S> sent, <E> edited, <K> skipped
- Breakdown: <P> positive_meeting, <I> interested, <Q> question, <W> wrong_person, <NN> not_now, <U> unsubscribe
- Stages advanced: <count>
- Time taken: ~<estimate>
```

## Failure modes

- If an email or LinkedIn reply has no matching playbook scenario, present it and ask the user to draft a response manually. Do not guess.
- If Attio log fails for any specific reply, continue but flag in the summary so the user can fix manually.
- If >15 replies are in the queue, offer to split into two sessions (high-priority first).
