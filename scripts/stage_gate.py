"""Artifact checks used before a pipeline stage can complete or be approved."""
from __future__ import annotations

import json
from pathlib import Path


def read(path: Path):
    if not path.is_file():
        raise ValueError(f"missing required artifact: {path}")
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".wav"}:
        return path
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.suffix == ".json" else path.read_text(encoding="utf-8")


def require_pass(review: dict, label: str) -> None:
    if review.get("status") != "pass" or any(x.get("severity") == "P0" for x in review.get("issues", [])):
        raise ValueError(f"{label} has unresolved blockers")


def validate_stage_outputs(run: Path, stage: str, approving: bool = False) -> None:
    out = run / "outputs"
    if stage == "story_generation": read(out / "story.md")
    elif stage == "art_direction": read(out / "style_bible.md")
    elif stage == "storyboard_director": read(out / "storyboard.json")
    elif stage == "storyboard_sequence_review":
        review = read(out / "reviews/storyboard_sequence_review.json")
        if approving: require_pass(review, "storyboard sequence review")
    elif stage == "asset_executor":
        read(out / "asset_manifest.json"); read(out / "shot_asset_map.json")
    elif stage == "asset_prompt_generation":
        manifest = read(out / "asset_manifest.json")
        for group in ("characters", "scenes", "props"):
            for item in manifest.get(group, []):
                if item.get("generation_required"):
                    read(run / item["output_prompt_path"].removeprefix("./"))
    elif stage == "asset_image_generation":
        queue = read(out / "image_generation_queue.json")
        incomplete = [x["task_id"] for x in queue["tasks"] if x["status"] != "succeeded"]
        if incomplete: raise ValueError("image queue incomplete: " + ", ".join(incomplete))
    elif stage == "generated_asset_review":
        manifest = read(out / "asset_manifest.json")
        pending = [x["asset_name"] for g in ("characters", "scenes", "props") for x in manifest[g] if x.get("generation_required") and x.get("approval_status") != "approved"]
        if approving and pending: raise ValueError("assets not approved: " + ", ".join(pending))
    elif stage == "video_segment_planning": read(out / "video_segment_plan.json")
    elif stage == "storyboard_prompt_generation":
        shots = read(out / "storyboard.json")["shots"]
        for shot in shots: read(out / "approved/storyboard_prompts" / f"{shot['shot_id']}.md")
    elif stage == "storyboard_image_generation":
        shots = read(out / "storyboard.json")["shots"]
        for shot in shots: read(out / "storyboards" / f"{shot['shot_id']}.png")
    elif stage == "storyboard_visual_review":
        review = read(out / "reviews/storyboard_visual_review.json")
        if approving: require_pass(review, "storyboard visual review")
    elif stage == "video_prompt_generation":
        plan = read(out / "video_segment_plan.json")
        for segment in plan["segments"]:
            read(out / "approved/video_generation" / segment["video_id"] / "prompt.txt")
            read(out / "approved/video_generation" / segment["video_id"] / "manifest.json")
    elif stage == "final_package":
        final = read(out / "final_package_manifest.json")
        if final.get("status") != "completed": raise ValueError("final package is not completed")
