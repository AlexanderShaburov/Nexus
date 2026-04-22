# .nexus/ — Nexus Runtime State

  

This directory holds ephemeral per-session state for the Nexus enforcement hooks. It is regenerated at every `SessionStart` and is not a source of truth.

  

Contents:

- `state.json` — per-session runtime: bootstrap status, read-ledger, turn index, decision-gate flag.

  

Do not edit by hand. Do not check `state.json` into version control (a `.gitignore` entry is provided).

  

If `state.json` is missing or corrupt, the hooks will recreate it with `bootstrap.status = "pending"` on the next `SessionStart`. Force a reset by deleting it.