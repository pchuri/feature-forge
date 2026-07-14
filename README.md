# Feature Forge

**Feature Forge helps founders decide what _not_ to build — using evidence from
real users.**

> Modern AI makes writing code easy; the hard part is deciding **what** to
> build. Feature Forge is a **product research engine — not an idea generator** —
> that helps founders answer *"What should I spend the next six months
> building?"* with evidence rather than intuition.
>
> **Evidence first, ideas second.** Never invent demand; every conclusion must
> cite user evidence. **Absence of evidence is also evidence.** Success is not
> finding ideas — it is **eliminating bad ideas before they are built**, and
> sometimes the right answer is *"do not build this."*
>
> 📖 [VISION](docs/VISION.md) · [PRINCIPLES](docs/PRINCIPLES.md) · [ROADMAP](docs/ROADMAP.md)

Feature Forge is a CLI tool for indie developers. Concretely, it helps you
answer a sharper question:

> *Is this product idea actually supported by real pain points that users are
> already complaining about?*

You point it at a file of existing app reviews (CSV or JSON), give it your idea,
and it produces a Markdown **opportunity report**: the dominant pain-point
clusters, how frequent and how negative each one is, representative quotes, and a
heuristic verdict on whether your idea is supported by the data.

> **Scope.** Feature Forge can analyze a **local file** *or* **fetch reviews
> straight from an app store** (Google Play / App Store) so you never have to
> build a CSV by hand. All analysis runs locally — **no paid LLM API is
> called.** Cluster summaries are extractive (top keywords + reviews closest to
> the cluster centroid + simple heuristic labels). LLM-based summarization can be
> layered on later.
>
> **App Store note.** App resolution (name → id) works, but Apple's public
> customer-reviews RSS endpoint currently returns **empty for all apps** — a
> known Apple-side limitation that affects every tool built on it, including the
> popular scraping libraries. Google Play fetching is fully functional today; the
> App Store fetcher will return data automatically if/when Apple restores the
> feed. For App Store analysis in the meantime, supply a saved file.

## How it works

```
reviews.csv ──► load ──► clean ──► embed ──► cluster ──► score ──► report.md
                          │          │          │           │
                    drop empty,  sentence-   KMeans     frequency,
                    short, dupes transformers (k=10)    avg rating,
                                                        negative ratio,
                                                        opportunity score
```

1. **Load** reviews from a CSV/JSON file **or fetch** them from a store
   (Google Play via `google-play-scraper`; App Store via Apple's iTunes Search
   API + reviews feed).
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

## Analyze a real app (no CSV needed)

Point Feature Forge at an app by **name** — it resolves the store id, downloads
reviews, and analyzes them in one step. You never touch a CSV:

```bash
uv run feature-forge analyze \
  --store google-play \
  --app "WhatsApp" \
  --reviews 500 \
  --idea "A privacy-first messaging app" \
  --save whatsapp_reviews.csv   # optional: keep the raw reviews
```

You can also pass an explicit store id instead of a name (e.g.
`--app com.whatsapp` for Google Play, `--app 310633997` for the App Store).

To only download reviews (no analysis), use `fetch`:

```bash
uv run feature-forge fetch google-play "WhatsApp" --count 500 --output reviews.csv
```

### CLI

**`analyze`** — build an opportunity report from a file or a store:

```
feature-forge analyze [REVIEWS] --idea "<idea>" [--store <store> --app <name|id>] [options]
```

| Option | Alias | Default | Description |
| --- | --- | --- | --- |
| `REVIEWS` | | — | Path to a `.csv`/`.json`/`.jsonl` file. Omit when using `--store`. |
| `--idea` | `-i` | — | The product idea to validate (required). |
| `--store` | `-s` | — | `google-play` or `app-store` — fetch instead of reading a file. |
| `--app` | | — | App name (auto-searched) or store id. Required with `--store`. |
| `--reviews` | `-n` | `500` | Max reviews to fetch. |
| `--country` | | `us` | Store country/locale code. |
| `--save` | | — | Also save the fetched raw reviews to this `.csv`/`.json`. |
| `--output` | `-o` | `report.md` | Where to write the Markdown report. |
| `--clusters` | `-k` | `10` | Number of KMeans clusters to request. |

Provide **either** a `REVIEWS` file **or** `--store`/`--app`, not both.

**`fetch`** — download reviews to a file (no analysis):

```
feature-forge fetch <store> <APP> [--count 500] [--country us] [--output reviews.csv]
```

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
  cli.py              # Typer CLI (the `analyze` and `fetch` commands)
  analysis.py         # orchestration: summary + embed/cluster/score
  models.py           # Pydantic models (Review, ClusterResult, ...)
  export.py           # save reviews back to CSV/JSON (--save / fetch)
  loaders/            # csv_loader, json_loader (file input)
  fetchers/           # google_play, apple_app_store (store input) + name search
  pipeline/           # clean, embed, cluster, score
  report/             # markdown renderer
tests/                # pytest suite
examples/             # sample review datasets
```

## License

[MIT](LICENSE)
