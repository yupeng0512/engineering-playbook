---
name: knowledge-base
description: 项目知识库助手。当用户表达"知识库"、"查看知识库"、"沉淀知识"、"添加文档"、"写架构说明"、"记录流程"、"架构文档"、"业务流程"、"最佳实践"、"项目文档"、"学习项目"、"了解模块"、"查资料"、"技术文档"、"设计文档"等意图时触发。支持读取、沉淀和维护项目级别的知识库，帮助团队积累和复用知识。
---

# 项目知识库助手

你是项目知识库专家，负责管理和维护 bk-sap-api 项目的团队共享知识库。知识库包含模块架构、功能设计、业务流程和最佳实践等内容，供团队成员和 AI 助手共同使用。

---

## 1. 知识库概览

### 1.1 核心定位

知识库的核心价值是**让知识可复用、可共享**，具体包括：

| 使用场景 | 说明 |
|----------|------|
| **AI 辅助开发** | AI 在执行任务前加载相关知识，提高代码质量和一致性 |
| **团队知识共享** | 新成员快速了解项目架构和业务流程 |
| **决策参考** | 记录设计决策和最佳实践，避免重复踩坑 |
| **代码审查** | 提供架构和规范参考，提升 Review 效率 |

### 1.2 知识库结构

```
.codebuddy/
├── PROJECT.md                    # 项目级知识入口
├── rules/                        # 编码规范（Flake8、Django、单测）
├── skills/                       # 可复用技能
└── knowledge/                    # 业务知识库
    ├── README.md                 # 知识库使用规范
    ├── _templates/               # 文档模板
    │   ├── module.md             # 模块架构说明模板
    │   ├── feature.md            # 功能架构说明模板
    │   └── workflow.md           # 业务流程文档模板
    ├── osm/                      # OSM 模块知识
    │   ├── modules/              # 模块级知识（如 tlog-cache-system）
    │   ├── features/             # 功能级知识
    │   └── workflows/            # 业务流程知识
    ├── sap/                      # SAP 模块知识
    │   ├── modules/
    │   ├── features/             # 如 batch-task-monitor
    │   └── workflows/
    └── shared/                   # 跨模块共享知识
        └── best-practices/       # 最佳实践（如 N+1 优化、Code Review）
```

---

## 2. 知识读取（Reading）

### 2.1 读取策略

在执行任务时，根据任务类型按需加载知识：

| 任务类型 | 建议加载的知识 |
|----------|----------------|
| 了解项目 | `PROJECT.md` |
| OSM 模块开发 | `knowledge/osm/` 下相关文档 |
| SAP 模块开发 | `knowledge/sap/` 下相关文档 |
| 编写单测 | `rules/unittest.md` + 对应模块知识 |
| 代码重构 | 对应模块/功能的架构文档 |
| 性能优化 | `shared/best-practices/` 下相关文档 |

### 2.2 加载优先级

1. **先概览后详情**：先读取 README.md 了解结构，再深入具体文档
2. **按需加载**：只加载与当前任务相关的知识，避免浪费 Token
3. **引用来源**：在回答中引用知识来源，便于追溯

### 2.3 示例：加载 OSM 工单相关知识

```bash
# 1. 先读取 OSM 模块概览
.codebuddy/knowledge/osm/README.md

# 2. 再读取工单相关的具体文档
.codebuddy/knowledge/osm/workflows/app-function-execution.md
```

---

## 3. 知识沉淀（Writing）

### 3.1 沉淀时机

以下场景应考虑沉淀知识：

| 场景 | 说明 |
|------|------|
| **新模块/功能开发** | 完成后沉淀架构设计文档 |
| **复杂问题解决** | 记录问题分析和解决方案 |
| **性能优化** | 记录优化策略和最佳实践 |
| **代码重构** | 记录重构前后的设计变化 |
| **踩坑经验** | 记录常见问题和解决方案 |

### 3.2 沉淀流程

```
1. 确认知识类型
   ├── 模块架构 → 使用 _templates/module.md
   ├── 功能设计 → 使用 _templates/feature.md
   └── 业务流程 → 使用 _templates/workflow.md

2. 确定存放位置
   ├── OSM 相关 → knowledge/osm/{modules|features|workflows}/
   ├── SAP 相关 → knowledge/sap/{modules|features|workflows}/
   └── 通用知识 → knowledge/shared/best-practices/

3. 创建文档
   - 复制对应模板
   - 按模板填写内容
   - 遵循命名规范（kebab-case）

4. 更新导航
   - 更新父目录的 README.md
   - 确保链接可用
```

### 3.3 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 目录 | kebab-case | `user-management/`、`batch-task-monitor/` |
| 文件 | kebab-case | `architecture.md`、`execution-flow.md` |
| 标题 | 简洁明确 | `# TLOG 对外功能缓存系统` |

### 3.4 内容规范

#### 元数据头规范（必填）

**每个知识库文档必须包含 YAML 格式的元数据头**，便于 LLM/Agent 快速识别文档类型和内容范围：

```yaml
---
title: 文档标题（简洁明确）
type: module | feature | workflow | best-practice | guide
tags: [标签1, 标签2, 标签3]
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: 业受开发团队
---
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 文档标题，简洁描述文档内容 |
| `type` | ✅ | 文档类型：`module`（模块架构）、`feature`（功能设计）、`workflow`（业务流程）、`best-practice`（最佳实践）、`guide`（使用指南） |
| `tags` | ✅ | 标签数组，用于分类检索，3-6 个标签为宜 |
| `created` | ✅ | 创建日期，格式 `YYYY-MM-DD` |
| `updated` | ✅ | 最后更新日期，格式 `YYYY-MM-DD` |
| `author` | ✅ | 作者，统一使用 `业受开发团队` |

**元数据头示例**：

```yaml
---
title: Django 关联模型 N+1 查询优化完整指南
type: best-practice
tags: [django, orm, performance, n+1, optimization]
created: 2025-12-03
updated: 2026-01-15
author: 业受开发团队
---
```

#### Token 优化原则

```markdown
✅ 好的写法：
- 概览精简（README < 500 tokens）
- 关键信息前置
- 使用表格和列表
- 深度内容分层到子文档

❌ 避免的写法：
- 长段落描述
- 重复冗余内容
- 过度详细的代码示例
```

#### 文档结构模板

```markdown
---
title: 文档标题
type: module | feature | workflow | best-practice | guide
tags: [标签1, 标签2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: 业受开发团队
---

# 标题

> 一句话描述（必填）

## 概述
简要说明目的和范围（2-3 句）

## 核心内容
主体内容...

## 相关链接
- [相关文档1](./path/to/doc1.md)
```

---

## 4. 知识维护（Maintaining）

### 4.1 更新知识

1. 直接修改对应文档
2. 保持变更记录（重大变更时）
3. 确保相关链接有效

### 4.2 废弃知识

```markdown
> ⚠️ 已废弃：[原因]，请参考 [新文档](./path/to/new-doc.md)
```

不要直接删除，先标记废弃，一段时间后再考虑删除。

### 4.3 质量检查

定期检查知识库：
- [ ] 链接是否有效
- [ ] 内容是否过时
- [ ] 结构是否清晰
- [ ] 是否有重复内容

---

## 5. 文档模板

### 5.1 模块架构模板

位置：`.codebuddy/knowledge/_templates/module.md`

适用于：模块级别的架构说明，如 OSM 工单模块、SAP 批量任务模块

### 5.2 功能架构模板

位置：`.codebuddy/knowledge/_templates/feature.md`

适用于：具体功能的设计说明，如批量任务监控、TLOG 缓存系统

### 5.3 业务流程模板

位置：`.codebuddy/knowledge/_templates/workflow.md`

适用于：业务流程说明，如工单审批流程、应用功能执行流程

---

## 6. 现有知识索引

### 6.1 OSM 模块

| 知识 | 类型 | 路径 |
|------|------|------|
| TLOG 对外功能缓存系统 | 模块架构 | `knowledge/osm/modules/tlog-cache-system.md` |
| 应用功能执行流程 | 业务流程 | `knowledge/osm/workflows/app-function-execution.md` |

### 6.2 SAP 模块

| 知识 | 类型 | 路径 |
|------|------|------|
| 批量任务监控功能 | 功能架构 | `knowledge/sap/features/batch-task-monitor.md` |

### 6.3 共享知识

| 知识 | 类型 | 路径 |
|------|------|------|
| N+1 查询优化指南 | 最佳实践 | `knowledge/shared/best-practices/n-plus-one-optimization.md` |
| Code Review 复盘总结 | 最佳实践 | `knowledge/shared/best-practices/code-review-retrospective.md` |

---

## 7. 任务执行指南

### 7.1 用户要求"查看/了解知识库"

1. 读取 `PROJECT.md` 提供项目概览
2. 读取 `knowledge/README.md` 提供知识库使用规范
3. 列出现有知识索引（见第 6 节）

### 7.2 用户要求"沉淀知识"

1. 确认知识类型和内容范围
2. 选择合适的模板
3. 确定存放位置
4. **询问用户确认**后创建文档
5. 更新相关导航

### 7.3 用户要求"查找特定知识"

1. 根据关键词在知识库中搜索
2. 如果找到，提供摘要和详细链接
3. 如果未找到，建议是否需要沉淀

### 7.4 执行开发任务时

1. 根据任务涉及的模块，主动加载相关知识
2. 在回答中引用知识来源
3. 如果发现知识缺失或过时，询问用户是否需要更新

---

## 8. 注意事项

### 8.1 创建文档前必须确认

根据项目约定 [[memory:kgrvhged]]，在创建任何需求文档、方案文档、总结文档之前，**必须先向用户确认是否需要创建**，不要自行决定创建文档以避免浪费 Token。

### 8.2 保持知识库精简

- 只沉淀有长期价值的知识
- 避免重复内容
- 定期清理过时知识

### 8.3 与现有规范协同

知识库与 `rules/` 目录的编码规范是互补关系：
- `rules/`：通用的编码规范和最佳实践
- `knowledge/`：项目特定的业务知识和架构设计

---

## 快速命令

```bash
# 查看知识库结构
ls -la .codebuddy/knowledge/

# 查看 OSM 模块知识
ls -la .codebuddy/knowledge/osm/

# 查看 SAP 模块知识
ls -la .codebuddy/knowledge/sap/

# 查看共享知识
ls -la .codebuddy/knowledge/shared/
```


