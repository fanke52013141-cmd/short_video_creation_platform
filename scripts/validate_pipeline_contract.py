#!/usr/bin/env python3
import re
from pathlib import Path
from pipeline_runtime import STAGES


ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "config/pipeline.yaml"


def main() -> None:
    text = PIPELINE.read_text(encoding="utf-8")
    skills = re.findall(r"^\s+(?:default_skill|skill):\s*([a-z0-9_-]+)\s*$", text, re.MULTILINE)
    def exists(name: str) -> bool:
        flat = ROOT / "skills" / f"{name}.md"
        directory = ROOT / "skills" / name.replace("_", "-") / "SKILL.md"
        return flat.is_file() or directory.is_file()
    missing = [name for name in skills if not exists(name)]
    required_stages = STAGES
    missing_stages = [stage for stage in required_stages if not re.search(rf"^\s+- id:\s*{stage}\s*$", text, re.MULTILINE)]
    declared = re.findall(r"^\s+- id:\s*([a-z0-9_-]+)\s*$", text, re.MULTILINE)
    ordered_core = [x for x in declared if x in STAGES]
    if missing or missing_stages or ordered_core != STAGES:
        if missing:
            print("Missing skill files: " + ", ".join(sorted(set(missing))))
        if missing_stages:
            print("Missing required stages: " + ", ".join(missing_stages))
        if ordered_core != STAGES:
            print("Core stage order does not match guarded runtime")
        raise SystemExit(1)
    print(f"OK: {len(skills)} pipeline skill references resolve")


if __name__ == "__main__":
    main()
