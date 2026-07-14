"""Shared helpers for turning raw records into :class:`Review` models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from feature_forge.models import Review

# Columns understood by Feature Forge. ``rating`` and ``body`` are required;
# everything else is optional.
REQUIRED_FIELDS = ("rating", "body")
OPTIONAL_FIELDS = ("title", "date", "app_name", "locale")


def _clean_value(value: Any) -> Any:
    """Normalize NaN/empty placeholders coming from pandas or JSON to ``None``."""
    if value is None:
        return None
    # pandas uses float('nan') for missing cells; NaN != NaN is the standard test.
    if isinstance(value, float) and value != value:  # noqa: PLR0124 - NaN check
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _parse_date(value: Any) -> date | None:
    value = _clean_value(value)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    # Tolerate full ISO timestamps by keeping only the date portion.
    text = text.split("T")[0].split(" ")[0]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def record_to_review(record: dict[str, Any]) -> Review | None:
    """Build a :class:`Review` from a raw mapping, or ``None`` if it cannot.

    Rows without a parseable rating or without a body are skipped rather than
    raising, so that a single malformed line does not abort the whole load.
    """
    rating_raw = _clean_value(record.get("rating"))
    if rating_raw is None:
        return None
    try:
        rating = int(float(rating_raw))
    except (TypeError, ValueError):
        return None
    if not 1 <= rating <= 5:
        return None

    body = _clean_value(record.get("body"))
    body = "" if body is None else str(body)

    return Review(
        rating=rating,
        body=body,
        title=_clean_value(record.get("title")),
        date=_parse_date(record.get("date")),
        app_name=_clean_value(record.get("app_name")),
        locale=_clean_value(record.get("locale")),
    )
