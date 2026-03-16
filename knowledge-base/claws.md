---
title: claws
type: note
permalink: engineering-playbook/knowledge-base/claws
---

# CLAWS (Continuous Learning And Working System) 完整经验档案

> 项目周期: 2026-02-28 ~ 进行中
> 最后更新: 2026-02-28
> 状态: 活跃开发

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | 自主探索系统 / 长运行编排器 |
| **领域** | AI Agent 编排、信息发现、品味自进化 |
| **规模** | ~850 行 Python + 3 个 Knot Agent + 4 阶段 Pipeline |
| **核心价值** | 7×24h 自动探索技术前沿，用可进化的品味模型过滤信息噪音，将发现沉淀为可行动的知识 |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 语言 | Python | 3.11+ | dataclass + async/await |
| Agent 平台 | Knot Agent (AG-UI) | - | 三个独立 Agent ID + 云工作区 |
| 调度 | APScheduler | 3.x | AsyncIOScheduler |
| HTTP | httpx | - | SSE 流式接收 |
| 部署 | Docker + docker-compose | - | 含健康检查 |
| 监控 | ops-dashboard | - | Push 层事件上报 |
| 推送 | 飞书 Webhook | - | 卡片消息 |

### 架构概览

```
  APScheduler (本地调度器)
       │
       ├── Phase 1: Scout (deepseek-v3.2 + web search)
       │   └── SENSE + FILTER → memory/raw/ + memory/filtered/
       │
       ├── Phase 2: Analyst (claude-4.5-sonnet + web search)
       │   └── DIVE → memory/deep-dives/
       │
       ├── Phase 3: Evolve (claude-4.5-sonnet)
       │   └── REFLECT → TASTE.md / SOUL.md / DISCOVERIES.md 自进化
       │
       └── Phase 4: Reviewer (Analyst Agent 复用)
           └── REVIEW → 商业可行性 + 品味审计 + 认知盲区检测
                         └── memory/reviews/ + memory/feedback/
```

---

## 做得好的地方

### 技术选型

#### Knot Agent (AG-UI) 替代 OpenClaw

- **技术**: Knot Agent 平台 + AG-UI 协议
- **场景**: 长运行 Agent 编排
- **考虑过的备选**: OpenClaw（自建 Agent 运行时）
- **选择理由**: OpenClaw API 成本高；Knot Agent 免费且自带云工作区（可读写文件系统）
- **实际效果**: 零 API 成本，三个专用 Agent 各司其职，云工作区让 Agent 可直接读写上下文文件
- **推荐指数**: 5/5
- **适用建议**: 适合内部使用、API 成本敏感的场景。不适合需要低延迟的实时系统（Agent 响应 200-330s）

#### 多模型策略（便宜模型扫描 + 强模型分析）

- **技术**: Scout 用 deepseek-v3.2（便宜快速），Analyst/Evolve 用 claude-4.5-sonnet（准确深入）
- **场景**: 分阶段使用不同成本/能力的模型
- **选择理由**: 扫描追求广度（不需要最强模型），分析追求深度（值得用贵模型）
- **实际效果**: 成本优化的同时保持分析质量
- **推荐指数**: 5/5
- **适用建议**: 任何多阶段 AI Pipeline 都应考虑此模式

### 架构设计

#### 品味自进化机制

- **解决的问题**: 如何让 AI 系统持续改进自己的判断标准，而非依赖固定规则
- **实现方式**: 
  1. `TASTE.md` 作为可读写的品味模型文件
  2. `Evolve Agent` 每日反思，输出包含 `new_taste_md` 字段的 JSON
  3. `_apply_evolution()` 将 JSON 中的内容覆盖写入文件
  4. `taste-changelog.md` 记录每次变更的证据
- **关键代码**: `_apply_evolution()` 方法
- **可复用程度**: 高——任何需要"自适应参数"的系统都可以用此模式

#### Reviewer Agent 自动反馈回路

- **解决的问题**: 传统 AI 系统依赖人工反馈，但人不可能 24h 在线审查
- **实现方式**: 用 Analyst Agent 充当"独立审计师"，每日 21:30 自动审查当天的发现和品味进化
- **关键设计**: Reviewer 的 Prompt 包含商业可行性（TAM/SAM、MVP 成本）、品味审计（回音壁风险）、认知盲区检测三个维度
- **可复用程度**: 高——任何自主系统都需要"自我审查"机制

#### 标准化 Agent 定义（main.md 元数据模式）

- **解决的问题**: 多 Agent 系统中，每个 Agent 的配置散落在不同文件
- **实现方式**: 每个 Agent 有独立目录 `config/agents/<name>/main.md`，包含标准化元信息（名称、描述、MCP 依赖、云工作区）+ Prompt
- **关键设计**: Runner 的 `_load_prompt()` 自动从 `main.md` 提取 `## Prompt` 之后的内容
- **可复用程度**: 高——任何多 Agent 项目

---

## 做得不好的地方

### 踩坑清单

#### 1. JSON 解析 LLM 输出的脆弱性

- **影响程度**: 🟡 中
- **耗时**: ~2h
- **现象**: `JSONDecodeError: Expecting ',' delimiter` — Evolve Agent 输出的 JSON 中含有未转义的中文引号（`"信号vs噪声"`）
- **排查过程**: 对比 raw output 和解析器预期，发现 CJK 引号和未转义双引号两类问题
- **根因**: LLM 在生成包含 Markdown 内容的 JSON 字符串时，不会正确转义内部引号
- **解决方案**: `extract_json()` 增加 `_fix_inner_quotes()` 辅助函数，基于上下文分析判断引号是结构性的还是内容性的
- **预防建议**: 任何从 LLM 提取 JSON 的场景，都必须有多层容错解析。不要依赖 LLM 生成完美 JSON

#### 2. Python str.format() 与 JSON 花括号冲突

- **影响程度**: 🔴 高（阻塞运行）
- **耗时**: ~30min
- **现象**: `KeyError: '\n "scan_time"'` — Prompt 模板中的 JSON 示例被 Python 当作 format 占位符
- **根因**: 使用 `f"..."` 或 `.format()` 渲染 Prompt 模板，但 Prompt 中包含 JSON 花括号
- **解决方案**: 改用 `str.replace()` 做显式变量替换，避免 Python 解析花括号
- **预防建议**: Prompt 模板渲染永远不要用 `str.format()` 或 f-string，用 `replace()` 或 Jinja2

#### 3. Evolve Agent 与 Runner 的写冲突

- **影响程度**: 🟡 中
- **耗时**: ~1h
- **现象**: `taste-changelog.md` 被写入两份相同内容——Evolve Agent 通过云工作区写了一次，Runner 的 `_apply_evolution` 又追加了一次
- **根因**: Evolve Agent 有云工作区写权限，且 Prompt 中没有明确禁止它直接写文件
- **解决方案**: 明确职责分工——Runner 负责所有文件写入，Evolve Agent 的 Prompt 中只输出 JSON，不直接操作文件
- **预防建议**: 多组件系统中，对共享资源的写权限必须有明确的唯一写入者

#### 4. httpx timeout 与实际执行时间不匹配

- **影响程度**: 🟡 中（在流式场景下被掩盖）
- **现象**: timeout 设 180s 但 Analyst 实际执行 331s，因为 SSE streaming 的 read timeout 行为与普通请求不同
- **解决方案**: 改用分离式 timeout：`httpx.Timeout(connect=30, read=600, write=30, pool=30)`，给 read 足够长时间
- **预防建议**: 流式 API 的 timeout 必须区分连接超时和读取超时

---

## 可复用资产

### 代码模式

| 资产 | 路径 | 描述 |
|------|------|------|
| 多层容错 JSON 提取器 | `extract_json()` | 处理 LLM 输出中的各种 JSON 格式错误 |
| Knot AG-UI 流式客户端 | `KnotClient` | SSE 流式接收、双模式认证 |
| 品味自进化框架 | `_apply_evolution()` | 文件化的参数自进化机制 |
| Reviewer Agent Prompt | `run_review()` | 商业+品味+盲区三维审查模板 |

### 配置模板

| 资产 | 描述 |
|------|------|
| `config/agents/<name>/main.md` | 标准化 Agent 定义模板（元数据+Prompt） |
| `agents.yaml` | 多 Agent Pipeline 编排配置 |
| `docker-compose.yml` | 长运行 Agent 系统的容器化部署 |

---

## 给未来自己的建议

1. **LLM 输出永远不可信**——JSON 解析必须有 3 层以上的 fallback（直接解析→代码块提取→子串提取→修复后重试）
2. **多 Agent 系统的写权限必须收敛**——一个文件只能有一个写入者，否则必然冲突
3. **品味模型需要"反向声音"**——只参考同质化信息源会形成回音壁，Reviewer Agent 的引入是解药
4. **"行动建议"必须可执行**——"持续关注"不是行动建议，"周五前 clone 仓库并跑 benchmark"才是
5. **成本是商业化的第一约束**——任何技术分析都应该包含"谁买单、花多少钱"的维度

---

## 元数据

| 维度 | 值 |
|------|-----|
| 作者 | CLAWS + archerpyu |
| 创建日期 | 2026-02-28 |
| Playbook 版本 | 1.0 |
| 关联项目 | alpha-radar, infohunter, ops-dashboard |
| 标签 | AI Agent, 自进化, 品味模型, 长运行编排器, Knot Agent |