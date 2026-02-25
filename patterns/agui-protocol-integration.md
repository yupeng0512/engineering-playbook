# SSE 流式 AI 客户端模式（AG-UI 协议实践）

> 来源项目: truthsocial-trump-monitor, github-sentinel, infohunter
> 沉淀时间: 2026-02-25
> 门控审核: 2026-02-25（重构：提升通用性，移除内部域名，消除与 llm-json-parser 的重复）

---

## 适用场景

通过 SSE（Server-Sent Events）流式协议调用远程 AI 平台智能体，获取分析结果。适用于：
- 对接任何支持 SSE 的 AI 服务端（AG-UI、OpenAI-compatible、自建平台）
- 需要处理流式文本、思考过程、工具调用等多类型事件
- 需要在 SSE 流中统计 token 用量和成本

---

## 核心模式

### 1. 协议层 + 业务层分离

```python
class SSEAIClient:
    """协议层：负责 HTTP/SSE 通信，不关心业务逻辑"""

    def __init__(self, endpoint: str, headers: dict):
        self.endpoint = endpoint
        self.headers = headers

    async def chat(self, message: str, **kwargs) -> SSEResponse:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", self.endpoint,
                json=self._build_request(message, **kwargs),
                headers=self.headers,
                timeout=60.0,
            ) as response:
                return await self._parse_sse_stream(response)

    async def _parse_sse_stream(self, response) -> SSEResponse:
        content_parts, thinking_parts = [], []
        token_usage = {}

        async for line in response.aiter_lines():
            chunk_str = line.lstrip("data:").strip()
            if chunk_str in ("[DONE]", ""):
                if chunk_str == "[DONE]":
                    break
                continue

            msg = json.loads(chunk_str)
            msg_type = msg.get("type", "")
            raw_event = msg.get("rawEvent", msg)

            if msg_type == "TEXT_MESSAGE_CONTENT":
                content_parts.append(raw_event.get("delta", ""))
            elif msg_type == "THINKING_TEXT_MESSAGE_CONTENT":
                thinking_parts.append(raw_event.get("delta", ""))
            elif msg_type == "STEP_FINISHED":
                step_usage = raw_event.get("tokenUsage", {})
                for k, v in step_usage.items():
                    token_usage[k] = token_usage.get(k, 0) + v

        return SSEResponse(
            content="".join(content_parts),
            thinking="".join(thinking_parts),
            token_usage=token_usage,
        )


class BusinessAnalyzer:
    """业务层：构建 prompt、解析结果，可独立替换"""

    def __init__(self, client: SSEAIClient):
        self.client = client

    async def analyze(self, data) -> dict:
        prompt = self._build_prompt(data)
        response = await self.client.chat(prompt)
        return extract_json(response.content)  # 引用 llm-json-parser Pattern
```

换分析场景只需替换 `BusinessAnalyzer`，`SSEAIClient` 完全复用。

### 2. 认证模式抽象

不同平台有不同认证方式，用工厂函数统一：

```python
def build_headers(token: str, platform: str = "default") -> dict:
    """根据平台构建认证 Headers"""
    if platform == "openai":
        return {"Authorization": f"Bearer {token}"}
    elif platform == "agui":
        if token.startswith("knot_"):
            return {"x-knot-token": token, "X-Username": "system"}
        return {"x-knot-api-token": token}
    else:
        return {"Authorization": f"Bearer {token}"}
```

### 3. 请求体通用结构

```python
def _build_request(self, message: str, **kwargs) -> dict:
    return {
        "input": {
            "message": message,
            "conversation_id": kwargs.get("conversation_id", ""),
            "model": kwargs.get("model", ""),
            "stream": True,
            "temperature": kwargs.get("temperature", 0.5),
        }
    }
```

---

## SSE 解析踩坑

### 1. `data:` 前缀处理

```python
# ✅ 正确：lstrip 容忍 "data:" 后的空格
chunk_str = line.lstrip("data:").strip()

# ❌ 错误：removeprefix 要求精确匹配，"data: " 和 "data:" 不同
chunk_str = line.removeprefix("data:")
```

### 2. 流中断无 `[DONE]` 信号

网络中断时 SSE 流可能无结束标记，必须有超时兜底：

```python
async with client.stream(..., timeout=60.0) as response:
    # timeout 保证不会永久挂起
```

### 3. Token 用量在 `STEP_FINISHED` 中

一个请求可能有多个 step（工具调用 + 最终回复），token 需要累加而非取最后一个。

### 4. 降级方案必备

SSE 平台可能不可用，设计三级降级：
- 超时兜底（30-60s）
- 降级到直接 LLM API 调用（OpenAI / Claude / 本地模型）
- 缓存最近一次分析结果作为 fallback

---

## JSON 结果解析

SSE 返回的 AI 文本通常需要从中提取 JSON。请参考 **`llm-json-parser` Pattern** 获取完整的多层防御解析方案。

---

## 前后对比

| 维度 | 无此 Pattern | 使用此 Pattern |
|------|-------------|---------------|
| SSE 解析 | 从零实现 | 复制 SSEAIClient 即可 |
| 换分析场景 | 重写整个客户端 | 只替换 Analyzer 类 |
| 认证适配 | 试错不同平台的 Header | 工厂函数按平台选择 |
| 流中断 | 进程挂起 | 超时 + 降级兜底 |

---

## 注意事项

1. SSE 事件类型因平台而异，上述事件类型来自 AG-UI 协议；OpenAI 使用 `choices[0].delta.content`
2. `conversation_id` 为空字符串（非 None）表示新对话（AG-UI 特有）
3. 温度参数影响 JSON 输出稳定性，推荐 0.3-0.5
4. AI 分析结果需要截断适配下游通知渠道的长度限制（参考 `data-pipeline-monitor` Pattern）
