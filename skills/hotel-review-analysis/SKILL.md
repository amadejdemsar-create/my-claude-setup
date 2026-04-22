---
name: hotel-review-analysis
description: "Turn a JSON file of Booking.com scraped reviews for a single hotel into a full Slovenian review sentiment analysis document in the Nevron format. Use when the user says things like 'analyze reviews for <hotel>', 'make a review analysis from this JSON', 'build the hotel review sentiment doc', or points at a scraped Booking.com JSON for a hotel."
user_invocable: true
---

# Hotel Review Analysis

Produce a Nevron-style Slovenian review sentiment analysis from a JSON of Booking.com reviews for one hotel. Output matches the standard Nevron deliverable structure so every hotel analysis is consistent.

## Reference analyses (read one before starting)

If you have access to any existing Nevron review analysis on your machine (e.g. Habakuk, Julian Alps), read one as a concrete structural example. Otherwise follow the skeleton at `~/.claude/skills/hotel-review-analysis/templates/review-analysis-template.md`, which contains the full section order with placeholders.

## When to use

- User hands over a JSON of scraped Booking.com reviews and asks for a review analysis or sentiment report
- User wants a Nevron-style "how to raise the rating + how Nevron helps" deliverable for a new hotel
- User asks to "do the same thing we did for Habakuk / Julian Alps" for another hotel

Do NOT use this skill for:

- Non-Booking review sources (Google, TripAdvisor) without adapting schema mapping first. The statistics script assumes Booking's 1 to 10 scoring.
- Multi-hotel aggregate reports (this is per-hotel).
- Raw review dumps without sentiment analysis.

## Inputs you MUST gather before writing

Ask the user for anything missing. Do not guess these.

1. **Path to the reviews JSON file.** Required.
2. **Hotel name in Slovenian** (how it appears on the deliverable, e.g. "Hotel Habakuk", "Hotel Julian Alps").
3. **Slug for the folder** (kebab-case, no diacritics). Default to a slugified hotel name if user doesn't provide.
4. **Approximate number of rooms** (for the revenue formula).
5. **Occupancy estimate** if known. Default to 65 % if user has no data.
6. **Star rating / hotel type** (e.g. "4 zvezdice, wellness hotel", "butični hotel, 4 zvezdice").
7. **Location** (one line, e.g. "Pohorje, ob vznožju gondole", "Zgornje Gorje, blizu Bleda").
8. **Current Nevron products used, if any.** Options:
   - None (full platform opportunity)
   - IPTV only (activate modules + add Mobile + Digital Signage)
   - IPTV + Mobile (focus on NevronCore analytics, signage, integrations)
   - Full suite (focus on optimization / expansion)
9. **Output directory.** Ask explicitly. This varies per machine; there is no fixed default. Suggested pattern: a folder where you keep hotel review work on your machine. The skill will create `<output_dir>/<slug>/` and write `<slug>-review-analysis.md` inside it.
10. **Cutoff date for "older vs newer" analysis** (optional). If the dataset spans 12+ months and the hotel had a major renovation or change of management, split the dataset into a before/after comparison. If no such event, skip the comparison section entirely.

If the user gives you a JSON without context, ASK these questions first before running anything.

## Step 1: Inspect the JSON shape

Run the inspection script to understand the schema, then confirm field mapping:

```bash
python3 ~/.claude/skills/hotel-review-analysis/scripts/inspect_reviews.py "<path-to-json>"
```

It prints:
- Total record count
- Top-level keys
- Sample record
- Guessed mapping for: score, date, title, liked text, disliked text, country, reviewer type (couple / family / group / solo), room type, nights

Verify the guessed mapping. If anything looks wrong, adjust the `DEFAULT_FIELDS` block in `scripts/analyze_reviews.py` or pass overrides via `--field key=actualName` flags before running Step 2.

## Step 2: Compute statistics

```bash
python3 ~/.claude/skills/hotel-review-analysis/scripts/analyze_reviews.py \
  "<path-to-json>" \
  --cutoff "YYYY-MM-DD"   # optional, only if doing before/after split
  --dump-texts "<output_dir>/<slug>"   # writes liked.txt and disliked.txt for theme analysis
```

Outputs a JSON block with:
- Total count, overall average, median
- Score distribution (10, 9, 8, ..., 1)
- Segment split (couples, families, groups, solo)
- Room type counts (top 10)
- Country counts (top 15)
- Monthly trend (average + count per month, last 12 to 24 months)
- Before/after cutoff averages + counts (if `--cutoff` provided)
- High-signal positive keyword counts (location, staff, breakfast, wellness, pool, room, clean, design, value, pet, view, quiet, family, food, dinner, bed)
- High-signal negative keyword counts (pool hours, pool temperature, parking, cleaning, food quality, ac / temperature, noise, bathroom smell, elevator, church bells, shower design, staff attitude, wifi, outdated rooms)

Save the output to `stats.json` inside the hotel's output folder so you can reference it while writing.

## Step 3: Read the review texts and build themes

The statistics are a starting point; the real analysis comes from reading the free-text fields.

1. Extract all non-empty `liked` and `disliked` fields into two text dumps (the analysis script writes them to `liked.txt` and `disliked.txt` when you pass `--dump-texts`).
2. Read both. Identify clusters of themes (target: 8 to 15 positive themes, 10 to 20 negative themes).
3. For each theme, count approximate mentions (the keyword counts from Step 2 are a starting floor; skim for variants in multiple languages).
4. Pick 2 to 4 verbatim quotes per theme. **Keep quotes in their original language** (German, Italian, Croatian, English, French, Slovenian, etc.). Do not translate.
5. Assign each negative theme a priority: KRITIČNA, VISOKA, or SREDNJA. Criteria:
   - KRITIČNA: structural to the guest promise (wellness hours for a wellness hotel, food quality for a 4 star, temperature for guest comfort), 25+ mentions, drives low scores.
   - VISOKA: 15 to 30 mentions, clear guest frustration, fixable.
   - SREDNJA: 5 to 15 mentions, quality of life.

## Step 4: Write the analysis document

Output path: `<output_dir>/<slug>/<slug>-review-analysis.md` where `<output_dir>` is the folder the user gave in input #9.

Create the folder if it doesn't exist.

Follow this exact section order (see `templates/review-analysis-template.md` for the skeleton):

1. **Title:** `# Hotel <Name>: Analiza ocen gostov`
2. **Datum analize** (today in D. M. YYYY format), **Vir podatkov** (N ocen na Booking.com, date range), and if doing before/after: **Meja med "novejšimi" in "starejšimi"**.
3. **## Pregled** (Overview)
   - Summary metrics table (skupno ocen, skupno povprečje, before/after averages if applicable, % ocen 9+, % ocen 4-, glavni segmenti, najpogostejša soba, tip hotela, lokacija).
   - **### Porazdelitev ocen** table (count + % for each score 10 to 1).
   - **### Segmenti gostov** table (if not already in summary).
   - **### Tipi sob** table (top 7 to 10).
   - **### Države izvora gostov** table (top 10 to 15, only those with meaningful counts).
   - **### Mesečni trendi ocen** or **Sezonski trendi ocen** table (last 12 to 24 months).
   - One to two sentences of commentary on the trend.
4. **## KAJ GOSTOM VŠEČ (Ključne prednosti)** with numbered subsections. Each subsection:
   - Heading: `### N. <theme> (M+ omemb)` where M is the mention count (approximate is fine).
   - 2 to 4 sentences of description.
   - Blockquotes with verbatim reviewer quotes in original languages.
5. (OPTIONAL) **## VERJETNO ŽE REŠENO** section, only if doing a before/after cutoff comparison. Each item has Pred / Po / Ocena fields.
6. **## AKTUALNE NEGATIVNE TEŽAVE (Še vedno potrebujejo pozornost)**
   - **### KRITIČNA PRIORITETA** subsections
   - **### VISOKA PRIORITETA** subsections
   - **### SREDNJA PRIORITETA** subsections
   - Each item: heading, 2 to 4 sentences, quotes, **Priporočilo:** line with concrete fix.
7. **## MEDNARODNA MEŠANICA GOSTOV** (one paragraph on the international guest mix and whether complaints are consistent across languages).
8. **## KLJUČNI ZAKLJUČEK** (two paragraphs: strengths, the gap between promise and delivery, which issues would move the score most).
9. **## KAKO DVIGNITI OCENO: AKCIJSKI NAČRT**
   - **### Formula vpliva na prihodke** (always use Cornell/STR: 0,1 višja ocena = ~10 EUR/sobo/noč). Compute actual EUR figure for this hotel using rooms × occupancy × score uplift × 10 × 365.
   - **### Faza 1: Takojšnji ukrepi (0 do 30 dni)** table (ukrep, vpliv na oceno, strošek).
   - **### Faza 2: Kratkoročni ukrepi (1 do 3 mesece)** table.
   - **### Faza 3: Srednjeročni ukrepi (3 do 12 mesecev)** table.
   - **### Ocenjeni skupni vpliv** one paragraph with a specific projected score uplift.
10. **## KAKO LAHKO NEVRON POMAGA** — pick the variant that matches the hotel's current Nevron status:
    - **No Nevron:** lead with Nevron Mobile (PWA) as the entry, then IPTV, Digital Signage, NevronCore Analytics. Frame as "to je priložnost za uvedbo celotne platforme".
    - **IPTV only:** lead with NevronCore as the platform that already powers IPTV, then module activation (Room Care, ordering, surveys, welcome screen), then add Nevron Mobile, then Digital Signage. Frame as "X že uporablja Nevron IPTV".
    - **IPTV + Mobile or more:** frame as optimization, integration (Connectivity Hub for in-room controls), and analytics-driven upsell. Still show the complaint-to-solution table.
    - Always end with:
      - A "Celostni vpliv" table mapping complaint categories to Nevron solutions with total mention counts.
      - Total Nevron revenue impact line using the same formula (0,1 to 0,3 score uplift × 10 EUR × rooms × occupancy × 365).

## Style rules (non-negotiable)

- **Slovenian throughout**, except verbatim guest quotes (keep original language).
- **No dashes as punctuation** (no em/en/hyphen between clauses). Use commas, periods, or restructure. Compound words like "4-zvezdnični" are fine.
- **No "Not X. Y." fragment pairs** or any dramatic two-sentence constructs. Write complete sentences.
- **Date format:** `2. marec 2026`, `12. marec 2026` in prose; `YYYY-MM-DD` inside tables or code only.
- **Numbers:** Slovenian separators. Thousands with period (`2.369`), decimals with comma (`8,5`), percentages with space (`60 %`).
- **Room math:** always EUR, always `X sob × Y zasedenost × Z × 10 EUR × 365 dni = ~<total> EUR` (use multiplication sign or "x", either is fine; be consistent inside one doc).
- **Mention counts:** use approximate floor numbers ("150+ omemb", "30+ omemb") rather than exact scraped counts, unless the number is naturally precise.
- **No em dash, no "Not just X, but Y" rhetoric, no bullet-fragment lists of short pairs.** This is a business deliverable that needs to read like a senior consultant wrote it.

## Quality checklist before declaring done

Before saying the analysis is complete, verify ALL of these:

- [ ] Overview table contains 8+ metrics including segments and top room type.
- [ ] Score distribution table covers every score level with non-zero count.
- [ ] Country and room type tables present.
- [ ] Monthly trend has at least 10 months of data (or as many as the dataset allows).
- [ ] 8+ positive themes, each with mention count and 2+ verbatim quotes.
- [ ] 10+ negative themes, split across KRITIČNA / VISOKA / SREDNJA.
- [ ] Every negative theme has a concrete **Priporočilo:** line.
- [ ] International guest mix paragraph present.
- [ ] Revenue formula computed with the hotel's actual room count and occupancy.
- [ ] Three phases of action plan, each with its own table.
- [ ] Nevron section chosen based on the hotel's actual Nevron status, not a generic template.
- [ ] "Celostni vpliv" table maps complaint categories to Nevron modules with mention totals.
- [ ] Final Nevron revenue impact calculated.
- [ ] No forbidden dashes or fragment pairs anywhere.
- [ ] Quotes preserved in original languages.

If any box is unchecked, the doc is NOT done; say "partially complete" and state what remains.

## Output handoff

After writing the file:

1. Tell the user the output path.
2. Share a 6 to 8 line summary: score, top 3 strengths, top 3 critical issues, estimated revenue upside from Phase 1 + 2 alone, Nevron angle.
3. Ask whether they want a branded HTML version (for client presentation) or additional deliverables. This skill produces the markdown only.
