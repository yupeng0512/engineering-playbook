---
title: structured-outcome-review-loop
type: note
permalink: engineering-playbook/patterns/structured-outcome-review-loop
---

# 结构化结果复盘先于自适应推荐

## 场景

很多 AI copilot 都希望根据历史输赢、执行结果、用户反馈去优化下一次推荐。

常见例子：

- 销售机会的 win/loss learning
- 客服流程的 escalation reason 学习
- 运营动作的失败原因归因

## 问题

如果结果只以自由文本 note 的形式存在，后续很快会遇到三个问题：

- 很难稳定聚合成可计数、可排序的洞察
- 很难把结果真正喂回推荐层或生成层
- Agent 回答“最近为什么总输在这里”时只能复述个案，不能引用模式

## 推荐做法

### 1. 关闭事件先产出结构化 review

不要只记录一段 note，至少要有：

- `outcome_type`
- `summary`
- `reason_tags[]`
- `objection_tags[]`
- `competitor_tags[]`
- `closed_at`

### 2. 允许 AI 先给草稿，人再补充/修正

AI 很适合把 thread、执行记录、上下文先整理成 review draft。

但最终落库应该是一个结构化对象，而不是把 AI 原文直接当系统记忆。

### 3. 聚合层消费 review，而不是消费原始长上下文

推荐层和生成层不该每次重新读所有历史消息。

更稳的方式是：

1. review 落库
2. 聚合成 tagged counts / effectiveness / conversion
3. 再把 compact insights 喂给 queue、next action、package generation、agent explanation

## 原则

- **学习闭环先结构化，再智能化。**
- **推荐层引用证据，不直接引用散乱历史。**
- **生成层消费 compact insight，不消费无限长原始 transcript。**

## 适用场景

- 任何需要“从结果中学会下一次怎么做”的 copilot
- 希望让 dashboard、queue、agent 三处叙事一致的产品
- 需要在成本可控前提下做 adaptive recommendation 的系统

## 来源

TradeRadar 在 Closing Intelligence Milestone 中，把 closing review 结构化后再聚合成 closing insights，并反向注入 queue、next actions、commercial package generation 与 agent explanation。
