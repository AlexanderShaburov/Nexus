---
type: plan
scope: system
status: draft
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: development
theme: nexus-self-update
tags: [plan, feedback, hosts, inbox, upstream, knowledge-vault]
---

## Relations

- depends_on:
  - [Document Frontmatter Specification](../specs/spec--system--document-frontmatter.md) — the new `feedback` document type must be registered there; the enum is closed.
  - [Knowledge Vault Specification](../specs/spec--system--knowledge-vault.md) — the new `knowledge/feedback/` directory needs a semantic role there; the two lists are one contract.
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — the notifier and the CLI this plan extends.
- relates_to:
  - [Plan: Nexus self-update](plan--system--nexus-self-update.md) — the core freeze (§7.2a there) is what makes a return path necessary; the cache directory and `tools/nexus-update.py` are shared.
  - [Knowledge-Driven Task Orchestration Specification](../specs/spec--system--knowledge-driven-task-orchestration.md) — feedback notes are the Sync obligation pointed at the wrong vault: knowledge about Nexus that a host cannot write into Nexus.

---

# Plan: Nexus feedback channel (hosts → template)

Plan status: **proposed** (operator asked for the design on 2026-09-22 after agreeing to freeze the Nexus core in hosts; nothing is implemented).

---

## 1. Problem

Nexus is under development and will stay so. Agents working inside a host project meet its rough edges first. Until now the fix was made in place, in the host's copy of a system file, which is how Liquid_Nexus diverged from the template. With the core frozen in hosts (`plan--system--nexus-self-update.md` §7.2a) that path is closed on purpose, so a replacement path is required, under two constraints set by the operator:

1. Hosts get **read-only** access to the Nexus repository. Never push rights.
2. Nexus must not keep a registry of host repositories and go looking; the dependency points one way, hosts know Nexus, Nexus does not know hosts.

---

## 2. Design in one paragraph

A feedback note is a **vault document** in the host (`knowledge/feedback/feedback--nexus--<slug>.md`), committed with the host, so it is durable and versioned regardless of delivery. Delivery is a separate, pluggable step. The default transport is a **local mailbox** in the cache directory the updater already maintains on the machine: hosts push copies there, and a session started in the template repository is told at bootstrap how many notes are waiting. No network, no credentials, no host registry. A second transport, GitHub issues, is specified but deferred until a host lives on another machine.

---

## 3. The note

### 3.1 Location and naming

`knowledge/feedback/feedback--nexus--<slug>.md` in the host. `feedback` is a new document type and `feedback/` a new vault directory; both must be added to `spec--system--document-frontmatter.md` (type table, closed enum) and `spec--system--knowledge-vault.md` (directory role), and to `TYPE_DIRS` in `tools/validate-vault.py`, in one change, as the frontmatter spec demands. Scope is `nexus` because the subject is the system, not the host's domain.

Role of the directory: "observations about the Nexus system made while using it in this project; not project knowledge; delivered upstream, never source of truth here". Forbidden: anything about the host's own domain (that belongs to `bugs/`, `open-questions/`, `plans/`).

### 3.2 Frontmatter

```yaml
---
type: feedback
scope: nexus
status: draft            # draft → review (delivered) → approved (accepted upstream) | deprecated (declined)
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: development
kind: bug | wish | praise
nexus_version: 1.0.0     # from .nexus/installed.json; "unknown" before the baseline exists
host: liquid-nexus       # directory basename of the host repository, kebab-case
touches: [.claude/hooks/nexus-tool-gate.py, knowledge/specs/spec--system--exit-gate.md]
delivered: []            # appended by `feedback push`: "inbox:2026-09-22T14:05:00", "issue:#42"
tags: [feedback, nexus, exit-gate]
---
```

`kind`, `nexus_version`, `host`, `touches`, `delivered` are registered extension fields (frontmatter spec §"Registered extension fields"), applying to `type: feedback` only. `delivered` is machine-owned once `feedback push` has written to it.

### 3.3 Body

Free Markdown with three fixed H2 sections the validator checks for `type: feedback`:

- `## What happened` — the situation, quoted hook output or gate denial if any.
- `## What is proposed` — the change wanted upstream; for `praise`, what worked and should not be broken.
- `## Attachment` — optional; a fenced `diff` block produced by `git diff` of the host's unlocked file against the baseline, or "none". The updater's `plan --diff <path>` output pastes here directly. A patch is a **proposal**, applied upstream by an agent after review, never by tooling.

### 3.4 Who writes it

The agent in the host, when: the tool gate denies a core edit (the denial text names this directory); an update leaves a `conflict`; a Nexus behaviour blocks or surprises the work; or the operator asks for a note. Writing a note is ordinary vault writeback: `KB changed: yes`, committed with the host.

---

## 4. Transport A (default): local mailbox

### 4.1 Layout

```
${NEXUS_UPSTREAM_CACHE:-~/.cache/nexus}/
  template/                 # clone used by the updater
  inbox/
    liquid-nexus/
      2026-09-22T14-05-00--feedback--nexus--exit-gate-narration.md
      2026-09-22T14-05-00--feedback--nexus--exit-gate-narration.json   # sidecar: host path, git commit, sha256
    <other-host>/
  inbox-archive/            # notes the template session has processed; moved, never deleted
```

Fixed location, no addresses anywhere: the host writes to a known place, the template reads from a known place. Both sides resolve the same environment variable the updater uses, so a relocated cache moves the mailbox with it.

### 4.2 Host side: `tools/nexus-update.py feedback push`

- Lists `knowledge/feedback/feedback--nexus--*.md` whose `delivered` has no `inbox:` entry, or whose content SHA differs from the last delivered sidecar (edited after delivery → delivered again as a new timestamped copy).
- Copies each into `inbox/<host>/` with a timestamp prefix and writes the sidecar.
- Appends `inbox:<timestamp>` to the note's `delivered` list and bumps `updated:`. This is the only host file it writes.
- `feedback status` lists notes and their delivery state; `feedback push --dry-run` shows what would go.
- Offline-safe by construction: it is a local copy. Missing cache directory → created.

### 4.3 Template side: bootstrap notice

`nexus-update-check.py` (the notifier from the self-update plan, Phase 4) runs in the template repository too. When the project has **no** `.nexus/installed.json` and **has** `nexus.manifest.json` (that is, it *is* the template), it counts files in `inbox/*/` and, if any, emits one line:

`Nexus feedback inbox: 3 notes from liquid-nexus (2), other-host (1). Run python3 tools/nexus-update.py feedback list to read them.`

Silent otherwise. Same guarantees as the update check: exit 0 on every path, no network, well inside the hook timeout.

### 4.4 Template side: triage

`feedback list` prints the inbox as a table (host, kind, nexus_version, touches, title). `feedback show <n>` prints one note. `feedback archive <n>` moves it to `inbox-archive/`; `feedback archive --all-from <host>` likewise. Nothing is deleted.

Acting on a note is agent work under the normal lifecycle: the agent reads the note, changes the template (spec, hook, tool), records a decision if the note is declined, and the change reaches the host with the next update. The note's `status` in the host is set by the host's operator later (`approved` when the fix arrived, `deprecated` when declined), so hosts keep their own history of what they asked for.

### 4.5 What the mailbox does not do

It does not sync two ways, does not notify the host of the outcome (the outcome *is* the next Nexus release), and does not merge notes about the same file. Those are triage, done by a person or an agent in the template session.

---

## 5. Transport B (deferred): GitHub issue

For a host on a machine that does not hold the template cache.

- `feedback push --issue` creates one issue per undelivered note with `gh issue create --title "<kind>: <slug> (from <host>, Nexus <version>)" --body-file <note> --label "feedback,host:<host>,kind:<kind>"`, then appends `issue:#<n>` to `delivered`.
- Required access: read on the repository plus issues write. On GitHub a fine-grained token with `Contents: read` and `Issues: write` gives exactly that; no push rights exist on the token. The operator, who owns both sides, decides whether to mint such a token at all.
- Not built until a host on another machine exists (operator, 2026-09-22: all current hosts are on one machine). Kept in the plan so the note format is not designed in a way that would need changing for it.

Rejected transports: a feedback server (over-engineered for one operator); Nexus scanning host repositories (violates constraint 2); pushing branches to the Nexus repository (violates constraint 1).

---

## 6. Phases

Runs after Phase 4 of the self-update plan, because it borrows the cache directory, the CLI and the notifier.

| Phase | Deliverable | Files | Acceptance |
|---|---|---|---|
| F0 | this proposal | this document | operator review |
| F1 | the document type | `spec--system--document-frontmatter.md` (type `feedback`, five extension fields), `spec--system--knowledge-vault.md` (`feedback/` role), `tools/validate-vault.py` (`TYPE_DIRS`, fixed-section check, `scope: nexus` allowed), one example note in the template under `knowledge/feedback/` marked `status: deprecated` as a fixture | `validate-vault.py --selftest` has fixtures for a valid note, a missing section, an unregistered field; `python3 tools/validate-vault.py` clean |
| F2 | mailbox transport | `feedback push/status/list/show/archive` in `tools/nexus-update.py`; inbox notice in `nexus-update-check.py` | on a throwaway host copy: push delivers, second push is a no-op, edit-then-push delivers again; in the template: the notice appears with one note in the inbox and is silent with none; piping JSON into the hook proves silence when the cache directory is absent |
| F3 | agent guidance | tool-gate denial text names `knowledge/feedback/`; `CLAUDE.md` "How work proceeds here" gains one sentence for hosts; installation guide section "Sending feedback upstream" | a fresh session in a host copy, told to edit a hook, ends with a note in `knowledge/feedback/` instead of an edit |
| F4 | issue transport | `feedback push --issue` | deferred; built when a host lives on another machine |

Vault writeback: the note format becomes `spec--system--feedback-channel.md` when F1 lands (behavioural contract: fields, sections, delivery states); architecture §2d lists the inbox; a `decision--system--nexus-feedback-channel.md` records the two constraints and the rejected transports when this plan is approved.

---

## 7. Decisions (operator, 2026-09-22)

The three questions raised with this proposal were answered as proposed:

1. The inbox notice in the template is shown at **every** session start, not throttled: it is local and cheap, and unread feedback should nag.
2. A note's `status` in the host stays **manual**; the updater may *suggest* "this note's `touches` were just updated" in `apply` output but never marks a note fixed.
3. `praise` notes **are delivered**: knowing what must not break is as useful upstream as knowing what is broken.

Plan status is unchanged (proposed); implementation starts after Phase 4 of the self-update plan.
