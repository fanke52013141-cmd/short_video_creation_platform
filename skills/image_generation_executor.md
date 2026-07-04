# Skill: image_generation_executor
**Version**: 1.0.0

## Purpose
辅助人工在即梦生成图片资产。本 Skill 只保留 `external_manual` 模式，不再包含 `internal_codex` 分支。

本 Skill 不重新决定角色、场景、道具是否需要生成。它只消费资产提示词阶段产出的 Markdown，并整理人工生成时的执行清单。

## Inputs
```json
{
  "asset_manifest_path": "./outputs/asset_manifest.json",
  "asset_prompt_dir": "./outputs/assets",
  "generation_mode": "external_manual"
}
```

## Outputs
```json
{
  "manual_queue_path": "./outputs/image_generation_queue.md",
  "asset_output_dirs": {
    "characters": "./outputs/assets/characters",
    "scenes": "./outputs/assets/scenes",
    "props": "./outputs/assets/props"
  }
}
```

## Procedure
1. 读取 `asset_manifest.json`。
2. 读取 `outputs/assets/characters/*.md`、`outputs/assets/scenes/*.md`、`outputs/assets/props/*.md`。
3. 按角色 → 场景 → 道具顺序输出人工生成队列。
4. 明确每个资产生成完成后应保存到哪个目录。
5. 不调用图片生成能力，不生成本地图片，不维护外部结果 manifest。

## Quality Gate
- [ ] 只支持 `external_manual`。
- [ ] 队列覆盖所有 `generation_required=true` 的资产。
- [ ] 每个队列项指向一个可复制的提示词文件。
- [ ] 每个队列项声明生成后保存路径。
- [ ] 不出现 `internal_codex` 分支。

## Checkpoint Update
本 Skill 是辅助节点，不属于主流程强制阶段。若执行，通过后可更新：
- `artifacts.image_generation_queue`: `./outputs/image_generation_queue.md`

## Failure Handling
- 资产提示词缺失：返回对应的角色、场景或道具提示词生成器。
- 用户还未生成图片：停止在人工生成点，不伪造结果。
