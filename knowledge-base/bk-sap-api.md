---
title: bk-sap-api
type: note
permalink: engineering-playbook/knowledge-base/bk-sap-api
---

# bk-sap-api 完整经验档案

> 项目周期: 2024 ~ 进行中
> 最后更新: 2026-02-25
> 状态: 生产运行

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | 企业级后端服务（运营管理 + 批量任务处理） |
| **领域** | 游戏运营 / 平台服务 |
| **规模** | 大型（Django 双域架构，37 个进程部署，51 个 Handler） |
| **核心价值** | 蓝鲸 PaaS 上的 OSM（运营系统管理）+ SAP（批量任务处理） |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 语言 | Python | 3.10 | |
| Web 框架 | Django | 3.2.25 | Blueapps 基础 |
| REST | Django REST Framework | 3.12.4 | |
| 数据库 | MySQL | 5.7+ | 多库路由 |
| 缓存 | Redis | 5.3.0 | TLOG 缓存系统 |
| 任务队列 | Celery | 5.5.3 | |
| 消息队列 | Kafka | kafka-python3 3.0.0 | 双通道 |
| 分布式计算 | Dask | 2025.3.0 | |
| 流程引擎 | bamboo-pipeline | 3.29.5 | 四套 Pipeline |
| 权限 | bk-iam | 1.3.3 | 蓝鲸权限中心 |
| 链路追踪 | OpenTelemetry | 1.21.0 | |
| 监控 | django-prometheus | 2.3.1 | |
| SSE | channels + django-eventstream | | 实时推送 |
| 代码规范 | Black (120) + Flake8 + pre-commit | | |
| 测试 | pytest + pytest-django | | TDD 工作流 |

### 架构概览

```
蓝鲸 PaaS 平台
├── OSM 模块（运营系统管理）
│   ├── business    业务管理（5 种功能类型）
│   ├── component   组件管理（API/功能/Web/标准字段）
│   ├── ticket      工单流程（bamboo-pipeline）
│   ├── permission   权限管理（IAM 集成）
│   ├── policy      策略管理
│   ├── core        TLOG 缓存系统（日峰值 200w 请求）
│   └── system      系统配置
│
├── SAP 模块（批量任务处理）
│   ├── function     功能定义
│   ├── handlers     51 个业务处理器
│   ├── celery_tasks 异步任务
│   └── beat         定时调度
│
└── Batch 模块（独立部署）
    ├── Kafka 消费者（双通道）
    ├── Dask 分布式（Scheduler + Worker）
    └── Pipeline 执行引擎
```

---

## 做得好的地方

### 技术选型

#### Django 双域架构

- **技术**: 通过 `BKAPP_DEPLOY_SERVICE` 环境变量隔离 OSM 和 SAP 模块
- **场景**: 运营管理（高交互低计算）和批量处理（低交互高计算）的不同需求
- **实现方式**: 三层配置覆盖（default → env → module），每个模块有独立的 settings/urls/INSTALLED_APPS
- **实际效果**: OSM 和 SAP 可独立部署扩缩容，团队可并行开发
- **推荐指数**: 5/5
- **适用建议**: 多业务域的 Django 项目，需要各域独立部署时采用

#### bamboo-pipeline 流程引擎

- **技术**: bamboo-pipeline 3.29.5
- **场景**: 4 套 Pipeline（功能使用/安全校验/批量执行/审批）
- **推荐指数**: 4/5
- **适用建议**: 蓝鲸生态内的流程编排首选，学习曲线中等

### 架构设计

#### TLOG 缓存系统（日峰值 200w 请求）

- **解决的问题**: 高频读取 TLOG 配置数据
- **实现方式**:
  - 专用 Redis，永不过期
  - 原子性覆盖更新（避免先删后设的缓存穿透）
  - 4 个核心缓存键（功能/数据库/字典/业务详情）
  - 每 5 分钟全维度刷新 + 每天 6:30 全量刷新
  - 智能去重 + 批量分批处理
- **可复用程度**: 中（TLOG 特定，但缓存策略通用）

#### 双通道 Kafka 批量处理

- **解决的问题**: 10 万条数据的批量执行
- **实现方式**:
  - 按 500 条拆分子任务
  - 常规通道 + 高优先级通道
  - Dask 并行数据校验和文件解析
- **可复用程度**: 中

#### 数据库路由隔离

- **解决的问题**: 批量任务大量写入不影响主业务
- **实现方式**: `db_router.py` 按模型路由到不同数据库
- **可复用程度**: 高
- **复用注意事项**: Django 原生支持多数据库路由

---

## 做得不好的地方

### 踩坑清单（来自 Code Review 复盘：450 MR，232 条评论）

#### 坑 1: N+1 查询（头号性能问题）

- **影响程度**: 高
- **现象**: 100 条数据产生 201 次 SQL 查询
- **根因**: Serializer 中直接访问 ForeignKey 字段，未做预加载
- **解决方案**: 四层协同 — Model(select_related/prefetch_related) → Resource(ViewSet 添加 queryset) → Serializer(使用 source 而非 property) → Filter(优化 filter 查询)
- **收益量化**: 201 次查询 → 3 次查询
- **预防建议**: 所有 Serializer 的 ForeignKey 字段都检查是否有对应的 select_related

#### 坑 2: ForeignKey 字段命名陷阱

- **影响程度**: 中
- **现象**: 数据库字段变成 `xxx_id_id`
- **根因**: Django ForeignKey 字段名用 `xxx_id` 时，ORM 自动追加 `_id` 后缀
- **解决方案**: ForeignKey 字段名不带 `_id` 后缀（如 `business` 而非 `business_id`）
- **预防建议**: Django 新手常犯，写进团队编码规范

#### 坑 3: Pipeline 节点重试 outputs 被清空

- **影响程度**: 高
- **现象**: Pipeline 节点重试后下游获取不到数据
- **根因**: bamboo-pipeline 重试时会完整执行 execute + schedule，outputs 在 execute 前被清空
- **解决方案**: 重试逻辑中必须重新设置 outputs
- **预防建议**: Pipeline 节点实现时，outputs 设置必须在每次 execute 中完整执行

#### 坑 4: bulk_update 不触发 auto_now

- **影响程度**: 中
- **现象**: `updated_at` 字段在 bulk_update 后未更新
- **根因**: Django `bulk_update` 绕过了 `auto_now` 机制
- **解决方案**: bulk_update 前手动设置 `updated_at = timezone.now()`
- **预防建议**: 使用 bulk_update 时显式处理所有 auto 字段

### Code Review 问题分布

| 问题类型 | 占比 | 高频问题 |
|----------|------|---------|
| 代码规范 | 41% | 死代码、DRY 违规、命名不规范、常量硬编码 |
| 设计架构 | 23% | 模型职责不清、if-else 过多 |
| 优化建议 | 23% | 缓存、日志级别、边界条件 |
| 性能问题 | 7% | N+1 查询、批量操作 |
| 安全问题 | 6% | 输入验证、配置注册遗漏 |

---

## 可复用资产

### 代码模式

- **Django 双域架构**: 三层配置覆盖 + 模块独立部署
- **N+1 查询四层优化**: Model → Resource → Serializer → Filter
- **TLOG 缓存策略**: 永不过期 + 原子覆盖 + 定时刷新
- **pytest_main.py 测试入口**: 统一测试入口 + JSON 参数化 + 关注字段断言

### 配置模板

- **多模块部署**: `app_desc_stag.yaml`（37 个进程的部署配置）
- **AI 工作流规范**: 9 个 CodeBuddy Skills 的组织方式

---

## 给未来自己的建议

### 如果重新做这个项目

1. N+1 查询检查纳入 CI（django-silk 或 django-debug-toolbar SQL 计数断言）
2. ForeignKey 命名规范从第一天写进 `.cursor/rules/`
3. Pipeline 节点模板包含 outputs 重置的标准实现

### 延伸到其他项目的通用建议

- **Django 双域**: 业务域差异大时（如管理端 vs 计算端），用模块化隔离而非单体
- **N+1 查询**: 所有 DRF Serializer 的 ForeignKey 必须有对应 select_related
- **bulk_update**: 永远手动设置 auto_now 字段
- **Code Review**: 按问题类型做定期复盘，发现趋势比单次修复更有价值

---

## 元数据

- **沉淀时间**: 2026-02-25
- **信息来源**: 代码分析 / Git log / .codebuddy/knowledge/ (27个知识文件) / .cursor/rules/ / Code Review 复盘
- **覆盖度评估**: 约 80%。遗漏：(1) 各 API 封装的具体使用经验 (2) Dask 分布式计算的调优 (3) 蓝鲸 IAM 集成的具体踩坑 (4) 生产运维数据