# Pattern: 项目上下文管理

> 来源: trading-system, claws, infohunter, digital-twin 多项目实践总结
> 创建: 2026-03-01

## 问题

AI Agent 在新 session 中缺乏项目上下文，导致重复劳动、错误决策。
项目缺少统一的上下文文件组织方式，导致知识碎片化。

## 解决方案

### 1. 项目上下文文件清单

每个项目仓库应包含以下上下文文件：

| 文件/目录 | 用途 | 写入模式 | 优先级 |
|-----------|------|----------|--------|
| `NOW.md` | 项目当前状态板 | 覆写 | P0 |
| `AGENTS.md` | Agent 行为规范 | 极少修改 | P0 |
| `.cursor/rules/*.md` | 自动注入的开发规范 | 极少修改 | P0 |
| `.cursor/plans/` | 实施计划与路线图 | 按阶段更新 | P1 |
| `docs/api-reference/` | 外部 API 速查表 | 按需更新 | P1 |
| `docs/guides/env-setup.md` | 环境变量获取指引 | 按需更新 | P1 |
| `.env.example` | 环境变量模板 | 随代码更新 | P0 |

### 2. API 文档存储规范

**原则**: 精准 API 速查表（~2-3KB）优于完整官方文档（-2.9pp 通过率）。

```
docs/
├── api-reference/
│   ├── polymarket-api.md     # 速查表：端点 + 认证 + 常用调用
│   ├── tradingview-webhook.md
│   └── ...
└── guides/
    ├── env-setup.md           # 傻瓜式环境变量获取指引
    └── deployment.md
```

速查表内容模板：
- 认证方式（1-2 段）
- 常用端点表（按使用频率排列）
- 代码示例（最简可运行）
- 关键限制（rate limit, 费率等）
- 官方文档链接（用于深入查阅）

### 3. 环境变量指引规范

`.env.example` + `docs/guides/env-setup.md` 配合使用：

- `.env.example`: 列出所有变量及默认值，简短注释
- `env-setup.md`: 每个变量的分步获取指引，包含：
  - 在哪个平台/页面获取
  - 具体操作步骤（截图级别的文字描述）
  - 安全注意事项
  - 按 Phase/优先级分组

### 4. Session 生命周期

```
SessionStart:
  1. 读 NOW.md（当前状态）
  2. 读 AGENTS.md（行为规范）
  3. .cursor/rules/ 自动注入

PreCompact:
  1. 更新 NOW.md
  2. 确保重要决策已记录

SessionEnd:
  1. 更新 NOW.md
  2. 写入 memory 日志
```

## 适用场景

- 新项目初始化时建立完整的上下文文件
- 已有项目的上下文文件补全
- 团队成员（包括 AI Agent）onboarding

## 反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| 把完整官方文档复制到仓库 | 上下文膨胀，命中率降低 | 写精准速查表 |
| 环境变量只写在 README | 散落、不易维护 | 集中到 `env-setup.md` |
| 没有 NOW.md | Agent 每次冷启动 | 覆写式状态板 |
| 所有上下文放 .cursor/rules/ | 超出 200 行限制 | 分层：rules 精华，docs 详细 |

## 检查清单

- [ ] `NOW.md` 存在且反映最新状态
- [ ] `AGENTS.md` 存在且定义了开发规范
- [ ] `.cursor/rules/` 不超过 200 行
- [ ] `.env.example` 覆盖所有环境变量
- [ ] `docs/guides/env-setup.md` 提供分步获取指引
- [ ] `docs/api-reference/` 存放关键 API 速查表
- [ ] `.gitignore` 排除 `.env` 和敏感文件
- [ ] `.cursor/plans/` 包含当前实施计划
