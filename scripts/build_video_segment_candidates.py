#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build hard-rule merge candidates for AI review; never writes an approved plan.")
    parser.add_argument("run_dir")
    parser.add_argument("--max-seconds", type=float, default=15)
    args = parser.parse_args()
    outputs = Path(args.run_dir).resolve() / "outputs"
    shots = json.loads((outputs / "storyboard.json").read_text(encoding="utf-8"))["shots"]
    segments, current = [], []
    for shot in shots:
        total = sum(x["duration_seconds"] for x in current)
        if current and (shot["scene_id"] != current[-1]["scene_id"] or total + shot["duration_seconds"] > args.max_seconds):
            segments.append(current); current = []
        current.append(shot)
    if current:
        segments.append(current)
    result = []
    for i, rows in enumerate(segments, 1):
        source = [x["shot_id"] for x in rows]
        result.append({
            "candidate_id": f"CAND-{i:03d}", "source_shots": source, "scene_id": rows[0]["scene_id"],
            "duration_seconds": sum(x["duration_seconds"] for x in rows),
            "hard_constraints_passed": True,
            "requires_ai_decision": len(rows) > 1
        })
    target = outputs / "drafts/video_segment_candidates.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"candidates": result}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} candidates for AI review")


if __name__ == "__main__":
    main()
