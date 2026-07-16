# Reddit Research Protocol — manual, pre-crawler

How Feature Forge uses Reddit **today, by hand**, before any crawler or API
integration exists. This protocol was derived from a real cross-channel
study (three utility markets checked against their Play-review verdicts) and
is binding until a Reddit fetcher is designed deliberately — do not shortcut
it with ad-hoc scraping. Illustrative examples below are anonymized; per
[PUBLICATION_POLICY.md](PUBLICATION_POLICY.md), concrete market studies live
in the private research archive, not in this repository.

```
Play reviews tell you what broke.
Reddit tells you who it happened to,
what they were trying to do,
and what they did instead of installing your app.
```

## 1. Why Reddit matters

Play reviews are written by people who already installed an app. Reddit
threads are written by people **in the middle of the job** — asking how to
do something, venting about a workflow, or recommending tools to each other.
That population includes the most valuable segment review mining can never
reach: people who solved the problem with a workaround and never installed
anything. A market can look healthy in Play data and still be full of
unserved demand visible only where users talk to each other.

## 2. What Reddit reveals that Play reviews do not

| Signal | Anonymized example (from a real study) |
| --- | --- |
| **Personas** | Play showed anonymous complaints about a file-viewer category; Reddit showed the dominant persona was a specific hobbyist community, plus a small-business *seller* sub-persona no review hinted at |
| **Jobs-to-be-done, one level deeper** | Those users didn't need "view the file" — they needed "predict why a downstream tool mangles it." No Play review articulated that |
| **Workflows & workarounds (non-consumption)** | A nine-step screenshot pipeline run "hundreds of times"; convert-to-another-format-just-to-view. None of these people write Play reviews |
| **Community trust norms** | A FOSS/offline credibility bar for privacy tools; distrust of "free utility" apps after bundled-adware incidents |
| **Common-knowledge context** | "The platforms already handle this on upload" — community knowledge that caps casual urgency in ways Play data can't show |
| **Segment-level willingness to pay** | Play showed purchase quotes in a category; Reddit showed one community within it would never pay — two populations, one market |

And the inverse — what Play gives that Reddit cannot: **volume** (hundreds
of datable reviews per app), **app-level breakage attribution**, **star
trends over time**, and **monetization evidence tied to actual products**.

## 3. When to use Reddit

- **After** a market passes the Play-review gate and **before** a BUILD is
  acted on — as the persona/job/workflow check on a verdict (due diligence
  first, Reddit cross-check second).
- When Play clusters show *what* fails but not *who* is failing or *why*
  they wanted it (anonymous demand).
- When monetization strategy depends on knowing **which segment pays**.
- When positioning/marketing copy is being written — Reddit supplies the
  users' own vocabulary and the channels they actually read.
- When a category is suspiciously healthy on Play and you need to know
  whether the pain moved somewhere else (desktop, pipelines, enterprise)
  rather than disappeared.

## 4. When not to use Reddit

- **Not as the primary screen.** Verdicts start from Play-review evidence;
  Reddit cannot supply frequency, star trends, or per-app breakage at
  volume, and thread-sample sizes are tiny (~10 threads).
- **Not for demand sizing.** Upvotes and thread counts are not installs.
- **Not to rescue a market that failed the Play gate.** A handful of
  enthusiastic threads is exactly the anecdotal "great idea!" signal
  Feature Forge exists to resist.
- **Not for monetization proof.** Reddit skews FOSS/technical and
  systematically *understates* willingness to pay (and occasionally
  overstates niche enthusiasm). Payment evidence comes from Play (§9).
- **Not at scale, not automated** — see §5.

## 5. Ethical constraints (binding)

1. **Do not scrape at scale.** Manual, single-URL reads only; ~10 threads
   per market is the working ceiling. No scripts, no bulk downloads, no
   crawler until one is deliberately designed and reviewed.
2. **Do not store usernames or any personal data.** Attribute views only as
   "a user in r/<subreddit>". Never retain profile links, post histories,
   or anything that identifies a person. Be extra careful with threads from
   vulnerable users (e.g. privacy threads from hostile jurisdictions) —
   summarize the *need*, never the person.
3. **Summarize and cite.** Store paraphrases plus the thread URL. Quote at
   most 1–2 short verbatim fragments per thread. Do not archive full
   thread bodies in the repo.
4. **Do not train on Reddit content.** Collected material is used for
   human/analyst reading and citation only.
5. **Respect the walls.** reddit.com and its mirrors block non-browser
   fetchers; do not circumvent beyond ordinary browsing (the PullPush
   public archive for single-URL reads is the accepted path today). If a
   source blocks you, that is an answer, not an obstacle to engineer around.

## 6. Manual research workflow

1. **Frame the question** from existing Play evidence: which persona, job,
   or monetization assumption needs testing? Write it down first.
2. **Search** (browser/web-search only) with 4–6 query variants:
   `reddit <market> <pain phrase>`, subreddit-targeted phrasing, app names
   from the Play incumbent set, and the suspected persona's vocabulary
   (the hobbyist community's term for the job, not the app-category name).
   Note: `site:reddit.com` operators may return nothing in some search
   tools; plain `reddit <terms>` works better.
3. **Select threads** against the criteria in §7; cap at ~10 per market.
4. **Read** each thread once, via browser or a single-URL archive read.
   Record: URL, subreddit, approximate date, one-line topic, paraphrased
   pain points / workflows / feature requests / tool mentions, and at most
   1–2 short quotes.
5. **Grade** every claim with an evidence level from §8.
6. **Compare** against the Play findings per §9 — agreements, divergences,
   and Reddit-only findings.
7. **Write up** using the template in §10, into the **private** research
   archive (`research/` is gitignored — see
   [PUBLICATION_POLICY.md](PUBLICATION_POLICY.md)), with the compliance
   block filled in.

## 7. Thread selection criteria

Prefer threads that are:

- **Job-centric, not app-centric** — someone trying to accomplish something
  ("how do I…", "why does my file…") over app-recommendation listicles.
- **Recent** (≤3 years) for workflow claims; older threads are acceptable
  for durable structural facts (e.g. "the OS gallery app can't render this
  format at all") and should be flagged as dated.
- **Answered** — threads with substantive comment discussion outrank
  unanswered asks; but note that *unanswered/dismissed asks are themselves
  evidence* of an unserved need (record them as such).
- **From the persona's home subreddit** (the hobby, profession, or
  community sub) over generic help subs — the vocabulary and norms are the
  data.
- **Independent of each other** — ten threads from one subreddit is one
  data point about one community; spread across communities.

Skip: promotional/self-posted app threads, low-effort memes, and anything
whose main content is personal circumstances rather than the workflow.

## 8. Evidence quality levels

Grade every Reddit-derived claim; carry the grade into the write-up.

| Level | Definition | Standing |
| --- | --- | --- |
| **R1 — Read thread** | Full thread (post + comments) read directly | Citable as evidence alongside Play clusters |
| **R2 — Partial read** | Post read but comments unavailable (archive gaps) | Citable, flag the gap |
| **R3 — Snippet only** | Search-result snippet; thread not opened | **Lower-confidence**: directional only, must be labeled, never load-bearing for a verdict |
| **R4 — Secondary source** | Blog/roundup *about* Reddit sentiment | Context only; never citable as user evidence |

A verdict-relevant claim needs R1/R2 support or agreement with Play data.
An entire section built on R3 must say so at the top of that section.

## 9. How to compare Reddit evidence against Play review evidence

```
Play validates: app breakage, frequency, star trends, monetization.
Reddit validates: personas, jobs-to-be-done, workflows, non-consumption.
Neither replaces the other.
```

Work through four buckets, in order:

1. **Agreements** — a pain/feature appearing independently in both channels.
   This is the strongest evidence Feature Forge has; raise confidence and
   let it anchor the MVP.
2. **Reddit-only findings** — personas, deeper jobs, workarounds. These
   *extend* a verdict (positioning, roadmap, marketing) but do not by
   themselves create or reverse one.
3. **Play-only findings** — breakage volume, purchase quotes. These remain
   the backbone of the verdict.
4. **Divergences** — treat as a **finding to explain, not an error to
   resolve away**. Ask "which population does each channel sample?" first;
   most divergences are segmentation (one channel's community doesn't pay;
   the other channel's pragmatists do — same market, two populations). A
   divergence you cannot explain is an open risk: record it in the report's
   counter-evidence section.

Monetization tie-break: when the channels disagree on willingness to pay,
**Play wins** (real purchases beat stated culture), but Reddit tells you
*who not to market to*.

### A worked example (real study, market masked)

This happened, in a market this protocol was tested on:

```
Google Play revealed one kind of evidence:
  purchase quotes across four incumbent apps — people in this
  category demonstrably pay.

Reddit revealed a different kind of evidence:
  the category's most vocal community defaults to free
  open-source tools and stated it would never pay.

Those findings disagreed.

That disagreement became a research result:
  two populations, one market. The verdict survived, but the
  pricing plan and the marketing plan changed — price for the
  pragmatists, don't pitch the purists.
```

Neither channel was wrong. Treating the disagreement as an error would have
meant discarding one true fact to keep another; treating it as a finding
produced the segmentation that neither channel could see alone.

## 10. Output template

```markdown
# NN — <Market> — Reddit cross-check

*Question under test (from Play evidence): <one sentence>*

**Compliance & method.** Browser search + single-URL reads only
(<N> threads); no scraping at scale; no usernames or personal data
recorded; paraphrase + max 1–2 short quotes per thread; thread URLs
cited for every claim. Access notes: <what worked / was blocked>.
Evidence levels per §8 noted inline; sections resting on R3
(snippet-only) are flagged as lower-confidence.

## Threads
| URL | Subreddit | ~Date | Topic | Level |

## Recurring pain points
- <paraphrase> (urls) [R1]

## Workflow complaints / workarounds
## Feature requests
## Personas
## Comparison vs Play evidence
| Play said | Reddit adds / corrects |
### Agreements (confidence ↑)
### Reddit-only findings
### Divergences (findings, not errors)

## Net effect on verdict
<intact / sharpened / weakened — and precisely what changed>
```

See also: [PRINCIPLES.md](PRINCIPLES.md) (Cross-channel evidence) ·
[PUBLICATION_POLICY.md](PUBLICATION_POLICY.md) (why concrete studies stay in
the private research archive).
