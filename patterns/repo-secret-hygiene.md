---
title: repo-secret-hygiene
type: note
permalink: engineering-playbook/patterns/repo-secret-hygiene
---

# Pattern: 仓库敏感信息防护

> 来源项目: engineering-playbook | 推荐指数: 5/5 | 适用范围: 任何公开或共享的代码仓库

## 适用场景

- 将内部项目经验、Skills、配置模板等资产开源或跨团队共享
- 代码仓库中包含示例、文档、配置模板
- 从私有仓库迁移内容到公开仓库

## 问题根因

敏感信息泄露往往不是故意的，而是在以下场景中"顺手"带入：

1. **文档中的真实示例**：`git@git.internal-domain.com:team/project.git`
2. **配置文件中的默认值**：`API_KEY=sk-real-key-here`
3. **脚本中的硬编码路径**：`/data/home/username/.cursor/skills/...`
4. **示例代码中的真实 ID**：`--story=1070059632130300616`
5. **user_id / 邮箱等个人标识符**
6. **内部域名**（暴露组织架构和基础设施信息）

## 核心实现

### 审计清单（提交前必检）

```
敏感信息类型           示例                           替换为
────────────────────────────────────────────────────────────────
API Key / Token        sk-abc123...                   <YOUR_API_KEY>
内部域名               git.woa.com, *.oa.com          <GIT_HOST>
数据库连接串            mysql://user:pass@host/db      <DATABASE_URL>
服务器绝对路径          /data/home/username/...        ~/...
内部系统 ID            story=107005963213...           <TAPD_STORY_ID>
Webhook URL            hooks.feishu.cn/xxx            <WEBHOOK_URL>
个人邮箱/手机           user@company.com               <EMAIL>
IP 地址                10.0.1.100:8080                <INTERNAL_IP>
```

### 自动化检测（Git pre-commit hook）

```bash
#!/bin/bash
# .git/hooks/pre-commit — 敏感信息检测

PATTERNS=(
    'sk-[a-zA-Z0-9]{20,}'       # OpenAI API Key
    'ghp_[a-zA-Z0-9]{36}'       # GitHub Personal Token
    'AKIA[0-9A-Z]{16}'          # AWS Access Key
    'xoxb-'                      # Slack Bot Token
    '\.woa\.com'                 # 内部域名
    '\.oa\.com'                  # 内部域名
    'password\s*=\s*["\x27][^"]+' # 硬编码密码
)

FOUND=0
for pattern in "${PATTERNS[@]}"; do
    matches=$(git diff --cached --diff-filter=ACM -G "$pattern" --name-only)
    if [ -n "$matches" ]; then
        echo "⚠️  疑似敏感信息 ($pattern):"
        echo "$matches" | sed 's/^/   /'
        FOUND=1
    fi
done

if [ $FOUND -eq 1 ]; then
    echo ""
    echo "请检查以上文件，确认无敏感信息后执行: git commit --no-verify"
    exit 1
fi
```

### 占位符规范

使用统一的占位符格式，便于用户识别和全局替换：

```
格式：<UPPER_SNAKE_CASE>

示例：
  <YOUR_API_KEY>        — 用户需要填入自己的 API Key
  <GIT_HOST>            — 替换为实际 Git 服务域名
  <DATABASE_URL>        — 替换为实际数据库连接串
  <TAPD_STORY_ID>       — 替换为实际 TAPD 单据 ID
  <YOUR_USER_ID>        — 替换为实际用户 ID
  <WEBHOOK_URL>         — 替换为实际 Webhook 地址
```

### .gitignore 防护

```gitignore
# 敏感文件
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json
service-account.json

# IDE 可能缓存的凭据
.vscode/settings.json
.idea/
```

## 前后对比（来自 engineering-playbook 实际案例）

| 文件 | 泄露内容 | 修复后 |
|------|---------|--------|
| gongfeng-mr/SKILL.md | `git@git.woa.com:GROUP/PROJECT.git` | `git@<GIT_HOST>:GROUP/PROJECT.git` |
| gongfeng-mr/SKILL.md | `--story=1070059632130300616` | `--story=<TAPD_STORY_ID>` |
| ui-ux-pro-max/SKILL.md | `/data/home/archerpyu/.cursor/skills/...` | `~/.cursor/skills/...` |
| infohunter-memory-pending.json | `"user_id": "archerpyu"` | `"user_id": "<YOUR_USER_ID>"` |
| project-retrospective.md | `user_id: archerpyu` | `user_id: <YOUR_USER_ID>` |

## 使用注意事项

1. **提交前审计是最后一道防线**：`git diff --cached` 查看即将提交的所有变更
2. **内部域名是高危项**：域名暴露组织结构、基础设施信息，且不易被常规检测发现
3. **示例代码也要脱敏**：即使是"教学用途"的代码，如果包含真实 ID 也必须替换
4. **git 历史不可逆**：一旦提交到远端，即使后续删除也可能已被 fork 或缓存
5. **定期 review**：每次大批量合并后，跑一次全量敏感信息扫描（参考上方审计清单）

## 推荐工具

| 工具 | 说明 |
|------|------|
| `git-secrets` | AWS 出品的 pre-commit hook，可自定义模式 |
| `trufflehog` | 扫描 git 历史中的高熵字符串和已知 key 格式 |
| `gitleaks` | CI/CD 集成友好的 secret 检测工具 |
| `detect-secrets` | Yelp 出品，支持 baseline 文件减少误报 |