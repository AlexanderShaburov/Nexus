---
type: invariant
scope: system
status: approved
created: 2026-06-04
updated: 2026-06-04
source_of_truth: true
knowledge_visibility: binding
tags: [invariant, review, gap-analysis, classification, knowledge-visibility]
---

## Relations

- depends_on:
  - [Knowledge Visibility Specification](../specs/spec--system--knowledge-visibility.md) — defines the three visibility classes this invariant ranges over.
  - [Architecture Review Specification](../specs/spec--system--architecture-review.md) — defines the dual-analysis review workflow this invariant requires.
- constrains:
  - [Knowledge-Driven Task Orchestration Specification](../specs/spec--system--knowledge-driven-task-orchestration.md) — the Retrieve obligation must cover development documents before declaring gaps.
- relates_to:
  - [Lifecycle Gates Invariant](invariant--system--lifecycle-gates.md) — both are non-negotiable agent invariants.

---

# Invariant: Review Classification

## Statement

No architecture gap, missing-spec finding, or roadmap omission may be reported until **both** authoritative documents **and** active development documents (including roadmap drafts, design proposals, pending specifications, in-review documents, and session-derived design notes) have been examined for coverage of the topic under review.

Every reported gap MUST be classified as exactly one of:

1. **Truly Missing** — no binding document exists, no development document exists, no roadmap or architecture draft or proposal covers the topic.
2. **Exists As Draft** — a development-class document covers the topic but is not yet promoted to binding.
3. **Exists But Not Normalized** — content covering the topic exists in architecture, roadmap, session, or proposal documents but has not been extracted into a formal specification.
4. **Superseded Gap** — the finding is invalid because a newer binding or development document already covers the topic.

A finding that says "Specification X is missing" without demonstrating absence from **both** binding and development knowledge is INVALID.

## Failure mode this invariant prevents

Without this invariant, reviewers consult only authoritative documents and miss design work that already exists in drafts, roadmaps, proposals, and session notes. The consequences observed in practice:

- phantom missing-spec findings;
- duplicate design work begun on topics already covered by drafts;
- divergent design tracks between authoritative and development knowledge;
- erosion of trust in review output.

See `decisions/decision--system--development-visibility-failure.md` for the originating case note.

## Consequences of violation

- Gap reports contain phantom findings.
- Development effort is wasted on already-drafted designs.
- The Knowledge Vault fragments into parallel un-reconciled tracks.

## Amendment rule

This invariant MAY be relaxed only via a formal `decision--system--…` document that records the reasoning and the trade-off. No temporary suspension is permitted.

## Pointer to enforcement

This is a **content-shape invariant**. Enforcement is by:

- the dual-analysis output format mandated in `specs/spec--system--architecture-review.md`;
- bootstrap-time discovery of active design tracks (see `specs/spec--system--session-bootstrap.md`, STEP 3);
- agent self-discipline at review time;
- post-hoc validation via the checklist in `runbooks/runbook--system--development-visibility-migration.md`.
