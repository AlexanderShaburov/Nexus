# Post-apply prompt — Development Visibility Migration

> **For the operator:** after `apply.sh --apply` finishes successfully and you have run `/hooks` in Claude Code, copy the entire block below (everything inside the `--- BEGIN PROMPT ---` … `--- END PROMPT ---` fences) into Claude Code as a single message.
>
> This is a **read-only first pass**. The agent will inspect, classify, and recommend — it will NOT modify any files. Mutating actions (frontmatter migration, commits) are explicitly out of scope for this pass and require a separate operator-authorized prompt.
>
> Required project state when you run this:
>
> - the Nexus development-visibility patch has been applied (Section A of the migration runbook);
> - hooks have been reloaded via `/hooks`;
> - bootstrap completes cleanly with the STEP 3 ACTIVE DESIGN TRACKS block in the injected context.
>
> Expected runtime: a few minutes of agent reasoning + one report.

---

--- BEGIN PROMPT ---

The Nexus **Development-Phase Knowledge Visibility** patch has just been applied to this project. This is the **first-pass verification and inventory**. Do **not** modify any file in this turn. Do **not** commit. Do **not** promote any draft. Produce only the report described below.

You must follow the existing Nexus lifecycle: complete bootstrap, satisfy the Context Decision Gate, end with the Closure Block. The Closure Block must reflect "code changed: no" and "KB changed: no" because this prompt is read-only.

If the bootstrap injection does NOT contain `STEP 3 — ACTIVE DESIGN TRACKS`, stop and tell me — the patch has not been activated and `/hooks` needs to be re-run.

## Part 1 — Verify the patch installation

Confirm, by reading the relevant files, that each of the following is true. Report a one-line PASS / FAIL for each:

1. The file `knowledge/invariants/invariant--system--review-classification.md` exists with `knowledge_visibility: binding` and `source_of_truth: true`.
2. The file `knowledge/specs/spec--system--knowledge-visibility.md` exists with `knowledge_visibility: binding` and `source_of_truth: true`.
3. The file `knowledge/specs/spec--system--architecture-review.md` exists with `knowledge_visibility: binding` and `source_of_truth: true`.
4. The file `knowledge/decisions/decision--system--development-visibility-failure.md` exists.
5. The file `knowledge/runbooks/runbook--system--development-visibility-migration.md` exists.
6. The file `docs/development-visibility-patch-report.md` exists.
7. `.claude/hooks/nexus-bootstrap.py` contains the literal string `STEP 3 — ACTIVE DESIGN TRACKS`.
8. The current session's bootstrap injection contains `STEP 3 — ACTIVE DESIGN TRACKS` (you should already have observed this; if not, fail this check).
9. `CLAUDE.md` references both `spec--system--knowledge-visibility.md` and `spec--system--architecture-review.md`.
10. `knowledge/index/index--system--project-navigation.md` references both new specs (`Knowledge Visibility`, `Architecture Review`) and the new invariant (`Review Classification`).

If any of checks 1–8 fails, stop after this part and report. Without those, the rest of the prompt is meaningless. Checks 9 and 10 may legitimately fail if the project has heavily customized `CLAUDE.md` or the navigation index and the patch refused them — in that case, continue and explicitly note that Section D of the migration runbook needs manual application.

## Part 2 — Inventory the project's knowledge by visibility class

Walk every Markdown file under `knowledge/`, parse its frontmatter, and classify each document into exactly one of the three visibility classes per `spec--system--knowledge-visibility.md`:

- **Binding** — explicit `knowledge_visibility: binding`, OR fallback (`status: approved` AND `source_of_truth: true`).
- **Historical** — explicit `knowledge_visibility: historical`, OR `status: deprecated`, OR any tag in `{archived, legacy, superseded, historical}`.
- **Development** — everything else (the conservative fallback).

Produce three sections, in this exact order:

```
## Binding State
- <relative path> — <status> — <source_of_truth> — <one-line summary from doc body>
- ...

## Development State
- <relative path> — <status> — <source_of_truth> — <one-line summary>
- ...

## Historical State
- <relative path> — <status> — <source_of_truth> — <one-line summary>
- ...
```

If a class has zero documents, write `(none)` under the heading. Do NOT omit a class.

For each document, also detect and flag any of the **invalid combinations** listed in `spec--system--knowledge-visibility.md` §"Override and Validation Rules". Do not silently normalize; produce a `## Invalid Combinations` section listing them with file path and the contradiction. If there are none, write `(none)`.

## Part 3 — Recommend frontmatter updates

For each document currently classified by the fallback (not by an explicit `knowledge_visibility:` field), recommend whether the explicit field should be added, and if so which value. Group recommendations by class:

```
## Recommended frontmatter additions
### Should declare `knowledge_visibility: binding`
- <path>: reason
- ...

### Should declare `knowledge_visibility: development`
- <path>: reason
- ...

### Should declare `knowledge_visibility: historical`
- <path>: reason
- ...

### Leave as fallback (no change needed)
- <path>: reason
- ...
```

Notes for this part:

- Be conservative. Recommend `binding` ONLY where the document is clearly authoritative AND has `status: approved` AND `source_of_truth: true`. Never recommend promoting a draft.
- Recommend `historical` ONLY where the document is clearly abandoned, superseded, or labelled legacy/archived. Add the suggested body note from the migration runbook §4.3.
- For ambiguous cases (e.g. an old "draft" that may actually still be active), say so explicitly under "Leave as fallback" and ask me for direction.
- Do **not** modify any frontmatter in this pass.

## Part 4 — Architecture-review smoke test

Run a small, real architecture review against this project, following `spec--system--architecture-review.md` exactly. Produce:

```
## Architecture Review (smoke test)

### Binding State
<from Part 2, condensed by topic if useful>

### Development State
<from Part 2, condensed by topic if useful>

### Gap Classification
- <finding 1>
  - Class: Truly Missing | Exists As Draft | Exists But Not Normalized | Superseded Gap
  - Evidence: <which binding/development docs were searched; cite paths>
  - Recommendation: <next action>
- <finding 2>
  - ...
```

You MUST produce at least one finding in each class if the project's state plausibly supports it. If a class is genuinely empty (e.g. no superseded docs at all), say so with one line: `- (none observed)`.

This is the moment that verifies the patch actually changed agent behaviour. A response that omits Development State, or that reports "X is missing" without classification, indicates the patch is not fully active.

## Part 5 — Readiness report

End with this exact section:

```
## Readiness Report

- Patch installation:               PASS | FAIL
- Bootstrap STEP 3 visible:         PASS | FAIL
- CLAUDE.md references new specs:   PASS | FAIL | MANUAL NEEDED
- Index references new entries:     PASS | FAIL | MANUAL NEEDED
- Inventory completed:              PASS | FAIL
- No invalid frontmatter combos:    PASS | FAIL
- Smoke test produced dual analysis: PASS | FAIL
- Smoke test classified all findings: PASS | FAIL

Project is READY / NOT READY for manual frontmatter migration (Section C of
runbook--system--development-visibility-migration.md) and the subsequent
commit.

If NOT READY, the blocking items are: <list of FAIL items>
```

## What you must NOT do in this pass

- Do not modify any file.
- Do not commit.
- Do not promote any document from `development` to `binding`.
- Do not set `source_of_truth: true` on any document.
- Do not delete or move any document.
- Do not skip the smoke test in Part 4 — it is the only check that confirms behavioural activation.
- Do not "fix" invalid frontmatter combinations silently — report them.

Begin.

--- END PROMPT ---

---

## What to do with the agent's report

1. **All PASS:** the project is ready for manual frontmatter migration (Section C of `knowledge/runbooks/runbook--system--development-visibility-migration.md`). Author a follow-up prompt authorizing the agent to apply the recommended frontmatter additions, then commit.
2. **Patch checks FAIL (1–8):** the patch has not landed correctly. Re-run `apply.sh --apply`, then re-run `/hooks`, then re-run this prompt.
3. **CLAUDE.md or index "MANUAL NEEDED":** the apply script refused those two files because of project-local customization. Follow Section D of the migration runbook manually for those files, then re-run this prompt.
4. **Smoke test FAIL:** the patch is installed but the agent did not execute the dual analysis. Confirm `/hooks` was run AFTER `apply.sh --apply` (not before). If the failure persists, file an issue against the patch upstream.
5. **Invalid combinations found:** resolve each one explicitly (per `spec--system--knowledge-visibility.md`) before proceeding to migration. Do not auto-normalize.

---

## Provenance

This prompt corresponds to the `development-visibility` patch bundle, version `1.1.0`. It is read-only: it must never instruct the agent to modify files. Mutating prompts for the migration's Section C are a separate, deliberate operator action.
