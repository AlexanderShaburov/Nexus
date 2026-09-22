---
type: spec
scope: system
status: approved
created: 2026-09-22
updated: 2026-09-22
source_of_truth: true
knowledge_visibility: binding
theme: nexus-self-update
governs: [knowledge/feedback, tools/nexus-update.py feedback, .claude/hooks/nexus-update-check.py]
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

Define how a host project records an observation about the Nexus system and how it reaches the template, under two constraints: hosts have **read-only** access to the Nexus repository, and Nexus keeps **no registry** of hosts. The note format (§1–§3) and the local mailbox transport (§4) are realized and tested; the GitHub-issue transport (§5) is specified but deliberately deferred.

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

A host whose `tools/validate-vault.py` predates the release that registered `type: feedback` will see `FM006` / `FM005` from its own validator on the first note. That is the validator being honest, not the note being wrong: update the host first (`apply` delivers the validator in the `tools` group), then write notes. `feedback push` itself only needs the frontmatter parser and works either way.

---

## 4. Transport A — local mailbox (*realized*)

```
${NEXUS_UPSTREAM_CACHE:-${XDG_CACHE_HOME:-~/.cache}/nexus}/
  template/                 # the updater's bare clone
  inbox/<host>/<YYYY-MM-DDTHH-MM-SS>--feedback--nexus--<slug>.md
  inbox/<host>/<same name>.json          # sidecar: host, path, commit, pushed_at, fingerprint, sha256, kind, nexus_version, title, receipt
  inbox-archive/<host>/                  # processed notes; moved with their sidecars, never deleted
```

**Host side**, `tools/nexus-update.py feedback push`:

- A note is **pending** when it has no `inbox:` receipt, when its receipt has no matching sidecar in the mailbox or the archive (cache wiped: deliver again rather than lose it), or when its **fingerprint** differs from the latest sidecar's. The fingerprint is the SHA-256 of the note with the `delivered:` and `updated:` lines removed, so a delivery never makes the next delivery think the note changed.
- Each pending note is copied into `inbox/<host>/` with a timestamp prefix and a sidecar, then the note in the host gets `inbox:<timestamp>` appended to `delivered:` and `updated:` bumped. Those two frontmatter lines are the only thing `push` writes in a host; the rest of the file is byte-identical. The host commits the note afterwards.
- `feedback status` lists every note with its delivery state and reason; `push --dry-run` writes nothing. No network, no credentials, the mailbox directory is created on demand.

**Template side**:

- `nexus-update-check.py`, when run where `nexus.manifest.json` exists and `.nexus/installed.json` does not (that is, in the template), counts `*.md` under `inbox/*/` and emits one line at **every** session start, not throttled (operator decision: unread feedback should nag): `Nexus feedback inbox: N notes from <host> (n), …. Run python3 tools/nexus-update.py feedback list to read them.` Silent when the mailbox is empty or absent. In a host this branch never runs.
- `feedback list` numbers the entries (host, kind, version, pushed_at, title); `--all` includes the archive. `feedback show <n|name>` prints one. `feedback archive <n|name>` or `archive --all-from <host>` moves the note and its sidecar to `inbox-archive/<host>/`. Nothing is ever deleted; archived sidecars still count as delivered for the host.

Acting on a note is agent work under the normal lifecycle: read it, change the template, record a decision if declined, archive it. The outcome reaches the host as the next release; the host's operator then sets the note's `status`.

---

## 5. Transport B — GitHub issue (*deferred*)

`feedback push --issue` creates one issue per undelivered note via `gh issue create` with the note as body and labels `feedback`, `host:<host>`, `kind:<kind>`, then appends `issue:#<n>`. Needs a token with `Contents: read` and `Issues: write`, never push rights. Built only when a host lives on a machine without the template cache.

---

## 6. What the channel is not

Not two-way sync, not a notification of outcome, not a merge tool, not a server, and never a reason for the template to know where hosts live.
