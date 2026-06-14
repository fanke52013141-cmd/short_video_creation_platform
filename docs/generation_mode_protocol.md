# Generation Mode Protocol

图片生成阶段有两个分支。每次进入图片生成前，必须先确认用户选择哪一种模式。

## 模式

| 模式 | 说明 | Codex 动作 | 用户动作 |
|---|---|---|---|
| `external_manual` | 用户在外部网页端生成图片。 | 输出图片提示词、资产清单和复制说明。 | 复制提示词到外部工具生成图片。 |
| `internal_codex` | Codex 直接调用图片生成能力。 | 使用图片提示词生成图片并保存到本地 run。 | 审看结果，决定是否重生或进入下一阶段。 |

视频生成默认仍然是 `external_manual`。剪辑默认在剪映 / CapCut 等外部工具完成。

## 必问问题

进入角色、场景、道具或分镜图生成前，如果用户没有明确说明生成模式，询问：

```text
这一步图片资产你希望怎么生成：外部生成，还是由 Codex 直接生成？
```

不要在用户未确认时默认执行大批量图片生成。

## 共同流程

无论选择哪种模式，都必须先生成图片提示词：

1. 读取 `asset_manifest.json` 和 `style_bible.md`。
2. 按人物、场景、道具分别生成图片提示词。
3. 对文字类道具要求生成明确文字，并记录可后期修正说明。
4. 更新 `checkpoint.generation_modes.image_generation`。

## external_manual 分支

输出：

- `outputs/04_assets/characters/character_assets.md`
- `outputs/04_assets/scenes/scene_assets.md`
- `outputs/04_assets/props/prop_assets.md`
- 可选：`outputs/06_external_results/image_generation_handoff.md`

不得调用图片生成工具。

## internal_codex 分支

输出：

- 上述图片提示词文件。
- `outputs/04_assets/final_images/characters/*.png`
- `outputs/04_assets/final_images/scenes/*.png`
- `outputs/04_assets/final_images/props/*.png`
- `outputs/generated_image_index.md`

要求：

- 人物的不同年龄、服装、情绪或状态必须拆成独立图片，不放在同一张资产图里。
- 主要人物的每个状态变体必须生成三视图：正视图、侧视图、后视图。
- 场景资产必须保持年代、地域、光线和美术风格一致。
- 道具资产必须生成，即使后续视频提示词不 `@PROP`。
- 生成图片只属于本地 run，不提交仓库。

## Checkpoint 字段

建议写入：

```json
{
  "generation_modes": {
    "image_generation": "external_manual | internal_codex",
    "video_generation": "external_manual",
    "editing": "external_manual"
  }
}
```

## 失败处理

- 外部生成失败：记录到 `outputs/06_external_results/generation_log.csv`，保留提示词，标记重试原因。
- 内部生成失败：保留提示词，记录失败资产 ID，不覆盖已确认图片。
- 文字生成错误：优先重生 1-2 次；仍失败时标记为“需后期修正”，但保留构图可用版本。
