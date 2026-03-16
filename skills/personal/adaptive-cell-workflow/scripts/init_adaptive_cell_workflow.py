#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold the Adaptive Cell Workflow into a target repository."
    )
    parser.add_argument("target_repo", help="Path to the target repository root")
    parser.add_argument(
        "--repo-name",
        help="Override the repository name used in template placeholders",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned writes without touching the filesystem",
    )
    return parser.parse_args()


def playbook_root() -> Path:
    return Path(__file__).resolve().parents[4]


def template_root() -> Path:
    root = playbook_root() / "templates" / "adaptive-cell-workflow" / "project-root"
    if not root.is_dir():
        raise FileNotFoundError(f"Template root not found: {root}")
    return root


def render_template(text: str, repo_name: str) -> str:
    replacements = {
        "{{REPO_NAME}}": repo_name,
        "{{DATE}}": date.today().isoformat(),
    }
    for needle, value in replacements.items():
        text = text.replace(needle, value)
    return text


def destination_for(template_file: Path, root: Path, target_repo: Path) -> Path:
    relative_path = template_file.relative_to(root)
    name = relative_path.name
    if name.endswith(".tmpl"):
        name = name[: -len(".tmpl")]
    return target_repo / relative_path.with_name(name)


def main() -> int:
    args = parse_args()
    target_repo = Path(args.target_repo).resolve()

    if not target_repo.exists():
        print(f"Target repository does not exist: {target_repo}", file=sys.stderr)
        return 1

    repo_name = args.repo_name or target_repo.name
    source_root = template_root()
    planned_writes: list[tuple[Path, Path]] = []

    for source in sorted(source_root.rglob("*")):
        if source.is_dir():
            continue
        destination = destination_for(source, source_root, target_repo)
        planned_writes.append((source, destination))

    collisions = [
        str(destination)
        for _, destination in planned_writes
        if destination.exists() and not args.force
    ]
    if collisions:
        print("Refusing to overwrite existing files without --force:", file=sys.stderr)
        for path in collisions:
            print(f"  - {path}", file=sys.stderr)
        return 1

    for source, destination in planned_writes:
        if args.dry_run:
            print(f"[dry-run] {source} -> {destination}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        rendered = render_template(source.read_text(encoding="utf-8"), repo_name)
        destination.write_text(rendered, encoding="utf-8")
        print(f"created {destination}")

    if args.dry_run:
        print(
            "[dry-run] Would scaffold the Adaptive Cell Workflow into "
            f"{target_repo} for repo '{repo_name}'"
        )
    else:
        print(
            "Next step: run "
            f"python {Path(__file__).with_name('validate_adaptive_cell_workflow.py')} {target_repo}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
