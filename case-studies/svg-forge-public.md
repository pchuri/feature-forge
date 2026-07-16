# Case Study — How Feature Forge picked its first product

*A real product-selection run, published at the level
[PUBLICATION_POLICY.md](../docs/PUBLICATION_POLICY.md) allows: the
**methodology and its numbers are real; the market, the incumbent apps, and
user quotes are masked.** The product that came out of this run — svg-forge —
is in closed beta; the detailed scans that selected it (and rejected 40+
other markets) stay in the private research archive.*

```
Market X
   ↓
Evidence
   ↓
Decision
   ↓
Outcome
```

## The question

A solo developer has a few weeks to a few months. **What should they build —
and, more importantly, what should they refuse to build?**

## Step 1 — Reject at scale

Feature Forge scanned **20 broad horizontal markets** (the "obvious ideas":
note apps, password managers, screen recorders…). Every one was rejected —
median opportunity score 13.5/100, dominated by billion-install incumbents.
Then it scanned **20 deliberately small, technical niches**. Even in a set
hand-picked to elicit a *yes*, the engine returned **zero BUILD verdicts**
under its strict gate. The screen refused to rubber-stamp.

That refusal is the product working as designed: *false positives are worse
than false negatives.*

## Step 2 — Evidence for Market X

One niche — **Market X, a small file-format utility category** — kept
ranking first. The five-factor evidence (all derived from ~270–350 cleaned
store reviews of the incumbent set, deterministically clustered):

| Factor | Score | What the evidence showed |
| --- | ---: | --- |
| Pain severity | 69 | top cluster **95% negative**, "does not work"-class complaints |
| Incumbent weakness | 80 | incumbent set averaged **~3.0★**, the weakest at **1.6★** — and users were *paying* for a premium tier that didn't work |
| Distribution advantage | 100 | no mega-brand present; largest incumbent under 300k installs |
| Ease of build | 80 | pure view/convert utility — OS-supported rendering, no ML, no cloud |
| Demand | 30 | **the one weak factor:** a genuinely small pond (~10⁵-install median) |

## Step 3 — Decision

Under the default VC-scale demand gate: **WATCH** (4/5 gates). The engine
would not call it a BUILD, and said exactly why: everything is right except
the pond is small.

The decision then became a *human* one with the trade-off made explicit:
relax only the demand gate to a solo-developer bar (documented, not
silently), and Market X flips to **BUILD (5/5)** — with the verdict caveated
in writing: *timebox it to weeks, not months; expect utility-scale returns,
not startup-scale.* A follow-up deep-diligence pass (15 apps, ~3,800
reviews) confirmed the verdict and defined the MVP purely from evidence:
fix the two failure clusters users actually complain about, and refuse the
features no review asks for (*negative space is evidence*).

## Step 4 — Outcome: what happened next

```
Research  →  Repository  →  Release Candidate
```

The verdict did not stay a document. It became a product:

- The product (**svg-forge**) was built inside the recommended timebox and
  is **in closed beta** — research to release candidate, on the schedule
  the evidence prescribed.
- The same pipeline that said *yes* once said **no** to 40+ other markets
  before and after — including several that looked attractive until the
  evidence was read (one candidate's "huge" market turned out to be a
  keyword collision with an unrelated 270M-install game; another's
  headline pain was measured, then traced to an OS restriction no app can
  fix).
- A later cross-channel study (store reviews vs community discussions)
  found the persona and the deeper job the reviews had never articulated —
  which now shapes the roadmap.

*This document will be updated after release with what actually happened —
the same evidence standard applies to our own product.*

## Lessons — what surprised us

- **The market was smaller than expected.** The evidence said so up front;
  believing it (and timeboxing accordingly) was the discipline.
- **Reliability mattered more than features.** Every dominant pain cluster
  was "it doesn't work" — not "it lacks X."
- **The MVP became smaller after reading the evidence, not bigger.** Most
  research inflates scope; cited evidence shrank it to two failure
  clusters worth fixing.
- **The biggest value was deciding what NOT to build** — 40+ rejections,
  each one a saved six months.

## What this case demonstrates

1. **Reject by default works.** One BUILD out of 40+ scanned markets, each
   rejection cited to evidence.
2. **Gates should fail loudly, not silently.** The demand gate was relaxed
   *explicitly, once, in writing* — the engine never pretended the pond was
   bigger than it was.
3. **Evidence defines the MVP, not just the verdict.** What to build — and
   what to leave out — came from the same clusters that justified building
   at all.

---

**Every product begins with evidence.**

*See the [README](../README.md) to run your own investigation — everything
in this repo (the engine, the scoring, the protocols) is what produced this
case.*
