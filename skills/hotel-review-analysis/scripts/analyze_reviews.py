#!/usr/bin/env python3
"""Compute statistics and theme-keyword counts from a Booking.com reviews JSON.

Usage:
    python3 analyze_reviews.py <path-to-json> \
        [--cutoff YYYY-MM-DD] \
        [--dump-texts DIR] \
        [--field score=reviewScore] [--field date=reviewDate] ...

Prints one JSON block on stdout with: counts, distribution, segments, room types,
countries, monthly trend, before/after cutoff averages (if cutoff given), and
positive/negative keyword hit counts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from typing import Any

# Default mapping, same candidate names as inspect_reviews.py. Overridable via --field.
DEFAULT_FIELDS = {
    "score": [
        "score", "rating", "reviewScore", "review_score", "overallRating",
        "overall_rating", "stars", "grade",
    ],
    "date": [
        "reviewDate", "review_date", "date", "datePublished", "date_published",
        "createdAt", "created_at", "publishedAt",
    ],
    "stay_date": [
        "stayDate", "stay_date", "checkInDate", "check_in_date", "checkIn",
        "check_in", "stayedAt",
    ],
    "title": ["reviewTitle", "review_title", "title", "headline"],
    "liked": [
        "liked", "positive", "pros", "likedText", "positiveText",
        "positive_text", "likedComment", "reviewPositiveText",
    ],
    "disliked": [
        "disliked", "negative", "cons", "dislikedText", "negativeText",
        "negative_text", "dislikedComment", "reviewNegativeText",
    ],
    "country": [
        "country", "nationality", "reviewerCountry", "reviewer_country",
        "userCountry", "user_country", "guestCountry",
    ],
    "reviewer_type": [
        "travelerType", "traveler_type", "travellerType", "traveller_type",
        "guestType", "guest_type", "reviewerType", "reviewer_type", "tripType",
        "trip_type",
    ],
    "room_type": [
        "roomType", "room_type", "roomName", "room_name", "room",
        "accommodationType",
    ],
    "nights": [
        "nights", "stayLength", "stay_length", "lengthOfStay", "length_of_stay",
        "numberOfNights",
    ],
}

# Positive keyword groups (lowercase substrings, multilingual).
POSITIVE_KEYWORDS = {
    "lokacija": ["location", "lage", "posizione", "lokacija", "lokaliteta", "położen", "location is great", "poloha"],
    "osebje": ["staff", "personal", "personale", "osoblje", "osebje", "personel", "service was", "receptionist", "friendly staff", "ljubazno"],
    "zajtrk": ["breakfast", "frühstück", "colazione", "zajtrk", "doručak", "snídaně", "śniadanie", "petit dej"],
    "večerja / hrana": ["dinner", "food", "meal", "hrana", "cena", "jedi", "abendessen", "jídlo", "meal was"],
    "wellness / spa": ["wellness", "spa", "sauna", "savna", "bazen", "pool", "jacuzzi", "hamam", "thermal"],
    "sobe": ["room", "zimmer", "camera", "soba", "sobu", "habitacion", "chambre", "rooms were"],
    "postelja": ["bed", "mattress", "postelja", "krevet", "cama", "lit", "bett"],
    "čistoča": ["clean", "sauber", "čist", "pulito", "propre", "cisto", "spotless"],
    "dizajn / prenova": ["design", "modern", "renovated", "renovation", "prenovlj", "stylish", "beautifully", "dizajn", "moderno"],
    "razgled / narava": ["view", "razgled", "nature", "mountain", "alpine", "natur", "gorski", "hory", "landscape"],
    "mir / spokoj": ["quiet", "peaceful", "mirn", "tranquil", "ruhig", "spokojno", "tihi", "calm"],
    "razmerje cena / kakovost": ["value", "worth", "cena", "vrednost", "preis-leistung", "prezzo", "good price"],
    "družinam prijazno": ["kids", "children", "family", "otroci", "deca", "djeca", "kinder", "bambini"],
    "hišni ljubljenčki": ["dog", "pet", "pes", "pies", "hund", "pets welcome", "dog-friendly"],
}

# Negative keyword groups.
NEGATIVE_KEYWORDS = {
    "urnik wellnessa / bazena": ["pool hours", "pool opens", "open later", "close early", "wellness hours", "wellness nur", "bazen odprt", "saune samo", "obratovalni čas"],
    "temperatura bazena / vode": ["cold pool", "water too cold", "water cold", "voda hladna", "bazen hladen", "swimming pool cold", "too cold water"],
    "temperatura sobe / klima": ["air condition", "ac ", "aircon", "klima", "too hot", "too cold", "heating", "prevroče", "prehladno", "temperature in room", "thermostat"],
    "parkiranje": ["parking", "garage", "parkiranje", "parking fee", "parkplatz", "autopark", "parcheggio"],
    "čiščenje / vzdrževanje": ["not cleaned", "dirty", "uncleaned", "hair", "dust", "umazan", "not hoovered", "cleaning was", "sobe nisu čistili", "linens"],
    "kakovost hrane": ["food was bad", "food quality", "overcooked", "cold food", "tasteless", "average food", "razočara", "slaba hrana", "hrana loša", "bad breakfast"],
    "cena / vrednost": ["overpriced", "expensive", "too expensive", "value for money", "skupo", "preskupo", "predrago", "not worth"],
    "wifi / internet": ["wifi", "wi-fi", "internet", "signal", "network"],
    "hrup / dogodki": ["noisy", "noise", "loud", "music", "party", "buka", "hrup", "laut", "church bells", "cerkvena zvonova"],
    "smrad / kanalizacija": ["smell", "stink", "odor", "odour", "sewer", "drain", "zaudarja", "smrdi", "kanalizacij"],
    "dvigalo": ["elevator", "lift", "dvigalo", "aufzug"],
    "zastarele sobe / pohištvo": ["outdated", "old", "worn", "tired", "dated", "zastarel", "old furniture", "staro", "ruined"],
    "prha / kopalnica": ["shower", "bathroom", "water leak", "splash", "kopalnica", "tusz", "slippery"],
    "odjava / ček-aut": ["checkout", "check-out", "early checkout", "11 am", "late checkout", "odjava"],
    "odnos osebja": ["rude", "unfriendly", "grumpy", "not welcoming", "nepristojn", "drsko", "nesramn", "unhelpful staff"],
    "pomanjkanje skupnih prostorov": ["no lounge", "no lobby", "no bar", "no terrace", "nowhere to sit", "ni salon", "no lounge area", "no common"],
}


def resolve_field(record: dict[str, Any], candidates: list[str]) -> Any:
    """Return the first matching field value from record using candidate keys."""
    lower_keys = {k.lower(): k for k in record.keys()}
    for cand in candidates:
        actual = lower_keys.get(cand.lower())
        if actual is not None:
            val = record[actual]
            if val not in (None, "", [], {}):
                return val
    # nested search one level deep
    for key, val in record.items():
        if isinstance(val, dict):
            inner = {k.lower(): k for k in val.keys()}
            for cand in candidates:
                actual = inner.get(cand.lower())
                if actual is not None:
                    inner_val = val[actual]
                    if inner_val not in (None, "", [], {}):
                        return inner_val
    return None


def parse_date(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    if not s:
        return None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%B %Y",
        "%b %Y",
    ):
        try:
            return datetime.strptime(s[:len(fmt) + 20] if len(s) > len(fmt) else s, fmt)
        except ValueError:
            continue
    # last resort: pull a YYYY-MM-DD substring
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def normalize_score(value: Any) -> float | None:
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        s = str(value).strip().replace(",", ".")
        try:
            v = float(re.search(r"[0-9.]+", s).group())  # type: ignore[union-attr]
        except Exception:
            return None
    # Booking uses a native 1 to 10 scale. Only rescale when the value is
    # clearly outside that range (fractional 0 to 1, or 100-scale percent).
    if 0 < v <= 1.0:
        v *= 10
    elif v > 10.0 and v <= 100.0:
        v /= 10.0
    if v < 1 or v > 10:
        return None
    return round(v, 2)


def bucket_reviewer_type(raw: Any) -> str:
    if not raw:
        return "neznano"
    s = str(raw).lower()
    if any(x in s for x in ("couple", "paar", "coppia", "par ")):
        return "Pari"
    if any(x in s for x in ("family", "famili", "família", "obitelj", "druž", "families")):
        return "Družine"
    if any(x in s for x in ("group", "gruppe", "gruppo", "grupa", "skupin")):
        return "Skupine"
    if any(x in s for x in ("solo", "single", "individu", "posamezn", "alleine")):
        return "Posamezniki"
    if any(x in s for x in ("business", "poslovn", "geschäft")):
        return "Poslovno"
    return "Drugo"


def count_keywords(text: str, groups: dict[str, list[str]]) -> dict[str, int]:
    out = {g: 0 for g in groups}
    t = text.lower()
    for label, keys in groups.items():
        for kw in keys:
            if kw in t:
                out[label] += 1
                break
    return out


def parse_field_overrides(overrides: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for item in overrides:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        result[k.strip()] = [v.strip()]
    return result


def load_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        for key in ("reviews", "results", "data", "items", "records"):
            if key in data and isinstance(data[key], list):
                return [r for r in data[key] if isinstance(r, dict)]
    raise ValueError(f"Unsupported JSON root: {type(data).__name__}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path")
    ap.add_argument("--cutoff", help="YYYY-MM-DD split date for before/after analysis")
    ap.add_argument("--dump-texts", metavar="DIR", help="write liked.txt and disliked.txt into DIR")
    ap.add_argument(
        "--field", action="append", default=[],
        help="override field mapping, e.g. --field score=reviewScore",
    )
    args = ap.parse_args()

    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    cutoff = parse_date(args.cutoff) if args.cutoff else None

    records = load_records(path)
    n = len(records)
    if n == 0:
        print(json.dumps({"error": "no records"}))
        return 0

    field_map = {k: list(v) for k, v in DEFAULT_FIELDS.items()}
    for k, v in parse_field_overrides(args.field).items():
        field_map[k] = v + field_map.get(k, [])

    scores: list[float] = []
    score_distribution: Counter[int] = Counter()
    monthly: dict[str, list[float]] = defaultdict(list)
    segments: Counter[str] = Counter()
    rooms: Counter[str] = Counter()
    countries: Counter[str] = Counter()
    before_scores: list[float] = []
    after_scores: list[float] = []

    liked_texts: list[str] = []
    disliked_texts: list[str] = []

    for r in records:
        score = normalize_score(resolve_field(r, field_map["score"]))
        if score is None:
            continue
        scores.append(score)
        bucket = int(round(score))
        score_distribution[bucket] += 1

        d = parse_date(resolve_field(r, field_map["date"]))
        if d is not None:
            monthly[d.strftime("%Y-%m")].append(score)
            if cutoff is not None:
                (before_scores if d < cutoff else after_scores).append(score)

        rtype = bucket_reviewer_type(resolve_field(r, field_map["reviewer_type"]))
        segments[rtype] += 1

        room = resolve_field(r, field_map["room_type"])
        if room:
            rooms[str(room).strip()] += 1

        country = resolve_field(r, field_map["country"])
        if country:
            countries[str(country).strip()] += 1

        liked = resolve_field(r, field_map["liked"])
        if liked:
            liked_texts.append(str(liked))
        disliked = resolve_field(r, field_map["disliked"])
        if disliked:
            disliked_texts.append(str(disliked))

    if not scores:
        print(json.dumps({"error": "no parseable scores"}))
        return 0

    # Keyword counts
    liked_blob = "\n".join(liked_texts).lower()
    disliked_blob = "\n".join(disliked_texts).lower()
    positive_counts = {
        label: sum(1 for t in liked_texts if any(kw in t.lower() for kw in keys))
        for label, keys in POSITIVE_KEYWORDS.items()
    }
    negative_counts = {
        label: sum(1 for t in disliked_texts if any(kw in t.lower() for kw in keys))
        for label, keys in NEGATIVE_KEYWORDS.items()
    }

    # Sort monthly
    monthly_sorted = [
        {"month": m, "count": len(s), "avg": round(mean(s), 2)}
        for m, s in sorted(monthly.items())
    ]

    # Optional dumps
    if args.dump_texts:
        outdir = Path(args.dump_texts).expanduser().resolve()
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "liked.txt").write_text("\n---\n".join(liked_texts), encoding="utf-8")
        (outdir / "disliked.txt").write_text("\n---\n".join(disliked_texts), encoding="utf-8")

    overall_mean = round(mean(scores), 2)
    overall_median = round(median(scores), 2)
    total_scored = len(scores)

    result = {
        "source_file": str(path),
        "total_records": n,
        "scored_records": total_scored,
        "overall": {
            "mean": overall_mean,
            "median": overall_median,
            "min": round(min(scores), 2),
            "max": round(max(scores), 2),
        },
        "distribution": {
            str(i): {
                "count": score_distribution.get(i, 0),
                "pct": round(100 * score_distribution.get(i, 0) / total_scored, 2),
            }
            for i in range(10, 0, -1)
        },
        "score_9_or_10_pct": round(
            100 * (score_distribution.get(9, 0) + score_distribution.get(10, 0)) / total_scored, 2
        ),
        "score_4_or_less_pct": round(
            100 * sum(score_distribution.get(i, 0) for i in range(1, 5)) / total_scored, 2
        ),
        "segments": {k: v for k, v in segments.most_common()},
        "room_types_top": rooms.most_common(10),
        "countries_top": countries.most_common(15),
        "monthly_trend": monthly_sorted,
        "liked_texts_count": len(liked_texts),
        "disliked_texts_count": len(disliked_texts),
        "positive_keyword_mentions": dict(
            sorted(positive_counts.items(), key=lambda x: -x[1])
        ),
        "negative_keyword_mentions": dict(
            sorted(negative_counts.items(), key=lambda x: -x[1])
        ),
    }
    if cutoff is not None:
        result["cutoff"] = cutoff.strftime("%Y-%m-%d")
        result["before_cutoff"] = {
            "count": len(before_scores),
            "avg": round(mean(before_scores), 2) if before_scores else None,
        }
        result["after_cutoff"] = {
            "count": len(after_scores),
            "avg": round(mean(after_scores), 2) if after_scores else None,
        }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
