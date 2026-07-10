#!/usr/bin/env python3
"""Single stateful entrypoint for production stage control."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline_runtime import APPROVAL_REQUIRED, STAGES, gate_errors, invalidate_from, load_checkpoint, next_stage, now, save_checkpoint
from stage_gate import validate_stage_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect and control the guarded production pipeline.")
    parser.add_argument("run_dir")
    parser.add_argument("action", choices=["status", "start", "complete", "approve", "reject", "invalidate"])
    parser.add_argument("--stage", choices=STAGES)
    parser.add_argument("--reason", default="")
    args = parser.parse_args()
    run = Path(args.run_dir).resolve()
    cp = load_checkpoint(run)
    stage = args.stage or next_stage(cp)
    if args.action == "status":
        print(json.dumps({"current_stage": next_stage(cp), "stages": cp["stages"], "blockers": cp["blockers"]}, ensure_ascii=False, indent=2))
        return
    if not stage:
        raise SystemExit("Pipeline already complete")
    row = cp["stages"][stage]
    if args.action == "start":
        errors = gate_errors(run, cp, stage)
        if errors:
            raise SystemExit("BLOCKED:\n- " + "\n- ".join(errors))
        if row["status"] not in {"not_started", "failed", "blocked"}:
            raise SystemExit(f"Cannot start {stage} from {row['status']}")
        row.update({"status": "in_progress", "started_at": now(), "updated_at": now()})
    elif args.action == "complete":
        if row["status"] != "in_progress":
            raise SystemExit(f"Cannot complete {stage} from {row['status']}")
        try: validate_stage_outputs(run, stage)
        except ValueError as exc: raise SystemExit(f"BLOCKED: {exc}")
        row.update({"status": "review_required" if stage in APPROVAL_REQUIRED else "completed", "version": row.get("version", 0) + 1, "updated_at": now()})
    elif args.action == "approve":
        if stage not in APPROVAL_REQUIRED or row["status"] != "review_required":
            raise SystemExit(f"Cannot approve {stage} from {row['status']}")
        try: validate_stage_outputs(run, stage, approving=True)
        except ValueError as exc: raise SystemExit(f"BLOCKED: {exc}")
        row.update({"status": "approved", "approved_at": now(), "updated_at": now()})
    elif args.action == "reject":
        if row["status"] not in {"review_required", "in_progress"}:
            raise SystemExit(f"Cannot reject {stage} from {row['status']}")
        row.update({"status": "failed", "failure_reason": args.reason or "rejected", "updated_at": now()})
    elif args.action == "invalidate":
        invalidated = invalidate_from(cp, stage, args.reason or "upstream artifact changed")
        row.update({"status": "not_started", "updated_at": now()})
        print("Invalidated: " + ", ".join(invalidated))
    cp["current_phase"] = next_stage(cp) or "completed"
    cp["completed_phases"] = [s for s in STAGES if cp["stages"][s]["status"] in {"approved", "completed"}]
    save_checkpoint(run, cp)
    print(f"{stage}: {row['status']}")


if __name__ == "__main__":
    main()
