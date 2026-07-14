# Vision — Why Feature Forge exists

Modern AI makes software development dramatically easier. The bottleneck is no
longer writing code. **The bottleneck is deciding _what_ to build.**

Most indie developers fail because they build products nobody wants. Feature
Forge exists to solve that problem.

It is **not** a review analyzer. It is **not** an LLM wrapper. It is a **product
research engine** — built to help founders answer one question with evidence
rather than intuition:

> **"What should I spend the next six months building?"**

## The core workflow

Feature Forge sits inside a larger decision loop. Its job is to manufacture the
one ingredient that loop cannot fake: **evidence.**

```
Idea
  ↓
Market
  ↓
Competitors
  ↓
User Reviews
  ↓
Evidence          ← Feature Forge is the engine that produces this
  ↓
Market Research
  ↓
Investment Decision
  ↓
Product
```

The shape of the project has changed as it matured. It started as a narrow
pipeline:

```
Review → Cluster → LLM
```

It is now a decision framework:

```
Market → Evidence → Research → Decision
```

That shift is the heart of the project.

## Separation of responsibilities

Feature Forge itself should stay **deterministic**. It collects evidence. An AI
agent, layered on top, *interprets* that evidence. These responsibilities must
not be merged.

- **Feature Forge** — reproducible, auditable, evidence-producing.
- **The AI agent** — judgment, synthesis, interpretation.

Keeping the engine deterministic is what lets every conclusion be traced back to
its source.

## The ultimate goal

The final goal is **not** "generate startup ideas." The final goal is **"help
founders make better investment decisions."**

Sometimes the correct answer is **"do not build this."** That is success.

Success is not finding ideas. Success is **eliminating bad ideas before they are
built.**

## A note to contributors

Whenever you make an architectural decision, optimize for **better product
research**, not better software engineering. Always ask:

> *"Does this help founders make better decisions?"*

If not, it probably does not belong in Feature Forge.

See also: [PRINCIPLES.md](PRINCIPLES.md) · [ROADMAP.md](ROADMAP.md)
