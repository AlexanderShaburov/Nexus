---
type: spec
scope: system
status: review
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: development
theme: nexus-self-update
governs: [knowledge/feedback, tools/nexus-update.py feedback]
tags: [spec, feedback, hosts, inbox, upstream]
---

## Relations

- depends_on:
  - [Document Frontmatter Specification](spec--system--document-frontmatter.md) — registers `type: feedback` and its five extension fields.
  - [Knowledge Vault Specification](spec--system--knowledge-vault.md) — defines the `feedback/` directory role.
  - [Nexus Update Specification](spec--system--nexus-update.md) — the core freeze (§6) is why notes exist; the cache directory and CLI are shared.
- relates_to:
  - [Plan: Nexus feedback channel](../plans/plan--system--nexus-feedback-channel.md) — design origin (development class).
  - [Knowledge-Driven Task Orchestration Specification](spec--system--knowledge-driven-task-orchestration.md) — writing a note is the Sync obligation for knowledge about Nexus.

---

# Feedback Channel Specification

## Purpose

Define how a host project records an observation about the Nexus system and how it reaches the template, under two constraints: hosts have **read-only** access to the Nexus repository, and Nexus keeps **no registry** of hosts. The note format (§1–§3) is *realized* and validated; the transports (§4–§5) are specified here and land with the next phase of the plan.

---

## 1. The note

A feedback note is a vault document in the host: `knowledge/feedback/feedback--nexus--<slug>.md`. It is committed with the host like any other document, so it survives whether or not it was ever delivered.

Frontmatter (`type: feedback`, `scope: nexus`, plus the registered fields):

```yaml
---
type: feedback
scope: nexus
status: draft            # draft → review (delivered) → approved (accepted upstream) | deprecated (declined or withdrawn)
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: development
kind: bug                # bug | wish | praise
nexus_version: 1.0.0     # from .nexus/installed.json; "unknown" before a baseline exists
host: liquid-nexus       # directory basename of the host repository, kebab-case
touches: [.claude/hooks/nexus-tool-gate.py]
delivered: []            # receipts appended by `feedback push`: "inbox:<timestamp>", "issue:#<n>"
tags: [feedback, nexus, tool-gate]
---
```

Rules, enforced by `tools/validate-vault.py`:

| Code | Rule |
|---|---|
| `FB001` | `kind`, `nexus_version` and `host` are required |
| `FB002` | `kind` is `bug`, `wish` or `praise` |
| `FB003` | the body carries the three fixed H2 sections of §2 |
| `FB004` | the five feedback fields appear on no other type |
| `FB005` | `touches` and `delivered` are lists |

A note is never `source_of_truth: true` and never `binding`: it proposes, the template decides. `status` in the host is set by the host's operator: `review` once delivered, `approved` when the fix arrived in an update, `deprecated` when declined or withdrawn. Tooling may *suggest* a status change; it never makes one.

---

## 2. Body

Three fixed H2 sections, in this order, each present even when short:

- `## What happened` — the situation; quote the hook output or gate denial when there is one.
- `## What is proposed` — the change wanted upstream; for `praise`, what worked and must not be broken.
- `## Attachment` — a fenced `diff` block, or the word `none`. The diff is a **proposal**: an agent in the template applies it after review; no tool applies it.

Free Markdown may surround them.

---

## 3. Who writes a note, and when

The agent in the host, as ordinary vault writeback (`KB changed: yes`), when:

- the tool gate denies an edit to a Nexus core file (`NEXUS CORE FILE`, `spec--system--nexus-update.md` §6);
- `plan` or `apply` leaves a `conflict`;
- a Nexus behaviour blocks or surprises the work;
- the operator asks for one, including praise.

`nexus_version` comes from `.nexus/installed.json`; `host` from the repository directory name; `touches` from the paths involved.

---

## 4. Transport A — local mailbox (*pending*)

```
${NEXUS_UPSTREAM_CACHE:-~/.cache/nexus}/
  template/                 # the updater's bare clone
  inbox/<host>/<timestamp>--feedback--nexus--<slug>.md   (+ .json sidecar: host path, commit, sha256)
  inbox-archive/            # processed notes; moved, never deleted
```

Host side, `tools/nexus-update.py feedback push`: copies every note without an `inbox:` receipt, or whose content changed since its last receipt, into `inbox/<host>/` with a timestamp prefix and a sidecar; appends `inbox:<timestamp>` to the note's `delivered` and bumps `updated:`. That is the only host file it writes. `feedback status` lists notes and receipts; `--dry-run` shows what would go. No network, no credentials.

Template side: `nexus-update-check.py`, when run where `nexus.manifest.json` exists and `.nexus/installed.json` does not (that is, in the template), counts notes in `inbox/*/` and emits one line at **every** session start (operator decision: unread feedback should nag): `Nexus feedback inbox: N notes from <host> (n), … Run python3 tools/nexus-update.py feedback list to read them.` `feedback list|show|archive` handle triage; nothing is deleted.

Acting on a note is agent work under the normal lifecycle; the outcome reaches the host as the next release.

---

## 5. Transport B — GitHub issue (*deferred*)

`feedback push --issue` creates one issue per undelivered note via `gh issue create` with the note as body and labels `feedback`, `host:<host>`, `kind:<kind>`, then appends `issue:#<n>`. Needs a token with `Contents: read` and `Issues: write`, never push rights. Built only when a host lives on a machine without the template cache.

---

## 6. What the channel is not

Not two-way sync, not a notification of outcome, not a merge tool, not a server, and never a reason for the template to know where hosts live.
