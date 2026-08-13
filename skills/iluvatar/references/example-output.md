# Worked example — `HIGH-LEVEL-ARCHITECTURE.md`

Real content, not a placeholder. The idea run through all six phases:

> "Paste a URL, get a clean readable version saved for later, with a
> weekly email digest of what I haven't read yet. I want to self-host it
> on one small server. No browser extension or mobile app for now."

Every number below was either produced by running `scripts/botec.py`
(shown verbatim), stated by the user, or written as an explicit
assumption — Provenance says which, so nothing here reads as more certain
than it is.

---

```markdown
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
```

---

Note for anyone extending this example: the numbers above were produced
by actually running `botec.py` with the arguments shown, not written by
hand — that is the standard this skill holds its own output to, and this
file is held to it too.
