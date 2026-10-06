# process/

What this project is for and where it stands. The vault under `knowledge/` holds what is *known*; this directory holds the project's *charter* and *navigation*, and the coarse-to-fine documents between them.

- `charter.md` — nature of the project, goal, validation policy, planning horizon, definition of done, goal-change policy. Owned by the operator: the agent proposes changes in text and does not edit it.
- `navigation.md` — where the project is now, the one question being tested, why there and now, what is deliberately ignored; then the net of project states and transitions (places, marking, the current transition), uncertainty and validation points. Owned by the agent, updated at closure when the position moves.
- `roadmap--<name>.md`, `iteration--<slug>.md` — the whole road at low resolution, and the one-screen contract of one transition of the net. An iteration exists only for the current transition and at most the next one.

Every document here must read cold: a reader with only `charter.md` and the document itself must understand it.

This directory belongs to the project. Nexus never updates it. Rules, frontmatter and what the runtime reads from here: `knowledge/specs/spec--system--process-space.md`.
