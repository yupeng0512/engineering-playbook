# Engineering Playbook

> 个人工程经验知识库 — 让每个新项目都站在过往经验的肩膀上。

## 为什么需要这个仓库

每次启动新项目时，AI 助手都是"失忆"的——不知道你踩过什么坑、偏好什么架构、用过哪些验证过的模式。这个仓库解决的核心问题是：

**将分散在各项目、各对话中的工程经验，收敛为一套结构化、可检索、跨平台复用的知识体系。**

目标：新项目中 60-70% 的技术决策来自历史沉淀，而非从零探索。

## 架构总览

```
┌────────────────────────────────────────────────────────────┐
│                  engineering-playbook (GitHub)              │
│                                                            │
│  ┌─────────────┐  ┌──────────┐  ┌────────────────────┐    │
│  │ knowledge-   │  │ patterns/│  │ skills/            │    │
│  │ base/        │  │          │  │ ├── personal/      │    │
│  │ 项目完整档案 │  │ 可复用   │  │ │   11 个 AI 协作  │    │
│  │              │  │ 代码模式 │  │ │   工具           │    │
│  │ - infohunter │  │          │  │ └── cursor-system/ │    │
│  │ - ...更多项目│  │ 4 个独立 │  │     5 个系统级     │    │
│  └──────────────┘  │ pattern  │  │     Skills         │    │
│                    └──────────┘  └────────────────────┘    │
│  ┌──────────────┐  ┌──────────┐                            │
│  │ project-     │  │templates/│                            │
│  │ rules/       │  │ 经验文档 │                            │
│  │ 3 个项目精华 │  │ 生成模板 │                            │
│  │ 经验 Rule    │  └──────────┘                            │
│  └──────────────┘                                          │
└────────────────────────────────────────────────────────────┘
            │                             │
            │ ./setup.sh                  │ git clone
            ▼                             ▼
  ┌──────────────────┐          ┌──────────────────┐
  │ Linux / Mac      │          │ 其他机器         │
  │ ~/.cursor/skills/│◄─symlink─│ ~/.cursor/skills/│
  │                  │          │                  │
  │ Cursor / VS Code │          │ CodeBuddy / CLI  │
  └──────────────────┘          └──────────────────┘
```

## 仓库结构

```
engineering-playbook/
│
├── knowledge-base/                # 📚 项目经验完整档案（按需引用）
│   ├── infohunter.md                # InfoHunter: AI 社交监控 — 完整经验
│   └── infohunter-memory-pending.json  # 待写入语义记忆的条目
│
├── patterns/                      # 🔧 可复用代码模式（独立于项目）
│   ├── dynamic-config.md            # 动态配置串联（env → DB → API → UI）
│   ├── llm-json-parser.md           # LLM JSON 多层清洗（5 层 fallback）
│   ├── idempotent-migration.md      # 幂等数据库迁移（免 Alembic 方案）
│   └── structured-prompt-engineering.md  # 结构化 Prompt 工程（6 模块模板）
│
├── skills/                        # 🤖 AI 协作工具集
│   ├── personal/                    # 个人 Skills（11 个）
│   │   ├── project-retrospective.md   # ★ 经验沉淀与复用（核心 Skill）
│   │   ├── article-tutor/             # 文章/书籍精读教学
│   │   ├── command-creator/           # Command/Skill 创建向导
│   │   ├── cybernetics-loop/          # 控制论反馈系统设计
│   │   ├── frontend-design/           # 前端 UI 设计
│   │   ├── gongfeng-mr/               # 工蜂 MR 提交（Git + TAPD 关联）
│   │   ├── share-writer/              # 团队分享文章编写
│   │   ├── skill-from-masters/        # 从专家方法论创建 Skill
│   │   ├── tech-review/               # 技术架构评审
│   │   ├── ui-ux-pro-max/             # UI/UX 设计（57 种风格 + 8 框架）
│   │   └── yt-dlp/                    # 视频下载助手
│   └── cursor-system/               # Cursor 系统级 Skills（5 个）
│       ├── create-rule/               # 创建 Cursor Rule
│       ├── create-skill/              # 创建 Cursor Skill
│       ├── create-subagent/           # 创建子 Agent
│       ├── migrate-to-skills/         # 迁移到 Skills 架构
│       └── update-cursor-settings/    # 更新 Cursor/VS Code 设置
│
├── project-rules/                 # 📋 各项目精华经验 Rule（auto-apply）
│   ├── infohunter/                  # lessons-learned.mdc
│   ├── infohunter-client/           # project-overview, mobile-dev, security
│   └── bk-sap-api/                  # django, flake8
│
├── templates/                     # 📝 经验文档生成模板
│   ├── lessons-learned.mdc.tmpl     # 精华版 Rule 模板（≤200 行）
│   └── full-retrospective.md.tmpl   # 完整版档案模板（无限制）
│
├── setup.sh                       # ⚡ 一键安装（建立 symlink）
└── README.md
```

## 快速开始

### 1. 克隆仓库

```bash
# Linux（开发机）
git clone https://github.com/yupeng0512/engineering-playbook.git ~/engineering-playbook

# Mac（本地）
git clone https://github.com/yupeng0512/engineering-playbook.git ~/engineering-playbook
```

### 2. 安装（建立 symlink）

```bash
cd ~/engineering-playbook
chmod +x setup.sh
./setup.sh
```

安装脚本会自动：
- 将 `skills/personal/*` 链接到 `~/.cursor/skills/`
- 将 `skills/cursor-system/*` 链接到 `~/.cursor/skills-cursor/`
- 如果本地已有同名 skill 目录，先备份为 `*.local-backup`

### 3. 卸载

```bash
./setup.sh --uninstall
```

### 4. 更新

```bash
cd ~/engineering-playbook && git pull
# symlink 自动指向最新内容，无需重新安装
```

## 使用场景

### 场景一：新项目启动，查阅历史经验

在 Cursor 中对 AI 说：

> "我要做一个 XX 项目，查看相关经验"

AI 会触发 `project-retrospective` Skill 的**查询模式**，搜索 `knowledge-base/` 和 `patterns/` 中的相关经验。

也可以直接引用：

```
@knowledge-base/infohunter.md 这个项目的动态配置是怎么做的？
@patterns/dynamic-config.md 我想在新项目中用这个模式
```

### 场景二：项目完成后，沉淀经验

在 Cursor 中对 AI 说：

> "沉淀这个项目的经验"

AI 会触发 `project-retrospective` Skill 的**生成模式**，自动收集项目信息、引导补充、生成三份产出：

| 产出 | 路径 | 用途 |
|------|------|------|
| 精华版 Rule | `{project}/.cursor/rules/lessons-learned.mdc` | 自动注入每次对话（≤200 行） |
| 完整版档案 | `knowledge-base/{project}.md` | 按需引用的详细档案 |
| 可复用 Pattern | `patterns/{name}.md` | 跨项目通用的代码模式 |

### 场景三：跨平台复用

本仓库不依赖任何特定 IDE，核心内容全部是 Markdown：

| 平台 | 使用方式 |
|------|---------|
| **Cursor** | `./setup.sh` 建立 symlink，自动加载 Skills |
| **CodeBuddy** | 直接 `@` 引用仓库中的 Markdown 文件 |
| **命令行 AI** | 将文件内容作为上下文传入 |
| **浏览器** | 在 GitHub 上直接阅读 |

## 经验质量标准

每条纳入知识库的经验必须满足**四有标准**：

| 标准 | 说明 | 反面案例 |
|------|------|---------|
| **有据可查** | 包含具体技术上下文和数据 | ❌ "遇到了一个 bug，后来修好了" |
| **有理可论** | 有因果链（现象 → 根因 → 解决方案） | ❌ "用了 React，挺好用的" |
| **有量可比** | 有前后对比数据 | ❌ "架构做了重构"（无新旧对比） |
| **可复用** | 明确适用场景和注意事项 | ❌ 只有结论没有上下文 |

不满足以上标准的经验不纳入知识库。

## 核心概念

### 经验的两层架构

```
自动注入层（精华版 Rule）
├── 载体: .cursor/rules/lessons-learned.mdc
├── 触发: alwaysApply: true（每次对话自动携带）
├── 密度: ≤ 200 行精华摘要
└── 场景: 同项目日常迭代

按需查阅层（完整版档案 + 可复用 Pattern）
├── 载体: knowledge-base/{project}.md + patterns/*.md
├── 触发: 手动 @ 引用 或 Skill 检索
├── 密度: 无限制，包含所有细节
└── 场景: 新项目启动 / 跨项目参考
```

### Pattern vs Knowledge Base

| 维度 | Pattern | Knowledge Base |
|------|---------|---------------|
| **粒度** | 单个可复用模式 | 整个项目的完整经验 |
| **独立性** | 脱离项目上下文可理解 | 需要了解项目背景 |
| **示例** | "动态配置串联" | "InfoHunter 完整经验档案" |
| **适用** | 解决某个具体技术问题 | 启动同领域新项目时整体参考 |

## 当前资产统计

| 类别 | 数量 | 说明 |
|------|------|------|
| 项目经验档案 | 1 | InfoHunter |
| 可复用 Pattern | 4 | 动态配置、LLM JSON 清洗、幂等迁移、结构化 Prompt |
| 个人 Skills | 11 | 覆盖经验沉淀、文章精读、前端设计、代码审查等 |
| 系统 Skills | 5 | Cursor 平台级能力 |
| 项目 Rules | 6 | 来自 3 个项目 |

## 贡献新经验

### 添加新项目经验

1. 在对应项目中运行 `project-retrospective` Skill 生成经验文档
2. 将完整档案放到 `knowledge-base/{project}.md`
3. 将精华 Rule 放到 `project-rules/{project}/lessons-learned.mdc`
4. 从经验中提取通用 Pattern 放到 `patterns/`
5. 提交到 GitHub：`git add -A && git commit -m "feat: add {project} experience" && git push`

### 添加新 Skill

1. 在 `skills/personal/{skill-name}/` 下创建 `SKILL.md`
2. 运行 `./setup.sh` 建立 symlink
3. 提交到 GitHub

## Changelog

| 日期 | 变更 |
|------|------|
| 2026-02-25 | 初始化仓库：迁移全量 Skills + 创建 InfoHunter 经验档案 + 提取 4 个 Pattern |
