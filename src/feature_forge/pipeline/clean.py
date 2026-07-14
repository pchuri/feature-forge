"""Cleaning step: drop empty, duplicate and trivially short reviews."""

from __future__ import annotations

from dataclasses import dataclass

from feature_forge.models import Review

#: Reviews with fewer than this many characters in their body are discarded.
MIN_BODY_LENGTH = 10


@dataclass
class CleanStats:
    """Bookkeeping about what the cleaning step removed."""

    input_count: int
    empty_removed: int
    short_removed: int
    duplicate_removed: int
    output_count: int


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def clean_reviews(reviews: list[Review]) -> tuple[list[Review], CleanStats]:
    """Return cleaned reviews plus stats describing what was removed.

    Steps, in order:

    1. Drop reviews whose body is empty/whitespace.
    2. Drop reviews whose body is shorter than :data:`MIN_BODY_LENGTH`.
    3. Drop duplicates (same normalized body text), keeping the first seen.
    """
    empty_removed = 0
    short_removed = 0
    duplicate_removed = 0
    seen: set[str] = set()
    cleaned: list[Review] = []

    for review in reviews:
        body = review.body.strip()
        if not body:
            empty_removed += 1
            continue
        if len(body) < MIN_BODY_LENGTH:
            short_removed += 1
            continue
        key = _normalize(body)
        if key in seen:
            duplicate_removed += 1
            continue
        seen.add(key)
        cleaned.append(review)

    stats = CleanStats(
        input_count=len(reviews),
        empty_removed=empty_removed,
        short_removed=short_removed,
        duplicate_removed=duplicate_removed,
        output_count=len(cleaned),
    )
    return cleaned, stats
