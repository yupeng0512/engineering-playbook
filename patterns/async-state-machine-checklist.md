---
title: 异步状态机 Code Review 检查清单
tags:
- go
- state-machine
- event-driven
- async
- code-review
type: pattern
project: trade-radar
date: 2026-03-12
permalink: engineering-playbook/patterns/async-state-machine-checklist
---

# 异步状态机 Code Review 检查清单

## 背景

在 TradeRadar Phase 7.2（Sequence Engine）代码 Review 中，发现了几个典型的异步状态机 bug，值得形成检查清单供后续 Review 时参考。

## Observations

- [problem] **事件名语义错配**：Publisher 发出 `"open"`, Consumer 检查 `"opened"`，导致条件判断永远失效，且不报错，极难发现 #event-driven #silent-bug
- [problem] **Dead Code 功能**：`ai_rewrite` flag 在 Model 和 UI 有配置项，但 `AdvanceStep` 从未调用 `RequestAIRewrite()`，功能完全无效，测试也发现不了 #dead-code
- [problem] **`http.DefaultClient` 无超时**：在 goroutine 中调用外部服务时用了 `http.DefaultClient`，若外部服务无响应，goroutine 永久挂起，调度器停摆 #goroutine #timeout
- [solution] 统一事件名到一种时态（推荐过去式：`opened / clicked / replied / bounced`），Publisher 和 Consumer 同文件定义常量
- [solution] 新增功能 flag 时，立即在核心流程调用点写一个 `if flag { /* TODO: implement */ }` 占位，避免 dead code
- [solution] 所有外部 HTTP 调用必须用带 timeout 的 `http.Client`，禁止用 `http.DefaultClient`

## 检查清单

### 事件驱动系统
- [ ] Publisher 发出的事件名 vs Consumer 检查的事件名是否完全一致（包括时态、大小写）
- [ ] 事件名是否用常量定义，而非散落的字符串字面量
- [ ] 事件消费失败是否有 error log（不能静默忽略）

### 状态机 AdvanceStep 类函数
- [ ] 所有 feature flag（`ai_rewrite`, `is_active` 等）是否都真正影响了执行路径
- [ ] 每个分支是否都有对应的 history 记录（sent / skipped / failed）
- [ ] 步骤推进失败（sendErr）时，`next_action_at` 是否更新到下一个合理时间（避免立即重试风暴）
- [ ] 是否有最大重试次数限制，防止某步骤永久 stuck

### Goroutine & HTTP 安全
- [ ] 所有外部 HTTP 调用必须用 `http.Client{Timeout: Ns}` 而非 `http.DefaultClient`
- [ ] Redis 分布式锁是否有合理的 TTL（> 单次操作最大预期耗时）
- [ ] Goroutine panic 是否有 `defer recover()` 保护（避免 goroutine 崩溃拖垮主进程）

### 前端一致性
- [ ] 新增表单元素是否使用了项目统一的 UI 组件（Select / Input / Badge），而非 native HTML 元素
- [ ] 异步操作是否等待响应后才 re-fetch（避免请求失败但 UI 看起来成功的假象）

## Relations

- part_of [[trade-radar-sequence-engine]]
- relates_to [[event-driven-architecture]]
- extends [[project-context-management]]