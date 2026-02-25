# Engineering Playbook

个人工程经验知识库 — 跨项目、跨平台的技术决策、踩坑记录、可复用模式和 AI 协作工具集。

## 目标

让 AI 协作者在新项目中不再"失忆"，携带过往项目的经验沉淀工作。确保 60-70% 的技术决策来自历史沉淀，而非每次从零探索。

## 仓库结构

```
engineering-playbook/
├── knowledge-base/            # 项目经验完整档案
│   └── infohunter.md            # InfoHunter 完整经验
├── patterns/                  # 可复用代码模式（独立提取）
│   ├── dynamic-config.md        # 动态配置串联
│   ├── llm-json-parser.md       # LLM JSON 清洗
│   ├── idempotent-migration.md  # 幂等数据库迁移
│   └── structured-prompt-engineering.md  # 结构化 Prompt 工程
├── skills/                    # AI 协作工具集
│   ├── personal/                # 个人 Skills
│   │   ├── project-retrospective.md  # 经验沉淀与复用
│   │   ├── article-tutor/       # 文章精读教学
│   │   ├── command-creator/     # Command/Skill 创建
│   │   ├── cybernetics-loop/    # 控制论反馈系统
│   │   ├── frontend-design/     # 前端设计
│   │   ├── gongfeng-mr/         # 工蜂 MR 提交
│   │   ├── share-writer/        # 分享文章编写
│   │   ├── skill-from-masters/  # 从专家方法论创建 Skill
│   │   ├── tech-review/         # 技术架构评审
│   │   ├── ui-ux-pro-max/       # UI/UX 设计
│   │   └── yt-dlp/              # 视频下载
│   └── cursor-system/           # Cursor 系统级 Skills
│       ├── create-rule/         # 创建 Cursor Rule
│       ├── create-skill/        # 创建 Cursor Skill
│       ├── create-subagent/     # 创建子 Agent
│       ├── migrate-to-skills/   # 迁移到 Skills
│       └── update-cursor-settings/  # 更新 Cursor 设置
├── project-rules/             # 各项目的精华经验 Rule
│   ├── infohunter/
│   ├── infohunter-client/
│   └── bk-sap-api/
├── templates/                 # 结构化模板
│   ├── lessons-learned.mdc.tmpl
│   └── full-retrospective.md.tmpl
├── setup.sh                   # 一键安装脚本
└── README.md
```

## 快速开始

### 安装（建立 symlink）

```bash
git clone <repo-url> ~/engineering-playbook
cd ~/engineering-playbook
chmod +x setup.sh
./setup.sh
```

### 使用方式

| 场景 | 方法 |
|------|------|
| **新项目启动** | 在 Cursor 中说"查看相关经验"触发查询模式 |
| **项目完成后** | 在 Cursor 中说"沉淀项目经验"触发生成模式 |
| **引用 pattern** | `@patterns/dynamic-config.md` |
| **引用完整档案** | `@knowledge-base/infohunter.md` |
| **跨平台使用** | 直接阅读 Markdown 文件，不依赖任何 IDE |

## 经验质量标准

每条经验条目必须满足：

1. **有据可查**: 包含具体的技术上下文和数据
2. **有理可论**: 有因果链（现象 → 根因 → 解决方案）
3. **有量可比**: 有前后对比数据（性能提升 X%、时间节省 Y 分钟）
4. **可复用**: 明确适用场景和注意事项

不满足以上标准的经验不纳入知识库。
