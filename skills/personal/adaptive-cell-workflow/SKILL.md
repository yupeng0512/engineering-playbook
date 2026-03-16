---
name: adaptive-cell-workflow
description: 为复杂研发交付任务启用自适应角色化协作。适用于需要根据复杂度/耦合度/风险/歧义在 Solo、Split-3、Split-4 之间切换，并产出 subagent briefs、merge decision、progress update 与 experience capture 的任务。
permalink: engineering-playbook/skills/personal/adaptive-cell-workflow/skill
---

# Adaptive Cell Workflow

这个 Skill 用于把“复杂任务吞吐优先”的角色化协作方式落到具体仓库。

## 什么时候用

- 任务跨多个模块、层级或系统
- 既要推进实现，又要同步文档、校验边界、沉淀经验
- 串行探索成本已经明显高于一次协调成本
- 需要决定是否启用 subagent / cell，而不是默认总是拆角色

## 先读哪些材料

只按需读取：

- `engineering-playbook/patterns/adaptive-cell-workflow.md`
  - 理解目标函数、模式选择、角色分工、合并协议
- `engineering-playbook/patterns/project-context-management.md`
  - 识别 repo truth 层应该更新哪些项目文档
- `engineering-playbook/patterns/bounded-autonomy-repo-contract.md`
  - 如果仓库已有 `.autonomy/`，用来判断高风险边界和审批门
- 目标仓库的 `.ai-work/intake-policy.json`（如果存在）
  - 这是 repo-local intake 规则的单一来源

## 标准流程

1. 先读取目标仓库的 `README` / `NOW` / `AGENTS` / 活跃计划 / `.autonomy/`
2. 如果仓库还没安装工作流模板，先初始化：

```bash
python engineering-playbook/skills/personal/adaptive-cell-workflow/scripts/init_adaptive_cell_workflow.py <repo-path>
```

3. 如果仓库有 `.ai-work/intake-policy.json`，先读取它，后续 mode 选择、high-risk floor、memory-cell activation 都以它为准。
4. 如果仓库还提供 `scripts/aiwork/start_run.py`，优先用它触发 intake 与 run 初始化：

```bash
python3 scripts/aiwork/start_run.py --goal "<task>"
```

5. 否则再用 `/work-intake` 按 policy 手动完成 4 维评分与 mode 选择。
6. 如果进入 split 模式，用 `/role-split` 生成：
   - `.ai-work/runs/<run-id>/board.json`
   - `briefs/`
   - 初始 merge/promotion 骨架
7. 让 cells 只做分析和草拟，不直接修改正式区。
8. 由 Commander 用 `/merge-and-decide` 形成唯一执行路径，再执行正式写入。
9. 阶段结束后执行：
   - `/progress-update`
   - `/doc-code-sync`
   - 需要时 `/experience-capture`

## 执行约束

- 子 Agent 只做分析、方案、草稿、审查
- 正式写入只能由 Commander 完成
- 若仓库存在 `.autonomy/`，`risk-validation-cell` 必须读取并遵守其边界
- 经验沉淀必须经过晋升，不得把临时草稿直接写入正式知识区

## 输出要求

应用这个 Skill 时，默认应交付：

- 一次明确的 mode 选择理由
- 一份 `DispatchBrief` 或一组 briefs
- 一份 `MergeDecision`
- 至少一次 repo truth 同步
- 需要时一条经验沉淀或明确的不沉淀理由
- 如果仓库是 policy-first 版本，应能指出 `.ai-work/intake-policy.json` 如何影响了这次 mode 选择

## 常见误区

- 把“拆角色”当作默认动作，而不是收益大于成本时的手段
- 让子 Agent 直接写正式文件，破坏汇总与裁决职责
- 把所有 AI 草稿直接沉淀进知识库
- 只拆实现，不拆风险与边界
- 把 `.autonomy/` 看成运行时专用，忽略它对开发协作的约束价值
- 在 `AGENTS.md`、命令、脚本、Skill 里各自复制一套 intake 规则，导致阈值和边界漂移
