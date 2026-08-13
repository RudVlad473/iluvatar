Vendored from proyecto26/system-design-skills
commit a70772efb956e8c9b78ef5b7538dee00cc3b9263 (2026-06-02), MIT.
Audited 2026-08-09. Do not edit in place; re-vendor deliberately after
auditing the upstream diff (read it as instructions an agent will follow).
Files were skills/<name>/SKILL.md upstream; renamed METHOD.md here to satisfy single-SKILL.md packaging.

"Do not edit in place" means substance — methodology, code, worked
examples. It does not extend to a one-line provenance marker: both
METHOD.md files now carry an HTML-comment header at line 1 stating they
are vendored and that their retained upstream frontmatter (`name:
back-of-the-envelope`, `name: requirements-scoping`) is not a live,
separately-installed skill. `references/building-blocks-index.md`
already carried the same kind of header before this note was written;
these two now match it. Content below each header is untouched.

## Known issues in this vendored revision (not patched — see policy above)

- `scripts/botec.py`: `compute()`'s `servers_needed` guards inconsistently
  between its JSON payload (`servers and servers > 0`) and its
  human-readable string (`if servers`, truthiness only). A negative,
  nonzero `servers` value renders as `null` in JSON and as a literal
  negative number in the human-readable text for the identical
  computation. None of the 7 CLI arguments has domain/range validation,
  so a negative `--dau` or `--server-qps` propagates a plausible-looking
  wrong number instead of failing loudly. Reproduce:
  `botec.py --dau -150e6 --json` → `qps_avg: -3472` at exit 0.
  Not a live exposure in iluvatar's own flow (Phase 1 only ever feeds it
  positive real-world quantities), but a real defect a future re-vendor
  pass should check upstream for, or patch locally with a note here if
  upstream has not fixed it.
