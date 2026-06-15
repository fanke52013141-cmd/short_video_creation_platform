# Storyboard Loop Protocol

分镜必须逐 shot 循环生成，不能只一次性生成总文件。

## 输出结构

```text
outputs/03_storyboard/
├── planning/
│   ├── story_beats.json
│   ├── shot_queue.json
│   ├── SHOT_001_PLAN.md
│   ├── SHOT_002_PLAN.md
│   └── ...
├── shots/
│   ├── SHOT_001_STORYBOARD.md
│   ├── SHOT_002_STORYBOARD.md
│   └── ...
├── storyboard.md
├── storyboard.json
└── draft_asset_sheet.json
```

用户最终主要查看 `storyboard.md`，但生成过程必须留下 `planning/` 和 `shots/` 中的单 shot 文件，用于证明每条镜头已经独立构思、独立生成、独立自检、可单独返修。

## 循环流程

对 `shot_queue.json` 中每个 shot 依次执行：

1. 读取当前 shot 绑定的 story beat。
2. 读取当前 shot 涉及的人物、场景、道具、情绪节点和视觉风格圣经。
3. 明确本 shot 的叙事功能、信息目标、情绪目标和观众心理距离。
4. 选择景别，并写明：
   - 推荐景别
   - 景别选择理由
   - 可替代景别
   - 为什么不用替代景别
5. 选择帧策略，并写明选择理由。
6. 选择运镜，并写明运动路径和选择理由。
7. 生成单 shot 分镜文件：`outputs/03_storyboard/shots/SHOT_XXX_STORYBOARD.md`。
8. 对当前 shot 自检。
9. 不合格则只重写当前 shot，不重写已通过 shot。
10. 全部 shot 通过后，再按顺序汇总为 `storyboard.md` 和 `storyboard.json`。

## Shot Planning 单文件结构

每个 `SHOT_XXX_PLAN.md` 必须包含：

```text
# SHOT_XXX Plan

- 绑定 story beat：
- 本镜头观众需要获得的信息：
- 本镜头观众应该产生的情绪：
- 角色心理距离：疏离 / 观察 / 贴近 / 压迫
- 推荐景别：
- 景别选择理由：
- 可替代景别：
- 为什么不用替代景别：
- 推荐帧策略：
- 帧策略选择理由：
- 推荐运镜：
- 运镜路径：
- 运镜选择理由：
- 与前一镜头的节奏关系：
- 与后一镜头的节奏关系：
```

## Storyboard 单文件结构

每个 `SHOT_XXX_STORYBOARD.md` 必须包含：

```text
# SHOT_XXX Storyboard

## 基础信息
- 时长：
- 景别：
- 引用资产：
- 叙事功能：
- 信息目标：
- 情绪目标：

## 镜头设计依据
- 景别选择理由：
- 帧策略选择理由：
- 运镜选择理由：

## 帧策略
- 类型：
- 锚定帧描述：

## 运镜
- 摄影机运动：
- 运动描述：

## 转场与蒙太奇
- 入场转场：
- 蒙太奇类型：
- 镜头间逻辑：

## 画面提示词
中文 Prompt：

## 音效/情绪提示
- 环境音：
- 情绪标注：

## 自检
- [ ] 绑定 story beat。
- [ ] 有明确叙事功能。
- [ ] 有信息目标和情绪目标。
- [ ] 有景别选择理由。
- [ ] 有帧策略选择理由。
- [ ] 有运镜选择理由。
- [ ] 引用资产 ID 稳定。
- [ ] 与前后镜头存在节奏关系。
```

## 自检规则

每个单 shot 文件必须检查：

- 是否绑定 story beat。
- 是否有明确叙事功能。
- 是否有信息目标和情绪目标。
- 是否有景别选择理由，而不是只填写景别名称。
- 是否有帧策略选择理由。
- 是否有运镜选择理由。
- 是否引用已登记或将进入草表的资产 ID。
- 是否与前后镜头存在节奏关系。
- 是否继承 `style_bible.md`，没有重新发明全片风格。

## 汇总规则

- `storyboard.md` 必须由 `shots/SHOT_XXX_STORYBOARD.md` 按顺序汇总。
- `storyboard.json` 必须与单 shot 文件字段一致。
- `draft_asset_sheet.json` 只能从已通过的单 shot 文件中提取，不得凭空补资产。
