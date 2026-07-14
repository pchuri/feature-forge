"""Tests for the cleaning step."""

from __future__ import annotations

from feature_forge.models import Review
from feature_forge.pipeline.clean import MIN_BODY_LENGTH, clean_reviews


def test_clean_removes_empty_short_and_duplicates() -> None:
    reviews = [
        Review(rating=5, body="This is a perfectly fine review body."),
        Review(rating=4, body="   "),  # empty after strip
        Review(rating=3, body="short"),  # under MIN_BODY_LENGTH
        Review(rating=2, body="This is a perfectly fine review body."),  # duplicate
        Review(rating=1, body="THIS IS a perfectly   fine review body."),  # dup (normalized)
        Review(rating=2, body="Another genuinely distinct review here."),
    ]

    cleaned, stats = clean_reviews(reviews)

    assert stats.input_count == 6
    assert stats.empty_removed == 1
    assert stats.short_removed == 1
    assert stats.duplicate_removed == 2
    assert stats.output_count == 2
    assert len(cleaned) == 2
    assert {r.body for r in cleaned} == {
        "This is a perfectly fine review body.",
        "Another genuinely distinct review here.",
    }


def test_min_length_boundary() -> None:
    just_under = "a" * (MIN_BODY_LENGTH - 1)
    exactly = "a" * MIN_BODY_LENGTH
    cleaned, stats = clean_reviews(
        [Review(rating=3, body=just_under), Review(rating=3, body=exactly)]
    )
    assert stats.short_removed == 1
    assert len(cleaned) == 1
    assert cleaned[0].body == exactly


def test_clean_empty_input() -> None:
    cleaned, stats = clean_reviews([])
    assert cleaned == []
    assert stats.output_count == 0
