---
title: infohunter
type: note
permalink: engineering-playbook/knowledge-base/infohunter
---

# InfoHunter 完整经验档案

> 项目周期: 2026-02 ~ 进行中
> 最后更新: 2026-02-25
> 状态: 活跃开发

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | Web 应用（后端 + 双端客户端） |
| **领域** | AI 社交媒体智能监控 |
| **规模** | 后端 ~30 文件，前端 monorepo（Web + Mobile） |
| **核心价值** | 自动从 Twitter/YouTube/Blog 抓取内容，AI 分析后推送高价值信息摘要 |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 语言 | Python | 3.12 | 后端 |
| 语言 | TypeScript | 5.x | 前端 |
| 后端框架 | FastAPI | ≥0.109 | REST API |
| 前端框架 | React 19 + Vite 7 | | Web 管理端 |
| 移动端 | Expo SDK 54 + RN 0.81 | | iOS/Android |
| 数据库 | MySQL | 8.x | SQLAlchemy ORM |
| AI 分析 | Knot Agent (AG-UI 协议) | | Claude 4.5 Sonnet |
| 部署 | Docker Compose + Supervisor | | 单容器双进程 |
| 调度 | APScheduler | ≥3.10 | 独立调度 fetch/analyze/notify |
| 推送 | 飞书 Webhook + Expo Push | | 双通道 |

### 架构概览

```
infohunter/
├── src/
│   ├── main.py              # 核心调度器（订阅流+探索流+AI分析+推送）
│   ├── api.py                # FastAPI REST API
│   ├── config.py             # pydantic-settings 配置
│   ├── sources/              # 数据源适配层
│   │   ├── twitter_search.py   # TwitterAPI.io 搜索
│   │   ├── twitter_detail.py   # ScrapeCreators 推文详情
│   │   ├── youtube.py          # YouTube Data API v3
│   │   ├── rss.py              # RSSHub RSS 解析
│   │   └── transcript_service.py # YouTube 字幕提取
│   ├── filter/
│   │   └── smart_filter.py   # 去重 + 质量评分 + 相关性评分
│   ├── analyzer/
│   │   ├── content_analyzer.py # AI 分析调度
│   │   └── agui_client.py      # AG-UI 协议客户端
│   ├── storage/
│   │   ├── models.py         # SQLAlchemy 模型
│   │   └── database.py       # 数据库操作 + 迁移
│   ├── notification/
│   │   ├── client.py         # 飞书 Webhook 客户端
│   │   ├── builder.py        # 通知内容构建
│   │   └── push_service.py   # Expo Push 推送
│   ├── auth/                 # JWT 认证
│   ├── subscription/         # 订阅管理
│   └── web/                  # 嵌入式管理界面（Vanilla JS）
│       ├── index.html
│       └── app.js
├── config/prompts/           # AI 分析 Prompt 模板
│   ├── content_analysis.txt    # 单条内容深度分析
│   ├── trend_analysis.txt      # 跨平台趋势汇总
│   └── recommend_evaluation.txt # 博主订阅评估
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 做得好的地方

### 技术选型

#### TwitterAPI.io + 高级搜索语法

- **技术**: TwitterAPI.io 作为推文搜索主力，支持 Twitter 高级搜索语法
- **场景**: 替代 Twitter 官方 API（价格过高且限制多）
- **考虑过的备选**: 直接爬虫、Nitter 等免费方案
- **选择理由**: 稳定、支持 min_faves/min_retweets 等高级语法，可在 API 层过滤低质量内容
- **实际效果**: 通过 `_build_query()` 拼接 `min_faves:50 min_retweets:10`，API 层面就过滤了 60%+ 的低质量推文，credit 消耗显著降低
- **推荐指数**: 4/5
- **适用建议**: 适合需要 Twitter 搜索但预算有限的场景；注意 credit 模型，需要做成本控制

#### AG-UI 协议 + Knot Agent

- **技术**: 通过 AG-UI 协议对接 Knot 平台的 AI Agent
- **场景**: 内容分析、趋势汇总、博主评估
- **考虑过的备选**: 直接调 OpenAI/Claude API
- **选择理由**: Knot 平台提供模型调度、token 管理，不需自己管 API key 轮转；且支持 streaming
- **实际效果**: agui_client.py 实现了完整的 RunAgent 协议，支持 streaming 和同步两种模式
- **推荐指数**: 4/5
- **适用建议**: 内网环境且有 Knot 平台可用时推荐；外网需要替换为直接 API 调用

#### pydantic-settings 三级配置链

- **技术**: env file → pydantic BaseSettings → system_config DB 表
- **场景**: 需要运行时动态调整的配置项
- **考虑过的备选**: 纯 env、YAML 配置文件、etcd/consul
- **选择理由**: 轻量级，不引入额外依赖；pydantic 提供类型安全和校验
- **实际效果**: 所有配置都可以通过前端 UI 动态调整，无需重启
- **推荐指数**: 5/5
- **适用建议**: 任何需要"默认值 + 运行时可调"的 Python 项目都适用

### 架构设计

#### 三层解耦管道（fetch → analyze → notify）

- **解决的问题**: 早期 fetch 和 analyze 耦合在一起，一旦 AI 分析慢或失败，会阻塞后续内容拉取
- **实现方式**: 三个独立的 APScheduler job，各自有独立的调度周期。fetch 只负责拉取+落库，analyze 从 DB 中取未分析的内容处理，notify 从 DB 中取已分析未推送的内容发送
- **关键代码**: `src/main.py` 中的 `run_fetch_cycle()` / `run_ai_analysis_job()` / `send_notification()`
- **可复用程度**: 高
- **复用注意事项**: 需要确保中间层（DB）的状态标记清晰，如 `ai_analyzed_at`、`notified` 等字段

#### 动态配置串联模式

- **解决的问题**: 配置写死在 env 中，每次改参数都要重启服务
- **实现方式**: `_get_db_config(key)` 读取 system_config 表 → `@property dynamic_xxx` 封装 → DB 有值用 DB，否则 fallback 到 Settings
- **关键代码**: `src/main.py:85-250`，约 20 个 `dynamic_*` 属性
- **可复用程度**: 高
- **复用注意事项**: 注意类型转换（DB 存的是 JSON，需要 `int()` / `float()` 转换），以及 try/except 防御非法值

#### 增量分析 + 保护机制

- **解决的问题**: AI 分析可能因 LLM 抽风而反复失败，浪费资源；过期内容不应再分析
- **实现方式**: Content 模型增加 `ai_analysis_retries` 字段，查询时 WHERE 过滤 `retries < max` AND `created_at >= cutoff`，按 quality_score DESC 排优先级
- **关键代码**: `src/storage/database.py` 的 `get_unanalyzed_contents_prioritized()` 和 `increment_analysis_retries()`
- **可复用程度**: 高
- **复用注意事项**: max_retries 和 max_age_days 应该是可配置的（已实现通过 ai_config 动态配置）

### 上下文管理（AI 协作编排）

- **Rules 设置**: 项目初期没有设置 Rules，后期添加了 `lessons-learned.mdc`
- **对话策略**: 单个对话 session 处理一个完整功能链（如"质量过滤优化"从分析→设计→实现→部署→验证），避免上下文碎片化
- **效果评价**: 长对话中 AI 能保持对项目架构的完整理解，适合迭代式开发；但对话过长时摘要可能丢失细节

### 其他亮点

- **Prompt 工程分层**: 三套独立的 prompt 模板（content_analysis / trend_analysis / recommend_evaluation），各自有完整的角色设定、方法论、输出规范、评分标准、质量约束。比单一 prompt 更易维护和迭代
- **Credit 成本可观测**: 内存计数 + DB 持久化 + API 看板 + 前端展示，形成完整的成本监控闭环
- **嵌入式 Web 管理界面**: 后端直接 serve 静态 HTML/JS，无需额外前端部署，适合原型期快速验证

#### JWT 认证体系

三文件架构（`security.py` + `deps.py` + `__init__.py`），bcrypt 密码哈希 + JWT access/refresh 双 token。FastAPI 依赖注入三级授权（`get_current_user` / `get_current_user_optional` / `require_admin`）。临时密钥自动生成（开发体验优先）但日志 WARNING 提醒。

#### MCP Server（7 工具）

`src/mcp/server.py` 实现 search_content / list_subscriptions / create_subscription / analyze_url / analyze_author / get_trending / get_stats。部分工具通过 HTTP 回调主 API 而非直接操作 DB——解耦 MCP 进程与主服务。

#### AG-UI JSON 提取 6 层 Fallback

`agui_client.py` 的 `extract_json()` 实现了从简单到复杂的 6 层解析：直接解析 → strict=False → Markdown 代码块提取 → 贪婪 `{}` + 中日韩引号归一化 → 控制字符清理 + trailing comma → 字符级状态机修复未转义双引号。这是 `llm-json-parser` Pattern 的深度强化版。

#### 多 Agent 分治 + 双 Token 认证

AG-UI 客户端支持 3 个独立 Agent（content / trend / recommend），各有独立 agent_id 和 api_key。认证通过 key 前缀 `knot_` 自动区分智能体 token vs 用户 token。

#### 用户内容推送模型（Phase 3）

`UserContentFeed` 表实现用户级内容推送 + 已读/未读追踪。User 模型的 `mode` 字段（global/custom）支持管理员全局订阅和用户个人订阅双轨模式。

#### YouTube 字幕提取双层容错

`TranscriptService` 主用免费 `youtube-transcript-api`（同步库需 `run_in_executor` 包装），失败 fallback 到付费 ScrapeCreators。多语言优先级：en → zh-Hans → zh-Hant → zh → ja → ko。

#### 飞书消息模板（4 种模板 + 双类型自适应）

- `FeishuClient` 自动检测流程 Webhook（纯文本）vs 传统群机器人（Markdown 卡片），响应格式兼容三种（`code:0` / `StatusCode:0` / `msg:success`）
- 4 种消息模板演进：`build_content_notification`（单条）→ `build_ai_digest`（AI 精选摘要）→ `build_daily_report`（日报）→ `build_briefing`（Phase 3 批量简报）
- `_render_ai_summary()` 防御性渲染：兼容 dict/raw_response/plain str 三种 AI 返回格式

---

## 做得不好的地方

### 踩坑清单

#### 坑 1: Docker 部署后浏览器缓存导致前端不更新

- **影响程度**: 中
- **耗时**: 约 30 分钟排查
- **现象**: 代码已部署到容器中，curl 容器内静态文件确认内容已更新，但浏览器页面上看不到新增的"编辑"按钮
- **排查过程**:
  1. 检查 app.js 源码，确认 editSub 函数和 edit-modal 结构存在
  2. docker exec 进容器检查部署的文件内容，确认新代码已到位
  3. curl 容器内端口获取静态文件，确认返回的是新版本
  4. 判定为浏览器缓存旧文件
- **根因**: FastAPI 的 StaticFiles mount 默认不设置 Cache-Control 头，浏览器会缓存 JS/HTML 文件
- **解决方案**: 建议用户 Ctrl+Shift+R 硬刷新；长期应在静态文件 URL 上加版本哈希（如 `app.js?v=hash`）
- **预防建议**: 对频繁更新的嵌入式前端，考虑在 HTML 中加 `<meta http-equiv="Cache-Control" content="no-cache">`，或在文件名中嵌入 content hash
- **关联文件**: `src/web/app.js`, `src/web/index.html`, `src/api.py`

#### 坑 2: YouTube OAuth refresh_token 过期导致 API 静默失败

- **影响程度**: 中
- **耗时**: 发现时问题已存在一段时间
- **现象**: YouTube 订阅不再获取新内容，日志中有 `error_description: "Token has been expired or revoked"` 但不影响其他功能
- **排查过程**:
  1. 查看 docker logs，发现 403 和 invalid_grant 错误
  2. 确认是 Google OAuth 的 refresh_token 过期（测试模式下 7 天过期）
- **根因**: Google 的 OAuth "测试" 发布状态下，refresh_token 有效期只有 7 天。需要将应用发布为"生产"状态或定期手动刷新 token
- **解决方案**: 临时方案是重新获取 refresh_token；长期方案是将 OAuth 应用发布为生产状态
- **预防建议**: 对所有 OAuth 集成，需要监控 token 有效性（如在 /api/health 中暴露 token 状态），并设置告警
- **关联文件**: `src/sources/youtube.py`

#### 坑 3: 订阅配置被环境变量默认值覆盖

- **影响程度**: 高
- **耗时**: 约 1 小时定位 + 修复
- **现象**: 用户在前端把订阅间隔从 4h 改为 8h，重新部署后发现又变回了 4h
- **排查过程**:
  1. 确认前端 API 调用正确，DB 中的值已更新
  2. 发现 main.py 中读取 fetch_interval 时直接用 `settings.default_fetch_interval`，没有查 DB
  3. 发现配置读取优先级错误：env 优先而非 DB 优先
- **根因**: 早期实现时没有区分"系统默认值"和"用户设置值"，所有配置都从 env 读取
- **解决方案**: 实现 `dynamic_*` 属性模式——先查 DB（system_config 表），没有再 fallback 到 Settings（env）
- **预防建议**: 凡是前端可编辑的配置，从一开始就用 DB 优先模式。env 只做首次启动的 seed value
- **关联文件**: `src/main.py`（dynamic 属性区域）

#### 坑 4: LLM 返回的 JSON 格式不标准

- **影响程度**: 高
- **耗时**: 反复迭代
- **现象**: AI 分析结果解析失败，json.loads 报错
- **排查过程**:
  1. 捕获原始 LLM 输出，发现多种格式问题
  2. 有的被 ```json ``` 包裹，有的尾部有解释文字，有的用了单引号
- **根因**: LLM 即使在 prompt 中明确要求"纯 JSON 输出"，仍会概率性违反
- **解决方案**: 实现 `_fix_json_value()` 做多层清洗：去掉 markdown 代码块标记 → 截断尾部非 JSON 文本 → 尝试修复单引号 → 最后一搏 regex 提取
- **预防建议**: 任何依赖 LLM 输出结构化数据的场景，都必须有鲁棒的 parser 层。不要假设 LLM 100% 遵循格式
- **关联文件**: `src/analyzer/content_analyzer.py`

#### 坑 5: Twitter credit 超支

- **影响程度**: 高（直接影响成本）
- **耗时**: 发现后快速修复
- **现象**: 实际 credit 消耗远超预估
- **排查过程**:
  1. 发现探索流每个 woeid 的趋势查询消耗 ~450 credit
  2. 叠加关键词搜索和订阅流，日均消耗失控
- **根因**: 没有成本控制机制，多个调度任务并行不受约束
- **解决方案**: 实现了三层控制——(1) 内存 credit 计数器 (2) DB 持久化每次调用的 credit (3) 日限额熔断 (4) 前端看板可视化
- **预防建议**: 使用计费 API 时，从第一天就要有成本追踪和预算控制。不要等到收到账单才反应
- **关联文件**: `src/main.py`（credit 追踪相关）, `src/api.py`（/api/credits/*）

### 架构调整

#### 调整 1: 全量分析 → 增量分析 + 保护机制

- **旧方案**: 每轮 AI 分析定时任务查询 `ai_analyzed_at IS NULL` 的所有内容，不加任何限制
- **问题**: (1) 分析失败的内容会反复进入队列 (2) 几天前的过期内容还在占用分析资源 (3) 没有优先级，低质量内容和高质量内容同等对待
- **新方案**: Content 模型加 `ai_analysis_retries` 字段，查询条件增加 `retries < max_retries AND created_at >= cutoff`，排序加入 `quality_score DESC`
- **迁移过程**: 新增数据库列（幂等迁移），修改查询方法，更新 job 逻辑
- **收益量化**:
  - 避免对反复失败内容的无效分析: 每条省 1 次 AI 调用
  - 过期内容跳过: 减少约 20-30% 的无效分析量
  - 高质量优先: 确保有限资源用在最有价值的内容上

#### 调整 2: 硬编码配置 → 动态配置体系

- **旧方案**: 所有配置通过 .env 文件或代码中的常量设定
- **问题**: 改任何参数（如探索流的 min_faves、分析 batch_size）都需要改 .env 然后重新部署
- **新方案**: system_config 表 + `dynamic_*` 属性 + API 读写 + 前端表单
- **迁移过程**: 逐步添加 dynamic 属性，每次新增配置项时同步更新 API stats 和前端 UI
- **收益量化**:
  - 配置变更从"改 env + 重新部署"（~5 分钟）变为"点前端保存"（~5 秒）
  - 运维友好度大幅提升

#### 调整 3: Latest 排序 → 多维过滤策略

- **旧方案**: Twitter 搜索纯用 `queryType: "Latest"` 排序，后处理做质量评分
- **问题**: 大量低互动内容被拉取，消耗 credit 后才在后处理被过滤掉
- **新方案**: (1) 搜索查询中拼接 `min_faves:N min_retweets:N` 做 API 层预过滤 (2) 后处理质量评分阈值微调 (3) engagement 评分曲线优化
- **收益量化**:
  - 探索流: min_faves:50 + min_retweets:10 → 低质量推文减少 60%+
  - 订阅流: min_faves:10 → 口水帖基本过滤
  - credit 消耗显著降低（相同的信息密度用更少的 API 调用）

### 决策失误

#### 失误 1: 嵌入式前端没有做资源版本化

- **当时的决策**: 用 FastAPI 的 StaticFiles 直接 serve HTML/JS，图省事没有做文件名哈希
- **当时的理由**: 原型期快速验证，觉得"不会经常改前端"
- **为什么错了**: 实际上前端改动频繁，每次部署后都可能遇到浏览器缓存问题
- **正确做法**: 即使是嵌入式前端，也应该用 content hash 做文件名版本化，或者至少设置正确的 Cache-Control 头
- **代价**: 每次前端改动后，都需要提醒用户硬刷新，用户体验差

---

## 可复用资产

### 代码模式

- **动态配置串联**: 从 env → DB → property 的完整实现模式
  - 源文件: `src/main.py:85-250`
  - 适用场景: 任何需要运行时可调配置的 Python 后端

- **幂等数据库迁移**: inspect → check column exists → ALTER 的模式
  - 源文件: `src/storage/database.py:46-80`
  - 适用场景: 不需要 Alembic 但需要安全增量迁移的项目

- **LLM JSON 清洗**: 多层 fallback 的 JSON 解析
  - 源文件: `src/analyzer/content_analyzer.py`
  - 适用场景: 任何需要从 LLM 输出中提取结构化数据的场景

- **Twitter 高级搜索查询构建**: `_build_query()` 拼接过滤条件
  - 源文件: `src/sources/twitter_search.py`
  - 适用场景: 使用 TwitterAPI.io 或 Twitter API 的项目

- **三层 Prompt 体系**: 角色 → 方法论 → 输出规范 → 评分标准 → 约束
  - 源文件: `config/prompts/`
  - 适用场景: 任何需要结构化 AI 分析输出的场景

### 配置模板

- **Docker Compose + Supervisor**: 单容器双进程部署模板
  - 文件: `docker-compose.yml`, `Dockerfile`, `config/supervisord.conf`

- **pydantic-settings 配置模板**: 带类型校验的完整配置类
  - 文件: `src/config.py`

### 工具/脚本

- **智能过滤器**: 基于互动量、内容丰富度、新鲜度、作者可信度的多维质量评分
  - 文件: `src/filter/smart_filter.py`

- **Credit 追踪系统**: 内存计数 + DB 持久化 + 日限额熔断
  - 文件: `src/main.py`（credit 相关方法）

---

## 给未来自己的建议

### 如果重新做这个项目

1. **从第一天就建立动态配置体系**: 不要先硬编码再迁移，直接用 DB 优先 + env fallback 的模式
2. **前端资源做版本化**: 即使是嵌入式的简单 HTML/JS，也要加 content hash 或 query string 版本号
3. **AI 分析从一开始就做增量 + 保护机制**: retries 限制、过期跳过、优先级排序应该是第一版就有的功能
4. **成本控制第一天就做**: 使用任何计费 API 时，从 day 1 就要有 credit 追踪 + 熔断 + 可视化

### 延伸到其他项目的通用建议

- **三级配置模式**（env → DB → dynamic property）: 适用于任何需要运维友好的后端服务
- **LLM 输出永远不可信**: 必须有鲁棒的解析层，不要依赖 prompt 约束
- **API 成本可观测**: 第三方 API 必须有调用量追踪和预算控制，不能裸奔
- **幂等迁移优于完整迁移链**: 对于小型项目，inspect + check + ALTER 的模式比 Alembic 更轻量
- **分层解耦胜过流水线**: 数据管道中每个阶段独立调度，一个环节故障不会拖垮整个系统

---

## 关联项目

| 项目 | 关系 | 说明 |
|------|------|------|
| **infohunter-client** | 配套前端 | Monorepo 双端客户端，独立档案 |
| **truthsocial-trump-monitor** | AG-UI 复用 | 共享 AG-UI 客户端模式和 MySQL |
| **github-sentinel** | 架构相似 | 同类数据管道系统，共享基础设施 |

---

## 元数据

- **沉淀时间**: 2026-02-25
- **门控审核**: 2026-02-25（增补内容融入主体结构，消除追加日志式组织）
- **信息来源**: 对话历史（多轮迭代）、代码分析、git log、深度代码扫描
- **覆盖度评估**: 约 95%。遗漏：(1) 前端经验已独立为 infohunter-client 档案 (2) 生产环境运维具体数据