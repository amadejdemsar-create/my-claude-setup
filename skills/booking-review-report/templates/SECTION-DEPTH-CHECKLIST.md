# Section Depth Checklist for Single-Hotel Reports

The subagent must MATCH the depth of `single-hotel-reference.html` (Hotel Habakuk reference, ~2.877 lines) and not compress sections. The Bled Rose first draft was 880 lines (~30 % of reference) and got rejected for shallow content. Use this checklist when authoring.

## Required sections, in order, with depth targets

Numbers in parentheses are line counts in Habakuk's `single-hotel-reference.html`. Match within +/- 30 %. Single-hotel reports without major Nevron-tech presence may legitimately drop the Tech section, but everything else must be present.

| # | Section | Anchor | Lines | Must contain |
|---|---|---|---|---|
| 1 | Nav | (n/a) | ~25 | Real Nevron SVG logo (verbatim from `templates/nevron-logo-nav.svg`), 7-9 anchor links |
| 2 | Hero | `#top` | ~25 | Hotel name, sub-heading, hero metrics row (4-6 stat cards: ocen, povprečje, % 9-10, sob, vodilni trg, doba) |
| 3 | Hospitality Index | `#index` | ~200 | Big donut gauge (360px), 7 component bars with scores + rationale, formula card |
| 4 | Pregled (Overview) | `#overview` | ~175 | Score distribution bar chart (10-1), top countries bar chart, segments table, room-types table, monthly trend line chart with anomaly annotations OUTSIDE the plot area |
| 5 | Strengths | `#strengths` | ~90 | 8+ strength cards each with mention count, description, 2-4 verbatim quotes (original language, NEVER translated) |
| 6 | Weaknesses (raw) | `#weaknesses` | ~130 | 10-15 weakness cards with mention counts and quotes (NOT yet tiered — that's #issues) |
| 7 | Verjetno že rešeno | `#fixed` | ~60 | 2-6 themes with badges (resolved green / partial yellow / uncertain orange), before-period mention count + quote, after-period mention count + quote OR silence note |
| 8 | Aktualne težave | `#issues` | ~200 | 10+ themes split into KRITIČNA / VISOKA / SREDNJA tiers, each with quotes + `Priporočilo:` line. NO overlap with #fixed at HIGH/CRITICAL. |
| 9 | Tech / Guest Experience | `#tech` | ~165 | Optional. Include when there are 30+ tech-related mentions (TV, Wi-Fi, app, digital). Score Tech as a sub-component, list strengths and pain points, recommend specific Nevron product modules. |
| 10 | Akcijski načrt | `#plan` | ~165 | **3 phases (0-30 dni, 1-3 mesece, 3-12 mesecev)** with **5-9 action-cards per phase**. Each action-card: name + impact badge (Visok/Srednji/Nizek vpliv) + cost badge (Brez stroška/Nizek/Srednji/Visok strošek). Phases use color-coded dots. |
| 11 | Nevron solutions | `#solutions` or `#nevron` | ~250 | Big revenue number formula card. 4-6 product-cards each with: icon, name, "Rešuje:" line listing weaknesses addressed, mention count, "Naslovi" tag. Complaint → Nevron solution table (5-8 rows). |
| 12 | Footer | (n/a) | ~20 | Verbatim from `footer-snippet.html`. NEVER add a "Zaključek" / Conclusion section above the footer — Habakuk does NOT have one and rejecting agents kept inserting it. The Nevron solutions section already serves as the close. |

**Total target: 1.500-2.900 lines.** If your output is below 1.500, you compressed too aggressively — go back and expand the sections marked above.

## Mandatory verbatim copies from the template

These cannot be improvised. Each snippet file lives in `~/.claude/skills/booking-review-report/templates/`:

- **`nevron-logo-nav.svg`**: paste verbatim inside `<div class="nav__logo">`. NEVER hand-roll a diamond+text placeholder.
- **`hero-snippet.html`**: the hero section needs the FULL Habakuk-style header: big Nevron SVG logo + "smart solutions for smart hotels" tagline + `Nevron Guest Intelligence Report` pretitle + property name H1 + subtitle + date + scroll arrow. Copy the snippet, only swap data placeholders (hotel name, review count, span). NEVER ship a hero with only stat cards.
- **`footer-snippet.html`**: footer needs the FULL Nevron logo + "To poročilo je pripravljeno kot del Nevronove storitve Guest Intelligence" copy + `info@nevron.eu` + `www.nevron.eu` + copyright. Always copy verbatim.
- **`issue-bubble-chart-snippet.html`**: paste inside the issues section as the visual summary above the tiered KRITIČNA/VISOKA/SREDNJA cards. Adapt SVG `<circle>` r= to match this hotel's mention counts (radius proportional to mention count). NEVER skip — the bubble chart is the visual hook of the issues section.
- **`tech-section-snippet.html`**: include `#tech` section if there are 30+ tech-related mentions in disliked.txt (TV, WiFi, digital, app, kontrola). Adapt the Tech Index gauge value, the 4 stat cards, and the "Razčlenitev po kategorijah" bars (Digitalna komunikacija, Wi-Fi in internet, TV in zabava). NEVER drop this section unless the data simply doesn't support it (<10 tech mentions).
- **CSS variables and tokens**: copy the `:root { --m1: #000126; ... }` block verbatim from the reference.
- **Reveal animation JS**: the `IntersectionObserver` setup that adds `is-visible` class.
- **Donut animation JS**: the `animateGauge()` / `donut-ring` SVG transform.
- **Component bar fill JS**: `animateBars()` that reads `data-width` and sets actual width.
- **Color thresholds**: green ≥75, yellow 55-74, red <55 (consistent across all charts).

## Action plan card pattern (verbatim)

```html
<div class="action-card reveal">
  <div class="action-card__name">Concrete action label here</div>
  <div class="action-card__badges">
    <span class="action-card__badge action-card__badge--impact-high">Visok vpliv</span>
    <span class="action-card__badge action-card__badge--cost-low">Nizek strošek</span>
  </div>
</div>
```

Impact badges: `--impact-high` (red), `--impact-med` (yellow), `--impact-low` (gray). Cost badges: `--cost-none`, `--cost-low`, `--cost-med`, `--cost-high`.

Phase header pattern:

```html
<div class="phase reveal">
  <div class="phase__dot" style="background:var(--green);"></div>
  <div class="phase__header">
    <span class="phase__name">Faza 1: Takojšnji ukrepi</span>
    <span class="phase__time">0 do 30 dni</span>
  </div>
  <div class="phase__actions stagger">
    <!-- action-cards here -->
  </div>
</div>
```

Phase dots: green (Phase 1, takoj), `var(--m4)` cyan (Phase 2, kratkoročno), `var(--m3)` deep blue (Phase 3, srednjeročno).

## Internal template names must NEVER appear in customer-facing copy (NON-NEGOTIABLE)

The Hospitality Index templates (`LAKE_GRAND`, `LAKE_WELLNESS`, `BOUTIQUE`, `WELLNESS`, `THERMAL_WELLNESS`, `SEASIDE_GRAND`, `SEASIDE_FAMILY`, `GARNI`) are INTERNAL identifiers. They must NEVER appear in subtitles, captions, body copy, or any visible text. Translate them to natural Slovenian prose instead:

| Template code (internal) | Customer-facing prose (Slovenian) |
|---|---|
| `LAKE_GRAND` | jezerski hotel višjega razreda |
| `LAKE_WELLNESS` | blejski wellness hotel |
| `BOUTIQUE` | butični hotel / aparthotel |
| `WELLNESS` | wellness hotel |
| `THERMAL_WELLNESS` | termalni spa hotel |
| `SEASIDE_GRAND` | prestižni obmorski hotel |
| `SEASIDE_FAMILY` | obmorski družinski hotel |
| `GARNI` | garni hotel |

Forbidden: "po predlogi LAKE_GRAND", "(predloga BOUTIQUE)", "WELLNESS template", any all-caps code in body copy. Acceptable: "prilagojenih jezerskemu hotelu višjega razreda", "značilnosti butičnega hotela", "tipičen termalni spa".

## Quote handling rules (NON-NEGOTIABLE)

Every subagent run must enforce these. The rule was inverted earlier; this is the correct version.

1. **Translate every foreign-language guest quote to natural Slovenian** AND append `<span class="tech-quote__translated">prevedeno iz XX</span>` to indicate the source language.
   - Slovenian quotes: stay verbatim, NO badge
   - English: translate, append `prevedeno iz EN`
   - German: translate, append `prevedeno iz DE`
   - Italian: `prevedeno iz IT`. French: `prevedeno iz FR`. Croatian: `prevedeno iz HR`. Serbian: `prevedeno iz SR`. Hungarian: `prevedeno iz HU`. Dutch: `prevedeno iz NL`. Spanish: `prevedeno iz ES`. Portuguese: `prevedeno iz PT`. Czech: `prevedeno iz CS`. Slovak: `prevedeno iz SK`.
2. **Translation must be natural Slovenian**, NOT word-for-word. Preserve emotional tone. Keep proper nouns (person names, hotel names, place names) untouched.
3. **NEVER ship a foreign quote without translation.** A German or Hungarian quote with no Slovenian readers can read is worse than nothing — Habakuk's reference template translates everything.
4. **Format inside the existing quote element**:
   ```html
   <div class="strength-card__quote">"Slovenian translation here." <span class="tech-quote__translated">prevedeno iz EN</span></div>
   ```
3. **Country names in Slovenian with FULL diacritics** when displayed in the report. Use this lookup, do not improvise:
   - Germany → **Nemčija** (NOT Nemcija)
   - Croatia → **Hrvaška** (NOT Hrvaska)
   - Hungary → **Madžarska** (NOT Madzarska)
   - Czech Republic → **Češka** (NOT Ceska)
   - Slovakia → **Slovaška**
   - Spain → **Španija**
   - Switzerland → **Švica**
   - Sweden → **Švedska**
   - Greece → **Grčija**
   - United Kingdom → **Velika Britanija**
   - United States → **ZDA**
   - Italy → Italija
   - France → Francija
   - Austria → Avstrija
   - Slovenia → Slovenija
   - Serbia → Srbija
   - Bulgaria → Bolgarija
   - Netherlands → Nizozemska
   - Belgium → Belgija
   - Poland → Poljska
   - Romania → Romunija
4. **Slovenian word diacritics**: če pišeš katero od teh ASCII-renderirano, je bug:
   - `kljucn` → ključn (ključnih, ključne)
   - `povprecn / povprecje` → povprečn / povprečje
   - `vec / Vec` → več / Več
   - `vecj` → večj (večji, večja)
   - `cas / Cas` → čas / Čas
   - `nacrt / Nacrt` → načrt / Načrt
   - `nacin / Nacin` → način / Način
   - `znacil` → značil
   - `tezav` → težav
   - `tezk` → težk (težki, težko)
   - `oznacen` → označen
   - `sestev` → seštev (seštevek)
   - `splosn` → splošn (splošno)
   - `nastet / nasteti` → naštet (našteti)
   - `specifin / specificn` → specifičn (specifične)
   - `Zakljucek / Najvecja / tocke` → Zaključek / Največja / točke
   - `vsec / všec` → všeč
   - `noc / Noc / noci` → noč / Noč / noči
   - `razlicn / razlicnim` → različn (različnimi, različno)
   - `natancn` → natančn
   - `vkljuc / izkljuc` → vključ / izključ
   - `tisoc` → tisoč
   - `placljiv / doplacil` → plačljiv / doplačil
   - `Nemcija / Hrvaska / Madzarska / Ceska / Slovaska / Spanija / Svica / Svedska / Grcija` → Nemčija / Hrvaška / Madžarska / Češka / Slovaška / Španija / Švica / Švedska / Grčija
   - `siroko / sirok / sibk / Sibk` → široko / širok / šibk / Šibk
   - `mozno / Mozno / moznost` → možno / Možno / možnost
   - `dolzin` → dolžin
   - `dosezk / Dosezk / doseze` → dosežk / Dosežk / doseže
   - `vazno / Vazno` → važno / Važno
   - `sele / Sele` → šele / Šele
   - `ze / Ze` (kot beseda, ne v "već") → že / Že
   - `ucinkovit / Ucinkovit` → učinkovit / Učinkovit
   - `zacet / Zacet / zacasn / zascit` → začet / Začet / začasn / zaščit
   - `trzn / Trzn` → trž / Trž (tržni)
   - `drzav / Drzav` → držav / Držav
   - `izrecn` → izrečn (izrečno)

   The Bled Rose run needed 4+ rounds to clean these. Run the self-check grep before declaring done.

## Self-check before declaring done

Run these greps against your output before saying "done":

```bash
# Logo present (in nav AND in hero AND in footer)
grep -c 'M244.3,93.9\|M254.4,97.8' <output>.html  # should be >=2 (nav + hero/footer)

# Hero structure (full, not just stat cards)
grep -c 'hero__pretitle' <output>.html             # must be 1
grep -c 'hero__title' <output>.html                # must be 1
grep -c 'hero__metric-value' <output>.html         # MUST be 0 — no stat cards in hero

# Footer structure
grep -c 'footer__text' <output>.html               # must be 1
grep -c 'info@nevron.eu' <output>.html             # must be 1

# Required visual sections
grep -c 'bubble-chart' <output>.html               # must be >=2 (issue magnitude bubble visualization)
grep -cE 'tech-section|id="tech"' <output>.html    # must be >=1 (Guest Experience Technology)

# Action plan depth
grep -c 'action-card__name' <output>.html          # should be 15-25 across 3 phases
grep -c 'phase__dot' <output>.html                 # should be 3

# Length and dash check
wc -l <output>.html                                # 1500-3300 lines
grep -cE '—|–' <output>.html                       # MUST be 0

# Translation badges PRESENT for foreign quotes (most non-Slovenia hotels have lots)
grep -c 'prevedeno iz' <output>.html       # should be ~25-50 for an international Slovenia property
# No untranslated foreign-language quote starters left in __quote elements
grep -cE '__quote">"(Der|Die|Das|Sehr|Wir|Ich|War) ' <output>.html  # MUST be 0
grep -cE '__quote">"(Le|La|Les|Très|J&#39;ai|C&#39;est) ' <output>.html   # MUST be 0
grep -cE '__quote">"[A-Z][a-z]+ (is|are|was|were|the|an|a) ' <output>.html  # MUST be 0 (English starters)

# No ASCII-stripped Slovenian (extensive list — Bled Rose needed 4 rounds because regex was too narrow)
grep -cE '\b(kljucn|povprecn|povprecj|nacrt|nacin|znacil|specifin|specificn|sestev|tezav|oznacen|tezk|cas|vecj|vec\b|Vec\b|izboljsa|drzav|izrecn|nujn|nastet|splosn|vsec|všec|noc\b|noci|razlicn|natancn|vkljuc|izkljuc|tisoc|placljiv|doplacil|Zakljucek|Najvecja|tocke|tocka|Mozno|mozno|moznost|dolzin|dosezk|doseze|vazno|sele\b|Sele\b|ze\b|Ze\b|ucinkovit|zacet|zacasn|zascit|trzn|sirok|sibk|Sibk)' <output>.html  # MUST be 0

# No ASCII country names
grep -cE '\b(Nemcija|Hrvaska|Madzarska|Ceska|Spanija|Svica|Slovaska|Grcija)\b' <output>.html  # MUST be 0

# No internal template names leaking into customer copy
grep -cE '\b(LAKE_GRAND|LAKE_WELLNESS|BOUTIQUE|WELLNESS|THERMAL_WELLNESS|SEASIDE_GRAND|SEASIDE_FAMILY|GARNI)\b' <output>.html  # MUST be 0
```

If any check fails, fix and re-verify before declaring done.
