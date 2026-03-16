---
name: bounded-autonomy
description: 为单个仓库安装并维护“边界内自治 + 配置级自举”契约。适用于需要初始化 `.autonomy/` 目录、设计审批门与默认动作、约束配置级自举边界、或为 repo-local runtime 提供状态机和 checkpoint 模板的任务。
permalink: engineering-playbook/skills/personal/bounded-autonomy/skill
---

# Bounded Autonomy

这个 Skill 用于把“边界内自主推进，并在需要人拍板时稳定停下”落到 **单仓库**。

## 什么时候用

- 需要在仓库里初始化 `.autonomy/` 契约
- 需要设计审批门、默认动作、checkpoint 模板
- 需要把自举限制在 prompt / policy / tool contract / heuristics 层
- 需要给 repo-local runtime 提供机器可校验的状态机和 schema

## 先读哪些材料

只按需读取：

- `engineering-playbook/patterns/bounded-autonomy-repo-contract.md`
  用于理解整体四层架构和 `.autonomy/` 最小契约
- `engineering-playbook/patterns/approval-gated-default-actions.md`
  用于审批触发器、8 段 checkpoint、默认动作矩阵
- `engineering-playbook/patterns/config-level-self-bootstrap.md`
  用于白名单自举和 eval 门

## 标准流程

1. 先读目标仓库的 `README` / `NOW` / `AGENTS` / 当前计划，确认产品边界和运行方式。
2. 初始化 `.autonomy/` 合同：

```bash
python engineering-playbook/skills/personal/bounded-autonomy/scripts/init_autonomy_contract.py <repo-path>
```

3. 立刻补齐 repo-specific 内容，至少完善：
   - `product_principles.md`
   - `decision_policy.md`
   - `definition_of_done.md`
4. 用校验脚本检查契约完整性和样例合法性：

```bash
python engineering-playbook/skills/personal/bounded-autonomy/scripts/validate_autonomy_contract.py <repo-path>
```

5. 只有在边界文件已经具体到项目语义后，才允许让 runtime 真正启用自治。

## 执行约束

- V1 自举只允许修改 `.autonomy/` 白名单文件
- 没有人类审批，不得跨越高风险边界
- `ready_for_review` 必须冻结任务推进
- 审批请求必须使用 8 段 checkpoint 模板

## 输出要求

当你应用这个 Skill 时，默认应交付：

- 一套完整 `.autonomy/` 目录
- 至少 1 个合法 `TaskRecord` 样例
- 至少 1 个合法 `ApprovalRecord` 样例
- 至少 1 个合法 `BootstrapCandidate` 样例
- 一次校验结果

## 常见误区

- 把审批态和任务态混成一个状态枚举
- 把默认动作写成“继续尽可能多做事”
- 允许 bootstrap candidate 直接覆盖 active config
- 把产品边界写得过空，导致 runtime 合规但语义跑偏
