"""Input loaders that turn local files into :class:`~feature_forge.models.Review` objects."""

from __future__ import annotations

from pathlib import Path

from feature_forge.models import Review

from .csv_loader import load_csv
from .json_loader import load_json

__all__ = ["load_csv", "load_json", "load_reviews"]


def load_reviews(path: str | Path) -> list[Review]:
    """Load reviews from ``path``, dispatching on the file extension.

    Supports ``.csv``, ``.json`` and ``.jsonl`` files.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_csv(path)
    if suffix in {".json", ".jsonl"}:
        return load_json(path)
    raise ValueError(
        f"Unsupported input format {suffix!r}. Expected a .csv, .json or .jsonl file."
    )
