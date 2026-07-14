"""Shared test fixtures and a deterministic fake embedder (no model download)."""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from feature_forge.models import Review


class HashingEmbedder:
    """A tiny deterministic embedder used to avoid downloading a real model.

    It maps each text to a fixed-size vector derived from a hash of its tokens,
    so semantically similar texts (sharing words) land near each other, which is
    enough to exercise clustering and scoring in tests.
    """

    def __init__(self, dim: int = 32) -> None:
        self.dim = dim

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in text.lower().split():
                digest = hashlib.md5(token.encode("utf-8")).digest()
                idx = int.from_bytes(digest[:4], "little") % self.dim
                vectors[row, idx] += 1.0
        # L2-normalize so distances are comparable.
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms


@pytest.fixture
def fake_embedder() -> HashingEmbedder:
    return HashingEmbedder()


@pytest.fixture
def sample_reviews() -> list[Review]:
    return [
        Review(rating=1, body="Too many ads pop up before every single conversion.", app_name="A"),
        Review(rating=1, body="The app is full of ads and I cannot use it at all.", app_name="A"),
        Review(rating=2, body="Converting a PDF to images is painfully slow.", app_name="B"),
        Review(rating=1, body="PDF conversion is so slow it freezes on files.", app_name="B"),
        Review(rating=5, body="Great app, fast and simple for quick conversions.", app_name="C"),
        Review(rating=4, body="Solid and reliable for everyday image resizing.", app_name="C"),
    ]
