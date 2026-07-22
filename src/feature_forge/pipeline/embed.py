"""Embedding step: turn review text into dense vectors.

The heavy ``sentence-transformers`` import is deferred until an embedder is
actually constructed, so importing this module (e.g. in tests) stays cheap and
does not require the model to be downloaded.
"""

from __future__ import annotations

import os
from typing import Protocol, runtime_checkable

import numpy as np

#: Small, fast, widely used default model. Downloaded on first use.
DEFAULT_MODEL = "all-MiniLM-L6-v2"

#: Default model when the ``openai:`` provider is selected without a model name.
OPENAI_DEFAULT_MODEL = "text-embedding-3-small"

#: Reviews are short; this guards the API's per-input token limit regardless.
_OPENAI_MAX_CHARS = 4000


class EmbeddingError(RuntimeError):
    """Raised when an embedder cannot be constructed (missing package/credentials)."""


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


class OpenAIEmbedder:
    """Embedder backed by the OpenAI embeddings API.

    Opt-in alternative to the local default: it sends review text to a paid
    external API, but needs no model download and is strong on multilingual
    input. Requires the ``openai`` extra and an ``OPENAI_API_KEY``.
    """

    def __init__(
        self, model_name: str = OPENAI_DEFAULT_MODEL, batch_size: int = 500
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise EmbeddingError(
                "The 'openai' package is not installed. Install it with "
                "'uv sync --extra openai' (or 'pip install feature-forge[openai]')."
            ) from exc
        if not os.environ.get("OPENAI_API_KEY"):
            raise EmbeddingError(
                "OPENAI_API_KEY is not set. OpenAI embeddings call a paid "
                "external API and need an API key in the environment."
            )
        self.model_name = model_name
        self.batch_size = batch_size
        self._client = OpenAI()

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            # The API rejects empty strings; reviews are pre-cleaned, but guard anyway.
            batch = [t[:_OPENAI_MAX_CHARS] or " " for t in texts[start : start + self.batch_size]]
            response = self._client.embeddings.create(model=self.model_name, input=batch)
            vectors.extend(item.embedding for item in response.data)
        array = np.asarray(vectors, dtype=np.float32)
        # Normalize like the sentence-transformers path so cluster geometry matches.
        norms = np.linalg.norm(array, axis=1, keepdims=True)
        return array / np.clip(norms, 1e-12, None)


def make_embedder(spec: str) -> Embedder:
    """Build an embedder from a model spec.

    ``openai:<model>`` (or bare ``openai:``) selects the OpenAI embeddings
    API; anything else is a local sentence-transformers model name.
    """
    provider, _, model_name = spec.partition(":")
    if provider == "openai":
        return OpenAIEmbedder(model_name or OPENAI_DEFAULT_MODEL)
    return SentenceTransformerEmbedder(spec)


def embed_texts(texts: list[str], embedder: Embedder | None = None) -> np.ndarray:
    """Embed ``texts`` with ``embedder`` (defaulting to the sentence transformer)."""
    if embedder is None:
        embedder = SentenceTransformerEmbedder()
    if not texts:
        return np.empty((0, 0), dtype=np.float32)
    return embedder.encode(texts)
