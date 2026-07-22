"""Store fetchers: download reviews straight from Google Play / the App Store."""

from __future__ import annotations

from feature_forge.models import Review

from .apple_app_store import AppStoreFetcher
from .base import AppMatch, FetchError, Store, StoreFetcher, looks_like_app_id
from .google_play import GooglePlayFetcher

__all__ = [
    "AppMatch",
    "AppStoreFetcher",
    "FetchError",
    "GooglePlayFetcher",
    "Store",
    "StoreFetcher",
    "get_fetcher",
    "fetch_reviews",
    "looks_like_app_id",
]


def get_fetcher(store: Store, lang: str = "en") -> StoreFetcher:
    """Return the fetcher implementation for ``store``.

    ``lang`` selects the review language on Google Play (which filters reviews
    by language, not country). The App Store feed is per-country and has no
    language filter, so ``lang`` is ignored there.
    """
    if store is Store.GOOGLE_PLAY:
        return GooglePlayFetcher(lang=lang)
    if store is Store.APP_STORE:
        return AppStoreFetcher()
    raise FetchError(f"Unsupported store: {store}")  # pragma: no cover


def fetch_reviews(
    store: Store,
    app: str,
    count: int = 500,
    country: str = "us",
    lang: str = "en",
) -> tuple[list[Review], AppMatch]:
    """Resolve ``app`` (name or id) on ``store`` and download up to ``count`` reviews.

    Returns the reviews plus the resolved :class:`AppMatch` so callers can show
    exactly which app was matched.
    """
    fetcher = get_fetcher(store, lang=lang)
    match = fetcher.resolve(app, country=country)
    reviews = fetcher.fetch(match, count=count, country=country)
    return reviews, match
