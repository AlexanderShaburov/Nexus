---
type: report
scope: system
status: approved
created: 2026-06-04
updated: 2026-06-04
source_of_truth: false
knowledge_visibility: development
tags: [report, patch, governance, visibility, audit]
---

# Development-Phase Knowledge Visibility — Patch Report

## What this patch does

This patch fixes a governance bug in the Nexus Knowledge Vault model called the **Development-Phase Knowledge Visibility Failure**: reviewers consulted only authoritative documents (`status: approved` + `source_of_truth: true`) and missed design work that already existed in drafts, roadmaps, proposals, and in-review documents, producing phantom missing-spec findings.

The patch introduces a third axis — **knowledge visibility** — with three classes (binding / development / historical), expressed via a new optional frontmatter field `knowledge_visibility`. It updates the review workflow to a mandatory dual analysis (Binding State + Development State) with four-way gap classification, and adds bootstrap-time visibility of active design tracks. A migration runbook is provided for existing Nexus-based projects.

This report exists for traceability and audit. It is intentionally short. The authoritative content lives in the vault documents listed below.

---

## Why a separate field

Existing fields described:

- `status` — workflow maturity (draft → review → approved)
- `source_of_truth` — authoritative status (boolean)

Neither directly answered the question that review tooling asks:

> "Must this document be considered when assessing what exists or what is missing?"

The full reasoning, including the rejected alternatives (extend `status`, use `tags`, introduce `lifecycle_state`), is in `knowledge/decisions/decision--system--development-visibility-failure.md`.

---

## Files added

| Path | Role |
|---|---|
| `knowledge/invariants/invariant--system--review-classification.md` | Non-negotiable rule: no gap may be reported without consulting binding AND development knowledge. |
| `knowledge/specs/spec--system--knowledge-visibility.md` | Defines the three classes, the `knowledge_visibility` field, the fallback mapping, the invalid combinations. |
| `knowledge/specs/spec--system--architecture-review.md` | Defines the dual-analysis review workflow and the four-way gap classification. |
| `knowledge/decisions/decision--system--development-visibility-failure.md` | Case note recording the failure mode and the decision rationale. |
| `knowledge/runbooks/runbook--system--development-visibility-migration.md` | Migration runbook for existing Nexus-based projects, including a validation checklist and review smoke tests. |
| `docs/development-visibility-patch-report.md` | This report. |

## Files modified

| Path | Change |
|---|---|
| `knowledge/specs/spec--system--document-frontmatter.md` | Registers `knowledge_visibility` as a recognized extended field; adds example; bumps `updated:`. |
| `knowledge/specs/spec--system--session-bootstrap.md` | Adds STEP 3 ("ACTIVE DESIGN TRACKS") to the bootstrap protocol; bumps `updated:`. |
| `knowledge/index/index--system--project-navigation.md` | Adds the new invariant and specs to the canonical lists; bumps `updated:`. |
| `.claude/hooks/nexus-bootstrap.py` | Injects the STEP 3 "ACTIVE DESIGN TRACKS" block into the bootstrap context emitted at `SessionStart` / `PreCompact`. (Must mirror the spec — see CLAUDE.md drift rule.) |
| `CLAUDE.md` | Adds a "Knowledge Visibility" pointer paragraph referencing the new invariant and specs. |

## Files explicitly NOT modified

- `status` enum in `spec--system--document-frontmatter.md` — unchanged; no breaking change.
- `nexus-prompt-gate.py`, `nexus-tool-gate.py`, `nexus-exit-gate.py` — visibility/review-classification is a content-shape rule; hook-level regex enforcement is not appropriate.
- Any existing draft, roadmap, or proposal — not promoted; not retroactively retagged.
- `legacy-kb/` — out of scope per project policy.

---

## Behavioural change in one line

Before this patch, a review answer to "what specs are missing?" could legitimately list a topic that was already covered by a draft. After this patch, such a finding is INVALID per `invariant--system--review-classification.md` — the agent must classify it as `Exists As Draft` (or one of the other three classes) instead.

---

## Validation performed

The patch itself was applied to the Nexus repository (the source of the template). For each project that consumes Nexus, validation is performed via the migration runbook's Section E checklist and the four review smoke-test prompts.

Repository-level checks for this commit:

1. The new and modified files satisfy `spec--system--document-frontmatter.md`.
2. The new invariant lives in `knowledge/invariants/` and will therefore be auto-loaded at every session bootstrap (per `spec--system--session-bootstrap.md` and `_nexus_common.REQUIRED_INVARIANTS_DIR`).
3. The bootstrap-hook STEP 3 text mirrors the corresponding section in `spec--system--session-bootstrap.md`, satisfying the CLAUDE.md drift rule.
4. No invalid `knowledge_visibility` combinations exist in the patched files.

---

## Rollback

This patch is non-destructive. If reverted:

- the new field has no consumers in existing tooling, so removal is safe;
- the invariant has no effect until reviews are run that respect it;
- existing documents are unchanged and continue to work under the prior model.

To revert: `git revert <commit-sha>` on the patch commit. No data loss.

---

## See also

- `knowledge/decisions/decision--system--development-visibility-failure.md` — case note, alternatives, rationale.
- `knowledge/specs/spec--system--knowledge-visibility.md` — the canonical mechanism.
- `knowledge/specs/spec--system--architecture-review.md` — the canonical workflow.
- `knowledge/invariants/invariant--system--review-classification.md` — the non-negotiable rule.
- `knowledge/runbooks/runbook--system--development-visibility-migration.md` — migration for existing projects.
