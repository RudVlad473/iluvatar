# ✨ iluvatar

*Conceives the world before anything is built.*

Ask an AI agent to architect your app and it names a tech stack before
it's named the problem — Postgres, Redis, and a queue appear before
anyone's asked what happens when two writes race, or what the app does
when the network is down.

iluvatar is a Claude Code skill that forces the boring questions first.
Give it a one-sentence app idea and it runs a 15-point classification
pass — state, failure, concurrency, compliance, the stuff that gets
skipped — and emits `HIGH-LEVEL-ARCHITECTURE.md`: a frozen,
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

**Or copy it directly** — works anywhere, no plugin system required.
Requires Python 3.9+ on PATH (stdlib only, nothing to `pip install`).

```
git clone https://github.com/RudVlad473/iluvatar
mkdir -p ~/.claude/skills
cp -r iluvatar/skills/iluvatar ~/.claude/skills/          # available in every project
```

Or scoped to one project only:

```
git clone https://github.com/RudVlad473/iluvatar
mkdir -p /path/to/your/project/.claude/skills
cp -r iluvatar/skills/iluvatar /path/to/your/project/.claude/skills/
```

On Windows (PowerShell):

```
git clone https://github.com/RudVlad473/iluvatar
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills"
Copy-Item -Recurse iluvatar\skills\iluvatar $HOME\.claude\skills\
```

Then just describe your app idea, or say "run iluvatar."

## 🤝 Pairs well with

iluvatar classifies whatever idea you hand it — it doesn't sharpen a
vague one first. Best served after Matt Pocock's
[`grill-with-docs`](https://github.com/mattpocock/skills): a relentless
interview that pressure-tests the idea and produces docs (ADRs, a
glossary) as it goes, so iluvatar has something more complete to
classify by the time it runs.

```
/plugin marketplace add mattpocock/skills
/plugin install mattpocock-skills@mattpocock
```

## What it produces

Give it: *"Paste a URL, get a clean readable version saved for later,
with a weekly email digest of what I haven't read yet. I want to
self-host it on one small server. No browser extension or mobile app for
now."*

iluvatar returns `HIGH-LEVEL-ARCHITECTURE.md`, classifying it as
`etl-pipeline` + `crud-service` + `background-jobs`, deriving a 10-stage
flow spine across write, read, and scheduled paths, and running real
numbers instead of adjectives:

```yaml
archetypes: [etl-pipeline, crud-service, background-jobs]
primary_artifact: a saved article (URL in, extracted text stored)
budget_notes: "~7 saves/day, ~639MB total storage over a 5-year
  retention window (botec.py), single self-hosted server..."
```

...and a flow spine that starts:

```
1. submit-url — user-entered URL → validated, canonicalized URL
2. fetch — canonicalized URL → raw HTML (or a recorded fetch failure)
3. extract — raw HTML → title + readable text + metadata
   ...
```

Every number is tagged with where it came from — a script run, something
the user stated, or an explicit assumption — so nothing in the document
reads as more certain than it is. The full worked example, all six
phases, is at
[`skills/iluvatar/references/example-output.md`](skills/iluvatar/references/example-output.md).

## Where this fits

| Tool | What it does | How iluvatar differs |
|---|---|---|
| BMAD Method (Analyst→PM→Architect) | Narrative `architecture.md` with tech-stack decisions already baked in, for a coding agent to read | Never names a technology; output is a schema-validated classification a *tool* parses by section name, not prose for an agent to interpret |
| GitHub Spec Kit | Captures requirements (what/why); deliberately excludes architecture | Sits downstream of what Spec Kit deliberately skips — the architecture classification, not another requirements pass |
| C4 model / Structurizr | Machine-parseable architecture models — but a human has to already know and author the model | Derives archetypes and cross-cutting concerns from a one-line idea; nothing to hand-author first |
| AI requirements-elicitation tools (Visure, Copilot4DevOps Elicit) | Extract structured requirements/user stories from raw input | Same upstream distinction as Spec Kit — requirements, not architecture classification |

No live tool was found (verified 2026-08-12) that takes a free-text idea
and emits a stable, schema-validated, downstream-parseable classification
this way. Re-verify before leaning on this claim long after that date.
Full reasoning, sources, and caveats: [`COMPARISON.md`](COMPARISON.md).

The 15-invariant checklist itself isn't invented from vibes, either — it
started as a domain-agnostic synthesis, then got audited clause-by-clause
against five named frameworks (ISO/IEC 25010:2023, arc42, the AWS
Well-Architected Framework, DDD strategic design, the Google SRE
production-readiness taxonomy), closing three real gaps the audit found.
Details and citations: [`COMPARISON.md`](COMPARISON.md#grounded-in-named-standards-not-invented).

Phase 1's requirements scoping and capacity estimation (the `botec.py`
calculator behind the numbers above) aren't original either — they're
vendored from
[`proyecto26/system-design-skills`](https://github.com/proyecto26/system-design-skills)
(MIT, pinned at a specific audited commit — see
[`skills/iluvatar/references/vendor/VENDOR.md`](skills/iluvatar/references/vendor/VENDOR.md)).

## What it won't do

- **Never names a technology** — not a database, not a framework, not a
  language — anywhere except a `Known Constraints` line the user imposed
  themselves. Classification, not selection.
- **Never writes code.**
- **Never skips a concern silently** — every one of its 15 invariants is
  marked relevant or deferred-with-a-reason; an unlisted concern is a
  decision some later tool would otherwise make alone.
- **Gates on a validator, not just a read-through** — a script checks the
  output's structure before a human ever reviews the content, because a
  section a downstream parser can't find is a defect a human review won't
  catch.

## License

MIT — see [LICENSE](LICENSE).
