---
type: spec
scope: system
status: approved
created: 2026-04-17
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
tags: [frontmatter, metadata, kb-system, feedback, plan-status]
---

## Relations

- constrains:
  - [Knowledge Vault Specification](spec--system--knowledge-vault.md) — every vault document must satisfy this contract.
- relates_to:
  - [Knowledge Graph Relations Specification](spec--system--knowledge-graph-relations.md) — relation declarations sit alongside frontmatter on every document.

---

# Document Frontmatter Specification

## Purpose

This document defines the **standardized YAML frontmatter structure** used across all knowledge base documents.

Frontmatter is a **mandatory control layer** for every document and is used for:
- classification
- routing
- validation
- lifecycle management
- knowledge synchronization

---

## Format

All documents MUST begin with a YAML frontmatter block:

```yaml
---
type: <string>
scope: <string>
status: <string>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
source_of_truth: <boolean>
tags: [<tag1>, <tag2>, ...]
---
```

---

## Fields Specification

### type (required)

Defines the document category. It MUST match the semantic role of the directory the document lives in (see `spec--system--knowledge-vault.md`).

Allowed values, with their canonical directory:

| `type` | Directory | Role |
|---|---|---|
| `architecture` | `architecture/` | structural description — what exists |
| `bug` | `bugs/` | defect record |
| `decision` | `decisions/`, `business/` | rationale for a choice (ADRs use this type) |
| `feedback` | `feedback/` | observation about the Nexus system made in a host project, for delivery upstream (contract: `spec--system--feedback-channel.md`) |
| `glossary` | `glossary/` | domain terminology |
| `index` | `index/` | routing entry point |
| `invariant` | `invariants/` | non-negotiable constraint |
| `pattern` | `patterns/` | reusable approach |
| `plan` | `plans/` | in-progress intent, roadmap |
| `prompt` | `runbooks/` | preserved generative prompt (historical origin material) |
| `question` | `open-questions/` | unresolved question |
| `runbook` | `runbooks/` | operational procedure |
| `session` | `sessions/` | execution trace or session summary |
| `spec` | `specs/` | behavioral contract |

A `type` value outside this list is a validation error. Adding one requires an update to this spec **and** to the directory roles in `spec--system--knowledge-vault.md` — the two lists are a single contract and MUST NOT drift.

---

### scope (required)

Defines the domain or subsystem.

Examples:
- system
- nexus — reserved for `type: feedback`: the subject is the Nexus system itself, observed from a host
- backend
- frontend
- editor
- infrastructure
- domain-specific (project-defined)

---

### status (required)

Defines lifecycle state (workflow maturity — orthogonal to `knowledge_visibility`).

Allowed values:
- draft
- in-progress
- review
- approved
- deprecated

This enum is deliberately closed and free of synonyms. In particular:

| Do NOT use | Use instead | Why |
|---|---|---|
| `accepted` | `approved` | same state, one spelling |
| `archived` | `deprecated` | same state; pair with `knowledge_visibility: historical` |

---

### created (required)

Format: `YYYY-MM-DD`.

Represents initial creation date.

---

### updated (required)

Format: `YYYY-MM-DD`.

Must be updated on every meaningful change. MUST NOT be earlier than `created`.

---

### Date format for machine-generated documents

Documents written by a hook MAY use a full ISO 8601 local timestamp, `YYYY-MM-DDTHH:MM:SS`, for `created` and `updated`. This applies to `type: session` archives produced by `nexus-session-writer.py`, which are rewritten several times a day: a date alone would discard the ordering information.

Hand-authored documents MUST use plain `YYYY-MM-DD`.

---

### source_of_truth (required)

Boolean.

- true → canonical document
- false → derived/supporting document

---

### tags (optional but recommended)

List of keywords.

Used for:
- search
- grouping
- cross-linking

---

### knowledge_visibility (optional but recommended; extension field)

Defines the **review-visibility class** of the document — orthogonal to `status` (workflow maturity) and `source_of_truth` (authoritative status).

Allowed values:
- binding — implementation-binding, authoritative.
- development — active design work; not authoritative, but MUST be visible to architecture review, gap analysis, roadmap planning, and missing-spec analysis.
- historical — superseded, archived, or legacy; excluded from review by default.

When omitted, a conservative fallback applies (see `spec--system--knowledge-visibility.md` §"Fallback Mapping").

Invalid combinations (e.g. `knowledge_visibility: binding` with `source_of_truth: false`) MUST be flagged as errors and MUST NOT be silently normalized. Full rules: `spec--system--knowledge-visibility.md`.

---

### Registered extension fields (optional)

Rule 3 below forbids unknown fields. These are the fields registered so far beyond the required set. Any other field is a validation error until it is added here.

| Field | Applies to | Written by | Meaning |
|---|---|---|---|
| `knowledge_visibility` | any document | agent | review-visibility class; see above |
| `theme` | `type: session`, and any document produced under a themed working session | `nexus-session-writer.py`, agent | working-session theme slug, mirroring `.nexus/session-theme.txt`; groups documents belonging to one line of work |
| `session_id` | `type: session` | `nexus-session-writer.py` | Claude Code session identifier the archive was generated from |
| `governs` | `type: spec` | agent | list of subsystems or concerns the spec has authority over |
| `plan_status` | `type: plan` only | agent | execution lifecycle of the planned work; see below |
| `kind` | `type: feedback` only (required) | agent | `bug`, `wish` or `praise` |
| `nexus_version` | `type: feedback` only (required) | agent | Nexus version installed in the host when the note was written (`unknown` before a baseline exists) |
| `host` | `type: feedback` only (required) | agent | kebab-case name of the host project |
| `touches` | `type: feedback` only | agent | list of Nexus-owned paths the note is about |
| `delivered` | `type: feedback` only | `tools/nexus-update.py feedback push` | list of delivery receipts (`inbox:<timestamp>`, `issue:#<n>`); empty until delivered |

Fields written by a hook are **machine-owned**: do not hand-edit them, and do not remove them when editing the document body. Using a `type: feedback` field on any other type is a validation error (`FB004`); a feedback note also has a fixed body shape (three H2 sections), defined and validated per `spec--system--feedback-channel.md`.

#### `plan_status` — why it is a separate field

`spec--system--knowledge-driven-task-orchestration.md` §"Planning Artifacts" requires every plan to carry an explicit status from `proposed | in_progress | implemented | rejected | superseded`. None of those are in the `status` enum, and they should not be: the two fields answer different questions.

- **`status`** — maturity of *the document*. Has this plan been reviewed and accepted as a plan? (`draft` → `approved`.)
- **`plan_status`** — lifecycle of *the work the plan describes*. Has it been started, finished, abandoned? (`proposed` → `in_progress` → `implemented`.)

They move independently. An approved plan whose work has not begun is `status: approved`, `plan_status: proposed`. A draft plan someone already started executing is `status: draft`, `plan_status: in_progress`.

Allowed values: `proposed`, `in_progress`, `implemented`, `rejected`, `superseded` (underscores, matching the orchestration spec). The validator rejects any other value (`PS001`) and the field on any other type (`PS002`).

SHOULD be present on every `type: plan` document; its absence is a warning (`PS100`), not an error, so existing plans stay valid. `rejected` and `superseded` normally pair with `status: deprecated` and `knowledge_visibility: historical`.

> Provenance: contributed by the Liquid_Nexus host on 2026-09-22, the first change to travel from a host back into the template. Closing the `status` enum had made the orchestration spec's requirement unsatisfiable; two agents hit it independently the same day (one worked around it with a "Plan status:" line in the body). Resolved here.

---

## Rules

1. Frontmatter MUST be present in every document.
2. Field names are case-sensitive.
3. Unknown fields are not allowed unless registered under "Registered extension fields" above.
4. Dates must follow ISO format.
5. source_of_truth must be explicitly set.
6. The frontmatter block MUST be valid YAML. In particular, list values use `-` items or inline `[a, b]` — a `*`-bulleted list is not YAML and MUST be rejected.
7. `type` MUST agree with the document's directory per the table above, and with the filename prefix.

---

## Validation Rules

A document is considered valid if:

- All required fields are present
- All values match allowed formats
- `type` and `status` values are valid enums
- `type` agrees with the directory and the filename prefix
- No unregistered fields are present
- The block parses as YAML
- `knowledge_visibility`, if present, does not form an invalid combination (see `spec--system--knowledge-visibility.md` §"Override and Validation Rules")

---

## Filename Contract

The naming convention is normatively defined in `spec--system--knowledge-vault.md` §"Naming Convention":

```
<type>--<scope>--<name>.md
```

Two document classes carry additional trailing segments, because they are generated per occurrence rather than authored once:

| Form | Used by | Example |
|---|---|---|
| `session--<theme>--<YYYY-MM-DD>--<session-id8>.md` | `nexus-session-writer.py` (automatic) | `session--framing-reset--2026-09-22--55345906.md` |
| `summary--<theme>--<YYYY-MM-DD>.md` | hand-written session handoff summaries | `summary--framing-reset--2026-09-21.md` |

Both carry `type: session`. The `summary--` prefix is an intentional exception to rule 7: it marks a human-authored summary as distinct from a machine-generated transcript sharing the same `type`. Validation tooling MUST accept these two forms.

### Registered prefix exceptions

Rule 7 requires the filename prefix to equal `type`. The following prefixes are registered exceptions; any other mismatch is a validation error.

| Prefix | `type` | Why |
|---|---|---|
| `summary--` | `session` | distinguishes a hand-written handoff summary from a generated transcript |
| `adr--` | `decision` | preserved on `adr--system--rename-soki-to-nexus.md` only. The filename is cited as a historical artefact by `runbook--system--phase2-nexus-migration.md`; renaming would break eight inbound references for no semantic gain. **Not** a licence for new `adr--` documents — new decision records use `decision--`. |

---

## Extension Policy

Additional fields may be introduced only via:
- system-level spec update
- or project-level extension spec

---

## Example

```yaml
---
type: spec
scope: system
status: approved
created: 2026-04-17
updated: 2026-04-17
source_of_truth: true
knowledge_visibility: binding
tags: [frontmatter, metadata, kb-system]
---
```

### Example with development visibility

```yaml
---
type: plan
scope: system
status: draft
created: 2026-06-04
updated: 2026-06-04
source_of_truth: false
knowledge_visibility: development
tags: [roadmap, draft]
---
```

---

## Notes

Frontmatter is not optional metadata.

It is a **structural contract** that enables the knowledge-driven workflow.
