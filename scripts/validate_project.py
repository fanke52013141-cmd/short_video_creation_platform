#!/usr/bin/env python3
"""Validate a short-video creation local run.

Usage:
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase initialized
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase all
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
MAX_SHOT_DURATION_SECONDS = 15
PHASE_ALIASES = {
    "init": "initialized",
    "art_direction": "art",
    "asset_executor": "assets",
    "asset_prompts": "asset_prompt_generation",
    "storyboard_prompts": "storyboard_prompt_generation",
    "video": "video_prompts",
}
REQUIRED_STYLE_HEADINGS = ["画面风格", "整体色调", "光线风格", "AI 视觉执行要求"]
FORBIDDEN_STORYBOARD_FIELDS = {
    "characters_in_shot",
    "location",
    "character_ids",
    "prop_ids",
    "asset_ids",
    "prompt_cn",
    "frame_strategy",
    "boundary_reason",
    "continuity_risk",
}
REQUIRED_VIDEO_PROMPT_SECTIONS = ["【自检通过项】", "【资产声明区】", "【中文视频提示词】"]
HIGH_INTENSITY_TERMS = re.compile(r"奔跑|跳跃|翻滚|剧烈打斗|打斗|快速追逐|追逐|摔倒|撞击|飞跃|爆炸")
OPERATION_TASK_TYPES = {"video_edit", "video_extend", "combined_task"}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"OK: {message}")


def warn(message: str) -> None:
    print(f"WARN: {message}")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {path} ({exc})")
    if not isinstance(data, dict):
        fail(f"JSON root must be object: {path}")
    return data


def require_file(path: Path) -> None:
    if not path.exists():
        fail(f"Required file missing: {path}")
    if not path.is_file():
        fail(f"Required path is not a file: {path}")


def require_dir(path: Path) -> None:
    if not path.exists():
        fail(f"Required directory missing: {path}")
    if not path.is_dir():
        fail(f"Required path is not a directory: {path}")


def schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_schema_subset(data: Any, schema: dict[str, Any], label: str) -> None:
    defs = schema.get("$defs", {})

    def resolve(node: dict[str, Any]) -> dict[str, Any]:
        ref = node.get("$ref")
        if not ref:
            return node
        if not ref.startswith("#/$defs/"):
            fail(f"{label}: unsupported schema ref {ref}")
        name = ref.split("/")[-1]
        if name not in defs:
            fail(f"{label}: missing schema def {name}")
        merged = dict(defs[name])
        merged.update({k: v for k, v in node.items() if k != "$ref"})
        return merged

    def check(value: Any, node: dict[str, Any], path: str) -> None:
        node = resolve(node)
        expected_type = node.get("type")
        if expected_type is not None:
            expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
            if not any(schema_type_matches(value, item) for item in expected_types):
                fail(f"{label}: {path} expected type {expected_types}, got {type(value).__name__}")
        if "enum" in node and value not in node["enum"]:
            fail(f"{label}: {path} value {value!r} not in enum {node['enum']}")
        if isinstance(value, str) and "pattern" in node and not re.search(node["pattern"], value):
            fail(f"{label}: {path} value {value!r} does not match {node['pattern']}")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "maximum" in node and value > node["maximum"]:
                fail(f"{label}: {path} value {value!r} is greater than maximum {node['maximum']}")
            if "minimum" in node and value < node["minimum"]:
                fail(f"{label}: {path} value {value!r} is less than minimum {node['minimum']}")
        if isinstance(value, dict):
            for required_key in node.get("required", []):
                if required_key not in value:
                    fail(f"{label}: {path}.{required_key} is required")
            for key, child_schema in node.get("properties", {}).items():
                if key in value:
                    check(value[key], child_schema, f"{path}.{key}")
        if isinstance(value, list) and "items" in node:
            for index, item in enumerate(value):
                check(item, node["items"], f"{path}[{index}]")

    check(data, schema, "$")
    ok(f"schema valid: {label}")


def validate_schema_file(data_path: Path, schema_name: str) -> dict[str, Any]:
    require_file(data_path)
    schema_path = SCHEMA_DIR / schema_name
    require_file(schema_path)
    data = read_json(data_path)
    schema = read_json(schema_path)
    validate_schema_subset(data, schema, data_path.name)
    return data


def normalize_phase(phase: str) -> str:
    return PHASE_ALIASES.get(phase, phase)


def outputs(run_dir: Path) -> Path:
    return run_dir / "outputs"


def validate_checkpoint(run_dir: Path) -> dict[str, Any]:
    checkpoint_path = run_dir / "checkpoint.json"
    require_file(checkpoint_path)
    checkpoint = read_json(checkpoint_path)
    required_order = [
        "story_generation",
        "art_direction",
        "storyboard_director",
        "asset_executor",
        "asset_prompt_generation",
        "storyboard_prompt_generator",
        "video_prompt_generator",
    ]
    if checkpoint.get("phase_order") != required_order:
        fail("checkpoint.phase_order does not match the simplified Jimeng pipeline")
    if checkpoint.get("current_phase") not in ["initialized", *required_order]:
        fail(f"unknown checkpoint.current_phase: {checkpoint.get('current_phase')}")
    completed = checkpoint.get("completed_phases", [])
    for phase in completed:
        if phase not in required_order:
            fail(f"unknown completed phase: {phase}")
    ok("checkpoint exists")
    return checkpoint


def validate_initialized(run_dir: Path) -> None:
    validate_checkpoint(run_dir)
    required_dirs = [
        "inputs",
        "outputs/assets/characters",
        "outputs/assets/scenes",
        "outputs/assets/props",
        "outputs/storyboards",
        "references",
        "logs",
    ]
    for rel in required_dirs:
        require_dir(run_dir / rel)
    require_file(run_dir / "inputs/idea_brief.md")
    ok("initialized run structure")


def validate_story(run_dir: Path) -> None:
    story_path = outputs(run_dir) / "story.md"
    require_file(story_path)
    text = story_path.read_text(encoding="utf-8").strip()
    if len(text) < 80:
        fail("story.md is too short to be a usable script/story output")
    if (outputs(run_dir) / "story.json").exists():
        fail("story.json is deprecated; story_generation must output story.md only")
    ok("story markdown")


def validate_art(run_dir: Path) -> None:
    style_path = outputs(run_dir) / "style_bible.md"
    require_file(style_path)
    text = style_path.read_text(encoding="utf-8")
    for heading in REQUIRED_STYLE_HEADINGS:
        if heading not in text:
            fail(f"style_bible.md missing required section: {heading}")
    if "## 构图倾向" in text:
        fail("style_bible.md must not contain a hard 构图倾向 section; composition belongs to storyboard_director")
    if "## 禁止出现的视觉元素" in text:
        fail("style_bible.md must not contain a standalone 禁止出现的视觉元素 section")
    non_empty_lines = [line for line in text.splitlines() if line.strip()]
    if len(non_empty_lines) > 80:
        fail("style_bible.md is too long; keep it within one page")
    if (outputs(run_dir) / "art_direction.json").exists():
        fail("art_direction.json is deprecated; use style_bible.md only")
    ok("style bible")


def validate_storyboard(run_dir: Path) -> dict[str, Any]:
    storyboard = validate_schema_file(outputs(run_dir) / "storyboard.json", "storyboard.schema.json")
    shots = storyboard.get("shots", [])
    if not shots:
        fail("storyboard.json has no shots")
    shot_ids = [shot.get("shot_id") for shot in shots]
    if len(shot_ids) != len(set(shot_ids)):
        fail("storyboard.json has duplicate shot_id values")
    for index, shot in enumerate(shots, start=1):
        expected = f"S{index:03d}"
        if shot.get("shot_id") != expected:
            fail(f"shot sequence must be contiguous: expected {expected}, got {shot.get('shot_id')}")
        scene_id = shot.get("scene_id")
        if not isinstance(scene_id, str) or not re.fullmatch(r"SC[0-9]{3}", scene_id):
            fail(f"{expected} scene_id must match SC###")
        duration = shot.get("duration_seconds")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool):
            fail(f"{expected} duration_seconds must be numeric")
        if duration <= 0 or duration > MAX_SHOT_DURATION_SECONDS:
            fail(f"{expected} duration_seconds must be > 0 and <= {MAX_SHOT_DURATION_SECONDS}")
        forbidden = sorted(FORBIDDEN_STORYBOARD_FIELDS.intersection(shot.keys()))
        if forbidden:
            fail(f"{expected} contains fields reserved for later stages: {', '.join(forbidden)}")
        if re.search(r"CHAR_|ENV_|PROP_|AUDIO_", json.dumps(shot, ensure_ascii=False)):
            fail(f"{expected} contains legacy abstract asset IDs; use scene_id and natural action description only")
    ok(f"storyboard shots: {len(shots)}")
    return storyboard


def _asset_names(manifest: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for group in ("characters", "scenes", "props"):
        for item in manifest.get(group, []) or []:
            name = item.get("asset_name")
            if name:
                names.add(name)
    return names


def validate_assets(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    storyboard = validate_storyboard(run_dir)
    manifest = validate_schema_file(outputs(run_dir) / "asset_manifest.json", "asset_manifest.schema.json")
    shot_map = validate_schema_file(outputs(run_dir) / "shot_asset_map.json", "shot_asset_map.schema.json")
    names = _asset_names(manifest)
    if len(names) != sum(len(manifest.get(group, []) or []) for group in ("characters", "scenes", "props")):
        fail("asset_manifest.json has duplicate asset_name values")
    if any(re.match(r"^(CHAR|ENV|PROP|AUDIO)_[0-9]{3}", name) for name in names):
        fail("asset names must use feature/state naming, not CHAR_/ENV_/PROP_ IDs")
    valid_shots = {shot["shot_id"] for shot in storyboard.get("shots", [])}
    mapped_shots = {item.get("shot_id") for item in shot_map.get("shot_assets", [])}
    missing_maps = valid_shots - mapped_shots
    if missing_maps:
        fail("shot_asset_map.json missing shots: " + ", ".join(sorted(missing_maps)))
    for item in shot_map.get("shot_assets", []) or []:
        for group in ("characters", "scenes", "props"):
            missing = sorted(set(item.get(group, []) or []) - names)
            if missing:
                fail(f"{item.get('shot_id')} references unknown assets in {group}: {', '.join(missing)}")
    ok(f"asset manifest assets: {len(names)}")
    return manifest, shot_map


def validate_asset_prompt_generation(run_dir: Path) -> None:
    manifest, _ = validate_assets(run_dir)
    prompt_dirs = {
        "characters": outputs(run_dir) / "assets" / "characters",
        "scenes": outputs(run_dir) / "assets" / "scenes",
        "props": outputs(run_dir) / "assets" / "props",
    }
    for group, directory in prompt_dirs.items():
        required_assets = [
            item["asset_name"]
            for item in manifest.get(group, []) or []
            if item.get("generation_required") is True
        ]
        for asset_name in required_assets:
            expected = directory / f"{asset_name}.md"
            if not expected.exists():
                warn(f"missing prompt file for {asset_name}: {expected}")
    ok("asset prompt directories checked")


def validate_storyboard_prompt_generation(run_dir: Path) -> None:
    validate_assets(run_dir)
    require_file(outputs(run_dir) / "storyboard_prompts.md")
    text = (outputs(run_dir) / "storyboard_prompts.md").read_text(encoding="utf-8")
    for shot in read_json(outputs(run_dir) / "storyboard.json").get("shots", []):
        if shot["shot_id"] not in text:
            fail(f"storyboard_prompts.md missing {shot['shot_id']}")
    ok("storyboard prompts")


def _declared_assets_by_role(text: str, role: str) -> list[str]:
    pattern = re.compile(r"@([^\s@（）()，,；;]+)[（(][^）)]*" + re.escape(role) + r"[^）)]*[）)]")
    return pattern.findall(text)


def _validate_operation_object_text(text: str, edit_assets: list[str], extend_assets: list[str]) -> None:
    for asset in edit_assets:
        if f"参考@{asset}" in text:
            fail(f"edit object @{asset} must not be referenced with 参考@")
        if not re.search(rf"严格编辑\s*@{re.escape(asset)}", text):
            fail(f"edit object @{asset} must be used with 严格编辑 @{asset}")
    for asset in extend_assets:
        if f"参考@{asset}" in text:
            fail(f"extend object @{asset} must not be referenced with 参考@")
        if not re.search(rf"向前延长\s*@{re.escape(asset)}|向后延长\s*@{re.escape(asset)}", text):
            fail(f"extend object @{asset} must be used with 向前延长/向后延长 @{asset}")


def validate_operation_object_usage(text: str) -> None:
    _validate_operation_object_text(
        text,
        _declared_assets_by_role(text, "编辑对象"),
        _declared_assets_by_role(text, "延长对象"),
    )


def validate_video_prompt_plan(run_dir: Path, storyboard: dict[str, Any]) -> dict[str, Any]:
    plan = validate_schema_file(outputs(run_dir) / "video_prompts.json", "video_prompt.schema.json")
    videos = plan.get("videos", [])
    if not videos:
        fail("video_prompts.json has no videos")
    valid_shots = [shot["shot_id"] for shot in storyboard.get("shots", [])]
    valid_shot_set = set(valid_shots)
    covered_shots: list[str] = []
    video_ids = [video.get("video_id") for video in videos]
    if len(video_ids) != len(set(video_ids)):
        fail("video_prompts.json has duplicate video_id values")
    for index, video in enumerate(videos, start=1):
        expected_video_id = f"V{index:03d}"
        video_id = video.get("video_id")
        if video_id != expected_video_id:
            fail(f"video sequence must be contiguous: expected {expected_video_id}, got {video_id}")
        duration = video.get("duration_seconds")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool):
            fail(f"{video_id} duration_seconds must be numeric")
        if duration <= 0 or duration > MAX_SHOT_DURATION_SECONDS:
            fail(f"{video_id} duration_seconds must be > 0 and <= {MAX_SHOT_DURATION_SECONDS}")
        source_shots = video.get("source_shots", [])
        unknown = sorted(set(source_shots) - valid_shot_set)
        if unknown:
            fail(f"{video_id} references unknown source_shots: {', '.join(unknown)}")
        covered_shots.extend(source_shots)

        prompt_cn = video.get("prompt_cn", "")
        if "English Prompt" in prompt_cn or "中英对照" in prompt_cn:
            fail(f"{video_id} prompt_cn must be Chinese-only")
        if "@PROP_" in prompt_cn or "PROP_" in prompt_cn:
            fail(f"{video_id} prop assets must be described in the body, not referenced as @PROP")
        if video.get("uses_previous_storyboard_anchor") is True and "参考@上一分镜_站位" not in prompt_cn:
            fail(f"{video_id} uses_previous_storyboard_anchor=true but prompt_cn is missing anchor text")
        if video.get("risk_notice_required") is True and "【生成风险提示】" not in prompt_cn:
            fail(f"{video_id} risk_notice_required=true but prompt_cn is missing 【生成风险提示】")
        declared_assets = video.get("declared_assets", []) or []
        edit_assets = [item["asset_name"] for item in declared_assets if item.get("role") == "edit_object"]
        extend_assets = [item["asset_name"] for item in declared_assets if item.get("role") == "extend_object"]
        if video.get("task_type") in OPERATION_TASK_TYPES and not (edit_assets or extend_assets or video.get("operation_objects")):
            fail(f"{video_id} operation task requires declared edit/extend operation objects")
        _validate_operation_object_text(prompt_cn, edit_assets, extend_assets)

    duplicate_shots = sorted({shot for shot in covered_shots if covered_shots.count(shot) > 1})
    if duplicate_shots:
        fail("video_prompts.json covers source shots more than once: " + ", ".join(duplicate_shots))
    missing_shots = sorted(valid_shot_set - set(covered_shots))
    if missing_shots:
        fail("video_prompts.json missing source shots: " + ", ".join(missing_shots))
    ok(f"video prompt plan videos: {len(videos)}")
    return plan


def validate_video_prompts(run_dir: Path) -> None:
    storyboard = validate_storyboard(run_dir)
    require_file(outputs(run_dir) / "video_prompts.md")
    text = (outputs(run_dir) / "video_prompts.md").read_text(encoding="utf-8")
    if "English Prompt" in text or "【English Prompt】" in text or "中英对照" in text:
        fail("English Prompt blocks are not allowed")
    if "@PROP_" in text or "PROP_" in text:
        fail("prop assets must be described in the prompt body, not referenced as @PROP")
    if not re.search(r"\bV[0-9]{3}\b", text):
        fail("video_prompts.md must contain V### prompt ids")
    for section in REQUIRED_VIDEO_PROMPT_SECTIONS:
        if section not in text:
            fail(f"video_prompts.md missing required section: {section}")
    for match in re.finditer(r"时长[：:]\s*([0-9]+(?:\.[0-9]+)?)\s*s", text):
        if float(match.group(1)) > MAX_SHOT_DURATION_SECONDS:
            fail("single video prompt duration must be <= 15s")
    same_scene_pairs = 0
    shots = storyboard.get("shots", [])
    for prev, current in zip(shots, shots[1:]):
        if prev.get("scene_id") == current.get("scene_id"):
            same_scene_pairs += 1
    if same_scene_pairs and "参考@上一分镜_站位" not in text:
        fail("same-scene continuity requires 参考@上一分镜_站位 anchor rule")
    if HIGH_INTENSITY_TERMS.search(text) and "【生成风险提示】" not in text:
        fail("high-intensity action prompts require 【生成风险提示】")
    validate_operation_object_usage(text)
    if "画面保持无字幕" not in text or "Logo" not in text or "水印" not in text:
        fail("video_prompts.md must include no-subtitle/no-logo/no-watermark constraints")
    validate_video_prompt_plan(run_dir, storyboard)
    ok("video prompts")


def validate_all(run_dir: Path) -> None:
    validate_initialized(run_dir)
    validate_story(run_dir)
    validate_art(run_dir)
    validate_assets(run_dir)
    validate_asset_prompt_generation(run_dir)
    validate_storyboard_prompt_generation(run_dir)
    validate_video_prompts(run_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a simplified Jimeng short-video local run.")
    parser.add_argument("run_dir", help="Local run directory")
    parser.add_argument(
        "--phase",
        default="all",
        choices=[
            "initialized",
            "init",
            "story",
            "art",
            "art_direction",
            "storyboard",
            "assets",
            "asset_executor",
            "asset_prompt_generation",
            "asset_prompts",
            "storyboard_prompt_generation",
            "storyboard_prompts",
            "video_prompts",
            "video",
            "all",
        ],
        help="Validation phase",
    )
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()
    if not run_dir.exists():
        fail(f"Run directory does not exist: {run_dir}")
    phase = normalize_phase(args.phase)
    validators = {
        "initialized": validate_initialized,
        "story": validate_story,
        "art": validate_art,
        "storyboard": validate_storyboard,
        "assets": validate_assets,
        "asset_prompt_generation": validate_asset_prompt_generation,
        "storyboard_prompt_generation": validate_storyboard_prompt_generation,
        "video_prompts": validate_video_prompts,
        "all": validate_all,
    }
    validators[phase](run_dir)
    print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
