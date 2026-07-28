"""Render an :class:`AnalysisReport` to a Markdown opportunity report."""

from __future__ import annotations

from feature_forge.models import AnalysisReport, ClusterResult, DatasetSummary

#: Clusters at or above this opportunity score are read as "supporting" the idea.
SUPPORT_THRESHOLD = 45.0

#: Minimum cosine similarity between the idea and a cluster centroid for the
#: cluster to count as evidence about the idea at all. Below this, a cluster is
#: real pain but *unrelated* pain — it says nothing about the idea. Heuristic,
#: tuned for normalized sentence-transformer embeddings.
RELEVANCE_THRESHOLD = 0.3


def _is_relevant(cluster: ClusterResult) -> bool:
    """Whether a cluster is semantically about the idea.

    Clusters without a similarity (reports produced before idea embedding
    existed, or built by hand) are treated as relevant for backward
    compatibility.
    """
    return cluster.idea_similarity is None or cluster.idea_similarity >= RELEVANCE_THRESHOLD


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
    if cluster.idea_similarity is not None:
        relevance = "relevant" if _is_relevant(cluster) else "unrelated"
        lines.append(
            f"- Idea relevance: {cluster.idea_similarity:.2f} ({relevance} to the idea)"
        )
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

    relevant = [c for c in report.clusters if _is_relevant(c)]
    supporting = [c for c in relevant if c.opportunity_score >= SUPPORT_THRESHOLD]

    if not relevant:
        top_unrelated = ", ".join(f"_{c.label}_" for c in report.clusters[:3])
        lines.append(
            f"The idea **\"{report.idea}\"** is **not supported** by this review "
            "data: the dominant pain points are unrelated to the idea. The "
            f"top clusters ({top_unrelated}) concern other problems, and no "
            "cluster semantically related to the idea rose above the noise. "
            "Real pain exists in this market, but it is not evidence for this "
            "idea — absence of evidence is evidence."
        )
        lines.append("")
        lines.append(_note_line())
        lines.append("")
        return lines

    top = supporting[0] if supporting else relevant[0]

    if supporting:
        verdict = (
            f"The idea **\"{report.idea}\"** appears **supported** by the review data."
        )
    else:
        verdict = (
            f"The idea **\"{report.idea}\"** is **weakly supported** by the review "
            "data; pain points related to the idea exist but are diffuse or mild."
        )

    lines.append(verdict)
    lines.append("")
    lines.append(
        f"The strongest idea-relevant signal is the cluster _{top.label}_ "
        f"({top.size} reviews, {top.negative_ratio:.0%} negative, opportunity "
        f"score {top.opportunity_score:.1f}). "
    )
    if supporting:
        others = ", ".join(f"_{c.label}_" for c in supporting[1:4])
        if others:
            lines[-1] += f"Other supporting clusters include {others}. "
    excluded = [
        c
        for c in report.clusters
        if not _is_relevant(c) and c.opportunity_score >= SUPPORT_THRESHOLD
    ]
    if excluded:
        excluded_names = ", ".join(f"_{c.label}_" for c in excluded[:3])
        lines[-1] += (
            f"High-scoring but unrelated clusters ({excluded_names}) were "
            "excluded from the verdict — they are real pain, but not evidence "
            "for this idea. "
        )
    lines[-1] += (
        "Representative reviews above show the concrete language users use to "
        "describe the problem, which you can mine for messaging and feature scope."
    )
    lines.append("")
    lines.append(_note_line())
    lines.append("")
    return lines


def _note_line() -> str:
    return (
        "> Note: opportunity scores are heuristic (frequency + negativity) and "
        "idea relevance is embedding cosine similarity — both prioritize where "
        "to look, not replace reading the reviews. In particular, read the "
        "relevant clusters' representative reviews to check whether the "
        "negativity is demand *for* the idea or backlash *against* it."
    )


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
