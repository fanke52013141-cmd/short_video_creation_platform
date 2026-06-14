# Skill: production_package_builder
**Version**: 0.1.0

## Purpose
汇总最终短片生产包，形成可交接、可归档、可复用的项目交付清单。

## Inputs
```json
{
  "checkpoint_path": "./checkpoint.json",
  "output_dir": "./outputs",
  "continuity_report_path": "./outputs/07_final_delivery/continuity_report.md"
}
```

## Outputs
```json
{
  "final_manifest_path": "./outputs/07_final_delivery/final_package_manifest.json",
  "final_readme_path": "./outputs/07_final_delivery/README.md"
}
```

## Procedure
1. 读取 `checkpoint.json` 和所有阶段产物路径。
2. 检查关键产物是否存在。
3. 生成最终交付清单，包含版本、Skill 源、产物路径、缺失项和后续待办。
4. 不重新创作内容，只做整理和归档。

## Quality Gate
- [ ] 所有必需产物路径存在。
- [ ] 每个产物能追溯到对应 Skill 和源提示词版本。
- [ ] 缺失项被明确标记，不伪装完成。

## Checkpoint Update
通过质量门后更新：
- `current_phase`: `production_package_builder`
- `completed_phases`: 追加 `production_package_builder`
- `status`: `completed`

## Failure Handling
- 缺失必需产物：输出缺失清单，不标记项目完成。

