#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote visually reviewed storyboard images to approved references.")
    parser.add_argument("run_dir")
    parser.add_argument("review_json")
    args = parser.parse_args()
    run = Path(args.run_dir).resolve(); out = run / "outputs"
    review = json.loads(Path(args.review_json).resolve().read_text(encoding="utf-8"))
    if review.get("status") != "pass" or any(x.get("severity") == "P0" for x in review.get("issues", [])):
        raise SystemExit("Storyboard visual review is not pass")
    shots = [x["shot_id"] for x in json.loads((out / "storyboard.json").read_text(encoding="utf-8"))["shots"]]
    if review.get("checked_shots") != shots:
        raise SystemExit("Review must list every shot in order")
    target = out / "approved/storyboards"; target.mkdir(parents=True, exist_ok=True)
    for shot_id in shots:
        source = out / "storyboards" / f"{shot_id}.png"
        if not source.is_file():
            raise SystemExit(f"Missing storyboard: {shot_id}")
        destination = target / source.name
        if destination.exists():
            raise SystemExit(f"Approved storyboard already exists: {shot_id}")
        shutil.copy2(source, destination)
    print(f"Promoted {len(shots)} storyboard images")


if __name__ == "__main__":
    main()
