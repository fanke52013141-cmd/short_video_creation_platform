#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute the minimal rerun boundary for a changed asset.")
    parser.add_argument("run_dir")
    parser.add_argument("asset_name")
    args = parser.parse_args()
    out = Path(args.run_dir).resolve() / "outputs"
    mapping = json.loads((out / "shot_asset_map.json").read_text(encoding="utf-8"))
    plan = json.loads((out / "video_segment_plan.json").read_text(encoding="utf-8"))
    shots = []
    for row in mapping["shot_assets"]:
        referenced = row["characters"] + row["scenes"] + row["props"]
        if args.asset_name in referenced:
            shots.append(row["shot_id"])
    shot_set = set(shots)
    videos = [x["video_id"] for x in plan["segments"] if shot_set.intersection(x["source_shots"])]
    result = {
        "changed_asset": args.asset_name,
        "affected_shots": shots,
        "affected_video_segments": videos,
        "rerun_from": "asset_image_generation" if shots else None
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
