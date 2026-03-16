---
title: push-poll-checkpoint-sync
type: note
permalink: engineering-playbook/patterns/push-poll-checkpoint-sync
---

# Webhook 同步不要只信 Push：用 Checkpoint + Catch-up Poll 兜底

## 场景

邮件、日历、消息流这类第三方集成，常见做法是接 provider 的 webhook / push notification，然后增量同步远端数据。

## 问题

只依赖 push 有几个天然风险：

- provider 可能延迟、丢消息、短暂停推
- webhook 接收端可能超时或临时不可用
- 消息顺序不稳定，单条事件本身未必足够重建状态

结果通常不是“完全挂掉”，而是更难查的那种静默漏数据。

## 推荐模式

### 核心原则

**Push 只负责提醒“有变更”，真正的状态推进依赖 provider checkpoint + 周期性 catch-up poll。**

### 典型流程

1. 首次全量或 bootstrap sync
2. 持久化 provider checkpoint（例如 `historyId` / cursor / delta token）
3. 收到 push 后，不直接信任 payload 全量内容，而是用 checkpoint 去拉增量
4. 周期性对“快过期 / 很久没同步 / 上次同步失败”的连接做 catch-up poll
5. 如果 checkpoint 失效，执行受控的 re-bootstrap，而不是静默继续

## Checklist

- [ ] 是否有持久化的远端 checkpoint，而不是只记最后一次 webhook 时间？
- [ ] push 到达后，是否通过 checkpoint 拉增量，而不是直接把 webhook 当 source of truth？
- [ ] 是否有 missed-push 的定时补拉机制？
- [ ] checkpoint 失效时，是否有明确的重建策略和错误状态？
- [ ] 连接状态里是否记录了 `last_synced_at` / `sync_status` / `last_error` 便于观测？

## TradeRadar 实例

Phase 13 的 Gmail reply inbox 使用：

- Gmail push / Pub/Sub 作为变更通知
- `last_history_id` 作为 checkpoint
- `watch_expiration` / `sync_status` 作为连接健康状态
- scheduler 定时 catch-up poll 作为漏推兜底

这样即使 push 丢失，也还能通过 checkpoint 增量恢复回复线程，不会让 inbox 静默漏消息。

## 适用范围

- Gmail / Outlook / Slack / Discord / Calendar / Stripe 类 webhook + delta API
- 任意“事件只是提示，状态仍需回源确认”的第三方同步场景
