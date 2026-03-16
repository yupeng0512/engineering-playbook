---
title: analysis-execution-send-layering
type: note
permalink: engineering-playbook/patterns/analysis-execution-send-layering
---

# AI Copilot 工作流对象分层：分析层、执行层、发送层分开

## 场景

在 AI 辅助销售、客服、运营这类工作流产品里，系统往往需要同时处理三类东西：

- 对当前上下文的理解与诊断
- 可执行的动作包或计划
- 真实会触发外部副作用的发送/执行请求

如果一开始没有把这三层拆开，项目很容易把所有内容都塞进一个 `JSON` 字段、一个 `draft` 对象，或者一个“万能任务”里。

## 问题

把三层混在一起，通常会带来几类问题：

- 分析结果和执行状态耦合，后续字段只会越堆越乱
- AI 一生成内容就天然靠近真实发送边界，审批门变得含糊
- 页面展示、排序、权限控制、状态机都很难各自演进
- “重新生成建议”和“真正创建外部副作用对象”无法解耦

## 推荐分层

### 1. 分析层

负责理解事实、提炼诊断，不直接承载执行状态。

例子：

- RFQ brief
- reply qualification
- missing information / blockers
- recommended next step

### 2. 执行层

负责把分析结果转成可审阅、可编辑、可排序、可归档的动作包。

例子：

- proposal-prep package
- sample follow-up package
- meeting package
- clarification package

### 3. 发送层

负责真正进入外部系统的副作用对象，例如邮件草稿、消息发送请求、工单执行。

例子：

- reply draft
- send queue item
- provider job

## 关键原则

- **生成执行包，不等于创建真实草稿。**
- **进入发送队列必须是显式动作。**
- **分析对象不承载执行生命周期。**
- **执行对象可以反复刷新或 supersede，但不应自动越过审批边界。**

## 推荐状态机思路

1. 先生成分析对象
2. 基于分析对象生成执行包
3. 人工检查/编辑执行包
4. 显式推入发送队列
5. 再由发送层走审批、发送、回执、已答复等生命周期

## 适用场景

- 需要 approval gate 的 AI copilot
- 真实发送或外部调用成本高、风险高的系统
- 页面需要同时展示“为什么这样做”和“准备怎么做”的产品

## 来源

TradeRadar Phase 15 把 `OpportunityBrief`、`CommercialPackage`、`ReplyDraft` 拆成三层，解决了“AI 生成内容是否应该直接创建真实发送对象”的边界问题。
