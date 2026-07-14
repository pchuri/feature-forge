"""Clustering step: group similar review embeddings with KMeans."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans

#: Default number of clusters requested for the MVP.
DEFAULT_N_CLUSTERS = 10


@dataclass
class ClusterAssignment:
    """Result of clustering a set of embeddings."""

    labels: np.ndarray  # shape (n_samples,), integer cluster id per review
    centroids: np.ndarray  # shape (n_clusters, n_features)
    n_clusters: int


def cluster_embeddings(
    embeddings: np.ndarray,
    n_clusters: int = DEFAULT_N_CLUSTERS,
    random_state: int = 42,
) -> ClusterAssignment:
    """Cluster ``embeddings`` into at most ``n_clusters`` groups with KMeans.

    The effective cluster count is capped at the number of samples so that a
    small dataset does not cause KMeans to fail.
    """
    embeddings = np.asarray(embeddings, dtype=np.float32)
    n_samples = embeddings.shape[0]
    if n_samples == 0:
        return ClusterAssignment(
            labels=np.empty((0,), dtype=int),
            centroids=np.empty((0, 0), dtype=np.float32),
            n_clusters=0,
        )

    k = max(1, min(n_clusters, n_samples))
    model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = model.fit_predict(embeddings)
    return ClusterAssignment(
        labels=labels.astype(int),
        centroids=np.asarray(model.cluster_centers_, dtype=np.float32),
        n_clusters=k,
    )
