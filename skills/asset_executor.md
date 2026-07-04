# Skill: asset_executor
**Version**: 1.4.0

## Purpose
从 `story.md` 和 `storyboard.json` 中固定后续生产需要的稳定资产：人物状态、场景和必要核心道具。

本 Skill 是资产命名、素材绑定和分镜资产映射的唯一来源。它不写图片提示词，不生成图片，不决定视频合并。

核心目标不是把资产拆成身份包，而是把每个需要生成图片提示词的资产固定成最小单位：

```text
asset_type + asset_name + output_prompt_path
```

其中人物资产名必须包含状态。不要默认把同一个人物拆成“人脸大头特写”和“全身妆造”两个输出。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "storyboard_json_path": "./outputs/storyboard.json",
  "reference_media": []
}
```

## Outputs
```json
{
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "shot_asset_map_path": "./outputs/shot_asset_map.json"
}
```

## Character Asset Naming

人物资产名采用：

```text
人物稳定名_状态
```

示例：

```text
林小满_基础状态
林小满_雨夜接电话状态
林小满_崩溃哭泣状态
警察_追捕状态
```

规则：

- `林小满` 是稳定人物名。
- `雨夜接电话状态` 是本次资产图要表现的状态。
- 同一人物可以有多个状态资产，但不能把状态资产命名成不同人物。
- 禁止默认输出 `林小满_人脸大头特写` 和 `林小满_全身妆造` 两个资产。
- 禁止用 `CHAR_001`、`AssetA` 之类内部 ID 当人物名。

人物状态不是“重新造一个人物”，而是同一人物在某个剧情状态下的一张资产参考图。

## Scene Asset Naming

场景资产名采用稳定场景名：

```text
雨夜客厅场景
宿舍场景
悬崖竹林场景
```

不因为普通光线、时间、天气变化拆新场景资产。只有空间结构、地点或叙事空间变化，才新建场景资产。

## Prop Handling

不需要把画面所有道具逐一生成或描述。只管控核心剧情道具。

道具分三类：

1. `inherited_from_reference`
   - 参考素材里已有的普通道具。
   - 默认保留，不单独生成，不额外描述。

2. `text_prompt_control`
   - 需要新增、出现、移动或被人物交互的关键道具。
   - 不生成独立道具图，后续在视频提示词正文中描述。

3. `generate_independent_prop`
   - 剧情关键、反复出现、需要特写、外形复杂或状态变化明显的道具。
   - 才生成独立道具资产提示词。

## asset_manifest.json Contract

```json
{
  "naming_policy": "asset_name_with_state_when_needed",
  "characters": [
    {
      "asset_type": "character",
      "asset_name": "林小满_雨夜接电话状态",
      "seedance_label": "林小满",
      "state": "雨夜接电话状态",
      "appears_in_shots": ["S001", "S002"],
      "generation_required": true,
      "handling_policy": "generate_character_state_reference",
      "output_prompt_path": "./outputs/assets/characters/林小满_雨夜接电话状态.md",
      "notes": "同一人物的状态资产，仍统一叫林小满"
    }
  ],
  "scenes": [
    {
      "asset_type": "scene",
      "asset_name": "雨夜客厅场景",
      "seedance_label": "雨夜客厅场景",
      "appears_in_shots": ["S001", "S002"],
      "generation_required": true,
      "handling_policy": "generate_scene_reference",
      "output_prompt_path": "./outputs/assets/scenes/雨夜客厅场景.md"
    }
  ],
  "props": [
    {
      "asset_type": "prop",
      "asset_name": "手机",
      "seedance_label": "手机",
      "appears_in_shots": ["S001", "S002"],
      "generation_required": false,
      "handling_policy": "text_prompt_control",
      "output_prompt_path": null,
      "notes": "普通手机不生成独立道具图，后续视频提示词正文控制"
    }
  ]
}
```

## Minimal Asset Prompt Input

资产提示词生成器每次只需要：

```json
{
  "story_markdown_path": "./outputs/story.md",
  "style_bible_path": "./outputs/style_bible.md",
  "asset_type": "character",
  "asset_name": "林小满_雨夜接电话状态",
  "output_prompt_path": "./outputs/assets/characters/林小满_雨夜接电话状态.md"
}
```

不需要：

- `task_id`
- `asset_payload`
- `usage_context`
- `generation_brief`
- `prompt_outputs` 数组
- 单独的 `asset_prompt_tasks.json`

## shot_asset_map.json Contract

```json
{
  "shot_assets": [
    {
      "shot_id": "S001",
      "characters": ["林小满_雨夜接电话状态"],
      "scenes": ["雨夜客厅场景"],
      "props": ["手机"]
    }
  ]
}
```

`shot_asset_map.json` 只映射稳定资产名，不写动作、不写提示词、不写素材分析。

## Procedure

1. 读取 `story.md`，识别剧情中的人物、地点、关键道具和用户参考素材关系。
2. 读取 `storyboard.json`，按 shot 判断实际出现的人物状态、场景和核心剧情道具。
3. 为人物资产命名为 `人物稳定名_状态`。
4. 不默认拆出人脸大头特写和全身妆造。
5. 为场景选择稳定场景名，不因普通光影、时间、天气变化新建场景资产。
6. 只保留核心剧情道具；普通背景小物件不进资产清单。
7. 判断 `generation_required` 和 `handling_policy`。
8. 为需要生成提示词的资产写入单个 `output_prompt_path`。
9. 写入 `asset_manifest.json`。
10. 为每个 shot 写入 `shot_asset_map.json`。
11. 校验所有映射资产都存在于资产清单。

## Quality Gate

- [ ] 人物资产名包含稳定人物名和状态，例如 `林小满_雨夜接电话状态`。
- [ ] 没有默认输出 `人脸大头特写` 和 `全身妆造` 两个资产。
- [ ] 未使用 `CHAR_001`、`ENV_001`、`PROP_001` 或抽象 Asset ID 作为主名称。
- [ ] 场景没有因为普通光线、时间、天气变化被拆分。
- [ ] 只有空间结构或地点变化才新建场景资产。
- [ ] 道具只保留核心剧情道具。
- [ ] 普通背景道具没有强行生成独立资产图。
- [ ] 每个需要生成提示词的资产只有一个 `output_prompt_path`。
- [ ] 没有输出 `asset_prompt_tasks.json`、`task_id`、`asset_payload` 或 `prompt_outputs` 数组。
- [ ] 每个 shot 都存在映射记录。
- [ ] `shot_asset_map.json` 中的所有资产都存在于 `asset_manifest.json`。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `asset_executor`
- `completed_phases`: 追加 `asset_executor`
- `artifacts.asset_manifest`: `./outputs/asset_manifest.json`
- `artifacts.shot_asset_map`: `./outputs/shot_asset_map.json`
- `next_phase.skill`: `asset_prompt_generation`

## Failure Handling

- 分镜动作太抽象导致无法判断人物状态：返回 `storyboard_director` 修正 `action_desc`。
- 人物状态资产被命名成另一个人物：改回 `人物稳定名_状态`。
- 默认拆成大头特写和全身妆造：合并为一个状态资产。
- 场景因光线/时间变化被拆成多个资产：合并为同一个场景资产，光影交给提示词控制。
- 普通道具被强行独立生成：改为 `text_prompt_control` 或从资产清单移除。
- 某 shot 缺少映射：补写该 shot 的人物状态、场景、关键道具关系。
