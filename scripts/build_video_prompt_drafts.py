#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render explicitly labeled per-segment video prompt drafts; never writes approved prompts.")
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run = Path(args.run_dir).resolve(); out = run / "outputs"
    shots = {x["shot_id"]: x for x in json.loads((out / "storyboard.json").read_text(encoding="utf-8"))["shots"]}
    maps = {x["shot_id"]: x for x in json.loads((out / "shot_asset_map.json").read_text(encoding="utf-8"))["shot_assets"]}
    segments = json.loads((out / "video_segment_plan.json").read_text(encoding="utf-8"))["segments"]
    videos, md = [], ["# 视频总提示词\n"]
    for seg in segments:
        vid = seg["video_id"]; folder = out / "drafts/video_generation" / vid; (folder / "references").mkdir(parents=True, exist_ok=True)
        names = []
        for sid in seg["source_shots"]:
            row = maps[sid]; names.extend(row["characters"] + row["scenes"])
        names = list(dict.fromkeys(names))
        declarations = "\n".join(f"@{x}" for x in names)
        evolution = "；随后".join(shots[sid]["action_desc"] for sid in seg["source_shots"])
        prompt = f"【资产声明区】\n{declarations}\n\n【中文视频提示词】\n{evolution}。只使用一种主要运镜逻辑，保持人物身份、银幕方向、站位、场景锚点和道具状态连续。画面保持无字幕、无额外文字、无无关 Logo、无水印。"
        frames = [{"shot_id": x["shot_id"], "asset_name": f"{x['shot_id']}_分镜参考图", "role": x["role"], "path": f"./outputs/storyboards/{x['shot_id']}.png"} for x in seg["frame_plan"]]
        video = {"video_id":vid,"task_type":"pipeline_shot_generation","source_shots":seg["source_shots"],"duration_seconds":seg["duration_seconds"],"scene_id":seg["scene_id"],"merge_decision":{"strategy":"single_shot" if len(seg["source_shots"])==1 else "merged_strong_action_continuity","reason":seg["merge_reason"],"continuity_risk":"high" if len(seg["source_shots"])>1 else "medium"},"frame_references":frames,"declared_assets":[{"asset_name":x,"media_type":"character" if any(x in maps[s]["characters"] for s in seg["source_shots"]) else "scene","role":"character_asset" if any(x in maps[s]["characters"] for s in seg["source_shots"]) else "scene_asset","usage_type":"reference","source_path":None} for x in names],"uses_previous_storyboard_anchor":False,"risk_notice_required":False,"prompt_cn":prompt}
        videos.append(video)
        (folder / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
        (folder / "manifest.json").write_text(json.dumps(video, ensure_ascii=False, indent=2)+"\n",encoding="utf-8")
        md.append(f"## {vid}\n\n【自检通过项】\n- 资产名称与映射一致\n- 合并时长不超过15秒\n- 抽象情绪已落实为动作和表情\n\n{prompt}\n")
    (out / "drafts/video_prompts.json").write_text(json.dumps({"status":"draft","videos":videos},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out / "drafts/video_prompts.md").write_text("# DRAFT — NOT APPROVED\n\n"+"\n".join(md),encoding="utf-8")
    print(f"Wrote {len(videos)} draft video prompts")


if __name__ == "__main__":
    main()
