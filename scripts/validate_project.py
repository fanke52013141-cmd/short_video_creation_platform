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
    storyboard_review_path = run_dir / "outputs" / "03_storyboard" / "storyboard_sequence_review.json"
    video_prompt_path = run_dir / "outputs" / "05_video_prompts" / "shot_video_prompts.md"
    single_shot_dir = run_dir / "outputs" / "05_video_prompts" / "shots"
    reference_path = run_dir / "outputs" / "05_video_prompts" / "video_prompt_asset_reference.md"
    production_status_path = run_dir / "production_status.csv"

    for path in [checkpoint_path, storyboard_path, storyboard_review_path, video_prompt_path, reference_path]:
        if not path.exists():
            fail(f"Required file missing: {path}")

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8-sig"))
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8-sig"))
    storyboard_review = json.loads(storyboard_review_path.read_text(encoding="utf-8-sig"))
    prompt_text = video_prompt_path.read_text(encoding="utf-8")
    reference_text = reference_path.read_text(encoding="utf-8")

    shots = storyboard.get("shots", [])
    shot_count = len(shots)
    if shot_count == 0:
        fail("storyboard.json has no shots")
    ok(f"storyboard shots: {shot_count}")

    review_status = storyboard_review.get("status")
    if review_status not in ("pass", "revise_required"):
        fail(f"Invalid storyboard sequence review status: {review_status}")
    p0_issues = [
        item for item in storyboard_review.get("issues", [])
        if item.get("severity") == "P0"
    ]
    if p0_issues:
        fail(f"storyboard sequence review has unresolved P0 issues: {len(p0_issues)}")
    ok(f"storyboard sequence review: {review_status}")

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

    if not single_shot_dir.exists():
        fail(f"Single-shot prompt directory missing: {single_shot_dir}")

    single_shot_files = sorted(single_shot_dir.glob("SHOT_*.md"))
    if len(single_shot_files) != shot_count:
        fail(f"single shot file count {len(single_shot_files)} does not match shot count {shot_count}")
    ok(f"single shot files: {len(single_shot_files)}")

    voice_manifest_path = run_dir / "outputs" / "04_assets" / "audio" / "voice_reference_manifest.json"
    voice_ids: set[str] = set()
    if voice_manifest_path.exists():
        voice_manifest = json.loads(voice_manifest_path.read_text(encoding="utf-8-sig"))
        for item in voice_manifest.get("voice_references", []):
            if item.get("id"):
                voice_ids.add(item["id"])
        ok(f"voice references: {len(voice_ids)}")
    else:
        warn(f"voice reference manifest missing: {voice_manifest_path}")

    dialogue_patterns = re.compile(
        r"对白|旁白|台词|留言|录音|电话|新闻|播报|宣誓|祝福|低声|问：|说：|回答|“[^”]+”"
    )
    for shot in shots:
        shot_id = shot.get("id")
        if not shot_id:
            fail("shot missing id")
        shot_file = single_shot_dir / f"{shot_id}.md"
        if not shot_file.exists():
            fail(f"single shot prompt missing: {shot_file}")
        shot_text = shot_file.read_text(encoding="utf-8")

        required_snippets = ["【引用决策】", "【资产声明】", "【中文提示词】", f"@{shot_id}_STORYBOARD"]
        for snippet in required_snippets:
            if snippet not in shot_text:
                fail(f"{shot_id} missing required snippet: {snippet}")
        if "【English Prompt】" in shot_text:
            fail(f"{shot_id} contains English Prompt block")
        if "@PROP_" in shot_text:
            fail(f"{shot_id} contains @PROP reference")
        if "场景：" not in shot_text:
            fail(f"{shot_id} missing scene reference decision")
        if "音色：" not in shot_text:
            fail(f"{shot_id} missing audio reference decision")

        shot_audio_hint = " ".join(
            str(shot.get(key, "")) for key in ("audio_emotion", "prompt_cn", "narrative_function")
        )
        has_dialogue = bool(dialogue_patterns.search(shot_audio_hint))
        if has_dialogue and "@AUDIO_" not in shot_text:
            fail(f"{shot_id} appears to contain voice/dialogue but has no @AUDIO reference")

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
