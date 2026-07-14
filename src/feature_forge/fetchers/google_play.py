"""Fetch reviews from the Google Play Store via ``google-play-scraper``."""

from __future__ import annotations

import re
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

from feature_forge.models import Review

from .base import AppMatch, FetchError, Store, StoreFetcher, looks_like_app_id

#: Google Play returns reviews in pages; this caps a single API call.
_PAGE_SIZE = 200

_SEARCH_URL = "https://play.google.com/store/search"
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
# Every app on a search results page is linked via /store/apps/details?id=<pkg>.
# The featured (best) match is the first such link, which is far more reliable
# than google-play-scraper's search parser (its top result loses its appId).
_DETAILS_ID = re.compile(r"/store/apps/details\?id=([a-zA-Z][a-zA-Z0-9_.]+)")


def _to_review(raw: dict[str, Any], app_name: str, locale: str) -> Review | None:
    """Map a raw google-play-scraper review dict to a :class:`Review`."""
    score = raw.get("score")
    if score is None:
        return None
    try:
        rating = int(score)
    except (TypeError, ValueError):
        return None
    if not 1 <= rating <= 5:
        return None

    at = raw.get("at")
    review_date = at.date() if isinstance(at, datetime) else None

    return Review(
        rating=rating,
        body=(raw.get("content") or "").strip(),
        title=None,  # Google Play reviews have no title.
        date=review_date,
        app_name=app_name,
        locale=locale,
    )


class GooglePlayFetcher(StoreFetcher):
    """Fetch reviews from Google Play."""

    store = Store.GOOGLE_PLAY

    def __init__(self, lang: str = "en") -> None:
        self.lang = lang

    # -- internal: import the third-party library lazily -------------------
    def _lib(self) -> Any:
        try:
            import google_play_scraper
        except ImportError as exc:  # pragma: no cover - import guard
            raise FetchError(
                "google-play-scraper is not installed. Install it with "
                "'uv sync' (it is a project dependency)."
            ) from exc
        return google_play_scraper

    def _search_ids(self, name: str, country: str) -> list[str]:
        params = urllib.parse.urlencode(
            {"q": name, "c": "apps", "hl": self.lang, "gl": country}
        )
        url = f"{_SEARCH_URL}?{params}"
        request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - fixed https host
                html = response.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            raise FetchError(f"Google Play search failed for {name!r}: {exc}") from exc
        ordered: list[str] = []
        for app_id in _DETAILS_ID.findall(html):
            if app_id not in ordered:
                ordered.append(app_id)
        return ordered

    def _title_for(self, app_id: str) -> str:
        try:
            return str(self._lib().app(app_id)["title"])
        except Exception:  # noqa: BLE001 - title is cosmetic; fall back to the id
            return app_id

    # -- StoreFetcher interface -------------------------------------------
    def search(self, name: str, country: str = "us") -> AppMatch:
        ids = self._search_ids(name, country)
        if not ids:
            raise FetchError(f"No Google Play app found matching {name!r}.")
        app_id = ids[0]
        return AppMatch(app_id=app_id, title=self._title_for(app_id), store=self.store)

    def resolve(self, app: str, country: str = "us") -> AppMatch:
        app = app.strip()
        if looks_like_app_id(self.store, app):
            return AppMatch(app_id=app, title=app, store=self.store)
        return self.search(app, country=country)

    def fetch(self, match: AppMatch, count: int, country: str = "us") -> list[Review]:
        lib = self._lib()
        collected: list[dict[str, Any]] = []
        token = None
        while len(collected) < count:
            want = min(_PAGE_SIZE, count - len(collected))
            try:
                batch, token = lib.reviews(
                    match.app_id,
                    lang=self.lang,
                    country=country,
                    sort=lib.Sort.NEWEST,
                    count=want,
                    continuation_token=token,
                )
            except Exception as exc:  # noqa: BLE001
                raise FetchError(
                    f"Failed to fetch Google Play reviews for {match.app_id!r}: {exc}"
                ) from exc
            if not batch:
                break
            collected.extend(batch)
            if token is None:
                break

        reviews = [_to_review(raw, match.title, country) for raw in collected[:count]]
        return [r for r in reviews if r is not None]
