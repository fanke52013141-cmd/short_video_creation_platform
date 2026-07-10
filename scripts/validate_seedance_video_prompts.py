#!/usr/bin/env python3
"""Validate current pipeline video prompt outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = ["【自检通过项】", "【资产声明区】", "【中文视频提示词】"]
DISALLOWED_TEXT = ["English Prompt", "英文提示词", "中英对照", "@PROP", "@PROP_"]
TASK_TYPE = "pipeline_shot_generation"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"OK: {message}")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {path} ({exc})")
    if not isinstance(data, dict):
        fail(f"JSON root must be object: {path}")
    return data


def require_file(path: Path) -> None:
    if not path.is_file():
        fail(f"Missing required file: {path}")


def load_expected_shots(storyboard_path: Path) -> list[str]:
    storyboard = read_json(storyboard_path)
    shots = storyboard.get("shots", [])
    if not isinstance(shots, list) or not shots:
        fail("storyboard.json contains no shots")
    shot_ids: list[str] = []
    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            fail(f"storyboard.shots[{index - 1}] must be object")
        expected = f"S{index:03d}"
        if shot.get("shot_id") != expected:
            fail(f"expected {expected}, got {shot.get('shot_id')!r}")
        shot_ids.append(expected)
    return shot_ids


def validate_markdown(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"video_prompts.md missing section: {section}")
    for token in DISALLOWED_TEXT:
        if token in text:
            fail(f"video_prompts.md contains disallowed text: {token}")
    if TASK_TYPE not in text:
        fail(f"video_prompts.md missing task type: {TASK_TYPE}")
    if "画面保持无字幕" not in text or "Logo" not in text or "水印" not in text:
        fail("video_prompts.md missing no-subtitle/no-logo/no-watermark constraint")
    ok("video_prompts.md")


def validate_plan(path: Path, expected_shots: list[str]) -> None:
    plan = read_json(path)
    videos = plan.get("videos", [])
    if not isinstance(videos, list) or not videos:
        fail("video_prompts.json contains no videos")

    expected_set = set(expected_shots)
    covered: list[str] = []
    for index, video in enumerate(videos, start=1):
        if not isinstance(video, dict):
            fail(f"videos[{index - 1}] must be object")
        video_id = f"V{index:03d}"
        if video.get("video_id") != video_id:
            fail(f"expected {video_id}, got {video.get('video_id')!r}")
        if video.get("task_type") != TASK_TYPE:
            fail(f"{video_id} must use task_type={TASK_TYPE}")
        source_shots = video.get("source_shots", [])
        if not isinstance(source_shots, list) or not source_shots:
            fail(f"{video_id} source_shots must be a non-empty list")
        unknown = sorted(set(source_shots) - expected_set)
        if unknown:
            fail(f"{video_id} references unknown source_shots: {', '.join(unknown)}")
        if len(source_shots) != len(set(source_shots)):
            fail(f"{video_id} source_shots contains duplicates")
        frame_references = video.get("frame_references", [])
        if not isinstance(frame_references, list) or not frame_references:
            fail(f"{video_id} missing frame_references")
        frame_shots = {frame.get("shot_id") for frame in frame_references if isinstance(frame, dict)}
        if frame_shots != set(source_shots):
            fail(f"{video_id} frame_references must match source_shots")
        prompt_cn = video.get("prompt_cn", "")
        if not isinstance(prompt_cn, str) or not prompt_cn.strip():
            fail(f"{video_id} has empty prompt_cn")
        for section in REQUIRED_SECTIONS:
            if section not in prompt_cn:
                fail(f"{video_id} prompt_cn missing section: {section}")
        for token in DISALLOWED_TEXT:
            if token in prompt_cn:
                fail(f"{video_id} prompt_cn contains disallowed text: {token}")
        covered.extend(source_shots)

    if sorted(covered) != sorted(expected_shots):
        fail("video_prompts.json must cover every storyboard shot exactly once")
    ok(f"video_prompts.json covers {len(expected_shots)} shots")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate current pipeline video prompt outputs.")
    parser.add_argument("run_dir", help="Local run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    storyboard_path = run_dir / "outputs" / "storyboard.json"
    video_markdown_path = run_dir / "outputs" / "video_prompts.md"
    video_json_path = run_dir / "outputs" / "video_prompts.json"

    require_file(storyboard_path)
    require_file(video_markdown_path)
    require_file(video_json_path)

    expected_shots = load_expected_shots(storyboard_path)
    validate_markdown(video_markdown_path)
    validate_plan(video_json_path, expected_shots)
    print("VIDEO PROMPT VALIDATION PASSED")


if __name__ == "__main__":
    main()
