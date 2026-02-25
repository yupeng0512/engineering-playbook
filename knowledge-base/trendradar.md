# TrendRadar 完整经验档案

> 项目周期: 2025 ~ 进行中
> 最后更新: 2026-02-25
> 状态: 活跃使用（定制化部署）

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | 热点新闻聚合与推送系统 |
| **领域** | 信息聚合 / AI 分析 |
| **规模** | ~8K 行 Python，26 个 MCP 工具，9 个推送渠道 |
| **核心价值** | 告别无效刷屏，30 秒部署的热点聚合助手 |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 语言 | Python | 3.10+ | |
| AI 接口 | LiteLLM | ≥1.57.0 | 100+ LLM 提供商统一接口 |
| MCP Server | FastMCP | 2.0 (≥2.12.0, <2.14.0) | stdio + HTTP 双模式 |
| 爬虫 | requests + feedparser | | newsnow API + RSS |
| 存储 | SQLite + S3 (boto3) | | 双后端自动选择 |
| 定时任务 | supercronic (Docker) / cron (GitHub Actions) | | |
| 部署 | Docker Compose + GitHub Actions | | |
| 配置 | YAML + 环境变量 | | 文件内嵌版本号 |

### 架构概览

```
定时触发 (cron/supercronic)
    │
    ▼
采集: DataFetcher → newsnow API (11平台) + RSSFetcher
    │
    ▼
存储: StorageManager → SQLite (local) / S3 (remote) auto 选择
    │
    ▼
分析: FrequencyAnalyzer (关键词) + AIAnalyzer (LiteLLM) + AITranslator
    │
    ▼
输出: HTML Report + NotificationDispatcher → 9 渠道推送
    │
    ▼
MCP: FastMCP 2.0 Server → 26 个工具 + 4 个资源
```

---

## 做得好的地方

### 技术选型

#### LiteLLM 统一 AI 接口

- **技术**: LiteLLM
- **场景**: AI 分析和翻译
- **考虑过的备选**: 直接调用各厂商 SDK
- **选择理由**: 一层抽象兼容 100+ 提供商，切换模型只需改配置
- **实际效果**: 无缝切换 DeepSeek/OpenAI/Gemini，零代码改动
- **推荐指数**: 5/5
- **适用建议**: 任何需要多 LLM 提供商支持的项目

#### FastMCP 2.0

- **技术**: FastMCP 2.0 (stdio + HTTP 双模式)
- **场景**: MCP 协议服务端
- **考虑过的备选**: 原始 MCP SDK
- **选择理由**: 声明式工具注册，比原始 SDK 简洁 5 倍
- **实际效果**: 26 个工具清晰组织在 7 个分类文件中
- **推荐指数**: 4/5（需锁定版本，<2.14.0 有 breaking change）
- **适用建议**: Python MCP Server 开发首选，但注意版本锁定

### 架构设计

#### AppContext 依赖注入模式

- **解决的问题**: 全局状态分散，模块间耦合高
- **实现方式**: `context.py` 封装所有配置和操作，作为唯一依赖注入点
- **可复用程度**: 高
- **复用注意事项**: 适合中型 Python 项目，超大项目考虑用 dependency-injector 库

#### periods + day_plans + week_map 调度模型

- **解决的问题**: 不同时段（白天/夜间/工作日/周末）需要不同的推送频率
- **实现方式**: 三层时间线模型 — `periods`(时段定义) → `day_plans`(日计划组合) → `week_map`(按星期映射)
- **可复用程度**: 高
- **复用注意事项**: 提供 5 种预设模板（通勤族/夜猫子/重度用户等），可直接复用

#### StorageManager 多后端自动选择

- **解决的问题**: GitHub Actions 无持久存储 vs Docker 有本地磁盘 vs 生产环境需要云存储
- **实现方式**: `auto` 模式根据环境变量自动选择 SQLite(local) 或 S3(remote)
- **可复用程度**: 高
- **复用注意事项**: S3 兼容层需处理 Cloudflare R2 的 chunked encoding 差异

#### 多渠道推送分批处理

- **解决的问题**: 9 个渠道字节限制不同（飞书 30KB、钉钉 20KB、Bark 4KB）
- **实现方式**: `split_content_into_batches()` 根据渠道上限自动拆分，每条独立发送
- **可复用程度**: 高
- **复用注意事项**: 字节估算需考虑 UTF-8 中文字符 3 字节

### 其他亮点

- **配置文件版本管理**: 文件内嵌版本号 + 远程版本检查，支持渐进式升级提醒
- **GitHub Actions 签到续期**: 7 天不签到自动停止，节约公共资源（创新方案）
- **可视化配置编辑器**: docs/ 目录下的纯前端 Web 编辑器，降低 YAML 门槛
- **MCP 工具分类组织**: 26 个工具按职责分 8 个文件，清晰可维护

---

## 做得不好的地方

### 踩坑清单

#### 坑 1: CRLF 换行符导致 Docker 容器启动失败

- **影响程度**: 中
- **现象**: Docker 容器启动时 entrypoint.sh 报错 `/bin/bash^M: bad interpreter`
- **根因**: Windows 开发环境 git 自动转换换行符为 CRLF
- **解决方案**: entrypoint.sh 中加 `sed -i 's/\r$//'` 强制转换
- **预防建议**: `.gitattributes` 中指定 `*.sh text eol=lf`

#### 坑 2: S3 兼容存储差异

- **影响程度**: 中
- **现象**: Cloudflare R2 上传/下载行为与 AWS S3 不一致
- **根因**: R2 对 chunked encoding 和 virtual-hosted style 的支持差异
- **解决方案**: boto3 配置中显式设置 `s3.addressing_style = path`
- **预防建议**: 使用 S3 兼容存储前先测试 CRUD 全流程

#### 坑 3: 时区计算错位

- **影响程度**: 高
- **现象**: 推送时间和数据日期不匹配
- **根因**: 全局 timezone 影响日期计算、调度器、存储三个环节，配置不一致
- **解决方案**: 统一设置 `TZ=Asia/Shanghai` 环境变量
- **预防建议**: 项目启动时在 config 层统一时区，所有时间操作使用 aware datetime

#### 坑 4: ntfy 默认地址误检测

- **影响程度**: 低
- **现象**: ntfy 推送渠道状态显示"已配置"但实际是默认值
- **根因**: 默认 `https://ntfy.sh` 不应被判为"用户已配置"
- **解决方案**: 判断逻辑中排除默认值

#### 坑 5: 配置版本 Breaking Change

- **影响程度**: 高
- **现象**: v6.0.0 升级后旧配置 `push_window` 不工作
- **根因**: 新的 timeline.yaml 调度系统替代了旧的 push_window 机制
- **解决方案**: 提供配置迁移说明，旧字段保留但标记 deprecated
- **预防建议**: Breaking Change 必须提供自动迁移脚本或清晰的手动迁移文档

### 架构调整

#### 调整 1: 推送内容五大板块重构 (v5.0.0)

- **旧方案**: 简单列表式推送
- **问题**: 信息密度低，用户需要自己筛选
- **新方案**: AI 分析 + 关键词匹配 + 趋势检测 + 翻译 + 原始热榜五大板块
- **收益量化**: 用户反馈信息获取效率提升约 3 倍

#### 调整 2: 存储架构全面重构 (v4.0.0)

- **旧方案**: 纯文件存储
- **问题**: GitHub Actions 无持久文件系统，数据每次运行都丢失
- **新方案**: SQLite (本地) + S3 (远程) 双后端 + auto 模式
- **收益量化**: 解决数据持久化问题，GitHub Actions 场景下数据可跨运行保留

---

## 可复用资产

### 代码模式

- **AppContext 依赖注入**: `trendradar/context.py` — 消除全局状态的轻量方案
- **多渠道推送分批**: `trendradar/notification/splitter.py` — 按字节限制自动拆分
- **三层时间线调度**: `config/timeline.yaml` — 灵活的定时任务编排
- **StorageManager 多后端**: `trendradar/storage/manager.py` — auto 模式自动选择存储

### 配置模板

- **Docker 多服务编排**: `docker/docker-compose.yml` — 主服务 + MCP 双容器
- **GitHub Actions 定时工作流**: `.github/workflows/crawler.yml` — 含签到续期机制

---

## 给未来自己的建议

### 如果重新做这个项目

1. 从第一天就用 timeline.yaml 调度系统，不要用 push_window（避免 v6 的 breaking change）
2. S3 兼容存储从一开始就测试 R2/OSS/COS 的差异，不要假设完全兼容
3. 配置文件版本管理从一开始就设计，不要等到版本多了才补

### 延伸到其他项目的通用建议

- **LiteLLM 统一接口**: 任何多 LLM 项目都应该用 LiteLLM，不要直接依赖单个 SDK
- **时区统一**: 项目初始化时就在 config 层定义时区策略，所有模块遵守
- **推送渠道抽象**: 如果需要多渠道推送，从第一天就做 Dispatcher + 渠道适配器抽象

---

## 元数据

- **沉淀时间**: 2026-02-25
- **信息来源**: 代码分析 / README / Git log / 项目结构扫描
- **覆盖度评估**: 约 75%。遗漏：(1) 具体的 MCP 工具实现细节 (2) 前端可视化配置编辑器的实现 (3) RSS 爬虫的具体适配经验
