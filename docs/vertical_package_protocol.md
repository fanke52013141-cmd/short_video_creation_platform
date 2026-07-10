# Vertical Package Protocol

## 核心规则

垂类包是“策略覆盖层”，不是另一条流水线。稳定主流程由 `config/pipeline.yaml` 定义；每个垂类只通过 `skill_overrides` 替换策略槽，并通过配置增加该垂类的业务约束和质量门。

## 运行过程

1. 用户提交 brief，并选择或由 Codex 判断垂类。
2. `select-vertical` 读取对应 `config/verticals/<id>.yaml`。
3. 路由器解析五个策略槽：内容策略、艺术方向、分镜策略、提示词策略、垂类质量门。
4. 没有被覆盖的策略槽回落到 `config/pipeline.yaml` 的默认 Skill。
5. 资产登记、图片队列、两种生图执行、返图导入、结果登记、视频提示词和最终打包始终使用稳定内核。
6. 垂类质量门在最终打包前检查垂类特有目标。

## 同一流程的两个例子

### narrative

`skill_overrides` 为空，全部使用当前故事型默认策略。稳定内核不变。

### advertising

内容策略换成广告策略，艺术方向加入品牌/商品约束，分镜策略加入钩子、展示、证据和 CTA，提示词策略强化商品真实性，最后增加广告验收门。资产和图片流程仍完全相同。

## 新增一个垂类

1. 复制一个 vertical YAML，只填写业务参数和需要覆盖的策略槽。
2. 只为确实不同的策略创建正式 Skill；相同节点使用默认 Skill。
3. 保持稳定输出契约。额外结构化信息使用 sidecar 文件，不破坏 `story.md`、`style_bible.md`、`storyboard.json` 等共享产物。
4. 为垂类增加最终质量门。
5. 运行 `scripts/validate_vertical_config.py`，再用一个真实案例做端到端回归。

## 当前迁移状态

已建立路由骨架、两个垂类配置，并完成广告内容策略、广告艺术方向、广告分镜策略、广告提示词策略和广告质量门五个正式 Skill。图片队列和外部返图导入仍属于稳定内核的后续实现。
