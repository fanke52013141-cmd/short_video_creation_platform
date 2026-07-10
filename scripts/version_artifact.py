#!/usr/bin/env python3
import argparse
import hashlib
import shutil
from pathlib import Path

from pipeline_runtime import invalidate_from, load_checkpoint, now, save_checkpoint

ARTIFACT_STAGE = {
    "story": "story_generation", "style_bible": "art_direction", "storyboard": "storyboard_director",
    "asset_manifest": "asset_executor", "shot_asset_map": "asset_executor",
    "video_segment_plan": "video_segment_planning",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a new immutable artifact version and invalidate dependent stages.")
    parser.add_argument("run_dir")
    parser.add_argument("artifact", choices=ARTIFACT_STAGE)
    parser.add_argument("source_file")
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    run = Path(args.run_dir).resolve(); source = Path(args.source_file).resolve()
    if not source.is_file():
        raise SystemExit("Source artifact does not exist")
    cp = load_checkpoint(run); current = cp["artifact_versions"].get(args.artifact, 0); version = current + 1
    suffix = "".join(source.suffixes) or ".dat"
    target = run / "outputs/versions" / args.artifact / f"{args.artifact}.v{version:03d}{suffix}"
    target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    cp["artifact_versions"][args.artifact] = version
    cp.setdefault("artifact_history", []).append({"artifact": args.artifact, "version": version, "path": "./" + target.relative_to(run).as_posix(), "sha256": digest, "reason": args.reason, "created_at": now()})
    invalidated = invalidate_from(cp, ARTIFACT_STAGE[args.artifact], args.reason)
    save_checkpoint(run, cp)
    print(f"{args.artifact} v{version:03d}; invalidated: {', '.join(invalidated) or 'none'}")


if __name__ == "__main__":
    main()
