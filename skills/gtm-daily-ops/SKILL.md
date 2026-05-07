---
name: gtm-daily-ops
description: |
  Run the 1-hour daily operating loop for the active campaign: morning reply triage, midday LinkedIn check, afternoon Attio hygiene, end-of-day deliverability. Accepts optional campaign slug.
---

# GTM Daily Ops

The disciplined daily loop that keeps the outbound machine running.

## Arguments

- `$ARGUMENTS` optional campaign slug.

## Pre-flight

Resolve campaign. Load context as usual.

Delegate most of this to `gtm-orchestrator` {op: daily_ops, campaign_slug} for tight coordination, OR run each block inline. Prefer orchestrator delegation to keep the top-level tidy.

## Block 1: Morning reply triage (~30 min)

Invoke the /gtm-reply-triage logic inline. All replies since the last triage get handled.

## Block 2: Midday LinkedIn (~15 min)

Delegate to `gtm-heyreach-operator`:
```
op: midday_check
campaign_slug: <slug>
```

Specialist returns:
- New accepted connections (within last 24h) that have not received a first message yet.
- Unread LinkedIn inbox messages.
- Any LinkedIn account health warnings.

For each new accepted connection, suggest sending the Day 4 first message from `linkedin-copy.md`. Ask "Send? (yes/no)" per connection.

For any account warnings, flag to the user to decide if the account should be paused.

## Block 3: Afternoon Attio hygiene (~15 min)

Delegate to `gtm-attio-librarian`:
```
op: hygiene_check
campaign_slug: <slug>
```

Specialist returns:
- Records touched today but missing a note.
- Deals stuck in Contacted for >30 days.
- Deals stuck in Engaged for >7 days.
- Deals stuck in Meeting Booked but meeting has passed with no follow-up.

For each stuck deal, present the record and suggest an action (re-engage, re-tag for Q3, close as Lost). Ask "Apply? (yes / no / skip)".

## Block 4: End of day deliverability (~5 min)

Delegate to `gtm-instantly-operator`:
```
op: deliverability_check
campaign_slug: <slug>
```

Specialist returns:
- Per-mailbox delivery rate last 24h.
- Per-mailbox spam rate.
- Flagged mailboxes.

For any flagged mailbox, recommend throttling its daily send cap for tomorrow. Ask "Apply throttle? (yes/no)".

## Final daily summary

```
## Daily Ops complete: <campaign_slug> / <YYYY-MM-DD>

### Morning triage
- <N> replies handled
- Classifications: <...>

### Midday LinkedIn
- <X> new accepted connections
- <Y> first messages sent

### Afternoon Attio
- <Z> stuck deals reviewed
- <A> advanced, <R> re-tagged, <L> closed as Lost

### End of day deliverability
- <D1..Dn>% delivery per mailbox
- <F> mailboxes flagged
- <T> throttled for tomorrow

Carry over to tomorrow:
- <list any items that need user decision not made today>
```

## Time budget

Target 1 hour total. If any block runs >1.5x budgeted time, suggest reducing batch size or splitting into two half-day sessions.
