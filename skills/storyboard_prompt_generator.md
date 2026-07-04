# Skill: storyboard_prompt_generator
**Version**: 1.0.0

## Purpose
将导演分镜序列转化为可在即梦生成分镜参考图的中文生图提示词。

导演分镜是叙事语言，本 Skill 输出的是生成语言。不得直接复制 `action_desc` 当作图片提示词。

## Inputs
```json
{
  "storyboard_json_path": "./outputs/storyboard.json",
  "style_bible_path": "./outputs/style_bible.md",
  "shot_asset_map_path": "./outputs/shot_asset_map.json",
  "asset_reference_dir": "./outputs/assets"
}
```

## Outputs
```json
{
  "storyboard_prompts_path": "./outputs/storyboard_prompts.md"
}
```

## Prompt Contract
每个 `S###` 必须输出一条中文分镜生图提示词，包含：

- 分镜 ID
- 引用资产：角色、场景、必要道具
- 风格约束：从 `style_bible.md` 注入
- 画面主体和动作
- 景别和构图
- 光线和氛围
- 禁止项

## Procedure
1. 读取 `storyboard.json`。
2. 读取 `style_bible.md`，将全片风格统一注入每条提示词。
3. 读取 `shot_asset_map.json`，为每个 shot 查询对应资产。
4. 检查 `outputs/assets/**` 中是否已有参考图；有图时在提示词中声明“参考对应资产图”。
5. 将 `framing`、`camera_move`、`action_desc` 转换为静态分镜参考图描述。
6. 不生成视频动作时长、不生成视频提示词、不合并镜头。
7. 汇总输出 `outputs/storyboard_prompts.md`。

## Output Format

```markdown
# Storyboard Prompts

## S001
- 参考资产：少女_默然_正面；破旧公寓_深夜_冷白灯光；旧皮箱_正面
- 分镜生图提示词：...
- 禁止项：...
```

## Quality Gate
- [ ] 每个 `storyboard.json` 中的 shot 都有对应提示词。
- [ ] 每条提示词注入 `style_bible.md` 的核心约束。
- [ ] 每条提示词只描述静态分镜参考图，不写视频运动过程。
- [ ] 资产引用来自 `shot_asset_map.json`。
- [ ] 不新增未登记资产。
- [ ] 输出中文。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `storyboard_prompt_generator`
- `completed_phases`: 追加 `storyboard_prompt_generator`
- `artifacts.storyboard_prompts`: `./outputs/storyboard_prompts.md`
- `next_phase.skill`: `video_prompt_generator`

## Failure Handling
- 某 shot 缺少资产映射：返回 `asset_executor` 补齐。
- 静态分镜提示词无法生成：返回 `storyboard_director` 具象化 `action_desc`。
- 风格约束缺失：返回 `art_direction` 修订 `style_bible.md`。
