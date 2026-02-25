# Methodology Database - 领域专家方法论数据库

> 收录 15+ 领域、80+ 专家的核心方法论和框架

---

## 📚 使用说明

本数据库收录了各领域大师级专家的经典方法论，用于 skill-from-masters 创建高质量 Skill。

**更新策略**：
- 每季度审查并补充新方法论
- 优先收录：经过时间检验的经典框架
- 验证标准：有书籍/论文/案例支持

---

## 1. 商业写作 (Business Writing)

### Barbara Minto - 金字塔原理 (Pyramid Principle)

**核心理念**：先结论后支撑，MECE（相互独立、完全穷尽）

**适用场景**：商业提案、技术文档、决策报告

**核心框架**：
```
金字塔结构：
1. 结论先行（Top-down）
2. 归类分组（Grouping）
3. 逻辑排序（Logical Order）
   - 演绎推理：大前提 → 小前提 → 结论
   - 归纳推理：现象1、现象2 → 结论
```

**参考资源**：
- 书籍：《金字塔原理》
- 应用：麦肯锡咨询报告标准

---

### Amazon - 6-Pager / Working Backwards

**核心理念**：叙事文档代替 PPT，从客户需求倒推方案

**适用场景**：产品规划、项目提案、战略决策

**核心框架**：
```
6-Pager 结构：
1. 上下文和问题陈述
2. 客户价值（Working Backwards）
3. 解决方案
4. 成功指标
5. 风险和缓解措施
6. 资源需求

强制叙事：
- 禁止 PPT
- 会前 20 分钟阅读
- 避免「Powerpoint 思维」
```

**参考资源**：
- 书籍：《Working Backwards》
- 模板：Amazon PR/FAQ 格式

---

## 2. 产品管理 (Product Management)

### Marty Cagan - 问题空间 vs 方案空间

**核心理念**：先定义问题，再探索方案；赋能团队而非指令

**适用场景**：产品发现、需求分析、团队协作

**核心框架**：
```
产品发现（Discovery）：
1. 问题空间（Problem Space）
   - 用户痛点
   - 业务目标
   - 技术可行性
   
2. 方案空间（Solution Space）
   - 多个候选方案
   - 快速原型验证
   - 迭代优化

产品三要素（Product Trinity）：
- 价值（Value）：用户需要吗？
- 可用性（Usability）：用户会用吗？
- 可行性（Feasibility）：能实现吗？
```

**参考资源**：
- 书籍：《Inspired》《Empowered》
- 博客：svpg.com

---

### Teresa Torres - Opportunity Solution Tree

**核心理念**：结构化探索机会，连接目标和解决方案

**适用场景**：产品规划、功能优先级、OKR 落地

**核心框架**：
```
机会解决方案树（OST）：
目标（Outcome）
  ├─ 机会1（Opportunity）
  │   ├─ 解决方案1a
  │   └─ 解决方案1b
  ├─ 机会2
  │   └─ 解决方案2a
  └─ 机会3

持续发现习惯（Continuous Discovery Habits）：
- 每周用户访谈
- 快速假设验证
- 团队共同决策
```

**参考资源**：
- 书籍：《Continuous Discovery Habits》
- 工具：Opportunity Solution Tree 模板

---

## 3. 用户研究 (User Research)

### Rob Fitzpatrick - The Mom Test

**核心理念**：问行为不问意见，挖掘真实需求

**适用场景**：用户访谈、需求验证、早期产品验证

**核心框架**：
```
三大原则：
1. 谈过去，不谈未来
   - ❌ "你会用这个功能吗？"
   - ✅ "你上次遇到这个问题是什么时候？"

2. 谈细节，不谈泛泛
   - ❌ "你觉得这个想法怎么样？"
   - ✅ "你当时具体是怎么解决的？"

3. 少说多听
   - ❌ 推销你的产品
   - ✅ 让用户讲故事

Mom Test 检验：
「能不能问你妈妈这个问题，并得到真实答案？」
```

**参考资源**：
- 书籍：《The Mom Test》
- 网站：momtestbook.com

---

### Jobs-to-be-Done (JTBD)

**核心理念**：用户不买产品，而是「雇佣」产品完成任务

**适用场景**：市场细分、竞品分析、创新机会

**核心框架**：
```
JTBD 语句格式：
"当 [情境] 时，我想要 [动机]，以便 [预期结果]"

示例：
"当我早上通勤时（情境），我想要快速充电（动机），
以便手机能撑到下班（预期结果）"

Four Forces（四力模型）：
推力：现有方案的不满
拉力：新方案的吸引力
焦虑：对新方案的担心
习惯：对现有方案的惯性
```

**参考资源**：
- 书籍：《Competing Against Luck》（Clayton Christensen）
- 工具：JTBD 访谈模板

---

## 4. 软件架构 (Software Architecture)

### Martin Fowler - 演进式架构

**核心理念**：架构是演进的，不是预先设计的；技术债务要主动管理

**适用场景**：架构设计、重构决策、技术债务管理

**核心框架**：
```
架构定义：
"架构 = 专家开发者对系统设计的共识"

演进原则：
1. 延迟决策（Last Responsible Moment）
2. 可逆性优先
3. 架构适应度函数（Fitness Function）

技术债务象限（Technical Debt Quadrant）：
           谨慎的             鲁莽的
故意的  | 考虑权衡后的决策  | 没时间就这样吧
无意的  | 现在才知道更好的  | 什么是设计？
```

**参考资源**：
- 网站：martinfowler.com/architecture
- 书籍：《重构》《企业应用架构模式》

---

### ATAM (Architecture Tradeoff Analysis Method)

**核心理念**：系统化评估架构质量，识别风险和权衡

**适用场景**：架构评审、技术选型、风险评估

**核心框架**：
```
9 步评审流程：
1. 介绍 ATAM 方法
2. 展示业务驱动因素
3. 展示架构设计
4. 识别架构方法
5. 生成质量属性效用树（QA Utility Tree）
6. 分析架构方法，识别：
   - 风险（Risks）
   - 敏感点（Sensitivity Points）
   - 权衡点（Tradeoff Points）
7. 头脑风暴并排序场景
8-9. 重复分析，展示结果

质量属性树：
性能（Performance）
  ├─ API 响应 < 200ms（H）
  └─ 页面加载 < 1s（M）
可用性（Availability）
  ├─ 99.95% SLA（H）
  └─ 故障恢复 < 5min（H）
```

**参考资源**：
- 来源：CMU Software Engineering Institute
- 链接：sei.cmu.edu/library/atam

---

### AWS Well-Architected Framework

**核心理念**：5 大支柱系统化评估云架构

**适用场景**：云架构设计、架构评审、成本优化

**核心框架**：
```
5 大支柱：
1. 成本优化（Cost Optimization）
   - 合适的资源类型
   - 弹性伸缩
   - 成本监控

2. 卓越运营（Operational Excellence）
   - 代码即基础设施
   - 自动化部署
   - 监控和告警

3. 性能效率（Performance Efficiency）
   - 全球化部署
   - 无服务器架构
   - 缓存策略

4. 可靠性（Reliability）
   - 多可用区
   - 自动恢复
   - 备份策略

5. 安全性（Security）
   - 最小权限原则
   - 数据加密
   - 审计日志
```

**参考资源**：
- 网站：aws.amazon.com/architecture/well-architected/
- 工具：AWS Well-Architected Tool

---

## 5. 销售 (Sales)

### Neil Rackham - SPIN Selling

**核心理念**：大客户销售靠提问，不靠推销

**适用场景**：B2B 销售、企业级产品、顾问式销售

**核心框架**：
```
SPIN 提问法：
1. Situation（情境问题）
   - "你们现在用什么工具？"
   - 目的：了解现状

2. Problem（问题问题）
   - "这个工具有什么不方便的地方？"
   - 目的：挖掘痛点

3. Implication（暗示问题）
   - "这个问题影响了团队的效率吗？"
   - 目的：放大痛点

4. Need-Payoff（需求-效益问题）
   - "如果解决了这个问题，能节省多少时间？"
   - 目的：让客户说出价值
```

**参考资源**：
- 书籍：《SPIN Selling》
- 训练：Huthwaite International

---

## 6. 决策制定 (Decision Making)

### Jeff Bezos - Type 1 vs Type 2 Decisions

**核心理念**：区分可逆和不可逆决策，匹配决策速度

**适用场景**：产品决策、战略规划、创业选择

**核心框架**：
```
决策分类：
Type 1（单向门，不可逆）：
- 慢决策，深思熟虑
- 高层决策
- 示例：并购、转型

Type 2（双向门，可逆）：
- 快决策，快速迭代
- 授权团队
- 示例：功能上线、定价调整

决策原则：
- 70% 信息即可决策
- 不同意但承诺（Disagree and Commit）
- 客户至上
```

**参考资源**：
- 来源：Bezos 股东信
- 文档：Amazon Leadership Principles

---

### Charlie Munger - 多学科心智模型

**核心理念**：用多个学科的框架思考，避免「锤子-钉子」陷阱

**适用场景**：复杂决策、投资分析、战略规划

**核心框架**：
```
核心心智模型：
1. 复利效应（数学）
2. 供需关系（经济学）
3. 进化论（生物学）
4. 心理偏误（心理学）
5. 临界点（物理学）

Latticework of Mental Models：
多学科模型网格化思维

决策清单（Checklist）：
- 避免心理偏误
- 逆向思考
- 边际效用递减
```

**参考资源**：
- 书籍：《穷查理宝典》
- 来源：Berkshire Hathaway 年会

---

## 7. 招聘 (Hiring)

### Geoff Smart - Who: The A Method

**核心理念**：系统化招聘流程，提升招聘成功率

**适用场景**：高管招聘、关键岗位、团队搭建

**核心框架**：
```
4 步招聘流程：
1. Scorecard（评分卡）
   - 定义成功标准
   - 列出关键能力

2. Source（来源）
   - 主动寻找 A 级候选人
   - 推荐网络

3. Select（选拔）
   - 筛选面试（Screening Interview）
   - 定向面试（TopGrading Interview）
   - 聚焦面试（Focused Interview）
   - 背景调查（Reference Interview）

4. Sell（说服）
   - 匹配候选人动机
   - 5 F's：Fit, Family, Freedom, Fortune, Fun
```

**参考资源**：
- 书籍：《Who: The A Method for Hiring》
- 工具：Scorecard 模板

---

## 8. 谈判 (Negotiation)

### Chris Voss - Never Split the Difference

**核心理念**：战术同理心，用情绪智能赢得谈判

**适用场景**：商务谈判、薪酬谈判、危机处理

**核心框架**：
```
核心技巧：
1. 镜像（Mirroring）
   - 重复对方最后 3 个词
   - 触发对方继续说

2. 标记（Labeling）
   - "看起来你担心..."
   - 识别并命名情绪

3. 校准问题（Calibrated Questions）
   - "这个问题如何解决？"
   - 让对方给方案

4. Accusation Audit
   - 主动说出对方可能的指控
   - "你可能觉得这个价格太高..."

5. "No"-Oriented Questions
   - "现在不是好时机吗？"
   - 降低防御心理
```

**参考资源**：
- 书籍：《Never Split the Difference》
- 背景：FBI 人质谈判专家

---

## 9. 创业 (Startups)

### Eric Ries - Lean Startup

**核心理念**：快速验证假设，减少浪费

**适用场景**：早期创业、新产品开发、创新项目

**核心框架**：
```
Build-Measure-Learn 循环：
1. Build（构建 MVP）
   - 最小可行产品
   - 快速上线

2. Measure（衡量数据）
   - 关键指标
   - A/B 测试

3. Learn（学习调整）
   - 验证假设
   - 转型（Pivot）或坚持（Persevere）

创新会计（Innovation Accounting）：
- 基准线指标
- 优化引擎
- 转型决策
```

**参考资源**：
- 书籍：《The Lean Startup》
- 方法：Lean Canvas

---

### Paul Graham - 做不可扩展的事 (Do Things That Don't Scale)

**核心理念**：早期不追求规模，手动获取种子用户

**适用场景**：0-1 阶段、用户增长、产品打磨

**核心框架**：
```
早期策略：
1. 手动招募用户
   - Airbnb 挨家挨户拍照
   - Stripe 帮用户集成

2. 过度服务用户
   - 创始人亲自客服
   - 快速响应反馈

3. 专注小市场
   - 先占领利基市场
   - 再扩展到大市场

4. 快速迭代
   - 每周发版
   - 根据反馈调整
```

**参考资源**：
- 文章：paulgraham.com/ds.html
- 来源：YC 创业课

---

## 10. 工程实践 (Engineering)

### Kent Beck - Extreme Programming (XP)

**核心理念**：通过极限实践提升软件质量

**适用场景**：敏捷开发、质量保障、团队协作

**核心框架**：
```
核心实践：
1. 测试驱动开发（TDD）
   - Red → Green → Refactor

2. 结对编程（Pair Programming）
   - Driver + Navigator
   - 知识共享

3. 持续集成（CI）
   - 频繁合并代码
   - 自动化测试

4. 简单设计（Simple Design）
   - YAGNI（You Aren't Gonna Need It）
   - 最小化复杂度

5. 重构（Refactoring）
   - 持续改进代码
   - 消除技术债务
```

**参考资源**：
- 书籍：《Extreme Programming Explained》
- 实践：XP Values and Principles

---

## 11. 领导力 (Leadership)

### Kim Scott - Radical Candor

**核心理念**：关心个人，直接挑战

**适用场景**：团队管理、反馈沟通、绩效管理

**核心框架**：
```
Radical Candor 矩阵：
            关心个人（Care Personally）
                    高          低
直接挑战  高  | Radical Candor | Obnoxious Aggression
（Challenge） 
Directly）低  | Ruinous Empathy | Manipulative Insincerity

核心实践：
1. 1-on-1 定期沟通
2. 即时反馈（当场、具体）
3. 鼓励下级挑战上级
4. 关注成长，而非"做好人"
```

**参考资源**：
- 书籍：《Radical Candor》
- 工具：Feedback 模板

---

## 12. 系统可靠性 (Site Reliability)

### Google SRE

**核心理念**：用软件工程方法解决运维问题

**适用场景**：大规模系统、运维自动化、可靠性工程

**核心框架**：
```
SRE 原则：
1. 拥抱风险（Embrace Risk）
   - Error Budget（错误预算）
   - SLO/SLA/SLI

2. 减少琐事（Eliminate Toil）
   - 自动化
   - 减少重复工作

3. 监控系统（Monitoring）
   - 四个黄金信号：
     - Latency（延迟）
     - Traffic（流量）
     - Errors（错误率）
     - Saturation（饱和度）

4. 应急响应（Incident Response）
   - Runbook
   - Blameless Postmortem

5. 发布工程（Release Engineering）
   - 灰度发布
   - 快速回滚
```

**参考资源**：
- 书籍：《Site Reliability Engineering》
- 网站：sre.google

---

## 13. 敏捷和 Scrum

### Scrum Guide - 官方框架

**核心理念**：轻量级框架，持续交付价值

**适用场景**：产品开发、迭代管理、团队协作

**核心框架**：
```
3 个角色：
- Product Owner（产品负责人）
- Scrum Master（敏捷教练）
- Development Team（开发团队）

5 个事件：
- Sprint（冲刺，2-4 周）
- Sprint Planning（规划会）
- Daily Scrum（每日站会）
- Sprint Review（评审会）
- Sprint Retrospective（复盘会）

3 个工件：
- Product Backlog（产品待办）
- Sprint Backlog（冲刺待办）
- Increment（增量）
```

**参考资源**：
- 文档：scrumguides.org
- 认证：Scrum Alliance

---

## 14. 设计思维 (Design Thinking)

### IDEO - Design Thinking

**核心理念**：以人为本的创新方法

**适用场景**：产品创新、用户体验、问题解决

**核心框架**：
```
5 步流程：
1. Empathize（共情）
   - 用户访谈
   - 观察行为

2. Define（定义）
   - 用户画像
   - 问题陈述

3. Ideate（创意）
   - 头脑风暴
   - 发散思维

4. Prototype（原型）
   - 快速原型
   - 低保真验证

5. Test（测试）
   - 用户测试
   - 迭代优化
```

**参考资源**：
- 机构：IDEO.org
- 工具：Design Thinking Toolkit

---

## 15. 持续学习与知识管理

### Zettelkasten（卡片盒笔记法）

**核心理念**：原子化笔记，双向链接，涌现洞察

**适用场景**：知识管理、研究写作、终身学习

**核心框架**：
```
3 种笔记：
1. Fleeting Notes（临时笔记）
   - 快速记录想法
   - 临时存储

2. Literature Notes（文献笔记）
   - 阅读摘要
   - 用自己的话

3. Permanent Notes（永久笔记）
   - 原子化（一个想法一张卡片）
   - 双向链接
   - 持续积累

核心原则：
- 一张卡片一个想法
- 用自己的话重写
- 链接相关卡片
- 让洞察自然涌现
```

**参考资源**：
- 书籍：《How to Take Smart Notes》
- 工具：Obsidian, Roam Research

---

## Oral Tradition（口述传统）

一些专家主要通过演讲、访谈、播客分享知识：

### Steve Jobs
- 产品设计、极简主义、创新
- 资源：Stanford 演讲、Apple 发布会

### Elon Musk
- 第一性原理、工程思维、快速迭代
- 资源：采访、Twitter/X

### Jensen Huang (NVIDIA)
- AI 基础设施、技术战略
- 资源：GTC Keynote

### Patrick Collison (Stripe)
- 支付基础设施、创业
- 资源：Twitter、访谈

---

## 数据库维护

### 更新流程

1. **季度审查**：每季度审查并补充
2. **社区贡献**：欢迎 PR 补充新方法论
3. **质量标准**：
   - 有书籍/论文/白皮书支持
   - 经过时间检验（至少 5 年）
   - 有实际案例应用

### 贡献指南

欢迎补充以下信息：
- 新的领域专家
- 具体的案例和模板
- 中文资源链接
- 国内专家方法论

---

## 中国特色补充

### 产品管理
- 张小龙（微信产品哲学）
- 俞军（产品方法论）

### 技术架构
- 阿里巴巴中间件团队
- 字节跳动飞书架构

### 合规和安全
- 等保 2.0 框架
- 数据安全法实施指南

---

**持续更新中...**

欢迎贡献：提 Issue 或 PR 到 GitHub 仓库
