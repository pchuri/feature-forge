"""Fetch reviews from the Apple App Store.

Uses Apple's official public endpoints instead of a scraping library:

* app search -> the iTunes Search API
* reviews    -> the Customer Reviews RSS feed (JSON)

The RSS feed is stable but paginated to ~10 pages of 50 reviews, so at most
around 500 reviews per app are available this way. That is plenty for idea
validation; the cap is reported to the caller.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import date
from typing import Any

from feature_forge.models import Review

from .base import AppMatch, FetchError, Store, StoreFetcher, looks_like_app_id

_SEARCH_URL = "https://itunes.apple.com/search"
_RSS_URL = "https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
_MAX_PAGES = 10
_USER_AGENT = "feature-forge/0.1 (+https://github.com/pchuri/feature-forge)"


def _get_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - fixed https host
            payload = response.read().decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        raise FetchError(f"App Store request failed: {exc}") from exc
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise FetchError(f"App Store returned invalid JSON from {url}") from exc


def _normalize_id(value: str) -> str:
    """Strip a leading ``id`` prefix from an App Store id if present."""
    value = value.strip()
    return value[2:] if value.lower().startswith("id") else value


def _label(entry: dict[str, Any], key: str) -> str | None:
    node = entry.get(key)
    if isinstance(node, dict):
        label = node.get("label")
        return str(label) if label is not None else None
    return None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    text = value.split("T")[0]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _entry_to_review(entry: dict[str, Any], app_name: str, country: str) -> Review | None:
    """Map one RSS ``feed.entry`` object to a :class:`Review`.

    Entries that lack ``im:rating`` (e.g. the leading app-metadata entry) are
    skipped by returning ``None``.
    """
    rating_label = _label(entry, "im:rating")
    if rating_label is None:
        return None
    try:
        rating = int(rating_label)
    except ValueError:
        return None
    if not 1 <= rating <= 5:
        return None

    return Review(
        rating=rating,
        body=(_label(entry, "content") or "").strip(),
        title=_label(entry, "title"),
        date=_parse_date(_label(entry, "updated")),
        app_name=app_name,
        locale=country,
    )


def _entries(feed_json: dict[str, Any]) -> list[dict[str, Any]]:
    feed = feed_json.get("feed", {})
    entry = feed.get("entry")
    if entry is None:
        return []
    if isinstance(entry, dict):  # single-entry feeds come back as an object
        return [entry]
    return [e for e in entry if isinstance(e, dict)]


class AppStoreFetcher(StoreFetcher):
    """Fetch reviews from the Apple App Store."""

    store = Store.APP_STORE

    def search(self, name: str, country: str = "us") -> AppMatch:
        query = urllib.parse.urlencode(
            {"media": "software", "term": name, "country": country, "limit": 1}
        )
        data = _get_json(f"{_SEARCH_URL}?{query}")
        results = data.get("results") or []
        if not results:
            raise FetchError(f"No App Store app found matching {name!r}.")
        top = results[0]
        return AppMatch(
            app_id=str(top["trackId"]),
            title=top.get("trackName", name),
            store=self.store,
        )

    def resolve(self, app: str, country: str = "us") -> AppMatch:
        app = app.strip()
        if looks_like_app_id(self.store, app):
            app_id = _normalize_id(app)
            return AppMatch(app_id=app_id, title=f"App {app_id}", store=self.store)
        return self.search(app, country=country)

    def fetch(self, match: AppMatch, count: int, country: str = "us") -> list[Review]:
        reviews: list[Review] = []
        for page in range(1, _MAX_PAGES + 1):
            if len(reviews) >= count:
                break
            url = _RSS_URL.format(country=country, page=page, app_id=match.app_id)
            data = _get_json(url)
            entries = _entries(data)
            page_reviews = [
                r
                for r in (_entry_to_review(e, match.title, country) for e in entries)
                if r is not None
            ]
            if not page_reviews:
                break
            reviews.extend(page_reviews)
        return reviews[:count]
