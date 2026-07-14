"""High-level orchestration tying the pipeline steps into one analysis run."""

from __future__ import annotations

from feature_forge.models import AnalysisReport, DatasetSummary, Review
from feature_forge.pipeline import (
    Embedder,
    cluster_embeddings,
    score_clusters,
)
from feature_forge.pipeline.cluster import DEFAULT_N_CLUSTERS
from feature_forge.pipeline.embed import embed_texts


def build_summary(reviews: list[Review]) -> DatasetSummary:
    """Compute aggregate statistics for a set of (cleaned) reviews."""
    total = len(reviews)
    if total == 0:
        return DatasetSummary(total_reviews=0, average_rating=0.0, negative_count=0)

    average = sum(r.rating for r in reviews) / total
    negative = sum(1 for r in reviews if r.is_negative)
    dates = sorted(r.date for r in reviews if r.date is not None)

    return DatasetSummary(
        total_reviews=total,
        average_rating=round(average, 2),
        negative_count=negative,
        date_min=dates[0] if dates else None,
        date_max=dates[-1] if dates else None,
    )


def analyze(
    reviews: list[Review],
    idea: str,
    n_clusters: int = DEFAULT_N_CLUSTERS,
    embedder: Embedder | None = None,
) -> AnalysisReport:
    """Run embed -> cluster -> score over already-cleaned ``reviews``.

    ``embedder`` can be injected (e.g. in tests) to avoid downloading a model.
    """
    summary = build_summary(reviews)
    if not reviews:
        return AnalysisReport(idea=idea, summary=summary, clusters=[])

    embeddings = embed_texts([r.text for r in reviews], embedder=embedder)
    assignment = cluster_embeddings(embeddings, n_clusters=n_clusters)
    clusters = score_clusters(reviews, embeddings, assignment)
    return AnalysisReport(idea=idea, summary=summary, clusters=clusters)
