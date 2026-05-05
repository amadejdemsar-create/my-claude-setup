---
name: booking-review-report
description: |
  Given a hotel name OR a Booking.com URL, scrape ALL the property's reviews
  from booking.com/reviewlist.*.html via Firecrawl, combine them into a
  canonical reviews.json, run the existing analyze_reviews pipeline, and
  produce a Nevron-branded Slovenian sentiment-analysis HTML report. Replaces
  the older booking-review-scrape and hotel-review-analysis skills.

  Use when the user says "make a review analysis for <hotel>", "scrape and
  analyze reviews for <hotel>", "make a Nevron review report for <hotel>",
  "naredi analizo ocen za <hotel>", or hands over a Booking URL and wants the
  full deliverable. Also accepts an existing reviews JSON file as input — in
  that case the skill skips scraping and goes straight to analysis.
---

# booking-review-report

End-to-end pipeline that turns a hotel name or Booking URL into a finished
Nevron-branded Slovenian review-sentiment HTML report.

Skill base directory: `~/.claude/skills/booking-review-report/`

## ⚠️ Internal-use only — Booking ToS

Booking.com's Terms (section A15.2) **prohibit automated access, scraping, and
"AI-powered assistants" interacting with the platform**, and `robots.txt`
disallows `/reviewlist.*.html` for every user-agent. This skill scrapes that
exact path. Therefore:

- **Internal research only.** Use this for sales prospecting, internal
  competitive analysis, and Nevron content. Never expose the scrape pipeline
  to a third party.
- **Do NOT ship as a SaaS, hotel-facing webapp, or partner-facing API.**
  If a hotel wants a report, switch to legitimate sources: their Booking
  Extranet review export (CSV they download themselves), a partner-API
  provider (Revinate / TrustYou / ReviewPro / Customer Alliance), Google
  Business Profile API, or TripAdvisor Content API.
- **Do NOT publish the resulting report on a public, indexable URL.** Reports
  belong on Nevron's noindexed report subdomains (`<slug>.nevron.co`) or in
  internal docs only.
- **Do NOT scrape at scale or in tight loops** — Booking actively blocks
  scrapers (section A15.3). Stay below ~150 page-fetches per hotel and don't
  batch more than ~10 requests in parallel.
- If the user asks for a productized version, refer them back to the
  alternatives above. Do not silently bake this scraper into a customer-facing
  product.

The legal analysis with verbatim ToS clauses lives in this conversation's
session-2026-05-04 archive (search for "Booking documentation legal" or
"section A15.2" if you need to refresh).

## When to use

- User gives a hotel name (with optional city) and wants a full review-sentiment
  HTML report. Example: `/booking-review-report NEU Residences` or
  `/booking-review-report Hotel Habakuk Maribor`.
- User pastes a Booking.com hotel URL or `reviewlist` URL.
- User points to an already-scraped reviews JSON and wants the HTML built from
  it (skip steps 1-6, jump to step 7).
- User wants to refresh an existing report after new reviews accrued.

## When NOT to use

- The user wants to build or sell anything to hotels. See the ToS warning above.
- The user wants reviews from Google / TripAdvisor / Expedia. Pivot to a
  partner API or write a separate skill.
- Less than 50 reviews. The analysis pipeline assumes enough volume to find
  statistically meaningful themes.

## High-level pipeline

```
hotel name or URL
        │
        ▼
   (1) resolve URL ────► confirm with user ◄── GATE
        │
        ▼
   (2) live header fetch (proxy=basic) → property name, total reviews, overall score, sub-scores
        │
        ▼
   (3) gather facts ────► confirm with user ◄── GATE
        │  rooms (web-lookup), occupancy (default 0,65), template, Nevron status, cutoff
        ▼
   (4) cost preview ────► confirm with user ◄── GATE
        │  ceil(N/25) pages × 1 credit, ~Y minutes wall time
        ▼
   (5) parallel scrape pages 1..P (Firecrawl basic proxy)
        │  save raw markdown to <out>/raw/page-NNN.md
        ▼
   (6) parse_reviewlist.py → reviews.json
        │
        ▼
   (7) analyze_reviews.py --cutoff <date> → stats.json + liked.txt + disliked.txt
        │
        ▼
   (8) deep theme analysis (subagent reads dumps, writes analysis.json)
        │
        ▼
   (9) render HTML (subagent uses Habakuk template — see "HTML build")
        │
        ▼
   (10) open in browser
```

## Scripts in this skill

| File | Purpose |
|---|---|
| `scripts/inspect_reviews.py` | Quick schema check on any review JSON |
| `scripts/analyze_reviews.py` | stats.json + liked.txt + disliked.txt; supports `--cutoff` for before/after split |
| `scripts/parse_reviewlist.py` | Reads `<dir>/page-*.md` Firecrawl outputs and writes a unified `reviews.json` |

## Step 1 — Resolve URL

Inputs are one of:

1. **Hotel name** (with optional city) — search for `"<hotel name> <city> site:booking.com/hotel"` via `mcp__firecrawl__firecrawl_search`. Pick the result whose URL matches `booking.com/hotel/<cc>/<slug>.html`. If multiple hotels share a name, ask the user to disambiguate by city.
2. **Booking.com hotel URL** — extract `<cc>` and `<slug>` directly.
3. **Booking.com reviewlist URL** — already in canonical form, just normalize.

Build the canonical reviewlist URL:

```
https://www.booking.com/reviewlist.en-gb.html?cc1=<cc>&pagename=<slug>&customer_type=total&order=completed_desc&page=<N>&r_lang=all&rows=25
```

`rows=25` is the maximum Booking will serve via this endpoint; higher values are silently clamped.

Also build the hotel landing URL for facts:

```
https://www.booking.com/hotel/<cc>/<slug>.html
```

## Step 2 — Live header fetch (one Firecrawl call)

Scrape `https://www.booking.com/reviewlist.en-gb.html?cc1=<cc>&pagename=<slug>&customer_type=total&order=completed_desc&page=1&r_lang=all&rows=25` with:

```
proxy: "basic"
formats: ["markdown"]
waitFor: 2000
onlyMainContent: true
```

From the returned markdown extract:

- **Total reviews**: regex `Guest reviews\s*\((\d[\d,\.]*?)\)` → integer
- **Total pages**: highest number in `[(\d+)Page \1\]\(` matches → that is `P`
- **Property name**: derivable from page title metadata (Firecrawl `metadata.title`)

Then scrape the hotel page for the headline numbers (`https://www.booking.com/hotel/<cc>/<slug>.html`) with `formats: ["json"]` and a `jsonOptions.prompt` asking for: `propertyName`, `numberOfApartments` / `numberOfRooms`, `starRating`, `propertyType`, `addressLine`, `overallReviewScore`, `subScores` `{staff, cleanliness, comfort, facilities, value_for_money, location, free_wifi}`. The hotel landing widget reliably exposes the score breakdown that the reviewlist URL does not.

If `numberOfApartments` is null on the hotel page, fall back to the third-party listing site `https://<slug>.ljubljana-hotel.com/en/` (or your-city equivalent — pattern is `<slug>.<city>-hotel.com`). They scrape Booking's fact-sheet and expose room count.

### Step 2 — confirmation gate

Show the user the resolved facts in a compact card and ask:

```
Resolved: <property name> in <city>, <stars>★ <type>.
  Apartments / rooms: <N>
  Total reviews on Booking: <X> (across <P> pages of 25)
  Overall score: <Y>
  Sub-scores: Staff <a> · Cleanliness <b> · Comfort <c> · Facilities <d> · Value <e> · Location <f> · WiFi <g>
  Reviewlist URL: https://...

Is this the right hotel? (yes / different one / cancel)
```

Only proceed when the user confirms.

## Step 3 — Gather missing facts

Ask only what's still missing or auto-pickable:

| Fact | How to get it |
|---|---|
| `slug` | from the URL (`<slug>` segment), kebab-case |
| `name_sl` | usually same as Booking property name; user can override |
| `rooms` | from step 2 hotel-page extract; if null, ask |
| `occupancy` | default `0,65` unless user overrides |
| `stars` | from hotel page |
| `template` | propose based on hotel type — see "Hospitality Index template selection" below |
| `nevron_status` | ask: none / IPTV-only / IPTV + Mobile / Full suite |
| `cutoff` | default to 9 months back from latest `review_date`; if span < 12 months, skip the `#fixed` section entirely |

### Hospitality Index template selection (proposal)

| Hotel type signal | Template |
|---|---|
| Has dedicated wellness/spa, mountain/lake setting | WELLNESS |
| Apartment hotel / aparthotel / serviced apartments | BOUTIQUE (consider renaming "Hrana in pijača" → "Apartma in oprema") |
| Thermal spa hotel | THERMAL_WELLNESS |
| Lake (Bled) prestige | LAKE_GRAND |
| Lake wellness | LAKE_WELLNESS |
| Garni / B&B / city budget | GARNI |
| Coastal prestige | SEASIDE_GRAND |
| Coastal family/mid-tier | SEASIDE_FAMILY |
| City boutique | BOUTIQUE |

Component sets and weights are documented in the legacy `hotel-review-analysis` SKILL.md and the existing chain `metadata.json` files. Keep them consistent across same-type hotels.

### Step 3 — confirmation gate

Echo the proposed template and weights, the slug, and any defaults that were filled. User confirms or overrides.

## Step 4 — Cost preview

```
This hotel has <N> reviews across <P> pages of 25.
  Estimated Firecrawl cost: P × 1 credit = ~P credits
  Estimated wall time:      P / 10 batches × ~3s = ~M minutes
  Output dir: /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/

Proceed with scrape? (yes / no)
```

Hard floor: refuse to scrape if the user has not confirmed. Hard ceiling: refuse if `P > 200` without explicit override (that's > 5,000 reviews and either the wrong hotel or a chain landing page).

## Step 5 — Parallel scrape

Create the output dir + raw subdir:

```bash
mkdir -p /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/raw
```

For pages `1..P`, call `mcp__firecrawl__firecrawl_scrape` in batches of 8-10 in parallel:

```
url:   https://www.booking.com/reviewlist.en-gb.html?cc1=<cc>&pagename=<slug>&customer_type=total&order=completed_desc&page=<N>&r_lang=all&rows=25
proxy: "basic"
formats: ["markdown"]
waitFor: 2000
onlyMainContent: true
```

After each call, save the returned `markdown` field to:

```
/Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/raw/page-NNN.md
```

(zero-padded 3-digit page number so file sort matches page order).

**Failure handling:**
- If a page returns empty markdown or contains "Just a moment" / "challenge", retry once with `waitFor: 5000`. If it still fails, mark the page as failed and continue. Don't stop the whole run.
- After all pages attempted, list any failed pages to the user. If failures are <2% of total, proceed; otherwise stop and ask.
- If Booking returns a CAPTCHA / consistent block, switch `proxy: "stealth"` (5 credits/page) for the remaining pages and warn the user about the cost increase.

**Polite rate limiting:**
- Max 10 parallel requests at a time (Firecrawl concurrency).
- 1-2 second jitter between batches.
- Total wall time for ~150 pages ≈ 1-3 minutes.

## Step 6 — Parse markdown to JSON

```bash
python3 ~/.claude/skills/booking-review-report/scripts/parse_reviewlist.py \
  /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/raw \
  --output /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/reviews.json \
  --property-id 1 \
  --property-name "<Booking property name>" \
  --source-url "<reviewlist URL with page=1>" \
  --reported-total <N from header> \
  --overall-score <score from hotel page> \
  --substaff <a> --subclean <b> --subcomfort <c> --subfac <d> \
  --subvalue <e> --subloc <f> --subwifi <g>
```

The script:
- Reads `page-*.md` in lexical (= page) order
- Splits each page's markdown into individual review blocks at `\n\n- ![`
- Parses each block: reviewer name, country (+ ISO-2 from flag URL), reviewer type, room type, nights, stay month, review date, score, title, liked, disliked, property response, language (heuristic detector)
- Dedupes by SHA1 hash of `name|date|title`
- Sorts newest-first
- Writes the canonical `reviews.json` shape that `analyze_reviews.py` already consumes

Verify: scraped count must be >= 98% of `total_reviews_reported`. If lower, list missing pages and ask whether to retry.

## Step 7 — Stats

```bash
python3 ~/.claude/skills/booking-review-report/scripts/analyze_reviews.py \
  /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/reviews.json \
  --dump-texts /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/ \
  --cutoff <YYYY-MM-DD> \
  > /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/stats.json
```

Outputs:
- `stats.json` (distribution, segments, countries, monthly trend, keyword counts, before/after cutoff aggregates)
- `liked.txt` (one positive review per line, all languages)
- `disliked.txt` (one negative review per line, all languages)

## Step 8 — Deep theme analysis (subagent)

Spawn a `general-purpose` subagent with model `opus` and a self-contained brief
that hands off:
- Path to `stats.json`, `liked.txt`, `disliked.txt`
- The hotel facts and chosen template + weights
- The cutoff date (so it can split themes into resolved vs current)
- Anchors to the reference HTML templates: `/Users/Shared/Domain/Assets/Nevron/clients/habakuk/report.html` and `/Users/Shared/Domain/Assets/Nevron/clients/julianalps/report.html`
- The mandatory style rules (Slovenian, no dashes, no fragment pairs, Slovenian number format, revenue formula)

The subagent's job is to:
1. Read both text dumps in full.
2. Extract 8+ strengths with verbatim quotes.
3. If the dataset spans 12+ months: extract 2-6 themes that meet the resolved/partial qualification rules and write them to a `fixed_problems` array.
4. Extract 10+ weaknesses tiered KRITIČNA / VISOKA / SREDNJA, each with quotes and a `Priporočilo:` line. Themes already in `fixed_problems` may not appear at KRITIČNA/VISOKA.
5. Score each Hospitality Index component 0-100 with rationale tied to text evidence.
6. Compute the action plan revenue using `<rooms> × <occupancy> × <uplift> × 10 EUR × 365`.
7. Write `analysis.json` with the structured output.

Brief template — copy into the subagent prompt verbatim, filling in placeholders:

```
You are extracting themes from a Booking.com review dataset and authoring a
Nevron-branded sentiment analysis. Output: analysis.json plus a finished
HTML report at <out>/<slug>-review-analysis.html.

(1) Read in full:
  - /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/stats.json
  - /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/liked.txt
  - /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/disliked.txt
  - ~/.claude/skills/booking-review-report/templates/single-hotel-reference.html  (PRIMARY TEMPLATE for single-hotel reports)
  - /Users/amadejdemsar/.claude/skills/booking-review-report/SKILL.md
  - The skill rules in ~/.claude/CLAUDE.md (style, dates, Slovenian)

(2) Hotel facts (paste the resolved values):
  ...

(3) Hospitality Index template (paste components + weights):
  ...

(4) Cutoff: <date>

(5) Produce:
  - 8+ strengths with 2-4 verbatim quotes per theme, original language preserved.
  - For datasets >= 12 months: 2-6 themes in #fixed (resolved / partial / uncertain), each with before-mentions, after-mentions, before-quote, after-quote-or-silence-note. Themes here may NOT appear at KRITIČNA/VISOKA in #issues.
  - 10+ weaknesses tiered, each with quotes + recommendation line.
  - Hospitality Index per-component scores with rationale.
  - 3-phase action plan with revenue formula.
  - 4-5 Nevron product cards matching weaknesses.
  - Complaint -> Nevron solution table.
  - Conclusion 2-3 sentences.

(6) Style: Slovenian throughout, no dashes as punctuation, no dramatic
fragment pairs, dates 2. marec 2026, numbers 3.572 / 9,08 / 60 %.

(7) Output: write the HTML to <out>/<slug>-review-analysis.html. Keep all
Habakuk CSS tokens, JS for IntersectionObserver reveal + donut + scroll-top
fix + tabbar drag-scroll. Preserve diacritics. Open in browser when done.

Quality gates: see SKILL.md "Quality checklist" section. Don't declare done
unless every item is met.
```

## Step 9 — HTML build

There are two reference templates inside this skill:

| Template | Path | When to use |
|---|---|---|
| Single hotel | `~/.claude/skills/booking-review-report/templates/single-hotel-reference.html` | One Booking property per report. Default for this skill. |
| Chain | `~/.claude/skills/booking-review-report/templates/chain-reference.html` | Multiple related properties under one chain (e.g., Sava Hotels & Resorts). Includes hotel-switcher tabbar, compare mode, mini-gauge grid. Single-hotel pipeline does NOT use this — switch templates only when you're aggregating multiple JSONs. |

The subagent writes the HTML using the relevant template as a 1:1 structural reference. CSS tokens, JS scaffolding, Nevron branding, and section markup all come from there.

### Single-hotel-only conventions (apply when using `single-hotel-reference.html`)

- Section order (top to bottom): nav, hero + gauge, strengths, hospitality index, fixed (only if dataset spans 12+ months), issues, guest profile, action plan, Nevron solutions, conclusion, footer.
- Anchors in nav: `#strengths`, `#index`, `#fixed` (conditional), `#issues`, `#tech`, `#plan`, `#nevron`.
- All gauges sized 360px unless layout truly forces smaller.
- Annotations on the monthly-trend chart must sit OUTSIDE the data plot area (leader lines plus an extended SVG viewBox like `0 -16 740 280`). Never on top of value labels — collision with the score labels was a real defect in the NEU Residences first draft.

### Chain-only conventions (apply when using `chain-reference.html`)

These exist BECAUSE the chain page has a sticky tabbar and a hotel switcher; they are NOT needed in single-hotel reports.

- `<script>history.scrollRestoration = 'manual'; if (location.hash) history.replaceState(null, '', location.pathname + location.search); window.addEventListener('load', () => window.scrollTo(0, 0));</script>` immediately after `</style>`. Without this, refresh leaves the chain page mid-scroll on whatever hotel panel was last viewed.
- Tabbar CSS: `scrollbar-width: none; cursor: grab; user-select: none;` plus `.hotels-tabbar::-webkit-scrollbar { display: none; }` and `.hotels-tabbar.is-dragging { cursor: grabbing; }`.
- Tabbar drag-scroll JS (mousedown / mousemove / mouseup with click suppression for moves > 4px, plus vertical-wheel-to-horizontal translation) so the hotel switcher pans without a visible scrollbar.
- Per-hotel detail panels can be plaintext (default) or AES-GCM encrypted with `cryptography` PBKDF2-SHA256 (100.000 iterations) + AES-256-GCM. Encrypted variant lives in `/Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/sava-hotels/build/build_chain_html.py`. The unlocked reference template here has all panels plaintext for editing convenience.

## Step 10 — Open

```bash
open /Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/<slug>-review-analysis.html
```

Then verify in the browser before declaring done:
- Donut animates to the score
- Component bars fill smoothly
- Reveal-on-scroll fires for each section
- Diacritics render correctly (č, š, ž)
- No `data-ciphertext`, no leftover lock emojis or "ODPRT" badges
- Tabbar (if present) drag-scrolls without visible scrollbar
- Refresh returns to top, not mid-page

## Quality checklist (before "done")

Single hotel:
- [ ] reviews.json has scraped count >= 98% of header total
- [ ] All scraped pages parsed; no `…` (U+2026) truncation in liked/disliked
- [ ] At least 4 languages represented (typical Slovenia/Adriatic property: sl, en, de, it, hr, hu)
- [ ] Hospitality Index gauge + component bars render with correct colors
- [ ] 8+ strengths with verbatim quotes (original language)
- [ ] If dataset >= 12 months: `#fixed` section with 2-6 themes, badges colored correctly, before/after quotes
- [ ] No theme appears in BOTH `#fixed` and `#issues` at HIGH/CRITICAL
- [ ] 10+ weaknesses tiered, each with `Priporočilo:` line
- [ ] Score distribution, countries, segments, monthly trend charts render
- [ ] 3-phase action plan with revenue formula
- [ ] Nevron product cards with "Rešuje:" line
- [ ] Complaint -> solution table
- [ ] No forbidden dashes or fragment pairs anywhere in prose
- [ ] All numbers in Slovenian format
- [ ] Refresh on the rendered HTML returns to top of page
- [ ] Visually inspected in browser

If any checkbox is unmet, say "partially complete" with a punch list.

## Common failure modes

- **Booking redirects reviewlist URL to hotel landing**: caused by the modern `/reviews/si/hotel/...` SPA URL. Always use the legacy `/reviewlist.en-gb.html?cc1=...&pagename=...` form. The `force_referer=google.com` injection in the response URL is fine — page still renders.
- **Empty markdown response**: `chal_t` query param = anti-bot challenge. Retry with longer waitFor or switch to `proxy: "stealth"` for that page.
- **Parser misclassifies language**: heuristic only. The detector lives in `parse_reviewlist.py::detect_language`; add language-specific tokens there if you see consistent misses for a market. Acceptable noise — doesn't affect downstream theme analysis.
- **Property responses appearing twice**: Booking ships a preview + full text concatenated by `…`. The parser keeps whichever half is longer.
- **Subagent forgets style rules**: re-paste the rules in the brief. The CLAUDE.md global rules apply but the subagent doesn't always read them. Be explicit.
- **HTML missing scroll-to-top fix**: every report needs the inline script after `</style>`. Verified bug from 2026-05-04 session.

## Deletion of legacy skills

After this skill is verified working on a fresh hotel:

```bash
rm -rf ~/.claude/skills/booking-review-scrape/
rm -rf ~/.claude/skills/hotel-review-analysis/
rm -rf /Users/Shared/Domain/Code/Personal/my-claude-setup/skills/hotel-review-analysis/
```

Update `/Users/Shared/Domain/Code/Personal/my-claude-setup/index.html` to point its `/hotel-review-analysis` install card to `/booking-review-report` (or remove that card entirely until the new skill is published).

## Notes

- This skill produces single-hotel reports only. The chain workflow still uses `/Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<chain-slug>/build/build_chain_html.py` for now. Merging chain support into this skill is a future improvement.
- Output paths follow the workspace convention: outputs under `/Users/Shared/Domain/Context/Business/nevron/products/new-entry/review-sentiment/<slug>/`. The polished client-facing copy can be moved to `/Users/Shared/Domain/Assets/Nevron/clients/<slug>/report.html` when sharing.
