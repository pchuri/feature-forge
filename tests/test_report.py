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


def test_render_markdown_no_clusters() -> None:
    report = AnalysisReport(
        idea="Some idea",
        summary=DatasetSummary(total_reviews=0, average_rating=0.0, negative_count=0),
        clusters=[],
    )
    md = render_markdown(report)
    assert "## Initial Product Hypothesis" in md
    assert "cannot be validated" in md
