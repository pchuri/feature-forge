# Publication Policy — what belongs in the public repo

Feature Forge is open source. The **methodology** is public; the **findings**
are not. This repo publishes the engine, the docs, and synthetic examples —
never the market research it produced or the product decisions built on it.

```
Publish the telescope.
Keep the star charts.
```

## Why the boundary exists

Feature Forge's output is product-selection research: which markets are
broken, which incumbents are weak, what an MVP should be, what users will
pay. Publishing those reports would (a) hand the analysis to anyone building
in the same niches, (b) expose real user quotes beyond the small-scale,
summarize-and-cite terms they were collected under, and (c) reveal the
maintainer's product strategy while the products are in flight. None of that
improves the quality of evidence, research, or decision-making for
contributors — the contributor's test in [PRINCIPLES.md](PRINCIPLES.md) —
so it stays out.

## Public — belongs in this repository

| Category | Examples |
| --- | --- |
| Source code | `src/`, `tests/`, CI config |
| Project docs | README, CONTRIBUTING, VISION, PRINCIPLES, ROADMAP |
| Methodology docs | REDDIT_RESEARCH_PROTOCOL, this policy |
| Generic examples | `examples/` — **synthetic** review datasets (invented app names, invented reviews) |
| Anonymized/sample reports | Reports generated from the synthetic examples, or real-structure reports with markets, apps, and quotes replaced by placeholders |
| **Case studies** | `case-studies/` — market-masked walkthroughs of real runs (**Market X → Evidence → Decision → Result**) |

### Case studies are public by design

The first question every open-source visitor asks is *"has anyone actually
used this?"* — case studies are the project's strongest credibility asset,
so they must **not** default to private. The rules that make them safe:

- The **methodology, scores, and decision path are real** and published.
- The **market name, incumbent apps, and user quotes are masked**
  ("Market X", "a file-format utility niche").
- A case study is published only **after** the decision is no longer
  strategically sensitive (the product has shipped or been announced).
  A shipped product's *name* may appear — the product is public by
  definition — but the scan details stay at Market-X altitude, and the
  scans of *other* (unshipped) markets stay fully private.

## Private — must never be committed

| Category | Where it lives instead |
| --- | --- |
| `research/` — real market scans, product-selection reports, due-diligence docs | local only (gitignored) |
| `scratchpad/` — analyst harness scripts, fetched datasets, intermediate JSON | session scratchpad / local (gitignored) |
| `products/`, `private/` — anything about apps being built: execution plans, positioning, roadmaps | local only (gitignored) |
| Selected-product decisions & app-specific execution plans | private research archive (until eligible for a masked case study, above) |
| Revenue assumptions, pricing plans, monetization strategy for specific products | private research archive |
| Fetched real review datasets (`*.csv`, `*.jsonl` outside `examples/`) | regenerate on demand; do not commit |
| Credentials of any kind: API keys, tokens, cookies, `.env` files | never in the repo, tracked or not |
| Play Console data, private tester names/emails, any personal data | never collected into the repo at all |

## Enforcement

1. **`.gitignore`** blocks the private directories (`research/`,
   `scratchpad/`, `products/`, `private/`), `.env*`, and fetched datasets
   (`*.csv` / `*.jsonl`, with `examples/` explicitly re-included for
   synthetic samples).
2. **Docs may cite the method, not the findings.** Public docs (e.g. the
   Reddit protocol) may say *how* a study was done and use **anonymized**
   illustrations ("a file-viewer niche", "a hobbyist community") — never
   named markets, named incumbents, verdicts, or strategy derived from
   private scans. If a doc needs a concrete example, use the synthetic
   `examples/` dataset.
3. **Before committing, ask three questions:** Does this reveal *which
   market* was studied? Does it reveal *what was decided*? Does it contain
   *data about real people or real fetched reviews*? Any "yes" → private.
4. **Audit on release:** `git ls-files` review + secret/PII grep before
   tagging. History matters too — a private file committed once must be
   treated as published; prevention (this policy) is the real control.
5. **Deletions need a human.** If an audit finds something that shouldn't be
   public, flag it and decide the remediation (redact vs history rewrite)
   explicitly — never silently delete.

## Litmus tests

- *"Would this help a stranger validate **their own** idea?"* → public.
- *"Would this help a stranger clone **our** next app?"* → private.
- *"Is this a real user's words or data?"* → private unless it is already an
  anonymized, small-scale, cited summary — and even then, only in the
  private archive.

See also: [PRINCIPLES.md](PRINCIPLES.md) ·
[REDDIT_RESEARCH_PROTOCOL.md](REDDIT_RESEARCH_PROTOCOL.md)
