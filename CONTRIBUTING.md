# Contributing to Feature Forge

Thank you for considering a contribution. Feature Forge is an open-source
project, and we want every contributor — human or AI coding agent — to act as a
**contributor who understands the vision**, not just someone changing code.

## Read these first

Before writing any code, read the three documents that define this project:

1. [docs/VISION.md](docs/VISION.md) — **why** the project exists.
2. [docs/PRINCIPLES.md](docs/PRINCIPLES.md) — the **philosophy** we judge by.
3. [docs/ROADMAP.md](docs/ROADMAP.md) — **where** the project is going.

These three documents are, over time, likely to be more valuable assets than the
code itself.

## The contributor's test

> Before implementing a new feature, ask whether it improves the quality of
> evidence, the quality of research, or the quality of decision-making. If it
> improves none of these, it probably does not belong in Feature Forge.

And when you make an architectural decision, optimize for **better product
research, not better software engineering.** Always ask: *"Does this help
founders make better decisions?"*

## Development setup

Feature Forge uses [uv](https://docs.astral.sh/uv/):

```bash
uv sync                # install deps (incl. dev tools)
uv run pytest          # run the test suite
uv run ruff check .    # lint
uv run mypy            # optional type check
```

The test suite uses a small deterministic hashing embedder, so tests do not
download any model and run offline.

## Keep the engine deterministic

Feature Forge collects evidence; it does not interpret it. The engine must stay
**reproducible and auditable** — interpretation belongs to the AI agent layered
on top. Please do not merge these responsibilities in a single change.
