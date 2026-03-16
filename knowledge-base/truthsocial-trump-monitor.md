---
title: truthsocial-trump-monitor
type: note
permalink: engineering-playbook/knowledge-base/truthsocial-trump-monitor
---

# TruthSocial Trump Monitor 完整经验档案

> 项目周期: 2025 ~ 进行中
> 最后更新: 2026-02-25
> 状态: 活跃运行

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | 社交媒体监控与 AI 分析系统 |
| **领域** | 金融 / 舆情监控 / AI |
| **规模** | ~3K 行 Python + 静态前端管理面板 |
| **核心价值** | 实时监控 Trump 动态，AI 驱动的投资洞察 |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 语言 | Python | 3.11+ | |
| Web 框架 | FastAPI + Uvicorn | | |
| 数据库 | MySQL | | SQLAlchemy + PyMySQL |
| 定时任务 | APScheduler (AsyncIO) | | |
| HTTP 客户端 | httpx (异步) + requests | | |
| AI 分析 | AG-UI 协议 (Knot 平台) | | SSE 流式调用 |
| 数据采集 | ScrapeCreators API | | |
| 翻译 | 腾讯云 TMT API | | |
| 通知 | 飞书 Webhook | | |
| 配置 | Pydantic Settings | | |
| 部署 | Docker + Docker Compose | | |

### 架构概览

```
ScrapeCreators API → 定时采集 Trump 帖子
    │
    ▼
MySQL (posts + scrape_logs)
    │
    ├──→ 翻译 (腾讯云 TMT) → 中文翻译
    │
    ├──→ AI 分析 (AG-UI/Knot) → 投资建议 + 风险提示
    │
    └──→ 飞书推送 (实时/日报/周报)
        │
        └──→ FastAPI + 静态前端管理面板
```

---

## 做得好的地方

### 技术选型

#### AG-UI 协议 (Knot 平台)

- **技术**: AG-UI 协议 + SSE 流式调用
- **场景**: 调用 Knot 平台上的 AI 智能体做投资分析
- **考虑过的备选**: 直接调用 OpenAI/DeepSeek API
- **选择理由**: 内网合规 + 平台已有金融分析智能体
- **实际效果**: 分析质量受限于 Agent 能力，但集成成本低
- **推荐指数**: 3/5（平台依赖性高）
- **适用建议**: 企业内网合规场景首选，但需设计降级方案

#### 智能调度频率

- **技术**: APScheduler + 时段策略
- **场景**: 根据 Trump 作息调整采集频率
- **实现方式**: 美东时间活跃时段(7AM-11PM) 每 1 小时采集，睡眠时段每 6 小时
- **实际效果**: 减少约 60% 的无效采集
- **推荐指数**: 5/5
- **适用建议**: 任何监控目标有时间规律的场景

### 架构设计

#### AG-UI SSE 客户端 (核心可复用资产)

- **解决的问题**: 流式调用 Knot 平台 AI Agent
- **实现方式**: `AGUIClient` 730 行，完整处理 SSE 事件类型
- **关键事件类型**:
  - `TEXT_MESSAGE_CONTENT` → 内容拼接
  - `THINKING_TEXT_MESSAGE_CONTENT` → 思考过程
  - `TOOL_CALL_START` / `TOOL_CALL_RESULT` → 工具调用
  - `STEP_FINISHED` → Token 用量统计
  - `RUN_ERROR` → 错误处理
  - `[DONE]` → 流结束
- **双模式认证**: 用户 Token (`x-knot-api-token`) / 智能体 Token (`x-knot-token` + `X-Username`)
- **可复用程度**: 高
- **复用注意事项**: 详见 `agui-protocol-integration` Pattern 中的通用 SSE 客户端实现

#### 业务层 + 协议层分离

- **解决的问题**: AG-UI 通信逻辑与业务分析逻辑耦合
- **实现方式**: `AGUIClient`(协议) + `TrumpPostAnalyzer`(业务) 两层分离
- **可复用程度**: 高
- **复用注意事项**: 换一个分析场景只需替换 Analyzer 类

#### JSON 三级提取策略

- **解决的问题**: AI 返回的 JSON 格式不一致
- **实现方式**:
  1. 直接 `json.loads(text)`
  2. 提取 `` ```json ... ``` `` 代码块
  3. 提取 `{ ... }` 花括号块
- **可复用程度**: 高
- **复用注意事项**: 已在 `llm-json-parser` Pattern 中沉淀

### 其他亮点

- **复用基础设施**: 与 github-sentinel 共享 MySQL 和 Docker 网络，减少资源浪费
- **运行时动态配置**: `runtime_config.py` 支持 API 热更新配置
- **分层推送**: 实时推送（即时）+ 日报（每日汇总）+ 周报（趋势分析）

---

## 做得不好的地方

### 踩坑清单

#### 坑 1: 时区处理混乱

- **影响程度**: 高
- **现象**: 定时任务触发时间和数据过滤时间范围不一致
- **根因**: 服务器时区 vs Trump 美东时区 vs 数据库无时区存储
- **解决方案**: Dockerfile 设置 `TZ=Asia/Shanghai`，采集逻辑中显式转换美东时间
- **预防建议**: 跨时区项目必须在设计阶段明确时区策略

#### 坑 2: 空内容帖子处理

- **影响程度**: 中
- **现象**: 纯视频/图片帖子的文本内容为空，导致 AI 分析和翻译异常
- **排查过程**: 多次迭代（`beaf4e0` → `0d129ef`）才完整处理
- **解决方案**: 空内容检测 + 跳过逻辑 + 日志记录
- **预防建议**: 社交媒体数据不可控，必须对所有字段做空值/异常值防御

#### 坑 3: AI 返回 JSON 格式不一致

- **影响程度**: 中
- **现象**: `specific_targets` 字段格式兼容问题（`82d38cc`）
- **根因**: AI Agent 返回的 JSON 结构随 prompt 和上下文变化
- **解决方案**: 三级 JSON 提取 + 字段级防御性解析
- **预防建议**: 对 AI 返回值永远做防御性解析，不信任格式一致性

### 架构调整

#### 调整 1: 通知模块重构 (9988f34)

- **旧方案**: 飞书消息构建逻辑散落在各处
- **问题**: 修改消息格式需要改多个文件，容易遗漏
- **新方案**: `notification/` 目录下 6 个文件分工明确：client(发送) + builder(构建) + formatters(格式化) + sections(段落) + messages(模板) + feishu(飞书适配)
- **收益量化**: 新增推送格式从改 3 个文件降到改 1 个文件

---

## 可复用资产

### 代码模式

- **AG-UI SSE 客户端**: `src/analyzer/agui_client.py` — 完整的 AG-UI 协议实现
- **JSON 三级提取**: `src/analyzer/agui_client.py` 中的 `_extract_json` — AI 返回值防御性解析
- **智能调度频率**: 根据目标时区和活跃规律调整采集频率
- **基础设施复用**: Docker 网络共享模式（多项目共享 MySQL/网络）

### 配置模板

- **Docker Compose 外部网络**: 复用 github-sentinel 的 MySQL + 网络

---

## 给未来自己的建议

### 如果重新做这个项目

1. 时区策略在 Day 1 设计好：服务器时区、目标时区、存储时区三者明确
2. 社交媒体数据的空值/异常值防御从第一天就做，不要等出 bug 才加
3. AG-UI 客户端做成独立包，方便跨项目复用

### 延伸到其他项目的通用建议

- **AG-UI 集成**: 协议层和业务层必须分离，换场景只换 Analyzer
- **AI 返回值**: 永远做防御性解析，三级降级策略是最佳实践
- **监控类项目**: 根据目标的活跃时间规律调整采集频率，能减少 50%+ 无效请求

---

## 关联项目

| 项目 | 关系 | 说明 |
|------|------|------|
| **github-sentinel** | 基础设施共享 | 共享 MySQL + Docker 网络 |
| **infohunter** | AG-UI 复用 | 共享 AG-UI 客户端模式 |

---

## 元数据

- **沉淀时间**: 2026-02-25
- **门控审核**: 2026-02-25（补充技术栈版本号，消除内部域名泄露，添加关联项目）
- **信息来源**: 代码分析 / README / Git log / 项目结构扫描
- **覆盖度评估**: 约 80%。遗漏：(1) 前端管理面板的具体实现 (2) ScrapeCreators API 的使用限制和成本 (3) 周报的加权排序算法细节