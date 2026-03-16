---
title: structured-prompt-engineering
type: note
permalink: engineering-playbook/patterns/structured-prompt-engineering
---

# Pattern: 结构化 Prompt 工程

> 来源项目: InfoHunter | 推荐指数: 5/5 | 适用范围: 任何需要 LLM 输出结构化分析结果的场景

## 适用场景

- 需要 LLM 输出可解析的 JSON 分析报告
- 需要多种不同类型的分析（单条 vs 汇总 vs 评估）
- 需要分析结果有一致的质量标准和评分体系

## 核心实现

### 分层 Prompt 结构

每个 prompt 模板由 6 个标准模块组成：

```
1. 角色设定（Role）
   定义 AI 的专业身份和分析风格

2. 任务描述（Task）
   输入数据格式和分析目标

3. 分析方法论（Methodology）
   思维框架，引导 AI 按步骤分析（内部思考，不输出）

4. 输出规范（Output Schema）
   严格的 JSON 结构定义，含每个字段的格式说明

5. 评分标准（Scoring Rubric）
   每个评分维度的 1-10 打分标准

6. 质量约束（Constraints）
   禁止事项、特殊规则、输出格式要求
```

### Prompt 分类

不同分析目标用不同的 prompt，而非一个万能 prompt：

| Prompt | 输入 | 输出 | 用途 |
|--------|------|------|------|
| content_analysis | 单条内容 | 深度分析 JSON | 逐条分析 |
| trend_analysis | 多条内容 | 趋势汇总 JSON | 定期汇总 |
| recommend_evaluation | 博主资料 + 样本 | 订阅评估 JSON | 信息源评估 |

### 关键约束示例

```markdown
# 关键约束

1. **禁止复述**：summary 不得简单复述原文
2. **拒绝平庸**：importance ≤ 3 的内容直接说明，不强行拔高
3. **内容自适应**：Twitter 短文精炼分析，长文/视频深入分析
4. **避免幻觉**：只基于提供的内容分析，不编造事实
5. **纯 JSON 输出**：直接输出 JSON，不要 markdown 代码块
```

## 前后对比

| 维度 | 单一 prompt | 分层 prompt 体系 |
|------|------------|----------------|
| 输出一致性 | 每次格式可能不同 | JSON schema 固定 |
| 可维护性 | 改一处影响全部 | 各 prompt 独立迭代 |
| 分析质量 | 缺乏评分标准 | 有明确的打分 rubric |
| 调试效率 | 难以定位问题 | 可逐模块检查 |

## 使用注意事项

1. 输出规范中包含示例值有助于 LLM 理解格式（但注意 LLM 可能照抄示例）
2. 评分标准必须有锚点（9-10 = 什么水平，3-4 = 什么水平）
3. 约束部分用"禁止""必须"等强指令词
4. 搭配 LLM JSON 清洗 pattern 使用，作为双保险