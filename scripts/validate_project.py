#!/usr/bin/env python3
"""Validate an AI short film local run.

Usage:
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"WARN: {message}")


def ok(message: str) -> None:
    print(f"OK: {message}")


def main() -> None:
    if len(sys.argv) != 2:
        fail("Expected one argument: local run directory")

    run_dir = Path(sys.argv[1]).resolve()
    if not run_dir.exists():
        fail(f"Run directory does not exist: {run_dir}")

    checkpoint_path = run_dir / "checkpoint.json"
    storyboard_path = run_dir / "outputs" / "03_storyboard" / "storyboard.json"
    video_prompt_path = run_dir / "outputs" / "05_video_prompts" / "shot_video_prompts.md"
    reference_path = run_dir / "outputs" / "05_video_prompts" / "video_prompt_asset_reference.md"
    production_status_path = run_dir / "production_status.csv"

    for path in [checkpoint_path, storyboard_path, video_prompt_path, reference_path]:
        if not path.exists():
            fail(f"Required file missing: {path}")

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8-sig"))
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8-sig"))
    prompt_text = video_prompt_path.read_text(encoding="utf-8")
    reference_text = reference_path.read_text(encoding="utf-8")

    shots = storyboard.get("shots", [])
    shot_count = len(shots)
    if shot_count == 0:
        fail("storyboard.json has no shots")
    ok(f"storyboard shots: {shot_count}")

    image_mode = checkpoint.get("generation_modes", {}).get("image_generation")
    if image_mode in (None, "ask_user"):
        warn("checkpoint.generation_modes.image_generation is not finalized")
    elif image_mode not in ("external_manual", "internal_codex"):
        fail(f"Invalid image generation mode: {image_mode}")
    else:
        ok(f"image generation mode: {image_mode}")

    heading_count = len(re.findall(r"^## SHOT_\d{3}\b", prompt_text, flags=re.MULTILINE))
    duration_count = len(re.findall(r"^建议时长：\d+ 秒$", prompt_text, flags=re.MULTILINE))
    storyboard_decl_count = len(re.findall(r"^@SHOT_\d{3}_STORYBOARD（", prompt_text, flags=re.MULTILINE))
    chinese_storyboard_count = len(re.findall(r"^以 @SHOT_\d{3}_STORYBOARD 作为", prompt_text, flags=re.MULTILINE))
    english_block_count = prompt_text.count("【English Prompt】")
    prop_at_count = prompt_text.count("@PROP_")

    expected_counts = {
        "shot headings": heading_count,
        "duration lines": duration_count,
        "storyboard declarations": storyboard_decl_count,
        "Chinese storyboard usage lines": chinese_storyboard_count,
    }
    for label, count in expected_counts.items():
        if count != shot_count:
            fail(f"{label} count {count} does not match shot count {shot_count}")
        ok(f"{label}: {count}")

    if english_block_count:
        fail(f"English Prompt blocks are not allowed: {english_block_count}")
    ok("Chinese-only video prompt contract")

    if prop_at_count:
        fail(f"@PROP references are not allowed by default: {prop_at_count}")
    ok("no @PROP references")

    reference_shot_map_count = len(re.findall(r"^\| `@SHOT_\d{3}_STORYBOARD`", reference_text, flags=re.MULTILINE))
    if reference_shot_map_count != shot_count:
        fail(f"storyboard reference map count {reference_shot_map_count} does not match shot count {shot_count}")
    ok(f"storyboard reference map: {reference_shot_map_count}")

    if not production_status_path.exists():
        warn(f"production_status.csv missing: {production_status_path}")
    else:
        ok("production_status.csv exists")

    print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
