#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    ".ai-work/README.md",
    ".ai-work/intake-policy.json",
    ".ai-work/runs/.gitkeep",
    ".ai-work/templates/board.json",
    ".ai-work/templates/dispatch-brief.md",
    ".ai-work/templates/worker-return.md",
    ".ai-work/templates/merge.md",
    ".ai-work/templates/promotion.md",
    "scripts/aiwork/start_run.py",
    ".cursor/agents/framing-cell.md",
    ".cursor/agents/implementation-cell.md",
    ".cursor/agents/risk-validation-cell.md",
    ".cursor/agents/memory-pattern-cell.md",
    ".cursor/commands/work-intake.md",
    ".cursor/commands/role-split.md",
    ".cursor/commands/merge-and-decide.md",
    ".cursor/commands/progress-update.md",
    ".cursor/commands/experience-capture.md",
    ".cursor/commands/doc-code-sync.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an Adaptive Cell Workflow installation."
    )
    parser.add_argument("target_repo", help="Path to the target repository root")
    return parser.parse_args()


def parse_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return {}
    frontmatter = {}
    for line in parts[0].splitlines()[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def validate_sections(path: Path, headings: list[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [heading for heading in headings if heading not in text]
    if missing:
        errors.append(f"{path.name} missing headings: {', '.join(missing)}")


def validate_board_template(payload: dict[str, Any], errors: list[str]) -> None:
    required_keys = [
        "run_id",
        "repo",
        "policy",
        "truth_sources",
        "main_goal",
        "mode",
        "score",
        "score_reasons",
        "workers",
        "status",
        "promotion_targets",
    ]
    missing = [key for key in required_keys if key not in payload]
    if missing:
        errors.append(f"board.json missing keys: {', '.join(missing)}")
        return

    if payload["mode"] not in {"solo", "split-3", "split-4"}:
        errors.append("board.json mode must be one of solo/split-3/split-4")
    policy = payload["policy"]
    if not isinstance(policy, dict):
        errors.append("board.json policy must be an object")
    else:
        if "path" not in policy or "version" not in policy:
            errors.append("board.json policy must include path and version")
    if not isinstance(payload["truth_sources"], list):
        errors.append("board.json truth_sources must be a list")
    if not isinstance(payload["workers"], list) or not payload["workers"]:
        errors.append("board.json workers must be a non-empty list")
    score = payload["score"]
    if not isinstance(score, dict):
        errors.append("board.json score must be an object")
        return
    for key in ["complexity", "coupling", "risk", "ambiguity", "total"]:
        if key not in score:
            errors.append(f"board.json score missing key: {key}")
    score_reasons = payload["score_reasons"]
    if not isinstance(score_reasons, dict):
        errors.append("board.json score_reasons must be an object")
    else:
        for key in ["complexity", "coupling", "risk", "ambiguity", "mode"]:
            if key not in score_reasons:
                errors.append(f"board.json score_reasons missing key: {key}")


def validate_intake_policy(payload: dict[str, Any], errors: list[str]) -> None:
    for key in ["version", "goal", "truth_sources", "mode_policy", "layers", "keywords", "scoring_policy", "scoring_hints"]:
        if key not in payload:
            errors.append(f"intake-policy.json missing key: {key}")
    if errors:
        return

    if not isinstance(payload["truth_sources"], list):
        errors.append("intake-policy.json truth_sources must be a list")
    mode_policy = payload["mode_policy"]
    if not isinstance(mode_policy, dict):
        errors.append("intake-policy.json mode_policy must be an object")
    else:
        for key in ["solo_max", "split_3_max", "split_4_requires_memory_signal", "high_risk_min_mode", "journey_bias_min_mode", "split_3_roles", "split_4_extra_roles"]:
            if key not in mode_policy:
                errors.append(f"intake-policy.json mode_policy missing key: {key}")
    keywords = payload["keywords"]
    if not isinstance(keywords, dict):
        errors.append("intake-policy.json keywords must be an object")
    else:
        for key in ["object_chain", "high_risk", "ambiguity", "complexity", "memory_signal", "shared_interface", "medium_risk"]:
            if key not in keywords:
                errors.append(f"intake-policy.json keywords missing key: {key}")


def validate_agent_file(path: Path, expected_name: str, errors: list[str]) -> None:
    frontmatter = parse_frontmatter(path)
    if frontmatter.get("name") != expected_name:
        errors.append(f"{path.name} frontmatter name must be '{expected_name}'")
    if not frontmatter.get("description"):
        errors.append(f"{path.name} must define a description in frontmatter")


def validate_command_file(path: Path, expected_heading: str, errors: list[str]) -> None:
    frontmatter = parse_frontmatter(path)
    if not frontmatter.get("description"):
        errors.append(f"{path.name} must define a description in frontmatter")
    text = path.read_text(encoding="utf-8")
    if expected_heading not in text:
        errors.append(f"{path.name} missing heading: {expected_heading}")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.target_repo).resolve()
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (repo_root / relative_path).exists():
            errors.append(f"missing required file: {relative_path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    validate_board_template(
        parse_json(repo_root / ".ai-work" / "templates" / "board.json"),
        errors,
    )
    validate_intake_policy(
        parse_json(repo_root / ".ai-work" / "intake-policy.json"),
        errors,
    )
    validate_sections(
        repo_root / ".ai-work" / "README.md",
        ["## Intake Policy", "## Modes", "## Run Layout", "## Promotion Rules"],
        errors,
    )
    validate_sections(
        repo_root / ".ai-work" / "templates" / "dispatch-brief.md",
        [
            "## Goal",
            "## Role",
            "## Scope",
            "## Inputs",
            "## Deliverable",
            "## Constraints",
            "## Escalate When",
        ],
        errors,
    )
    validate_sections(
        repo_root / ".ai-work" / "templates" / "worker-return.md",
        [
            "## Summary",
            "## Findings",
            "## Proposed Changes",
            "## Risks",
            "## Open Questions",
            "## Recommended Next Step",
        ],
        errors,
    )
    validate_sections(
        repo_root / ".ai-work" / "templates" / "merge.md",
        [
            "## Chosen Path",
            "## Rejected Paths",
            "## Required Checks",
            "## Promotion Targets",
        ],
        errors,
    )
    validate_sections(
        repo_root / ".ai-work" / "templates" / "promotion.md",
        [
            "## Repo Truth",
            "## Playbook",
            "## Second Brain",
            "## Deferred",
        ],
        errors,
    )

    validate_agent_file(repo_root / ".cursor" / "agents" / "framing-cell.md", "framing-cell", errors)
    validate_agent_file(repo_root / ".cursor" / "agents" / "implementation-cell.md", "implementation-cell", errors)
    validate_agent_file(repo_root / ".cursor" / "agents" / "risk-validation-cell.md", "risk-validation-cell", errors)
    validate_agent_file(repo_root / ".cursor" / "agents" / "memory-pattern-cell.md", "memory-pattern-cell", errors)

    validate_command_file(repo_root / ".cursor" / "commands" / "work-intake.md", "# /work-intake", errors)
    validate_command_file(repo_root / ".cursor" / "commands" / "role-split.md", "# /role-split", errors)
    validate_command_file(repo_root / ".cursor" / "commands" / "merge-and-decide.md", "# /merge-and-decide", errors)
    validate_command_file(repo_root / ".cursor" / "commands" / "progress-update.md", "# /progress-update", errors)
    validate_command_file(repo_root / ".cursor" / "commands" / "experience-capture.md", "# /experience-capture", errors)
    validate_command_file(repo_root / ".cursor" / "commands" / "doc-code-sync.md", "# /doc-code-sync", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Adaptive Cell Workflow OK: {repo_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
