#!/usr/bin/env python3
"""Validate an AI short film local run.

Usage:
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase video
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase final
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
BLOCKING_IMAGE_STATUSES = {"missing", "rejected", "needs_regeneration"}
READY_IMAGE_STATUSES = {"generated", "approved"}
READY_AUDIO_STATUSES = {"provided", "approved", "ready"}
NOT_FINAL_AUDIO_STATUSES = {"missing", "needed", "placeholder"}

ABSTRACT_TERMS = re.compile(
    r"疲惫|压抑|紧张|孤独|温馨|神秘|犹豫|愤怒|委屈|亲密|疏离|对峙|等待|思考|难过|高级|克制|失控"
)
VISIBLE_EVIDENCE = re.compile(
    r"眼|眉|嘴|唇|下颌|肩|手|拳|指|呼吸|视线|身体|距离|前景|后景|阴影|顶光|侧光|色调|滴答|嗡鸣|风声|脚步|回响|敲|捏|靠|低头|抬手|转身|停顿"
)
DIALOGUE_HINT = re.compile(r"对白|旁白|台词|留言|录音|电话|新闻|播报|低声|说：|说道|回答|问：|“[^”]+”")
TASK_TYPES = {"pipeline_shot_generation", "multimodal_reference", "video_edit", "video_extend", "combined_task"}
REQUIRED_SEEDANCE_SECTIONS = ["【引用决策】", "【资产声明区】", "【中文视频提示词】", "【自检通过项】"]
CONTINUOUS_RELATIONS = {"match_action", "same_continuous_shot"}
CONTINUOUS_GENERATION_STRATEGIES = {"merge_with_previous", "previous_last_frame", "video_extend"}

PHASE_ALIASES = {
    "init": "initialized",
    "art_direction": "art",
    "storyboard_sequence_review": "storyboard",
    "asset_manifest": "assets",
    "voice": "audio",
    "video": "video_prompts",
    "handoff": "external",
    "generated_media": "media_review",
}

PROP_GENERATION_REASONS = {
    "repeated_appearance",
    "story_clue",
    "story_motif",
    "character_identity_bound",
    "close_up",
    "state_change",
    "text_or_symbol",
    "complex_design",
    "functional_story_action",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"WARN: {message}")


def ok(message: str) -> None:
    print(f"OK: {message}")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {path} ({exc})")


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


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


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


def validate_checkpoint(run_dir: Path) -> dict[str, Any]:
    checkpoint_path = run_dir / "checkpoint.json"
    require_file(checkpoint_path)
    checkpoint = read_json(checkpoint_path)
    completed = checkpoint.get("completed_phases", [])
    if completed and "asset_manifest_builder" in completed and "storyboard_sequence_review" not in completed:
        fail("asset_manifest_builder completed before storyboard_sequence_review")
    ok("checkpoint exists")
    return checkpoint


def validate_initialized(run_dir: Path) -> None:
    validate_checkpoint(run_dir)
    required_dirs = [
        "inputs",
        "outputs/01_story",
        "outputs/02_art_direction",
        "outputs/03_storyboard",
        "outputs/04_assets/characters",
        "outputs/04_assets/scenes",
        "outputs/04_assets/props",
        "outputs/04_assets/audio",
        "outputs/05_video_prompts/shots",
        "outputs/06_external_results",
        "outputs/07_final_delivery",
        "references",
        "logs",
    ]
    for rel in required_dirs:
        require_dir(run_dir / rel)
    required_files = [
        "inputs/idea_brief.md",
        "checkpoint.json",
        "production_status.csv",
        "outputs/04_assets/audio/voice_reference_manifest.json",
        "outputs/04_assets/image_generation_queue.json",
        "outputs/06_external_results/image_result_manifest.json",
        "outputs/06_external_results/shot_result_manifest.template.json",
    ]
    for rel in required_files:
        require_file(run_dir / rel)
    ok("initialized run structure")


def validate_story(run_dir: Path) -> None:
    require_file(run_dir / "outputs/01_story/story.md")
    validate_schema_file(run_dir / "outputs/01_story/story.json", "story.schema.json")


def validate_art(run_dir: Path) -> None:
    require_file(run_dir / "outputs/02_art_direction/style_bible.md")
    validate_schema_file(run_dir / "outputs/02_art_direction/art_direction.json", "art_direction.schema.json")


def unresolved_issues(review: dict[str, Any], severity: str) -> list[dict[str, Any]]:
    unresolved: list[dict[str, Any]] = []
    for item in review.get("issues", []) or []:
        if item.get("severity") != severity:
            continue
        if item.get("fix_applied") is True or item.get("accepted_by_user") is True:
            continue
        if str(item.get("resolution_status", "")).lower() in {"fixed", "accepted", "resolved"}:
            continue
        unresolved.append(item)
    return unresolved


def evidence_has_content(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(evidence_has_content(item) for item in value)
    if isinstance(value, dict):
        return any(evidence_has_content(item) for item in value.values())
    return False


def expected_adjacent_pairs(shot_ids: list[str]) -> list[list[str]]:
    return [[shot_ids[index - 1], shot_ids[index]] for index in range(1, len(shot_ids))]


def validate_review_coverage(review: dict[str, Any], shot_ids: list[str], label: str) -> list[dict[str, Any]]:
    if review.get("status") != "pass":
        fail(f"{label} status is not pass")
    if review.get("checked_shots") != shot_ids:
        fail(f"{label} checked_shots must exactly match storyboard order")
    adjacent_checks = review.get("adjacent_checks")
    if not isinstance(adjacent_checks, list):
        fail(f"{label} adjacent_checks must be an array")
    actual_pairs = [item.get("shot_ids") for item in adjacent_checks]
    expected_pairs = expected_adjacent_pairs(shot_ids)
    if actual_pairs != expected_pairs:
        fail(f"{label} adjacent checks mismatch; expected {expected_pairs}, got {actual_pairs}")
    return adjacent_checks


def validate_continuity_strategy(shot_id: str, relation: str, strategy: str) -> None:
    if relation in CONTINUOUS_RELATIONS and strategy not in CONTINUOUS_GENERATION_STRATEGIES:
        fail(f"{shot_id} continuous relation requires merge, previous last frame, or video extension")
    if relation == "same_continuous_shot" and strategy not in {"merge_with_previous", "video_extend"}:
        fail(f"{shot_id} same continuous shot must be merged or generated by video extension")


def validate_shot_contract(shot: dict[str, Any]) -> None:
    shot_id = shot.get("id") or "<missing id>"
    duration = shot.get("duration_seconds")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool):
        fail(f"{shot_id} duration_seconds must be a number")
    if duration <= 0 or duration > MAX_SHOT_DURATION_SECONDS:
        fail(f"{shot_id} duration_seconds must be > 0 and <= {MAX_SHOT_DURATION_SECONDS}")
    if len(str(shot.get("boundary_reason", "")).strip()) < 8:
        fail(f"{shot_id} boundary_reason is missing or too thin")
    prompt_cn = str(shot.get("prompt_cn", ""))
    terms = shot.get("abstract_terms_detected")
    evidence = shot.get("concretization_evidence")
    if terms is None:
        fail(f"{shot_id} missing abstract_terms_detected")
    if evidence is None or not evidence_has_content(evidence):
        fail(f"{shot_id} missing concretization_evidence")
    if ABSTRACT_TERMS.search(prompt_cn) and not VISIBLE_EVIDENCE.search(prompt_cn):
        fail(f"{shot_id} contains abstract terms but lacks visible/audio evidence in prompt_cn")
    for field in ("start_state", "end_state"):
        if not evidence_has_content(shot.get(field)):
            fail(f"{shot_id} missing {field}")


def validate_storyboard(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    storyboard = validate_schema_file(run_dir / "outputs/03_storyboard/storyboard.json", "storyboard.schema.json")
    require_file(run_dir / "outputs/03_storyboard/storyboard.md")
    review = validate_schema_file(run_dir / "outputs/03_storyboard/storyboard_sequence_review.json", "storyboard_sequence_review.schema.json")
    require_file(run_dir / "outputs/03_storyboard/storyboard_sequence_review.md")
    shots = storyboard.get("shots", [])
    if not shots:
        fail("storyboard.json has no shots")
    shot_ids = [shot.get("id") for shot in shots]
    if len(shot_ids) != len(set(shot_ids)):
        fail("storyboard.json has duplicate shot ids")
    for shot in shots:
        validate_shot_contract(shot)
    for index, shot in enumerate(shots):
        expected_previous = shots[index - 1].get("id") if index else None
        if shot.get("previous_shot_id") != expected_previous:
            fail(f"{shot.get('id')} previous_shot_id must be {expected_previous!r}")
        if index == 0 and shot.get("continuity_relation") != "sequence_start":
            fail(f"{shot.get('id')} must use continuity_relation=sequence_start")
        if index > 0 and shot.get("continuity_relation") == "sequence_start":
            fail(f"{shot.get('id')} cannot use continuity_relation=sequence_start")
        validate_continuity_strategy(
            str(shot.get("id")),
            str(shot.get("continuity_relation")),
            str(shot.get("recommended_generation")),
        )
    if review.get("duration_check_passed") is False:
        fail("storyboard sequence review duration_check_passed=false")
    if review.get("shot_boundary_check_passed") is False:
        fail("storyboard sequence review shot_boundary_check_passed=false")
    if review.get("concretization_check_passed") is not True:
        fail("storyboard sequence review concretization_check_passed is not true")
    if review.get("key_turning_point_visual_evidence_check_passed") is False:
        fail("key turning point visual evidence check failed")
    if review.get("storytelling_quality_check_passed") is False:
        fail("storyboard sequence review storytelling_quality_check_passed=false")
    adjacent_checks = validate_review_coverage(review, shot_ids, "storyboard sequence review")
    for index, item in enumerate(adjacent_checks, start=1):
        if item.get("shot_boundary_passed") is not True or item.get("continuity_passed") is not True:
            fail(f"storyboard adjacent review failed for {item.get('shot_ids')}")
        if item.get("suggested_generation") != shots[index].get("recommended_generation"):
            fail(f"storyboard generation suggestion mismatch for {shots[index].get('id')}")
    p0_unresolved = unresolved_issues(review, "P0")
    if p0_unresolved:
        fail(f"storyboard sequence review has unresolved P0 issues: {len(p0_unresolved)}")
    p1_unresolved = unresolved_issues(review, "P1")
    if p1_unresolved:
        fail(f"storyboard sequence review has unresolved P1 issues: {len(p1_unresolved)}")
    ok(f"storyboard shots: {len(shots)}")
    ok("storyboard concretization checks")
    return storyboard, review


def collect_storyboard_asset_refs(storyboard: dict[str, Any]) -> dict[str, set[str]]:
    refs = {"characters": set(), "scenes": set(), "props": set(), "audio": set()}
    for shot in storyboard.get("shots", []):
        if shot.get("scene_id"):
            refs["scenes"].add(shot["scene_id"])
        for item in shot.get("character_ids", []) or []:
            refs["characters"].add(item)
        for item in shot.get("prop_ids", []) or []:
            refs["props"].add(item)
        audio = shot.get("audio_id") or shot.get("audio_reference_id")
        if audio:
            refs["audio"].add(audio)
    return refs


def validate_assets(run_dir: Path) -> dict[str, Any]:
    storyboard, _ = validate_storyboard(run_dir)
    manifest = validate_schema_file(run_dir / "outputs/04_assets/asset_manifest.json", "asset_manifest.schema.json")
    ids_by_group = {
        "characters": {item.get("id") for item in manifest.get("characters", []) if item.get("id")},
        "scenes": {item.get("id") for item in manifest.get("scenes", []) if item.get("id")},
        "props": {item.get("id") for item in manifest.get("props", []) if item.get("id")},
        "audio": {item.get("id") for item in manifest.get("audio", []) if item.get("id")},
    }
    all_ids = [item for ids in ids_by_group.values() for item in ids]
    if len(all_ids) != len(set(all_ids)):
        fail("duplicate asset ids across asset groups")
    refs = collect_storyboard_asset_refs(storyboard)
    missing = []
    for group, required_ids in refs.items():
        missing.extend(f"{group}:{asset_id}" for asset_id in sorted(required_ids - ids_by_group[group]))
    if missing:
        fail("storyboard references missing from asset_manifest.json: " + ", ".join(missing))
    for prop in manifest.get("props", []) or []:
        prop_id = prop.get("id", "<missing prop>")
        if prop.get("generation_required") is True:
            if prop.get("asset_tier") != "canonical_prop":
                fail(f"{prop_id} generation_required=true but asset_tier is not canonical_prop")
            reasons = set(as_list(prop.get("reason_to_generate")))
            if not reasons:
                fail(f"{prop_id} generation_required=true but missing reason_to_generate")
            unknown = reasons - PROP_GENERATION_REASONS
            if unknown:
                fail(f"{prop_id} has unknown reason_to_generate values: {sorted(unknown)}")
            if not as_list(prop.get("must_not_change")):
                fail(f"{prop_id} generation_required=true but missing must_not_change")
        if prop.get("asset_tier") in {"scene_dressing", "shot_description_only"} and prop.get("generation_required") is True:
            fail(f"{prop_id} non-canonical prop tier cannot be generation_required=true")
    ok("asset manifest references and prop policy")
    return manifest


def validate_image_result_manifest(run_dir: Path, enforce_no_blocking_missing: bool = False) -> dict[str, Any]:
    manifest = validate_schema_file(run_dir / "outputs/06_external_results/image_result_manifest.json", "image_result_manifest.schema.json")
    queue_path = run_dir / "outputs/04_assets/image_generation_queue.json"
    if queue_path.exists():
        queue = read_json(queue_path)
        queue_items = queue.get("image_queue", queue.get("queue", []))
        if isinstance(queue_items, list):
            must_queue_ids = {item.get("queue_id") for item in queue_items if item.get("generation_priority") == "must_generate" and item.get("queue_id")}
            result_queue_ids = {item.get("queue_id") for item in manifest.get("image_results", []) if item.get("queue_id")}
            missing_queue_ids = sorted(must_queue_ids - result_queue_ids)
            if missing_queue_ids:
                fail("must_generate queue items missing from image_result_manifest.json: " + ", ".join(missing_queue_ids))
    blocking_missing = []
    for item in manifest.get("image_results", []) or []:
        asset_id = item.get("asset_id", "<missing asset_id>")
        role = item.get("image_role")
        status = item.get("status")
        if item.get("generation_priority") == "must_generate" and item.get("blocking_if_missing") is not True:
            fail(f"{asset_id}/{role} must_generate requires blocking_if_missing=true")
        if item.get("generation_priority") == "skip_generation" and status != "not_required":
            fail(f"{asset_id}/{role} skip_generation must use status=not_required")
        if item.get("blocking_if_missing") is True and status in BLOCKING_IMAGE_STATUSES:
            blocking_missing.append(f"{asset_id}/{role}:{status}")
        if item.get("used_as_video_reference") is True and status not in READY_IMAGE_STATUSES:
            fail(f"{asset_id}/{role} is marked used_as_video_reference but status is {status}")
    if enforce_no_blocking_missing and blocking_missing:
        fail("final completed is blocked by required image results: " + ", ".join(blocking_missing))
    if blocking_missing:
        warn(f"blocking image results not ready: {len(blocking_missing)}")
    ok(f"image results: {len(manifest.get('image_results', []))}")
    return manifest


def validate_audio(run_dir: Path, enforce_final_ready: bool = False) -> dict[str, Any]:
    voice_manifest = validate_schema_file(run_dir / "outputs/04_assets/audio/voice_reference_manifest.json", "voice_reference_manifest.schema.json")
    for item in voice_manifest.get("voice_references", []) or []:
        status = str(item.get("status", "")).lower()
        audio_id = item.get("id", "<missing audio id>")
        if enforce_final_ready and status in NOT_FINAL_AUDIO_STATUSES:
            fail(f"{audio_id} audio reference is {status}; final completed is not allowed")
    ok(f"voice references: {len(voice_manifest.get('voice_references', []))}")
    return voice_manifest


def shot_has_dialogue(shot: dict[str, Any]) -> bool:
    text = " ".join(str(shot.get(key, "")) for key in ("audio_emotion", "audio_intent", "prompt_cn", "narrative_function"))
    return bool(DIALOGUE_HINT.search(text))


def extract_cn_prompt(text: str) -> str:
    if "【中文视频提示词】" not in text:
        return ""
    content = text.split("【中文视频提示词】", 1)[1]
    if "【自检通过项】" in content:
        content = content.split("【自检通过项】", 1)[0]
    return content.strip()


def declared_task_type(text: str) -> str | None:
    for task_type in TASK_TYPES:
        if task_type in text:
            return task_type
    match = re.search(r"任务类型[：:]\s*([a-z_]+)", text)
    if match and match.group(1) in TASK_TYPES:
        return match.group(1)
    return None


def validate_seedance_shot_file(shot: dict[str, Any], shot_file: Path) -> None:
    require_file(shot_file)
    shot_id = shot.get("id")
    text = shot_file.read_text(encoding="utf-8")
    for section in REQUIRED_SEEDANCE_SECTIONS:
        if section not in text:
            fail(f"{shot_id} missing required section: {section}")
    if "【English Prompt】" in text or "English Prompt" in text or "中英对照" in text:
        fail(f"{shot_id} contains forbidden English/bilingual block")
    if f"@{shot_id}_STORYBOARD" not in text:
        fail(f"{shot_id} missing @{shot_id}_STORYBOARD reference")
    if "@PROP_" in text:
        fail(f"{shot_id} contains @PROP reference; props must be described in prompt body")
    task_type = declared_task_type(text)
    if not task_type:
        fail(f"{shot_id} missing Seedance task type declaration")
    cn_prompt = extract_cn_prompt(text)
    if not cn_prompt:
        fail(f"{shot_id} has empty 中文视频提示词 section")
    if task_type == "video_edit" and not re.search(r"严格编辑\s*@视频\d+", cn_prompt):
        fail(f"{shot_id} video_edit must use '严格编辑 @视频N'")
    if task_type == "video_extend" and not re.search(r"向前延长\s*@视频\d+|向后延长\s*@视频\d+", cn_prompt):
        fail(f"{shot_id} video_extend must use '向前延长 @视频N' or '向后延长 @视频N'")
    if task_type == "combined_task":
        has_reference = re.search(r"参考\s*@(?:图片|视频|音频)\d+", cn_prompt)
        has_operation = re.search(r"严格编辑\s*@视频\d+|向前延长\s*@视频\d+|向后延长\s*@视频\d+", cn_prompt)
        if not has_reference or not has_operation:
            fail(f"{shot_id} combined_task must include both reference and edit/extend operation")
    if shot_has_dialogue(shot) and "@AUDIO_" not in text:
        fail(f"{shot_id} appears to contain voice/dialogue but has no @AUDIO reference")
    if ("@AUDIO_" in text or re.search(r"@音频\d+", text)) and ("说道" in cn_prompt or "台词" in text) and "{" not in cn_prompt:
        fail(f"{shot_id} dialogue should use Seedance braces like {{台词内容}}")
    if "场景：" not in text:
        fail(f"{shot_id} missing scene reference decision")
    if "音色：" not in text:
        fail(f"{shot_id} missing audio reference decision")


def validate_video_prompts(run_dir: Path) -> None:
    storyboard, _ = validate_storyboard(run_dir)
    validate_audio(run_dir)
    validate_image_result_manifest(run_dir, enforce_no_blocking_missing=False)
    video_prompt_path = run_dir / "outputs/05_video_prompts/shot_video_prompts.md"
    single_shot_dir = run_dir / "outputs/05_video_prompts/shots"
    reference_path = run_dir / "outputs/05_video_prompts/video_prompt_asset_reference.md"
    require_file(video_prompt_path)
    require_dir(single_shot_dir)
    require_file(reference_path)
    prompt_text = video_prompt_path.read_text(encoding="utf-8")
    shots = storyboard.get("shots", [])
    if "【English Prompt】" in prompt_text or "English Prompt" in prompt_text:
        fail("English Prompt blocks are not allowed")
    if "@PROP_" in prompt_text:
        fail("@PROP references are not allowed by default")
    single_shot_files = sorted(single_shot_dir.glob("SHOT_*.md"))
    if len(single_shot_files) != len(shots):
        fail(f"single shot file count {len(single_shot_files)} does not match shot count {len(shots)}")
    for shot in shots:
        shot_id = shot.get("id")
        validate_seedance_shot_file(shot, single_shot_dir / f"{shot_id}.md")
        shot_json = single_shot_dir / f"{shot_id}.json"
        contract = validate_schema_file(shot_json, "shot_video_prompt.schema.json")
        for field in ("previous_shot_id", "continuity_relation", "start_state", "end_state"):
            if contract.get(field) != shot.get(field):
                fail(f"{shot_id} video prompt {field} does not match storyboard")
        strategy = contract.get("generation_strategy")
        if strategy != shot.get("recommended_generation"):
            fail(f"{shot_id} video generation strategy does not match storyboard review decision")
        validate_continuity_strategy(str(shot_id), str(contract.get("continuity_relation")), str(strategy))
        shot_text = shot_json.with_suffix(".md").read_text(encoding="utf-8")
        previous_id = contract.get("previous_shot_id")
        if strategy == "merge_with_previous":
            if not previous_id or "合并生成" not in shot_text or f"@{previous_id}_STORYBOARD" not in shot_text:
                fail(f"{shot_id} merge strategy must explicitly merge the previous storyboard")
        if strategy == "previous_last_frame":
            if not previous_id or f"@{previous_id}_LAST_FRAME" not in shot_text:
                fail(f"{shot_id} previous_last_frame strategy must reference @{previous_id}_LAST_FRAME")
        if strategy == "video_extend" and contract.get("task_type") not in {"video_extend", "combined_task"}:
            fail(f"{shot_id} video_extend strategy requires video_extend or combined_task")
    prompt_review = validate_schema_file(
        run_dir / "outputs/05_video_prompts/video_prompt_review.json",
        "video_prompt_review.schema.json",
    )
    shot_ids = [shot.get("id") for shot in shots]
    adjacent_checks = validate_review_coverage(prompt_review, shot_ids, "video prompt AI review")
    for item in adjacent_checks:
        if item.get("prompt_executable") is not True or item.get("continuity_passed") is not True:
            fail(f"video prompt AI review failed for {item.get('shot_ids')}")
        if item.get("breakthrough_risk") is True:
            fail(f"video prompt AI review found breakthrough risk for {item.get('shot_ids')}")
    for severity in ("P0", "P1"):
        pending = unresolved_issues(prompt_review, severity)
        if pending:
            fail(f"video prompt AI review has unresolved {severity} issues: {len(pending)}")
    ok(f"Seedance shot prompts: {len(shots)}")


def validate_external(run_dir: Path) -> None:
    require_file(run_dir / "outputs/06_external_results/external_generation_handoff.md")
    require_file(run_dir / "outputs/06_external_results/shot_result_manifest.template.json")
    require_file(run_dir / "outputs/06_external_results/edit_notes.md")
    validate_image_result_manifest(run_dir, enforce_no_blocking_missing=False)
    ok("external generation handoff")


def validate_media_review(run_dir: Path) -> None:
    review = validate_schema_file(run_dir / "outputs/06_external_results/generated_media_review.json", "generated_media_review.schema.json")
    require_file(run_dir / "outputs/06_external_results/generated_media_review.md")
    if review.get("status") == "pass" and unresolved_issues(review, "P0"):
        fail("generated media review has unresolved P0 while status=pass")
    ok("generated media review")


def validate_final(run_dir: Path) -> None:
    continuity = validate_schema_file(run_dir / "outputs/07_final_delivery/continuity_report.json", "continuity_report.schema.json")
    require_file(run_dir / "outputs/07_final_delivery/continuity_report.md")
    if continuity.get("status") != "pass":
        fail("continuity report status is not pass")
    manifest_path = run_dir / "outputs/07_final_delivery/final_package_manifest.json"
    manifest = validate_schema_file(manifest_path, "final_package_manifest.schema.json")
    if manifest.get("status") == "completed":
        checkpoint = validate_checkpoint(run_dir)
        if checkpoint.get("known_gaps"):
            fail("final package is completed but checkpoint.known_gaps is not empty")
        if checkpoint.get("blocking_issues"):
            fail("final package is completed but checkpoint.blocking_issues is not empty")
        if manifest.get("quality_gates", {}).get("video_prompt_review_passed") is not True:
            fail("final completed requires video_prompt_review_passed=true")
        validate_image_result_manifest(run_dir, enforce_no_blocking_missing=True)
        validate_audio(run_dir, enforce_final_ready=True)
        media_review = validate_schema_file(
            run_dir / "outputs/06_external_results/generated_media_review.json",
            "generated_media_review.schema.json",
        )
        if media_review.get("status") != "pass":
            fail("final completed requires generated_media_review status=pass")
        if unresolved_issues(media_review, "P0"):
            fail("final completed blocked by generated media P0 issues")
        package_dir = run_dir / "outputs/07_final_delivery/resource_package"
        for rel in ("story", "storyboard", "characters", "scenes", "props", "audio", "video_prompts", "quality_reports"):
            require_dir(package_dir / rel)
    ok("final delivery")


def validate_all(run_dir: Path) -> None:
    validate_initialized(run_dir)
    validate_story(run_dir)
    validate_art(run_dir)
    validate_assets(run_dir)
    validate_video_prompts(run_dir)
    validate_external(run_dir)
    validate_media_review(run_dir)
    validate_final(run_dir)
    ok("production_status.csv exists" if (run_dir / "production_status.csv").exists() else "production_status.csv optional")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an AI short film local run.")
    parser.add_argument("run_dir", help="Local run directory")
    parser.add_argument(
        "--phase",
        default="all",
        choices=[
            "initialized", "init", "story", "art", "art_direction", "storyboard", "storyboard_sequence_review",
            "assets", "asset_manifest", "audio", "voice", "video_prompts", "video", "external", "handoff",
            "media_review", "generated_media", "final", "all",
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
        "audio": validate_audio,
        "video_prompts": validate_video_prompts,
        "external": validate_external,
        "media_review": validate_media_review,
        "final": validate_final,
        "all": validate_all,
    }
    validators[phase](run_dir)
    print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
