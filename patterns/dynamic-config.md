# Pattern: 动态配置串联

> 来源项目: InfoHunter | 推荐指数: 5/5 | 适用范围: 任何需要运行时可调配置的 Python 后端

## 适用场景

- 配置项需要在不重启服务的情况下动态调整
- 需要提供 Web UI 让运维/用户修改配置
- 需要 env 默认值 + 用户自定义覆盖的优先级机制

## 核心实现

### 三级配置链

```
.env 文件 → pydantic BaseSettings（类型安全默认值）
    ↓
system_config DB 表（用户运行时修改）
    ↓
@property dynamic_xxx（封装优先级逻辑）
    ↓
API 端点（读写 DB）→ 前端表单
```

### 关键代码模式

```python
# 1. pydantic Settings 定义默认值
class Settings(BaseSettings):
    analysis_batch_size: int = Field(default=20, description="每轮分析条数")

# 2. system_config 表（通用 JSON 存储）
class SystemConfig(Base):
    key: str          # 配置键名，如 "ai_config"
    value: dict       # JSON 值，如 {"batch_size": 15, "max_retries": 5}
    description: str

# 3. 核心读取方法
def _get_db_config(self, key: str) -> Optional[dict]:
    """从 system_config 表读取配置，带缓存"""
    with self.db.get_session() as session:
        cfg = session.execute(
            select(SystemConfig).where(SystemConfig.key == key)
        ).scalar_one_or_none()
        return cfg.value if cfg else None

# 4. Dynamic 属性封装优先级
@property
def dynamic_analysis_batch_size(self) -> int:
    cfg = self._get_db_config("ai_config")
    if cfg and cfg.get("batch_size") is not None:
        try:
            return int(cfg["batch_size"])
        except (ValueError, TypeError):
            pass
    return settings.analysis_batch_size  # fallback 到 env
```

### 前端联动

```javascript
// 加载时：先从 /api/stats 读当前值，再从 /api/config 读 DB 覆盖值
// 保存时：PUT /api/config/{key} 写入 DB
await put('ai_config', {
    batch_size: parseInt(el.value) || 20,
}, 'AI 分析配置');
```

## 前后对比

| 维度 | 改前（硬编码/env） | 改后（动态配置） |
|------|-------------------|-----------------|
| 修改配置 | 改 .env + 重新部署（~5 min） | 点前端保存（~5 sec） |
| 配置追溯 | 看 .env 文件 | DB 有记录 + 前端可视化 |
| 多环境 | 每个环境维护独立 .env | 同一份代码，DB 区分 |

## 使用注意事项

1. DB 值类型是 JSON，取出后需要 `int()` / `float()` 转换，加 try/except 防御
2. 配置读取频率高的话考虑加内存缓存（TTL 30s），避免每次都查 DB
3. env 应该只做"首次启动 seed value"，用户修改后以 DB 为准
