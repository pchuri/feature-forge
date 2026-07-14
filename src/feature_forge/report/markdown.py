"""Render an :class:`AnalysisReport` to a Markdown opportunity report."""

from __future__ import annotations

from feature_forge.models import AnalysisReport, ClusterResult, DatasetSummary

#: Clusters at or above this opportunity score are read as "supporting" the idea.
SUPPORT_THRESHOLD = 45.0


def _summary_section(summary: DatasetSummary) -> list[str]:
    lines = [
        "## Dataset Summary",
        "",
        f"- Total reviews: {summary.total_reviews}",
        f"- Average rating: {summary.average_rating:.2f}",
        f"- Negative review count: {summary.negative_count}",
    ]
    if summary.date_min and summary.date_max:
        lines.append(
            f"- Date range: {summary.date_min.isoformat()} to {summary.date_max.isoformat()}"
        )
    else:
        lines.append("- Date range: not available")
    lines.append("")
    return lines


def _cluster_section(index: int, cluster: ClusterResult) -> list[str]:
    lines = [
        f"### {index}. {cluster.label}",
        "",
        f"- Number of reviews: {cluster.size}",
        f"- Average rating: {cluster.avg_rating:.2f}",
        f"- Negative ratio: {cluster.negative_ratio:.0%}",
        f"- Opportunity score: {cluster.opportunity_score:.1f} / 100",
    ]
    if cluster.keywords:
        lines.append(f"- Top keywords: {', '.join(cluster.keywords)}")
    lines.append("- Representative reviews:")
    if cluster.representative_reviews:
        for review in cluster.representative_reviews:
            snippet = " ".join(review.split())
            lines.append(f"  - \"{snippet}\"")
    else:
        lines.append("  - (none)")
    lines.append("")
    return lines


def _hypothesis_section(report: AnalysisReport) -> list[str]:
    lines = ["## Initial Product Hypothesis", ""]

    if not report.clusters:
        lines.append(
            "No pain-point clusters could be derived from the supplied reviews, so "
            "the idea cannot be validated against this dataset yet."
        )
        lines.append("")
        return lines

    top = report.clusters[0]
    supporting = [c for c in report.clusters if c.opportunity_score >= SUPPORT_THRESHOLD]

    if supporting:
        verdict = (
            f"The idea **\"{report.idea}\"** appears **supported** by the review data."
        )
    else:
        verdict = (
            f"The idea **\"{report.idea}\"** is **weakly supported** by the review "
            "data; pain points exist but are diffuse or mild."
        )

    lines.append(verdict)
    lines.append("")
    lines.append(
        f"The strongest signal is the cluster _{top.label}_ "
        f"({top.size} reviews, {top.negative_ratio:.0%} negative, opportunity "
        f"score {top.opportunity_score:.1f}). "
    )
    if supporting:
        others = ", ".join(f"_{c.label}_" for c in supporting[1:4])
        if others:
            lines[-1] += f"Other supporting clusters include {others}. "
    lines[-1] += (
        "Representative reviews above show the concrete language users use to "
        "describe the problem, which you can mine for messaging and feature scope."
    )
    lines.append("")
    lines.append(
        "> Note: opportunity scores are heuristic (frequency + negativity) and "
        "meant to prioritize where to look, not to replace reading the reviews."
    )
    lines.append("")
    return lines


def render_markdown(report: AnalysisReport) -> str:
    """Return the full Markdown document for ``report``."""
    lines: list[str] = ["# Feature Forge Report", ""]
    lines += ["## Idea", "", report.idea, ""]
    lines += _summary_section(report.summary)
    lines += ["## Top Pain Point Clusters", ""]

    if report.clusters:
        for i, cluster in enumerate(report.clusters, start=1):
            lines += _cluster_section(i, cluster)
    else:
        lines += ["No clusters were produced.", ""]

    lines += _hypothesis_section(report)
    return "\n".join(lines).rstrip() + "\n"
