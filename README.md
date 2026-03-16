---
title: README
type: note
permalink: engineering-playbook/readme
---

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
    │  skills/            AI 协作工具集（26 + 5 个）    │
    │  judgment-cards/    判断力卡片精华库（跨领域通用）│
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
| 项目经验档案 | 12 | InfoHunter、InfoHunter-Client、bk-sap-api、TrendRadar、GitHub Sentinel、Digital Twin、AgentStudio、TruthSocial Monitor、Next AI Draw.io、亲缘桥、CLAWS 等 |
| 可复用 Pattern | 49 | 动态配置、MCP Server、Repo Secret Hygiene、Playwright ROI E2E、Adaptive Cell Workflow、Bounded Autonomy、Docker/Traefik 路由、Agent 性能优化 等 |
| 判断力卡片 | 10 | Agent 架构选型、简单性优先、上下文有限、工具设计优先、角色转变、止损优先、经济周期、身份元认知 等 |
| 个人 Skills | 26 | 经验沉淀、判断力锻造、AI Workflow、Adaptive Cell Workflow、Bounded Autonomy、头脑风暴、系统调试、TDD 测试、投研报告、UI/UX 等 |
| 系统 Skills | 5 | Cursor Rule/Skill/Subagent 创建、配置管理、架构迁移 |
| 项目 Rules | 9 | 4 个项目（InfoHunter / InfoHunter-Client / bk-sap-api / 亲缘桥） |
| 模板资产 | 2 组 | `adaptive-cell-workflow`、`autonomy-contract` 两套可安装模板 |

<details>
<summary>完整目录结构</summary>

```
engineering-playbook/
├── knowledge-base/              (12 份项目/主题档案)
│   ├── infohunter.md
│   ├── trendradar.md
│   ├── github-sentinel.md
│   ├── digital-twin.md
│   ├── claws.md
│   └── ...
├── judgment-cards/              (10 张判断力卡片)
│   ├── README.md
│   ├── arch-agent-architecture-selection.md
│   ├── arch-simplicity-over-complexity.md
│   ├── arch-context-is-finite-resource.md
│   ├── arch-tool-design-over-prompt.md
│   ├── arch-vibe-engineering-role-shift.md
│   ├── eng-research-before-solving.md
│   ├── meta-identity-shapes-action.md
│   ├── risk-stop-loss-first.md
│   └── risk-economic-cycle-decision.md
├── docs/
│   └── qinyuanqiao-bp.md      (商业计划书，非技术经验)
├── patterns/                    (49 个跨项目 Pattern)
│   ├── dynamic-config.md
│   ├── mcp-server-development.md
│   ├── adaptive-cell-workflow.md
│   ├── bounded-autonomy-repo-contract.md
│   ├── playwright-roi-e2e-sop.md
│   └── ...
├── skills/
│   ├── personal/  (26 个: ai-workflow, adaptive-cell-workflow, article-tutor,
│   │    bounded-autonomy, brainstorming, command-creator, cybernetics-loop,
│   │    defense-in-depth, gongfeng-mr, investment-research-report,
│   │    judgment-forge, knowledge-base, md2deck, playbook-onboarding,
│   │    project-retrospective, share-writer, skill-from-masters,
│   │    slidev-pitch-deck, slidev-presentation, stagehand-automation,
│   │    system-debugging, tech-review, ui-ux-pro-max, unittest,
│   │    writing-plans, yt-dlp)
│   └── cursor-system/  (5 个: create-rule, create-skill, create-subagent,
│        migrate-to-skills, update-cursor-settings)
├── project-rules/
│   ├── infohunter/          (1 rule)
│   ├── infohunter-client/   (3 rules)
│   ├── bk-sap-api/         (4 rules)
│   └── qinyuanqiao/        (1 rule)
├── templates/               (2 组项目模板)
│   ├── adaptive-cell-workflow/
│   └── autonomy-contract/
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
| 2026-03-16 | 知识图谱 metadata 规范化（frontmatter + permalink）+ 新增 Adaptive Cell Workflow / Bounded Autonomy 资产包 + README 索引刷新 |
| 2026-02-26 | 新增 stagehand-automation Skill + stagehand-browser-automation Pattern：代码+AI 混合浏览器自动化 |
| 2026-02-25 | 判断力锻造：新增 judgment-forge Skill + 3 张判断力卡片 + judgment-index 自进化索引 |
| 2026-02-25 | 新增 slidev-presentation + slidev-pitch-deck Skill：Markdown → Slidev 交互式演示文稿 |
| 2026-02-25 | 门控审核 + 批量沉淀：10 经验档案 / 8 Pattern / 20 Skills / 安全修复 / 质量把关 |
| 2026-02-25 | 初始化仓库：Skills + Rules + Pattern + InfoHunter 首份档案 + md2deck |
