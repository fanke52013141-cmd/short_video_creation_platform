#!/usr/bin/env python3
"""Build the final short-film resource package without adding a workflow phase."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

try:
    from .validate_project import validate_video_prompts
except ImportError:
    from validate_project import validate_video_prompts


def copy_tree(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if not source.is_dir():
        return
    for path in source.rglob("*"):
        target = destination / path.relative_to(source)
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def copy_if_exists(source: Path, destination: Path) -> None:
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def build_resource_package(run_dir: Path) -> Path:
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Run directory does not exist: {run_dir}")
    validate_video_prompts(run_dir)

    delivery_dir = run_dir / "outputs/07_final_delivery"
    package_dir = delivery_dir / "resource_package"
    staging_dir = delivery_dir / "resource_package.staging"
    if staging_dir.parent.resolve() != delivery_dir.resolve() or package_dir.parent.resolve() != delivery_dir.resolve():
        raise ValueError("Unsafe resource package path")
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    for folder in ("story", "storyboard", "characters", "scenes", "props", "audio", "video_prompts", "quality_reports"):
        (staging_dir / folder).mkdir(parents=True, exist_ok=True)

    copy_tree(run_dir / "outputs/01_story", staging_dir / "story")
    copy_tree(run_dir / "outputs/03_storyboard", staging_dir / "storyboard")
    copy_if_exists(run_dir / "outputs/02_art_direction/style_bible.md", staging_dir / "story/style_bible.md")
    copy_if_exists(run_dir / "outputs/02_art_direction/art_direction.json", staging_dir / "story/art_direction.json")
    copy_tree(run_dir / "outputs/04_assets/characters", staging_dir / "characters")
    copy_tree(run_dir / "outputs/04_assets/final_images/characters", staging_dir / "characters")
    copy_tree(run_dir / "outputs/04_assets/scenes", staging_dir / "scenes")
    copy_tree(run_dir / "outputs/04_assets/final_images/scenes", staging_dir / "scenes")
    copy_tree(run_dir / "outputs/04_assets/props", staging_dir / "props")
    copy_tree(run_dir / "outputs/04_assets/final_images/props", staging_dir / "props")
    copy_tree(run_dir / "outputs/04_assets/audio", staging_dir / "audio")
    copy_tree(run_dir / "outputs/05_video_prompts", staging_dir / "video_prompts")
    copy_if_exists(run_dir / "outputs/04_assets/asset_manifest.json", staging_dir / "asset_manifest.json")

    quality_files = (
        "outputs/03_storyboard/storyboard_sequence_review.md",
        "outputs/03_storyboard/storyboard_sequence_review.json",
        "outputs/05_video_prompts/video_prompt_review.json",
        "outputs/06_external_results/generated_media_review.md",
        "outputs/06_external_results/generated_media_review.json",
        "outputs/07_final_delivery/continuity_report.md",
        "outputs/07_final_delivery/continuity_report.json",
    )
    for relative in quality_files:
        source = run_dir / relative
        copy_if_exists(source, staging_dir / "quality_reports" / source.name)

    (staging_dir / "README.md").write_text(
        "# 短视频生成资源包\n\n"
        "- `story/`：故事、视觉方向\n"
        "- `storyboard/`：详细分镜、分镜图与分镜审查\n"
        "- `characters/`、`scenes/`、`props/`、`audio/`：分类资产\n"
        "- `video_prompts/`：逐镜提示词与跨镜连续性质检\n"
        "- `quality_reports/`：各阶段质检报告\n",
        encoding="utf-8",
    )
    if package_dir.exists():
        shutil.rmtree(package_dir)
    os.replace(staging_dir, package_dir)
    return package_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the final short-film resource package.")
    parser.add_argument("run_dir", help="Local run directory")
    args = parser.parse_args()
    try:
        package_dir = build_resource_package(Path(args.run_dir))
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Built resource package: {package_dir}")


if __name__ == "__main__":
    main()
