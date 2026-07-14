"""Feature Forge command-line interface."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from feature_forge import __version__
from feature_forge.analysis import analyze
from feature_forge.loaders import load_reviews
from feature_forge.models import AnalysisReport
from feature_forge.pipeline.clean import clean_reviews
from feature_forge.pipeline.cluster import DEFAULT_N_CLUSTERS
from feature_forge.report import render_markdown

app = typer.Typer(
    add_completion=False,
    help="Validate product ideas against real user pain points mined from app reviews.",
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"feature-forge {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: bool | None = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the Feature Forge version and exit.",
    ),
) -> None:
    """Feature Forge CLI."""


@app.command()
def analyze_command(  # noqa: PLR0913 - explicit CLI options read better flat
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        dir_okay=False,
        readable=True,
        metavar="REVIEWS",
        help="Path to a reviews .csv, .json or .jsonl file.",
    ),
    idea: str = typer.Option(
        ...,
        "--idea",
        "-i",
        help="The product idea you want to validate.",
    ),
    output: Path = typer.Option(
        Path("report.md"),
        "--output",
        "-o",
        help="Where to write the Markdown report.",
    ),
    clusters: int = typer.Option(
        DEFAULT_N_CLUSTERS,
        "--clusters",
        "-k",
        min=1,
        help="Number of KMeans clusters to request.",
    ),
) -> None:
    """Analyze reviews and generate a Markdown opportunity report."""
    console.print(f"[bold]Loading[/bold] reviews from {input_file}...")
    reviews = load_reviews(input_file)
    console.print(f"  loaded {len(reviews)} review(s)")

    if not reviews:
        console.print("[red]No usable reviews were loaded. Aborting.[/red]")
        raise typer.Exit(code=1)

    cleaned, stats = clean_reviews(reviews)
    console.print(
        f"[bold]Cleaned[/bold]: kept {stats.output_count}, "
        f"removed {stats.empty_removed} empty, {stats.short_removed} short, "
        f"{stats.duplicate_removed} duplicate."
    )

    if not cleaned:
        console.print("[red]No reviews left after cleaning. Aborting.[/red]")
        raise typer.Exit(code=1)

    console.print(
        f"[bold]Embedding + clustering[/bold] {len(cleaned)} reviews "
        f"(k={min(clusters, len(cleaned))})... this may download a model on first run."
    )
    report = analyze(cleaned, idea=idea, n_clusters=clusters)

    _print_cluster_table(report)

    output.write_text(render_markdown(report), encoding="utf-8")
    console.print(f"\n[green]Report written to[/green] {output}")


def _print_cluster_table(report: AnalysisReport) -> None:
    table = Table(title="Top Pain Point Clusters")
    table.add_column("#", justify="right")
    table.add_column("Cluster")
    table.add_column("Reviews", justify="right")
    table.add_column("Avg", justify="right")
    table.add_column("Neg%", justify="right")
    table.add_column("Score", justify="right")

    for i, cluster in enumerate(report.clusters[:10], start=1):
        table.add_row(
            str(i),
            cluster.label,
            str(cluster.size),
            f"{cluster.avg_rating:.2f}",
            f"{cluster.negative_ratio:.0%}",
            f"{cluster.opportunity_score:.1f}",
        )
    console.print(table)


# Typer derives the command name from the function; expose it as "analyze".
app.command(name="analyze")(analyze_command)


if __name__ == "__main__":
    app()
