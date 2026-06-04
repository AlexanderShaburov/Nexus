---
type: runbook
scope: system
status: approved
created: 2026-06-04
updated: 2026-06-04
source_of_truth: true
knowledge_visibility: binding
tags: [runbook, migration, knowledge-visibility, governance]
---

## Relations

- implements:
  - [Knowledge Visibility Specification](../specs/spec--system--knowledge-visibility.md) — operationalizes adoption of the visibility field for existing projects.
  - [Architecture Review Specification](../specs/spec--system--architecture-review.md) — verifies that the dual-analysis review workflow becomes active.
- relates_to:
  - [Review Classification Invariant](../invariants/invariant--system--review-classification.md) — enforces the rule this runbook helps adopt.
  - [Decision: Development-Phase Knowledge Visibility Failure](../decisions/decision--system--development-visibility-failure.md) — the case note that motivates this migration.

---

# Runbook: Development Visibility Migration

## Purpose

Retrofit the **knowledge visibility** mechanism into an existing Nexus-based project so that architecture reviews, gap analysis, roadmap planning, and missing-spec analysis include active development documents (drafts, roadmaps, proposals, in-review specs).

This runbook is for projects that were initialized from an earlier Nexus template (before the visibility patch was added) and now contain drafts, roadmaps, or proposals that are being skipped by review.

> **Target end state:** every document in the project's `knowledge/` vault either carries an explicit `knowledge_visibility` value, or is correctly covered by the fallback mapping. Architecture review responses follow the dual-analysis format (Binding State + Development State + Gap Classification). Local `CLAUDE.md` and bootstrap copies point at the new spec.

All paths are relative to the project's `$CLAUDE_PROJECT_DIR`.

---

## 1. Preconditions

- [ ] `git status` is clean.
- [ ] A feature branch exists: `git checkout -b chore/knowledge-visibility-migration`.
- [ ] The project already uses the Nexus runtime (`.claude/hooks/nexus-*.py` present, `.nexus/` exists).
- [ ] The Nexus repository has been updated to include:
  - `knowledge/specs/spec--system--knowledge-visibility.md`
  - `knowledge/specs/spec--system--architecture-review.md`
  - `knowledge/invariants/invariant--system--review-classification.md`
  - the bootstrap hook STEP 3 ("ACTIVE DESIGN TRACKS") update.
- [ ] Operator has read `specs/spec--system--knowledge-visibility.md` (the three classes, the fallback, the invalid combinations).

---

## 2. Section A — Pull the Nexus Patch into the Project

> **Recommended:** use the executable patch bundle at `patches/development-visibility/` in the upstream Nexus repository. It automates this section AND most of Section D (anchor-based, idempotent, backup-before-modify, refuses on missing anchors). See the bundle's own `README.md`. The bundle does NOT replace Sections B, C, or E — those still require operator judgement.
>
> ```bash
> # from the existing project's root, after copying or unzipping the bundle:
> ./patches/development-visibility/apply.sh --project-root . --apply
> ```
>
> The rest of this section documents the **manual** alternative for operators who prefer not to run the bundle, or who need to handle files the bundle refused (heavily customized `CLAUDE.md` or navigation index).

If the project keeps its own copy of the Nexus runtime (most projects do), pull the three new vault documents and the bootstrap-hook update from the upstream Nexus repository.

Minimum set of files to copy into the project:

| Source (Nexus repo) | Destination (project) |
|---|---|
| `knowledge/specs/spec--system--knowledge-visibility.md` | `knowledge/specs/spec--system--knowledge-visibility.md` |
| `knowledge/specs/spec--system--architecture-review.md` | `knowledge/specs/spec--system--architecture-review.md` |
| `knowledge/invariants/invariant--system--review-classification.md` | `knowledge/invariants/invariant--system--review-classification.md` |
| `.claude/hooks/nexus-bootstrap.py` (STEP 3 block) | merge into project's hook copy |
| `knowledge/specs/spec--system--document-frontmatter.md` (registration of `knowledge_visibility`) | merge into project's copy |
| `knowledge/specs/spec--system--session-bootstrap.md` (ACTIVE DESIGN TRACKS section) | merge into project's copy |
| `knowledge/index/index--system--project-navigation.md` (new entries) | merge into project's copy |

If the project does NOT keep local copies of these system documents (it consumes them via reference), there is no copy to perform — proceed to Section B.

---

## 3. Section B — Inventory Existing Development Work

Identify documents in the project that are currently active design work but are NOT yet authoritative. These are the documents at risk of being invisible to review.

### 3.1 Candidate signals

A document is a likely development-class candidate if **any** of the following hold:

- it lives under `knowledge/plans/` (roadmaps, in-progress intent);
- it lives under `knowledge/sessions/` (design-bearing session notes);
- `status` is `draft`, `in-progress`, or `review`;
- `source_of_truth: false`;
- the body contains words like "draft", "proposal", "in review", "pending", "TBD", "roadmap";
- it is referenced by name from other documents but not yet promoted.

### 3.2 Discovery (suggested commands)

```bash
# Documents with non-approved status
grep -lE '^status:\s*(draft|in-progress|review)\b' knowledge/**/*.md 2>/dev/null

# Documents marked as not source of truth
grep -lE '^source_of_truth:\s*false\b' knowledge/**/*.md 2>/dev/null

# Common development markers in bodies
grep -liE '\b(proposal|roadmap|pending|in[- ]review)\b' knowledge/**/*.md 2>/dev/null
```

Cross-check candidates against the conservative fallback rules in `spec--system--knowledge-visibility.md` to decide whether they really need an explicit `knowledge_visibility: development` declaration.

### 3.3 Decide per document

For each candidate, choose one:

- **Mark as `development`** (explicit) — recommended for any document that the team actively edits or that any review should consider.
- **Leave implicit** — acceptable when the fallback already classifies it as `development` correctly. (Risk: future maintainers may misread its visibility.)
- **Mark as `binding`** — only if the document is truly approved and authoritative. This is a **promotion** decision and MUST be made by a human, not by the agent.
- **Mark as `historical`** — only if the document is actually superseded or abandoned. Add a brief body note explaining why.

---

## 4. Section C — Apply Visibility Markings (Active Existing Projects)

This is the active project's main step. Per-document edits.

### 4.1 For each development-class candidate

Edit the frontmatter:

```yaml
---
type: <unchanged>
scope: <unchanged>
status: <draft | in-progress | review>      # unchanged
created: <unchanged>
updated: <YYYY-MM-DD of this migration>     # bump
source_of_truth: false                       # unchanged or set false
knowledge_visibility: development            # NEW
tags: [..., draft]                           # add 'draft' tag if missing
---
```

### 4.2 For each binding document (already approved + source_of_truth: true)

Optional but recommended — declare the field explicitly:

```yaml
knowledge_visibility: binding
```

This makes the visibility class explicit and removes reliance on the fallback. Only add it if the existing `status` and `source_of_truth` already match the binding rule. Do NOT promote anything in the process.

### 4.3 For each historical / superseded document

If a document was previously implicitly historical (e.g. tagged `legacy`, or `status: deprecated`), declare explicitly:

```yaml
knowledge_visibility: historical
```

Do NOT delete historical documents.

### 4.4 Invalid combinations

If any document ends up with one of the invalid combinations listed in `spec--system--knowledge-visibility.md` (e.g. `knowledge_visibility: binding` with `source_of_truth: false`), **do not silently normalize**. Either:

- correct the visibility value, OR
- correct the workflow state (`status` / `source_of_truth`),

based on what the document actually is. Record the choice in the commit message.

### 4.5 Bump `updated:`

On every edited document, bump the `updated:` field to the migration date.

---

## 5. Section D — Update Project-Local CLAUDE.md / Bootstrap Copies

If the project carries a local copy of any of these files, update them to mention the new mechanism.

### 5.1 Local `CLAUDE.md`

Under the "Mandatory Startup Reading Set" or "Read Priority" section, add a pointer:

```markdown
## Knowledge Visibility (review/gap-analysis)

When performing review, gap-analysis, or roadmap tasks, the agent MUST follow
`knowledge/specs/spec--system--architecture-review.md`:
both Binding State and Development State must be enumerated before any gap is
declared. The visibility classes are defined in
`knowledge/specs/spec--system--knowledge-visibility.md` and the non-negotiable
rule is in `knowledge/invariants/invariant--system--review-classification.md`.
```

### 5.2 Local bootstrap copies

If the project has overridden the bootstrap hook text or maintains its own bootstrap document, mirror the upstream "ACTIVE DESIGN TRACKS" block (STEP 3 of the bootstrap injection):

```
STEP 3 — ACTIVE DESIGN TRACKS (advisory; required when performing review tasks)

These documents are not authoritative, but they MUST be considered during
architecture reviews, gap analysis, roadmap planning, and missing-spec
analysis:

  - knowledge/plans/        — roadmap drafts and in-progress intent
  - knowledge/sessions/     — session-derived design notes
  - any document with status != approved
  - any document with knowledge_visibility: development

See:
  - knowledge/invariants/invariant--system--review-classification.md
  - knowledge/specs/spec--system--architecture-review.md
  - knowledge/specs/spec--system--knowledge-visibility.md
```

### 5.3 Local copies of registered specs

If the project carries local copies of `spec--system--document-frontmatter.md`, `spec--system--session-bootstrap.md`, or `index--system--project-navigation.md`, merge the upstream changes that register `knowledge_visibility` and reference the new specs/invariant.

---

## 6. Section E — Validation Checklist

After migration, walk this checklist. Mark each item explicitly.

### Vault state

- [ ] Every active development document under `knowledge/` has `knowledge_visibility: development` declared explicitly, OR the fallback correctly resolves it to `development`.
- [ ] At least one document in the vault has `knowledge_visibility: binding` declared explicitly (use the upstream system specs as the seed).
- [ ] No document has an invalid combination (see `spec--system--knowledge-visibility.md` §"Override and Validation Rules").
- [ ] Historical / superseded documents are still present (none deleted).

### Bootstrap and agent surface

- [ ] `nexus-bootstrap.py` (or the project's bootstrap hook copy) emits the STEP 3 "ACTIVE DESIGN TRACKS" block.
- [ ] Local `CLAUDE.md` (if present) references the new specs.
- [ ] Local copy of `spec--system--session-bootstrap.md` (if present) carries the ACTIVE DESIGN TRACKS section.

### Review smoke test

Run a fresh Claude Code session against the migrated project. Issue each of the following review prompts in order, and confirm the answer satisfies the listed criterion. **Do not skip this step** — it is the only verification that the patch actually changed agent behaviour.

#### Smoke test prompt 1 — visibility enumeration

> "List all binding documents, all development documents, and all historical documents in the vault."

- [ ] The response distinguishes the three classes.
- [ ] Binding list contains at least the system specs.
- [ ] Development list contains the project's drafts / proposals / roadmaps inventoried in Section B.
- [ ] Historical list contains anything previously deprecated; default exclusion is honoured (i.e. historical documents are NOT mixed into the other two lists).

#### Smoke test prompt 2 — gap analysis

> "What specifications are missing from this project? Use the architecture-review workflow."

- [ ] The response begins with a `## Binding State` section.
- [ ] The response then has a `## Development State` section.
- [ ] The response then has a `## Gap Classification` section.
- [ ] Every finding is classified as one of: `Truly Missing`, `Exists As Draft`, `Exists But Not Normalized`, `Superseded Gap`.
- [ ] No finding says "X is missing" without one of those classifications.
- [ ] Evidence (which documents were searched) is cited for each finding.

#### Smoke test prompt 3 — anti-regression

> "List what should be implemented next."

- [ ] The response does NOT recommend creating a new spec for any topic that already exists as a draft (`Exists As Draft` instead leads to a "complete and promote" recommendation).
- [ ] The response considers development documents, not just binding ones.

#### Smoke test prompt 4 — historical exclusion

> "Review this architecture."

- [ ] Historical / superseded / legacy documents are NOT included in either the binding or development enumeration, unless the user explicitly asked for them.

---

## 7. Section F — Rollback

The migration is non-destructive at the vault level (no deletions). Rollback options:

### Per-document rollback

Revert the frontmatter additions on individual documents. The fallback mapping continues to apply.

### Full rollback

```bash
git checkout main
git branch -D chore/knowledge-visibility-migration
```

The upstream Nexus patch may remain in place (the new specs and the invariant are not destructive even if unused — the invariant simply has no effect until reviews are run that respect it).

---

## 8. Anti-Patterns to Avoid During Migration

- ✗ Promoting drafts to `binding` during the migration. Migration MUST NOT change implementation conformance.
- ✗ Marking drafts as `source_of_truth: true`. Development is not authoritative.
- ✗ Deleting historical documents.
- ✗ Silently normalizing invalid combinations.
- ✗ Skipping the smoke test. The smoke test is the only verification that agent behaviour actually changed.
- ✗ Bulk-applying `knowledge_visibility: development` to every non-approved document without inspection. Some non-approved documents are genuinely abandoned and should be marked `historical`.

---

## 9. Final Success Criteria

- [ ] Section B inventory has been performed and recorded (e.g. in the commit message or a session log).
- [ ] Section C visibility markings applied; `updated:` bumped on every edited document.
- [ ] Section D local bootstrap / CLAUDE.md copies updated.
- [ ] Section E validation checklist fully ticked, including all four smoke-test prompts.
- [ ] Branch committed and PR opened.
- [ ] No invalid frontmatter combinations remain in the vault.
- [ ] No drafts were promoted as a side-effect of migration.
