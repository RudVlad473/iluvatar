# iluvatar — algorithm invariants

## Why this file exists

Iluvatar's output is a contract downstream tools parse by section name and
by the fact that every scale claim is a number, not an adjective. Both
guarantees depend on order: numbers come from Phase 1 before classification
names an archetype in Phase 2, the flow spine in Phase 3 exists before the
archetype and cross-cutting sweeps can compare against it in Phases 4-5,
and nothing is emitted until the user has confirmed it section by section.
This file registers that order so a change to it is visible as a change to
what the skill promises, not just a rewording.

## Pointer format

Each skeleton entry carries `implements:` — a heading anchor, resolved
against slugs generated the standard way: lowercased, every character that
is not a letter, digit, space or hyphen dropped, spaces to hyphens, runs of
hyphens collapsed.

## Skeleton — mode `CLASSIFY`

```
0. BUNDLE CHECK   Every bundled dependency (building-blocks-index.md,
                  the two vendored METHOD.md trees) is present, readable,
                  and uncorrupted. Missing any → stop before Phase 1, name
                  the missing file, never substitute a live or memory copy.
                  A hard stop performed on every run.
                  implements: SKILL.md#bundled-dependencies-no-external-lookups

1. INPUT CHECK    An application idea must already be in the conversation.
                  If not, ask for it and stop — no other input is required
                  or assumed.
                  implements: SKILL.md#required-input

2. SCOPE          Requirements-scoping method to verb-first requirements,
                  quantified non-functional constraints and an out-of-scope
                  list; back-of-the-envelope method (botec.py) turns the
                  constraints into numbers, with a documented manual
                  fallback if it fails. Solution-shaped requirements get
                  stripped to the underlying need.
                  implements: SKILL.md#phase-1-scope-the-idea

3. CLASSIFY       Name every archetype that applies — plural, not one label
                  for a hybrid system — one justification line each.
                  implements: SKILL.md#phase-2-classify

4. FLOW SPINE     Identify the primary artifact and list, in order, both
                  write and read paths; a spineless app gets one spine per
                  core user action instead.
                  implements: SKILL.md#phase-3-derive-the-flow-spine

5. ARCHETYPE SWEEP  For each archetype from step 3, add stages mature
                  systems of that kind contain that the spine is missing,
                  marked archetype-derived.
                  implements: SKILL.md#phase-4-archetype-sweep

6. INVARIANT SWEEP  SKILL.md's 5A: every invariant question run against
                  the derived spine, each marked relevant or
                  deferred-with-reason, never silently skipped.
                  implements: SKILL.md#5a-invariant-questions-always-every-archetype

7. ARCHETYPE CROSS-CHECK  SKILL.md's 5B: for backend/distributed/service
                  archetypes, cross-check step 6's output against the
                  bundled backend catalog. A weaker guarantee than step 6:
                  only archetypes with a sourced catalog get this
                  cross-check; others say so plainly instead of claiming
                  coverage they don't have.
                  implements: SKILL.md#5b-archetype-cross-check-completeness-only

8. GENERATIVE CATCH-ALL  SKILL.md's 5C, asked last: what must be true of
                  the system as a whole that no single flow stage owns?
                  Anything found is added and flagged as a candidate
                  addition to 5A's list.
                  implements: SKILL.md#5c-generative-catch-all

9. WRITE  SKILL.md's 6a: write HIGH-LEVEL-ARCHITECTURE.md to the frozen
                  section schema, extended with Provenance and How to
                  Verify.
                  implements: SKILL.md#6a-write-the-document

10. VALIDATE  SKILL.md's 6b: run scripts/validate_architecture.py; fix
                  what it reports before the document is presented.
                  implements: SKILL.md#6b-validate-before-gating

11. USER GATE  SKILL.md's 6c: re-read the validated document from disk
                  and walk the user through it section by section. Only a
                  confirmed document is a valid output. USER GATE.
                  implements: SKILL.md#6c-user-gate
```

Steps 6-8 were previously one skeleton entry ("CROSS-CUTTING SWEEP")
covering only 5A. 5B and 5C are real, separately-ordered sub-passes with
their own admission rules (5B's "do not translate the backend catalog by
analogy," 5C's "asked last") — collapsing them into 5A's entry made a
change to either invisible as a change to what the skill promises, which
is exactly what this file exists to prevent.

## Invariants

Each entry names its family. `ORDERING` invariants are evidenced by the
skeleton above plus `validate_skeleton.py`'s conformance check — no
separate enforcement line. `ADMISSION` and `BOUNDARY` invariants get one:
either a script that refuses, or `none — stated-but-unenforced` plus where
the rule is written, so an unenforced rule is never read as equivalent to
an enforced one.

```
I-IL-1   [ORDERING]   WRITE BEFORE VALIDATE BEFORE GATE
         Step 9 writes the document; step 10 checks its structure; step 11
         presents it to the user. Nothing reaches the user gate unwritten,
         and nothing is presented unchecked.

I-IL-2   [ORDERING]   EMIT NEVER RUNS WITHOUT THE USER GATE
         The pipeline is not complete at step 9 or step 10 — only a
         confirmed document (step 11) is a valid output of this skill.
         validate_skeleton.py's conformance check flags step 11 being
         listed ahead of steps 9-10 as a reorder, and flags its heading
         disappearing from SKILL.md as an unresolvable pointer. Neither
         check observes a real run — they confirm this file's claimed
         order still matches SKILL.md's actual order, not that the model
         followed it this time.

I-IL-3   [ADMISSION]  NO TECHNOLOGY NAMES OUTSIDE KNOWN CONSTRAINTS
         Classification, Flow Spine, and Cross-cutting name concepts and
         concerns, never products — Known Constraints is the only section
         a technology name may appear in, and only when user-imposed.
         Enforcement: none — stated-but-unenforced. Stated in Guardrails'
         "No technology names" bullet.

I-IL-4   [BOUNDARY]   BUNDLED COPIES ONLY
         Never substitute an externally installed skill, the live
         upstream repo, or a memory-reconstructed catalog for the vendored
         copies under references/vendor/ — even if a substitute is newer.
         Enforcement: none — stated-but-unenforced. Stated in
         Preconditions' "Use ONLY these bundled copies" paragraph, which
         also names the sanctioned upgrade path (audit the upstream diff,
         re-vendor, update the commit hash).

I-IL-5   [ADMISSION]  NO SILENT SKIPS IN THE CROSS-CUTTING SWEEP
         Every 5A invariant question is marked relevant or
         deferred-with-a-reason; nothing is left unmarked.
         Enforcement: none — stated-but-unenforced. Stated in Phase 5's
         "Never skip one silently" paragraph and restated in Guardrails.

I-IL-6   [ADMISSION]  THE OUTPUT SCHEMA IS FROZEN
         Renaming, merging, or omitting a required section, or altering
         an existing frontmatter key, is a breaking change for every
         downstream parser. New schema versions extend by appending a
         section at the end.
         Enforcement: scripts/validate_architecture.py confirms all nine
         sections are present, correctly named, and in order — it cannot
         confirm nothing downstream still depends on a key that gets
         renamed anyway, only that this run's document conforms.

I-IL-7   [ADMISSION]  NUMBERS OVER ADJECTIVES
         Every scale claim is a number or a written assumption, and
         Provenance says which — a script run, a user statement, or an
         assumption cross-referenced to Open Questions.
         Enforcement: scripts/validate_architecture.py confirms the
         Provenance section exists and is non-empty; it cannot confirm
         a given tag inside it is accurate, only that the section itself
         was not skipped. Stated in Guardrails' "Numbers over adjectives"
         bullet and Phase 6a's Provenance section description.

I-IL-8   [BOUNDARY]   A MISSING OR CORRUPT VENDOR FILE STOPS THE RUN
         Preconditions' bundled-dependency check is a hard stop before
         Phase 1 if any bundled file is missing, unreadable, or corrupt —
         and the stop never resolves itself by substituting a live or
         memory copy (that would violate I-IL-4 instead).
         Enforcement: none — stated-but-unenforced.
```

## Not violations — no marked commit needed

- Adding a clarifying question inside Phase 1's scoping pass *(ordering)*
- Adding an invariant question to the 5A list, once 5C has repeatedly
  surfaced it *(admission — the list is stated as stable but refinable)*
- Adding a new archetype-derived stage in Phase 4 *(admission — tightening)*
- Appending a new section at the end of the Phase 6a schema *(admission —
  the schema is frozen against renaming or reordering existing sections,
  not against extension; Provenance and How to Verify were added exactly
  this way)*

## Violations — require `[INVARIANT CHANGE]`

- Naming a technology in Classification, the Flow Spine, or Cross-cutting
  *(admission — I-IL-3)*
- Substituting a live, newer, or memory-reconstructed copy of the vendored
  requirements-scoping / back-of-the-envelope / building-blocks material for
  the bundled one in `references/vendor/` *(boundary — I-IL-4)*
- Proceeding into Phase 1 when a bundled vendor file turns out to be
  missing, unreadable, or corrupt *(boundary — I-IL-8)*
- Marking a Phase 5A invariant neither relevant nor deferred-with-reason
  *(admission — I-IL-5)*
- Skipping 5B's cross-check for an archetype the bundled catalog covers,
  or translating that catalog into a different domain by analogy for one
  it doesn't *(admission — Phase 5B's own two rules)*
- Declaring the run complete without walking the user through Phase 6c's
  document section by section *(ordering — I-IL-2)*
- Renaming, merging, or omitting a Phase 6a output section, or altering a
  frontmatter key *(admission — I-IL-6)*
- Filling a scale claim with a plausible-sounding adjective instead of a
  number or a written assumption, or omitting its Provenance tag
  *(admission — I-IL-7)*
