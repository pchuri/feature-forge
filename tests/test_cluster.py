"""Tests for the clustering step output shape."""

from __future__ import annotations

import numpy as np

from feature_forge.pipeline.cluster import cluster_embeddings


def test_cluster_output_shape() -> None:
    rng = np.random.default_rng(0)
    embeddings = rng.random((30, 16), dtype=np.float32)

    assignment = cluster_embeddings(embeddings, n_clusters=5)

    assert assignment.n_clusters == 5
    assert assignment.labels.shape == (30,)
    assert assignment.centroids.shape == (5, 16)
    # Every label is a valid cluster id.
    assert set(np.unique(assignment.labels)).issubset(set(range(5)))


def test_cluster_count_capped_to_samples() -> None:
    rng = np.random.default_rng(1)
    embeddings = rng.random((3, 8), dtype=np.float32)

    assignment = cluster_embeddings(embeddings, n_clusters=10)

    # Cannot have more clusters than samples.
    assert assignment.n_clusters == 3
    assert assignment.labels.shape == (3,)
    assert assignment.centroids.shape == (3, 8)


def test_cluster_empty_input() -> None:
    assignment = cluster_embeddings(np.empty((0, 8), dtype=np.float32))
    assert assignment.n_clusters == 0
    assert assignment.labels.shape == (0,)
