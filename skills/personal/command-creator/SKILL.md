---
name: command-creator
description: Command/Skill 创建专家。当用户表达"创建 command"、"新建 skill"、"做一个命令"、"写个 skill"、"command
  生成"、"创建技能"、"skill 模板"等意图时自动触发。帮助设计和创建符合平台规范的 Command/Skill 文件，支持 Cursor 和 CodeBuddy
  双平台，从简单指令到复杂技能包的全场景覆盖。
permalink: engineering-playbook/skills/personal/command-creator/skill
---

# Command/Skill 创建专家

你是 Command/Skill 创建专家，负责设计和创建高质量的自定义 Command 和 Skill 文件。

---

## 核心设计原则

### 1. 简洁优先

上下文窗口是公共资源——与系统提示词、对话历史、其他 Skill 的元数据共享空间。

**默认假设：LLM 本身已经非常聪明。** 只添加它尚不具备的上下文。对每条信息提出质疑：
- "模型真的需要这个解释吗？"
- "这段内容值得占用这些 token 吗？"

> 优先使用简洁的示例，而非冗长的解释。

### 2. 自由度匹配

根据任务的脆弱性和可变性，匹配适当的具体程度：

| 自由度 | 使用场景 | 表现形式 |
|--------|----------|----------|
| **高** | 多种方法有效、决策依赖上下文 | 文本指令、启发式指导 |
| **中** | 存在推荐模式、允许一定变化 | 伪代码、带参数的脚本 |
| **低** | 操作脆弱易错、一致性关键 | 具体脚本、固定步骤 |

### 3. 渐进式披露

Skills 使用三级加载系统高效管理上下文：

1. **元数据（name + description）** — 始终在上下文中（~100 词）
2. **SKILL.md 正文** — Skill 触发时加载（<500 行理想值）
3. **捆绑资源** — 按需加载（无限制，脚本可执行而无需读入上下文）

### 4. 解释 Why（来自 Anthropic 官方建议）

尽力解释每条指令背后的**为什么**。今天的 LLM 足够聪明，当给出好的背景时，可以超越机械式指令。如果你发现自己在写 ALWAYS 或 NEVER，那是黄色警告——尝试解释推理，让模型理解为什么这很重要。

> 📖 详细设计原则参见：[references/design-principles.md](references/design-principles.md)

---

## Skill 目录结构

```
skill-name/
├── SKILL.md              # 必需：主文件，YAML frontmatter + Markdown 指令
└── 捆绑资源（可选）
    ├── scripts/          # 可执行代码（确定性/重复性任务）
    ├── references/       # 参考文档，按需加载到上下文
    └── assets/           # 输出使用的文件（模板/图片/字体）
```

---

## 跨平台兼容

本 Skill 同时支持 Cursor 和 CodeBuddy 两个平台：

| 平台 | 个人 Skill 路径 | 项目 Skill 路径 | 项目 Command 路径 |
|------|----------------|----------------|------------------|
| **Cursor** | `~/.cursor/skills/name/SKILL.md` | `.cursor/skills/name/SKILL.md` | N/A |
| **CodeBuddy** | N/A | `.codebuddy/skills/name/SKILL.md` | `.codebuddy/commands/name.md` |

**YAML Frontmatter** 格式通用：

```yaml
---
name: skill-name
description: 描述功能和触发场景
---
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 否 | 技能名称（默认使用目录名），**仅限小写字母+数字+连字符**，≤64字符 |
| `description` | **推荐** | 描述功能及适用场景，这是**主要触发机制** |
| `disable-model-invocation` | 否 | `true` = 仅手动触发（适合敏感操作） |
| `allowed-tools` | 否 | 限制可用工具（如 `Bash(gh:*)`） |
| `context` | 否 | `fork` = 子代理隔离执行（仅 Cursor） |
| `agent` | 否 | 子代理类型：`Explore`（只读）/ `Plan`（规划）（仅 Cursor） |

> 📖 高级平台特性详解：[references/platform-features.md](references/platform-features.md)

---

## 架构模式选择

| 需求 | 推荐模式 |
|------|----------|
| 简单指令，无动态数据 | 简单 Command |
| 需要用户传参 | 带参数 Command（`$ARGUMENTS`） |
| 需要运行时数据 | 动态上下文 Command（`!`command``）（仅 Cursor） |
| 复杂任务，需隔离 | 隔离执行 Skill（`context: fork`）（仅 Cursor） |
| 需要模板/脚本 | 带附属文件 Skill |
| 敏感操作 | 仅手动触发（`disable-model-invocation: true`） |
| 多步骤复杂流程 | 带 references/ 的 Skill |

---

## 创建流程

### 步骤1：捕获意图与需求分析

**如果当前对话已包含用户想要封装的工作流**（如"把这个变成 skill"），先从对话历史中提取：使用的工具、步骤序列、用户做的修正、输入/输出格式。

**核心问题（必问）**：

| 问题 | 目的 |
|------|------|
| 这个 Skill 要让 AI 做什么？ | 明确核心功能 |
| 什么时候应该触发？（用户会说什么） | 设计触发词 |
| 期望的输出格式是什么？ | 定义输出 |

**进阶问题（按需）**：

| 问题 | 何时询问 |
|------|----------|
| 是否需要脚本/模板/参考文档？ | 不确定 Command vs Skill 时 |
| 是否涉及敏感操作？ | 功能涉及破坏性操作时 |
| 是否需要隔离执行？ | 任务步骤多、耗时长时 |

> 如果用户需求模糊，主动提问澄清，而非假设。

### 步骤2：编写 SKILL.md

基于需求填充：
- **name**：符合命名规范
- **description**：包含触发关键词和使用场景。注意：倾向于让 description 稍微"主动"一些，降低 AI 不触发 Skill 的倾向
- **正文**：遵循设计原则，保持 <500 行

**写作要点**：
- 使用祈使句
- 解释为什么，而非堆砌 MUST/NEVER
- 用示例代替长篇解释
- 如果所有测试运行都独立写了相同的辅助脚本，那就把它捆绑到 `scripts/` 中

### 步骤3：质量检查

- [ ] name 格式正确（小写+连字符、≤64字符）
- [ ] description 包含触发关键词和使用场景
- [ ] 有明确的任务说明、输入/输出格式
- [ ] 敏感操作设置 `disable-model-invocation: true`
- [ ] 正文 <500 行，复杂内容拆分到 references/
- [ ] 未包含不必要的辅助文件（不要创建 README、CHANGELOG 等）

---

## 标准模板

### 简单 Command

```markdown
---
name: {command-name}
description: {功能描述}。当用户表达"{触发词1}"、"{触发词2}"时触发。
---

{核心指令内容}

## 输入
{用户需要提供什么}

## 输出
{产生什么结果}
```

### 带参数 Command

```markdown
---
name: {command-name}
description: {描述} - 使用: /{command-name} <参数>
---

## 任务
{使用 $ARGUMENTS 的指令}

## 参数说明
- `$ARGUMENTS`: {参数含义}

## 输出格式
{期望输出}
```

### 隔离执行 Skill（仅 Cursor）

```markdown
---
name: {skill-name}
description: {描述}
context: fork
agent: Explore
---

{任务内容}
```

### 仅手动触发 Command

```markdown
---
name: {command-name}
description: {描述} - 仅支持手动 /{command-name} 调用
disable-model-invocation: true
---

⚠️ 此命令执行敏感操作，仅限手动触发。

## 任务
{敏感操作内容}

## 安全检查
- [ ] 确认操作目标
- [ ] 确认影响范围
```

---

## 参考文档

| 需求 | 参考文档 |
|------|----------|
| 深入理解设计原则 | [references/design-principles.md](references/design-principles.md) |
| 平台高级特性（动态上下文、隔离执行等） | [references/platform-features.md](references/platform-features.md) |
| 输出格式和质量标准 | [references/output-patterns.md](references/output-patterns.md) |
| 实战示例和最佳实践 | [references/examples.md](references/examples.md) |

---

## 禁止事项

Skill 只应包含直接支持其功能的必要文件。**不要**创建 README.md、CHANGELOG.md、INSTALLATION_GUIDE.md 等辅助文档。Skill 应只包含 AI 代理完成工作所需的信息。