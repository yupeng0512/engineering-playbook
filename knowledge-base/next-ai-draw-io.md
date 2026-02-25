# Next AI Draw.io 完整经验档案

> 项目周期: 2025 ~ 进行中
> 最后更新: 2026-02-25
> 状态: 活跃使用（v0.4.8）

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | AI 驱动的图表创建工具 |
| **领域** | AI / 可视化 / 开发工具 |
| **规模** | 中大型全栈项目，Next.js 16 + MCP Server 独立包 |
| **核心价值** | 自然语言对话 → draw.io 图表，多 AI Provider 支持 |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 框架 | Next.js | 16 | Turbopack + standalone output |
| 前端 | React 19 + TypeScript | | async params, use pattern |
| AI SDK | Vercel AI SDK | 6 (^5.0) | 12+ Provider 统一 |
| 图表 | react-drawio | | draw.io iframe 集成 |
| UI | Radix UI + TailwindCSS 4 | | |
| MCP | @modelcontextprotocol/sdk | | 独立包 |
| 可观测 | Langfuse + OpenTelemetry | | Token 追踪 |
| 部署 | Docker / Vercel / Cloudflare Workers | | OpenNext |

### 架构概览

```
用户自然语言 → Chat Panel (AI SDK useChat)
    │
    ▼
Next.js API Route → getAIModel() (12+ Provider 抽象)
    │
    ├──→ LLM → Tool Calls (display/edit/append/get_shape_library)
    │                │
    │                ├── XML 验证 + 24 项自动修复
    │                └── 截断检测 + append 续传
    │
    └──→ DiagramContext → react-drawio iframe → draw.io 渲染
                │
                └── 版本历史 (循环缓冲区, max 20)

MCP Server (独立包) ─── stdio ───→ Claude Desktop / Cursor
    │
    ├── 内嵌 HTTP Server (6002-6020)
    ├── 浏览器 draw.io → 2s 轮询状态同步
    └── 5 个工具: start_session / create / edit / get / export
```

---

## 做得好的地方

### 技术选型

#### Vercel AI SDK 6 多 Provider 统一

- **技术**: `getAIModel()` 工厂函数 + Provider Options Builder
- **场景**: 支持 12+ AI 提供商（Bedrock/OpenAI/Anthropic/Google/Azure/Ollama/DeepSeek 等）
- **选择理由**: Vercel AI SDK 提供标准化的 streamText/generateText 接口
- **实际效果**: 新增 Provider 只需加一个 case，零 API 层改动
- **推荐指数**: 5/5
- **适用建议**: 所有 Next.js AI 应用的标配

#### Client Override 机制

- **技术**: 浏览器端 Settings → HTTP headers → 服务端 API Key/Provider/Model 动态切换
- **选择理由**: 免部署即可切换 AI 后端，BYOK (Bring Your Own Key) 模式
- **安全措施**: SSRF 防护 — custom baseUrl 必须同时提供 API Key
- **推荐指数**: 4/5

### 架构设计

#### 多层容错管道（核心亮点）

- **解决的问题**: LLM 生成的 draw.io XML 经常不完整或格式错误
- **实现方式**: 四层防线
  1. **JSON 修复**: `jsonrepair` + 预处理（`:=` → `: `）修复 Tool Call 参数
  2. **XML 验证**: 10 项检查（DOM 解析、重复属性、未转义字符、重复 ID 等）
  3. **XML 自动修复**: 24 项修复（CDATA 移除、标签拼写、嵌套扁平化、暴力丢弃等）
  4. **截断续传**: 检测不完整 XML → 存储部分内容 → 引导 LLM 调用 `append_diagram` 续传
- **可复用程度**: 中（draw.io XML 特定，但容错管道设计模式通用）
- **复用注意事项**: 任何 LLM 生成结构化输出（XML/JSON/HTML）的场景都可以参考这个多层防线设计

#### 分层 Prompt 设计

- **解决的问题**: 不同模型需要不同长度的 system prompt
- **实现方式**:
  - 基础层: 核心指令 + 工具定义 + XML 结构参考（~1900 tokens）
  - 扩展层: 编辑示例 + Edge 路由示例（~2600 tokens，仅大模型启用）
  - 样式层: 完整/最小化两种模式可切换
  - Model-aware: Opus 4.5/Haiku 4.5 使用扩展 prompt（满足缓存 4000 token 门槛）
- **可复用程度**: 高
- **复用注意事项**: 分层 prompt + 模型感知是 prompt 工程的最佳实践

#### Prompt Caching 双层断点

- **解决的问题**: 多轮对话中 system prompt 重复消费 token
- **实现方式**: Bedrock prompt caching 双断点 — 静态指令（缓存断点 1）+ 当前 XML 上下文（缓存断点 2）
- **可复用程度**: 中（Bedrock/Claude 特定）
- **复用注意事项**: 缓存断点位置影响命中率，静态内容放前面

#### MCP Server 状态同步

- **解决的问题**: MCP stdio 协议无法直接操作 GUI
- **实现方式**: MCP Server 内嵌 HTTP Server → 浏览器 2s 轮询 → draw.io iframe postMessage
- **可复用程度**: 中
- **复用注意事项**: 适用于任何需要 MCP 操作 GUI 应用的场景

### 其他亮点

- **客户端响应缓存**: 4 个预缓存示例响应，命中时零 AI 调用
- **版本历史**: 循环缓冲区（max 20），支持消息编辑时 XML 回滚
- **配额管理**: 请求数/Token 数/TPM 三维限制
- **i18n**: en/zh/ja 三语言，基于 Next.js `[lang]` 动态路由
- **多部署目标**: Docker / Vercel / Cloudflare Workers (OpenNext)

---

## 做得不好的地方

### 踩坑清单

#### 坑 1: SGLang SSE 流不标准

- **影响程度**: 中
- **现象**: SGLang 模型返回的 SSE 流格式非标准，AI SDK 无法解析
- **根因**: SGLang 的 OpenAI 兼容层 SSE 格式有差异
- **解决方案**: 自定义 fetch wrapper，用 `TransformStream` 在中间层修复流格式
- **预防建议**: 使用"兼容层"前先测试流式输出格式

#### 坑 2: LLM 生成 XML 截断

- **影响程度**: 高
- **现象**: 复杂图表的 XML 超过 maxOutputTokens，被截断导致 Tool Call 失败
- **解决方案**: `append_diagram` 工具 + 截断检测 + 自动重试（最多 2 次）
- **预防建议**: 生成长结构化输出时，必须设计截断续传机制

#### 坑 3: draw.io XML 格式多样性

- **影响程度**: 高
- **现象**: LLM 生成的 XML 包含各种格式错误（重复属性、未转义字符、嵌套 mxCell、标签拼写错误等）
- **解决方案**: 24 项自动修复规则，最后手段是暴力丢弃无法修复的 mxCell
- **预防建议**: LLM 输出结构化格式时，必须有验证 + 自动修复层

---

## 可复用资产

### 代码模式

- **多 AI Provider 抽象**: `lib/ai-providers.ts` — 12+ Provider 统一工厂
- **分层 Prompt 设计**: `lib/system-prompts.ts` — 基础层/扩展层/样式层 + 模型感知
- **容错管道**: JSON 修复 → XML 验证 → 24 项修复 → 截断续传 → 自动重试
- **Client Override**: 浏览器端 Settings → HTTP headers → 服务端 Provider 切换
- **MCP GUI 同步**: MCP stdio ↔ HTTP Server ↔ 浏览器 iframe 三层同步

---

## 给未来自己的建议

### 延伸到其他项目的通用建议

- **AI 生成结构化输出**: 永远需要验证 + 修复 + 截断续传三层防线
- **Prompt 分层**: 基础/扩展/模型感知三层设计，平衡 token 消耗和输出质量
- **多 Provider 支持**: 用 Vercel AI SDK 或类似抽象层，不要直接调用厂商 SDK
- **Prompt Caching**: 静态内容放前面设置缓存断点，能显著降低成本

---

## 元数据

- **沉淀时间**: 2026-02-25
- **信息来源**: 代码分析 / README / Git log / 深度代码审查
- **覆盖度评估**: 约 80%。遗漏：(1) Electron 桌面版具体实现 (2) DynamoDB 配额管理细节 (3) Cloudflare Workers 部署的具体踩坑
