# AI Short Film Pipeline

这是一个将现有优化提示词 scale 化为 CodeX/Skill 工作流的项目骨架。

设计原则：
- 原始提示词保存在 `skills/raw_prompts/`，作为不可随意改写的源文件。
- `skills/*.md` 只做接口化包装：定义输入、输出、质量门槛、Checkpoint 更新和上下游契约。
- 每个阶段必须产出文件，后续阶段只读取文件产物，不依赖对话记忆。
- 故事、视觉风格、分镜、资产、视频提示词之间通过稳定资产 ID 串联。
- 图片生成有两种模式：`internal_codex` 由 CodeX 直接调用图片生成能力；`external_manual` 由用户在外部网页端生成。每次进入图片阶段必须先确认模式。
- 视频生成和剪辑默认在外部网页端/剪映完成，项目只输出逐镜头中文视频提示词、参考素材声明和交接材料。
- 视频提示词统一只输出中文，避免中英双语导致提示词体量膨胀。

推荐试跑顺序：
1. 执行 `scripts/init_local_run.ps1 -ProjectSlug your-project-slug` 初始化本地创作目录。
2. 填写 `local_runs/YYYY-MM-DD/your-project-slug/inputs/idea_brief.md`。
3. 运行 `skills/story_generation.md`。
4. 人工确认故事后运行 `skills/art_direction.md`。
5. 人工确认视觉方向后运行 `skills/storyboard_director.md`。
6. 运行 `skills/asset_manifest_builder.md` 统一资产 ID。
7. 分别运行角色、场景、道具提示词 Skill。
8. 确认图片生成模式：外部生成则输出资产提示词；内部生成则用同一提示词调用 CodeX 图片生成并保存到本地 run。
9. 运行 `skills/shot_video_prompt_generator.md` 生成逐镜头中文视频提示词。
10. 运行 `skills/external_generation_handoff.md` 整理外部视频生成和剪辑交接包。
11. 将视频提示词复制到即梦/Seedance 等外部视频工具生成素材。
12. 运行 `skills/continuity_review.md` 做一致性审查。

仓库边界：
- 仓库保存流程、Skill、配置模板、检查规则和文档。
- 每天真实创作和外部生成结果放入本地 `local_runs/YYYY-MM-DD/project_slug/`。
- 本地创作产物、参考素材、生成图片/视频、日志和 `checkpoint.json` 不提交仓库。
- 详细规则见 `docs/repository_policy.md` 和 `docs/iteration_protocol.md`。
