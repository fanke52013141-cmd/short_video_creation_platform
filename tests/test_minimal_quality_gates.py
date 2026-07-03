from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import build_resource_package
from scripts import validate_project


class MinimalQualityGateTests(unittest.TestCase):
    def test_original_thirteen_phases_are_unchanged(self) -> None:
        checkpoint = json.loads(
            (Path(__file__).parents[1] / "checkpoint.template.json").read_text(encoding="utf-8")
        )
        self.assertEqual(checkpoint["total_phases"], 13)
        self.assertEqual(len(checkpoint["phase_order"]), 13)

    def test_ai_review_cannot_skip_adjacent_shot(self) -> None:
        review = {
            "status": "pass",
            "checked_shots": ["SHOT_001", "SHOT_002", "SHOT_003"],
            "adjacent_checks": [
                {"shot_ids": ["SHOT_001", "SHOT_002"]},
            ],
        }
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            validate_project.validate_review_coverage(
                review,
                ["SHOT_001", "SHOT_002", "SHOT_003"],
                "fixture review",
            )

    def test_continuous_action_cannot_generate_independently(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            validate_project.validate_continuity_strategy(
                "SHOT_002",
                "match_action",
                "independent_clip",
            )
        validate_project.validate_continuity_strategy(
            "SHOT_002",
            "match_action",
            "previous_last_frame",
        )
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            validate_project.validate_continuity_strategy(
                "SHOT_002",
                "same_continuous_shot",
                "previous_last_frame",
            )

    def test_final_requires_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp)
            final_dir = run_dir / "outputs/07_final_delivery"
            final_dir.mkdir(parents=True)
            (final_dir / "continuity_report.json").write_text(
                json.dumps({"status": "pass", "issues": []}),
                encoding="utf-8",
            )
            (final_dir / "continuity_report.md").write_text("pass", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
                validate_project.validate_final(run_dir)

    def test_failed_continuity_report_blocks_final(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp)
            final_dir = run_dir / "outputs/07_final_delivery"
            final_dir.mkdir(parents=True)
            (final_dir / "continuity_report.json").write_text(
                json.dumps({"status": "revise_required", "issues": []}),
                encoding="utf-8",
            )
            (final_dir / "continuity_report.md").write_text("revise", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
                validate_project.validate_final(run_dir)

    def test_resource_package_uses_existing_asset_folders(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp)
            (run_dir / "outputs/01_story").mkdir(parents=True)
            (run_dir / "outputs/01_story/story.md").write_text("story", encoding="utf-8")
            (run_dir / "outputs/03_storyboard/keyframes").mkdir(parents=True)
            (run_dir / "outputs/03_storyboard/storyboard.md").write_text("storyboard", encoding="utf-8")
            (run_dir / "outputs/04_assets/characters").mkdir(parents=True)
            (run_dir / "outputs/04_assets/characters/CHAR_001.md").write_text("character", encoding="utf-8")
            (run_dir / "outputs/04_assets/scenes").mkdir(parents=True)
            (run_dir / "outputs/04_assets/props").mkdir(parents=True)
            (run_dir / "outputs/04_assets/audio").mkdir(parents=True)
            (run_dir / "outputs/05_video_prompts/shots").mkdir(parents=True)
            (run_dir / "outputs/05_video_prompts/shots/SHOT_001.md").write_text("prompt", encoding="utf-8")

            original_validator = build_resource_package.validate_video_prompts
            build_resource_package.validate_video_prompts = lambda _: None
            try:
                package_dir = build_resource_package.build_resource_package(run_dir)
            finally:
                build_resource_package.validate_video_prompts = original_validator

            self.assertTrue((package_dir / "story/story.md").is_file())
            self.assertTrue((package_dir / "storyboard/storyboard.md").is_file())
            self.assertTrue((package_dir / "characters/CHAR_001.md").is_file())
            self.assertTrue((package_dir / "scenes").is_dir())
            self.assertTrue((package_dir / "props").is_dir())
            self.assertTrue((package_dir / "audio").is_dir())
            self.assertTrue((package_dir / "video_prompts/shots/SHOT_001.md").is_file())
            self.assertTrue((package_dir / "quality_reports").is_dir())


if __name__ == "__main__":
    unittest.main()
