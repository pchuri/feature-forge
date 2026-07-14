"""Tests for store fetchers — transforms and resolution, no network calls."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from feature_forge.fetchers import Store, get_fetcher, looks_like_app_id
from feature_forge.fetchers.apple_app_store import (
    AppStoreFetcher,
    _entries,
    _entry_to_review,
)
from feature_forge.fetchers.base import AppMatch
from feature_forge.fetchers.google_play import GooglePlayFetcher, _to_review


def test_looks_like_app_id() -> None:
    assert looks_like_app_id(Store.GOOGLE_PLAY, "com.whatsapp")
    assert looks_like_app_id(Store.GOOGLE_PLAY, "com.google.android.apps.photos")
    assert not looks_like_app_id(Store.GOOGLE_PLAY, "WhatsApp")
    assert not looks_like_app_id(Store.GOOGLE_PLAY, "single")

    assert looks_like_app_id(Store.APP_STORE, "310633997")
    assert looks_like_app_id(Store.APP_STORE, "id310633997")
    assert not looks_like_app_id(Store.APP_STORE, "WhatsApp")


def test_get_fetcher_types() -> None:
    assert isinstance(get_fetcher(Store.GOOGLE_PLAY), GooglePlayFetcher)
    assert isinstance(get_fetcher(Store.APP_STORE), AppStoreFetcher)


def test_google_play_to_review() -> None:
    raw = {
        "score": 1,
        "content": "  Too many ads everywhere  ",
        "at": datetime(2026, 1, 5, 10, 30),
    }
    review = _to_review(raw, app_name="Photos", locale="us")
    assert review is not None
    assert review.rating == 1
    assert review.body == "Too many ads everywhere"
    assert review.title is None
    assert review.date == date(2026, 1, 5)
    assert review.app_name == "Photos"
    assert review.locale == "us"


def test_google_play_to_review_skips_bad_rows() -> None:
    assert _to_review({"content": "no score"}, "A", "us") is None
    assert _to_review({"score": 9, "content": "out of range"}, "A", "us") is None


def test_google_play_resolve_id_skips_search() -> None:
    fetcher = GooglePlayFetcher()
    match = fetcher.resolve("com.whatsapp")
    assert match == AppMatch("com.whatsapp", "com.whatsapp", Store.GOOGLE_PLAY)


def test_app_store_entry_to_review() -> None:
    entry = {
        "im:rating": {"label": "2"},
        "title": {"label": "Slow"},
        "content": {"label": "  Conversion is painfully slow  ", "attributes": {"type": "text"}},
        "updated": {"label": "2026-02-14T09:00:00-07:00"},
    }
    review = _entry_to_review(entry, app_name="PDF App", country="us")
    assert review is not None
    assert review.rating == 2
    assert review.title == "Slow"
    assert review.body == "Conversion is painfully slow"
    assert review.date == date(2026, 2, 14)
    assert review.app_name == "PDF App"


def test_app_store_entry_skips_app_metadata() -> None:
    # The leading feed entry describes the app and has no im:rating.
    app_meta = {"im:name": {"label": "PDF App"}, "title": {"label": "PDF App"}}
    assert _entry_to_review(app_meta, "PDF App", "us") is None


def test_app_store_entries_shapes() -> None:
    assert _entries({"feed": {}}) == []
    single = {"feed": {"entry": {"im:rating": {"label": "5"}}}}
    assert len(_entries(single)) == 1
    many = {"feed": {"entry": [{"a": 1}, {"b": 2}]}}
    assert len(_entries(many)) == 2


def test_app_store_resolve_id_normalizes_prefix() -> None:
    fetcher = AppStoreFetcher()
    match = fetcher.resolve("id310633997")
    assert match.app_id == "310633997"
    assert match.store is Store.APP_STORE


def test_google_play_fetch_paginates(monkeypatch: pytest.MonkeyPatch) -> None:
    """fetch() should page via the continuation token until it hits `count`."""
    fetcher = GooglePlayFetcher()

    class FakeSort:
        NEWEST = "newest"

    calls: list[dict] = []

    def fake_reviews(app_id, *, lang, country, sort, count, continuation_token):
        calls.append({"count": count, "token": continuation_token})
        rows = [{"score": 3, "content": f"review {i}", "at": None} for i in range(count)]
        # Return a token on the first page, then stop.
        token = "next" if continuation_token is None else None
        return rows, token

    class FakeLib:
        Sort = FakeSort
        reviews = staticmethod(fake_reviews)

    monkeypatch.setattr(fetcher, "_lib", lambda: FakeLib)

    match = AppMatch("com.example", "Example", Store.GOOGLE_PLAY)
    reviews = fetcher.fetch(match, count=250)
    assert len(reviews) == 250
    # 200 on the first page, 50 on the second.
    assert calls[0]["count"] == 200
    assert calls[1]["count"] == 50
