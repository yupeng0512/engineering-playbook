---
title: staged-live-bridge-before-real-money
type: note
permalink: engineering-playbook/patterns/staged-live-bridge-before-real-money
---

# 先做 staged-live bridge，再决定要不要碰真钱

## 场景

一个自动化执行系统在 paper trading 跑出正收益后，团队很容易产生下一步冲动：

- 既然 paper 在赚钱
- 是不是就该直接开小资金真钱验证

这个跳跃通常过快，因为很多系统在进入真钱前，还没有把执行真实性、feed 健康、agent 增益和 guardrail 可观测性做扎实。

## 问题

如果从 paper 直接跳到真钱，常见风险有：

- paper fill 仍然靠 midpoint 或低频轮询，和真实 orderbook 偏差未知
- agent 可能还没有证明自己相对 deterministic baseline 有正 lift
- 自进化规则只有文本生成，没有 exposure / application / realized outcome
- 系统一旦出错，缺少 staged intent、preflight、kill switch 这类中间层证据

## 推荐做法

在 `paper execution` 和 `real money` 之间插入一个明确的 **staged-live bridge**。

这个桥接层至少要包含：

- `counterfactual decisions`
- `staged order intents`
- `feed health telemetry`
- `non-null fill drift gate`
- `route-level live candidate policy`

推荐顺序：

1. `paper trade with realistic costs`
2. `shadow market truth`
3. `counterfactual agent evidence`
4. `staged order intent + preflight`
5. 再决定是否给真钱 authority

## 设计原则

- **先证明执行真实性，再讨论真钱。**
- **agent 先做 counterfactual evidence generator，不要默认它有资本分配权。**
- **snapshot fallback 只能做 debug，不应伪装成 live truth。**
- **真钱前先有 intent、preflight、kill switch 和 blocked reason。**

## 适用场景

- 自动交易 / agentic execution 系统
- 任意需要从 simulation 过渡到 live execution 的产品
- 希望先验证 route-level edge，再逐步放开 authority 的团队

## 来源

Trading System Phase 8 把 `counterfactual_decisions + staged_order_intents + feed_health + websocket-only drift gate`
作为 real-money 之前的强制桥接层，避免把 `paper赚钱` 误当成 `已经能安全上真钱`。
