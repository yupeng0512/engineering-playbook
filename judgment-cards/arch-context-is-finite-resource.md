---
title: arch-context-is-finite-resource
type: note
permalink: engineering-playbook/judgment-cards/arch-context-is-finite-resource
---

## 判断力卡片：上下文是有限资源，精准胜于丰富

> 来源: Anthropic Context Engineering + Manus 上下文工程六大原则
> 锻造日期: 2026-02-25
> 领域: 技术架构

### 核心判断
在设计 AI Agent 系统时，上下文不是"越多越好"而是"越精越好"；应将 KV-cache 命中率作为核心性能指标，通过 append-only 结构保持前缀稳定，并严格控制每个 token 的信噪比——因为 Context rot（注意力稀释）会随上下文长度 n 的增加产生 n^2 级别的关系膨胀，导致模型聚焦能力指数衰减。

### 关键问题
**这个 token 对当前决策的信息增益是多少？如果为零，它就不应该在上下文中。**

### 适用边界
- **成立条件**: Agent 执行多步工具调用链（输入/输出比 > 10:1）；上下文长度 > 32K tokens；需要长时运行且保持一致性
- **失效条件**: 单轮对话场景（上下文不膨胀）；模型窗口远大于任务所需（如 2M 窗口处理 5K 任务）；未来模型架构突破 n^2 注意力瓶颈
- **不确定区域**: Manus 的"4 次重建"是否因方法论不成熟而非上下文本身的问题；不同模型的 context rot 拐点差异

### 心智模型
- **系统思维（瓶颈理论）**: KV-cache 命中率 = Agent 经济学的核心杠杆（Manus：10 倍成本差异）
- **概率思维**: Context rot 的 n^2 关系模型提供了精确的衰减预期，但基础率因模型而异
- **激励结构**: Anthropic 和 Manus 都从自身产品实践中得出结论，利益与用户一致度高

### 反面论证
反对观点：更大的上下文窗口（如 Gemini 2M）可能让精简策略变得不必要；过度压缩上下文可能丢失关键信息导致决策质量下降。仍坚持本判断的原因：信噪比优化在任何窗口大小下都有价值（大窗口只是提高了上限，不消除 rot）；Manus 的 append-only 策略和 Anthropic 的 attention budget 理论在生产环境中已被验证。

### 新增实证：SkillsBench 量化验证（2026-02-27）

SkillsBench（BenchFlow + Stanford/CMU/UC Berkeley 等联合研究，7,308 次执行轨迹）从 Agent Skill 注入维度为本卡片提供了大规模量化证据：

| 证据 | 数据 | 支撑点 |
|------|------|--------|
| 全面型 Skill 有害 | Comprehensive 型文档导致通过率 -2.9pp | 过度阐释消耗上下文预算，直接验证"精准胜于丰富" |
| 精准知识缩短搜索空间 | Gemini 3 Pro 接入 Skill 后输入 Token 反降 6% | 结构化程序性知识阻断无效探索路径 |
| 模块数量阈值 | 2-3 模块 +18.6pp → ≥4 模块仅 +5.9pp | 上下文噪音阈值的量化标定 |
| 小模型代偿 | Flash 消耗 1.08M tokens（Pro 的 2.3 倍）弥补推理不足 | 上下文预算与推理深度的直接竞争关系 |

### 验证状态
部分验证于 InfoHunter（AG-UI 上下文管理）、TruthSocial Monitor（多步工具链）；SkillsBench 论文提供了 7,308 次轨迹的大规模实证支持（2026-02-27 补充）