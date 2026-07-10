#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from image_queue_runtime import eligible, load


def main() -> None:
    parser = argparse.ArgumentParser(description="Return the next resumable image task without duplicating completed work.")
    parser.add_argument("run_dir")
    args = parser.parse_args()
    queue = load(Path(args.run_dir).resolve() / "outputs/image_generation_queue.json")
    task = next((x for x in queue["tasks"] if eligible(x)), None)
    if not task:
        blocked = [x["task_id"] for x in queue["tasks"] if x["status"] == "blocked"]
        waiting = [x["task_id"] for x in queue["tasks"] if x["status"] == "waiting_for_provider"]
        print(json.dumps({"next_task": None, "waiting_for_provider": waiting, "blocked": blocked}, ensure_ascii=False, indent=2))
        return
    print(json.dumps({"next_task": task}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
