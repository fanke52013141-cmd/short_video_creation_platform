#!/usr/bin/env python3
import argparse
from pathlib import Path

from pipeline_runtime import STAGES, load_checkpoint, save_checkpoint


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate a run checkpoint to the guarded 3.1 state model.")
    parser.add_argument("run_dir")
    parser.add_argument("--completed-through", choices=STAGES)
    args = parser.parse_args()
    run = Path(args.run_dir).resolve(); cp = load_checkpoint(run)
    if args.completed_through:
        end = STAGES.index(args.completed_through)
        for i, stage in enumerate(STAGES):
            cp["stages"][stage]["status"] = "approved" if stage in {"story_generation", "art_direction", "storyboard_sequence_review", "generated_asset_review", "storyboard_visual_review"} and i <= end else ("completed" if i <= end else "not_started")
    cp["schema_version"] = "3.1"
    cp["current_phase"] = next((x for x in STAGES if cp["stages"][x]["status"] == "not_started"), "completed")
    cp["completed_phases"] = [x for x in STAGES if cp["stages"][x]["status"] in {"approved", "completed"}]
    save_checkpoint(run, cp)
    print(f"Migrated checkpoint: {run}")


if __name__ == "__main__":
    main()
