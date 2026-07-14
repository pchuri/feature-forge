"""Tests for saving reviews and round-tripping them back through the loaders."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from feature_forge.export import save_reviews
from feature_forge.loaders import load_csv, load_json
from feature_forge.models import Review


def _sample() -> list[Review]:
    return [
        Review(
            rating=1,
            title="Ads",
            body="Too many ads here now",
            date=date(2026, 1, 1),
            app_name="A",
            locale="us",
        ),
        Review(rating=5, body="Works great for me every day", app_name="A", locale="us"),
    ]


def test_save_and_reload_csv(tmp_path: Path) -> None:
    path = tmp_path / "out.csv"
    save_reviews(_sample(), path)
    reloaded = load_csv(path)
    assert len(reloaded) == 2
    assert reloaded[0].rating == 1
    assert reloaded[0].title == "Ads"
    assert reloaded[0].date == date(2026, 1, 1)
    assert reloaded[1].title is None


def test_save_and_reload_json(tmp_path: Path) -> None:
    path = tmp_path / "out.json"
    save_reviews(_sample(), path)
    reloaded = load_json(path)
    assert len(reloaded) == 2
    assert reloaded[1].body == "Works great for me every day"


def test_save_rejects_unknown_extension(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported save format"):
        save_reviews(_sample(), tmp_path / "out.txt")
