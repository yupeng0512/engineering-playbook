# 实战示例集合

本文档提供各种场景下的完整 Command/Skill 示例，可直接复制使用或作为参考。

---

## 目录

1. [简单 Command 示例](#简单-command-示例)
2. [带参数 Command 示例](#带参数-command-示例)
3. [动态上下文 Command 示例](#动态上下文-command-示例)
4. [隔离执行 Skill 示例](#隔离执行-skill-示例)
5. [带附属文件 Skill 示例](#带附属文件-skill-示例)
6. [仅手动触发 Command 示例](#仅手动触发-command-示例)

---

## 简单 Command 示例

### 代码格式化检查

```markdown
---
name: lint-check
description: 代码格式检查。当用户说"检查代码格式"、"lint"、"代码规范"时触发。
---

# 代码格式检查

## 任务
检查当前项目的代码格式问题。

## 检查项
1. **Python**: 使用 flake8 和 black 检查
2. **JavaScript/TypeScript**: 使用 eslint 检查
3. **Go**: 使用 gofmt 检查

## 输出格式
### 检查结果

| 文件 | 行号 | 问题类型 | 描述 |
|------|------|----------|------|

### 修复建议
{针对每个问题的修复建议}
```

### 生成 .gitignore

```markdown
---
name: gitignore
description: 生成 .gitignore 文件。当用户说"生成 gitignore"、"创建 gitignore"时触发。
---

# 生成 .gitignore

## 任务
根据项目类型生成合适的 .gitignore 文件。

## 步骤
1. 识别项目类型（Python/Node.js/Go/Java 等）
2. 识别使用的框架和工具
3. 生成包含以下内容的 .gitignore：
   - 语言特定的忽略规则
   - IDE/编辑器配置
   - 操作系统文件
   - 依赖目录
   - 构建产物
   - 环境配置文件

## 输出
生成 `.gitignore` 文件到项目根目录。
```

---

## 带参数 Command 示例

### Issue 快速修复

```markdown
---
name: fix-issue
description: 修复 GitHub issue - 使用: /fix-issue <issue-number>
allowed-tools: Bash(gh:*)
---

# 修复 Issue

## Issue 信息
!`gh issue view $ARGUMENTS --json title,body,labels,assignees`

## 任务
1. 分析 issue #$ARGUMENTS 的问题描述
2. 理解问题的根本原因
3. 定位相关代码文件
4. 实现修复
5. 编写或更新测试（如适用）
6. 验证修复有效

## 完成标准
- [ ] 问题已修复
- [ ] 相关测试通过
- [ ] 代码符合项目规范

## 提交格式
```
fix: 修复 #$ARGUMENTS - {简短描述}

{详细说明修复内容}

Closes #$ARGUMENTS
```
```

### 分支切换并拉取

```markdown
---
name: checkout
description: 切换到指定分支并拉取最新代码 - 使用: /checkout <branch-name>
---

# 分支切换

## 任务
切换到分支 `$ARGUMENTS` 并确保代码最新。

## 步骤
1. 检查当前工作区状态
2. 如果有未提交更改，提示用户处理
3. 切换到目标分支：`git checkout $ARGUMENTS`
4. 拉取最新代码：`git pull origin $ARGUMENTS`
5. 报告当前状态

## 输出
- 切换结果
- 当前分支状态
- 最新提交信息
```

### 依赖查询

```markdown
---
name: dep-info
description: 查询依赖包信息 - 使用: /dep-info <package-name>
---

# 依赖信息查询

## 任务
查询依赖包 `$ARGUMENTS` 的详细信息。

## 查询内容
1. **当前版本**：项目中安装的版本
2. **最新版本**：npm/PyPI 上的最新版本
3. **许可证**：开源许可证类型
4. **使用情况**：项目中哪些文件使用了这个依赖
5. **安全问题**：是否有已知漏洞

## 输出格式
### $ARGUMENTS 信息

| 属性 | 值 |
|------|-----|
| 当前版本 | |
| 最新版本 | |
| 许可证 | |
| 使用文件数 | |
| 安全状态 | |
```

---

## 动态上下文 Command 示例

### PR 差异摘要

```markdown
---
name: pr-summary
description: 生成当前 PR 的变更摘要。当用户说"PR 摘要"、"总结 PR"时触发。
allowed-tools: Bash(gh:*)
---

# PR 变更摘要

## PR 上下文
- **基本信息**: !`gh pr view --json title,body,author,baseRefName,headRefName`
- **变更文件**: !`gh pr diff --name-only`
- **提交历史**: !`gh pr view --json commits --jq '.commits[].messageHeadline'`

## 任务
生成这个 PR 的结构化摘要。

## 输出格式
### PR 摘要

**标题**: {PR 标题}
**作者**: {作者}
**分支**: {head} → {base}

### 变更概述
{1-2 句话总结这个 PR 做了什么}

### 主要变更
1. {变更 1}
2. {变更 2}
3. {变更 3}

### 影响范围
- 影响的模块: {列表}
- 变更文件数: {数量}
- 新增/删除行数: {统计}

### 关注点
{需要特别关注的内容，如 breaking changes、性能影响等}
```

### Git 状态报告

```markdown
---
name: git-status
description: 显示详细的 Git 仓库状态。当用户说"git 状态"、"仓库状态"时触发。
---

# Git 仓库状态

## 上下文数据
- **当前分支**: !`git branch --show-current`
- **状态**: !`git status --short`
- **最近提交**: !`git log -3 --oneline`
- **远程状态**: !`git remote -v`
- **暂存区**: !`git diff --cached --stat`

## 任务
分析并报告 Git 仓库的当前状态。

## 输出格式
### 仓库状态

| 项目 | 状态 |
|------|------|
| 当前分支 | |
| 与远程差异 | 领先/落后 x 个提交 |
| 未跟踪文件 | x 个 |
| 已修改文件 | x 个 |
| 已暂存文件 | x 个 |

### 最近活动
{最近 3 个提交的简要信息}

### 建议操作
{根据当前状态给出建议，如需要提交、需要拉取等}
```

---

## 隔离执行 Skill 示例

### PR 代码审查

```markdown
---
name: pr-review
description: PR 代码审查。当用户说"审查 PR"、"review PR"、"代码审查"时触发。
context: fork
agent: Explore
allowed-tools: Bash(gh:*)
---

# PR 代码审查

## PR 上下文
- **PR 信息**: !`gh pr view --json title,body,author,additions,deletions`
- **变更文件**: !`gh pr diff --name-only`
- **PR 差异**: !`gh pr diff`

## 审查要点

### 1. 代码质量
- 可读性和清晰度
- 复杂度是否合理
- 是否有重复代码
- 命名是否清晰

### 2. 安全性
- 敏感数据处理
- 输入验证
- 注入风险
- 权限检查

### 3. 性能
- 算法复杂度
- 数据库查询效率
- 内存使用
- 潜在的性能瓶颈

### 4. 测试覆盖
- 是否有对应测试
- 边界情况覆盖
- 测试质量

### 5. 一致性
- 是否符合项目规范
- 与现有代码风格一致

## 输出格式

### 总体评价
{LGTM / 需要修改 / 需要讨论}

### 审查摘要
{1-2 句话总结}

### 具体问题

| 文件 | 行号 | 级别 | 问题描述 |
|------|------|------|----------|
| ... | ... | 🔴/🟠/🟡 | ... |

### 详细说明
{对重要问题的详细解释和修复建议}

### 亮点
{代码中做得好的地方}
```

### 安全审计

```markdown
---
name: security-audit
description: 代码安全审计。当用户说"安全检查"、"安全审计"、"vulnerability scan"时触发。
context: fork
agent: Explore
---

# 代码安全审计

## 任务
对当前项目进行安全审计，识别潜在的安全漏洞。

## 审计范围

### 1. 输入验证
- [ ] SQL 注入
- [ ] XSS 跨站脚本
- [ ] 命令注入
- [ ] 路径遍历

### 2. 认证授权
- [ ] 硬编码凭证
- [ ] 弱密码策略
- [ ] 会话管理
- [ ] 权限检查

### 3. 数据保护
- [ ] 敏感数据加密
- [ ] 安全传输
- [ ] 日志脱敏

### 4. 依赖安全
- [ ] 已知漏洞
- [ ] 过期依赖

## 输出格式

### 安全评估

**风险等级**: 高/中/低
**发现问题**: X 个

### 漏洞清单

| ID | 严重程度 | 类型 | 位置 | 描述 |
|----|----------|------|------|------|
| V1 | 🔴 高 | | | |
| V2 | 🟠 中 | | | |

### 详细分析
{每个漏洞的详细说明和修复建议}

### 修复优先级
1. {最紧急的问题}
2. {次优先级}
3. ...
```

### 架构分析

```markdown
---
name: arch-analyze
description: 项目架构分析。当用户说"分析架构"、"架构评审"时触发。
context: fork
agent: Explore
---

# 项目架构分析

## 任务
分析当前项目的架构设计，识别优点和改进空间。

## 分析维度

### 1. 目录结构
- 组织方式
- 模块划分
- 职责分离

### 2. 依赖关系
- 模块间依赖
- 循环依赖
- 依赖方向

### 3. 设计模式
- 使用的模式
- 模式适用性

### 4. 可扩展性
- 扩展点
- 插件机制

### 5. 可测试性
- 依赖注入
- 接口抽象

## 输出格式

### 架构概览
{整体架构描述}

### 架构图
```mermaid
{生成架构图}
```

### 优点
1. {优点 1}
2. {优点 2}

### 改进建议
| 领域 | 当前状态 | 建议 | 优先级 |
|------|----------|------|--------|
| | | | |

### 技术债务
{识别的技术债务及处理建议}
```

---

## 带附属文件 Skill 示例

### 项目初始化

```
project-init/
├── SKILL.md
├── scripts/
│   └── setup.py
├── references/
│   └── conventions.md
└── assets/
    ├── python-template/
    ├── node-template/
    └── go-template/
```

**SKILL.md**:
```markdown
---
name: project-init
description: 初始化新项目。当用户说"新建项目"、"初始化项目"、"create project"时触发。
---

# 项目初始化

## 支持的项目类型
- Python（FastAPI/Django/Flask）
- Node.js（Express/NestJS/Next.js）
- Go（Gin/Echo）

## 流程
1. 确认项目类型和框架
2. 从 `assets/` 复制对应模板
3. 根据用户需求定制配置
4. 运行 `scripts/setup.py` 完成初始化

## 项目规范
详见 [references/conventions.md](references/conventions.md)

## 输出
- 项目目录结构
- 基础配置文件
- README.md
- .gitignore
- CI/CD 配置（可选）
```

---

## 仅手动触发 Command 示例

### 生产部署

```markdown
---
name: deploy-prod
description: 部署到生产环境 - 仅支持手动 /deploy-prod 调用
disable-model-invocation: true
allowed-tools: Bash(kubectl:*), Bash(docker:*)
---

# 生产环境部署

⚠️ **警告**：此命令将部署到生产环境，请确认已完成所有检查。

## 前置检查
- [ ] 所有测试通过
- [ ] 代码已审查
- [ ] 版本号已更新
- [ ] 文档已更新
- [ ] 回滚方案已准备

## 部署步骤
1. 构建生产镜像
2. 推送到镜像仓库
3. 更新 Kubernetes 部署
4. 验证部署状态
5. 运行冒烟测试

## 回滚命令
如需回滚，执行：
```bash
kubectl rollout undo deployment/{deployment-name}
```

## 输出
- 部署状态
- 服务健康检查结果
- 部署时间
```

### 数据库迁移

```markdown
---
name: db-migrate
description: 执行数据库迁移 - 仅支持手动 /db-migrate 调用
disable-model-invocation: true
---

# 数据库迁移

⚠️ **警告**：此命令将修改数据库结构，请确认已备份。

## 前置检查
- [ ] 数据库已备份
- [ ] 迁移脚本已测试
- [ ] 非高峰期执行
- [ ] 回滚脚本已准备

## 执行步骤
1. 验证数据库连接
2. 检查待执行的迁移
3. 执行迁移
4. 验证迁移结果

## 回滚
如需回滚，执行最近的 down 迁移：
```bash
python manage.py migrate {app_name} {previous_migration}
```

## 输出
- 执行的迁移列表
- 执行时间
- 验证结果
```

### 缓存清理

```markdown
---
name: clear-cache
description: 清理所有缓存 - 仅支持手动 /clear-cache 调用
disable-model-invocation: true
---

# 缓存清理

⚠️ **警告**：此操作将清除所有缓存，可能影响系统性能。

## 清理范围
- [ ] Redis 缓存
- [ ] 本地文件缓存
- [ ] CDN 缓存（可选）
- [ ] 浏览器缓存提示

## 影响评估
清理缓存后：
- 首次请求响应时间增加
- 数据库负载临时增加
- 预计恢复时间：5-10 分钟

## 执行确认
请输入 `CONFIRM` 确认执行。

## 输出
- 清理的缓存类型
- 释放的空间
- 完成时间
```

---

## 模板快速参考

| 场景 | 关键配置 |
|------|----------|
| 简单指令 | 无特殊配置 |
| 需要参数 | 使用 `$ARGUMENTS` |
| 需要运行时数据 | 使用 `!`command`` |
| 需要隔离 | `context: fork` + `agent: Explore/Plan` |
| 敏感操作 | `disable-model-invocation: true` |
| 限制工具 | `allowed-tools: Bash(xxx:*)` |
