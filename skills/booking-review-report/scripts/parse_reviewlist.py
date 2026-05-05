#!/usr/bin/env python3
"""Parse Booking.com reviewlist.*.html scrape output (markdown) into JSON.

Input: a directory containing one markdown file per scraped page, named like
       page-001.md, page-002.md, ... (zero-padded so sort works lexically).
       Each file is the `markdown` field returned by Firecrawl when it scrapes
       https://www.booking.com/reviewlist.en-gb.html?...&page=N.

Output: a single JSON file at <output> in the canonical Booking review shape:

{
  "property_id": <int>,
  "property_name": <str>,
  "scraped_at": <ISO timestamp>,
  "source_url": <reviewlist URL with page=1>,
  "total_reviews_reported": <int from header, may be unknown>,
  "total_reviews_scraped": <int>,
  "overall_score": <float, may be unknown>,
  "sub_scores_aggregate": { staff, cleanliness, comfort, facilities, value_for_money, location, free_wifi },
  "reviews": [
    {
      "review_id":  "<hash of name+date+title>",
      "reviewer_name":     str,
      "reviewer_country":  str | null,
      "reviewer_type":     str | null,
      "trip_type":         str | null,
      "room_type":         str | null,
      "nights_stayed":     int | null,
      "stay_month":        str | null,        # "April 2026"
      "review_date":       str | null,        # ISO yyyy-mm-dd
      "score":             float | null,
      "review_title":      str | null,
      "positive_text":     str | null,
      "negative_text":     str | null,
      "language":          str | null,        # detected, ISO 639-1
      "is_verified":       True,
      "helpful_votes":     null,              # not exposed in legacy reviewlist
      "property_response": {"text": str, "date": null} | null,
      "sub_scores":        null,              # not per-review on legacy reviewlist
      "tags":              [],
      "submitted_from_mobile": null,
      "reviewer_review_count": null,
      "reviewer_country_code": <ISO-3166 alpha-2 from flag URL> | null
    }
  ]
}

Usage:
    python3 parse_reviewlist.py <input_dir> --output <out.json> \
        [--property-id 1] [--property-name "..."] [--source-url "..."] \
        [--reported-total 3591] [--overall-score 9.1] \
        [--substaff 9.1 --subclean 9.4 ...]

When run without overrides it tries to derive property_name and totals from
the first page's markdown.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


REVIEW_BLOCK_SPLIT = re.compile(r"\n\n- !\[", re.MULTILINE)
DATE_RE = re.compile(
    r"Reviewed:\s+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})"
)
TITLE_RE = re.compile(r"^### (.+?)$", re.MULTILINE)
NIGHTS_RE = re.compile(r"-\s+(\d+)\s+nights?\s+·")
STAY_MONTH_RE = re.compile(
    r"-\s+\d+\s+nights?\s+·\s*\n\n\s*([A-Z][a-z]+\s+\d{4})"
)
ROOM_TYPE_RE = re.compile(r"-\s+\[([^\]]+?)\]\(https://www\.booking\.com/reviewlist")
REVIEWER_TYPE_RE = re.compile(
    r"-\s+(Couple|Family with young children|Family with older children|"
    r"Family|Group|Group of friends|Solo traveler|Solo traveller|"
    r"Travelers with friends|Business traveler|Business traveller)\s*\n",
    re.IGNORECASE,
)
FLAG_RE = re.compile(
    r"!\[[^\]]*\]\(https://cf\.bstatic\.com/static/img/flags/16/([a-z]{2})/"
)
NAME_COUNTRY_RE = re.compile(
    r"^\s*([^!\n]+?)!\[[^\]]*\]\([^)]*flags/16/[a-z]{2}/[^)]+\)([^\n]+)$",
    re.MULTILINE,
)
SCORE_LINE_RE = re.compile(r"^(10|\d{1,2}\.\d)\s*$", re.MULTILINE)
LIKED_RE = re.compile(r"Liked\s*·\s*(.+?)(?=\n\nDisliked\s*·|\n\nProperty response:|\n\nHelpful\b|\Z)", re.DOTALL)
DISLIKED_RE = re.compile(r"Disliked\s*·\s*(.+?)(?=\n\nProperty response:|\n\nHelpful\b|\Z)", re.DOTALL)
PROPERTY_RESPONSE_RE = re.compile(
    r"Property response:\s*\n\n(.+?)\s*\[Continue reading\]",
    re.DOTALL,
)
TOTAL_REVIEWS_HEADER_RE = re.compile(r"Guest reviews\s*\((\d[\d,\.]*?)\)")
TOTAL_PAGES_RE = re.compile(r"\[(\d+)Page \1\]\(")
PROPERTY_NAME_HINTS = (
    re.compile(r"NEU RESIDENCES smart stay"),  # not used — informational
)


SLO_MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}


def parse_reviewed_date(s: str) -> str | None:
    """'May 4, 2026' -> '2026-05-04'."""
    m = re.match(r"^([A-Z][a-z]+)\s+(\d{1,2}),\s+(\d{4})$", s.strip())
    if not m:
        return None
    month, day, year = m.group(1), int(m.group(2)), int(m.group(3))
    if month not in SLO_MONTHS:
        return None
    return f"{year:04d}-{SLO_MONTHS[month]:02d}-{day:02d}"


def detect_language(text: str | None) -> str | None:
    """Cheap heuristic language detection. Returns ISO-639-1 or None."""
    if not text or len(text.strip()) < 4:
        return None
    t = text.lower()
    # Slovenian-specific letters
    if any(c in t for c in "čšž"):
        # Disambiguate Slovenian / Croatian / Serbian / Czech
        if re.search(r"\b(je|in|ki|sem|smo|so|bil|bila|nismo|smo|sva)\b", t):
            return "sl"
        if re.search(r"\b(je|i|sa|smo|smo|biloh|bili|bila)\b", t):
            return "hr"
        return "sl"  # default Slavic with čšž
    # English first since most reviews are in English and the other Latin-language
    # detectors share short tokens like "was" / "met" with Dutch.
    en_strong = re.search(r"\b(the|and|with|were|this|that|stay|room|location|breakfast|everything|nothing|excellent|wonderful|great|nice|good|hotel|apartment|clean|comfortable|staff)\b", t)
    de_strong = re.search(r"\b(und|der|die|das|nicht|sehr|gut|haben|wir|war|ist|sehr|nichts|alles|sauber|zimmer|hotel|nicht)\b", t)
    fr_strong = re.search(r"\b(et|le|la|les|nous|avec|très|bien|pas|était|été|en|du|des|une|un|c'est|chambre|hôtel|petit-déjeuner|emplacement|piscine|tout|rien|propre|confortable)\b", t)
    it_strong = re.search(r"\b(il|la|che|sono|molto|tutto|stato|abbiamo|era|colazione|camera|hotel|niente|posizione|pulito|comodo|ottimo|buono)\b", t)
    nl_strong = re.search(r"\b(het|een|wij|niet|heel|zeer|goed|kamer|ontbijt|locatie|alles|niets|schoon|geweldig|prima|leuk|gezellig)\b", t)
    es_strong = re.search(r"\b(el|la|los|las|que|muy|estaba|hemos|todo|pero|hotel|habitación|excelente|limpio|cómodo|nada|desayuno|ubicación)\b", t)
    pt_strong = re.search(r"\b(o|a|os|as|que|muito|tudo|estava|fomos|mas|hotel|quarto|excelente|limpo|nada|pequeno-almoço|localização|café da manhã)\b", t)
    ru_strong = re.search(r"\b(и|в|на|с|по|для|это|был|была|очень|хорошо|отличный|номер|отель|завтрак|расположение|чисто|удобно)\b", t)
    sr_strong = re.search(r"\b(je|i|sa|smo|biloh|bili|bila|hotel|soba|odlicno|sve|nista|dobro|cisto)\b", t)

    scores = {
        "en": (en_strong, 1),
        "de": (de_strong, 1),
        "fr": (fr_strong, 1),
        "it": (it_strong, 1),
        "nl": (nl_strong, 1),
        "es": (es_strong, 1),
        "pt": (pt_strong, 1),
        "ru": (ru_strong, 1),
        "sr": (sr_strong, 1),
    }
    matched = [(lang, m) for lang, (m, _) in scores.items() if m]
    if not matched:
        return None
    # If only one Latin-script language matches, return it.
    if len(matched) == 1:
        return matched[0][0]
    # When multiple match, prefer the language whose word is more uniquely diagnostic.
    # Hard rule: if German "und"/"nicht"/"sehr" present, it's de.
    if re.search(r"\b(und|nicht|sehr|kein|keine|schöne|schön)\b", t):
        return "de"
    # French: rich diacritics or French-only words.
    if re.search(r"\b(très|était|c'est|petit-déjeuner|emplacement|chambre|hôtel)\b", t):
        return "fr"
    # Italian: "molto", "ottimo", "stato", "abbiamo".
    if re.search(r"\b(molto|ottimo|abbiamo|colazione|posizione)\b", t):
        return "it"
    # Spanish: "muy", "habitación", "ubicación", "excelente"
    if re.search(r"\b(muy|habitación|ubicación|excelente|desayuno)\b", t):
        return "es"
    # Dutch: "een", "ontbijt", "kamer".
    if re.search(r"\b(een|ontbijt|gezellig|leuk)\b", t):
        return "nl"
    # Default to English when ambiguous (most common case).
    if en_strong:
        return "en"
    return matched[0][0]


def hash_review_id(name: str, date: str | None, title: str | None) -> str:
    h = hashlib.sha1(f"{name}|{date or ''}|{title or ''}".encode("utf-8")).hexdigest()[:12]
    return f"r_{h}"


def parse_one_review(block: str) -> dict[str, Any] | None:
    """Parse one review block. Block should NOT include the leading '- !['."""
    # Re-prepend the marker we stripped during split
    block = "- ![" + block

    # Reviewer name + country
    name = country = None
    m = NAME_COUNTRY_RE.search(block)
    if m:
        name = m.group(1).strip()
        country = m.group(2).strip()
    else:
        # Single-letter avatar fallback (no Google avatar URL): "  J\n\n  Josh![flag]Country"
        m2 = re.search(
            r"^\s*[A-Z]\s*\n\s*\n\s*([^!\n]+?)!\[[^\]]*\]\([^)]*flags/16/[a-z]{2}/[^)]+\)([^\n]+)$",
            block,
            re.MULTILINE,
        )
        if m2:
            name = m2.group(1).strip()
            country = m2.group(2).strip()
    if not name:
        return None  # malformed, skip

    # Country code from flag URL
    cc = None
    cm = FLAG_RE.search(block)
    if cm:
        cc = cm.group(1).upper()

    room_type = None
    rm = ROOM_TYPE_RE.search(block)
    if rm:
        room_type = rm.group(1).strip()

    nights_stayed = None
    nm = NIGHTS_RE.search(block)
    if nm:
        nights_stayed = int(nm.group(1))

    stay_month = None
    sm = STAY_MONTH_RE.search(block)
    if sm:
        stay_month = sm.group(1).strip()

    reviewer_type = None
    rtm = REVIEWER_TYPE_RE.search(block)
    if rtm:
        reviewer_type = rtm.group(1).strip()

    review_date = None
    dm = DATE_RE.search(block)
    if dm:
        review_date = parse_reviewed_date(dm.group(1))

    title = None
    tm = TITLE_RE.search(block)
    if tm:
        title = tm.group(1).strip()

    score = None
    # Score appears alone on a line right after the title. Use first match after title position.
    if tm:
        tail = block[tm.end():]
        sm2 = SCORE_LINE_RE.search(tail)
        if sm2:
            try:
                score = float(sm2.group(1))
            except ValueError:
                score = None

    positive_text = None
    lm = LIKED_RE.search(block)
    if lm:
        positive_text = lm.group(1).strip()
        # Trim a trailing dotted "Continue reading" footer if present
        positive_text = re.sub(r"\s*\[Continue reading\].*$", "", positive_text, flags=re.DOTALL).strip()

    negative_text = None
    dm2 = DISLIKED_RE.search(block)
    if dm2:
        negative_text = dm2.group(1).strip()
        negative_text = re.sub(r"\s*\[Continue reading\].*$", "", negative_text, flags=re.DOTALL).strip()
        if negative_text in (".", "-", "—"):
            negative_text = None

    property_response = None
    pm = PROPERTY_RESPONSE_RE.search(block)
    if pm:
        text = pm.group(1).strip()
        # The text often appears twice (preview + full). Keep the longer half.
        # Pattern: "preview…full text" -> keep whichever is longest after a "…" splitter.
        if "…" in text:
            parts = [p.strip() for p in text.split("…") if p.strip()]
            if parts:
                text = max(parts, key=len)
        property_response = {"text": text, "date": None}

    language = detect_language(positive_text or negative_text)

    return {
        "review_id": hash_review_id(name, review_date, title),
        "reviewer_name": name,
        "reviewer_country": country,
        "reviewer_country_code": cc,
        "reviewer_type": reviewer_type,
        "trip_type": None,
        "room_type": room_type,
        "nights_stayed": nights_stayed,
        "stay_month": stay_month,
        "review_date": review_date,
        "score": score,
        "review_title": title,
        "positive_text": positive_text,
        "negative_text": negative_text,
        "language": language,
        "is_verified": True,
        "helpful_votes": None,
        "property_response": property_response,
        "sub_scores": None,
        "tags": [],
        "submitted_from_mobile": None,
        "reviewer_review_count": None,
    }


def parse_page_markdown(md: str) -> list[dict[str, Any]]:
    """Split a single page's markdown into individual review blocks and parse each."""
    # Trim header noise above "### Guest reviews"
    if "### Guest reviews" in md:
        md = md.split("### Guest reviews", 1)[1]
    # Trim pagination footer
    cut = re.search(r"\n\d+Current page \d+", md)
    if cut:
        md = md[: cut.start()]

    # The first review starts with "- ![avatar...]"; subsequent ones are split by "\n\n- !["
    if "- ![" not in md:
        return []
    parts = REVIEW_BLOCK_SPLIT.split(md)
    # The first chunk has prefix before the first "- ![". Include it if it starts with "- ![".
    out: list[dict[str, Any]] = []
    for i, chunk in enumerate(parts):
        if i == 0:
            # Fragment before first "- ![" — discard
            continue
        rec = parse_one_review(chunk)
        if rec:
            out.append(rec)
    return out


def derive_header_facts(md: str) -> dict[str, Any]:
    """Pull total reviews count and total page count from a page-1 markdown."""
    out: dict[str, Any] = {}
    m = TOTAL_REVIEWS_HEADER_RE.search(md)
    if m:
        out["total_reviews_reported"] = int(m.group(1).replace(",", "").replace(".", ""))
    pages = [int(g) for g in TOTAL_PAGES_RE.findall(md)]
    if pages:
        out["total_pages"] = max(pages)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir", help="Directory with page-NNN.md files")
    ap.add_argument("--output", required=True, help="Output JSON path")
    ap.add_argument("--property-id", type=int, default=1)
    ap.add_argument("--property-name", default="")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--reported-total", type=int, default=None)
    ap.add_argument("--overall-score", type=float, default=None)
    ap.add_argument("--substaff", type=float, default=None)
    ap.add_argument("--subclean", type=float, default=None)
    ap.add_argument("--subcomfort", type=float, default=None)
    ap.add_argument("--subfac", type=float, default=None)
    ap.add_argument("--subvalue", type=float, default=None)
    ap.add_argument("--subloc", type=float, default=None)
    ap.add_argument("--subwifi", type=float, default=None)
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    files = sorted(input_dir.glob("page-*.md"))
    if not files:
        print(f"No page-*.md files in {input_dir}", file=sys.stderr)
        return 1

    page1 = files[0].read_text(encoding="utf-8")
    header_facts = derive_header_facts(page1)

    all_reviews: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for f in files:
        md = f.read_text(encoding="utf-8")
        page_reviews = parse_page_markdown(md)
        for r in page_reviews:
            if r["review_id"] in seen_ids:
                continue
            seen_ids.add(r["review_id"])
            all_reviews.append(r)

    # Sort newest first
    all_reviews.sort(
        key=lambda r: (r.get("review_date") or "0000-00-00", r.get("reviewer_name") or ""),
        reverse=True,
    )

    out = {
        "property_id": args.property_id,
        "property_name": args.property_name,
        "scraped_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": args.source_url,
        "total_reviews_reported": args.reported_total or header_facts.get("total_reviews_reported"),
        "total_reviews_scraped": len(all_reviews),
        "overall_score": args.overall_score,
        "sub_scores_aggregate": {
            "staff": args.substaff,
            "cleanliness": args.subclean,
            "comfort": args.subcomfort,
            "facilities": args.subfac,
            "value_for_money": args.subvalue,
            "location": args.subloc,
            "free_wifi": args.subwifi,
        },
        "pagination_meta": {
            "pages_scraped": len(files),
            "pages_reported": header_facts.get("total_pages"),
            "reviews_per_page": 25,
        },
        "reviews": all_reviews,
    }

    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Wrote {args.output} with {len(all_reviews):,} reviews "
        f"(reported header total: {out['total_reviews_reported']})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
