#!/usr/bin/env python3
"""Validate a short-video creation local run."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT / "schemas"
MAX_SHOT_DURATION_SECONDS = 15
FRAME_ROLES = {"first_frame", "last_frame", "keyframe"}
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
        merged.update({key: value for key, value in node.items() if key != "$ref"})
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
        fail("checkpoint.phase_order does not match the simplified pipeline")
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
    for rel in [
        "inputs",
        "outputs/assets/characters",
        "outputs/assets/scenes",
        "outputs/assets/props",
        "outputs/storyboards",
        "references",
        "logs",
    ]:
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
        fail("style_bible.md must not contain a hard 构图倾向 section")
    if "## 禁止出现的视觉元素" in text:
        fail("style_bible.md must not contain a standalone 禁止出现的视觉元素 section")
    if len([line for line in text.splitlines() if line.strip()]) > 80:
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
            fail(f"{expected} contains legacy abstract asset IDs")
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
        fail("asset names must use stable names, not CHAR_/ENV_/PROP_ IDs")
    for group in ("characters", "scenes", "props"):
        for item in manifest.get(group, []) or []:
            if "prompt_outputs" in item:
                fail("asset_manifest.json must use output_prompt_path, not prompt_outputs")
            if item.get("generation_required") is True and not item.get("output_prompt_path"):
                fail(f"{item.get('asset_name')} generation_required=true but output_prompt_path is missing")
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
    for group in ("characters", "scenes", "props"):
        for item in manifest.get(group, []) or []:
            prompt_path = item.get("output_prompt_path")
            if item.get("generation_required") is True and prompt_path:
                require_file(run_dir / prompt_path.replace("./", ""))
    ok("asset prompt files checked")


def _shot_sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"(?m)^##\s+(S[0-9]{3})\b", text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[start:end]
    return sections


def _extract_field(section: str, field: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(field)}\s*:\s*([^\n]+)", section)
    return match.group(1).strip() if match else None


def validate_storyboard_prompt_generation(run_dir: Path) -> None:
    validate_assets(run_dir)
    storyboard = read_json(outputs(run_dir) / "storyboard.json")
    require_file(outputs(run_dir) / "storyboard_prompts.md")
    text = (outputs(run_dir) / "storyboard_prompts.md").read_text(encoding="utf-8")
    sections = _shot_sections(text)
    shots = storyboard.get("shots", [])
    by_id = {shot["shot_id"]: shot for shot in shots}
    for index, shot in enumerate(shots):
        shot_id = shot["shot_id"]
        section = sections.get(shot_id)
        if not section:
            fail(f"storyboard_prompts.md missing section for {shot_id}")
        role = _extract_field(section, "recommended_frame_role")
        if role not in FRAME_ROLES:
            fail(f"{shot_id} recommended_frame_role must be one of {sorted(FRAME_ROLES)}")
        uses_previous = _extract_field(section, "uses_previous_storyboard_reference")
        if uses_previous not in {"true", "false"}:
            fail(f"{shot_id} uses_previous_storyboard_reference must be true or false")
        if uses_previous == "true":
            if index == 0:
                fail(f"{shot_id} cannot reference previous storyboard; it is the first shot")
            source_shot_id = _extract_field(section, "source_shot_id")
            expected_prev = shots[index - 1]["shot_id"]
            if source_shot_id != expected_prev:
                fail(f"{shot_id} previous storyboard source must be {expected_prev}, got {source_shot_id}")
            if by_id[source_shot_id]["scene_id"] != shot["scene_id"]:
                fail(f"{shot_id} must not reference previous storyboard across scene_id")
            if "placement_anchor" not in section and "站位" not in section:
                fail(f"{shot_id} previous storyboard reference must be placement-only")
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


def _storyboard_index(storyboard: dict[str, Any]) -> dict[str, int]:
    return {shot["shot_id"]: index for index, shot in enumerate(storyboard.get("shots", []))}


def validate_video_prompt_plan(run_dir: Path, storyboard: dict[str, Any]) -> dict[str, Any]:
    plan = validate_schema_file(outputs(run_dir) / "video_prompts.json", "video_prompt.schema.json")
    videos = plan.get("videos", [])
    if not videos:
        fail("video_prompts.json has no videos")
    shots = storyboard.get("shots", [])
    valid_shots = [shot["shot_id"] for shot in shots]
    valid_shot_set = set(valid_shots)
    shot_index = _storyboard_index(storyboard)
    shot_by_id = {shot["shot_id"]: shot for shot in shots}
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
        source_indexes = [shot_index[shot_id] for shot_id in source_shots]
        if source_indexes != list(range(min(source_indexes), max(source_indexes) + 1)):
            fail(f"{video_id} source_shots must be contiguous")
        source_scene_ids = {shot_by_id[shot_id]["scene_id"] for shot_id in source_shots}
        if len(source_scene_ids) != 1:
            fail(f"{video_id} must not merge shots across scene_id")
        duration_sum = sum(shot_by_id[shot_id]["duration_seconds"] for shot_id in source_shots)
        if duration_sum > MAX_SHOT_DURATION_SECONDS:
            fail(f"{video_id} merged source_shots exceed {MAX_SHOT_DURATION_SECONDS}s")
        if len(source_shots) > 1:
            strategy = (video.get("merge_decision") or {}).get("strategy", "")
            if not strategy.startswith("merged_"):
                fail(f"{video_id} merged source_shots require a merged_* strategy")
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
    parser = argparse.ArgumentParser(description="Validate a simplified short-video local run.")
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
