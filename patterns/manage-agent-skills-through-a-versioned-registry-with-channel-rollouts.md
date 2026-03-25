---
title: manage-agent-skills-through-a-versioned-registry-with-channel-rollouts
type: note
permalink: engineering-playbook/patterns/manage-agent-skills-through-a-versioned-registry-with-channel-rollouts
---

# Manage Agent Skills Through a Versioned Registry With Channel Rollouts

## 场景

当团队开始依赖越来越多的本地 agent skills 时，最常见的失败模式不是“没有 skill”，而是：

- 大家各自从 GitHub 散装安装
- 上游改了 nobody knows
- 新 skill 直接污染默认环境
- 出问题时很难知道是谁把哪个版本装进去了

这时真正需要的通常不是另一个“万能 skill 管理器”，而是一套受控分发机制。

## 推荐做法

### 1. 建独立 registry 仓库

不要把 skill 治理直接混进业务仓库。

更稳的结构是：

- `skills-manifests/`
- `vendor/skills/`
- `channels/stable.yaml`
- `channels/canary.yaml`
- `channels/experimental.yaml`
- `schemas/`
- `scripts/`
- `.github/workflows/`
- `renovate.json`

### 2. vendor 实际快照，而不是只存链接

只存 GitHub URL 的问题是：

- PR diff 不可审
- 上游临时挂了就没法同步
- 回滚时也难确认到底装过什么

把 skill 快照 vendored 进 registry 后：

- diff 可审查
- 安装更稳定
- 回滚和 bisect 更直接

### 3. 用渠道而不是“一把梭哈更新”

至少区分：

- `stable`
- `canary`
- `experimental`

默认环境只消费 `stable`。  
新 skill、新规则、新上游 ref 先放 `canary`，验证稳定后再提升。

### 4. 自动订阅更新，但不要自动直达生产

最稳的做法不是自动安装，而是：

- 用 Renovate 监控上游 repo/ref
- 自动开 PR
- 跑 schema/frontmatter/smoke install CI
- review 后再合并

这样既有自动订阅更新，也保住了审计和回滚边界。

### 5. 本机同步脚本默认采用 additive sync

同步时只安装/更新 registry 管理的 skills，不删除本机其它未托管 skill。

这样可以：

- 降低迁移成本
- 先试运行 registry，不强制一次性接管所有历史本地技能

## 为什么有效

- 把“谁都能随手装点什么”变成“有记录、有 diff、有渠道的受控变更”
- 让技能升级有 PR 和 CI，而不是靠口头通知
- 不依赖某个特定 agent 平台的 marketplace 才能治理
- 可以先小范围试运行，再逐步收紧默认环境

## 适用场景

- Codex / Claude Code / 本地 agent 混合环境
- 团队已经开始共享本地 skill 包
- 希望引入 canary 规则包或 workflow pack
- 希望自动追上游更新，但不想自动污染主环境

## 反模式

- 每个人直接从 GitHub raw 路径装 skill
- 上游一更新就直接同步到默认环境
- 用业务仓库顺手存一堆本地 skill 快照
- 没有渠道分层，就让实验性规则和稳定规则混装

## 来源

TradeRadar `Phase 28AU`：在没有成熟 Codex-native skill manager 的前提下，用独立 `agent-skills-registry` + Renovate + CI + stable/canary/experimental 渠道，为 Codex 工作环境补齐了统一治理、自动订阅更新和安全 rollout。
