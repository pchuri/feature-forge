"""Scoring step: derive opportunity metrics and extractive summaries per cluster."""

from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

from feature_forge.models import ClusterResult, Review

from .cluster import ClusterAssignment

#: How many keywords / representative reviews to surface per cluster.
TOP_KEYWORDS = 6
TOP_REPRESENTATIVES = 3


def _extract_keywords(texts: list[str], top_n: int = TOP_KEYWORDS) -> list[str]:
    """Return the most frequent, non-stopword unigrams/bigrams for ``texts``."""
    if not texts:
        return []
    vectorizer = CountVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]+\b",
    )
    try:
        matrix = vectorizer.fit_transform(texts)
    except ValueError:
        # Happens when every token is a stop word / too short.
        return []
    counts = np.asarray(matrix.sum(axis=0)).ravel()
    vocab = np.array(vectorizer.get_feature_names_out())
    order = np.argsort(counts)[::-1]
    return [str(vocab[i]) for i in order[:top_n]]


def _representative_reviews(
    reviews: list[Review],
    member_embeddings: np.ndarray,
    centroid: np.ndarray,
    top_n: int = TOP_REPRESENTATIVES,
) -> list[str]:
    """Pick the reviews whose embeddings sit closest to the cluster centroid."""
    if not reviews:
        return []
    distances = np.linalg.norm(member_embeddings - centroid, axis=1)
    order = np.argsort(distances)
    return [reviews[i].text for i in order[:top_n]]


def _opportunity_score(size: int, total: int, negative_ratio: float) -> float:
    """Heuristic 0-100 score blending how common and how painful a cluster is.

    A cluster scores high when it is both frequent (many users hit it) and
    negative (users are unhappy about it) — the shape of a real opportunity.
    """
    frequency = size / total if total else 0.0
    raw = 0.6 * negative_ratio + 0.4 * frequency
    return round(raw * 100, 1)


def _heuristic_label(keywords: list[str]) -> str:
    if not keywords:
        return "Uncategorized feedback"
    return ", ".join(keywords[:3]).title()


def score_clusters(
    reviews: list[Review],
    embeddings: np.ndarray,
    assignment: ClusterAssignment,
) -> list[ClusterResult]:
    """Build a scored :class:`ClusterResult` for each cluster, best first."""
    total = len(reviews)
    results: list[ClusterResult] = []

    for cluster_id in range(assignment.n_clusters):
        mask = assignment.labels == cluster_id
        indices = np.where(mask)[0]
        if indices.size == 0:
            continue

        members = [reviews[i] for i in indices]
        member_embeddings = embeddings[indices]
        ratings = np.array([r.rating for r in members], dtype=float)
        negative_count = sum(1 for r in members if r.is_negative)
        negative_ratio = negative_count / len(members)

        keywords = _extract_keywords([r.text for r in members])
        representatives = _representative_reviews(
            members, member_embeddings, assignment.centroids[cluster_id]
        )

        results.append(
            ClusterResult(
                cluster_id=int(cluster_id),
                label=_heuristic_label(keywords),
                size=len(members),
                avg_rating=round(float(ratings.mean()), 2),
                negative_ratio=round(negative_ratio, 3),
                opportunity_score=_opportunity_score(len(members), total, negative_ratio),
                keywords=keywords,
                representative_reviews=representatives,
            )
        )

    results.sort(key=lambda c: c.opportunity_score, reverse=True)
    return results
