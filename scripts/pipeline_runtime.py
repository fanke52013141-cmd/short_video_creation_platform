"""Shared production state and gate helpers."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGES = [
    "story_generation", "art_direction", "storyboard_director",
    "storyboard_sequence_review", "asset_executor", "asset_prompt_generation",
    "asset_image_generation", "generated_asset_review", "video_segment_planning",
    "storyboard_prompt_generation", "storyboard_image_generation",
    "storyboard_visual_review", "video_prompt_generation", "final_package",
]

PREREQUISITES = {
    stage: STAGES[:i] for i, stage in enumerate(STAGES)
}

APPROVAL_REQUIRED = {
    "story_generation", "art_direction", "storyboard_sequence_review",
    "generated_asset_review", "storyboard_visual_review",
}

TERMINAL_OK = {"approved", "completed"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_checkpoint(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "checkpoint.json"
    data = read_json(path)
    data.setdefault("schema_version", "3.1")
    data.setdefault("stages", {})
    for stage in STAGES:
        data["stages"].setdefault(stage, {"status": "not_started", "version": 0, "updated_at": None})
    data.setdefault("blockers", [])
    data.setdefault("artifact_versions", {})
    data["phase_order"] = STAGES
    data["total_phases"] = len(STAGES)
    return data


def save_checkpoint(run_dir: Path, data: dict[str, Any]) -> None:
    data["last_updated"] = now()
    write_json(run_dir / "checkpoint.json", data)


def unresolved_p0(run_dir: Path) -> list[str]:
    found = []
    review_dir = run_dir / "outputs" / "reviews"
    if not review_dir.is_dir():
        return found
    for path in review_dir.glob("*.json"):
        try:
            review = read_json(path)
        except (OSError, json.JSONDecodeError):
            found.append(f"invalid review: {path.name}")
            continue
        for issue in review.get("issues", []):
            if issue.get("severity") == "P0" and issue.get("resolution_status") not in {"resolved", "accepted"}:
                found.append(f"{path.name}: {issue.get('id') or issue.get('description', 'P0')}")
    return found


def gate_errors(run_dir: Path, checkpoint: dict[str, Any], target_stage: str) -> list[str]:
    if target_stage not in STAGES:
        return [f"unknown stage: {target_stage}"]
    errors = []
    for stage in PREREQUISITES[target_stage]:
        status = checkpoint["stages"][stage]["status"]
        if status not in TERMINAL_OK:
            errors.append(f"{stage} is {status}, expected approved/completed")
    if target_stage not in {"story_generation", "art_direction", "storyboard_director", "storyboard_sequence_review"}:
        errors.extend(unresolved_p0(run_dir))
    return errors


def next_stage(checkpoint: dict[str, Any]) -> str | None:
    for stage in STAGES:
        if checkpoint["stages"][stage]["status"] not in TERMINAL_OK:
            return stage
    return None


def invalidate_from(checkpoint: dict[str, Any], stage: str, reason: str) -> list[str]:
    index = STAGES.index(stage)
    invalidated = []
    for name in STAGES[index + 1:]:
        row = checkpoint["stages"][name]
        if row["status"] != "not_started":
            row.update({"status": "not_started", "invalidated_by": stage, "invalidation_reason": reason, "updated_at": now()})
            invalidated.append(name)
    return invalidated
