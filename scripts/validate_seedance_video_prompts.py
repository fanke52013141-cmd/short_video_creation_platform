#!/usr/bin/env python3
"""Validate Seedance 2.0 shot video prompt files.

This validator is intentionally focused on prompt-surface rules that are hard to
express in JSON schema:
- per-shot markdown files exist,
- required output sections exist,
- Seedance task type is declared,
- strict edit / extend wording is not confused with reference wording,
- @PROP is not used by default,
- Chinese-only prompt contract is respected.

Usage:
  python scripts/validate_seedance_video_prompts.py local_runs/YYYY-MM-DD/project_slug
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TASK_TYPES = {
    "pipeline_shot_generation",
    "multimodal_reference",
    "video_edit",
    "video_extend",
    "combined_task",
}

REQUIRED_SECTIONS = ["【引用决策】", "【资产声明区】", "【中文视频提示词】", "【自检通过项】"]
ENGLISH_BLOCK_PATTERNS = ["【English Prompt】", "English Prompt", "英文提示词", "中英对照"]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"WARN: {message}")


def ok(message: str) -> None:
    print(f"OK: {message}")


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {path} ({exc})")


def extract_cn_prompt(text: str) -> str:
    marker = "【中文视频提示词】"
    if marker not in text:
        return ""
    after = text.split(marker, 1)[1]
    if "【自检通过项】" in after:
        after = after.split("【自检通过项】", 1)[0]
    return after.strip()


def declared_task_type(text: str) -> str | None:
    for task_type in TASK_TYPES:
        if task_type in text:
            return task_type
    match = re.search(r"任务类型[：:]\s*([a-z_]+)", text)
    if match and match.group(1) in TASK_TYPES:
        return match.group(1)
    return None


def validate_seedance_sentence_type(shot_id: str, task_type: str, text: str, cn_prompt: str) -> None:
    if task_type == "video_edit":
        if not re.search(r"严格编辑\s*@视频\d+", cn_prompt):
            fail(f"{shot_id} video_edit must use '严格编辑 @视频N' in 中文视频提示词")
        if re.search(r"参考\s*@视频\d+", cn_prompt) and "严格编辑" not in cn_prompt:
            fail(f"{shot_id} video_edit is written as a reference task")

    if task_type == "video_extend":
        if not re.search(r"向前延长\s*@视频\d+|向后延长\s*@视频\d+", cn_prompt):
            fail(f"{shot_id} video_extend must use '向前延长 @视频N' or '向后延长 @视频N'")
        first_sentence = cn_prompt.split("。", 1)[0]
        if re.search(r"参考\s*@视频\d+", first_sentence):
            fail(f"{shot_id} video_extend first sentence must not be a reference task")

    if task_type == "combined_task":
        has_reference = re.search(r"参考\s*@(?:图片|视频|音频)\d+", cn_prompt)
        has_operation = re.search(r"严格编辑\s*@视频\d+|向前延长\s*@视频\d+|向后延长\s*@视频\d+", cn_prompt)
        if not has_reference or not has_operation:
            fail(f"{shot_id} combined_task must include both a reference source and an edit/extend operation")


def validate_sound_symbols(shot_id: str, text: str, cn_prompt: str) -> None:
    has_audio_ref = "@AUDIO_" in text or re.search(r"@音频\d+", text)
    has_dialogue = "{" in cn_prompt or "说道" in cn_prompt or "台词" in text
    if has_audio_ref and has_dialogue and "{" not in cn_prompt:
        fail(f"{shot_id} dialogue should use Seedance braces like {{台词内容}}")
    if "背景音乐" in cn_prompt and "（背景中播放着" not in cn_prompt:
        warn(f"{shot_id} mentions background music without Seedance music parentheses")
    if "环境音" in cn_prompt and "<" not in cn_prompt:
        warn(f"{shot_id} mentions environment sound without Seedance angle brackets")


def validate_shot_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    shot_id = path.stem

    for section in REQUIRED_SECTIONS:
        if section not in text:
            fail(f"{shot_id} missing required section: {section}")

    for pattern in ENGLISH_BLOCK_PATTERNS:
        if pattern in text:
            fail(f"{shot_id} contains forbidden English/bilingual block: {pattern}")

    if "@PROP_" in text:
        fail(f"{shot_id} contains @PROP reference; props must be described in prompt body by default")

    if f"@{shot_id}_STORYBOARD" not in text:
        fail(f"{shot_id} missing @{shot_id}_STORYBOARD reference")

    task_type = declared_task_type(text)
    if not task_type:
        fail(f"{shot_id} missing Seedance task type declaration")

    cn_prompt = extract_cn_prompt(text)
    if not cn_prompt:
        fail(f"{shot_id} has empty 中文视频提示词 section")

    validate_seedance_sentence_type(shot_id, task_type, text, cn_prompt)
    validate_sound_symbols(shot_id, text, cn_prompt)

    if "无字幕" in cn_prompt and "【" in cn_prompt and "【中文视频提示词】" not in cn_prompt:
        warn(f"{shot_id} may contain conflicting subtitle instructions")

    ok(f"{shot_id} Seedance prompt")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Seedance shot video prompt markdown files.")
    parser.add_argument("run_dir", help="Local run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    storyboard_path = run_dir / "outputs" / "03_storyboard" / "storyboard.json"
    shot_dir = run_dir / "outputs" / "05_video_prompts" / "shots"
    summary_path = run_dir / "outputs" / "05_video_prompts" / "shot_video_prompts.md"

    if not storyboard_path.exists():
        fail(f"Missing storyboard.json: {storyboard_path}")
    if not shot_dir.is_dir():
        fail(f"Missing shot prompt directory: {shot_dir}")
    if not summary_path.exists():
        fail(f"Missing summary prompt file: {summary_path}")

    storyboard = read_json(storyboard_path)
    shot_ids = [shot.get("id") for shot in storyboard.get("shots", []) if shot.get("id")]
    if not shot_ids:
        fail("storyboard.json contains no shot ids")

    for shot_id in shot_ids:
        validate_shot_file(shot_dir / f"{shot_id}.md")

    summary_text = summary_path.read_text(encoding="utf-8")
    for shot_id in shot_ids:
        if f"## {shot_id}" not in summary_text:
            fail(f"summary file missing heading for {shot_id}")

    ok(f"validated Seedance prompts: {len(shot_ids)}")
    print("SEEDANCE VIDEO PROMPT VALIDATION PASSED")


if __name__ == "__main__":
    main()
