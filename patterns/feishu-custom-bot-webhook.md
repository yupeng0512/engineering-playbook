---
title: feishu-custom-bot-webhook
type: note
permalink: engineering-playbook/patterns/feishu-custom-bot-webhook
---

# 飞书自定义机器人 Webhook 最佳实践

> 适用于所有需要向飞书推送通知的系统。
> 
> 教训来源：7 个系统从 Flow Trigger Webhook 迁移到自定义机器人 Webhook 的实战经验。

## Webhook 类型对比

| 特性 | 自定义机器人 Webhook | Flow Trigger Webhook |
|------|---------------------|---------------------|
| URL 格式 | `open.feishu.cn/open-apis/bot/v2/hook/{id}` | `feishu.cn/flow/api/trigger-webhook/{id}` |
| 消息渲染 | **直接渲染**，POST 什么就显示什么 | 需要 Flow 模板绑定变量，否则**空白卡片** |
| 支持消息类型 | text / post / interactive / image | 仅传递变量给 Flow 模板 |
| 签名校验 | HMAC-SHA256，安全可靠 | 不支持 |
| 适用场景 | **所有推送场景（推荐）** | 需要复杂自动化流程时 |

**结论：除非需要 Flow 自动化编排，否则一律使用自定义机器人 Webhook。**

## 签名校验

### 算法

```
string_to_sign = f"{timestamp}\n{secret}"
signature = Base64(HMAC-SHA256(key=string_to_sign, msg=empty_bytes))
```

注意：HMAC 的 **key** 是 `string_to_sign`，**消息体是空字节串** `b""`。

### Python 实现

```python
import base64, hashlib, hmac, time

def feishu_gen_sign(secret: str) -> tuple[str, str]:
    """返回 (timestamp, sign) 元组"""
    timestamp = str(int(time.time()))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return timestamp, sign
```

### 发送时附加签名

```python
payload = {"msg_type": "text", "content": {"text": message}}
ts, sign = feishu_gen_sign(secret)
payload["timestamp"] = ts
payload["sign"] = sign
requests.post(webhook_url, json=payload)
```

**常见 Bug**：`hmac.new(secret, string_to_sign)` — 这是错误的！key 应该是 `string_to_sign`，不是 `secret`。

## 消息类型

### 1. 纯文本（msg_type: text）

```json
{
  "msg_type": "text",
  "content": {"text": "Hello World"}
}
```

最简单，适用于告警、日志等纯信息推送。

### 2. 富文本（msg_type: post）

```json
{
  "msg_type": "post",
  "content": {
    "post": {
      "zh_cn": {
        "title": "标题",
        "content": [
          [
            {"tag": "text", "text": "普通文本 "},
            {"tag": "a", "text": "链接", "href": "https://example.com"},
            {"tag": "at", "user_id": "ou_xxx"}
          ]
        ]
      }
    }
  }
}
```

支持的 tag：`text`、`a`（链接）、`at`（@人）、`img`（图片）。

### 3. 交互式卡片（msg_type: interactive）

```json
{
  "msg_type": "interactive",
  "card": {
    "config": {"wide_screen_mode": true},
    "header": {
      "title": {"tag": "plain_text", "content": "标题"},
      "template": "blue"
    },
    "elements": [
      {
        "tag": "div",
        "text": {"content": "**加粗** 和 [链接](url)", "tag": "lark_md"}
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {"content": "查看详情", "tag": "plain_text"},
            "url": "https://example.com",
            "type": "primary"
          }
        ]
      }
    ]
  }
}
```

header.template 颜色选项：`blue`、`green`、`orange`、`red`、`grey`、`purple`、`turquoise`、`yellow`、`violet`、`wathet`、`indigo`、`carmine`

elements 支持的组件：
- `div` — 文本区块（支持 `lark_md` Markdown）
- `markdown` — Markdown 内容（简写形式）
- `hr` — 分割线
- `action` — 按钮区域
- `note` — 备注区域
- `img` — 图片

按钮 type：`primary`（蓝色）、`default`（灰色）、`danger`（红色）

### Markdown 快捷写法

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {...},
    "elements": [
      {"tag": "markdown", "content": "**粗体** *斜体* [链接](url)\n- 列表项"}
    ]
  }
}
```

## 限制

- 请求体 ≤ 20KB
- timestamp 与服务器时间差 ≤ 1 小时
- 超长消息需分段发送（建议 4000 字符/段）

## 各系统配置清单

| 系统 | 环境变量 | 签名变量 |
|------|---------|---------|
| Trading-System | `FEISHU_WEBHOOK_URL` (DB + ENV) | `FEISHU_SECRET` (DB + ENV) |
| Trump-Monitor | `FEISHU_WEBHOOK_URL` | `FEISHU_SECRET` |
| GitHub-Sentinel | `FEISHU_WEBHOOK_URL` | `FEISHU_SECRET` |
| Ops-Dashboard | `FEISHU_WEBHOOK_URL` (DB + ENV) | `FEISHU_SECRET` (DB + ENV) |
| TrendRadar | `FEISHU_WEBHOOK_URL` | `FEISHU_SECRET` |
| Claws | `FEISHU_WEBHOOK_URL` | `FEISHU_SECRET` |
| InfoHunter | `FEISHU_WEBHOOK_URL` | `FEISHU_SECRET` |

## 升级路径

当前所有系统使用 `msg_type: text`。后续可按需升级到 `interactive` 卡片：

1. **告警类**（ops-dashboard）→ 彩色 header + 按钮跳转
2. **报告类**（trading-system daily report）→ Markdown 卡片
3. **内容类**（trump-monitor, github-sentinel）→ 富文本 + 链接