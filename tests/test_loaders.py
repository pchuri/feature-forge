"""Tests for CSV and JSON loading."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from feature_forge.loaders import load_csv, load_json, load_reviews

CSV_CONTENT = """rating,title,body,date,app_name,locale
5,Nice,Works really well for my needs,2026-01-02,MyApp,en-US
3,,Body without a title here,,,
7,Bad rating,This rating is out of range and should be skipped,2026-01-03,MyApp,en-US
2,Slow,It is quite slow on big files,not-a-date,MyApp,en-US
"""


def test_load_csv_parses_rows_and_types(tmp_path: Path) -> None:
    csv_path = tmp_path / "reviews.csv"
    csv_path.write_text(CSV_CONTENT, encoding="utf-8")

    reviews = load_csv(csv_path)

    # The out-of-range rating (7) row is dropped; three valid rows remain.
    assert len(reviews) == 3

    first = reviews[0]
    assert first.rating == 5
    assert first.title == "Nice"
    assert first.body == "Works really well for my needs"
    assert first.date == date(2026, 1, 2)
    assert first.locale == "en-US"

    # Missing optional fields become None.
    assert reviews[1].title is None
    assert reviews[1].date is None

    # Unparseable date is tolerated as None rather than raising.
    assert reviews[2].date is None


def test_load_csv_missing_required_column(tmp_path: Path) -> None:
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("rating,note\n5,hello\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required column"):
        load_csv(csv_path)


def test_load_json_list_and_wrapper(tmp_path: Path) -> None:
    list_path = tmp_path / "list.json"
    list_path.write_text(
        '[{"rating": 4, "body": "Good enough for daily use"}]', encoding="utf-8"
    )
    wrapper_path = tmp_path / "wrapper.json"
    wrapper_path.write_text(
        '{"reviews": [{"rating": 1, "body": "Crashes all the time on launch"}]}',
        encoding="utf-8",
    )

    assert len(load_json(list_path)) == 1
    assert load_json(list_path)[0].rating == 4
    assert load_json(wrapper_path)[0].rating == 1


def test_load_reviews_dispatches_by_extension(tmp_path: Path) -> None:
    csv_path = tmp_path / "r.csv"
    csv_path.write_text("rating,body\n5,All good here thanks\n", encoding="utf-8")
    assert load_reviews(csv_path)[0].rating == 5

    with pytest.raises(ValueError, match="Unsupported input format"):
        load_reviews(tmp_path / "r.txt")


def test_load_bundled_example_csv() -> None:
    example = Path(__file__).resolve().parents[1] / "examples" / "reviews.csv"
    reviews = load_csv(example)
    assert len(reviews) >= 20
    assert all(1 <= r.rating <= 5 for r in reviews)
