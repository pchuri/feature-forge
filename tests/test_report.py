"""Tests for analysis orchestration and Markdown report generation."""

from __future__ import annotations

from datetime import date

from feature_forge.analysis import analyze, build_summary
from feature_forge.models import (
    AnalysisReport,
    ClusterResult,
    DatasetSummary,
    Review,
)
from feature_forge.report import render_markdown


def test_build_summary() -> None:
    reviews = [
        Review(rating=1, body="bad one here", date=date(2026, 1, 1)),
        Review(rating=5, body="great one here", date=date(2026, 3, 1)),
        Review(rating=2, body="meh one here"),
    ]
    summary = build_summary(reviews)
    assert summary.total_reviews == 3
    assert summary.negative_count == 2
    assert summary.average_rating == round((1 + 5 + 2) / 3, 2)
    assert summary.date_min == date(2026, 1, 1)
    assert summary.date_max == date(2026, 3, 1)


def test_analyze_with_fake_embedder(sample_reviews, fake_embedder) -> None:
    report = analyze(
        sample_reviews, idea="PDF to Image converter", n_clusters=3, embedder=fake_embedder
    )

    assert isinstance(report, AnalysisReport)
    assert report.idea == "PDF to Image converter"
    assert report.summary.total_reviews == len(sample_reviews)
    assert 1 <= len(report.clusters) <= 3
    # Total reviews across clusters equals input count.
    assert sum(c.size for c in report.clusters) == len(sample_reviews)
    # Sorted by opportunity score, descending.
    scores = [c.opportunity_score for c in report.clusters]
    assert scores == sorted(scores, reverse=True)


def test_render_markdown_contains_all_sections() -> None:
    report = AnalysisReport(
        idea="PDF to Image converter",
        summary=DatasetSummary(
            total_reviews=10,
            average_rating=2.5,
            negative_count=6,
            date_min=date(2026, 1, 1),
            date_max=date(2026, 3, 1),
        ),
        clusters=[
            ClusterResult(
                cluster_id=0,
                label="Slow, Conversion, Pdf",
                size=6,
                avg_rating=1.8,
                negative_ratio=0.83,
                opportunity_score=71.5,
                keywords=["slow", "conversion", "pdf"],
                representative_reviews=["Converting a PDF is painfully slow."],
            )
        ],
    )

    md = render_markdown(report)

    assert md.startswith("# Feature Forge Report")
    assert "## Idea" in md
    assert "PDF to Image converter" in md
    assert "## Dataset Summary" in md
    assert "Total reviews: 10" in md
    assert "Date range: 2026-01-01 to 2026-03-01" in md
    assert "## Top Pain Point Clusters" in md
    assert "Slow, Conversion, Pdf" in md
    assert "Opportunity score: 71.5" in md
    assert "Converting a PDF is painfully slow." in md
    assert "## Initial Product Hypothesis" in md
    assert "supported" in md.lower()


def _cluster(
    cluster_id: int,
    label: str,
    opportunity_score: float,
    idea_similarity: float | None,
    negative_ratio: float = 0.8,
) -> ClusterResult:
    return ClusterResult(
        cluster_id=cluster_id,
        label=label,
        size=10,
        avg_rating=1.9,
        negative_ratio=negative_ratio,
        opportunity_score=opportunity_score,
        idea_similarity=idea_similarity,
    )


def _report(
    clusters: list[ClusterResult], idea: str = "AI-powered smart replies"
) -> AnalysisReport:
    return AnalysisReport(
        idea=idea,
        summary=DatasetSummary(total_reviews=50, average_rating=2.1, negative_count=30),
        clusters=clusters,
    )


def test_verdict_not_supported_when_top_clusters_unrelated() -> None:
    """High-scoring clusters that are semantically unrelated must not support the idea."""
    md = render_markdown(
        _report(
            [
                _cluster(0, "Login, Phone Number", 70.0, idea_similarity=0.05),
                _cluster(1, "Account, Verification", 55.0, idea_similarity=0.10),
            ]
        )
    )
    assert "**not supported**" in md
    assert "unrelated to the idea" in md
    assert "absence of evidence is evidence" in md
    assert "appears **supported**" not in md


def test_verdict_supported_only_by_relevant_clusters() -> None:
    """An unrelated top scorer is excluded; the relevant cluster drives the verdict."""
    md = render_markdown(
        _report(
            [
                _cluster(0, "Login, Phone Number", 70.0, idea_similarity=0.05),
                _cluster(1, "Smart Reply, Translation", 50.0, idea_similarity=0.62),
            ]
        )
    )
    assert "appears **supported**" in md
    assert "strongest idea-relevant signal is the cluster _Smart Reply, Translation_" in md
    assert "_Login, Phone Number_" in md  # named as excluded
    assert "excluded from the verdict" in md


def test_verdict_weakly_supported_when_relevant_but_mild() -> None:
    md = render_markdown(
        _report(
            [
                _cluster(0, "Login, Phone Number", 70.0, idea_similarity=0.05),
                _cluster(1, "Smart Reply, Translation", 30.0, idea_similarity=0.62),
            ]
        )
    )
    assert "**weakly supported**" in md
    assert "_Smart Reply, Translation_" in md


def test_cluster_section_shows_idea_relevance() -> None:
    md = render_markdown(
        _report([_cluster(0, "Smart Reply, Translation", 50.0, idea_similarity=0.62)])
    )
    assert "Idea relevance: 0.62 (relevant to the idea)" in md


def test_analyze_attaches_idea_similarity(sample_reviews, fake_embedder) -> None:
    report = analyze(
        sample_reviews, idea="PDF to Image converter", n_clusters=3, embedder=fake_embedder
    )
    assert report.clusters
    for cluster in report.clusters:
        assert cluster.idea_similarity is not None
        assert -1.0 <= cluster.idea_similarity <= 1.0


def test_render_markdown_no_clusters() -> None:
    report = AnalysisReport(
        idea="Some idea",
        summary=DatasetSummary(total_reviews=0, average_rating=0.0, negative_count=0),
        clusters=[],
    )
    md = render_markdown(report)
    assert "## Initial Product Hypothesis" in md
    assert "cannot be validated" in md
