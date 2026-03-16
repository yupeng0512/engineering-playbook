#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    ".autonomy/README.md",
    ".autonomy/product_principles.md",
    ".autonomy/decision_policy.md",
    ".autonomy/definition_of_done.md",
    ".autonomy/default_action_policy.md",
    ".autonomy/bootstrap_policy.md",
    ".autonomy/checkpoint_template.md",
    ".autonomy/model_policy.json",
    ".autonomy/state_machine.json",
    ".autonomy/schemas/task-record.schema.json",
    ".autonomy/schemas/approval-record.schema.json",
    ".autonomy/schemas/bootstrap-candidate.schema.json",
    ".autonomy/examples/task-record.example.json",
    ".autonomy/examples/approval-record.example.json",
    ".autonomy/examples/bootstrap-candidate.example.json",
    ".autonomy/examples/checkpoint.example.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a repo-local .autonomy contract."
    )
    parser.add_argument("target_repo", help="Path to the target repository root")
    return parser.parse_args()


def parse_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_iso_datetime(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def ensure_required_keys(
    payload: dict[str, Any], required_keys: list[str], label: str, errors: list[str]
) -> None:
    missing = [key for key in required_keys if key not in payload]
    if missing:
        errors.append(f"{label} missing keys: {', '.join(missing)}")


def validate_state_machine(state_machine: dict[str, Any], errors: list[str]) -> None:
    for entity_name in ["task_record", "approval_record", "bootstrap_candidate"]:
        entity = state_machine.get(entity_name)
        if not isinstance(entity, dict):
            errors.append(f"state_machine missing entity: {entity_name}")
            continue

        states = entity.get("states")
        transitions = entity.get("transitions")
        if not isinstance(states, list) or not all(isinstance(item, str) for item in states):
            errors.append(f"{entity_name}.states must be a string list")
            continue
        if not isinstance(transitions, dict):
            errors.append(f"{entity_name}.transitions must be an object")
            continue

        state_set = set(states)
        for source, targets in transitions.items():
            if source not in state_set:
                errors.append(f"{entity_name}.transitions has unknown source state: {source}")
                continue
            if not isinstance(targets, list) or not all(isinstance(item, str) for item in targets):
                errors.append(f"{entity_name}.transitions[{source}] must be a string list")
                continue
            unknown_targets = [target for target in targets if target not in state_set]
            if unknown_targets:
                errors.append(
                    f"{entity_name}.transitions[{source}] has unknown targets: "
                    + ", ".join(unknown_targets)
                )


def validate_model_policy(model_policy: dict[str, Any], errors: list[str]) -> None:
    slots = model_policy.get("slots")
    if not isinstance(slots, dict):
        errors.append("model_policy.slots must be an object")
        return

    for slot_name in ["planner", "reviewer", "executor"]:
        slot = slots.get(slot_name)
        if not isinstance(slot, dict):
            errors.append(f"model_policy missing slot: {slot_name}")
            continue
        if not isinstance(slot.get("default_model"), str) or not slot.get("default_model"):
            errors.append(f"model_policy.{slot_name}.default_model must be a non-empty string")
        if not isinstance(slot.get("override_env"), str) or not slot.get("override_env"):
            errors.append(f"model_policy.{slot_name}.override_env must be a non-empty string")


def validate_schema_documents(schema_documents: dict[str, dict[str, Any]], errors: list[str]) -> None:
    for name, payload in schema_documents.items():
        if not isinstance(payload.get("title"), str) or not payload.get("title"):
            errors.append(f"{name} schema must define a non-empty title")
        if payload.get("type") != "object":
            errors.append(f"{name} schema must have type=object")
        if "required" not in payload or not isinstance(payload["required"], list):
            errors.append(f"{name} schema must define a required list")


def validate_task_example(
    payload: dict[str, Any], state_machine: dict[str, Any], errors: list[str]
) -> None:
    required = [
        "id",
        "goal",
        "repo",
        "state",
        "approval_state",
        "risk_level",
        "priority",
        "depends_on",
        "blocked_reason",
        "next_check_at",
        "default_action_policy",
        "evidence_refs",
        "allowed_paths",
        "updated_at",
    ]
    ensure_required_keys(payload, required, "task example", errors)

    task_states = set(state_machine["task_record"]["states"])
    approval_states = set(state_machine["approval_record"]["states"])
    if payload.get("state") not in task_states:
        errors.append(f"task example has invalid state: {payload.get('state')}")
    if payload.get("approval_state") not in approval_states:
        errors.append(
            f"task example has invalid approval_state: {payload.get('approval_state')}"
        )
    if payload.get("risk_level") not in {"low", "medium", "high"}:
        errors.append("task example risk_level must be one of low/medium/high")
    if payload.get("priority") not in {"P0", "P1", "P2", "P3"}:
        errors.append("task example priority must be one of P0/P1/P2/P3")
    if not isinstance(payload.get("depends_on"), list):
        errors.append("task example depends_on must be a list")
    if not isinstance(payload.get("evidence_refs"), list):
        errors.append("task example evidence_refs must be a list")
    if not isinstance(payload.get("allowed_paths"), list) or not payload.get("allowed_paths"):
        errors.append("task example allowed_paths must be a non-empty list")
    if not is_iso_datetime(payload.get("next_check_at")):
        errors.append("task example next_check_at must be ISO datetime or null")
    if not is_iso_datetime(payload.get("updated_at")):
        errors.append("task example updated_at must be an ISO datetime")

    if payload.get("state") == "ready_for_review" and payload.get("default_action_policy") != "generate_evidence_only":
        errors.append(
            "task example in ready_for_review must use default_action_policy=generate_evidence_only"
        )


def validate_approval_example(
    payload: dict[str, Any], state_machine: dict[str, Any], errors: list[str]
) -> None:
    required = [
        "task_id",
        "state",
        "requested_at",
        "decision_at",
        "decision_by",
        "checkpoint_path",
        "risk_summary",
        "timeout_at",
    ]
    ensure_required_keys(payload, required, "approval example", errors)

    approval_states = set(state_machine["approval_record"]["states"])
    if payload.get("state") not in approval_states:
        errors.append(f"approval example has invalid state: {payload.get('state')}")
    for field_name in ["requested_at", "decision_at", "timeout_at"]:
        if not is_iso_datetime(payload.get(field_name)):
            errors.append(f"approval example {field_name} must be ISO datetime or null")


def validate_bootstrap_example(
    payload: dict[str, Any], state_machine: dict[str, Any], errors: list[str]
) -> None:
    required = [
        "id",
        "repo",
        "status",
        "target_files",
        "change_summary",
        "evidence_refs",
        "evals",
        "promotion_required",
        "updated_at",
    ]
    ensure_required_keys(payload, required, "bootstrap example", errors)

    bootstrap_states = set(state_machine["bootstrap_candidate"]["states"])
    if payload.get("status") not in bootstrap_states:
        errors.append(f"bootstrap example has invalid status: {payload.get('status')}")
    target_files = payload.get("target_files")
    if not isinstance(target_files, list) or not target_files:
        errors.append("bootstrap example target_files must be a non-empty list")
    else:
        invalid_targets = [
            item for item in target_files if not isinstance(item, str) or not item.startswith(".autonomy/")
        ]
        if invalid_targets:
            errors.append(
                "bootstrap example target_files must stay under .autonomy/: "
                + ", ".join(map(str, invalid_targets))
            )

    evals = payload.get("evals")
    if not isinstance(evals, list) or len(evals) < 3:
        errors.append("bootstrap example evals must contain at least three entries")
    else:
        required_eval_names = {
            "boundary_compliance",
            "history_replay",
            "failure_regression",
        }
        seen_names = set()
        for item in evals:
            if not isinstance(item, dict):
                errors.append("bootstrap example eval entries must be objects")
                continue
            ensure_required_keys(item, ["name", "status", "notes"], "bootstrap eval", errors)
            name = item.get("name")
            status = item.get("status")
            seen_names.add(name)
            if name not in required_eval_names:
                errors.append(f"bootstrap eval has invalid name: {name}")
            if status not in {"passed", "failed"}:
                errors.append(f"bootstrap eval has invalid status: {status}")
        missing_eval_names = sorted(required_eval_names - seen_names)
        if missing_eval_names:
            errors.append(
                "bootstrap example missing required evals: " + ", ".join(missing_eval_names)
            )

    if not isinstance(payload.get("promotion_required"), bool):
        errors.append("bootstrap example promotion_required must be boolean")
    if not is_iso_datetime(payload.get("updated_at")):
        errors.append("bootstrap example updated_at must be an ISO datetime")


def validate_checkpoint(checkpoint_path: Path, errors: list[str]) -> None:
    text = checkpoint_path.read_text(encoding="utf-8")
    required_sections = [
        "## 1. 当前目标",
        "## 2. 已完成内容",
        "## 3. 证据",
        "## 4. 未决问题",
        "## 5. 候选方案 A / B",
        "## 6. 推荐方案及理由",
        "## 7. 风险",
        "## 8. 超时默认动作",
    ]
    missing = [section for section in required_sections if section not in text]
    if missing:
        errors.append("checkpoint example missing sections: " + ", ".join(missing))


def main() -> int:
    args = parse_args()
    repo_root = Path(args.target_repo).resolve()
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        path = repo_root / relative_path
        if not path.exists():
            errors.append(f"missing required file: {relative_path}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    model_policy = parse_json(repo_root / ".autonomy" / "model_policy.json")
    state_machine = parse_json(repo_root / ".autonomy" / "state_machine.json")
    schema_documents = {
        "task-record": parse_json(
            repo_root / ".autonomy" / "schemas" / "task-record.schema.json"
        ),
        "approval-record": parse_json(
            repo_root / ".autonomy" / "schemas" / "approval-record.schema.json"
        ),
        "bootstrap-candidate": parse_json(
            repo_root / ".autonomy" / "schemas" / "bootstrap-candidate.schema.json"
        ),
    }
    task_example = parse_json(repo_root / ".autonomy" / "examples" / "task-record.example.json")
    approval_example = parse_json(
        repo_root / ".autonomy" / "examples" / "approval-record.example.json"
    )
    bootstrap_example = parse_json(
        repo_root / ".autonomy" / "examples" / "bootstrap-candidate.example.json"
    )

    validate_model_policy(model_policy, errors)
    validate_schema_documents(schema_documents, errors)
    validate_state_machine(state_machine, errors)
    validate_task_example(task_example, state_machine, errors)
    validate_approval_example(approval_example, state_machine, errors)
    validate_bootstrap_example(bootstrap_example, state_machine, errors)
    validate_checkpoint(repo_root / ".autonomy" / "examples" / "checkpoint.example.md", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"Autonomy contract OK: {repo_root / '.autonomy'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
