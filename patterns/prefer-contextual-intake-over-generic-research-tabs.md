---
title: prefer-contextual-intake-over-generic-research-tabs
type: note
permalink: engineering-playbook/patterns/prefer-contextual-intake-over-generic-research-tabs
---

# Prefer Contextual Intake Over Generic Research Tabs

## 场景

很多 AI 产品在引入文件上传、资料解析、Agent 提议后，会很自然地长出一个叫：

- 导入与研究
- Research
- Intake Lab
- Document Workspace

这样的 tab。

技术上它常常能工作，但产品上很容易把用户带偏。

## 问题

用户真正想做的通常不是“去研究”。

用户想做的是：

- 给当前产品补资料
- 给当前线程补买家附件
- 让系统读一份文档并继续推进

如果默认 IA 先暴露一个抽象的 research tab，用户就要额外理解：

- 我为什么要来这里？
- 这里和当前产品/线程是什么关系？
- 结果会落到哪一个对象上？

这会抬高心智成本，也容易让 scope 漂移。

## 推荐做法

### 1. 默认入口用上下文化动作，不用抽象能力名

把主路径动作写成：

- 上传这条产品线资料
- 上传买家附件/要求
- 给这个对象补资料

而不是让用户先决定要不要去一个叫“导入与研究”的地方。

### 2. intake surface 必须带明确 scope

canonical intake UI 打开时，至少要绑定：

- `product`
- `thread`
- `opportunity`
- `reference_only`

这样 Agent、parser、proposal、writeback 都知道自己是在为哪个对象服务。

### 3. research/workspace 退成 expert route

保留统一 workspace 是合理的，但它更适合承担：

- backlog
- evidence
- reports
- checkpoint / session recovery

而不是默认主任务入口。

### 4. 所有导入结果都走 review-before-write

资料解析不应直接写库。

更稳的顺序是：

1. 读资料
2. 产出结构化候选
3. 展示字段级 proposal
4. 用户确认
5. 再写入对象级上下文

### 5. provenance 要跟着对象走

导入结果除了字段值，还要带来源证据：

- 来源文件
- block / section
- excerpt
- page / sheet

这样用户和后续 Agent 都知道这条结论从哪来。

## 为什么有效

- 用户不需要理解系统内部能力层
- 所有 intake 都围绕当前对象，scope 更稳定
- parser / Agent / writeback 会自然收口成一条闭环
- expert workspace 仍然存在，但不会污染默认主路径

## 适用场景

- 产品资料补录
- 买家附件解析
- 机会条款/包装/付款要求补充
- 任意“上传资料 -> 提议结构化上下文 -> review -> 写库”的系统

## 反模式

- 把“导入与研究”当成默认用户任务名
- 主路径必须 route jump 到 research workspace 才能开始 intake
- 同一份资料没有对象 scope，导致 proposal 不知道该写到产品还是线程
- 上传后直接写库，不给 review 与 provenance

## 来源

TradeRadar `Phase 28AR`：把“导入与研究”从一个用户需要理解的 tab，收口成围绕当前产品/线程/对象的 contextual intake 能力。
