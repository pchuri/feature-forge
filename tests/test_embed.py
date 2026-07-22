"""Tests for embedder construction — offline, no model download, no API calls."""

from __future__ import annotations

import sys
import types

import numpy as np
import pytest

from feature_forge.pipeline.embed import (
    OPENAI_DEFAULT_MODEL,
    EmbeddingError,
    OpenAIEmbedder,
    make_embedder,
)


class _FakeOpenAIClient:
    def __init__(self, dim: int = 4) -> None:
        self.dim = dim
        self.calls: list[list[str]] = []
        self.embeddings = types.SimpleNamespace(create=self._create)

    def _create(self, model: str, input: list[str]):  # noqa: A002 - mirrors the API
        self.calls.append(list(input))
        data = [
            types.SimpleNamespace(embedding=[float(len(text))] * self.dim)
            for text in input
        ]
        return types.SimpleNamespace(data=data)


@pytest.fixture
def fake_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide a stub ``openai`` package and an API key."""
    module = types.ModuleType("openai")
    module.OpenAI = lambda: _FakeOpenAIClient()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", module)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


def test_make_embedder_routes_openai_prefix(fake_openai) -> None:
    embedder = make_embedder("openai:custom-model")
    assert isinstance(embedder, OpenAIEmbedder)
    assert embedder.model_name == "custom-model"


def test_make_embedder_openai_defaults_model(fake_openai) -> None:
    embedder = make_embedder("openai:")
    assert isinstance(embedder, OpenAIEmbedder)
    assert embedder.model_name == OPENAI_DEFAULT_MODEL


def test_openai_embedder_requires_api_key(fake_openai, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY")
    with pytest.raises(EmbeddingError, match="OPENAI_API_KEY"):
        OpenAIEmbedder()


def test_openai_embedder_encodes_batched_and_normalized(fake_openai) -> None:
    embedder = OpenAIEmbedder(batch_size=2)
    client = _FakeOpenAIClient()
    embedder._client = client

    vectors = embedder.encode(["a", "bb", "ccc"])

    assert vectors.shape == (3, 4)
    assert vectors.dtype == np.float32
    # batch_size=2 -> two API calls.
    assert [len(call) for call in client.calls] == [2, 1]
    # Rows are unit-normalized like the sentence-transformers path.
    np.testing.assert_allclose(np.linalg.norm(vectors, axis=1), 1.0, rtol=1e-5)


def test_openai_embedder_replaces_empty_text(fake_openai) -> None:
    embedder = OpenAIEmbedder()
    client = _FakeOpenAIClient()
    embedder._client = client

    embedder.encode(["", "ok"])

    assert client.calls == [[" ", "ok"]]
