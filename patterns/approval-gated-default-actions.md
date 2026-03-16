---
title: approval-gated-default-actions
type: pattern
permalink: engineering-playbook/patterns/approval-gated-default-actions
date: 2026-03-13
tags:
- approval
- checkpoint
- state-machine
- defaults
---

# Pattern: 审批门 + 默认动作，保证自治不卡死也不越界

## 问题

自治系统最常见的两个失败模式：

1. 没有默认动作，系统一旦等人就彻底停摆
2. 默认动作过于激进，系统会在无人确认时越过产品或技术边界

解决办法不是减少审批，而是：

**把审批压缩到少数高价值节点，并为每个阻塞态预先写好默认动作。**

## 审批触发器

以下情况必须发 checkpoint 并停下：

- 方向性决策：产品逻辑、用户流程、接口语义、收费策略
- 高影响技术决策：schema、权限模型、新依赖、迁移方案
- 低置信度分叉：存在 2 个以上合理方案，且无法从现有规范唯一确定
- 完成一个可验证阶段：PR、测试报告、截图、ADR、迁移计划已经齐
- 长时间无确认：连续运行 60-90 分钟需要主动报一次阶段状态
- 安全/外部系统边界：生产环境、支付、第三方后台、真实用户数据

## CheckpointPayload 固定八段

任何审批请求都必须使用固定模板：

1. 当前目标
2. 已完成内容
3. 证据
4. 未决问题
5. 候选方案 A / B
6. 推荐方案及理由
7. 风险
8. 超时默认动作

不允许只发一句“可以吗？”。

## 默认动作矩阵

| 场景 | 默认动作 | 禁止动作 |
|------|----------|----------|
| `blocked_on_decision` | 补测试、补文档、补低风险调研，或切到无依赖 sibling task | 擅自选方向方案 |
| `blocked_on_external` | 指数退避重试，并切换其他可做任务 | 伪造外部结果继续推进 |
| `ready_for_review` | 冻结实现，只整理证据包和 review 包 | 再继续做新改动 |
| `approval timeout` | 先提醒一次，超时后只执行低风险 backlog | 跨越 API/schema/依赖/产品边界 |

## 推荐计时规则

- `15 min`：提醒一次审批未处理
- `30 min`：审批超时，进入保守默认动作
- `60 min`：长运行 checkpoint

## Adapter 契约

审批通道可以替换，但 payload 结构不能变：

- Feishu card
- Slack message
- PR comment
- Local UI panel

通道只是投递层，状态机与默认动作仍由 runtime 统一控制。

## 评审时重点检查

- `requested` 状态是否一定附带完整 checkpoint
- `rejected` 后是否会回退到可恢复状态，而不是悬空
- `ready_for_review` 是否真的冻结推进
- silence 路径是否只执行低风险 backlog

## 来源

- OpenAI Computer use / human-in-the-loop: <https://platform.openai.com/docs/guides/tools-computer-use>
