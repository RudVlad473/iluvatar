<div align="center">

# ✨ iluvatar

### Conceives the world before anything is built.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-5A67D8.svg)](https://github.com/RudVlad473/iluvatar)
[![Stars](https://img.shields.io/github/stars/RudVlad473/iluvatar?style=social)](https://github.com/RudVlad473/iluvatar)

</div>

---

Ask an AI agent to architect your app and it names a tech stack before
it's named the problem: Postgres, Redis, and a queue appear before
anyone's asked what happens when two writes race, or what the app does
when the network is down.

iluvatar is a Claude Code skill that forces the boring questions first.
Give it a one-sentence app idea and it runs a 15-point classification
pass (state, failure, concurrency, compliance, the stuff that gets
skipped) and emits `HIGH-LEVEL-ARCHITECTURE.md`: a frozen,
schema-validated contract that names archetypes and cross-cutting
concerns but never a single technology. No tool gets picked until the
shape is settled.

In Tolkien's legendarium, Ilúvatar conceives Middle-earth in thought,
complete, before the Ainur ever sing it into being. That's the whole
pitch: architecture before creation, not architecture as an afterthought
to "which framework."

## 📦 Install

**As a Claude Code plugin:**

```
/plugin marketplace add RudVlad473/iluvatar
/plugin install iluvatar@RudVlad473
```

**Or copy it directly.** Works anywhere, no plugin system required.
Requires Python 3.9+ on PATH (stdlib only, nothing to `pip install`).

```
git clone https://github.com/RudVlad473/iluvatar
cd iluvatar
mkdir -p ~/.claude/skills
cp -r skills/iluvatar ~/.claude/skills/          # available in every project
```

Or scoped to one project only:

```
git clone https://github.com/RudVlad473/iluvatar
cd iluvatar
mkdir -p /path/to/your/project/.claude/skills
cp -r skills/iluvatar /path/to/your/project/.claude/skills/
```

On Windows (PowerShell):

```
git clone https://github.com/RudVlad473/iluvatar
Set-Location iluvatar
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills"
Copy-Item -Recurse skills\iluvatar $HOME\.claude\skills\
```

Then just describe your app idea, or say "run iluvatar."

## 🤝 Pairs well with

iluvatar classifies whatever idea you hand it; it doesn't sharpen a
vague one first. Best served after Matt Pocock's
[`grill-with-docs`](https://github.com/mattpocock/skills): a relentless
interview that pressure-tests the idea and produces docs (ADRs, a
glossary) as it goes, so iluvatar has something more complete to
classify by the time it runs.

```
/plugin marketplace add mattpocock/skills
/plugin install mattpocock-skills@mattpocock
```

## 🧪 Example

**You say:**

> Paste a URL, get a clean readable version saved for later, with a
> weekly email digest of what I haven't read yet. I want to self-host it
> on one small server. No browser extension or mobile app for now.

**iluvatar returns** `HIGH-LEVEL-ARCHITECTURE.md`, classifying it as
`etl-pipeline` + `crud-service` + `background-jobs`, deriving a 10-stage
flow spine across write, read, and scheduled paths, and running real
numbers instead of adjectives. Every number is tagged with where it came
from (a script run, something the user stated, or an explicit
assumption), so nothing in the document reads as more certain than it
is.

<details>
<summary><b>Full <code>HIGH-LEVEL-ARCHITECTURE.md</code> output, verbatim</b></summary>

````markdown
---
archetypes: [etl-pipeline, crud-service, background-jobs]
primary_artifact: a saved article (URL in, extracted text stored)
budget_notes: "~7 saves/day, ~639MB total storage over a 5-year retention
  window (botec.py), single self-hosted server — throughput is not the
  constrained resource here, storage retention and per-fetch latency are"
---
# Classification

**etl-pipeline** — a URL goes in, gets fetched, extracted to readable
text, and lands in storage; that is an extract-transform-load chain even
though each run is one record, not a batch.

**crud-service** — saved articles are listed, read, and marked read; a
conventional create/read/update surface sits on top of the pipeline's
output.

**background-jobs** — the weekly digest email runs on a schedule,
independent of any single user request.

# Flow Spine

Write path:
1. submit-url — user-entered URL → validated, canonicalized URL
2. fetch — canonicalized URL → raw HTML (or a recorded fetch failure)
3. extract — raw HTML → title + readable text + metadata
4. store — extracted article → persisted record (id, url, title, text,
   fetched_at, read_at=null, status)
5. retry-or-quarantine — a failed fetch/extract is retried; after 3
   failures the record is marked `quarantined` instead of retried again
   (archetype-derived: etl-pipeline → poison-message handling)

Read path:
6. list-unread — query the store → paginated list of unread articles
   (archetype-derived: crud-service → pagination)
7. render-article — a stored record → the rendered reading view
8. mark-read — user action on a rendered article → `read_at` set

Scheduled path (independent of both above):
9. digest-compile — weekly trigger + store query (unread, not yet
   digested) → digest content
10. digest-send — digest content → email sent, `last_digested_at`
    watermark advanced (archetype-derived: background-jobs → schedule
    step the spine has no other stage for)

# Cross-cutting

**Runtime**
- State: article records and their `read_at`/`status` live in the store;
  the digest job's `last_digested_at` watermark is state too, and losing
  it would re-send old digests.
- Boundaries: only `fetch` (stage 2) talks to the open internet; the
  store is never reachable from outside the service.
- Movement: `fetch`→`store` (stages 2-4) is synchronous within the
  submit request; the digest (stages 9-10) is deferred, run weekly.
- Identity: an article is keyed by its canonicalized URL (tracking
  parameters stripped) — this is what makes stage 1's idempotency check
  possible; the same URL submitted twice must not create two records.
- Concurrency: two submits of the same URL racing is resolved by
  identity's uniqueness constraint at the store, not by locking earlier.
- Failure: a fetch or extract failure is recorded on the record with a
  status and retry count (stage 5); quarantined records are excluded
  from the digest so a permanently-broken URL doesn't repeat weekly.
- Observability: `fetch` logs duration and outcome per submission; the
  digest job logs how many articles it included.
- Verification: extraction logic is unit-tested against fixture HTML
  pages (that layer is fully covered); the digest job is
  integration-tested against a seeded store (schedule-triggering and
  email delivery are exercised, real delivery is not). Neither layer
  covers actual internet fetch reliability against live sites — that is
  deliberately left to the retry/quarantine path (stage 5) rather than
  to tests, since a test can't make the open internet reliable.
- Budget: extraction must complete within 10s per URL (a foreground
  request); the digest job processes well under 10k rows weekly with no
  real-time constraint. Sustainability: no separate energy/carbon driver
  — the single small server is already sized to ~7 saves/day, well under
  any threshold where scheduling or data-placement would matter.
- Delivery: one deployable service plus one scheduled job, both running
  from a single container on the user's own server.

**Dev-process**
- Change over time: the article record's schema and the digest email
  template are versioned independently, so a template change never
  forces a data migration.

**5C catch-all:** none beyond 5A/5B.

# Deferred

- Multi-user auth — no second user exists yet to impose a constraint;
  reopens when a second user is invited.
- Full-text search across saved articles — reopens once the list is too
  long to scroll usefully, assumed around 500+ stored articles.
- Interaction — single self-hosted user, one locale, no accessibility
  requirement stated; reopens if the tool gains other users or a
  public-facing UI.
- Compliance & Data Governance — no regulatory regime applies; the only
  data is the user's own reading history, on their own server, never
  processed by a third party; reopens if the tool is offered to other
  users or hosted data leaves the user's own infrastructure.

# Known Constraints

- "I want to self-host it on one small server." (user-imposed —
  rules out a managed multi-service architecture.)
- "Weekly email digest," not daily or real-time. (user-imposed.)

# Out of Scope

- Browser extension (explicitly excluded by the user).
- Mobile app (explicitly excluded by the user).
- Full-text search (excluded for v1; see Deferred for its reopening
  trigger).

# Open Questions

- Is ~7 saves/day representative, or a rough guess? (assumed from "a
  handful a day" in the scoping conversation; confirm before treating
  the storage estimate below as load-bearing.)
- Is a 10s extraction budget acceptable for slow source sites, or should
  slow fetches be backgrounded instead of blocking the submit request?
  (assumed, not stated by the user.)
- Is 3 failed attempts the right threshold before a URL is quarantined,
  or should it be tunable? (assumed a reasonable default; not stated by
  the user.)

# Provenance

- `budget_notes` "~7 saves/day" — `assumption` (Open Questions, item 1).
- `budget_notes` "~639MB total storage over 5 years" —
  `botec.py --dau 1 --actions 7 --peak 2 --obj-bytes 50000 --media-frac 1.0 --retention-days 1825 --server-qps 1000 --json`
  → `storage_total_bytes: 638750000` (`storage_total: "638.8MB"`,
  `storage_per_day: "350.0KB"`, `servers_needed: 0` — confirming
  throughput was never the constrained resource at this scale).
- `budget_notes` "single self-hosted server" — `user-stated`.
- Cross-cutting → Budget "extraction must complete within 10s per URL" —
  `assumption` (Open Questions, item 2).
- Cross-cutting → Budget "the digest job processes well under 10k rows
  weekly" — derived from the same `botec.py` run above (~7 saves/day × 7
  days ≈ 49/week), not an independently re-run figure.
- Flow Spine stage 5 "after 3 failures the record is marked quarantined"
  — `assumption` (Open Questions, item 3).
- Known Constraints (both entries) — `user-stated`, taken verbatim from
  the scoping conversation.

# How to Verify

Reproduce the one script-derived figure directly. `<iluvatar>` is this
skill's own resolved directory — substitute it for wherever it actually
lives, the same convention SKILL.md's Phase 6b uses:

```bash
python <iluvatar>/references/vendor/back-of-the-envelope/scripts/botec.py \
  --dau 1 --actions 7 --peak 2 --obj-bytes 50000 --media-frac 1.0 \
  --retention-days 1825 --server-qps 1000 --json
```

Confirm `storage_total_bytes: 638750000`. Every other figure in this
document is `user-stated`, `assumption`, or derived from that one script
run without re-running it — that is what Provenance is for: telling a
reader which is which.
````

</details>

Source: [`skills/iluvatar/references/example-output.md`](skills/iluvatar/references/example-output.md).

## 🧭 Where this fits

| Tool | What it does | How iluvatar differs |
|---|---|---|
| 🏗️ [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) (Analyst→PM→Architect) | Narrative `architecture.md` with tech-stack decisions already baked in, for a coding agent to read | Never names a technology; output is a schema-validated classification a *tool* parses by section name, not prose for an agent to interpret |
| 📋 [GitHub Spec Kit](https://github.com/github/spec-kit) | Captures requirements (what/why); deliberately excludes architecture | Sits downstream of what Spec Kit deliberately skips: the architecture classification, not another requirements pass |
| 🗺️ [C4 model](https://c4model.com) / [Structurizr](https://structurizr.com) | Machine-parseable architecture models, but a human has to already know and author the model | Derives archetypes and cross-cutting concerns from a one-line idea; nothing to hand-author first |
| 🔍 AI requirements-elicitation tools ([Visure](https://visuresolutions.com/ai-engineering/ai-requirements-elicitation), [Copilot4DevOps Elicit](https://copilot4devops.com/elicit/)) | Extract structured requirements/user stories from raw input | Same upstream distinction as Spec Kit: requirements, not architecture classification |

No live tool was found (verified 2026-08-12) that takes a free-text idea
and emits a stable, schema-validated, downstream-parseable classification
this way. Re-verify before leaning on this claim long after that date.
Full reasoning, sources, and caveats: [`COMPARISON.md`](COMPARISON.md).

The 15-invariant checklist itself isn't invented from vibes, either: it
started as a domain-agnostic synthesis, then got audited clause-by-clause
against five named frameworks (ISO/IEC 25010:2023, arc42, the AWS
Well-Architected Framework, DDD strategic design, the Google SRE
production-readiness taxonomy), closing three real gaps the audit found.
Details and citations: [`COMPARISON.md`](COMPARISON.md#grounded-in-named-standards-not-invented).

Phase 1's requirements scoping and capacity estimation (the `botec.py`
calculator behind the numbers above) aren't original either: they're
vendored from
[`proyecto26/system-design-skills`](https://github.com/proyecto26/system-design-skills)
(MIT, pinned at a specific audited commit; see
[`skills/iluvatar/references/vendor/VENDOR.md`](skills/iluvatar/references/vendor/VENDOR.md)).

## 🚫 What it won't do

- **Never names a technology** (not a database, not a framework, not a
  language) anywhere except a `Known Constraints` line the user imposed
  themselves. Classification, not selection.
- **Never writes code.**
- **Never skips a concern silently**: every one of its 15 invariants is
  marked relevant or deferred-with-a-reason; an unlisted concern is a
  decision some later tool would otherwise make alone.
- **Gates on a validator, not just a read-through**: a script checks the
  output's structure before a human ever reviews the content, because a
  section a downstream parser can't find is a defect a human review won't
  catch.

## 📄 License

MIT. See [LICENSE](LICENSE).
