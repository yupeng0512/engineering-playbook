# Pattern: 幂等数据库迁移

> 来源项目: InfoHunter | 推荐指数: 4/5 | 适用范围: 小型项目不需要 Alembic 完整迁移链

## 适用场景

- 项目规模较小（< 20 张表），不需要 Alembic 的完整迁移管理
- 需要安全地给已有表新增字段
- 部署时自动执行迁移，不需要手动操作

## 核心实现

```python
from sqlalchemy import text, inspect

def _run_migrations(self) -> None:
    """幂等数据库迁移 — 检查后再 ALTER，支持重复执行"""
    inspector = inspect(self.engine)
    table_names = inspector.get_table_names()

    if "contents" in table_names:
        columns = {c["name"] for c in inspector.get_columns("contents")}

        # 新增字段：检查不存在后再 ALTER
        if "ai_analysis_retries" not in columns:
            try:
                with self.engine.begin() as conn:
                    conn.execute(text(
                        "ALTER TABLE contents "
                        "ADD COLUMN ai_analysis_retries INT NOT NULL DEFAULT 0"
                    ))
                logger.info("迁移: contents 新增 ai_analysis_retries 列")
            except Exception as e:
                logger.warning(f"迁移失败 (可能已完成): {e}")

        # 扩展字段长度
        content_id_col = {c["name"]: c for c in inspector.get_columns("contents")}.get("content_id")
        if content_id_col and getattr(content_id_col["type"], "length", 0) < 512:
            try:
                with self.engine.begin() as conn:
                    conn.execute(text(
                        "ALTER TABLE contents MODIFY COLUMN content_id VARCHAR(512) NOT NULL"
                    ))
                logger.info("迁移: content_id 扩展到 VARCHAR(512)")
            except Exception as e:
                logger.warning(f"迁移失败 (可能已完成): {e}")
```

### 调用时机

```python
def init_db(self) -> None:
    """初始化数据库表"""
    Base.metadata.create_all(bind=self.engine)  # 新表自动创建
    self._run_migrations()                       # 增量字段迁移
```

## 与 Alembic 的 trade-off

| 维度 | 幂等迁移 | Alembic |
|------|---------|---------|
| 复杂度 | 低（几十行代码） | 高（需要配置、生成脚本、管理版本链） |
| 回滚支持 | 无 | 有（downgrade） |
| 迁移历史 | 无记录 | 完整版本链 |
| 多人协作 | 可能冲突 | 有序管理 |
| 适用规模 | < 20 表 | 任意规模 |

## 使用注意事项

1. 每个迁移操作必须幂等（先检查再执行）
2. 使用 `try/except` + warning 日志，不要因为迁移失败阻塞启动
3. 当项目规模增长到需要回滚或多人协作时，应迁移到 Alembic
4. 注意不同数据库的 DDL 语法差异（MySQL vs PostgreSQL）
