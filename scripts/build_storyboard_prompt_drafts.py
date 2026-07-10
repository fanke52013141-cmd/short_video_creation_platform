#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render explicitly labeled storyboard prompt drafts for later AI replacement.")
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run = Path(args.run_dir).resolve(); out = run / "outputs"
    shots = json.loads((out / "storyboard.json").read_text(encoding="utf-8"))["shots"]
    maps = {x["shot_id"]: x for x in json.loads((out / "shot_asset_map.json").read_text(encoding="utf-8"))["shot_assets"]}
    plan = json.loads((out / "video_segment_plan.json").read_text(encoding="utf-8"))["segments"]
    roles = {x["shot_id"]: x["role"] for seg in plan for x in seg["frame_plan"]}
    folder = out / "drafts/storyboard_prompts"; folder.mkdir(parents=True, exist_ok=True)
    combined = ["# DRAFT Storyboard Prompts — NOT APPROVED\n"]
    for i, shot in enumerate(shots):
        sid = shot["shot_id"]; row = maps[sid]
        previous = shots[i-1] if i else None
        use_prev = bool(previous and previous["scene_id"] == shot["scene_id"])
        assets = [f"@{x}（人物资产）" for x in row["characters"]] + [f"@{x}（场景资产）" for x in row["scenes"]] + [f"{x}（道具）" for x in row["props"]]
        block = f"""## {sid}\n\nframe_role: {roles[sid]}\nuses_previous_storyboard_reference: {'true' if use_prev else 'false'}\nsource_shot_id: {previous['shot_id'] if use_prev else 'none'}\nreference_purpose: {'placement_anchor' if use_prev else 'none'}\n\n## 资产声明区\n""" + "\n".join(assets) + f"""\n\n## 中文分镜图提示词\n{'只继承上一分镜的人物相对位置、朝向和空间比例；' if use_prev else ''}{shot['framing']}，{shot['action_desc']} 运镜意图：{shot['camera_move']}。写实电影广告，16:9，遵守 style_bible.md；无额外文字、无无关Logo、无水印。\n"""
        (folder / f"{sid}.md").write_text(f"# {sid} 分镜参考图提示词\n\n" + block, encoding="utf-8")
        combined.append(block)
    (out / "drafts/storyboard_prompts.md").write_text("\n".join(combined), encoding="utf-8")
    print(f"Wrote {len(shots)} draft storyboard prompts")


if __name__ == "__main__":
    main()
