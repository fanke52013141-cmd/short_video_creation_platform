# Skill: scene_prompt_generator
**Version**: 2.0.0

## Source Prompt
`skills/raw_prompts/scene_prompt_generator.source.md`

## Purpose
为单个场景资产生成即梦图片生成提示词。

一次只处理一个场景，不混入其他场景设定。场景定义只来自 `asset_manifest.json`，本阶段不得新增、合并或重命名场景资产。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "scene_asset_name": "破旧公寓_深夜_冷白灯光"
}
```

## Outputs
```json
{
  "scene_prompt_path": "./outputs/assets/scenes/破旧公寓_深夜_冷白灯光.md"
}
```

## Procedure
1. 读取 `story.md`。
2. 从 `asset_manifest.json` 中只切出本次场景资产。
3. 输出一个可用于生成场景 Key Plate 的中文提示词。
4. 提示词必须包含：地点、时间/光线、氛围、空间结构、可拍摄路径、材质、尺度锚点、禁止项。
5. 不输出四宫格 Scene Sheet，除非用户明确要求。
6. 文件名必须与 `asset_name` 一致。

## Quality Gate
- [ ] 一次只处理一个场景。
- [ ] 场景提示词是单一场景图，不是拼贴、分屏或四宫格。
- [ ] 有前景、中景、背景三层或明确说明为何不需要。
- [ ] 光源有来源、方向、色温和阴影逻辑。
- [ ] 场景有尺度锚点。
- [ ] 与 `style_bible.md` 和分镜用途一致。
- [ ] 不使用真实艺术家、摄影师、建筑师、设计师姓名。
- [ ] 不使用模型专属语法。

## Checkpoint Update
完成某场景后更新：
- `artifacts.assets.scenes.{asset_name}`: `./outputs/assets/scenes/{asset_name}.md`

全部场景完成后，`asset_prompt_generation` 的场景分支可标记完成。

## Failure Handling
- 场景定义过抽象：返回 `asset_executor` 补充时间、光线、氛围或空间用途。
- 场景空间不支持分镜用途：返回 `storyboard_director` 或 `asset_executor` 修正。
- 输出成多个场景：拆回单个场景资产提示词。
