---
title: config-level-self-bootstrap
type: pattern
permalink: engineering-playbook/patterns/config-level-self-bootstrap
date: 2026-03-13
tags:
- agent
- bootstrap
- evals
- governance
---

# Pattern: 配置级自举先于代码级自进化

## 核心判断

要让自治系统先稳定，再让它逐步变强，最好的起点不是“允许它直接改产品代码”，而是：

**只允许它进化 `.autonomy/` 下的配置、策略、提示和工具契约。**

这样做的收益是：

- 风险显著低于自动改业务代码
- 失败时可快速回滚
- 评估对象更清晰，方便做历史回放和失败样例回归
- 进化成果可跨项目复用

## 允许进化的白名单

V1 只允许改这些配置面：

- prompt 模板
- tool contract / tool docs
- decision policy
- default-action heuristics
- review checklist
- 风险阈值、提醒间隔、评估门槛

## 明确禁止的黑名单

在没有人工晋升前，禁止候选变更触达：

- 产品代码
- 数据库 schema 与 migration
- 基础设施配置
- 密钥、令牌、凭据
- 生产环境变量
- 计费、权限、生产写操作

## 固定闭环

```text
reflect run history
    -> draft candidate
    -> run evals
    -> generate checkpoint
    -> human promotion
```

任何候选改动都必须先进入 `BootstrapCandidate`，不能直接覆盖 active config。

## 候选实体最小要求

`BootstrapCandidate` 至少记录：

- `id`
- `repo`
- `status`
- `target_files`
- `change_summary`
- `evidence_refs`
- `evals`
- `promotion_required`
- `updated_at`

其中 `target_files` 必须限制在 `.autonomy/` 路径内。

## 三道评估门

每个 candidate 至少通过三类评估后，才能进入 `ready_for_review`：

1. **边界合规**
   只改白名单文件，且不越过审批策略。
2. **历史回放**
   用既有执行轨迹验证新策略没有明显回退。
3. **失败样例回归**
   对已知失败 case 重新评估，确认新配置没有复发旧问题。

任何一类失败，都应直接 `discarded` 或退回重写。

## 推荐晋升策略

- 默认不自动晋升
- 由人审阅 checkpoint 后再把 candidate promote 为 active config
- promote 时保留前一版快照，支持 `rolled_back`

## 适用边界

适合：

- 新自治系统的第一版
- Prompt / Tool / Review 规则还在快速变化的阶段
- 希望把经验沉淀为跨仓可复用资产

不适合：

- 追求“全自动改代码并自动合并”的平台级方案
- 没有 eval 基础设施，却想直接开放高影响改动

## 与代码级自举的关系

配置级自举不是终点，而是风险最低的第一层：

- 第 1 层：策略、阈值、模板、工具契约
- 第 2 层：代码补丁建议，但必须人审
- 第 3 层：极低风险代码自动晋升

这三个层次应该逐层开启，而不是一开始全部放开。
