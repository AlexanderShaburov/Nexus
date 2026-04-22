---
type: glossary
scope: system
status: approved
created: 2026-04-19
updated: 2026-04-22
source_of_truth: true
tags: [glossary, terminology, canonical]
---

# Terminology Glossary

This document fixes canonical terminology for the Nexus knowledge system. All specs, architecture docs, decisions, plans, index entries, and hook messages MUST use these terms as defined. Drift is a validation failure.

---

## Canonical Terms

### `Nexus` (canonical system name)

The canonical name of the knowledge-driven enforcement system (specs + hooks + lifecycle gates) in this repository. Adopted on 2026-04-22 per `adr--system--rename-soki-to-nexus.md`.

- Use `Nexus` in all new documentation, specs, architecture, and decision documents.
- The first meaningful mention in each active document MAY use the transitional form `Nexus (formerly SOKI)`; subsequent mentions in the same document use just `Nexus`.
- `Nexus` names the *runtime enforcement system*. It does **not** replace `knowledge` (Tier-1 content) or `Knowledge Vault` (Tier-2 structured store). The Knowledge Vault is one component of Nexus.

---

### `knowledge` (lowercase, generic noun)

The information content itself, independent of where it is stored.

- Used as an adjective prefix: `knowledge-driven`, `knowledge-bearing`, `knowledge-sync`.
- Used in generic prose: "project knowledge", "retrieve relevant knowledge", "durable knowledge".
- Not capitalized. No leading article unless the reference is specific.

### `Knowledge Vault` (proper noun, two words, capitalized)

The structured system that stores project knowledge. This is the **canonical name for the system as a whole**.

- Used in spec titles and definitions.
- Used in architecture and decision documents when referring to the system.
- First mention in any document should use the full form `Knowledge Vault`. Subsequent mentions within the same section may use "the vault" as prose shorthand.

### `knowledge/` (code font, filesystem identifier)

The filesystem root directory where all Knowledge Vault artifacts live. Used only for concrete paths.

- Examples: `knowledge/specs/spec--system--knowledge-vault.md`, `knowledge/invariants/…`.

### `KB` (abbreviation, FROZEN)

Canonically expands to **"Knowledge [Vault]"**. Retained unchanged in hook-enforced contract fields to avoid churn across regex, specs, and runtime messages.

Appears in:

- `KB changed: yes/no` — Closure Block field (Exit Gate).
- `KB consult required: YES/NO` — Context Decision Gate field.
- `KB unchanged because …` — Rule 3 justification line.

MUST NOT be renamed to `KV` or expanded inline in those fields unless a formal decision document amends this glossary.

---

## Retired Terms

| Retired term | Replacement | Rationale |
|---|---|---|
| `Knowledge Base` | `Knowledge Vault` (system) or `knowledge` (generic content) | Two names for one entity created search noise and reader uncertainty. |
| `World Structure` (as a system concept name) | `Knowledge Vault structure` | "World" added metaphor without semantic value. |
| `world` (as a standalone system concept) | — (removed; no canonical use) | Previously an orphan term meaning nothing beyond "the Knowledge Vault as a whole". |
| `vault` (as standalone identifier, filename slug, or tag) | `knowledge-vault` or omit | "The vault" as **prose shorthand** is still permitted in Tier-2 context. "vault" as an identifier component is NOT. |

---

## Legacy Aliases

Terms retained for **compatibility during transition**. These are NOT retired and NOT a validation failure — but new documents SHOULD prefer the canonical form.

| Alias | Canonical replacement | Status | Notes |


---

## Register Rules (at a glance)

| Register | Form | Example |
|---|---|---|
| Tier 1 — content | `knowledge` (lowercase) | "retrieve relevant knowledge" |
| Tier 2 — system | `Knowledge Vault` (capitalized) | "The Knowledge Vault is the source of truth." |
| Tier 2 — prose shorthand | `the vault` (lowercase, bare) | "Place documents in the correct vault directory." |
| Tier 3 — implementation | `knowledge/` (code font) | `knowledge/specs/spec--system--knowledge-vault.md` |
| Contract abbreviation | `KB` | `KB changed: yes` |

---

## Enforcement

Terminology is part of the validation contract for any doc written into `knowledge/`:

- No `Knowledge Base` in prose.
- No reference to `spec--system--world-structure.md` — that file was renamed to `spec--system--knowledge-vault.md` on 2026-04-19.
- No filename, slug, tag, or other identifier contains bare `vault` or `world`.
- `KB` stays `KB` in hook-enforced fields.

Prose use of "the vault" as shorthand is acceptable within a section that has already introduced `Knowledge Vault` in full.

---

## See also

- [Knowledge Vault Specification](../specs/spec--system--knowledge-vault.md) — the canonical vault structure spec.
- [Document Frontmatter](../specs/spec--system--document-frontmatter.md) — frontmatter contract.
- [Project Navigation Index](../index/index--system--project-navigation.md) — entry point to the vault.
