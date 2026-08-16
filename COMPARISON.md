# Comparison

How iluvatar's actual differentiator — classification that never names a
technology, emitted as a schema-validated contract — compares against the
closest tools in the space. Researched 2026-08-12 against primary sources
(fetched and cited, not search-snippet-only); re-verify before treating
this as current if you're reading it much later.

## Tools checked

| Tool | What it does | Verdict |
|---|---|---|
| BMAD Method (Analyst→PM→Architect) | Multi-agent pipeline: Analyst produces a Project Brief, PM a PRD, Architect an `architecture.md` with tech decisions; artifact-per-phase handoff | Adjacent, not equivalent |
| GitHub Spec Kit (`/speckit.specify`) | Turns a plain-language feature description into a templated `spec.md` (user stories, functional requirements, acceptance criteria); deliberately excludes tech choices; adds `/speckit.checklist` and `/speckit.analyze` consistency passes | Adjacent, not equivalent |
| C4 model + Structurizr DSL | Text/"models-as-code" description of software structure (context/containers/components), machine-parseable, MCP server for validation | Adjacent, not equivalent |
| AI requirements-elicitation tools (Visure AI, Copilot4DevOps "Elicit") | Extract structured functional/non-functional requirements and user stories from raw input into a backlog | Adjacent, not equivalent |

The AI "architecture generators" that dominate a casual search — Arqi AI,
TechStacker, Eraser's diagram generator, and various app-builder apps —
were checked and discarded as not relevant: they're single-pass
prose/diagram producers, not staged classification tools.

**No candidate rose to "equivalent or better."**

## Why each is adjacent, not equivalent

**BMAD** is the closest structured pipeline, but it does a different job.
Its planning artifacts (Project Brief, PRD, `architecture.md`) are
narrative documents optimized for a downstream *coding* agent to read, not
a machine-parseable *classification* of the system. It has no fixed,
archetype-agnostic invariant checklist that is forced to mark every
concern "relevant" or "deferred with a reason," no CS-archetype labeling
step, and no read-path/write-path flow spine as a first-class artifact.
Its completeness relies on the agent's in-the-moment judgment plus a
readiness review, not a schema validator over a frozen section structure.

**GitHub Spec Kit** captures the "what/why" (requirements) and explicitly
excludes architecture; it sits *upstream* of the classification job, not
as a substitute for it. Its `/speckit.checklist` ("unit tests for
English") and `/speckit.analyze` findings table are real completeness
mechanisms, but they check a spec for clarity/consistency, not a system
against a taxonomy of cross-cutting architectural concerns.

**C4/Structurizr** is genuinely machine-parseable but requires a human to
already know and author the model; it neither derives archetypes from a
one-line idea nor sweeps cross-cutting concerns.

**AI requirements-elicitation tools** (Visure, Copilot4DevOps Elicit) sit
in the same upstream lane as Spec Kit — structured requirements
extraction, not architecture classification.

## Conclusion

No live product found takes a free-text idea and emits a stable,
schema-validated, downstream-parseable classification — archetypes, a
read/write flow spine, and a fixed invariant cross-cutting sweep with
explicit relevant/deferred marks. That's the genuinely open ground
iluvatar occupies.

## What would change this verdict

If BMAD's architecture workflow started enforcing per-archetype
classification against a fixed invariant checklist with explicit
relevant/deferred marks — instead of relying on the Architect agent's
in-the-moment judgment — or if Spec Kit or the C4/Structurizr tooling
added automatic archetype derivation and a cross-cutting sweep from a
one-line idea instead of requiring a human to author the model, that
would narrow or close this gap. Worth re-checking if either project ships
something in that shape.

## Grounded in named standards, not invented

The 16 cross-cutting invariants iluvatar sweeps against (State,
Boundaries, Movement, Identity, Trust, Secrets, Concurrency, Failure,
Observability, Verification, Change-over-time, Budget, Delivery,
Interaction, Compliance & Data Governance, Attack Surface) started as a
domain-agnostic synthesis — "what must any software system answer
regardless of shape" — not a transcription of any one standard.
`SKILL.md` says so directly: "this list is a synthesis, not a sourced
taxonomy."

What makes it more than vibes is what happened next: a deliberate, cited
gap analysis against five named external frameworks, closing three real
gaps and confirming the rest were already covered — checked, not
asserted.

**Real gaps found and closed:**
- **Interaction** (invariant #14) — ISO/IEC 25010:2023 replaced
  "usability" with "interaction capability" and added inclusivity as an
  explicit sub-characteristic, verbatim from the 2023 revision. Nothing
  in the original 13 invariants asked whether a human interacts with the
  system directly, or what accessibility/localization obligations that
  creates.
- **Compliance & Data Governance** (invariant #15) — arc42's
  "Constraints" section and ISO 25010's Security sub-characteristics ask
  about legal/regulatory constraints (GDPR/HIPAA/PCI, data residency,
  retention, audit) that Trust and Secrets alone don't cover.
- **A sustainability sub-question under Budget** — the AWS
  Well-Architected Framework's sixth pillar (added December 2021) treats
  energy/carbon/resource efficiency as a design driver alongside cost;
  Budget originally only asked about money and volumes.
- **Attack Surface** (invariant #16, added 2026-08-16 — a separate pass
  from the August 12 audit above) — the AWS Well-Architected Framework's
  Security pillar splits Identity and Access Management and Data
  Protection (already covered by Trust and Secrets) from two further
  areas neither invariant reaches: Infrastructure Protection ("protected
  against unintended and unauthorized access, and potential
  vulnerabilities," naming WAFs and API gateways as policy-enforcement
  points) and Application Security's dependency-management practice
  (SEC11-BP05, "Centralize services for packages and dependencies").
  Trust answers who is allowed to do what; neither it nor Secrets asks
  what happens when something malicious — malformed input, a flood of
  requests, a compromised dependency — hits the boundary regardless of
  who it claims to be.

**Confirmed already covered, not manufactured into findings:** DDD
strategic design's bounded contexts map onto the Boundaries invariant and
its `[boundary-spanning]` tag; the Google SRE production-readiness
taxonomy (monitoring, capacity, rollback, on-call) maps onto
Observability, Budget, Delivery, and Failure; the rest of ISO 25010's
characteristics (Maintainability, Flexibility, Reliability, Performance
Efficiency) map onto Change-over-time, Failure, Verification, and
Budget.

This audit isn't a one-time claim — it's how the invariant list is meant
to grow. `SKILL.md`'s own rule: a new invariant only gets added when a
generative catch-all pass repeatedly surfaces the same missing question,
or a *deliberate, cited* gap analysis against a named framework
identifies a specific gap and its architectural consequence. Invariants
#14, #15, and #16 were added this second way.

The three vendored methods iluvatar's Phase 1 runs on are a separate,
narrower kind of grounding, not written for this project: Phase 1's
requirements scoping and capacity estimation (`botec.py`) come from
[`proyecto26/system-design-skills`](https://github.com/proyecto26/system-design-skills)
(MIT, pinned at a specific audited commit — see
`skills/iluvatar/references/vendor/VENDOR.md`).

**Sources for this audit** (fetched and cited August 12, 2026):

- https://www.iso.org/obp/ui/en/#!iso:std:78176:en
- https://quality.arc42.org/standards/iso-25010
- https://arc42.org/overview/
- https://docs.arc42.org/home/
- https://aws.amazon.com/blogs/apn/the-6-pillars-of-the-aws-well-architected-framework/
- https://aws.amazon.com/about-aws/whats-new/2021/12/new-sustainability-pillar-aws-well-architected-framework/
- https://martinfowler.com/bliki/BoundedContext.html
- https://sre.google/sre-book/evolving-sre-engagement-model/

## Caveats

- **BMAD is mid-rewrite** (`bmad-create-architecture` moving toward
  `bmad-architecture` / `ARCHITECTURE-SPINE.md`). Some of its internal
  workflow step files could not be opened during this research (GitHub
  raw/tree access was blocked), so claims about its *exact current*
  architecture-workflow output are the most likely of this table to
  drift — re-verify against whatever version is installed.
- A third-party "bmad-architecture" Claude skill (by GitHub user
  `bacoco`) is **not** an official bmad-code-org component and was not
  what was evaluated here.
- Vendor marketing pages for the discarded tools (Arqi AI, TechStacker,
  and similar app-builder listings) were treated as promotional, not as
  evidence — those tools were judged "not relevant" rather than accepted
  at face value.
- ATAM (Architecture Tradeoff Analysis Method) — its quality-attribute
  utility tree is a plausible additional lens for iluvatar's own
  cross-cutting sweep, but the research budget ran out before that query
  completed. Flagged as an open follow-up, not a finding.

## Sources

Fetched and cited August 12, 2026:

- https://docs.bmad-method.org/reference/workflow-map/
- https://github.com/bmad-code-org/BMAD-METHOD
- https://github.com/github/spec-kit
- https://github.com/github/spec-kit/blob/main/spec-driven.md
- https://den.dev/blog/github-spec-kit/
- https://structurizr.com/
- https://docs.structurizr.com/dsl
- https://visuresolutions.com/ai-engineering/ai-requirements-elicitation
- https://copilot4devops.com/elicit/

Fetched and cited August 16, 2026, for the Attack Surface addition
(invariant #16):

- https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/security.html
- https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/infrastructure-protection.html
- https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/application-security.html
