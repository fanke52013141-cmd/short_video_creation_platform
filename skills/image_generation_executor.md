# Skill: image_generation_executor
**Version**: 1.3.0

## Purpose
执行单个资产图片生成任务。

本 Skill 不决定资产、不新增资产、不改名、不重写提示词。它只把已经定稿的资产提示词生成成一张图片文件。

## Input

```json
{
  "asset_type": "character",
  "asset_name": "林小满_雨夜居家装",
  "prompt_path": "./outputs/assets/characters/prompts/林小满_雨夜居家装.md",
  "generation_mode": "jimeng_web_manual | chatgpt_web | codex_direct | external_manual",
  "output_image_path": "./outputs/assets/characters/images/林小满_雨夜居家装.png"
}
```

不需要：

- `task_id`
- `output_count`
- `asset_payload`
- 完整 `story.md`
- 完整 `style_bible.md`
- 完整 `storyboard.json`

## Output

核心输出只有一张图片文件：

```text
./outputs/assets/characters/images/林小满_雨夜居家装.png
```

如果需要记录状态，使用执行日志，不新增主流程 JSON 产物。

## Character Image Rule

人物资产允许是一张 21:9 人物状态资产图。它可以在同一张图中包含：

```text
人物特写 / 正面 / 侧面 / 后视图
```

这仍然算一张人物资产图，不算多个输出。

## Scene Image Rule

场景资产只生成一张场景参考图。

## Prop Image Rule

只有 `generation_required=true` 且确实需要独立生成的核心道具，才生成道具图片。

## Quality Gate

- [ ] 一次只处理一个资产。
- [ ] 只生成一张图片文件。
- [ ] 人物资产图允许是 21:9 多视角单图。
- [ ] 不新增资产。
- [ ] 不修改资产名。
- [ ] 不输出额外 JSON 主产物。
