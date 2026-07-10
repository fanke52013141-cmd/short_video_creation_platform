#!/usr/bin/env python3
"""Validate vertical profiles against the stable pipeline strategy slots."""

from __future__ import annotations

import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def scalar(text: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?([^\n\"']+)[\"']?\s*$", text)
    if not match:
        raise ValueError(f"missing scalar {key}")
    return match.group(1).strip()


def mapping_keys(text: str, section: str, child_indent: int) -> set[str]:
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line == f"{section}:"), None)
    if start is None:
        raise ValueError(f"missing section {section}")
    keys: set[str] = set()
    prefix = " " * child_indent
    for line in lines[start + 1 :]:
        if line and not line.startswith(" "):
            break
        match = re.match(rf"^{re.escape(prefix)}([a-z][a-z0-9_-]*):(?:\s*(.*))?$", line)
        if match:
            keys.add(match.group(1))
    return keys


def override_mapping(text: str) -> dict[str, str]:
    inline = re.search(r"(?m)^skill_overrides:\s*\{\s*\}\s*$", text)
    if inline:
        return {}
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if line == "skill_overrides:"), None)
    if start is None:
        raise ValueError("missing section skill_overrides")
    result: dict[str, str] = {}
    for line in lines[start + 1 :]:
        if line and not line.startswith(" "):
            break
        match = re.match(r"^  ([a-z][a-z0-9_-]*):\s*([a-z][a-z0-9-]*)\s*$", line)
        if match:
            result[match.group(1)] = match.group(2)
    return result


def main() -> None:
    pipeline_text = (ROOT / "config" / "pipeline.yaml").read_text(encoding="utf-8")
    slots = mapping_keys(pipeline_text, "strategy_slots", 2)
    if not slots:
        raise ValueError("pipeline has no strategy_slots")

    seen: set[str] = set()
    profiles = sorted((ROOT / "config" / "verticals").glob("*.yaml"))
    if not profiles:
        raise ValueError("no vertical profiles found")

    for path in profiles:
        text = path.read_text(encoding="utf-8")
        profile_id = scalar(text, "id")
        if profile_id in seen:
            raise ValueError(f"duplicate profile id: {profile_id}")
        seen.add(profile_id)
        overrides = override_mapping(text)
        unknown = set(overrides) - slots
        if unknown:
            raise ValueError(f"{profile_id} overrides unknown slots: {sorted(unknown)}")
        print(f"OK: {profile_id} ({len(overrides)} overrides)")

    default_section = re.search(r"(?ms)^vertical_selection:\n(?P<body>(?:^  .*\n?)+)", pipeline_text)
    if not default_section:
        raise ValueError("missing vertical_selection")
    default_id = scalar(default_section.group("body").replace("  ", "", 1), "default")
    if default_id not in seen:
        raise ValueError(f"default vertical not found: {default_id}")
    print("VALIDATION PASSED")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        sys.exit(1)
