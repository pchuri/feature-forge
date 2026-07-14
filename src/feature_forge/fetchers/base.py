"""Shared types for store fetchers.

Fetchers turn a store + app reference (name or id) into the same
:class:`~feature_forge.models.Review` objects that the file loaders produce,
so everything downstream (clean/embed/cluster/score) is identical regardless
of where the reviews came from.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

from feature_forge.models import Review


class Store(StrEnum):
    """Supported review sources."""

    GOOGLE_PLAY = "google-play"
    APP_STORE = "app-store"


@dataclass
class AppMatch:
    """A resolved app: its store id plus a human-readable title."""

    app_id: str
    title: str
    store: Store


class FetchError(RuntimeError):
    """Raised when a store lookup or download fails."""


# A Google Play package name, e.g. ``com.whatsapp`` or ``com.google.android.apps.photos``.
_GOOGLE_PLAY_ID = re.compile(r"^[a-zA-Z][\w]*(\.[a-zA-Z][\w]*)+$")
# An App Store numeric id, optionally prefixed with ``id`` (e.g. ``id310633997``).
_APP_STORE_ID = re.compile(r"^(id)?\d+$")


def looks_like_app_id(store: Store, value: str) -> bool:
    """Return True if ``value`` is already a store id rather than an app name."""
    value = value.strip()
    if store is Store.GOOGLE_PLAY:
        return bool(_GOOGLE_PLAY_ID.match(value))
    return bool(_APP_STORE_ID.match(value))


@runtime_checkable
class StoreFetcher(Protocol):
    """Anything that can resolve an app reference and download its reviews."""

    store: Store

    def search(self, name: str, country: str = "us") -> AppMatch:
        """Resolve an app *name* to an :class:`AppMatch` (best hit)."""

    def fetch(self, match: AppMatch, count: int, country: str = "us") -> list[Review]:
        """Download up to ``count`` reviews for a resolved app."""

    def resolve(self, app: str, country: str = "us") -> AppMatch:
        """Resolve ``app`` (name or store id) to an :class:`AppMatch`."""
