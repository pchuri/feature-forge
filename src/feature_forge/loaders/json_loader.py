"""Load reviews from a JSON or JSON Lines file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from feature_forge.models import Review

from ._common import record_to_review


def _iter_records(raw: Any) -> list[dict[str, Any]]:
    """Accept either a top-level list or a ``{"reviews": [...]}`` wrapper."""
    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, dict) and isinstance(raw.get("reviews"), list):
        records = raw["reviews"]
    else:
        raise ValueError(
            "JSON input must be a list of review objects or an object with a "
            "'reviews' array."
        )
    return [record for record in records if isinstance(record, dict)]


def load_json(path: str | Path) -> list[Review]:
    """Read ``path`` (``.json`` or ``.jsonl``) and return the reviews."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    text = path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".jsonl":
        records = [
            json.loads(line) for line in text.splitlines() if line.strip()
        ]
    else:
        records = _iter_records(json.loads(text))

    reviews: list[Review] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        review = record_to_review(record)
        if review is not None:
            reviews.append(review)
    return reviews
