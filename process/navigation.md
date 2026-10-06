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

Position: Per the charter, Nexus has two layers of context. The first layer, knowledge of the project, is done, released as version 1.3.0 and running in several host projects. The second layer, management of the project, is the current change. It is built in this repository only and has reached this point: the layer's rules are written as a draft specification, and both of the layer's documents exist and are agreed (the charter and this navigation). On 2026-10-06 a fresh agent read the two files by hand and stated the position correctly, but could not say why this step and not another; this file gained the `Why here` line in response. The runtime does not read these files yet, and no host has them.

Heading: One question: can two one-screen files, the charter and this navigation, tell a fresh agent where the project is and why it works there? Check: at the start of the next sessions the agent reads both files by hand and states the position and the reason; the operator judges whether both are right. Until that answer exists, the hooks are not touched.

Why here: Everything above this layer assumes that one screen is enough to carry the position. If that is false, the runtime change, the delivery to hosts and the release would be built on the wrong carrier. This is therefore the cheapest check that can invalidate the most. Going deep here is on the critical path; going deep on hooks or validators now is not, because they would read files whose shape is unproven.

Ignoring: Teaching the hooks to read `process/` at session start and on every turn. Machine validation of process file headers. Delivering `process/` to host projects at install. A roadmap for Nexus itself. Anything concerning the hosts' own projects. Each of these waits for the answer to the heading, not for lack of interest.

## Horizon

- The runtime reads `process/` at session start and after context compaction, so the position survives both.
- Host projects receive `process/` at install, as empty templates filled in dialogue.
- A roadmap for Nexus itself, once more than one step ahead is visible.
- A checker for process file headers, like the one the vault has.
- The second layer shipped as the next Nexus version.

## Critical path

1. Confirm that the two files tell a fresh agent where Nexus is and why. ← here
2. Teach the runtime to read them.
3. Run the result in one host project.
4. Release.

## Uncertainty points

- Whether one screen stays enough once the project has more than one line of work.
- Whether the agent keeps this file current without a gate forcing it, or whether it rots.
- Whether the horizon rule stops premature detail, or only moves it into the open-questions folder.
- Whether the charter is stable enough to deserve reading at every session start.
- Whether the agent, having read `Why here`, actually declines work that is off the critical path, or only reports it.

## Validation points

- Start of the next sessions: the agent states the position and the reason from the two files alone; the operator judges. Answers the current heading. First check, 2026-10-06: position right, reason absent; the file was amended.
- After the runtime change: the same check, with no manual reading.
- After the first host: the host's operator can tell where their project is from its navigation alone.
