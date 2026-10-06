---
type: navigation
status: approved
state: active
owner: agent
created: 2026-10-06
updated: 2026-10-06
---

# Nexus navigation

## Now

Position: Per the charter, Nexus has two layers of context. The first layer, knowledge of the project, is done, released as version 1.3.0 and running in several host projects. The second layer, management of the project, is being introduced now; that is the current change. It is built in this repository only and has reached this point: the layer's rules are written (the process-space specification, a draft), the layer's first document exists and is agreed (the charter), the second is being written (this file). The runtime does not read these files yet, and no host has them.

Heading: One question: can two one-screen files, the charter and this navigation, tell a fresh agent where the project is? Check: at the start of the next few sessions the agent reads both files by hand and states the position; the operator judges whether it is right. Until that answer exists, the hooks are not touched.

Ignoring: Teaching the hooks to read `process/` at session start and on every turn. Machine validation of process file headers. Delivering `process/` to host projects at install. A roadmap for Nexus itself. Anything concerning the hosts' own projects.

## Horizon

- The runtime reads `process/` at session start and after context compaction, so the position survives both.
- Host projects receive `process/` at install, as empty templates filled in dialogue.
- A roadmap for Nexus itself, once more than one step ahead is visible.
- A checker for process file headers, like the one the vault has.
- The second layer shipped as the next Nexus version.

## Critical path

1. Confirm that the two files tell a fresh agent where Nexus is (the current heading).
2. Teach the runtime to read them.
3. Run the result in one host project.
4. Release.

## Uncertainty points

- Whether one screen stays enough once the project has more than one line of work.
- Whether the agent keeps this file current without a gate forcing it, or whether it rots.
- Whether the horizon rule stops premature detail, or only moves it into the open-questions folder.
- Whether the charter is stable enough to deserve reading at every session start.

## Validation points

- Start of the next sessions: the agent states the position from the two files alone; the operator judges. Answers the current heading.
- After the runtime change: the same check, with no manual reading.
- After the first host: the host's operator can tell where their project is from its navigation alone.
