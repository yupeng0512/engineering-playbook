---
title: dynamic-config
type: note
permalink: engineering-playbook/patterns/dynamic-config
---

# Pattern: 动态配置 + Admin Dashboard 全栈架构

> 来源项目: InfoHunter → Trading System（演进）
> 推荐指数: 5/5
> 适用范围: 任何需要运行时可调配置的 Python 后端项目

## 核心思想

**DB 优先、ENV 兜底** — 所有可变配置存入数据库，运行时动态读取。DB 无数据时自动回退到环境变量默认值。配合 Admin Dashboard 实现"改配置不碰代码、不重启服务"。

## 适用场景

- 配置项需要在不重启服务的情况下动态调整
- 需要提供 Web UI 让运维/用户管理配置
- 业务实体（如鲸鱼钱包、监控源、通知渠道）需要动态 CRUD
- 项目有多套环境（开发/测试/生产），希望同一份代码适配不同配置
- 避免把业务数据硬编码在源码中

## 架构全景

```
┌───────────────────────────────────────────────┐
│               Admin Dashboard                  │
│  (前端: HTML/CSS/JS, 由 FastAPI 托管)          │
│                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ 业务实体 │  │ 系统配置 │  │ 系统状态仪表 │ │
│  │  CRUD    │  │  编辑    │  │  盘 (只读)   │ │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘ │
└───────┼─────────────┼───────────────┼──────────┘
        │             │               │
   ┌────▼─────────────▼───────────────▼──────┐
   │              Admin API (FastAPI)         │
   │  /admin/whales   /admin/config   /admin/status │
   └────┬─────────────┬──────────────────────┘
        │             │
   ┌────▼─────────────▼──────────────────────┐
   │              PostgreSQL                  │
   │  whale_wallets │ system_config │ ...     │
   └────┬─────────────┬──────────────────────┘
        │             │
   ┌────▼─────────────▼──────────────────────┐
   │           Business Logic                 │
   │  get_dynamic_config(key)                 │
   │    → DB 有值? 返回 DB 值                 │
   │    → DB 无值? 返回 ENV 默认值            │
   └──────────────────────────────────────────┘
```

## 三级配置优先级

```
读取顺序（越下层优先级越高）:

  Level 0: 代码默认值（Pydantic Field default）
    ↑ 被覆盖
  Level 1: .env 文件 → Pydantic BaseSettings
    ↑ 被覆盖
  Level 2: system_config DB 表（运行时修改）
```

## 关键实现

### 1. Pydantic Settings（Level 0 + Level 1）

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    feishu_webhook_url: str = ""
    telegram_bot_token: str = ""
    max_position_pct: float = 0.05
    max_daily_trades: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### 2. SystemConfig DB 模型（Level 2）

```python
class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=False, default="")
    category = Column(String(50), nullable=False, default="general")
    description = Column(Text, default="")
    is_secret = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

设计要点：
- `key` 唯一索引，直接通过 key 查询
- `category` 用于前端分组展示（如 "notification"、"risk"、"trading"）
- `is_secret` 标记敏感字段，前端展示时脱敏（显示 `***`）
- `value` 统一用 Text，业务层做类型转换

### 3. 动态配置读取函数

```python
def get_dynamic_config(key: str, fallback: str = "") -> str:
    """DB 优先 → ENV 兜底"""
    session = get_session()
    try:
        cfg = session.query(SystemConfig).filter_by(key=key).first()
        if cfg and cfg.value:
            return cfg.value
    finally:
        session.close()
    return getattr(settings, key, fallback)
```

业务代码中这样使用：

```python
# 通知模块：动态读取飞书 URL
feishu_url = get_dynamic_config("feishu_webhook_url")

# 风控模块：动态读取仓位限制
max_pct = float(get_dynamic_config("max_position_pct", "0.05"))
```

### 4. 业务实体模型（以鲸鱼钱包为例）

```python
class WhaleWallet(Base):
    __tablename__ = "whale_wallets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alias = Column(String(100), nullable=False, unique=True)
    address = Column(String(42), nullable=False, default="")
    category = Column(String(50), nullable=False, default="general")
    is_active = Column(Boolean, nullable=False, default=True)
    # ... 其他业务字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

设计要点：
- `is_active` 软删除，便于恢复和审计
- `created_at` / `updated_at` 用于追溯

### 5. Seed 机制（首次启动自动初始化）

```python
def init_db():
    Base.metadata.create_all(engine)
    session = get_session()
    _seed_default_config(session)     # ENV → DB（仅空表时）
    _seed_default_entities(session)   # 硬编码默认值 → DB（仅空表时）
    session.close()

def _seed_default_config(session):
    if session.query(SystemConfig).count() > 0:
        return
    defaults = [
        SystemConfig(key="feishu_webhook_url", value=settings.feishu_webhook_url,
                     category="notification", description="飞书 Webhook 地址"),
        # ...
    ]
    session.add_all(defaults)
    session.commit()
```

Seed 原则：
- **只在表为空时执行**（`count() > 0` 判断），避免覆盖用户修改
- Seed 值从 ENV 中读取，确保首次部署时 `.env` 的值被写入 DB
- 后续用户通过 Dashboard 修改的值以 DB 为准

### 6. Admin API（FastAPI Router）

```python
router = APIRouter(prefix="/admin", tags=["admin"])

# 配置 CRUD
@router.get("/config")
@router.put("/config/{key}")

# 业务实体 CRUD
@router.get("/whales")
@router.post("/whales")
@router.put("/whales/{id}")
@router.delete("/whales/{id}")

# 系统状态（只读）
@router.get("/status")

# 功能测试
@router.post("/test-feishu")
```

### 7. 前端 Dashboard

由 FastAPI 直接托管静态文件（无需 Node.js 构建工具链）：

```python
# api.py
DASHBOARD_DIR = Path(__file__).parent.parent / "dashboard"
if DASHBOARD_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(DASHBOARD_DIR / "assets")), name="assets")

    @app.get("/dashboard")
    async def dashboard():
        return FileResponse(str(DASHBOARD_DIR / "index.html"))
```

目录结构：

```
dashboard/
  index.html      # 主页面（Tab 导航 + 各功能面板）
  assets/
    style.css     # 暗色主题 + 工业终端风格
    app.js        # 纯 Vanilla JS，无框架依赖
```

前端设计原则：
- **零构建依赖**：纯 HTML/CSS/JS，无 React/Vue/Webpack
- **单文件部署**：FastAPI 直接托管，无需额外 Nginx
- **Tab 导航**：Dashboard / 业务实体管理 / 配置管理 / 数据列表
- **Toast 反馈**：所有操作有即时视觉反馈

## 项目实践对照

| 项目 | 业务实体 | 动态配置项 | Dashboard 功能 |
|------|----------|-----------|---------------|
| **InfoHunter** | 数据源 / 分析规则 | AI 分析参数、抓取间隔 | 数据源管理 + 配置编辑 |
| **Trading System** | 鲸鱼钱包 | 通知渠道、风控参数 | 钱包 CRUD + 地址验证 + 系统仪表盘 |
| **TrendRadar** | 监控平台 | 刷新频率、过滤规则 | 平台管理 + 热度阈值 |
| **GitHub Sentinel** | 监控仓库 | 分析频率、通知配置 | 仓库列表 + 告警规则 |

## 前后对比

| 维度 | 改前（硬编码 / ENV） | 改后（动态配置 + Dashboard） |
|------|---------------------|---------------------------|
| 修改配置 | 改 .env + 重新部署 (~5 min) | 点前端保存 (~5 sec) |
| 添加业务实体 | 改代码 + 提交 + 部署 | 前端表单填写即生效 |
| 配置追溯 | 看 .env 文件 | DB 有 updated_at 时间戳 |
| 多环境 | 每环境维护独立 .env | 同一份代码，DB 区分 |
| 状态监控 | 命令行查 DB / 看日志 | Dashboard 仪表盘一目了然 |

## Checklist：新项目接入

1. **定义 Settings**
   - [ ] 创建 `config.py` + Pydantic BaseSettings
   - [ ] 所有可变配置都给 Field default

2. **创建 DB 模型**
   - [ ] 添加 `SystemConfig` 表（通用键值对）
   - [ ] 添加业务实体表（如 `whale_wallets`、`data_sources`）
   - [ ] 实现 `init_db()` + seed 逻辑

3. **实现动态读取**
   - [ ] 创建 `get_dynamic_config()` 函数
   - [ ] 改造业务代码使用动态读取

4. **Admin API**
   - [ ] 配置 CRUD（GET / PUT）
   - [ ] 业务实体 CRUD（GET / POST / PUT / DELETE）
   - [ ] 系统状态端点

5. **Dashboard 前端**
   - [ ] 创建 `dashboard/` 目录
   - [ ] Tab 导航 + 各功能面板
   - [ ] FastAPI 静态文件挂载

## 注意事项

1. **类型安全**：DB 值统一存 Text，读取时做 `int()` / `float()` 转换，加 try/except 防御
2. **性能**：配置读取频率高时加内存缓存（TTL 30s），避免每次查 DB
3. **安全**：`is_secret` 字段标记敏感配置，前端展示脱敏
4. **Seed 幂等**：只在表为空时执行 seed，避免覆盖用户修改
5. **SQLAlchemy engine 延迟初始化**：避免在缺少 DB 驱动的环境（如测试）import 时报错
6. **ENV 是"出厂设置"**：首次部署时 `.env` 的值被 seed 到 DB，之后以 DB 为准