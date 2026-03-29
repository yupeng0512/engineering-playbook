# 搜索策略参考

> 本文档定义 Landscape Scan 阶段的搜索方法、关键词模板和信源层级。

---

## 三层搜索策略

按成本递增顺序执行，前一层收获足够时可提前停止。

### Layer 1: GitHub / 开源社区（5-15 分钟）

**目标**：找到可直接使用或 Fork 的开源项目。

**搜索关键词模板**：
```
"{problem_domain}" stars:>100 language:{lang} pushed:>{one_year_ago}
"{problem_domain}" awesome list
"{problem_domain}" open source self-hosted
"{problem_domain}" framework library
```

**中文项目额外搜索**：
```
"{问题领域}" 开源
"{问题领域}" GitHub
"{问题领域}" 自建 部署
```

**筛选条件**（硬门槛）：
- Stars > 100（或 Fork > 30）
- 最近 12 个月内有 commit
- 有 README 且说明核心功能
- 许可证明确（Apache 2.0 / MIT / BSD 优先，GPL 标注风险）

**补充信源**：
- Gitee 热门项目（国内生态）
- Hacker News "Show HN" 搜索
- Product Hunt 搜索
- AlternativeTo.net（找替代品）

### Layer 2: Web 搜索（10-20 分钟）

**目标**：找到商业产品、SaaS 方案、社区实践文章。

**搜索关键词模板**：
```
"{problem_domain}" best tools 2026
"{problem_domain}" SaaS vs self-hosted comparison
"{problem_domain}" architecture blog
"how to build {problem_domain}" engineering blog
"{problem_domain}" case study {company_type}
```

**中文搜索**：
```
"{问题领域}" 方案对比
"{问题领域}" 技术选型
"{问题领域}" 架构设计 实战
"{问题领域}" 最佳实践 2026
```

**优先信源**：
- 技术博客：InfoQ, ThoughtWorks Insights, Hacker News, dev.to
- 中文社区：掘金, 知乎专栏, CSDN（需甄别质量）
- 官方文档：产品官方 docs / blog
- 视频：YouTube 技术频道（架构解析类）

### Layer 3: 深度调研（15-30 分钟，按需）

**目标**：获取白皮书、架构设计文档、行业报告等一手深度资料。

**搜索关键词模板**：
```
"{problem_domain}" white paper filetype:pdf
"{problem_domain}" architecture design document
"{problem_domain}" RFC specification
"{expert_name}" "{problem_domain}" talk transcript
"{problem_domain}" survey systematic review
```

**信源**：
- 学术搜索：Google Scholar, arXiv, IEEE
- 行业报告：Gartner, Forrester（摘要即可）
- 会议演讲：InfoQ presentations, QCon, KubeCon
- RFC / PEP / ADR：标准化提案文档

---

## 搜索维度矩阵

对每个问题领域，从四个维度搜索：

| 维度 | 要找什么 | 典型产出 |
|------|---------|---------|
| 完整方案 | 能直接部署使用的项目 | GitHub 项目 + SaaS 产品 |
| 模块方案 | 能复用其中某个模块的项目 | 库 / SDK / API |
| 对标产品 | 商业竞品，学习其设计 | 产品官网 + 定价 + 功能矩阵 |
| 社区实践 | 别人怎么解决类似问题 | 博客 + 论坛 + 视频 |

---

## 搜索结果记录模板

每个候选方案用以下格式记录：

```markdown
### [方案名称](链接)

| 维度 | 信息 |
|------|------|
| 类型 | 开源 / 商业 SaaS / 商业 API / 框架 |
| Stars/用户 | N / 估算 |
| 技术栈 | 语言, 框架, 依赖 |
| 许可证 | Apache 2.0 / MIT / GPL / 商业 |
| 最后更新 | YYYY-MM |
| 核心功能 | 1-2 句话 |
| 与我的需求匹配度 | 高 / 中 / 低 |
| 备注 | 值得深挖的点 / 风险提示 |
```

---

## 停止搜索的条件

满足以下全部条件时可停止：
1. 找到 5+ 个候选方案（至少 2 个开源 + 1 个商业）
2. 覆盖了完整方案和模块方案两个维度
3. 对核心问题的业界主流做法有了基本认知
4. 能回答"这个领域大家通常怎么做"

如果搜索了 30 分钟仍不足 3 个候选 → 说明该领域可能较新或小众，记录这个发现，调整预期。
