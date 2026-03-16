---
title: Email Sender Abstraction Layer
tags:
- go
- email
- provider
- pattern
type: pattern
permalink: engineering-playbook/patterns/email-sender-abstraction
---

# Email Sender Abstraction Layer

## Context

SaaS 产品需要发送邮件（OTP、触达、通知），但不同场景适合不同服务商（Resend 适合事务邮件，SendGrid 适合批量营销）。

## Pattern

定义 `Sender` 接口 + 工厂函数 + 多实现：

```go
type Sender interface {
    Send(ctx context.Context, msg *Message) (string, error)
    SendBatch(ctx context.Context, msgs []*Message) ([]string, error)
    Name() string
}
```

### 关键设计

1. **工厂函数 `NewSender(provider, keys...)`** — 根据环境变量 `EMAIL_PROVIDER` 选择实现
2. **Log-only 兜底** — 无 API Key 时降级为日志打印，开发环境零配置可用
3. **`Message` 统一结构** — 包含 `To, From, Subject, HTML, Text, TrackingID, Tags`
4. **SendGrid `from` 字段解析** — `"Name <email>"` 格式需拆分为 `{name, email}` 结构

### 典型切换配置

```env
EMAIL_PROVIDER=resend     # OTP + 事务邮件
# EMAIL_PROVIDER=sendgrid # 批量营销（需 SendGrid API Key）
```

## Observations

- [decision] 接口 + 工厂模式比策略模式更轻量 #email #go
- [technique] Resend Batch API 限制 100 封/次，需分块 #resend
- [technique] SendGrid REST API 返回 `X-Message-Id` header 作为消息 ID #sendgrid
- [insight] Log-only sender 让开发环境完全解耦邮件服务商 #dx

## Relations

- implements [[TradeRadar]]
- relates_to [[BYOK API Key Proxy]]