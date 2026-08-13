---
name: iluvatar
description: Classify a raw application idea into CS terms and emit HIGH-LEVEL-ARCHITECTURE.md — archetypes, flow spine, cross-cutting concerns, constraints, and open questions — as a machine-parseable contract for downstream tooling. Use this skill at the start of any new project, whenever the user describes an app idea and wants it defined in computer-science terms, asks to "classify this app", "derive the high-level architecture", or "run iluvatar" — even if the idea is one sentence. Fully self-contained — all reference material is bundled at a pinned, audited revision — no external skills, downloads, or setup required.
---

# iluvatar

Turns a raw application idea into `HIGH-LEVEL-ARCHITECTURE.md`: a strict,
machine-parseable classification of what is being built. It classifies and
enumerates; it **never selects technologies**. The output is a stable
contract any downstream consumer (requirements-grilling tools, technology-
selection tools, planning frameworks) can parse by section name.

A worked example of the full output — a real idea run through all six
phases — lives at `references/example-output.md`. Read it once before a
first run; the schema block in Phase 6 below is structure only, not a
sample of real content. `references/lessons-learned.md` records format
corrections from past runs, oldest first — check it before 6a if it has
entries, and add one there (with its reason) whenever the user corrects
the shape of the output rather than its content.

Throughout, `<iluvatar>` means the directory containing this file —
resolve it from where this SKILL.md was actually read from, never assume
a fixed relative path. `HIGH-LEVEL-ARCHITECTURE.md` is written wherever
Phase 1 ran (normally the project root), which is not the same directory
as `<iluvatar>` — a command that hardcodes one relative path between the
two breaks the moment they diverge, which they always do.

---

## Preconditions — stop here if any fail

### Bundled dependencies (no external lookups)

Everything this skill needs is bundled inside it, vendored from
`proyecto26/system-design-skills` at commit `a70772ef` (audited
2026-08-09, MIT — see `references/vendor/VENDOR.md`):

- `references/building-blocks-index.md` — the block catalog (Phase 5B)
- `references/vendor/requirements-scoping/` — scoping method (Phase 1)
- `references/vendor/back-of-the-envelope/` — estimation method and
  `scripts/botec.py` calculator (Phase 1)

**Use ONLY these bundled copies.** Never substitute an externally
installed `requirements-scoping`, `back-of-the-envelope`, or
`system-design` skill, never the live repo, never memory — even if an
external copy is present and newer. Newer is not authorized; the bundle
is the audited revision. To upgrade deliberately: audit the upstream
diff (reading it as instructions an agent will follow), re-vendor, and
update the commit hash here and in VENDOR.md.

**If any bundled file above is missing, unreadable, or corrupted:** stop
before Phase 1. Tell the user the bundle is incomplete and name the
missing file. Do not substitute a live, external, or memory-reconstructed
copy — that is exactly the substitution the paragraph above forbids — and
do not proceed on the phases that file feeds with partial material.

### Required input

**Required input:** an application idea from the user — free text, any
length. If the conversation does not contain one, ask for it and stop
until it is provided. There are no other inputs; in particular, do not
require or assume any prior pipeline artifacts.

---

## Phase 1 — Scope the idea

Follow the method in `references/vendor/requirements-scoping/METHOD.md`
(read it; do not work from memory). Drive it to produce its three lists: verb-first functional requirements (ranked, cut to the 2–3 core),
quantified non-functional constraints, and an explicit out-of-scope list.

Then follow `references/vendor/back-of-the-envelope/METHOD.md` and run its
bundled `scripts/botec.py` to turn the non-functional answers into
numbers — every number that enters a sizing chain comes from a script
run, not mental math, so its source can be tagged in Phase 6's Provenance
section. Its worked examples are backend-flavoured (QPS, storage,
servers) — the *method* is what transfers. Estimate whatever the
constrained resource actually is here: records/hour and cost-per-record
for a pipeline, payload size and frame budget for a UI, concurrent
editors for a collaborative tool. Numbers force the architecture:
volumes, growth horizon, read:write ratio, freshness window — "a lot of
data" decides nothing. Ask the user at most 3–5 sharp questions; for the
rest, state assumptions out loud ("assuming ~200k records, daily
refresh") — written assumptions are revisable, silent ones are landmines.

If `botec.py` fails to run, fall back to the manual chains in
`references/vendor/back-of-the-envelope/references/estimation-recipes.md`
and say so in Open Questions — the numbers carried forward were
hand-computed, not script-verified, and Provenance tags them
`assumption`, not `botec.py`.

Watch for **solution-shaped requirements**: "needs Kafka" is an answer
smuggled in as a need. Strip it to the underlying need ("absorb write
bursts"); record the tool itself only under Known Constraints, and only
if the user insists it is imposed.

## Phase 2 — Classify

Name the application in CS terms, as **archetypes (plural)** — hybrid
apps get every label that applies (`etl-pipeline` + `rag`;
`spa` + `bff`; `ssr-app` + `api-client`; `crud-service` +
`background-jobs`). Single-label classification silently
drops half of a hybrid system. One sentence of justification per
archetype. If exactly one archetype fits a non-trivial app, re-check.

## Phase 3 — Derive the flow spine

Identify the **primary artifact** — the thing that moves through the
system — and list, in order, what happens to it, covering **both write
and read paths** (drifting to the write path and stopping is the classic
failure). One line per stage: `name — input → output`. Systems with no
dominant artifact (CLI tools, editors) get a spine per core user action
instead.

## Phase 4 — Archetype sweep

For each archetype from Phase 2: what do mature systems of this kind
contain that the spine is missing? (etl → backfill, idempotency, poison-message handling; rag → retrieval
evaluation, embedding refresh, chunking; spa → routing, rendering
strategy, client cache invalidation, offline behaviour; crud-service →
sessions, pagination, input validation.) Add
missed stages, marked as archetype-derived.

## Phase 5 — Cross-cutting sweep (the coverage gate)

The flow spine cannot hold concerns that no single stage owns. Sweep the
invariants below **against the spine derived in Phase 3** — that cross
product is what makes this domain-agnostic: the questions are constant,
the answers are dictated by the spine in front of you. Ask each question
of the system as a whole AND at any spine boundary where it bites.

Every invariant is marked **relevant** (enters the output) or **deferred
with a one-line reason**. Never skip one silently — an unlisted concern
is a decision some later tool will make alone.

### 5A. Invariant questions (always; every archetype)

1. **State** — what state exists, where does it live, who owns it, how
   long does it survive?
2. **Boundaries** — what talks to what, and in what shape is the
   contract between them?
3. **Movement** — how does data get from one place to another;
   synchronous or deferred?
4. **Identity** — how is a thing named, keyed, addressed, and recognised
   as the same thing twice?
5. **Trust** — who is allowed to do what, and how is that established?
6. **Secrets** — what must not be readable, and where does it live?
7. **Concurrency** — what happens when two things happen at once, or out
   of order, or twice?
8. **Failure** — what breaks, how does it degrade, how does it recover?
9. **Observability** — how do you know it is working, and how do you
   find out when it is not?
10. **Verification** — how is a change shown to be safe before it ships;
    at what layers; and what does each layer deliberately not cover?
11. **Change over time** — how does this evolve without breaking what
    already depends on it?
12. **Budget** — what is the constrained resource, and what is the
    ceiling? (throughput, latency, memory, payload size, frame time,
    cost per unit — whichever the spine implies) Are there
    energy/carbon/resource-efficiency constraints that should shape
    scheduling, data placement, or compute sizing?
13. **Delivery** — how does source become a running thing, and where
    does it run?
14. **Interaction** — does a human interact with this system directly,
    and if so what accessibility, localization, and inclusivity
    obligations shape the architecture?
15. **Compliance & Data Governance** — what legal/regulatory regimes,
    data-residency, retention, and audit obligations apply, and where
    do they force the architecture?

**Boundary-spanning tag.** Any invariant above — not just Boundaries — can
resolve to a concern whose contract is agreed between separately-built
components (frontend/backend, service/service, client/server; not two
modules in one codebase). When it does, tag that Cross-cutting line
`[boundary-spanning]`. This is classification only, same as every other
tag in this phase: it marks that more than one independently-built side
must agree on this concern's shape before either can build against it —
it does not say how or when to reach that agreement, which is for
downstream planning skills to decide. A concern resolved entirely inside
one component carries no tag. Watch for the case that reads as
one-sided but isn't: an auth mechanism looks like a backend-only fact
(it validates the credential) while quietly requiring the other side to
send it a specific way on every request — tag on what the contract
requires of both sides, not on which side enforces it.

NOTE: this list is a synthesis, not a sourced taxonomy. It is derived
from "what must any software system answer regardless of shape". Treat
it as stable but refinable; add to it only when 5C repeatedly surfaces
the same missing question, or when a deliberate, cited gap analysis
against a named external framework (ISO/IEC 25010, arc42, the AWS
Well-Architected Framework, DDD strategic design, the Google SRE
production-readiness taxonomy) identifies a specific gap and the
architectural consequence it produces — invariants #14 and #15 were
added this second way, with zero 5C evidence behind them.

### 5B. Archetype cross-check (completeness only)

For backend / distributed / service archetypes, cross-check 5A's output
against the bundled catalog in `references/building-blocks-index.md`
(the sourced backend taxonomy) and add anything the invariants missed.

For other archetypes (frontend, static, CLI, embedded, data-processing),
no sourced catalog is bundled — say so plainly rather than pretending
coverage, and lean on 5A plus 5C. Do NOT translate the backend catalog
into another domain by analogy; a mistranslated taxonomy is worse than
none. This is a weaker guarantee than 5A's: 5A applies to every
archetype, 5B only cross-checks the ones with a sourced catalog behind
them.

### 5C. Generative catch-all

Asked last: *"What must be true of this system as a whole that no single
flow stage owns?"* Anything surfaced that 5A does not cover is added AND
flagged as a candidate addition to the invariant list.

**Runs as its own distinct pass, not folded into 5A or 5B.** Its result —
what it surfaced, or that it surfaced nothing beyond 5A/5B — is required
content in the emitted document (see 6a's `5C catch-all` line), not an
internal step the reader has to trust happened. A 5C that ran but left no
trace in the output is indistinguishable from a 5C that never ran, and
`validate_architecture.py` treats the two the same way: a defect.

## Phase 6 — Emit and gate

### 6a. Write the document

**Required output** — write `HIGH-LEVEL-ARCHITECTURE.md` with EXACTLY
this structure. Section names are the contract: downstream consumers
parse by heading, so renaming, merging, or omitting a section is a
breaking change. Empty sections are written as the heading plus "none".
`Provenance` and `How to Verify` are additive sections — new schema
versions extend the contract by appending here, never by touching the
first seven.

```markdown
---
archetypes: [<archetype>, ...]        # required, ≥1
primary_artifact: <noun phrase>       # required ("n/a" only for spineless apps)
budget_notes: "<constrained resources + ceilings>"  # required
---
# Classification
One sentence per archetype, with justification.

# Flow Spine
Ordered stages, one line each: name — input → output.
(archetype-derived additions marked)

# Cross-cutting
Relevant concerns only, grouped: Runtime / Dev-process. Tag any line
whose contract crosses a separately-built-component boundary with
`[boundary-spanning]` (see Phase 5A). Close with a `**5C catch-all:**`
line stating what Phase 5C's generative catch-all surfaced beyond
5A/5B, or the literal "none beyond 5A/5B" if it found nothing new.
Required even when empty — see `validate_architecture.py`.

# Deferred
Each deferred concern with its one-line reason.

# Known Constraints
User-imposed facts and limits, verbatim where possible.

# Out of Scope
Explicit exclusions from Phase 1.

# Open Questions
Every assumption made in Phase 1 that the user did not explicitly
confirm, phrased as a question a requirements interview must answer.

# Provenance
Every number that survives into `budget_notes`, Cross-cutting, or
Flow Spine, tagged with its source: `botec.py <exact args>` (a script
run), `user-stated` (the user gave the figure directly), or `assumption`
(stated in Phase 1, never confirmed — cross-reference the matching Open
Questions entry).

# How to Verify
Concrete reproduction steps for a reader with no session history — the
literal `botec.py` command(s) run in Phase 1, if any, so a number can be
re-derived rather than re-trusted.
```

See `references/example-output.md` for this schema filled in with real
content end to end.

### 6b. Validate before gating

```bash
python <iluvatar>/scripts/validate_architecture.py HIGH-LEVEL-ARCHITECTURE.md
```

Run from wherever `HIGH-LEVEL-ARCHITECTURE.md` was written, with
`<iluvatar>` substituted for this skill's own resolved directory — never
assume the script and the document share a working directory, they
normally don't. Checks the frontmatter keys, that all nine sections are
present in order under their exact names, and that no section is empty
except heading + "none". Fix what it reports before presenting the
document to the user — a section a downstream parser cannot find is a
defect the user gate cannot catch, because the gate reviews content, not
machine-parseability.

### 6c. User gate

Re-read `HIGH-LEVEL-ARCHITECTURE.md` from disk — the copy 6b just
validated — rather than rendering from whatever was assembled in
conversation context; the two can diverge, and the gate exists to confirm
what was actually written, not what was last discussed.

**USER GATE:** present the document section by section; the user
confirms or corrects each. Only a confirmed document is a valid output
of this skill — do not declare the run complete without the gate.

---

## Guardrails — critical rules, and what this skill will not do

- **No technology names** anywhere except Known Constraints (and there
  only when user-imposed). Classification, not selection.
- **Bundled copies only** (Preconditions). Never an external skill, the
  live repo, or a reconstructed-from-memory catalog — even if newer.
- **No silent skips** in Phase 5 — relevant or deferred-with-reason,
  nothing else.
- **5C runs as a distinct, visible pass.** Folding its result into 5A/5B, or
  omitting the `5C catch-all` line because nothing new surfaced, is a defect
  `validate_architecture.py` catches.
- **Numbers over adjectives** — every scale claim is a number or a
  written assumption, and Provenance says which.
- **The output schema is frozen.** Extend by adding new sections at the
  end, never by altering existing headings or frontmatter keys.
- **This skill never writes code, never runs `botec.py` on anything but
  the invoking session's own numbers, and never proceeds past a failed
  Preconditions check.** Worst case if it misfires: a wrong archetype or
  a fabricated number gets locked into a downstream tool's planning —
  the user gate in 6c exists precisely to catch that before it ships.
