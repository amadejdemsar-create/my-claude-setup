#!/usr/bin/env python3
"""Inspect a scraped Booking.com reviews JSON and suggest a field mapping.

Usage:
    python3 inspect_reviews.py <path-to-json>

Prints:
    - total records
    - top-level shape (list/dict + record count)
    - one sample record (truncated)
    - guessed mapping for score/date/title/liked/disliked/country/type/room/nights
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


CANDIDATE_KEYS = {
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
    "reviewer_name": [
        "reviewerName", "reviewer_name", "userName", "user_name", "author",
        "guestName", "guest_name", "name",
    ],
}


def load(path: Path) -> tuple[list[dict[str, Any]], Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data, data
    if isinstance(data, dict):
        for key in ("reviews", "results", "data", "items", "records"):
            if key in data and isinstance(data[key], list):
                return data[key], data
        # fall back: treat the dict as a single record
        return [data], data
    raise ValueError(f"Unsupported JSON root: {type(data).__name__}")


def guess_mapping(sample: dict[str, Any]) -> dict[str, str | None]:
    keys_lower = {k.lower(): k for k in sample.keys()}
    # also flatten one level of nesting
    nested = {}
    for parent_key, parent_val in sample.items():
        if isinstance(parent_val, dict):
            for child_key in parent_val:
                nested[child_key.lower()] = f"{parent_key}.{child_key}"
    mapping: dict[str, str | None] = {}
    for canonical, candidates in CANDIDATE_KEYS.items():
        hit = None
        for cand in candidates:
            if cand.lower() in keys_lower:
                hit = keys_lower[cand.lower()]
                break
            if cand.lower() in nested:
                hit = nested[cand.lower()]
                break
        mapping[canonical] = hit
    return mapping


def truncate(value: Any, max_len: int = 120) -> Any:
    if isinstance(value, str) and len(value) > max_len:
        return value[:max_len] + "..."
    if isinstance(value, list):
        return [truncate(v, max_len) for v in value[:3]]
    if isinstance(value, dict):
        return {k: truncate(v, max_len) for k, v in list(value.items())[:10]}
    return value


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 inspect_reviews.py <path-to-json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    records, root = load(path)
    print(f"File: {path}")
    print(f"Root type: {type(root).__name__}")
    print(f"Record count: {len(records)}")
    if not records:
        return 0

    # aggregate top-level keys observed
    all_keys: dict[str, int] = {}
    for r in records:
        if isinstance(r, dict):
            for k in r.keys():
                all_keys[k] = all_keys.get(k, 0) + 1
    print("\nTop-level keys (coverage across records):")
    for k, n in sorted(all_keys.items(), key=lambda x: (-x[1], x[0])):
        pct = 100 * n / len(records)
        print(f"  {k:<30s} {n:>7d} ({pct:5.1f} %)")

    print("\nSample record (truncated):")
    print(json.dumps(truncate(records[0]), ensure_ascii=False, indent=2))

    print("\nGuessed field mapping:")
    mapping = guess_mapping(records[0])
    for canonical, found in mapping.items():
        status = found if found else "(not found)"
        print(f"  {canonical:<15s} -> {status}")

    missing = [k for k, v in mapping.items() if v is None]
    if missing:
        print(
            "\nMissing mappings: "
            + ", ".join(missing)
            + ". Check the top-level keys above and either rename fields or pass "
            "overrides to analyze_reviews.py via --field KEY=JSON_PATH."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
