---
title: platform-features
type: note
permalink: engineering-playbook/skills/personal/command-creator/references/platform-features
---

# CodeBuddy 平台高级特性

本文档详细介绍 CodeBuddy 平台提供的高级特性，帮助你创建功能强大的 Command/Skill。

---

## 目录

1. [动态上下文注入](#动态上下文注入)
2. [参数传递](#参数传递)
3. [调用控制](#调用控制)
4. [隔离执行](#隔离执行)
5. [工具限制](#工具限制)
6. [完整 Frontmatter 字段参考](#完整-frontmatter-字段参考)

---

## 动态上下文注入

### 基本语法

使用 `!`shell_command`` 语法在 Skill 内容发送给 Claude **之前**执行 shell 命令，并将输出替换到对应位置。

```markdown
## PR 上下文
- PR 差异: !`gh pr diff`
- 变更文件: !`gh pr diff --name-only`
- PR 信息: !`gh pr view --json title,body,author`
```

### 工作原理

1. 用户触发 Command/Skill
2. 平台扫描内容中的 `!`...`` 占位符
3. 执行对应的 shell 命令
4. 将命令输出替换到占位符位置
5. 将处理后的完整内容发送给 Claude

### 使用场景

| 场景 | 示例命令 |
|------|----------|
| Git/GitHub 信息 | `!`gh pr diff``, `!`git log -n 5`` |
| 系统信息 | `!`uname -a``, `!`date`` |
| 文件内容 | `!`cat config.json``, `!`head -20 file.txt`` |
| 环境变量 | `!`echo $PROJECT_ROOT`` |
| 自定义脚本 | `!`./scripts/gather_context.sh`` |

### 注意事项

1. **执行时机**：命令在发送给 Claude 之前执行，不是 Claude 执行的
2. **错误处理**：如果命令失败，错误信息会显示在对应位置
3. **安全考虑**：避免在动态上下文中使用危险命令
4. **性能考虑**：避免执行耗时过长的命令

---

## 参数传递

### 基本语法

使用 `$ARGUMENTS` 占位符接收用户调用时传入的参数。

```markdown
---
name: fix-issue
description: 修复 GitHub issue - 使用: /fix-issue <issue-number>
---

修复 GitHub issue #$ARGUMENTS，遵循项目编码规范。
```

### 调用方式

```
/fix-issue 123
```

Claude 收到的内容：
```
修复 GitHub issue #123，遵循项目编码规范。
```

### 与动态上下文结合

```markdown
---
name: fix-issue
description: 修复 GitHub issue - 使用: /fix-issue <issue-number>
allowed-tools: Bash(gh:*)
---

## Issue 信息
!`gh issue view $ARGUMENTS --json title,body,labels`

## 任务
1. 分析 issue #$ARGUMENTS 的问题描述
2. 定位相关代码
3. 实现修复
4. 编写测试（如适用）

## 完成后
提交格式：`fix: 修复 #$ARGUMENTS - {简短描述}`
```

### 多参数处理

`$ARGUMENTS` 包含用户输入的全部参数文本。如需解析多个参数，可在 Skill 中说明格式：

```markdown
---
name: compare-branches
description: 比较两个分支 - 使用: /compare-branches <base> <head>
---

## 参数说明
`$ARGUMENTS` 格式：`<base-branch> <head-branch>`

## 任务
比较分支差异：$ARGUMENTS
```

---

## 调用控制

### 调用方式对照表

| 设置 | 用户手动调用 | Claude 自动调用 |
|------|-------------|----------------|
| **默认（无设置）** | ✅ | ✅ |
| `disable-model-invocation: true` | ✅ | ❌ |
| `user-invocable: false` | ❌ | ✅ |

### disable-model-invocation

禁止 Claude 自动调用，仅允许用户手动触发。

**适用场景**：
- 敏感操作（删除、部署等）
- 破坏性命令
- 需要人工确认的操作
- 付费 API 调用

```yaml
---
name: deploy-production
description: 部署到生产环境 - 仅支持手动 /deploy-production 调用
disable-model-invocation: true
---
```

### user-invocable

禁止用户直接调用，仅允许 Claude 根据上下文自动调用。

**适用场景**：
- 内部辅助 Skill
- 作为其他 Skill 的组件
- 需要特定上下文才能正确执行的操作

```yaml
---
name: internal-helper
description: 内部辅助功能
user-invocable: false
---
```

---

## 隔离执行

### context: fork

在独立的子代理中执行 Skill，避免污染主对话上下文。

```yaml
---
name: pr-review
description: PR 代码审查
context: fork
agent: Explore
---
```

### agent 类型

| 类型 | 用途 | 能力 |
|------|------|------|
| **Explore** | 只读分析任务 | 读取文件、搜索代码、分析代码 |
| **Plan** | 规划任务 | 生成计划但不执行修改 |

### 适用场景

**使用 `context: fork` + `agent: Explore`**：
- 代码审查
- 代码分析
- 安全审计
- 依赖检查
- 文档生成（基于代码分析）

**使用 `context: fork` + `agent: Plan`**：
- 重构规划
- 迁移方案设计
- 架构评估

### 隔离执行的优势

1. **上下文隔离**：子代理的操作不影响主对话
2. **安全性**：限制子代理的能力范围
3. **专注性**：子代理专注于特定任务
4. **可重复性**：每次调用都是全新的上下文

---

## 工具限制

### allowed-tools

限制 Skill 可以使用的工具。

```yaml
---
name: gh-helper
description: GitHub 操作助手
allowed-tools: Bash(gh:*)
---
```

### 语法格式

| 格式 | 说明 | 示例 |
|------|------|------|
| `Bash(command:*)` | 允许特定命令的所有参数 | `Bash(gh:*)` |
| `Bash(command:subcommand)` | 允许特定子命令 | `Bash(gh:pr)` |
| 多个工具 | 逗号分隔 | `Bash(gh:*), Bash(git:*)` |

### 使用场景

1. **安全限制**：只允许特定的安全命令
2. **功能聚焦**：确保 Skill 专注于特定功能
3. **权限控制**：限制对敏感操作的访问

---

## 完整 Frontmatter 字段参考

```yaml
---
# 基础字段
name: skill-name                    # 技能名称（可选，默认使用目录名）
description: 功能描述                # 功能描述和触发场景（强烈推荐）

# 调用控制
disable-model-invocation: true      # 禁止 Claude 自动调用
user-invocable: false               # 禁止用户直接调用

# 隔离执行
context: fork                       # 在子代理中隔离执行
agent: Explore                      # 子代理类型（Explore / Plan）

# 工具限制
allowed-tools: Bash(gh:*)           # 限制可用工具
---
```

### 字段详细说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | string | 否 | 目录名 | 技能名称，≤64字符，小写+数字+连字符 |
| `description` | string | 推荐 | - | 功能描述，Claude 据此决定自动加载 |
| `disable-model-invocation` | boolean | 否 | false | true = 仅手动触发 |
| `user-invocable` | boolean | 否 | true | false = 仅 Claude 自动调用 |
| `context` | string | 否 | - | `fork` = 子代理隔离执行 |
| `agent` | string | 否 | - | 子代理类型：`Explore` / `Plan` |
| `allowed-tools` | string | 否 | - | 限制可用工具 |

### 命名规范

- 最大长度：64 字符
- 允许字符：小写字母、数字、连字符
- 不能以连字符开头或结尾
- 示例：`pr-review`、`fix-issue`、`deploy-prod`

---

## 组合使用示例

### 安全的 PR 审查

```yaml
---
name: pr-review
description: PR 代码审查。当用户说"审查 PR"、"review PR"时触发。
context: fork
agent: Explore
allowed-tools: Bash(gh:*)
---
```

### 敏感部署操作

```yaml
---
name: deploy-production
description: 部署到生产环境 - 仅支持手动 /deploy-production 调用
disable-model-invocation: true
allowed-tools: Bash(kubectl:*), Bash(docker:*)
---
```

### 带参数的 Issue 修复

```yaml
---
name: fix-issue
description: 修复 GitHub issue - 使用: /fix-issue <issue-number>
allowed-tools: Bash(gh:*)
---
```