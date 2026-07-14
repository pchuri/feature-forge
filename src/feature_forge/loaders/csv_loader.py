"""Load reviews from a CSV file using pandas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from feature_forge.models import Review

from ._common import REQUIRED_FIELDS, record_to_review


def load_csv(path: str | Path) -> list[Review]:
    """Read ``path`` and return the reviews it contains.

    The CSV must at least provide ``rating`` and ``body`` columns. Optional
    columns (``title``, ``date``, ``app_name``, ``locale``) are used when
    present. Rows with an invalid rating are skipped.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    frame = pd.read_csv(path, dtype=str, keep_default_na=True)
    frame.columns = [str(col).strip().lower() for col in frame.columns]

    missing = [field for field in REQUIRED_FIELDS if field not in frame.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required column(s): {', '.join(missing)}. "
            f"Found columns: {', '.join(frame.columns) or '(none)'}."
        )

    reviews: list[Review] = []
    for record in frame.to_dict(orient="records"):
        review = record_to_review(record)
        if review is not None:
            reviews.append(review)
    return reviews
