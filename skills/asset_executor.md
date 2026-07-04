# Skill: asset_executor
**Version**: 1.0.0

## Purpose
从 `story.md` 和 `storyboard.json` 中提取全部需要生产或描述的角色、场景、道具资产，并建立分镜到资产的映射。

本 Skill 是资产清单和分镜资产映射的唯一来源。它不写图片提示词，不生成图片，不决定视频合并。

## Inputs
```json
{
  "story_markdown_path": "./outputs/story.md",
  "storyboard_json_path": "./outputs/storyboard.json"
}
```

## Outputs
```json
{
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "shot_asset_map_path": "./outputs/shot_asset_map.json"
}
```

## Naming Policy
资产命名遵守“特征 + 状态”，避免 A/B/C 抽象编号。

| 类型 | 格式 | 示例 |
|---|---|---|
| 角色 | `{外貌特征}_{情绪状态}_{角度}` | `少女_默然_正面`、`少女_崩溃_侧面` |
| 场景 | `{地点名}_{时间/光线}_{氛围}` | `破旧公寓_深夜_冷白灯光` |
| 道具 | `{物品名}_{视角/状态}` | `旧皮箱_正面`、`血迹信封_特写` |

禁止把资产主标识命名为 `CHAR_001`、`ENV_001`、`PROP_001`。

## asset_manifest.json Contract

```json
{
  "naming_policy": "feature_state",
  "characters": [
    {
      "asset_name": "少女_默然_正面",
      "asset_type": "character",
      "base_name": "少女",
      "feature": "少女",
      "state": "默然",
      "angle_or_view": "正面",
      "visual_anchors": ["短发", "灰色外套"],
      "appears_in_shots": ["S001", "S002"],
      "generation_required": true,
      "prompt_scope": "single_character_all_states"
    }
  ],
  "scenes": [],
  "props": []
}
```

## shot_asset_map.json Contract

```json
{
  "shot_assets": [
    {
      "shot_id": "S001",
      "characters": ["少女_默然_正面"],
      "scenes": ["破旧公寓_深夜_冷白灯光"],
      "props": ["旧皮箱_正面"],
      "notes": "道具在桌面右前方，后续镜头保持位置。"
    }
  ]
}
```

## Procedure
1. 读取 `story.md`，提取角色、场景和关键道具候选。
2. 读取 `storyboard.json`，逐 shot 提取画面中实际需要的角色状态、场景状态和道具状态。
3. 合并同一资产的同义名称，保留最清晰的“特征 + 状态”命名。
4. 判断是否需要独立生成资产图：
   - 角色：只要在分镜中出现，通常需要生成。
   - 场景：只要作为视频空间出现，通常需要生成。
   - 道具：只有叙事关键、反复出现、特写、状态变化或复杂造型时生成；普通一次性物件可只写入后续提示词正文。
5. 写入 `asset_manifest.json`。
6. 为每个 shot 写入 `shot_asset_map.json`。
7. 校验所有映射资产都存在于资产清单。

## Quality Gate
- [ ] 覆盖所有分镜中需要稳定出现的角色、场景和关键道具。
- [ ] 每个资产名都使用特征 + 状态命名。
- [ ] 没有 `CHAR_001`、`ENV_001`、`PROP_001` 等抽象主标识。
- [ ] 每个 shot 都存在映射记录。
- [ ] `shot_asset_map.json` 中的所有资产都存在于 `asset_manifest.json`。
- [ ] 道具生成决策克制，不为普通一次性物件创建独立资产图。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `asset_executor`
- `completed_phases`: 追加 `asset_executor`
- `artifacts.asset_manifest`: `./outputs/asset_manifest.json`
- `artifacts.shot_asset_map`: `./outputs/shot_asset_map.json`
- `next_phase.skill`: `asset_prompt_generation`

## Failure Handling
- 分镜动作太抽象导致无法提取资产：返回 `storyboard_director` 修正 `action_desc`。
- 资产重名：保留更具体的状态命名，更新全部映射。
- 某 shot 缺少映射：补写该 shot 的角色、场景、道具关系。
