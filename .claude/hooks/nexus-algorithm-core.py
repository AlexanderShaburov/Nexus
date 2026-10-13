#!/usr/bin/env python3
"""Nexus: UserPromptSubmit hook, canonical management algorithm, part 1/2 (§§1–2: definitions and the diagram).

A registration of its own: the updater identifies a hook entry by
`<event>/<nexus-*.py basename>` (spec--system--nexus-update.md §2.2), so one
script registered twice with different arguments is not a unit it can deliver
to a host. The work is done by nexus-management-algorithm.py. Read-only.
"""

import pathlib
import runpy
import sys

sys.argv = [sys.argv[0], "--part", "core"]
runpy.run_path(
    str(pathlib.Path(__file__).resolve().with_name("nexus-management-algorithm.py")),
    run_name="__main__",
)
