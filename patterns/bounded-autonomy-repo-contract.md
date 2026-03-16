---
title: bounded-autonomy-repo-contract
type: pattern
permalink: engineering-playbook/patterns/bounded-autonomy-repo-contract
date: 2026-03-13
tags:
- agent
- autonomy
- workflow
- approval
- state-machine
---

# Pattern: 单仓库的边界内自治契约

## 场景

当一个仓库希望让 AI 在夜间或长时间任务中“自己推进”，真正需要的不是无限循环，而是一份可执行的仓库契约：

- 哪些事情 AI 可以自己做
- 哪些事情必须停下来等人拍板
- 长任务如何异步执行并回传结果
- 自举能力允许改到哪一层

这个 Pattern 约束的是 **单仓库 runtime**，不是多项目平台。

## 四层结构

```text
engineering-playbook
    -> 提供模式、模板、默认策略

bounded-autonomy Skill
    -> 把模板装进目标仓库，指导执行与复盘

repo-local runtime
    -> 维护任务状态、审批状态、默认动作、证据包

approval adapter
    -> 把 checkpoint 投递到 Feishu / Slack / PR / 本地 UI
```

## `.autonomy/` 最小契约

每个接入仓库至少提供以下文件：

| 文件 | 作用 |
|------|------|
| `product_principles.md` | 产品边界，不允许 AI 擅自改的方向 |
| `decision_policy.md` | 哪些事可自动决策，哪些必须审批 |
| `definition_of_done.md` | 完成标准与证据要求 |
| `default_action_policy.md` | 阻塞、超时、评审态的默认动作 |
| `bootstrap_policy.md` | 配置级自举边界、评估门、回滚门 |
| `checkpoint_template.md` | 人工审批固定模板 |
| `model_policy.json` | planner / reviewer / executor 的模型映射槽位 |
| `state_machine.json` | 三套状态机与定时规则 |
| `schemas/*.schema.json` | 机器可校验的记录契约 |
| `examples/*` | runtime 和审查时可直接参考的样例 |

## 三个状态实体

不要把所有语义塞进一个枚举，拆成三个实体：

### 1. `TaskRecord`

任务执行态，只表达任务推进本身：

- `queued`
- `planning`
- `researching`
- `executing`
- `blocked_on_decision`
- `blocked_on_external`
- `deferred`
- `ready_for_review`
- `completed`
- `failed`

最小字段：

- `id`
- `goal`
- `repo`
- `state`
- `approval_state`
- `risk_level`
- `priority`
- `depends_on`
- `blocked_reason`
- `next_check_at`
- `default_action_policy`
- `evidence_refs`
- `allowed_paths`
- `updated_at`

### 2. `ApprovalRecord`

审批态只表达“人是否已经做出决定”：

- `not_required`
- `requested`
- `approved`
- `rejected`
- `expired`

### 3. `BootstrapCandidate`

自举候选态只表达“配置级变更是否完成评估与晋升”：

- `drafted`
- `evaluating`
- `ready_for_review`
- `accepted`
- `discarded`
- `rolled_back`

## 运行时硬规则

- 高风险动作不能仅靠 `TaskRecord.state` 跨越，必须同时满足 `ApprovalRecord=approved`
- `ready_for_review` 只允许产出证据包和 review 包，不再继续实现
- 长任务必须支持异步执行与回调，OpenAI 路线优先使用 Responses API `background` + `webhooks`
- 高风险工具动作必须保留 human-in-the-loop 门，尤其是生产环境、支付、敏感数据、第三方后台

## 推荐目录形态

```text
.autonomy/
  README.md
  product_principles.md
  decision_policy.md
  definition_of_done.md
  default_action_policy.md
  bootstrap_policy.md
  checkpoint_template.md
  model_policy.json
  state_machine.json
  schemas/
  examples/
```

## 什么时候适合用

- 单仓库希望获得“边界内自治”能力
- 希望未来多个仓库复用同一套自治规范
- 需要把“审批门”“默认动作”“配置级自举”做成资产，而不是散落在 prompt 里

## 什么时候不适合用

- 只是一次性脚本任务，没有长运行或审批需求
- 需要的是多仓队列平台，而不是单仓自治 runtime
- 团队无法维护 `.autonomy/` 契约，导致边界文件长期失真

## 来源

- OpenAI Background mode: <https://platform.openai.com/docs/guides/background>
- OpenAI Webhooks: <https://platform.openai.com/docs/webhooks>
- OpenAI Computer use / human-in-the-loop: <https://platform.openai.com/docs/guides/tools-computer-use>
- OpenAI Models: <https://platform.openai.com/docs/models>
