---
type: plan
scope: system
status: review
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: development
tags: [plan, decision-gate, hooks, transcript, claim]
---

## Relations

- depends_on:
  - [Context Decision Gate Specification](../specs/spec--system--context-decision-gate.md) — the contract this plan extends with a second, tool-carried form of the decision.
  - [Overall Structure (Nexus System)](../architecture/architecture--system--overall-structure.md) — the tool gate and state file this plan modifies.
- relates_to:
  - [Lifecycle Gates Invariant](../invariants/invariant--system--lifecycle-gates.md) — the gate stays non-negotiable; only the channel that carries the decision gains an alternative.

---

# Plan: Context Decision claim via tool call

Plan status: **implemented** (approved by the operator on 2026-09-22; implemented and verified the same day in session 0a09f097: the claim was accepted by the live gate in the same session where the text form was being narrated away, and a following Edit passed without a second claim).

## 1. Problem

`nexus-tool-gate.py` finds the Context Decision by reading the assistant text of the current turn from the Claude Code transcript on disk. In Claude Code 2.1.278 (observed with Fable 5.1, sessions 07fc5fdc, 8f40538b and 0a09f097 on 2026-09-22) assistant text written in the same message as a tool call is frequently persisted as a `thinking` block holding a one-sentence paraphrase, not as a `text` block. The regex then has nothing to match and every mutating tool is denied for the whole session, regardless of what the agent writes. The hook is correct for the transcript shape it was designed for; the transcript shape changed underneath it.

Tool calls, by contrast, are persisted verbatim, and the hook receives them directly in `tool_input` without reading the transcript at all.

## 2. Decision

The decision gains a second carrier: a **claim**, which is a Bash call of fixed form and is the first mutating call of the turn.

```
python3 tools/nexus-decide.py --kb YES --reads <vault-doc> [<vault-doc> ...] --reason "<why>"
python3 tools/nexus-decide.py --kb NO --reason "<why the KB is not needed and what risk is accepted>"
```

- The script decides nothing and writes nothing. It validates its arguments and prints the decision to the terminal in the same shape as the text block, so the decision stays visible on screen and lands in the transcript as a tool call.
- The gate recognises the claim from `tool_input.command`, records the decision in `.nexus/state.json` under `turn.decision`, sets `turn.decision_gate_seen`, and lets the call through.
- The text form stays as the **fallback**: when no claim has been seen, the gate still searches the transcript text as before. Environments that persist text normally keep working unchanged, and hosts with an installed Nexus are not broken by the upgrade.
- One decision per turn, as today. Once the flag is set, later mutating calls in the same turn are not re-checked.

Operator decisions recorded 2026-09-22: keep the text fallback (yes); script location `tools/` (yes).

## 3. Recognition rules (mirrored in `_nexus_common.parse_decision_claim`)

- The command is a single line and a single simple command. An optional leading `cd <dir> &&` is tolerated because the Bash tool resets its working directory between calls.
- The script path resolves to `tools/nexus-decide.py` inside the project; a same-named script elsewhere is not a claim.
- After the script path, only `--kb`, `--reason` and `--reads` are accepted. Shell operators (`;`, `&&`, `||`, `|`, redirections), command substitution and backticks anywhere after the script path make the claim malformed and the call is denied.
- `--kb` is `YES` or `NO`, case-insensitive. `--reason` is required, and must be at least 15 characters after trimming, so the stubs the spec calls invalid ("not needed") cannot pass as a reason. `--reads` is required when `--kb YES`; every path must be an existing file under the project.
- A malformed claim is denied with a message naming the defect. A well-formed claim is allowed, and the state records `{kb, reason, reads, via: "claim"}`.

## 4. Files

| File | Change |
|---|---|
| `tools/nexus-decide.py` | new; argument validation and printing only; stdlib only; imports the parser from `.claude/hooks/_nexus_common.py` so there is one parser, not two |
| `.claude/hooks/_nexus_common.py` | `parse_decision_claim_args`, `parse_decision_claim`, `DECISION_CLAIM_SCRIPT` |
| `.claude/hooks/nexus-tool-gate.py` | four-step order: flag set → claim → text fallback → deny; denial text shows both forms |
| `.claude/hooks/nexus-prompt-gate.py` | turn contract names both forms |
| `knowledge/specs/spec--system--context-decision-gate.md` | Decision Trace admits the claim form; recognition rules |
| `knowledge/architecture/architecture--system--overall-structure.md` | tool-gate description, control flow, state shape, Decision Gate grammar |
| `CLAUDE.md` | gate 2 summary |
| `docs/nexus-implementation-report.md` | parser fixtures (S7) and live rows for the claim |

## 5. Rollout order

The hooks govern the session that edits them (see the caution in `docs/nexus-self-update-brief.md` §0).

1. Write `tools/nexus-decide.py` and the parser in `_nexus_common.py` without touching the gate.
2. Feed the gate JSON on stdin for three cases: well-formed claim, malformed claim, plain call with the flag already set. Also run the script directly.
3. Replace `nexus-tool-gate.py` and `nexus-prompt-gate.py`.
4. Update spec, architecture, `CLAUDE.md` and the report in the same commit as the hooks; run `python3 tools/validate-vault.py`.
5. Re-register the `PreToolUse` hook in `.claude/settings.json` (it was removed temporarily to make this work possible) and test live in a fresh session: Bash without a claim is denied, a claim passes, a following Edit passes without a second claim.

## 6. Out of scope, noted

- `nexus-session-writer.py` strips tool calls, so a claim does not appear in the session archive. Rendering claims there is a follow-up.
- While the tool gate is unregistered, nothing records bootstrap reads, so `bootstrap.status` never becomes `completed` and the exit gate demands the confirmation block every turn. Restoring the registration resolves this.
