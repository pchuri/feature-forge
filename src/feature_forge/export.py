"""Persist :class:`Review` objects back to CSV/JSON (used by --save and `fetch`)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from feature_forge.models import Review

#: Column order used when writing CSV, matching the documented input schema.
FIELDNAMES = ("rating", "title", "body", "date", "app_name", "locale")


def _to_row(review: Review) -> dict[str, object]:
    return {
        "rating": review.rating,
        "title": review.title or "",
        "body": review.body,
        "date": review.date.isoformat() if review.date else "",
        "app_name": review.app_name or "",
        "locale": review.locale or "",
    }


def save_reviews(reviews: list[Review], path: str | Path) -> Path:
    """Write ``reviews`` to ``path`` as CSV or JSON, chosen by file extension."""
    path = Path(path)
    suffix = path.suffix.lower()
    path.parent.mkdir(parents=True, exist_ok=True)

    if suffix == ".csv":
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
            writer.writeheader()
            for review in reviews:
                writer.writerow(_to_row(review))
    elif suffix in {".json", ".jsonl"}:
        rows = [_to_row(r) for r in reviews]
        if suffix == ".jsonl":
            path.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
                encoding="utf-8",
            )
        else:
            path.write_text(
                json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    else:
        raise ValueError(
            f"Unsupported save format {suffix!r}. Use .csv, .json or .jsonl."
        )
    return path
