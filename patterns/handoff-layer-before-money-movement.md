---
title: handoff-layer-before-money-movement
type: note
permalink: engineering-playbook/patterns/handoff-layer-before-money-movement
---

# 先做交接层，再决定要不要碰资金流

## 场景

当一个 B2B workflow 产品已经从 lead / outreach / quote 走到成交后段时，团队很容易产生一个看似自然的冲动：

- 客户已经接受报价
- 下一步是不是就该做平台内 invoice / payment / split settlement

这个跳跃经常过快，因为系统往往还没有把 billing 信息、交接材料、内部 handoff checklist 这些更基础的商业真相收口清楚。

## 问题

如果在没有 `billing readiness / finance handoff` 层的情况下直接进入 money movement，通常会同时引入两类复杂度：

- **产品复杂度**
  - 谁是 billing truth source 不清楚
  - payment terms / tax info / required docs 还散落在邮件和备注里
  - quote accepted 和 finance-ready 被混成一个状态
- **合规复杂度**
  - 一旦平台开始代收代付，就会触发 KYC / KYB、refund、chargeback、negative balance、split payout、税务责任等要求
  - 产品边界会从 workflow SaaS 突然变成 money-moving platform

## 推荐做法

在 `quote / order readiness` 和 `invoice / payment` 之间，先引入一个明确的 **finance handoff / billing readiness** 层。

这个中间层至少应承载：

- buyer billing profile
- missing billing fields
- missing artifacts / required docs
- requested terms summary
- internal handoff checklist
- handoff packet summary

推荐顺序：

1. `quote accepted`
2. `order readiness`
3. `finance handoff / billing readiness`
4. `ready for finance or ops handoff`
5. 再决定是否真的需要 `invoice / payment`

## 设计原则

- **商业信息先结构化，再考虑资金流。**
- **handoff-ready 不等于平台必须代收代付。**
- **如果产品还没有 billing truth，就不要急着做 payment truth。**
- **优先把系统做成可靠的交接层，而不是过早把它做成收款平台。**

## 适用场景

- quote-first 的 B2B 商业工作流产品
- 想继续纵深成交闭环，但暂时不想承担支付合规成本的团队
- 仍处于 owner-led SMB / internal-first 阶段的销售协作产品

## 来源

TradeRadar Phase 22 选择先实现 `CustomerBillingProfile + FinanceHandoff`，把产品止于 `finance/ops handoff ready`，而不是直接进入 invoice/payment 或平台侧资金中转。
