# Engineering Playbook

> 个人工程经验知识库 — 让每个新项目都站在过往经验的肩膀上。

## 解决什么问题

AI 助手是"失忆"的。每开一个新项目，它不知道你踩过什么坑、偏好什么架构、验证过哪些模式。

这个仓库把分散在各项目、各对话中的工程经验，**收敛为一套结构化、可检索、跨平台复用的知识体系**。目标是新项目中 60-70% 的技术决策来自历史沉淀，而非从零探索。

## 核心设计

```
                    engineering-playbook (GitHub)
    ┌──────────────────────────────────────────────────┐
    │                                                  │
    │  knowledge-base/    项目完整经验档案（按需引用）  │
    │  patterns/          可复用代码模式（跨项目通用）  │
    │  skills/            AI 协作工具集（18 + 5 个）    │
    │  project-rules/     项目精华 Rule（自动注入）     │
    │  templates/         经验文档生成模板              │
    │                                                  │
    └────────────────────┬─────────────────────────────┘
                         │ ./setup.sh (symlink)
                         ▼
              ~/.cursor/skills/  ←── 任意机器
              Cursor · CodeBuddy · CLI · 浏览器
```

**两层架构，各司其职**：

| 层级 | 载体 | 触发方式 | 信息密度 |
|------|------|---------|---------|
| 自动注入 | `project-rules/` → `.cursor/rules/` | 每次对话自动携带 | ≤ 200 行精华 |
| 按需查阅 | `knowledge-base/` + `patterns/` | `@` 引用或 Skill 检索 | 无限制，全部细节 |

## 快速开始

```bash
git clone https://github.com/yupeng0512/engineering-playbook.git ~/engineering-playbook
cd ~/engineering-playbook && ./setup.sh        # 安装（建立 symlink）
./setup.sh --status                            # 查看链接状态
./setup.sh --uninstall                         # 卸载
cd ~/engineering-playbook && git pull           # 更新（symlink 自动生效）
```

## 怎么用

| 场景 | 做法 |
|------|------|
| 新项目启动 | 对 AI 说 *"查看相关经验"*，或 `@knowledge-base/infohunter.md` 直接引用 |
| 解决具体问题 | `@patterns/dynamic-config.md` 引用可复用模式 |
| 项目复盘 | 对 AI 说 *"沉淀项目经验"*，自动生成精华 Rule + 完整档案 + Pattern |
| 换机器 / 换 IDE | `git clone` + `./setup.sh`，全部恢复 |

## 经验准入标准

每条经验必须满足**四有**，否则不入库：

- **有据可查** — 具体技术上下文，不是泛泛而谈
- **有理可论** — 有因果链：现象 → 根因 → 解决方案
- **有量可比** — 有前后对比数据
- **可复用** — 明确适用场景和注意事项

## 当前资产一览

| 类别 | 数量 | 内容 |
|------|------|------|
| 项目经验档案 | 3 | InfoHunter（AI 社交监控）、亲缘桥（投研/BP）、资产评估报告 |
| 可复用 Pattern | 5 | 动态配置串联、LLM JSON 清洗、幂等迁移、结构化 Prompt、仓库敏感信息防护 |
| 个人 Skills | 18 | 经验沉淀、AI 工作流、头脑风暴、深度防御、系统调试、TDD 测试、投研报告、执行计划、UI/UX 设计 等 |
| 系统 Skills | 5 | Cursor Rule/Skill/Subagent 创建、配置管理、架构迁移 |
| 项目 Rules | 9 | 4 个项目（InfoHunter / InfoHunter-Client / bk-sap-api / 亲缘桥） |
| 模板 | 3 | 精华 Rule、完整档案、资产评估 |

<details>
<summary>完整目录结构</summary>

```
engineering-playbook/
├── knowledge-base/
│   ├── infohunter.md
│   ├── qinyuanqiao-bp.md
│   └── asset-review-2026-02-25.md
├── patterns/
│   ├── dynamic-config.md
│   ├── llm-json-parser.md
│   ├── idempotent-migration.md
│   ├── structured-prompt-engineering.md
│   └── repo-secret-hygiene.md
├── skills/
│   ├── personal/  (18 个: ai-workflow, article-tutor, brainstorming,
│   │    command-creator, cybernetics-loop, defense-in-depth, gongfeng-mr,
│   │    investment-research-report, knowledge-base, project-retrospective,
│   │    share-writer, skill-from-masters, system-debugging, tech-review,
│   │    ui-ux-pro-max, unittest, writing-plans, yt-dlp)
│   └── cursor-system/  (5 个: create-rule, create-skill, create-subagent,
│        migrate-to-skills, update-cursor-settings)
├── project-rules/
│   ├── infohunter/          (1 rule)
│   ├── infohunter-client/   (3 rules)
│   ├── bk-sap-api/         (4 rules)
│   └── qinyuanqiao/        (1 rule)
├── templates/               (3 个模板)
├── setup.sh
└── README.md
```

</details>

## 贡献新经验

1. 在项目中说 *"沉淀项目经验"* → 自动生成精华 Rule + 完整档案
2. 从经验中提取通用 Pattern → `patterns/{name}.md`
3. `git add -A && git commit && git push`

## Changelog

| 日期 | 变更 |
|------|------|
| 2026-02-25 | 敏感信息审计 + 新增 `repo-secret-hygiene` Pattern |
| 2026-02-25 | 资产评估修复：C 级资产清零，精简冗余 Rule |
| 2026-02-25 | 合并 Mac 端：+8 Skill / +4 Rule / 投研报告案例入库 |
| 2026-02-25 | 初始化仓库：全量 Skills + InfoHunter 经验档案 + 4 Pattern |
