#!/usr/bin/env python3
import argparse
import json
import shutil
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build per-video production folders and final manifest.")
    parser.add_argument("run_dir")
    parser.add_argument("--mode", choices=["linked", "portable"], default="portable")
    args = parser.parse_args()
    run = Path(args.run_dir).resolve()
    outputs = run / "outputs"
    plan = json.loads((outputs / "video_segment_plan.json").read_text(encoding="utf-8"))
    assets = json.loads((outputs / "asset_manifest.json").read_text(encoding="utf-8"))
    shot_map = json.loads((outputs / "shot_asset_map.json").read_text(encoding="utf-8"))
    asset_by_name = {x["asset_name"]: x for g in ("characters", "scenes", "props") for x in assets.get(g, [])}
    shots = {x["shot_id"]: x for x in shot_map["shot_assets"]}
    artifacts, blockers = [], []
    for segment in plan["segments"]:
        video_id = segment["video_id"]
        folder = outputs / "approved/video_generation" / video_id
        refs = folder / "references"
        refs.mkdir(parents=True, exist_ok=True)
        prompt = folder / "prompt.txt"
        if not prompt.is_file():
            blockers.append(f"{video_id}: missing prompt.txt")
        names = set()
        for shot_id in segment["source_shots"]:
            board = outputs / "approved/storyboards" / f"{shot_id}.png"
            if board.is_file():
                if args.mode == "portable": shutil.copy2(board, refs / board.name)
            else:
                blockers.append(f"{video_id}: missing storyboard {shot_id}.png")
            row = shots[shot_id]
            names.update(row["characters"] + row["scenes"] + row["props"])
        for name in sorted(names):
            item = asset_by_name[name]
            path = item.get("canonical_path")
            if path:
                source = run / path.removeprefix("./")
                if source.is_file():
                    if args.mode == "portable": shutil.copy2(source, refs / source.name)
                elif item.get("generation_required"):
                    blockers.append(f"{video_id}: missing asset image {name}")
        segment_manifest = folder / "manifest.json"
        segment_copy = dict(segment)
        segment_copy["package_mode"] = args.mode
        segment_copy["reference_integrity"] = []
        for path in sorted(refs.glob("*")) if args.mode == "portable" else []:
            segment_copy["reference_integrity"].append({"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        segment_manifest.write_text(json.dumps(segment_copy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        artifacts.append({"video_id": video_id, "folder": "./" + folder.relative_to(run).as_posix(), "mode": args.mode})
    result = {
        "status": "completed" if not blockers else "revise_required",
        "artifacts": {"video_segments": artifacts},
        "quality_gates": {"completed_blockers_checked": True},
        "known_gaps": [],
        "blocking_issues": blockers,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    out = outputs / "final_package_manifest.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {out}")
    if blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
