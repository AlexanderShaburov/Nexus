#!/usr/bin/env python3
"""Apply the Nexus Development Visibility patch to a target project.

Safe by default: dry-run unless --apply is passed. Idempotent: re-running on
an already-patched project is a no-op. Anchor-based surgical edits refuse to
mutate a file when anchors are missing (heavily customized project) — never
corrupts.

Invoked by apply.sh; can also be run directly:

    python3 apply.py --bundle-dir <path> --project-root <path> [--apply]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import pathlib
import re
import shutil
import sys

# ---------------------------------------------------------------------------
# Patch metadata
# ---------------------------------------------------------------------------

PATCH_ID = "development-visibility"
PATCH_VERSION = "1.1.0"
SOURCE_COMMIT = "445dcd0c83f54d0d49d5048cf4f2b6217df2d12f"
PATCH_TITLE = "Development-Phase Knowledge Visibility"
POST_APPLY_PROMPT = "prompts/post-apply-development-visibility-migration.md"

# Files that are entirely new (no upstream version exists in older projects).
# Copied from payload/ verbatim. If the target file exists and matches byte-for-byte
# we skip. If it exists and differs, we back it up and replace.
NEW_FILES = [
    "knowledge/invariants/invariant--system--review-classification.md",
    "knowledge/specs/spec--system--knowledge-visibility.md",
    "knowledge/specs/spec--system--architecture-review.md",
    "knowledge/decisions/decision--system--development-visibility-failure.md",
    "knowledge/runbooks/runbook--system--development-visibility-migration.md",
    "docs/development-visibility-patch-report.md",
]

# ---------------------------------------------------------------------------
# Surgical edits for the 5 modified files
# Each edit:
#   idempotency : string that, if found anywhere in the file, means "already
#                 patched; skip"
#   anchor      : exact string to locate in the file (must match exactly once)
#   mode        : "insert_after" — payload is appended immediately after anchor
#                 "replace"      — anchor is replaced with payload
#   payload     : string to insert / replacement text
#
# Edits are applied in order. If ANY anchor in a file is missing AND the
# idempotency marker is also not present, the file is reported as "refused"
# and left untouched. No partial application.
# ---------------------------------------------------------------------------

EDITS: dict[str, list[dict]] = {

    # ----- CLAUDE.md -----------------------------------------------------------
    "CLAUDE.md": [
        {
            "idempotency": "## Knowledge Visibility (review",
            "anchor": (
                "Use the navigation index (`knowledge/index/index--system--project-navigation.md`) "
                "to locate documents structurally. Grep is a fallback, not a primary lookup."
            ),
            "mode": "insert_after",
            "payload": (
                "\n\n## Knowledge Visibility (review / gap-analysis)\n\n"
                "When performing review-class tasks (\"what specs are missing?\", "
                "\"what gaps remain?\", \"what should be implemented next?\", \"review this "
                "architecture\", \"create a roadmap\"), the agent MUST follow "
                "`knowledge/specs/spec--system--architecture-review.md`: enumerate "
                "**Binding State** AND **Development State** before declaring any gap, and "
                "classify every finding as one of `Truly Missing` / `Exists As Draft` / "
                "`Exists But Not Normalized` / `Superseded Gap`.\n\n"
                "The three visibility classes (binding / development / historical) and the "
                "optional `knowledge_visibility` frontmatter field are defined in "
                "`knowledge/specs/spec--system--knowledge-visibility.md`. The non-negotiable "
                "rule is `knowledge/invariants/invariant--system--review-classification.md` "
                "(auto-loaded at bootstrap).\n\n"
                "Migration for existing Nexus-based projects: "
                "`knowledge/runbooks/runbook--system--development-visibility-migration.md`."
            ),
        },
    ],

    # ----- knowledge/index/index--system--project-navigation.md -----------------
    "knowledge/index/index--system--project-navigation.md": [
        {
            "idempotency": "[Knowledge Visibility]",
            "anchor": "- [Document Frontmatter](../specs/spec--system--document-frontmatter.md) — YAML contract for every doc",
            "mode": "insert_after",
            "payload": (
                "\n- [Knowledge Visibility](../specs/spec--system--knowledge-visibility.md) — "
                "the three review-visibility classes (binding / development / historical) and "
                "the `knowledge_visibility` field"
                "\n- [Architecture Review](../specs/spec--system--architecture-review.md) — "
                "mandatory dual-analysis workflow (Binding State + Development State) and "
                "four-way gap classification"
            ),
        },
        {
            "idempotency": "[Review Classification]",
            "anchor": "- [Lifecycle Gates](../invariants/invariant--system--lifecycle-gates.md) — Bootstrap, Decision Gate, Exit Gate are non-negotiable",
            "mode": "insert_after",
            "payload": (
                "\n- [Review Classification](../invariants/invariant--system--review-classification.md) — "
                "no gap may be reported without examining both binding and development "
                "knowledge; every gap must be classified"
            ),
        },
    ],

    # ----- knowledge/specs/spec--system--document-frontmatter.md ----------------
    "knowledge/specs/spec--system--document-frontmatter.md": [
        # 1) New field section, inserted before "## Rules".
        {
            "idempotency": "### knowledge_visibility (optional",
            "anchor": "- cross-linking\n\n---\n\n## Rules",
            "mode": "replace",
            "payload": (
                "- cross-linking\n\n"
                "---\n\n"
                "### knowledge_visibility (optional but recommended; extension field)\n\n"
                "Defines the **review-visibility class** of the document — orthogonal to "
                "`status` (workflow maturity) and `source_of_truth` (authoritative status).\n\n"
                "Allowed values:\n"
                "- binding — implementation-binding, authoritative.\n"
                "- development — active design work; not authoritative, but MUST be visible "
                "to architecture review, gap analysis, roadmap planning, and missing-spec analysis.\n"
                "- historical — superseded, archived, or legacy; excluded from review by default.\n\n"
                "When omitted, a conservative fallback applies (see "
                "`spec--system--knowledge-visibility.md` §\"Fallback Mapping\").\n\n"
                "Invalid combinations (e.g. `knowledge_visibility: binding` with "
                "`source_of_truth: false`) MUST be flagged as errors and MUST NOT be silently "
                "normalized. Full rules: `spec--system--knowledge-visibility.md`.\n\n"
                "---\n\n"
                "## Rules"
            ),
        },
        # 2) Add development-visibility example after the existing binding example.
        {
            "idempotency": "### Example with development visibility",
            "anchor": (
                "source_of_truth: true\n"
                "tags: [frontmatter, metadata, kb-system]\n"
                "---\n"
                "```"
            ),
            "mode": "replace",
            "payload": (
                "source_of_truth: true\n"
                "knowledge_visibility: binding\n"
                "tags: [frontmatter, metadata, kb-system]\n"
                "---\n"
                "```\n\n"
                "### Example with development visibility\n\n"
                "```yaml\n"
                "---\n"
                "type: plan\n"
                "scope: system\n"
                "status: draft\n"
                "created: 2026-06-04\n"
                "updated: 2026-06-04\n"
                "source_of_truth: false\n"
                "knowledge_visibility: development\n"
                "tags: [roadmap, draft]\n"
                "---\n"
                "```"
            ),
        },
    ],

    # ----- knowledge/specs/spec--system--session-bootstrap.md -------------------
    "knowledge/specs/spec--system--session-bootstrap.md": [
        {
            "idempotency": "STEP 3 — ACTIVE DESIGN TRACKS",
            "anchor": (
                "All invariants MUST be treated as non-negotiable constraints.\n\n"
                "------------------------------------------------------------------------\n\n"
                "## Operational Mode"
            ),
            "mode": "replace",
            "payload": (
                "All invariants MUST be treated as non-negotiable constraints.\n\n"
                "------------------------------------------------------------------------\n\n"
                "## STEP 3 — ACTIVE DESIGN TRACKS (advisory; required when performing review tasks)\n\n"
                "Before performing **architecture review**, **gap analysis**, **roadmap\n"
                "planning**, or **missing-spec analysis**, the agent MUST also discover and\n"
                "consider documents in the **development** visibility class. These documents\n"
                "are **not** authoritative, but they must be visible to review so that\n"
                "already-drafted work is not reported as missing.\n\n"
                "Sources of development-class documents:\n\n"
                "-   `knowledge/plans/` — roadmap drafts and in-progress intent.\n"
                "-   `knowledge/sessions/` — session-derived design notes.\n"
                "-   any document with `status` of `draft`, `in-progress`, or `review`.\n"
                "-   any document with `knowledge_visibility: development`.\n\n"
                "Workflow contract for review tasks:\n\n"
                "-   `knowledge/specs/spec--system--architecture-review.md` — mandatory dual\n"
                "    analysis (Binding State + Development State) with four-way gap\n"
                "    classification.\n\n"
                "Non-negotiable rule:\n\n"
                "-   `knowledge/invariants/invariant--system--review-classification.md` — no\n"
                "    gap may be reported without examining both binding and development\n"
                "    knowledge.\n\n"
                "Classification mechanism:\n\n"
                "-   `knowledge/specs/spec--system--knowledge-visibility.md` — the three\n"
                "    visibility classes and the fallback mapping.\n\n"
                "This step is advisory at session start (it does not block bootstrap\n"
                "completion), but it is **required** whenever a review-class task is\n"
                "triggered. The Mandatory Startup Reading Set above is unchanged; this\n"
                "section names additional discovery the agent owes the review surface.\n\n"
                "------------------------------------------------------------------------\n\n"
                "## Operational Mode"
            ),
        },
    ],

    # ----- .claude/hooks/nexus-bootstrap.py -------------------------------------
    ".claude/hooks/nexus-bootstrap.py": [
        {
            "idempotency": "STEP 3 — ACTIVE DESIGN TRACKS",
            "anchor": (
                '        "  ---",\n'
                '        "",\n'
                '        "ENFORCEMENT:",'
            ),
            "mode": "replace",
            "payload": (
                '        "  ---",\n'
                '        "",\n'
                '        "STEP 3 — ACTIVE DESIGN TRACKS (advisory; REQUIRED when performing review tasks)",\n'
                '        "",\n'
                '        "Before performing architecture review, gap analysis, roadmap planning, or",\n'
                '        "missing-spec analysis, you MUST discover and consider documents in the",\n'
                '        "\'development\' visibility class. These documents are NOT authoritative,",\n'
                '        "but they MUST be visible to review so that already-drafted work is not",\n'
                '        "reported as missing.",\n'
                '        "",\n'
                '        "Sources of development-class documents:",\n'
                '        "  - knowledge/plans/        — roadmap drafts and in-progress intent",\n'
                '        "  - knowledge/sessions/     — session-derived design notes",\n'
                '        "  - any document with status of draft, in-progress, or review",\n'
                '        "  - any document with knowledge_visibility: development",\n'
                '        "",\n'
                '        "Required workflow contract:",\n'
                '        "  - knowledge/specs/spec--system--architecture-review.md",\n'
                '        "      → mandatory dual analysis (Binding State + Development State)",\n'
                '        "      → four-way gap classification:",\n'
                '        "        Truly Missing | Exists As Draft | Exists But Not Normalized | Superseded Gap",\n'
                '        "",\n'
                '        "Non-negotiable rule:",\n'
                '        "  - knowledge/invariants/invariant--system--review-classification.md",\n'
                '        "      → no gap may be reported without examining BOTH binding AND",\n'
                '        "        development knowledge.",\n'
                '        "",\n'
                '        "Classification mechanism:",\n'
                '        "  - knowledge/specs/spec--system--knowledge-visibility.md",\n'
                '        "      → defines the three classes (binding / development / historical),",\n'
                '        "        the fallback mapping, and the invalid combinations.",\n'
                '        "",\n'
                '        "ENFORCEMENT:",'
            ),
        },
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sha256_of(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def looks_like_nexus_project(project: pathlib.Path) -> list[str]:
    """Return list of missing required artifacts; empty list = looks like a Nexus project."""
    guards = [
        project / ".claude" / "hooks" / "nexus-bootstrap.py",
        project / ".nexus",
        project / "knowledge",
    ]
    return [str(p.relative_to(project)) for p in guards if not p.exists()]


def backup_file(path: pathlib.Path, project: pathlib.Path, backup_dir: pathlib.Path) -> None:
    rel = path.relative_to(project)
    dst = backup_dir / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst)


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


def apply_new_files(
    bundle: pathlib.Path,
    project: pathlib.Path,
    backup_dir: pathlib.Path,
    apply_changes: bool,
    results: dict,
) -> int:
    rc = 0
    for rel in NEW_FILES:
        src = bundle / "payload" / rel
        dst = project / rel
        if not src.is_file():
            print(f"  [ERROR] bundle payload missing: {src}", file=sys.stderr)
            results["errors"].append(f"missing payload: {rel}")
            rc = 3
            continue

        if dst.exists():
            if dst.read_bytes() == src.read_bytes():
                print(f"  [skip-identical]    {rel}")
                results["new_skipped_identical"].append(rel)
                continue
            verb = "replaced" if apply_changes else "WOULD REPLACE"
            print(f"  [{verb}]    {rel}    (backup: {backup_dir.relative_to(project)})")
            if apply_changes:
                backup_file(dst, project, backup_dir)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            results["new_replaced"].append(rel)
        else:
            verb = "created" if apply_changes else "WOULD CREATE"
            print(f"  [{verb}]     {rel}")
            if apply_changes:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            results["new_created"].append(rel)
    return rc


def apply_edits(
    project: pathlib.Path,
    backup_dir: pathlib.Path,
    apply_changes: bool,
    results: dict,
) -> int:
    rc = 0
    for rel, edits in EDITS.items():
        path = project / rel
        if not path.is_file():
            print(f"  [ERROR] target missing:  {rel}", file=sys.stderr)
            results["errors"].append(f"missing target: {rel}")
            rc = 3
            continue

        text = path.read_text()

        # Idempotency: if ANY edit's marker is already present, treat the whole file as done.
        if any(e["idempotency"] in text for e in edits):
            print(f"  [skip-idempotent]   {rel}    (already patched)")
            results["edits_skipped_idempotent"].append(rel)
            continue

        new_text = text
        failed = False
        for e in edits:
            if e["anchor"] not in new_text:
                print(f"  [REFUSED]           {rel}    (anchor not found; manual patch needed)")
                results["edits_refused"].append(rel)
                failed = True
                break
            if new_text.count(e["anchor"]) > 1:
                print(f"  [REFUSED]           {rel}    (anchor matched {new_text.count(e['anchor'])} times; manual patch needed)")
                results["edits_refused"].append(rel)
                failed = True
                break
            if e["mode"] == "insert_after":
                new_text = new_text.replace(e["anchor"], e["anchor"] + e["payload"], 1)
            elif e["mode"] == "replace":
                new_text = new_text.replace(e["anchor"], e["payload"], 1)
            else:
                print(f"  [ERROR] unknown mode '{e['mode']}' for {rel}", file=sys.stderr)
                results["errors"].append(f"bad mode: {rel}")
                failed = True
                rc = 4
                break
        if failed:
            continue

        verb = "patched" if apply_changes else "WOULD PATCH"
        print(f"  [{verb}]    {rel}")
        if apply_changes:
            backup_file(path, project, backup_dir)
            path.write_text(new_text)
        results["edits_applied"].append(rel)

    if results["edits_refused"]:
        rc = max(rc, 1)
    return rc


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


_FM_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(path: pathlib.Path) -> dict[str, str]:
    text = path.read_text()
    m = _FM_PATTERN.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def validate(project: pathlib.Path) -> bool:
    ok = True

    hook = (project / ".claude/hooks/nexus-bootstrap.py").read_text()
    if "STEP 3 — ACTIVE DESIGN TRACKS" in hook:
        print("  OK: bootstrap hook contains STEP 3")
    else:
        print("  FAIL: bootstrap hook missing STEP 3 (expected after apply)")
        ok = False

    expected = {
        "knowledge/invariants/invariant--system--review-classification.md": ("binding", "true"),
        "knowledge/specs/spec--system--knowledge-visibility.md":             ("binding", "true"),
        "knowledge/specs/spec--system--architecture-review.md":              ("binding", "true"),
        "knowledge/decisions/decision--system--development-visibility-failure.md": ("binding", "true"),
        "knowledge/runbooks/runbook--system--development-visibility-migration.md": ("binding", "true"),
    }
    for rel, (exp_vis, exp_sot) in expected.items():
        p = project / rel
        if not p.is_file():
            print(f"  FAIL: missing {rel}")
            ok = False
            continue
        fm = _parse_frontmatter(p)
        if fm.get("knowledge_visibility") != exp_vis:
            print(f"  FAIL: {rel}  knowledge_visibility={fm.get('knowledge_visibility')} (expected {exp_vis})")
            ok = False
            continue
        if fm.get("source_of_truth") != exp_sot:
            print(f"  FAIL: {rel}  source_of_truth={fm.get('source_of_truth')} (expected {exp_sot})")
            ok = False
            continue
        print(f"  OK: {rel}")

    claude = (project / "CLAUDE.md").read_text()
    if ("spec--system--knowledge-visibility.md" in claude
            and "spec--system--architecture-review.md" in claude):
        print("  OK: CLAUDE.md references new specs")
    else:
        print("  WARN: CLAUDE.md does not reference new specs "
              "(may have been heavily customized; see manual section in migration runbook)")

    return ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="apply.py",
        description=f"Apply the Nexus '{PATCH_ID}' patch to a target project (dry-run by default).",
    )
    p.add_argument("--bundle-dir", required=True, help="path to the patch bundle directory")
    p.add_argument("--project-root", required=True, help="path to the target project root")
    p.add_argument("--apply", action="store_true", help="actually apply (default: dry-run)")
    p.add_argument("--force", action="store_true",
                   help="skip the 'looks like a Nexus project' guard")
    p.add_argument("--backup-dir", default=None,
                   help="override backup directory (default: .nexus/backups/<patch>-<ts>)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    bundle = pathlib.Path(args.bundle_dir).resolve()
    project = pathlib.Path(args.project_root).resolve()

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== Nexus patch: {PATCH_TITLE} ===")
    print(f"  patch id:       {PATCH_ID}")
    print(f"  patch version:  {PATCH_VERSION}")
    print(f"  source commit:  {SOURCE_COMMIT}")
    print(f"  bundle:         {bundle}")
    print(f"  project root:   {project}")
    print(f"  mode:           {mode}")
    print()

    missing = looks_like_nexus_project(project)
    if missing and not args.force:
        print("ERROR: target does not look like a Nexus project. Missing:", file=sys.stderr)
        for p in missing:
            print(f"  - {p}", file=sys.stderr)
        print("Use --force to override (NOT recommended).", file=sys.stderr)
        return 2

    backup_dir = (
        pathlib.Path(args.backup_dir).resolve()
        if args.backup_dir
        else project / ".nexus" / "backups" / f"{PATCH_ID}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )

    results: dict[str, list[str]] = {
        "new_created": [],
        "new_replaced": [],
        "new_skipped_identical": [],
        "edits_applied": [],
        "edits_skipped_idempotent": [],
        "edits_refused": [],
        "errors": [],
    }

    print("--- new files ---")
    rc1 = apply_new_files(bundle, project, backup_dir, args.apply, results)

    print()
    print("--- surgical edits ---")
    rc2 = apply_edits(project, backup_dir, args.apply, results)

    rc = max(rc1, rc2)

    if args.apply:
        print()
        print("--- post-apply validation ---")
        if not validate(project):
            print("VALIDATION FAILED — review report above", file=sys.stderr)
            rc = max(rc, 5)

    print()
    print("=== summary ===")
    print(f"  mode:                            {mode}")
    print(f"  new files created:               {len(results['new_created'])}")
    print(f"  new files replaced (backed up):  {len(results['new_replaced'])}")
    print(f"  new files identical (skipped):   {len(results['new_skipped_identical'])}")
    print(f"  edits applied:                   {len(results['edits_applied'])}")
    print(f"  edits skipped (already applied): {len(results['edits_skipped_idempotent'])}")
    print(f"  edits refused (manual needed):   {len(results['edits_refused'])}")
    print(f"  errors:                          {len(results['errors'])}")
    if args.apply and (results["new_created"] or results["new_replaced"] or results["edits_applied"]):
        print(f"  backup directory:                {backup_dir}")
    print()

    if mode == "DRY-RUN":
        print("This was a DRY-RUN. Re-run with --apply to actually modify files.")
    elif results["edits_refused"]:
        print("Some edits were REFUSED. Follow the manual section of")
        print("  knowledge/runbooks/runbook--system--development-visibility-migration.md")
        print("for the files listed above.")
    elif results["errors"]:
        print("Errors occurred during apply. See messages above.")
    else:
        print("Patch applied successfully.")
        print()
        print("Next steps:")
        print("  1. In Claude Code, run:  /hooks")
        print("     (reloads hook configuration; required for STEP 3 to take effect)")
        print(f"  2. Paste the post-apply verification prompt into Claude Code:")
        print(f"     {(pathlib.Path(args.bundle_dir) / POST_APPLY_PROMPT).resolve()}")
        print("     This is a READ-ONLY first pass: verify, inventory, smoke-test.")
        print("     Mutating frontmatter / committing is a separate operator step.")

    return rc


if __name__ == "__main__":
    sys.exit(main())
