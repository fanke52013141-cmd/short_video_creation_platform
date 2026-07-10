#!/usr/bin/env python3
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Import one generated asset into its canonical location.")
    parser.add_argument("run_dir")
    parser.add_argument("asset_id")
    parser.add_argument("source_file")
    args = parser.parse_args()
    run = Path(args.run_dir).resolve()
    source = Path(args.source_file).resolve()
    if not source.is_file() or source.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise SystemExit("Source must be an existing PNG, JPG, JPEG or WEBP image")
    manifest_path = run / "outputs/asset_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    match = None
    group_name = None
    for group in ("characters", "scenes", "props"):
        for item in data.get(group, []):
            if item.get("asset_id") == args.asset_id:
                match, group_name = item, group
    if not match:
        raise SystemExit(f"Unknown asset_id: {args.asset_id}")
    next_version = int(match.get("version") or 0) + 1
    target = run / "outputs" / "assets" / group_name / "images" / f"{match['asset_name']}.v{next_version:03d}{source.suffix.lower()}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise SystemExit(f"Refusing to overwrite versioned asset: {target}")
    shutil.copy2(source, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    match["source_path"] = source.as_posix()
    match["canonical_path"] = "./" + target.relative_to(run).as_posix()
    match["content_hash"] = f"sha256:{digest}"
    match["version"] = next_version
    match["approval_status"] = "pending"
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(match["canonical_path"])


if __name__ == "__main__":
    main()
