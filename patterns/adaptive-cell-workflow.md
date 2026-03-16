---
title: adaptive-cell-workflow
type: pattern
permalink: engineering-playbook/patterns/adaptive-cell-workflow
date: 2026-03-14
tags:
- agent
- workflow
- subagent
- throughput
- review
---

# Pattern: Adaptive Cell Workflow

## 场景

这套工作流用于处理**复杂研发交付任务**，目标不是“让更多 Agent 一起工作”，而是：

**在不降低质量、不过界高风险边界的前提下，缩短复杂任务从理解到交付的端到端周期时间。**

典型场景：

- 任务横跨多个模块或多层系统
- 既要推进实现，又要同步文档、校验边界、复用经验
- 串行探索成本明显高于一次协调成本

## 第一性原理

### 主目标

- 最小化复杂任务的端到端周期时间

### 硬约束

- 质量不过线不交付
- 高风险边界不越界
- 不让知识同步和经验沉淀反客为主，拖慢主链路

### 推导结论

- 子 Agent 不是目的，而是减少串行探索时间的手段
- 只有当并行收益大于协调成本时，才启用角色化分工
- 不是所有任务都应该拆 3 个角色，更不是所有任务都值得启用多 Agent

## 解决的核心痛点

- 单线程推进时，上下文切换频繁，复杂任务容易被串行探索拖慢
- 风险审查、文档同步、经验沉淀常被挤到最后，导致返工和知识流失
- 多 Agent 协作如果没有合并协议，反而会增加沟通和裁决成本

## 三种运行模式

### `Solo Mode`

适合：

- 单模块、小改动、低风险、低歧义任务

规则：

- 主 Agent 单独推进
- 仍然要求执行基础 hygiene：`/progress-update`、`/doc-code-sync`、必要时 `/experience-capture`

### `Split-3 Mode`

默认复杂研发交付模式，启用 3 个 Cell：

- `framing-cell`
  - 负责目标澄清、spec 锚点、边界、验收标准
- `implementation-cell`
  - 负责模块路径、改动面、执行步骤、实现顺序
- `risk-validation-cell`
  - 负责风险、测试、回归、`.autonomy/`、审批门

### `Split-4 Mode`

仅在以下情况追加 `memory-pattern-cell`：

- 明显存在跨项目经验复用价值
- 当前问题包含陌生领域，需要读经验资产或第二大脑
- 这次产出大概率值得晋升为 playbook pattern 或长期记忆

## 模式选择评分

推荐把这些规则放进 repo-local `.ai-work/intake-policy.json`，让 `AGENTS.md`、启动脚本、命令和 Skill 都引用同一份 policy，而不是各自复制一套阈值和关键词。

对任务做 4 维评分，每维 0-2 分：

### 1. `complexity`

- `0`: 单模块、小改动、实现路径清晰
- `1`: 触达 2 个模块，或存在有限实现分叉
- `2`: 触达 3 个以上模块，或需要明显的时序/架构拆解

### 2. `coupling`

- `0`: 局部内部逻辑，几乎不影响共享接口
- `1`: 影响共享类型、状态、组件或内部 API
- `2`: 横跨 `web/api/ai-service`、repo 文档、运行边界等多个层面

### 3. `risk`

- `0`: 无真实外部副作用，回滚简单
- `1`: 用户可见或有中等回归风险，但不触达高风险边界
- `2`: 命中 `.autonomy/decision_policy` 中的高风险项，如发送、OAuth、billing、schema、权限、生产边界

### 4. `ambiguity`

- `0`: 目标和验收标准明确
- `1`: 有少量缺失信息，但能通过本地探索补齐
- `2`: 存在多个合理方案或明显 spec 缺口

### 评分结果

- `0-2` -> `Solo Mode`
- `3-5` -> `Split-3 Mode`
- `6-8` -> `Split-4 Mode`

### 强制规则

- 只要命中 `.autonomy/decision_policy` 的高风险项，至少进入 `Split-3 Mode`
- 高风险任务必须保留 `risk-validation-cell`
- 如果边界文件缺失或不清晰，应直接转 `blocked`，而不是继续推进

## Commander 与 Cells 的分工

### Commander

负责：

- intake 与模式选择
- 生成 dispatch brief
- 汇总 Cell 返回
- 形成唯一执行路径
- 执行正式写入与正式交付
- 决定哪些内容晋升到 repo / playbook / second-brain

### Cells

只负责：

- 分析
- 方案
- 草稿
- 审查

V1 约束：

- 不直接修改正式文件
- 如需落盘，只能写到临时区

## 中间产物协议

### `DispatchBrief`

最小字段：

- `goal`
- `role`
- `scope`
- `inputs`
- `deliverable`
- `constraints`
- `escalate_when`

### `WorkerReturn`

最小字段：

- `summary`
- `findings`
- `proposed_changes`
- `risks`
- `open_questions`
- `recommended_next_step`

### `MergeDecision`

最小字段：

- `chosen_path`
- `rejected_paths`
- `required_checks`
- `promotion_targets`

## `.ai-work` 临时区协议

每个项目统一使用：

```text
.ai-work/
  README.md
  templates/
    board.json
    dispatch-brief.md
    worker-return.md
    merge.md
    promotion.md
  runs/
    <run-id>/
      board.json
      briefs/
      returns/
      merge.md
      promotion.md
```

作用：

- 让并行分析有稳定落点
- 让汇总过程可追踪、可复盘
- 避免把草稿直接污染正式知识区

## 正式区分层

### 1. Repo 文档

记录项目真相与当前状态：

- README
- CONTEXT
- NOW
- `.autonomy/`
- 项目级 plans

### 2. `engineering-playbook`

只接收**跨项目可复用**的模式、命令、子 Agent 模板、判断规则。

### 3. `second-brain`

只接收晋升后的 session、决策、经验和长期记忆，不接收未筛选草稿。

## 高频命令面

V1 固定 6 个命令：

- `/work-intake`
  - 做 4 维评分并选择 `Solo / Split-3 / Split-4`
- `/role-split`
  - 生成 `DispatchBriefs + board.json`
- `/merge-and-decide`
  - 汇总 Cell 返回并形成唯一执行路径
- `/progress-update`
  - 同步 README / CONTEXT / NOW / active plan
- `/experience-capture`
  - 从复杂问题中提炼“原因-判断-修复-复用建议”
- `/doc-code-sync`
  - 检查 spec、代码、常量、枚举、文档漂移

## 什么时候不适合用

- 单文件、小改动、低风险任务
- 只是知识整理而非交付任务
- 当前执行环境无法承担额外协调成本
- 团队无法维护 `.autonomy/`、项目上下文和临时区协议

## 相关资产

- `engineering-playbook/skills/personal/adaptive-cell-workflow/`
- `engineering-playbook/templates/adaptive-cell-workflow/`
- `engineering-playbook/patterns/bounded-autonomy-repo-contract.md`
- `engineering-playbook/patterns/project-context-management.md`
