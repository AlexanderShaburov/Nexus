---
type: bug
scope: system
status: deprecated
created: 2026-10-10
updated: 2026-10-10
source_of_truth: false
knowledge_visibility: historical
theme: progressive-resolution
tags: [bug, session-writer, hooks, stop, archive, rename, fixed]
---

## Relations

- relates_to:
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — §2a describes the session writer and the naming of its archive.
  - [Bug: session writer can miss the last assistant answer of a turn](bug--system--session-writer-last-turn-race.md) — found and fixed together on 2026-10-10.

---

# Bug: a session running past midnight renamed its own archive

**Status: fixed 2026-10-10.**

## Symptom

A session that started on one day and ended on the next had its archive renamed on its last `Stop`: `session--framing-reset--2026-10-09--e5f044cf.md` became `session--framing-reset--2026-10-10--e5f044cf.md`, and the ownership marker `.nexus/session-file.txt` changed with it. The summary document written by hand in the same session named the archive by its old name, which no longer existed. Observed in the Liquid_Nexus host on 2026-10-10 (session started 2026-10-09T16:03, last Stop 2026-10-10T07:22); the next session there noticed the uncommitted rename at bootstrap and reported it.

## Cause, verified

`nexus-session-writer.py` built the filename from `datetime.date.today()` on every `Stop`. The marker lets the writer rename the archive it already owns when the computed name differs from the current one; that path exists for a theme change within a session, and a date change triggered it in exactly the same way. `created:` in the frontmatter was preserved correctly; only the name moved.

## Fix (applied 2026-10-10)

The date segment is set once, at the session's first archive. When the marker names an archive this session owns, the writer takes the date from that filename (`archive_date`), falling back to the `created:` date and only then to today. A theme change still renames the file, with the date kept. The heading `# Session <date>` uses the same date.

## Verification

`python3 .claude/hooks/nexus-session-writer.py --selftest`: an archive dated yesterday with a marker for the same session is updated in place on a run today (one file, name kept, `created:` preserved, marker unchanged); a theme change renames it and keeps the date; a marker left by another session does not affect a new session's archive. The static plan of `docs/nexus-implementation-report.md` §2 is clean after the change.

Archives renamed before the fix are not renamed back; the host's summary reference is the operator's to correct.
