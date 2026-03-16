---
title: ranked-candidate-enrichment
type: note
permalink: engineering-playbook/patterns/ranked-candidate-enrichment
---

# 排序候选集的昂贵增强：先稳定排序，再做 Capped Enrichment

## 场景

推荐系统、行动队列、告警面板里，通常会先生成一批候选项，再对其中一部分做较昂贵的增强，例如：

- 额外查知识库 / 历史最佳实践
- 查语义检索结果
- 做二次打分或补全模板

为了控制成本，工程上往往只对前 N 个候选做增强。

## 问题

如果候选集在增强前还没有经过稳定排序，或者中间经过了 `map` / `set` 去重再直接截断，那么“前 N 个”其实是随机的。

这会导致：

- 高优先级项没有拿到增强信息
- 低优先级项反而被增强
- 结果看起来“偶发不稳定”，很难靠肉眼复现

## TradeRadar 实例

Phase 12 的 `NextActionService` 在做去重后，先对动作队列做 knowledge enrichment，再排序输出。

问题在于：

- 去重使用 `map`
- Go 的 `map` 迭代顺序不稳定
- capped enrichment 只处理前几个 action

结果是：有些真正应该出现在最终队列顶部的动作，可能根本没拿到 template/channel enrichment。

## 解法

### 原则

**先用便宜的基础分数稳定排序，再对排序靠前的一小段候选做昂贵增强，最后再重排一次。**

### 推荐流程

1. 生成候选集
2. 去重
3. 按基础分数排序
4. 对 top K 做昂贵增强
5. 按增强后的最终分数再排序
6. 截断返回

## Checklist

- [ ] capped enrichment 之前，候选集是否已经稳定排序？
- [ ] 去重是否使用了 `map` / `set`，从而破坏了顺序？
- [ ] 增强后的分数是否需要二次排序？
- [ ] `K` 是否比最终返回的 `limit` 略大，给增强后的重排留出余量？

## 来源

TradeRadar Phase 12 Review — Next Best Action Copilot 中，knowledge enrichment 原本发生在去重后的未排序动作列表上，存在“增强到错误候选”的隐性稳定性问题。
