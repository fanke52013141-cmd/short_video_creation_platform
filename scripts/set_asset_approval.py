#!/usr/bin/env python3
import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a structured generated-asset review to the manifest.")
    parser.add_argument("run_dir")
    parser.add_argument("asset_id")
    parser.add_argument("review_json")
    args = parser.parse_args()
    run = Path(args.run_dir).resolve(); review_path = Path(args.review_json).resolve()
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("asset_id") != args.asset_id:
        raise SystemExit("Review asset_id mismatch")
    manifest_path = run / "outputs/asset_manifest.json"; data = json.loads(manifest_path.read_text(encoding="utf-8"))
    item = None; group_name = None
    for group in ("characters", "scenes", "props"):
        for candidate in data[group]:
            if candidate.get("asset_id") == args.asset_id:
                item, group_name = candidate, group
    if not item:
        raise SystemExit("Unknown asset_id")
    if review.get("asset_version") != item.get("version"):
        raise SystemExit("Review version does not match current asset version")
    if review.get("status") == "pass":
        canonical = item.get("canonical_path")
        if not canonical or not (run / canonical.removeprefix("./")).is_file():
            raise SystemExit("Cannot approve without canonical image")
        source = run / canonical.removeprefix("./")
        approved = run / "outputs/approved/assets" / group_name / source.name
        approved.parent.mkdir(parents=True, exist_ok=True)
        if approved.exists():
            raise SystemExit(f"Approved version already exists: {approved}")
        shutil.copy2(source, approved)
        item.update({"approval_status": "approved", "working_image_path": canonical, "canonical_path": "./" + approved.relative_to(run).as_posix(), "approved_version": item["version"], "approved_at": datetime.now(timezone.utc).isoformat(), "review_report_path": "./" + review_path.relative_to(run).as_posix()})
    else:
        item.update({"approval_status": "rejected", "review_report_path": "./" + review_path.relative_to(run).as_posix(), "regeneration_instruction": "; ".join(x.get("regeneration_instruction", "") for x in review.get("issues", []) if x.get("regeneration_instruction"))})
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{item['asset_name']}: {item['approval_status']}")


if __name__ == "__main__":
    main()
