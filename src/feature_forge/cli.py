"""Feature Forge command-line interface."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from feature_forge import __version__
from feature_forge.analysis import analyze
from feature_forge.export import save_reviews
from feature_forge.fetchers import FetchError, Store, fetch_reviews
from feature_forge.loaders import load_reviews
from feature_forge.models import AnalysisReport, Review
from feature_forge.pipeline.clean import clean_reviews
from feature_forge.pipeline.cluster import DEFAULT_N_CLUSTERS
from feature_forge.pipeline.embed import DEFAULT_MODEL, EmbeddingError, make_embedder
from feature_forge.report import render_markdown

app = typer.Typer(
    add_completion=False,
    help="Validate product ideas against real user pain points mined from app reviews.",
)
console = Console()

# Apple's public customer-reviews RSS feed has been returning empty for all apps;
# this affects every tool built on it (not just Feature Forge). Point users at the
# alternatives rather than failing silently.
_APP_STORE_EMPTY_HINT = (
    "[yellow]Apple's public reviews feed returned no reviews. This is a known "
    "limitation of Apple's RSS endpoint (currently empty for all apps), not a bug "
    "in the app match. Try --store google-play, or analyze a saved file.[/yellow]"
)


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


def _gather_reviews(
    input_file: Path | None,
    store: Store | None,
    app_ref: str | None,
    count: int,
    country: str,
    lang: str,
    save: Path | None,
) -> list[Review]:
    """Load reviews from a file or fetch them from a store, per the given options."""
    if input_file is not None and store is not None:
        console.print(
            "[red]Provide either a REVIEWS file or --store/--app, not both.[/red]"
        )
        raise typer.Exit(code=2)

    if store is not None:
        if not app_ref:
            console.print("[red]--store requires --app (an app name or store id).[/red]")
            raise typer.Exit(code=2)
        console.print(
            f"[bold]Fetching[/bold] up to {count} reviews for "
            f"{app_ref!r} from {store}..."
        )
        try:
            reviews, match = fetch_reviews(
                store, app_ref, count=count, country=country, lang=lang
            )
        except FetchError as exc:
            console.print(f"[red]Fetch failed:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(f"  matched app: [cyan]{match.title}[/cyan] ({match.app_id})")
        console.print(f"  downloaded {len(reviews)} review(s)")
        if not reviews and store is Store.APP_STORE:
            console.print(_APP_STORE_EMPTY_HINT)
        if save is not None:
            save_reviews(reviews, save)
            console.print(f"  saved raw reviews to {save}")
        return reviews

    if input_file is not None:
        console.print(f"[bold]Loading[/bold] reviews from {input_file}...")
        reviews = load_reviews(input_file)
        console.print(f"  loaded {len(reviews)} review(s)")
        return reviews

    console.print(
        "[red]Nothing to analyze. Pass a REVIEWS file or use "
        "--store <store> --app <name|id>.[/red]"
    )
    raise typer.Exit(code=2)


def analyze_command(  # noqa: PLR0913 - explicit CLI options read better flat
    input_file: Path | None = typer.Argument(
        None,
        exists=True,
        dir_okay=False,
        readable=True,
        metavar="[REVIEWS]",
        help="Path to a reviews .csv, .json or .jsonl file (omit when using --store).",
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
    store: Store | None = typer.Option(
        None,
        "--store",
        "-s",
        help="Fetch reviews from this store instead of a file.",
    ),
    app_ref: str | None = typer.Option(
        None,
        "--app",
        help="App name (auto-searched) or store id to fetch reviews for.",
    ),
    count: int = typer.Option(
        500,
        "--reviews",
        "-n",
        min=1,
        help="Max number of reviews to fetch (when using --store).",
    ),
    country: str = typer.Option(
        "us",
        "--country",
        help="Store country/locale code used for search and reviews.",
    ),
    lang: str = typer.Option(
        "en",
        "--lang",
        help=(
            "Review language code for Google Play (e.g. 'ja'). Google Play "
            "filters reviews by language, so --country alone does not change "
            "the review language. Ignored for app-store."
        ),
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        help=(
            "Embedding model. A sentence-transformers name runs locally (for "
            "non-English reviews try 'paraphrase-multilingual-MiniLM-L12-v2'); "
            "'openai:<model>' (e.g. 'openai:text-embedding-3-small') uses the "
            "OpenAI API instead — requires the 'openai' extra and "
            "OPENAI_API_KEY, and sends review text to a paid external API."
        ),
    ),
    save: Path | None = typer.Option(
        None,
        "--save",
        help="Also save the fetched raw reviews to this .csv/.json file.",
    ),
) -> None:
    """Analyze reviews (from a file or a store) and write a Markdown report."""
    reviews = _gather_reviews(input_file, store, app_ref, count, country, lang, save)

    if not reviews:
        console.print("[red]No usable reviews were obtained. Aborting.[/red]")
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
    try:
        embedder = make_embedder(model)
    except EmbeddingError as exc:
        console.print(f"[red]Embedding setup failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    report = analyze(cleaned, idea=idea, n_clusters=clusters, embedder=embedder)

    _print_cluster_table(report)

    output.write_text(render_markdown(report), encoding="utf-8")
    console.print(f"\n[green]Report written to[/green] {output}")


def fetch_command(
    store: Store = typer.Argument(..., help="Which store to fetch from."),
    app_ref: str = typer.Argument(
        ..., metavar="APP", help="App name (auto-searched) or store id."
    ),
    count: int = typer.Option(500, "--count", "-n", min=1, help="Max reviews to fetch."),
    country: str = typer.Option("us", "--country", help="Store country/locale code."),
    lang: str = typer.Option(
        "en",
        "--lang",
        help=(
            "Review language code for Google Play (e.g. 'ja'). Ignored for "
            "app-store."
        ),
    ),
    output: Path = typer.Option(
        Path("reviews.csv"),
        "--output",
        "-o",
        help="Where to save the downloaded reviews (.csv/.json).",
    ),
) -> None:
    """Download reviews from a store and save them to a file (no analysis)."""
    console.print(f"[bold]Fetching[/bold] up to {count} reviews for {app_ref!r} from {store}...")
    try:
        reviews, match = fetch_reviews(
            store, app_ref, count=count, country=country, lang=lang
        )
    except FetchError as exc:
        console.print(f"[red]Fetch failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"  matched app: [cyan]{match.title}[/cyan] ({match.app_id})")
    console.print(f"  downloaded {len(reviews)} review(s)")

    if not reviews:
        console.print("[yellow]No reviews downloaded; nothing saved.[/yellow]")
        if store is Store.APP_STORE:
            console.print(_APP_STORE_EMPTY_HINT)
        raise typer.Exit(code=1)

    save_reviews(reviews, output)
    console.print(f"[green]Saved[/green] {len(reviews)} review(s) to {output}")


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


# Typer derives command names from the functions; register explicit names.
app.command(name="analyze")(analyze_command)
app.command(name="fetch")(fetch_command)


if __name__ == "__main__":
    app()
