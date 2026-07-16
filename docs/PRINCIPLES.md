# Principles — How Feature Forge judges

These are the rules Feature Forge reasons by. They are more important than any
single feature, and they take precedence when a design decision is unclear.

## Evidence first

```
Evidence first.
Ideas second.

Never invent demand.
Never recommend products without evidence.
Every conclusion must cite user evidence.
```

An idea with no supporting evidence is not a weak opportunity — it is a
non-opportunity. Feature Forge does not manufacture demand to make a report look
useful.

## Reject by default

```
Find opportunity → Reject markets.
```

Feature Forge behaves like a venture capitalist: it says **no** to almost
everything. A VC rejects ~99% of what they see, and a good screen is judged by
the bad bets it avoids, not the deals it finds. The default verdict is
**AVOID** — a market must *earn* a BUILD.

**False positives are worse than false negatives.** Missing a good market costs
a founder nothing they can see. Recommending a bad market costs them six months.
When in doubt, reject. Every AI tool is happy to say *"great idea!"*; Feature
Forge's value is that it will say *"do not build this."*

## Every opportunity must be scored on eight dimensions

An opportunity is only real if it can be evaluated across all of these:

| Dimension            | Question it answers                                  |
| -------------------- | ---------------------------------------------------- |
| **Evidence**         | Is there real user data behind this?                 |
| **Frequency**        | How often does this pain appear?                     |
| **Severity**         | How badly does it hurt the people who feel it?       |
| **Market Size**      | How many people are affected?                        |
| **Competition**      | Who already solves this, and how well?               |
| **Ease of Build**    | Can a small team ship a credible version?            |
| **Revenue Potential**| Will anyone pay to make the pain stop?               |
| **Confidence**       | How much should we trust the answer above?           |

A high score on one dimension never excuses a missing one.

## Broken markets over big markets

```
Big market → usually No.
Small, technically broken market → often Yes.
```

A large market is not an opportunity; it is a crowd of competitors. The best
opportunities are **small, technically broken markets** — narrow niches where
users feel real, specific, unaddressed pain (think obscure file formats, viewers,
converters, one-off developer tooling). Market Size is one dimension of eight,
not the goal. Feature Forge should be *more* interested in a tiny market full of
angry users than a huge market full of satisfied ones.

## Negative space is evidence

```
Absence of evidence is also evidence.
If users never ask for a feature,
that itself is an important finding.
```

This is Feature Forge's biggest differentiator. Most tools only report what is
loudly present in the data. Feature Forge treats **what users never complain
about, never request, and never mention** as a first-class signal. Silence
about a "hot" idea is often the most valuable thing the research can tell you.

## Cross-channel evidence

```
Play reviews tell you what broke.
Reddit tells you who, why, and what they did instead.
Different questions — never substitutes.
```

Store reviews and community discussions answer **different questions**. Play
reviews validate app breakage, frequency, and monetization — at volume, from
people who installed something. Reddit validates personas, jobs-to-be-done,
workflows, and *non-consumption* — the people who never installed anything.

The **strongest evidence Feature Forge can produce is agreement across both
channels**: a pain that shows up independently in review clusters and in
community threads deserves more confidence than either source alone.

**Divergence between channels is a finding, not an error.** When Play says
"users pay" and Reddit says "users never would," the usual explanation is
that the two channels sample different populations of the same market —
that segmentation is itself a research result. Explain a divergence before
acting on either side of it; an unexplained divergence is recorded as an
open risk. (Manual method: [REDDIT_RESEARCH_PROTOCOL.md](REDDIT_RESEARCH_PROTOCOL.md).)

## Determinism over cleverness

The engine that produces evidence must be **reproducible and auditable**. Given
the same inputs, it must produce the same evidence. Interpretation is the job of
the AI agent layered on top — not the engine. Do not blur that line for the sake
of a slicker output.

## The contributor's test

Before implementing a new feature, ask whether it improves:

1. the **quality of evidence**,
2. the **quality of research**, or
3. the **quality of decision-making**.

If it improves none of these, it probably does not belong in Feature Forge.

See also: [VISION.md](VISION.md) · [ROADMAP.md](ROADMAP.md)
