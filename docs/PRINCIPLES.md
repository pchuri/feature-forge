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
