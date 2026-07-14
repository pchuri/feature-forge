# Feature Forge

**Validate product ideas against real user pain points mined from app reviews.**

Feature Forge is a CLI tool for indie developers. Instead of generating random
startup ideas, it helps you answer a sharper question:

> *Is this product idea actually supported by real pain points that users are
> already complaining about?*

You point it at a file of existing app reviews (CSV or JSON), give it your idea,
and it produces a Markdown **opportunity report**: the dominant pain-point
clusters, how frequent and how negative each one is, representative quotes, and a
heuristic verdict on whether your idea is supported by the data.

> **MVP scope.** Feature Forge works on **local input files** only. App Store /
> Google Play scraping is intentionally out of scope for now. All analysis runs
> locally — **no paid LLM API is called.** Cluster summaries are extractive
> (top keywords + reviews closest to the cluster centroid + simple heuristic
> labels). LLM-based summarization can be layered on later.

## How it works

```
reviews.csv ──► load ──► clean ──► embed ──► cluster ──► score ──► report.md
                          │          │          │           │
                    drop empty,  sentence-   KMeans     frequency,
                    short, dupes transformers (k=10)    avg rating,
                                                        negative ratio,
                                                        opportunity score
```

1. **Load** reviews from a CSV or JSON file.
2. **Clean**: drop empty bodies, duplicates, and reviews under 10 characters.
3. **Embed** review text with [`sentence-transformers`](https://www.sbert.net/)
   (`all-MiniLM-L6-v2`, downloaded on first run).
4. **Cluster** similar reviews with KMeans (default `k=10`).
5. **Score** each cluster: frequency, average rating, negative-review ratio, and
   a heuristic opportunity score (0–100) blending how *common* and how *painful*
   the cluster is.
6. **Report**: render a Markdown opportunity report.

## Install

Feature Forge uses [uv](https://docs.astral.sh/uv/). With the repo cloned:

```bash
uv sync
```

This creates a virtual environment and installs Feature Forge plus its
dependencies. (Python 3.12+ is required; `uv` will fetch it if needed.)

## Run the sample

A bundled example dataset (`examples/reviews.csv`) contains ~28 reviews about
image/PDF conversion apps — ads, slow conversions, missing batch mode, HEIC
support, sharing, compression quality, and crashes.

```bash
uv run feature-forge analyze examples/reviews.csv \
  --idea "PDF to Image converter" \
  --output report.md
```

Open `report.md` to see the generated opportunity report.

### CLI

```
feature-forge analyze REVIEWS --idea "<your idea>" [--output report.md] [--clusters 10]
```

| Option | Alias | Default | Description |
| --- | --- | --- | --- |
| `REVIEWS` | | — | Path to a `.csv`, `.json` or `.jsonl` reviews file (required). |
| `--idea` | `-i` | — | The product idea to validate (required). |
| `--output` | `-o` | `report.md` | Where to write the Markdown report. |
| `--clusters` | `-k` | `10` | Number of KMeans clusters to request. |

## Input format

CSV files must include a `rating` and `body` column. Other columns are optional.

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `rating` | integer 1–5 | ✅ | Rows outside 1–5 are skipped. |
| `body` | string | ✅ | Main review text. |
| `title` | string | | Optional review title. |
| `date` | ISO date | | e.g. `2026-01-05`. Unparseable dates are ignored. |
| `app_name` | string | | Source app. |
| `locale` | string | | e.g. `en-US`. |

JSON input can be either a top-level array of review objects or an object with a
`{"reviews": [...]}` array (see `examples/reviews.json`). `.jsonl` (one JSON
object per line) is also supported.

## Development

```bash
uv sync                # install deps (incl. dev tools)
uv run pytest          # run the test suite
uv run ruff check .    # lint
uv run mypy            # optional type check
```

The test suite uses a small deterministic hashing embedder, so **tests do not
download any model** and run offline.

## Project layout

```
src/feature_forge/
  cli.py              # Typer CLI (the `feature-forge analyze` command)
  analysis.py         # orchestration: summary + embed/cluster/score
  models.py           # Pydantic models (Review, ClusterResult, ...)
  loaders/            # csv_loader, json_loader
  pipeline/           # clean, embed, cluster, score
  report/             # markdown renderer
tests/                # pytest suite
examples/             # sample review datasets
```

## License

[MIT](LICENSE)
