---
title: self-evolving-agent-pipeline
type: note
permalink: engineering-playbook/patterns/self-evolving-agent-pipeline
---

# Pattern: 自进化多 Agent Pipeline

## 适用场景

- 需要 7×24h 持续运行的自主探索/监控系统
- 多阶段处理（采集→分析→进化→审查）
- 系统参数（品味、偏好、阈值）需要根据运行反馈自动调整
- 人工无法实时参与反馈循环

## 核心架构

```
  调度器 (APScheduler / Cron)
       │
       ├── Phase 1: Scout (便宜模型 + 联网)
       │   └── 广度采集 → 初筛 → 结构化 JSON
       │
       ├── Phase 2: Analyst (强模型 + 联网)
       │   └── 深度分析 → 商业评估 → 行动建议
       │
       ├── Phase 3: Evolve (强模型，不联网)
       │   └── 反思 → 参数进化 → 覆盖配置文件
       │
       └── Phase 4: Reviewer (复用 Analyst)
           └── 独立审计 → 商业可行性 → 盲区检测
                         └── 反馈信号 → 下轮 Evolve 输入

  共享状态（文件系统）：
    TASTE.md ← Evolve 写入，Scout/Analyst 读取
    SOUL.md  ← Evolve 写入
    memory/  ← 各阶段写入，下游读取
```

## 关键设计决策

### 1. 多模型策略

| 阶段 | 模型选择 | 理由 |
|------|---------|------|
| Scout | 便宜/快速模型 | 追求广度，不需要深度推理 |
| Analyst | 强模型 | 追求深度和准确性 |
| Evolve | 强模型 | 反思需要强推理能力 |
| Reviewer | 复用 Analyst | 审查需要客观判断 |

### 2. 文件化状态管理

所有状态通过 Markdown 文件管理（不用数据库）：
- 优点：Agent 可直接读写、版本可追溯、人可阅读
- 缺点：并发写入需要协调
- 关键约束：**一个文件只能有一个写入者**

### 3. 自进化机制

```
探索数据 → Evolve Agent 反思 → JSON 输出（含 new_config 字段）
                                      ↓
                              Runner 解析 → 覆盖写入配置文件
                                      ↓
                              changelog 追加（版本追踪）
```

进化规则：
- 正反馈 → 提升相关权重
- 负反馈 → 降低相关权重
- 自发现 → 扩展关注边界
- 过时淘汰 → 移除或降级

### 4. 自动反馈回路（替代人工）

人工反馈的瓶颈：不可能 24h 在线审查。解决方案：

用独立 Agent 充当"审计师"，评估维度：
- 商业可行性（TAM/市场/MVP 成本）
- 品味审计（回音壁风险）
- 认知盲区检测
- 行动建议可执行性评分

输出结构化 feedback → 下一轮 Evolve 的输入。

## 通用踩坑

| 坑 | 表现 | 解决方案 |
|----|------|---------|
| LLM JSON 输出不可靠 | 中文引号、未转义引号、尾随逗号 | 多层容错解析器（直接→代码块→子串→修复） |
| Prompt 模板与 JSON 冲突 | `str.format()` 把 JSON 花括号当占位符 | 用 `str.replace()` 做显式替换 |
| 多组件写同一文件 | 内容重复或覆盖 | 明确唯一写入者，其他只读 |
| 流式 API timeout | 连接成功但读取超时 | 分离 connect/read timeout |
| Agent 采集量不足 | 找到几个高分就停 | Prompt 中强制最低采集量约束 |
| 品味回音壁 | 只关注正向信息源 | 引入反向声音和独立审查者 |

## 前后对比

| 维度 | 改进前 | 改进后 |
|------|--------|--------|
| 反馈 | 依赖人工 | Reviewer Agent 自动审查 |
| 品味 | 固定权重 | 每日自进化 + 版本追踪 |
| 商业 | 纯技术视角 | TAM/MVP/对标 多维评估 |
| 运维 | 手动运行 | Docker + Ops 告警 + 飞书推送 |
| 可靠性 | 单点 timeout | 分离式 timeout + 连续失败告警 |