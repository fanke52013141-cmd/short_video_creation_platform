# Skill: scene_prompt_generator
**Version**: 1.0.0

## Source Prompt
`skills/raw_prompts/scene_prompt_generator.source.md`

## Purpose
为 `asset_manifest.json` 中的场景资产生成具有物理真实感、情绪张力和可复现视觉参数的自然语言画面描述。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/04_assets/asset_manifest.json",
  "style_bible_path": "./outputs/02_art_direction/style_bible.md",
  "scene_id": "ENV_001"
}
```

## Outputs
```json
{
  "scene_prompt_path": "./outputs/04_assets/scenes/ENV_001.md",
  "scene_prompt_json_path": "./outputs/04_assets/scenes/ENV_001.json"
}
```

## Procedure
1. 读取场景源提示词。
2. 读取场景资产、状态变体、出现镜头和视觉风格圣经。
3. 输出连贯自然语言画面描述，不堆关键词。
4. 若场景有多个状态，按 `ENV_001_A`、`ENV_001_B` 分别输出。

## Quality Gate
- [ ] 光线有方向、光比、色温。
- [ ] 镜头视角、焦段暗示、景深倾向明确。
- [ ] 材质、色彩、构图和情绪可执行。
- [ ] 不出现真实艺术家、摄影师、设计师人名。
- [ ] 与分镜和风格圣经一致。

## Checkpoint Update
通过质量门后更新：
- `artifacts.scenes.ENV_001`: `./outputs/04_assets/scenes/ENV_001.md`

## Failure Handling
- 场景定义过抽象：按源提示词补问真正影响画面质量的问题。
- 与分镜用途冲突：优先回到资产清单修正该场景定义。

