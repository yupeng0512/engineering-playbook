---
name: research-driven-planner
description: 调研驱动的项目规划。在设计系统或做技术选型之前，先系统化搜索业界现有方案、分析开源项目、学习参考实现，再站在巨人肩膀上设计自己的方案。当用户表达'做一个XX系统'、'设计一个XX方案'、'调研一下XX怎么做'、'看看别人怎么做的'、'有没有现成的方案'、'技术选型'、'架构设计'等意图时触发。涉及3+模块的系统设计、Build
  vs Buy 决策、开源方案评估也应触发。即使用户只是说'帮我做个XX'，只要任务涉及架构决策，也应触发调研环节。
permalink: engineering-playbook/skills/personal/research-driven-planner/skill
---

# Research-Driven Planner — 站在巨人肩膀上做方案

核心信念：**任何值得做的系统，别人大概率已经做过类似的事情**。先搜索业界已有方案、学习参考实现、评估 Build vs Buy，再设计自己的架构。

## Skill 协作链

```
brainstorming (WHAT) → research-driven-planner (HOW) → writing-plans (EXECUTE)
```

需求模糊时先用 `brainstorming` 澄清。设计确认后需详细执行计划时转入 `writing-plans`。

**豁免**：单文件修改、Bug 修复、用户说"不用调研，直接做"、方案显而易见的简单任务。

## 七阶段工作流

```
问题定义 → 搜索扫描 → 深度剖析 → 模式提取 → Build/Buy 决策 → 方案设计 → 落地路径
```

每个阶段有明确的输入、动作和输出。阶段之间可根据发现回溯。

---

### Stage 1: 问题定义 (Problem Framing)

**目标**：用一句话锁定要解决的核心问题。

**动作**：
1. 提炼核心问题（一句话：谁，在什么场景下，需要什么能力，解决什么痛点）
2. 明确约束条件（预算、时间、团队规模、技术栈偏好）
3. 定义成功标准（上线后怎么判断做成了）
4. 划定边界（什么不做）

如果从 `brainstorming` 过来，直接复用已有的意图澄清结果，跳到 Stage 2。

**输出**：问题定义卡片（≤10 行）

```markdown
**核心问题**：{一句话}
**用户/场景**：{谁，什么场景}
**约束**：{预算/时间/团队/技术栈}
**成功标准**：{可衡量指标}
**不做**：{明确排除}
```

---

### Stage 2: 搜索空间映射 (Landscape Scan)

**目标**：广撒网，找到 5-10 个候选方案（开源 + 商业 + 社区实践）。

**动作**：按三层策略搜索（详见 `references/search-strategies.md`）。

**Layer 1 — GitHub / 开源社区**：搜索 stars>100、近 12 个月活跃的项目
**Layer 2 — Web 搜索**：商业产品、SaaS、技术博客、社区讨论
**Layer 3 — 深度资料**（按需）：白皮书、架构文章、会议演讲

从四个维度搜索：完整方案、模块方案、对标产品、社区实践。

**并行搜索**：尽量并行发起多个搜索请求，提高效率。使用 Task 子代理并行搜索不同角度。

**停止条件**：
- 找到 5+ 候选方案（至少 2 个开源 + 1 个商业）
- 覆盖完整方案和模块方案
- 能回答"这个领域大家通常怎么做"

**输出**：候选方案清单表格

```markdown
| # | 名称 | 类型 | Stars/用户 | 技术栈 | 许可证 | 匹配度 | 备注 |
|---|------|------|-----------|--------|--------|--------|------|
| 1 | ... | 开源 | 9.4k | Python | MIT | 高 | ... |
```

呈现清单后，与用户确认 Top 3 进入深度分析。

---

### Stage 3: 深度剖析 Top 3 (Deep Dive)

**目标**：深入理解 Top 3 方案的架构、决策和可复用模式。

**动作**：对每个方案（可并行）：
1. 阅读 README 和核心文档
2. 浏览代码结构和关键模块
3. 理解它如何解决核心问题
4. 识别关键架构决策和 trade-off
5. 评估优劣势和适用边界
6. 提取可复用的设计模式

使用 `references/analysis-templates.md` 中的「方案深度分析卡片」模板记录。

对考虑 Fork 或深度依赖的开源项目，额外做健康度评估（见 `references/analysis-templates.md`）。

**输出**：3 张方案分析卡片，呈现给用户讨论。

---

### Stage 4: 模式提取 (Pattern Extraction)

**目标**：从 Top 3 中提炼出「业界共识」「争议点」「反模式」。

**动作**：
1. 横向比较三个方案的架构决策
2. 标记共识模式（≥2 个方案都这么做 → 可能是最佳实践）
3. 标记争议点（不同方案选择不同 → 需要根据我们的场景决策）
4. 标记反模式（方案的 Issues/踩坑记录 → 我们要避免）
5. 按 Technology Radar 四环分类评估关键技术：Adopt / Trial / Assess / Hold

使用 `references/analysis-templates.md` 中的「模式提取汇总表」模板。

**输出**：模式汇总表（共识 + 争议 + 反模式 + 技术雷达）

---

### Stage 5: Build vs Buy 决策 (Decision Matrix)

**目标**：对系统中的每个子模块，明确是 Build / Buy / Fork+Extend。

**动作**：
1. 将系统拆分为独立的子模块
2. 对每个子模块，用加权评分矩阵打分（详见 `references/decision-frameworks.md`）
3. 六个维度：战略差异化(3x)、定制化需求(2x)、方案成熟度(2x)、团队能力(2x)、时间压力(1x)、维护成本(1x)
4. 根据总分落入决策区间：Buy / Buy+Extend / Fork+Extend / Build on OSS / Build from Scratch

**决策阈值**：
- 1.0-2.0 → Buy（直接用商业产品）
- 2.1-2.8 → Buy + Extend（买基础 + 定制插件）
- 2.9-3.5 → Fork + Extend（Fork 开源 + 二次开发）
- 3.6-4.2 → Build on OSS（基于开源组件自建）
- 4.3-5.0 → Build from Scratch（完全自研）

**注意**：自建的真实成本通常是初始估算的 3-5 倍（含维护、迭代、机会成本）。超过 30% 定制化需求的购买方案，成本通常超过自建。

**输出**：子模块决策表

```markdown
| 子模块 | 总分 | 决策 | 具体方案 | 理由 |
|--------|------|------|---------|------|
| 模块A | 3.2 | Fork+Extend | Fork social-auto-upload | 基础功能匹配，需扩展多账号并发 |
| 模块B | 1.5 | Buy | 用可灵 API | 自建 GPU 成本高，先用商业 API 验证 |
```

---

### Stage 6: 方案设计 (Solution Design)

**目标**：站在调研结果上，设计整体架构。

**动作**：
1. 明确每个模块的来源（复用 / Fork / 自建）
2. 设计模块间的连接方式（API、消息队列、数据库）
3. 画出整体架构图（用 Mermaid）
4. 为关键决策写 ADR（详见 `references/decision-frameworks.md`）

**架构图要求**：
- 标注每个组件的来源（开源项目名 / 商业产品名 / 自建）
- 标注关键接口和数据流
- 标注部署方式（Docker / Cloud / 本地）

**ADR 速记格式**：
```
在 {上下文} 场景下，面对 {问题}，
我们选择了 {方案}，以实现 {目标}，
接受 {代价}，因为 {核心理由}。
```

**输出**：架构设计文档 + ADR 列表

---

### Stage 7: 落地路径 (Landing Path)

**目标**：设计渐进式的实施路径。

**动作**：
1. 按「先验证后规模」原则拆分 Phase
2. Phase 1 必须是 MVP（最小可行产品），聚焦验证核心假设
3. 每个 Phase 定义：目标、交付物、验证标准、预计时间
4. 评估关键风险并设计应对策略
5. 做 ROI 速算（可选，对成本敏感的项目）

使用 `references/decision-frameworks.md` 中的落地路径模板。

**原则**：
- Phase 1 用最低成本验证核心假设（先商业 API，再自建）
- 每个 Phase 有明确的 Go/No-Go 判断标准
- 风险最高的假设在最早的 Phase 验证

**输出**：渐进式落地路径 + 风险矩阵

如果用户需要更详细的执行计划（精确到文件和命令），转入 `writing-plans` Skill。

---

## 输出归档

### 调研产出存放

按项目需求选择：
- 项目级：`{project}/.context/research/YYYY-MM-DD-{topic}.md`
- 或跟随 Plan：`{project}/docs/plans/` 目录下

### 经验沉淀

调研完成后，按 AGENTS.md 的 Value Gate 判断是否值得沉淀：
- 跨项目可复用的调研结论 → `second-brain/3-value/` 或 `engineering-playbook/`
- 项目特定的上下文 → `second-brain/2-biz/projects/`
- 日常记录 → `second-brain/1-daily/`

用 `basic-memory` MCP 或 `memlog.sh` 写入。

---

## 质量检查

完成全部 7 个阶段后，自检：

- [ ] 搜索覆盖了开源 + 商业 + 社区实践三个维度
- [ ] 深度分析了 ≥3 个参考方案
- [ ] 提取了共识模式和反模式
- [ ] 每个子模块有明确的 Build/Buy 决策和理由
- [ ] 架构设计标注了每个组件的来源
- [ ] 关键决策有 ADR 记录
- [ ] 落地路径 Phase 1 是 MVP，聚焦验证而非大而全
- [ ] 用户确认了方案设计

---

## 核心原则

1. **搜索先于设计**：永远不要跳过搜索直接画架构。别人踩过的坑就是你的捷径。
2. **学架构不学代码**：从参考项目中学设计决策和模式，而非复制代码。
3. **ROI 驱动决策**：每个 Build vs Buy 决策都要算账。自建的隐性成本是显性成本的 3-5 倍。
4. **渐进验证**：先用最低成本验证核心假设，再逐步投入。
5. **记录决策**：重要的技术选择写 ADR，未来的自己会感谢现在的自己。

---

## 参考资料来源

- Build vs Buy: ARDURA 10-criteria matrix, Baytech 6-factor model
- ADR: MADR (Markdown Architectural Decision Records), Nygard 原始格式
- 开源评估: OpenSSF Best Practices, OSPS Baseline 2026
- 技术雷达: ThoughtWorks Technology Radar 四环模型
- 竞品分析: Product Manager's Competitive Analysis Framework