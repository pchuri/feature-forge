# Roadmap — Where Feature Forge is going

This document describes direction, not dates. It exists so that any new
contributor — human or AI — can understand the long-term ambition in one read.

## Today

Feature Forge analyzes app-store reviews and produces a Markdown opportunity
report. It:

- fetches reviews from **Google Play** (fully functional) and **App Store**
  (resolution works; Apple's public reviews feed currently returns empty), or
  reads a local file;
- clusters pain points and scores them deterministically;
- runs entirely locally, with **no paid LLM API call**.

This is the seed. The engine is deliberately narrow so its evidence is
trustworthy. Reviews are simply the **first evidence source** — not the identity
of the project. As [VISION.md](VISION.md) puts it, Feature Forge is a product
research engine, not a review analyzer; review analysis is where that engine
starts, not where it ends.

## Expanding the evidence base

The quality of any decision is bounded by the breadth of evidence behind it.
Feature Forge should eventually understand what people actually struggle with
across many sources:

- App Store
- Google Play
- Reddit
- GitHub Issues
- Hacker News
- Amazon Reviews
- Product Hunt
- Forums
- Support tickets
- YouTube comments

Each new source is only worth adding if it improves the **quality of evidence**
(see [PRINCIPLES.md](PRINCIPLES.md)) — not merely to grow the list.

## From evidence to decisions

As sources broaden, the work shifts from *collecting* signal to *cross-checking*
it: corroborating a pain point across sources, detecting negative space
(features nobody asks for), and quantifying confidence. The deterministic engine
produces this; the AI agent interprets it.

## The long-term ambition

> Feature Forge should eventually become **the Bloomberg Terminal for product
> opportunities** — the place founders go to decide, with evidence, what is
> worth building and what is not.

The measure of progress is never how many ideas we surface. It is how reliably
we help founders **avoid building the wrong thing.**

See also: [VISION.md](VISION.md) · [PRINCIPLES.md](PRINCIPLES.md)
