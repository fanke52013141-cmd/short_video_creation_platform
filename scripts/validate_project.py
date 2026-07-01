#!/usr/bin/env python3
"""Validate an AI short film local run.

Usage:
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase initialized
  python scripts/validate_project.py local_runs/YYYY-MM-DD/project_slug --phase video_prompts

Phases:
  initialized, story, art, storyboard, assets, audio,
  video_prompts, external, media_review, final, all
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
    "storyboard_sequence_review": "storyboard",
    "asset_manifest": "assets",
    "voice": "audio",
    "video": "video_prompts",
    "handoff": "external",
    "generated_media": "media_review",
}


CHARACTER_VARIANT_REQUIRED_TYPES = {
    "age_change",
    "wardrobe_change",
    "identity_uniform",
    "dirty_clothes",
    "wet_clothes",
    "damaged_wardrobe",
    "blood",
    "visible_wound",
    "scar",
    "bandage",
    "hair_change",
    "makeup_change",
    "body_shape_change",
    "nonhuman_transformation",
    "mechanical_transformation",
    "disguise",
    "ritual_state",
    "post_event_state",
    "other_persistent_visual_change",
}


TRANSIENT_CHARACTER_CHANGE_KEYWORDS = re.compile(
    r"表情|微笑|哭|皱眉|惊讶|愤怒|恐惧|动作|站立|奔跑|坐下|回头|伸手|弯腰|"
    r"近景|远景|侧面|背影|俯视|仰视|冷光|暖光|逆光|阴影|临时拿|拿着|握着|"
    r"汗水|轻微灰尘|短暂|一瞬间|镜头角度"
)


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
    """Small JSON-schema subset validator for this repo's contracts.

    It intentionally covers only the keywords used in schemas/: type, required,
    properties, items, enum, pattern and local $ref into $defs.
    Project-specific semantic checks are implemented separately below.
    """

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
        for key, value in node.items():
            if key != "$ref":
                merged[key] = value
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

        if isinstance(value, str) and "pattern" in node:
            if not re.search(node["pattern"], value):
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

    project = checkpoint.get("project")
    if isinstance(project, dict):
        for key in ("slug", "created_at", "run_dir"):
            if not project.get(key) or str(project.get(key)).startswith("__"):
                fail(f"checkpoint.project.{key} is not initialized")
        ok("checkpoint project metadata")
    else:
        warn("checkpoint.project is not an object; using legacy checkpoint shape")

    phase_order = checkpoint.get("phase_order", [])
    if phase_order:
        required_order = [
            "story_generation",
            "art_direction",
            "storyboard_director",
            "storyboard_sequence_review",
            "asset_manifest_builder",
        ]
        positions = {phase: phase_order.index(phase) for phase in phase_order}
        for earlier, later in zip(required_order, required_order[1:]):
            if earlier not in positions or later not in positions:
                fail(f"checkpoint.phase_order missing required phase: {earlier} or {later}")
            if positions[earlier] > positions[later]:
                fail(f"checkpoint.phase_order has invalid order: {earlier} after {later}")
        ok("checkpoint phase order")

    completed = checkpoint.get("completed_phases", [])
    if completed:
        if "asset_manifest_builder" in completed and "storyboard_sequence_review" not in completed:
            fail("asset_manifest_builder completed before storyboard_sequence_review")
        if phase_order:
            last_index = -1
            for phase in completed:
                if phase not in phase_order:
                    warn(f"completed phase not in checkpoint.phase_order: {phase}")
                    continue
                current_index = phase_order.index(phase)
                if current_index < last_index:
                    fail(f"completed_phases out of order at {phase}")
                last_index = current_index
        ok("checkpoint completed phase order")

    return checkpoint


def validate_initialized(run_dir: Path) -> None:
    validate_checkpoint(run_dir)
    required_dirs = [
        "inputs",
        "outputs/01_story",
        "outputs/02_art_direction",
        "outputs/03_storyboard",
        "outputs/03_storyboard/keyframes",
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
        "notes.md",
        "production_status.csv",
        "outputs/04_assets/audio/voice_reference_manifest.json",
        "outputs/06_external_results/image_result_manifest.json",
        "outputs/06_external_results/shot_result_manifest.template.json",
    ]
    for rel in required_files:
        require_file(run_dir / rel)
    ok("initialized run structure")


def validate_story(run_dir: Path) -> None:
    require_file(run_dir / "outputs" / "01_story" / "story.md")
    validate_schema_file(run_dir / "outputs" / "01_story" / "story.json", "story.schema.json")


def validate_art(run_dir: Path) -> None:
    require_file(run_dir / "outputs" / "02_art_direction" / "style_bible.md")
    validate_schema_file(run_dir / "outputs" / "02_art_direction" / "art_direction.json", "art_direction.schema.json")


def unresolved_issues(review: dict[str, Any], severity: str) -> list[dict[str, Any]]:
    issues = [item for item in review.get("issues", []) if item.get("severity") == severity]
    unresolved: list[dict[str, Any]] = []
    for item in issues:
        if item.get("fix_applied") is True or item.get("accepted_by_user") is True:
            continue
        if str(item.get("resolution_status", "")).lower() in {"fixed", "accepted", "resolved"}:
            continue
        unresolved.append(item)
    return unresolved


def validate_shot_contract(shot: dict[str, Any]) -> None:
    shot_id = shot.get("id") or "<missing id>"
    duration = shot.get("duration_seconds")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool):
        fail(f"{shot_id} duration_seconds must be a number")
    if duration <= 0:
        fail(f"{shot_id} duration_seconds must be greater than 0")
    if duration > MAX_SHOT_DURATION_SECONDS:
        fail(f"{shot_id} duration_seconds {duration} exceeds {MAX_SHOT_DURATION_SECONDS} seconds")

    boundary_type = str(shot.get("shot_boundary_type", "")).strip()
    if not boundary_type:
        fail(f"{shot_id} missing shot_boundary_type")

    boundary_reason = str(shot.get("boundary_reason", "")).strip()
    if not boundary_reason:
        fail(f"{shot_id} missing boundary_reason")
    if len(boundary_reason) < 8:
        fail(f"{shot_id} boundary_reason is too thin to justify an independent shot")


def validate_storyboard(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    storyboard = validate_schema_file(
        run_dir / "outputs" / "03_storyboard" / "storyboard.json",
        "storyboard.schema.json",
    )
    require_file(run_dir / "outputs" / "03_storyboard" / "storyboard.md")
    review = validate_schema_file(
        run_dir / "outputs" / "03_storyboard" / "storyboard_sequence_review.json",
        "storyboard_sequence_review.schema.json",
    )
    require_file(run_dir / "outputs" / "03_storyboard" / "storyboard_sequence_review.md")

    shots = storyboard.get("shots", [])
    if not shots:
        fail("storyboard.json has no shots")
    shot_ids = [shot.get("id") for shot in shots]
    if len(shot_ids) != len(set(shot_ids)):
        fail("storyboard.json has duplicate shot ids")
    for shot in shots:
        validate_shot_contract(shot)
    ok(f"storyboard shots: {len(shots)}")
    ok(f"storyboard shot duration limit: <= {MAX_SHOT_DURATION_SECONDS}s")
    ok("storyboard shot boundary metadata")

    if review.get("duration_check_passed") is False:
        fail("storyboard sequence review duration_check_passed=false")
    if review.get("shot_boundary_check_passed") is False:
        fail("storyboard sequence review shot_boundary_check_passed=false")
    if review.get("storytelling_quality_check_passed") is False:
        fail("storyboard sequence review storytelling_quality_check_passed=false")

    p0_unresolved = unresolved_issues(review, "P0")
    if p0_unresolved:
        fail(f"storyboard sequence review has unresolved P0 issues: {len(p0_unresolved)}")
    p1_unresolved = unresolved_issues(review, "P1")
    if p1_unresolved:
        fail(f"storyboard sequence review has unresolved P1 issues: {len(p1_unresolved)}")
    ok(f"storyboard sequence review: {review.get('status')}")
    return storyboard, review


def collect_storyboard_asset_refs(storyboard: dict[str, Any]) -> dict[str, set[str]]:
    refs = {"characters": set(), "scenes": set(), "props": set(), "audio": set()}
    for shot in storyboard.get("shots", []):
        scene_id = shot.get("scene_id")
        if scene_id:
            refs["scenes"].add(scene_id)
        for item in shot.get("character_ids", []) or []:
            refs["characters"].add(item)
        for item in shot.get("prop_ids", []) or []:
            refs["props"].add(item)
        audio = shot.get("audio_id") or shot.get("audio_reference_id")
        if audio:
            refs["audio"].add(audio)
    return refs


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def is_truthy_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "required", "1"}
    return False


def validate_character_variants(manifest: dict[str, Any]) -> None:
    checked_variants = 0
    generated_variants = 0
    for character in manifest.get("characters", []) or []:
        character_id = str(character.get("id", "<missing id>"))
        variants = as_list(character.get("variants"))
        identity_anchors = as_list(character.get("identity_anchors"))

        if variants and not identity_anchors:
            fail(f"{character_id} has variants but missing identity_anchors")

        seen_variant_ids: set[str] = set()
        for variant in variants:
            if not isinstance(variant, dict):
                fail(f"{character_id} variants must be objects")
            checked_variants += 1

            variant_id = str(variant.get("variant_id", "")).strip()
            if not variant_id:
                fail(f"{character_id} has variant missing variant_id")
            if variant_id in seen_variant_ids:
                fail(f"{character_id} duplicate variant_id: {variant_id}")
            seen_variant_ids.add(variant_id)

            if not variant_id.startswith(f"{character_id}_"):
                fail(f"{variant_id} must use parent character prefix {character_id}_")

            trigger = str(variant.get("trigger", "")).strip()
            if not trigger:
                fail(f"{variant_id} missing trigger")

            appears = variant.get("appears_in_shots")
            if not isinstance(appears, list) or not appears:
                fail(f"{variant_id} appears_in_shots must be a non-empty list")

            change_types = {str(item) for item in as_list(variant.get("appearance_change_type")) if item}
            visual_changes = str(variant.get("visual_changes", "")).strip()
            if change_types & CHARACTER_VARIANT_REQUIRED_TYPES and not visual_changes:
                fail(f"{variant_id} has persistent appearance change type but missing visual_changes")

            if TRANSIENT_CHARACTER_CHANGE_KEYWORDS.search(" ".join(sorted(change_types)) + " " + visual_changes):
                if not (change_types & CHARACTER_VARIANT_REQUIRED_TYPES):
                    warn(f"{variant_id} may be a transient action/expression variant; consider merging it")

            if is_truthy_flag(variant.get("generation_required")):
                generated_variants += 1
                if not visual_changes:
                    fail(f"{variant_id} generation_required=true but missing visual_changes")
                if not is_truthy_flag(variant.get("three_view_required")):
                    fail(f"{variant_id} generation_required=true but three_view_required is not true")
                must_keep = as_list(variant.get("must_keep"))
                if not must_keep:
                    fail(f"{variant_id} generation_required=true but missing must_keep identity anchors")

            must_not_mix_with = as_list(variant.get("must_not_mix_with"))
            if variant_id in {str(item) for item in must_not_mix_with}:
                fail(f"{variant_id} must_not_mix_with cannot include itself")

    ok(f"character variants checked: {checked_variants}")
    ok(f"character variants requiring generation: {generated_variants}")


def validate_assets(run_dir: Path) -> dict[str, Any]:
    storyboard, _ = validate_storyboard(run_dir)
    manifest = validate_schema_file(
        run_dir / "outputs" / "04_assets" / "asset_manifest.json",
        "asset_manifest.schema.json",
    )
    markdown_path = run_dir / "outputs" / "04_assets" / "asset_manifest.md"
    if markdown_path.exists():
        ok("asset manifest markdown")
    else:
        warn(f"asset manifest markdown missing: {markdown_path}")

    id_lists_by_group = {
        "characters": [item.get("id") for item in manifest.get("characters", []) if item.get("id")],
        "scenes": [item.get("id") for item in manifest.get("scenes", []) if item.get("id")],
        "props": [item.get("id") for item in manifest.get("props", []) if item.get("id")],
        "audio": [item.get("id") for item in manifest.get("audio", []) if item.get("id")],
    }
    ids_by_group = {group: set(ids) for group, ids in id_lists_by_group.items()}
    all_ids: list[str] = []
    for group, ids in id_lists_by_group.items():
        if len(ids) != len(set(ids)):
            fail(f"duplicate asset ids in {group}")
        all_ids.extend(ids)
    if len(all_ids) != len(set(all_ids)):
        fail("duplicate asset ids across asset groups")

    refs = collect_storyboard_asset_refs(storyboard)
    missing: list[str] = []
    for group, required_ids in refs.items():
        missing.extend(f"{group}:{asset_id}" for asset_id in sorted(required_ids - ids_by_group[group]))
    if missing:
        fail("storyboard references missing from asset_manifest.json: " + ", ".join(missing))
    ok("storyboard asset references resolved")
    validate_character_variants(manifest)
    return manifest


def validate_audio(run_dir: Path) -> dict[str, Any]:
    voice_manifest = validate_schema_file(
        run_dir / "outputs" / "04_assets" / "audio" / "voice_reference_manifest.json",
        "voice_reference_manifest.schema.json",
    )
    voice_ids = {item.get("id") for item in voice_manifest.get("voice_references", []) if item.get("id")}
    ok(f"voice references: {len(voice_ids)}")
    return voice_manifest


def shot_has_dialogue(shot: dict[str, Any]) -> bool:
    dialogue_patterns = re.compile(
        r"对白|旁白|台词|留言|录音|电话|新闻|播报|宣誓|祝福|低声|问：|说：|回答|“[^”]+”"
    )
    shot_audio_hint = " ".join(
        str(shot.get(key, "")) for key in ("audio_emotion", "audio_intent", "prompt_cn", "narrative_function")
    )
    return bool(dialogue_patterns.search(shot_audio_hint))


def validate_video_prompts(run_dir: Path) -> None:
    storyboard, _ = validate_storyboard(run_dir)
    validate_audio(run_dir)

    video_prompt_path = run_dir / "outputs" / "05_video_prompts" / "shot_video_prompts.md"
    single_shot_dir = run_dir / "outputs" / "05_video_prompts" / "shots"
    reference_path = run_dir / "outputs" / "05_video_prompts" / "video_prompt_asset_reference.md"
    require_file(video_prompt_path)
    require_dir(single_shot_dir)
    require_file(reference_path)

    prompt_text = video_prompt_path.read_text(encoding="utf-8")
    reference_text = reference_path.read_text(encoding="utf-8")
    shots = storyboard.get("shots", [])
    shot_count = len(shots)

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

    single_shot_files = sorted(single_shot_dir.glob("SHOT_*.md"))
    if len(single_shot_files) != shot_count:
        fail(f"single shot file count {len(single_shot_files)} does not match shot count {shot_count}")
    ok(f"single shot files: {len(single_shot_files)}")

    for shot in shots:
        shot_id = shot.get("id")
        if not shot_id:
            fail("shot missing id")
        shot_file = single_shot_dir / f"{shot_id}.md"
        require_file(shot_file)
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
        if shot_has_dialogue(shot) and "@AUDIO_" not in shot_text:
            fail(f"{shot_id} appears to contain voice/dialogue but has no @AUDIO reference")

        shot_json = single_shot_dir / f"{shot_id}.json"
        if shot_json.exists():
            validate_schema_file(shot_json, "shot_video_prompt.schema.json")

    reference_shot_map_count = len(re.findall(r"^\| `@SHOT_\d{3}_STORYBOARD`", reference_text, flags=re.MULTILINE))
    if reference_shot_map_count != shot_count:
        fail(f"storyboard reference map count {reference_shot_map_count} does not match shot count {shot_count}")
    ok(f"storyboard reference map: {reference_shot_map_count}")


def validate_external(run_dir: Path) -> None:
    require_file(run_dir / "outputs" / "06_external_results" / "external_generation_handoff.md")
    require_file(run_dir / "outputs" / "06_external_results" / "shot_result_manifest.template.json")
    require_file(run_dir / "outputs" / "06_external_results" / "edit_notes.md")
    image_manifest = run_dir / "outputs" / "06_external_results" / "image_result_manifest.json"
    if image_manifest.exists():
        validate_schema_file(image_manifest, "image_result_manifest.schema.json")
    ok("external generation handoff")


def validate_media_review(run_dir: Path) -> None:
    validate_schema_file(
        run_dir / "outputs" / "06_external_results" / "generated_media_review.json",
        "generated_media_review.schema.json",
    )
    require_file(run_dir / "outputs" / "06_external_results" / "generated_media_review.md")
    ok("generated media review")


def validate_final(run_dir: Path) -> None:
    validate_schema_file(
        run_dir / "outputs" / "07_final_delivery" / "continuity_report.json",
        "continuity_report.schema.json",
    )
    require_file(run_dir / "outputs" / "07_final_delivery" / "continuity_report.md")
    manifest_path = run_dir / "outputs" / "07_final_delivery" / "final_package_manifest.json"
    if manifest_path.exists():
        manifest = validate_schema_file(manifest_path, "final_package_manifest.schema.json")
        if manifest.get("status") == "completed":
            checkpoint = validate_checkpoint(run_dir)
            if checkpoint.get("known_gaps"):
                fail("final package is completed but checkpoint.known_gaps is not empty")
            if checkpoint.get("blocking_issues"):
                fail("final package is completed but checkpoint.blocking_issues is not empty")
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

    production_status_path = run_dir / "production_status.csv"
    if not production_status_path.exists():
        warn(f"production_status.csv missing: {production_status_path}")
    else:
        ok("production_status.csv exists")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an AI short film local run.")
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
            "storyboard_sequence_review",
            "assets",
            "asset_manifest",
            "audio",
            "voice",
            "video_prompts",
            "video",
            "external",
            "handoff",
            "media_review",
            "generated_media",
            "final",
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
