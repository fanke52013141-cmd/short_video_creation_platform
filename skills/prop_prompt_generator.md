# Skill: prop_prompt_generator
**Version**: 2.0.0

## Source Prompt
`skills/raw_prompts/prop_prompt_generator.source.md`

## Purpose
为单个道具资产生成即梦图片生成提示词。

一次只处理一个道具，不混入其他道具或角色设定。道具是否需要独立生成只由 `asset_executor` 决定。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "prop_asset_name": "旧皮箱_正面"
}
```

## Outputs
```json
{
  "prop_prompt_path": "./outputs/assets/props/旧皮箱_正面.md"
}
```

## Procedure
1. 读取 `story.md`。
2. 从 `asset_manifest.json` 中只切出本次道具资产。
3. 如果 `generation_required` 不是 true，输出“不生成独立道具资产”的原因，不生成最终图像提示词。
4. 需要生成时，输出单一物体的中文图片提示词。
5. 提示词必须包含：物品名、视角/状态、形状、材质、颜色、尺度、磨损、可识别细节、禁止项。
6. 文字类道具必须说明文字策略：直接生成、留白后期加字或不可读暗示。
7. 文件名必须与 `asset_name` 一致。

## Quality Gate
- [ ] 一次只处理一个道具。
- [ ] 只为 `generation_required=true` 的道具生成独立图片提示词。
- [ ] 没有为普通一次性背景物件强行生成独立道具资产。
- [ ] 道具在缩略图和特写中都可辨识。
- [ ] 材质、尺度、颜色、状态明确。
- [ ] 没有与角色或场景资产冲突。
- [ ] 不默认要求视频阶段使用 `@PROP`；道具写入视频提示词正文描述。

## Checkpoint Update
完成某道具后更新：
- `artifacts.assets.props.{asset_name}`: `./outputs/assets/props/{asset_name}.md`

全部道具完成后，`asset_prompt_generation` 的道具分支可标记完成。

## Failure Handling
- 道具定义不足：返回 `asset_executor` 补充状态、视角、生成理由或出现镜头。
- 道具不应生成：返回 `asset_executor` 将其标记为 `generation_required=false`。
- 文字策略缺失：返回 `asset_executor` 补充文字处理策略。
