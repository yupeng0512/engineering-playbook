---
title: data-pipeline-monitor
type: note
permalink: engineering-playbook/patterns/data-pipeline-monitor
---

# 数据采集→分析→推送管道模式

> 来源项目: TrendRadar, github-sentinel, truthsocial-trump-monitor, infohunter
> 沉淀时间: 2026-02-25

---

## 适用场景

构建"定时采集数据 → AI/算法分析 → 多渠道推送"的监控/聚合系统。

---

## 核心架构

```
定时调度器 (cron / APScheduler / supercronic)
    │
    ▼
数据采集层 (API / 爬虫 / RSS)
    │ 原始数据
    ▼
存储层 (MySQL / SQLite / S3)
    │ 结构化数据
    ▼
分析层 (AI 分析 / 评分算法 / 关键词匹配)
    │ 分析结果
    ▼
推送层 (飞书 / 企微 / 钉钉 / Telegram / 邮件)
    │ 格式化消息
    ▼
展示层 (Web Dashboard / MCP Server / API)
```

---

## 各层最佳实践

### 1. 调度层

| 技术 | 适用场景 | 项目实例 |
|------|---------|---------|
| APScheduler (Python, AsyncIO) | 应用内调度，支持动态 reschedule | github-sentinel, truthsocial |
| supercronic (Docker) | 容器内轻量定时器，替代 cron | TrendRadar |
| GitHub Actions cron | 无服务器场景 | TrendRadar (轻量模式) |
| node-cron (Node.js) | Node.js 应用内调度 | agentstudio |

**关键实践**:
- 智能调度频率：根据目标活跃时间调整采集间隔（如跨时区目标的活跃/睡眠时段）
- 动态配置：推送时间存储在 DB 中，调度器定期轮询检测变化
- 签到续期：长期运行的 GitHub Actions 加自动过期 + 手动续期

### 2. 采集层

**数据源策略**:
- 单一数据源有单点风险，推荐多数据源 + 自动降级
- github-sentinel 的三模式（auto/github/bigquery）是参考范例
- 根据查询特征（时间范围/精度/成本）智能路由数据源

**防御性采集**:
- 空内容检测（社交媒体的纯图片/视频帖子）
- 数据完整性验证（批量采集后检查字段缺失）
- Rate limit 尊重 + 指数退避重试

### 3. 存储层

| 方案 | 适用场景 | 项目实例 |
|------|---------|---------|
| MySQL + SQLAlchemy 2.0 async | 结构化数据、多维查询 | github-sentinel, truthsocial |
| SQLite + S3 双后端 | 轻量部署、GitHub Actions 场景 | TrendRadar |
| Repository 模式 | 数据访问层统一封装 | github-sentinel |

**关键实践**:
- Repository 模式封装数据访问（`RepoRepository.get_by_id()` 而非散落的 SQL）
- 文件缓存零依赖方案（MD5 key + TTL + JSONL）避免重复查询云服务

### 4. 分析层

| 方案 | 适用场景 | 项目实例 |
|------|---------|---------|
| LLM 分析 (LiteLLM / AG-UI) | 非结构化文本理解、投资洞察 | TrendRadar, truthsocial |
| 多维加权评分 | 结构化数据量化排名 | github-sentinel (六维热度) |
| 关键词匹配 + 频率统计 | 热点发现、趋势检测 | TrendRadar |
| Prompt-based 评估 | 内容推荐和过滤 | infohunter |

**关键实践**:
- AI 返回值永远做防御性解析（JSON 三级提取策略）
- 成本监控从 Day 1 建立（BigQuery/LLM API 调用都需要）
- 评分权重可配置 + 可动态调优

### 5. 推送层

**多渠道 Dispatcher 模式**:

```python
class NotificationDispatcher:
    def __init__(self, channels: list[NotificationChannel]):
        self.channels = channels

    async def dispatch(self, content: AnalysisResult):
        for channel in self.channels:
            if channel.is_configured():
                formatted = channel.format(content)
                batches = channel.split_into_batches(formatted)
                for batch in batches:
                    await channel.send(batch)
```

**关键实践**:
- 各渠道字节限制不同（飞书 30KB、企微 4096 字符、Bark 4KB），需自动分批
- AI 分析结果 → IM 消息需要专门的格式化层
- 懒加载客户端（未配置的渠道不初始化）
- 推送失败不阻塞其他渠道

### 6. 展示层

- Web Dashboard 做只读展示（React + TailwindCSS）
- MCP Server 暴露数据查询能力给 AI 编辑器
- REST API 支持外部系统集成

---

## 通用踩坑

### 时区问题（所有监控项目都踩过）

**解决方案**: 项目初始化时定义时区策略
- Docker 容器: `TZ=Asia/Shanghai` 环境变量
- 数据库: 统一存储 UTC，查询时转换
- 前端: 按用户时区展示
- 调度器: 与服务器时区对齐

### IM 消息长度限制

**解决方案**: 推送前统一做长度检查
```python
CHANNEL_LIMITS = {
    "feishu": 30 * 1024,   # 30KB
    "wework": 4096,         # 4096 字符
    "dingtalk": 20 * 1024,  # 20KB
    "bark": 4096,           # 4KB
}
```

### 云服务成本控制

**解决方案**: 从 Day 1 建立成本监控
- 记录每次 API 调用的 token 数/查询量/费用
- 设置预算上限告警
- 文件缓存减少重复查询

---

## 前后对比

| 维度 | 无此 Pattern | 使用此 Pattern |
|------|-------------|---------------|
| 新监控系统启动 | 从零设计架构 | 五层架构直接套用 |
| 推送渠道适配 | 每次硬编码 | Dispatcher + 渠道适配器 |
| 时区问题 | 每个项目踩一次 | Day 1 定义策略 |
| 成本失控 | 收到账单才发现 | Day 1 建立监控 |