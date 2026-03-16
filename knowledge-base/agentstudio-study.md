---
title: agentstudio-study
type: note
permalink: engineering-playbook/knowledge-base/agentstudio-study
---

# AgentStudio Study 完整经验档案

> 项目周期: 2025 ~ 进行中
> 最后更新: 2026-02-25
> 状态: 学习/定制使用

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | AI Agent 工作台（Claude Code Web 化） |
| **领域** | AI Agent / IDE 工具 |
| **规模** | ~50K+ 行 TypeScript，pnpm monorepo（前后端分离） |
| **核心价值** | 将 Claude Code CLI 体验转化为友好的 Web UI |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 前端 | React 19 + TypeScript + Vite 7 | | TailwindCSS |
| 状态管理 | Zustand (client) + TanStack Query (server) | | |
| 后端 | Node.js 20+ + Express + TypeScript | | |
| AI 核心 | @anthropic-ai/claude-agent-sdk | ^0.1.62 | Streaming Input Mode |
| A2A | @a2a-js/sdk | ^0.2.5 | Agent-to-Agent 协议 |
| AI SDK | Vercel AI SDK | ^5.0.22 | |
| 认证 | JWT + bcryptjs | | |
| 定时任务 | node-cron | | |
| 包管理 | pnpm 10 workspaces | | 前后端 monorepo |
| 测试 | Vitest + Playwright | | |
| UI | Radix UI + Lucide + Monaco Editor | | |
| 部署 | Docker / Vercel / npm 全局包 / 系统服务 | | |

### 架构概览

```
React 19 SPA (Vite 7)
    │ SSE Streaming
    ▼
Express Backend (TypeScript)
    │
    ├── SessionManager → ClaudeSession (Claude Agent SDK query())
    │      │                    │
    │      │                    └── Streaming Input Mode (async generator)
    │      │
    │      ├── MessageQueue → 消息排队
    │      ├── AgentStorage → Agent 配置持久化
    │      └── SchedulerService → 定时任务 (node-cron)
    │
    ├── A2A Service → Agent-to-Agent 协议
    ├── PluginParser → 插件系统
    └── TunnelService → WebSocket 外部访问
```

---

## 做得好的地方

### 技术选型

#### Claude Agent SDK Streaming Input Mode

- **技术**: `@anthropic-ai/claude-agent-sdk` 的 `query()` + async generator
- **场景**: 长会话中持续向 Claude 推送用户输入
- **选择理由**: 官方 SDK，原生支持流式输入/输出
- **实际效果**: 实现了与 Claude Code CLI 等价的 Web 交互体验
- **推荐指数**: 5/5
- **适用建议**: 需要构建 Claude Code 类产品的唯一选择

#### pnpm Workspaces Monorepo

- **技术**: pnpm 10 + workspaces
- **场景**: 前后端 + 类型共享
- **选择理由**: 依赖管理高效 + workspace:* 协议
- **实际效果**: 前后端类型可复用，但需要手动同步
- **推荐指数**: 4/5
- **适用建议**: 中大型全栈 TypeScript 项目标配

### 架构设计

#### ClaudeSession + MessageQueue 会话管理

- **解决的问题**: 管理与 Claude 的长期流式会话
- **实现方式**:
  - `ClaudeSession`: 封装 SDK `query()`，使用 async generator 持续推送输入
  - `MessageQueue`: 消息排队，确保有序处理
  - 支持 `resume` 模式恢复历史会话
  - 会话级并发控制（`isProcessing` 锁）
- **可复用程度**: 高
- **复用注意事项**: 需要 Claude API Key

#### SessionManager 三级索引 + 生命周期管理

- **解决的问题**: 多 Agent 多会话的生命周期管理
- **实现方式**:
  - 三级索引: `sessionId → ClaudeSession` / `agentId → Set<sessionId>` / `tempKey → ClaudeSession`
  - 心跳机制: 30 分钟超时
  - 配置快照对比: 检测 model/claudeVersionId/mcpTools 变化，自动重建
  - 定期清理空闲会话（1 分钟检查）
- **可复用程度**: 中
- **复用注意事项**: 针对 Claude Agent SDK 设计，其他 AI SDK 需适配

#### SSE 流式 JSON 增量累加模式

- **解决的问题**: 流式响应中工具输入 JSON 的正确显示
- **关键实现**: 前端 `useAIStreamHandler.ts` 中必须用 `+=` 累加 JSON 片段
- **教训**: 用 `=` 替代 `+=` 会导致 Tool Input 只显示最后一个 chunk
- **可复用程度**: 高
- **复用注意事项**: 所有 SSE 流式 JSON 场景的通用模式

#### CLAUDE.md 作为项目知识库

- **解决的问题**: 新贡献者/AI 助手理解项目
- **实现方式**: 360 行 CLAUDE.md 覆盖架构、开发模式、常见问题、调试方法
- **核心价值**: 功能等同于 `.cursor/rules/`，为 Claude Code 提供项目上下文
- **可复用程度**: 高
- **复用注意事项**: 适合所有使用 Claude Code 开发的项目

### 其他亮点

- **四级 Agent 体系**: Built-in → Custom → Subagents → Project Commands
- **多部署方式**: Docker / npm 全局包 / Vercel / 系统服务，满足不同场景
- **国际化**: i18n 支持中英文
- **Storybook**: 组件库可视化开发

---

## 做得不好的地方

### 踩坑清单

#### 坑 1: SSE JSON 增量累加 (反复出现的坑)

- **影响程度**: 高
- **现象**: Tool Input 只显示最后一个 JSON chunk，信息丢失
- **根因**: 前端处理 `content_block_delta` 时用 `=` 赋值而非 `+=` 累加
- **解决方案**: 修改为 `+=` 累加，并在 CLAUDE.md 中反复强调
- **预防建议**: SSE 流式处理必须用增量累加，且在项目文档中显著标注

#### 坑 2: 前后端类型同步

- **影响程度**: 中
- **现象**: 后端修改了 Agent 类型定义，前端未同步导致运行时错误
- **根因**: Monorepo 中类型文件需要手动同步
- **解决方案**: 类型定义放在共享 package 中，前后端引用同一份
- **预防建议**: Monorepo 项目应建立 shared-types package

#### 坑 3: 会话 pending 状态卡死

- **影响程度**: 中
- **现象**: 会话状态卡在 pending，无法继续交互
- **根因**: 异步流处理中异常未正确捕获，导致状态未更新
- **解决方案**: `manualCleanupSession()` 强制清理 + 异常边界完善
- **预防建议**: 异步状态机需要超时兜底和强制重置机制

#### 坑 4: ESM import 路径

- **影响程度**: 低
- **现象**: TypeScript ESM 模式下 import 报错
- **根因**: ESM 模式要求 import 路径带 `.js` 后缀
- **解决方案**: 所有 import 加 `.js` 后缀
- **预防建议**: ESM 项目初始化时配置好路径解析规则

---

## 可复用资产

### 代码模式

- **ClaudeSession Streaming**: Claude Agent SDK 的 Web 化封装
- **SessionManager 生命周期**: 多会话管理、心跳、配置变化检测
- **SSE 增量累加**: 流式 JSON 处理的标准模式
- **CLAUDE.md 项目指南**: AI 辅助开发的项目知识库模板

### 配置模板

- **pnpm Monorepo**: workspace 配置 + 前后端分离
- **多部署方式**: Docker / npm / Vercel / systemd service

---

## 给未来自己的建议

### 如果重新做这个项目

1. 从第一天就用 shared-types package 统一前后端类型
2. SSE 流式处理规范写进项目 linter 规则，不只靠文档提醒
3. 会话状态机加超时兜底，不依赖手动清理

### 延伸到其他项目的通用建议

- **Claude Agent SDK**: Streaming Input Mode + MessageQueue 是构建 Web AI Agent 的参考架构
- **Monorepo 类型共享**: 务必用 shared package，不要手动同步
- **SSE 处理**: 增量累加是铁律，必须在代码审查中检查
- **CLAUDE.md**: 每个使用 AI 辅助开发的项目都应该有一份项目知识库

---

## 元数据

- **沉淀时间**: 2026-02-25
- **信息来源**: 代码分析 / README / CLAUDE.md / Git log / 项目结构扫描
- **覆盖度评估**: 约 70%。遗漏：(1) A2A 协议的具体使用经验 (2) 插件系统的设计细节 (3) Tunnel 服务的网络穿透实现 (4) 具体的调试和运维经验