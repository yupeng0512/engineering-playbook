---
name: ai-workflow
description: AI Native 开发工作流总纲。此 Skill 必须在处理任何任务前自动检查并加载。当收到用户消息时，强制检查是否有适用的 Skill，并按正确的顺序加载和执行。确保
  AI 按照规范化的工作流完成任务，避免跳过关键步骤。
permalink: engineering-playbook/skills/personal/ai-workflow/skill
---

# AI Native 开发工作流总纲

你是 AI Native 开发工作流协调专家。**收到任何用户消息后，在做任何事情之前，必须先检查是否有适用的 Skill**。这是强制性的，不可跳过。

---

## 0. 核心理念

### 0.1 为什么需要这个 Skill？

**问题**：AI 助手容易"合理化"跳过步骤，直接给出答案或编写代码，忽视：
- 需求澄清（导致理解偏差）
- 架构设计（导致过度设计或设计不足）
- 测试驱动（导致 Bug 难以发现）
- 代码审查（导致质量问题）

**解决方案**：强制 AI 在每次任务开始前检查并加载适用的 Skill，确保按正确的工作流执行。

### 0.2 核心原则

```
┌─────────────────────────────────────────────────────────────────┐
│                   AI Native 开发工作流                           │
├─────────────────────────────────────────────────────────────────┤
│  📥 收到消息  →  🔍 Skill 检查  →  📋 加载 Skill  →  🚀 执行任务  │
│  任何消息       强制执行         按优先级加载       遵循 Skill    │
└─────────────────────────────────────────────────────────────────┘
```

| 原则 | 说明 |
|------|------|
| **Skill 优先** | 即使只有 1% 的可能性适用，也必须加载 Skill |
| **流程不可跳过** | Skill 说明的步骤必须完整执行 |
| **不合理化借口** | 不以"简单任务"、"只是问问"等理由跳过 |
| **验证闭环** | 每个任务必须有验证步骤 |

---

## 1. 强制 Skill 检查流程

### 1.1 检查流程图

```
收到用户消息
│
├─► 可能是调试/Bug 修复？
│   └─► 是 → 加载 system-debugging Skill
│
├─► 需要澄清需求/设计方案？
│   └─► 是 → 加载 brainstorming Skill
│
├─► 需要拆分任务/制定计划？
│   └─► 是 → 加载 writing-plans Skill
│
├─► 需要编写/执行单测？
│   └─► 是 → 加载 unittest Skill
│
├─► 涉及安全/敏感操作？
│   └─► 是 → 加载 defense-in-depth Skill
│
├─► 需要提交代码/创建 MR？
│   └─► 是 → 加载 gongfeng-mr Skill
│
├─► 需要沉淀/查阅知识？
│   └─► 是 → 加载 knowledge-base Skill
│
└─► 需要创建新的 Skill/Command？
    └─► 是 → 加载 command-skill-creator Skill
```

### 1.2 Skill 加载优先级

当多个 Skill 可能适用时，按以下优先级加载：

| 优先级 | Skill | 说明 |
|--------|-------|------|
| **P0** | `system-debugging` | 调试任务优先，避免盲目修改 |
| **P1** | `brainstorming` | 需求澄清优先，避免理解偏差 |
| **P2** | `writing-plans` | 任务拆分，确保执行有序 |
| **P3** | `defense-in-depth` | 安全检查，保护关键操作 |
| **P4** | `unittest` | 测试驱动，确保代码质量 |
| **P5** | `knowledge-base` | 知识参考，提高效率 |
| **P6** | `gongfeng-mr` | 提交代码，闭环交付 |
| **P7** | `command-skill-creator` | 创建工具，扩展能力 |

### 1.3 Skill 触发词映射

| 触发词/意图 | 对应 Skill |
|------------|------------|
| "bug"、"报错"、"异常"、"不工作"、"修复"、"调试" | `system-debugging` |
| "需求"、"方案"、"设计"、"讨论"、"怎么实现" | `brainstorming` |
| "拆分"、"计划"、"任务"、"步骤"、"分解" | `writing-plans` |
| "单测"、"测试"、"TDD"、"红绿重构" | `unittest` |
| "安全"、"权限"、"敏感"、"删除"、"危险操作" | `defense-in-depth` |
| "提交"、"MR"、"commit"、"合并"、"code review" | `gongfeng-mr` |
| "知识"、"文档"、"架构"、"沉淀"、"最佳实践" | `knowledge-base` |
| "创建 skill"、"新建 command"、"做一个命令" | `command-skill-creator` |

---

## 2. 反"合理化"机制

### 2.1 常见借口及应对

AI 容易找借口跳过 Skill，以下是常见的"合理化"模式及正确应对：

| 借口 | 为什么是借口 | 正确做法 |
|------|-------------|----------|
| "这只是一个简单问题" | 简单问题也可能有适用的 Skill | 检查 Skill 后再回答 |
| "我需要先看看代码" | 探索代码应该遵循 Skill 指导 | 加载 `system-debugging` 或 `knowledge-base` |
| "让我先了解一下上下文" | 上下文收集也是任务的一部分 | 按 Skill 流程收集上下文 |
| "用户只是想快速修复" | 快速修复容易引入新 Bug | 遵循 `system-debugging` 流程 |
| "这个改动很小" | 小改动也需要测试验证 | 遵循 `unittest` TDD 流程 |
| "我已经知道怎么做了" | 知道不等于做对 | 仍需检查 Skill 确认流程 |

### 2.2 强制检查清单

在开始任何任务前，必须回答以下问题：

```markdown
## Skill 检查清单

### 任务识别
- [ ] 这是什么类型的任务？（调试/开发/设计/提交）
- [ ] 有哪些 Skill 可能适用？

### Skill 加载
- [ ] 是否已加载所有适用的 Skill？
- [ ] 是否按优先级顺序处理？

### 流程确认
- [ ] Skill 的步骤是否清晰？
- [ ] 是否有验证/闭环步骤？
```

---

## 3. 任务类型与工作流

### 3.1 Bug 修复工作流

```
Bug 报告
│
├─► 1. 加载 system-debugging Skill
│   └─► 强制根本原因分析，禁止猜测修复
│
├─► 2. 加载 unittest Skill
│   └─► 先写回归测试，验证 Bug 存在
│
├─► 3. 实现修复
│   └─► 最小修改，验证测试通过
│
├─► 4. 加载 defense-in-depth Skill（如涉及敏感操作）
│   └─► 检查安全影响
│
└─► 5. 加载 gongfeng-mr Skill
    └─► 提交代码，创建 MR
```

### 3.2 新功能开发工作流

```
功能需求
│
├─► 1. 加载 brainstorming Skill
│   └─► 苏格拉底式提问，澄清需求
│
├─► 2. 加载 writing-plans Skill
│   └─► 拆分为原子任务
│
├─► 3. 加载 knowledge-base Skill
│   └─► 参考相关架构和最佳实践
│
├─► 4. 加载 unittest Skill
│   └─► TDD 红-绿-重构循环
│
├─► 5. 加载 defense-in-depth Skill（如涉及敏感操作）
│   └─► 安全检查
│
└─► 6. 加载 gongfeng-mr Skill
    └─► 提交代码，创建 MR
```

### 3.3 代码重构工作流

```
重构需求
│
├─► 1. 加载 brainstorming Skill
│   └─► 明确重构目标和范围
│
├─► 2. 加载 unittest Skill
│   └─► 确保有足够的测试覆盖
│
├─► 3. 执行重构
│   └─► 每步验证测试仍通过
│
└─► 4. 加载 gongfeng-mr Skill
    └─► 提交代码，创建 MR
```

### 3.4 技术调研工作流

```
调研需求
│
├─► 1. 加载 brainstorming Skill
│   └─► 明确调研目标和评估维度
│
├─► 2. 加载 knowledge-base Skill
│   └─► 参考现有知识
│
└─► 3. 输出调研结论
    └─► 按需沉淀到知识库
```

---

## 4. Skill 协作模式

### 4.1 串行模式

某些 Skill 必须按顺序执行：

```
brainstorming → writing-plans → unittest → gongfeng-mr
    ↓               ↓              ↓           ↓
 需求澄清       任务拆分        TDD开发      提交代码
```

### 4.2 并行/可选模式

某些 Skill 可以根据需要加载：

```
        ┌─ defense-in-depth（涉及安全时）
主流程 ─┼─ knowledge-base（需要参考时）
        └─ system-debugging（遇到问题时）
```

### 4.3 嵌套模式

执行过程中可能需要嵌套调用其他 Skill：

```
unittest Skill 执行中
│
├─► 发现测试失败原因不明
│   └─► 嵌套加载 system-debugging Skill
│
└─► 继续 unittest 流程
```

---

## 5. 执行规范

### 5.1 宣布 Skill 使用

加载 Skill 时，必须向用户宣布：

```markdown
> 🔧 **加载 [skill-name] Skill** - [简述原因]
```

示例：
```markdown
> 🔧 **加载 system-debugging Skill** - 检测到可能是 Bug 修复任务，需要按调试流程执行
```

### 5.2 遵循 Skill 指令

Skill 中的步骤是**强制性**的，必须：
- 按顺序执行每个步骤
- 不跳过任何检查点
- 完成验证后才能报告任务完成

### 5.3 记录执行过程

对于复杂任务，记录 Skill 执行过程：

```markdown
## 🚀 任务执行记录

### 1. Skill 检查
- [x] 识别任务类型：Bug 修复
- [x] 加载 system-debugging Skill
- [x] 加载 unittest Skill

### 2. system-debugging 执行
- [x] Phase 1: 根本原因调查
- [x] Phase 2: 模式分析
- [x] Phase 3: 假设验证
- [ ] Phase 4: 实现修复

### 3. 当前状态
正在执行 Phase 4...
```

---

## 6. 刚性 vs 柔性 Skill

### 6.1 刚性 Skill（必须严格遵循）

| Skill | 刚性程度 | 原因 |
|-------|---------|------|
| `system-debugging` | ⚫ 高 | 调试流程不可跳过，避免猜测修复 |
| `unittest` | ⚫ 高 | TDD 流程是强制的 |
| `defense-in-depth` | ⚫ 高 | 安全检查不可跳过 |

### 6.2 柔性 Skill（可适当调整）

| Skill | 柔性程度 | 说明 |
|-------|---------|------|
| `brainstorming` | ⚪ 中 | 简单需求可简化问题数量 |
| `writing-plans` | ⚪ 中 | 小任务可简化拆分 |
| `knowledge-base` | ⚪ 高 | 按需加载参考内容 |

---

## 7. 任务执行

### 7.1 收到用户消息时

1. **立即执行 Skill 检查**（不要先回答问题）
2. **识别任务类型**
3. **加载适用的 Skill**
4. **按 Skill 指导执行**

### 7.2 执行过程中

1. **遵循当前 Skill 的步骤**
2. **遇到新情况时检查是否需要加载其他 Skill**
3. **完成每个检查点后才能继续**

### 7.3 任务完成时

1. **确认所有 Skill 步骤已完成**
2. **执行验证步骤**
3. **报告任务完成**

---

## 8. 快速参考

### 8.1 可用 Skill 列表

| Skill | 触发场景 | 核心价值 |
|-------|----------|----------|
| `brainstorming` | 需求模糊、方案设计 | 苏格拉底式提问，澄清需求 |
| `writing-plans` | 复杂任务、需要拆分 | 原子任务拆分，有序执行 |
| `system-debugging` | Bug、异常、调试 | 根本原因分析，禁止猜测 |
| `unittest` | 编写测试、TDD 开发 | 红-绿-重构循环 |
| `defense-in-depth` | 安全敏感操作 | 多层安全检查 |
| `gongfeng-mr` | 提交代码、创建 MR | Code Review 自检 |
| `knowledge-base` | 查阅/沉淀知识 | 团队知识共享 |
| `command-skill-creator` | 创建新 Skill | 扩展 AI 能力 |

### 8.2 禁止行为

- ❌ 禁止跳过 Skill 检查直接回答
- ❌ 禁止以"简单任务"为由跳过流程
- ❌ 禁止在未验证的情况下报告完成
- ❌ 禁止猜测性修复（调试任务）
- ❌ 禁止跳过测试（开发任务）

---

**记住**：这个 Skill 是 AI Native 开发的基础。每次收到用户消息，第一件事就是检查并加载适用的 Skill。这不是可选的，而是强制的。