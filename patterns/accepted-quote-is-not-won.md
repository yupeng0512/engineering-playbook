---
title: accepted-quote-is-not-won
type: note
permalink: engineering-playbook/patterns/accepted-quote-is-not-won
---

# 报价已接受，不等于机会已赢单

## 场景

在销售、采购、外贸这类 workflow 产品里，系统一旦开始支持 buyer-facing quote，最容易出现一个过于乐观的简化：

- buyer 接受了报价
- 系统马上把机会打成 `won`

这个简化在 demo 里看起来流畅，但一旦进入真实商业流程，往往会漏掉 PO、付款条款、出货确认、内部交接这些成交前的关键动作。

## 问题

如果把 `quote accepted` 直接等价成 `won`，通常会带来几类问题：

- 产品没有位置承载 “还差什么确认项”
- queue 和 next action 会过早停止推进
- closing analytics 会高估真实 handoff / 成交效率
- 用户会在系统外用表格、聊天或便签继续追 PO 和内部交接，导致主工作台失真

## 推荐做法

在 `quote` 和 `won` 之间插入一个明确的 **order readiness / handoff readiness** 层。

这个中间层至少要承载：

- commitment summary
- missing confirmations
- requested documents
- po reference
- internal handoff checklist
- handoff summary

推荐状态机：

1. `quote accepted`
2. `order_confirming`
3. `awaiting_po / needs_confirmation / ready_for_handoff`
4. `handed_off`
5. `won`

## 设计原则

- **accepted quote 是买方意向，不是交付完成。**
- **won 应该代表商业交接已经准备完成，而不是只收到一句 “sounds good”。**
- **中间层最好是轻量 handoff 对象，不必一开始就做完整 order / invoice / ERP。**
- **如果还没有附件解析、支付、订单系统，就先把“准备就绪”结构化，而不是硬上 full order。**

## 适用场景

- quote-first 的 B2B 销售产品
- 需要在成交前追踪 PO / order confirmation / shipping confirmation 的产品
- 想做 closing intelligence，但还不准备做完整 ERP/OMS 的产品

## 来源

TradeRadar Phase 20 引入 `OrderReadiness`，把 `CommercialQuote.accepted` 和 `Opportunity.won` 之间的真实商业动作显式建模，避免把 buyer commitment 过早算成最终成交。
