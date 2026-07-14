"""Embedding step: turn review text into dense vectors.

The heavy ``sentence-transformers`` import is deferred until an embedder is
actually constructed, so importing this module (e.g. in tests) stays cheap and
does not require the model to be downloaded.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np

#: Small, fast, widely used default model. Downloaded on first use.
DEFAULT_MODEL = "all-MiniLM-L6-v2"


@runtime_checkable
class Embedder(Protocol):
    """Anything that can turn a list of strings into a 2D float array."""

    def encode(self, texts: list[str]) -> np.ndarray: ...


class SentenceTransformerEmbedder:
    """Embedder backed by a ``sentence-transformers`` model."""

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return np.asarray(vectors, dtype=np.float32)


def embed_texts(texts: list[str], embedder: Embedder | None = None) -> np.ndarray:
    """Embed ``texts`` with ``embedder`` (defaulting to the sentence transformer)."""
    if embedder is None:
        embedder = SentenceTransformerEmbedder()
    if not texts:
        return np.empty((0, 0), dtype=np.float32)
    return embedder.encode(texts)
