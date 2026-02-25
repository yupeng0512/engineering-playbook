# GitHub Sentinel 完整经验档案

> 项目周期: 2025 ~ 进行中
> 最后更新: 2026-02-25
> 状态: 活跃使用

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | GitHub 热门项目监控与订阅系统 |
| **领域** | 开源监控 / 数据分析 / AI |
| **规模** | ~5K 行 Python + React 前端 + Node.js MCP 服务 |
| **核心价值** | 追踪开源世界的脉搏，发现高潜力项目 |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 语言 | Python | 3.10+ (容器 3.11-slim) | |
| Web 框架 | FastAPI | ≥0.109 | |
| ORM | SQLAlchemy 2.0 (async) | | aiomysql 异步驱动 |
| 数据库 | MySQL | 8.0 | |
| 定时任务 | APScheduler | ≥3.10 (AsyncIO) | |
| HTTP 客户端 | httpx | ≥0.26 | 异步 |
| GraphQL | gql[all] | ≥3.4 | GitHub GraphQL API |
| 大数据 | Google BigQuery | ≥3.15 | GH Archive 历史数据 |
| 配置 | Pydantic Settings | ≥2.5 | 嵌套结构 + YAML |
| AI | AG-UI 协议 (Knot) | | 智能体调用 |
| MCP | Node.js SDK | | 独立服务 |
| 前端 | React + TailwindCSS | | Web Dashboard |
| 部署 | Docker Compose | 4 服务 | |

### 架构概览

```
GitHub API / GraphQL / GH Archive (BigQuery)
    │
    ▼
TrendingAnalyzerV2 (智能数据源选择: auto/github/bigquery)
    │
    ▼
CrawlServiceV2 (采集编排) → MySQL (repos/trending/star_history)
    │
    ▼
RankingService (六维加权热度评分)
    │
    ▼
NotificationDispatcher → 企微/飞书 + AI 分析 (Knot AG-UI)
    │
    ▼
FastAPI → React Dashboard / MCP Server
```

---

## 做得好的地方

### 技术选型

#### 三模式数据源策略 (auto/github/bigquery)

- **技术**: GitHub REST API + GraphQL + BigQuery (GH Archive)
- **场景**: 不同时间范围的热门项目查询
- **选择理由**: 短期(≤3天)用 GitHub API 免费实时，长期用 BigQuery 回溯到 2011 年
- **实际效果**: auto 模式根据查询参数自动选择，BigQuery 不可用时自动降级到 GitHub
- **推荐指数**: 5/5
- **适用建议**: 数据源成本不均时，按查询特征路由是最佳实践

#### GraphQL + REST 并用

- **技术**: GitHub REST API + GraphQL API
- **选择理由**: GraphQL 一次查询获取 Star/Fork/PR/Issue/Topic，节省 API 调用次数
- **实际效果**: 减少约 60% 的 API 请求
- **推荐指数**: 4/5
- **适用建议**: GitHub 数据密集型项目必选，但需处理 rate limit 差异

#### Pydantic Settings 嵌套配置

- **技术**: Pydantic Settings + YAML + 环境变量
- **场景**: 12 个子配置类的复杂配置管理
- **选择理由**: 类型安全 + 验证 + 环境变量自动绑定
- **实际效果**: 配置错误在启动时即被发现，开发体验优秀
- **推荐指数**: 5/5
- **适用建议**: 所有 FastAPI 项目的配置管理标配

### 架构设计

#### 六维加权热度评分算法

- **解决的问题**: 如何量化一个 GitHub 项目的"热度"
- **实现方式**: 6 个维度 + 对数归一化 + 可调权重
  ```
  0.35×weekly_stars + 0.20×monthly_stars + 0.10×weekly_forks
  + 0.15×activity_decay + 0.10×total_stars_log + 0.10×trending_bonus
  ```
- **可复用程度**: 中（GitHub 特定，但评分框架通用）
- **复用注意事项**: 权重可通过 `weight_tuning_service` API 动态调整

#### Repository 模式数据访问

- **解决的问题**: 数据访问逻辑分散，难以测试
- **实现方式**: `RepoRepository` / `StarHistoryRepository` / `TrendingRepository` / `CrawlLogRepository`
- **可复用程度**: 高
- **复用注意事项**: 基于 SQLAlchemy 2.0 async，需要 aiomysql 驱动

#### 文件系统查询缓存

- **解决的问题**: BigQuery 查询成本高（每次约 $0.005-0.05）
- **实现方式**: MD5 key + TTL + JSONL 存储，零基础设施依赖
- **可复用程度**: 高
- **复用注意事项**: 适合单实例场景，多实例需换 Redis

### 其他亮点

- **BigQuery 成本监控**: `MonitoringService` 按 JSONL 记录查询成本，支持配额告警
- **动态配置推送时间**: 存储在 MySQL `system_config` 表，调度器每分钟轮询检测变化
- **Click CLI 多命令**: `api` / `scheduler` / `crawl_trending` / `run_job` / `status` 子命令

---

## 做得不好的地方

### 踩坑清单

#### 坑 1: BigQuery 成本失控

- **影响程度**: 高
- **耗时**: 约 1 天排查 + 优化
- **现象**: 每小时查询导致 BigQuery 账单快速增长
- **根因**: 初始版本每小时全量查询 GH Archive，每次扫描大量数据
- **解决方案**: (1) 查询频率从每小时降到每 6 小时 (2) 文件缓存避免重复查询 (3) 免费额度监控告警
- **预防建议**: 云服务调用必须在 MVP 阶段就设计成本监控和预算上限

#### 坑 2: 企业微信消息长度截断

- **影响程度**: 中
- **现象**: AI 分析内容超过 4096 字符被截断
- **根因**: 企微 Markdown 消息最多 4096 字符，AI 输出不可控
- **解决方案**: AI 分析结果格式化时预留空间，超长时提供精简版
- **预防建议**: IM 推送前统一做长度检查和截断，保留完整版链接

#### 坑 3: 时区三重问题

- **影响程度**: 高
- **现象**: 定时任务触发时间、数据库查询范围、前端展示时间不一致
- **根因**: APScheduler 时区 + MySQL 时区 + Python datetime 混用
- **解决方案**: 统一 `TZ=Asia/Shanghai`，所有时间使用 timezone-aware datetime
- **预防建议**: 同 TrendRadar — 项目初始化时定义时区策略

#### 坑 4: GH Archive 不支持语言过滤

- **影响程度**: 中
- **现象**: BigQuery 查询结果包含所有语言，无法在查询层过滤
- **根因**: GH Archive 的 event payload 中不包含仓库语言信息
- **解决方案**: BigQuery 查询候选量 ×3，再通过 GraphQL 获取语言信息后过滤
- **预防建议**: 使用第三方数据源前，先验证其字段完整性

#### 坑 5: 仓库描述数据丢失

- **影响程度**: 中
- **现象**: 部分仓库的 description 为空
- **根因**: GraphQL 批量查询可能返回 None
- **解决方案**: 专门的 `fill_missing_descriptions` 定时任务补数据
- **预防建议**: 批量数据采集后需要有数据完整性检查和补偿机制

### 决策失误

#### 失误 1: 初始选择纯 GitHub API

- **当时的决策**: 仅使用 GitHub REST API 获取数据
- **当时的理由**: 简单直接，API 免费
- **为什么错了**: 无法获取 7 天以上的 Star 增量数据，排名不准确
- **正确做法**: 从一开始就设计多数据源架构（API + Archive）
- **代价**: 后来重构数据源层，增加了 BigQuery 集成工作量

---

## 可复用资产

### 代码模式

- **智能数据源路由**: `src/analyzer/trending_v2.py` — 根据查询特征自动选择数据源
- **Repository 模式**: `src/storage/repository.py` — SQLAlchemy 2.0 async 数据仓库
- **文件缓存**: `src/services/query_cache.py` — MD5 key + TTL + JSONL，零依赖
- **成本监控**: `src/services/monitoring_service.py` — 云服务调用成本跟踪

### 配置模板

- **Docker Compose 4 服务编排**: MySQL + Backend + Scheduler + Frontend 分离部署
- **Pydantic Settings 嵌套**: 12 个子配置类的组织方式

---

## 给未来自己的建议

### 如果重新做这个项目

1. 从第一天就设计多数据源架构，不要先用单一 API 再重构
2. BigQuery 成本监控在第一次调用前就配好，不要等账单出来才做
3. 企微/飞书消息长度限制写在配置中而非硬编码

### 延伸到其他项目的通用建议

- **云服务成本控制**: 任何云 API 调用（LLM、BigQuery、S3）都需要从 Day 1 设计成本监控
- **数据源完整性验证**: 使用第三方 API 前，先验证所需字段是否完整，避免后期补数据
- **Repository 模式**: SQLAlchemy 2.0 async + Repository 是 FastAPI 项目的标配架构

---

## 元数据

- **沉淀时间**: 2026-02-25
- **信息来源**: 代码分析 / README / Git log / 项目结构扫描
- **覆盖度评估**: 约 80%。遗漏：(1) React 前端 Dashboard 的具体实现 (2) MCP Node.js 服务细节 (3) 权重调优服务的具体使用经验
