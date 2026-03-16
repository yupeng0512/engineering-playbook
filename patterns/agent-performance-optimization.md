---
title: agent-performance-optimization
type: note
permalink: engineering-playbook/patterns/agent-performance-optimization
---

# Agent 性能优化模式

> 来源：everything-claude-code (affaan-m, Anthropic Hackathon Winner, 50K+ Stars)
> 仓库：https://github.com/affaan-m/everything-claude-code

## 一、Hooks 机制（会话生命周期钩子）

Hooks 是 Agent 在关键时刻自动触发的脚本，解决"Agent 忘记做某事"的问题。

### 推荐采纳的 Hooks

| Hook | 触发时机 | 作用 |
|------|----------|------|
| **PreCompact** | Context 压缩前 | 保存当前关键状态到文件，防止压缩丢失重要信息 |
| **SessionEnd** | 会话结束时 | 持久化会话状态 + 抽取可复用模式（continuous learning） |
| **SessionStart** | 新会话开始时 | 自动加载先前 context，恢复工作状态 |
| **PostToolUse (Edit)** | 编辑文件后 | 自动格式化 + 类型检查 + console.log 警告 |
| **PreToolUse (tmux)** | 执行长命令前 | 提醒在 tmux 中运行，防止阻塞 |

### 在 Cursor 中的对应实践

Cursor 没有原生 Hooks 机制，但可以通过以下方式模拟：
- **PreCompact → AGENTS.md 规则**：在规则中写明"context 压缩前先更新 NOW.md"
- **SessionEnd → AGENTS.md 规则**：在规则中写明"会话结束前更新 NOW.md 并写日志"
- **SessionStart → AGENTS.md 规则**：在规则中写明"会话开始时先读 NOW.md 和当天日志"

## 二、Rules 最佳实践

### 推荐采纳的规则类别

1. **security.md** — 无硬编码密钥、输入校验、敏感信息不入日志
2. **coding-style.md** — 不可变性优先、文件组织、文件大小限制（主文件 < 300 行）
3. **testing.md** — TDD 优先、80% 覆盖率要求
4. **performance.md** — 模型选择策略、token 预算意识
5. **agents.md** — 何时使用 subagent、任务委托规则

## 三、Continuous Learning（持续学习）

核心理念：Agent 在每次会话中学到的模式应自动沉淀为可复用的 Skill。

流程：
1. SessionEnd Hook 触发模式抽取
2. 识别本次会话中反复出现的模式
3. 将模式写入 skills/ 目录
4. 下次会话自动加载

在 Cursor 中的实践：
- 对应 `cursor-skills/` 目录中的 SKILL.md 文件
- 手动触发：完成一个项目后，用 `skill-from-masters` 或 `command-creator` 技能沉淀经验

## 四、Subagent 编排

关键约束：不同 subagent 之间的 context 完全隔离。

最佳实践：
- 给 subagent 的 prompt 必须包含所有必要 context（不能假设它"知道"什么）
- 用文件作为 subagent 间的通信通道
- 结果要明确指定返回格式

## 五、值得引入的 Skills

| Skill | 用途 | 是否需要引入 |
|-------|------|-------------|
| skill-stocktake | 盘点审计已有 skills | 推荐 — 你有 14+ skills 可以用它来优化 |
| search-first | 先搜索再编码 | 推荐 — 避免重复造轮子 |
| continuous-learning | 从会话中自动抽取模式 | 考虑 — 需要适配 Cursor |
| verification-loop | 检查点式验证 | 考虑 — 减少错误传播 |
| strategic-compact | 手动控制 context 压缩 | 低优 — Claude Code 特有 |