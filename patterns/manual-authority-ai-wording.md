---
title: manual-authority-ai-wording
type: note
permalink: engineering-playbook/patterns/manual-authority-ai-wording
---

# 商业对象里让 AI 负责措辞，不让 AI 负责价格与承诺

## 场景

在销售、采购、客服这类 AI copilot 里，系统经常需要生成 buyer-facing 内容，例如报价邮件、商业回复、条款摘要、跟进说明。

这时候最容易犯的错误是：既让 AI 负责写措辞，也让 AI 顺手生成价格、MOQ、交期、承诺条款。

## 问题

如果把这些权威字段也交给 AI，通常会带来三类风险：

- AI 会补全“看起来合理”的价格或商业条件，但这些内容并没有真实来源
- 前端或 agent 很难区分“可编辑文案”与“必须人工确认的商业事实”
- 一旦 buyer-facing 内容直接进入发送链路，错误承诺会被系统放大

## 推荐分工

### 1. 人工权威字段

这些字段必须来自手工输入、确定数据源或明确的业务系统：

- line items
- quantity
- unit price
- amount
- MOQ
- lead time
- incoterm / payment term

### 2. AI 辅助字段

这些字段适合交给 AI 辅助生成、润色或刷新：

- buyer subject
- buyer body
- terms summary
- follow-up hint
- risk flags
- wording variants

## 设计原则

- **AI 可以整理商业表达，不能凭空制造商业事实。**
- **进入 buyer-facing 对象前，权威字段必须先存在。**
- **发送审批检查的重点，是“文案是否合适”加“权威字段是否齐全”。**
- **如果没有 authoritative line items，就不应该进入 ready-to-send。**

## 适用场景

- 报价 copilot
- 合同/条款邮件生成
- 发票说明或付款提醒
- 任何 buyer-facing 且包含商业承诺的 AI 工作流

## 来源

TradeRadar Phase 19 引入 `CommercialQuote` 时，采用了“manual quote lines + AI wording”分层：价格和数量由人工 line items 提供，AI 只负责 buyer subject/body、terms summary、follow-up hint 和 risk flags。
