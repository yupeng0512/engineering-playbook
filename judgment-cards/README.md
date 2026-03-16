---
title: README
type: note
permalink: engineering-playbook/judgment-cards/readme
---

# Judgment Cards — 判断力卡片精华库

存放经过门控审核的跨领域通用判断力卡片。

## 准入标准

从 `judgment-index.md` 中筛选，满足以下条件方可入库：

1. **跨领域通用** — 不局限于单一技术栈或项目
2. **有据可查** — 来源明确，推导过程完整
3. **有边界标注** — 明确成立条件和失效条件
4. **经过验证** — 至少在一个实际场景中验证过

## 文件命名

`{领域}-{主题关键词}.md`

示例：
- `arch-simplicity-over-complexity.md`
- `risk-stop-loss-first.md`
- `meta-evidence-quality.md`

## 领域分类

| 缩写 | 领域 |
|------|------|
| `arch` | 技术架构 |
| `risk` | 风险决策 |
| `meta` | 元认知 |
| `eng` | 工程管理 |
| `product` | 产品判断 |

## 生成方式

由 `judgment-forge` Skill 锻造产出 → 写入 `judgment-index.md` → 精华同步至本目录。