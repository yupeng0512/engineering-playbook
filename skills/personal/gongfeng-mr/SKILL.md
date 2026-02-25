---
name: gongfeng-mr
description: 工蜂 MR 提交助手。规范化 Git 提交流程：自动总结变更、生成 Commit Message、关联 TAPD 单据、创建 Merge Request。适用于需要提交代码到工蜂仓库并关联 TAPD 的场景。
---

# 工蜂 MR 提交助手

## 概述

规范化的工蜂 Merge Request 提交流程，解决以下痛点：
- Commit Message 不规范、信息不完整
- MR 未关联 TAPD 单据
- 变更内容未经确认就提交

## 核心能力

1. **变更分析**：自动获取 Git 变更，生成变更摘要
2. **Commit 规范**：按 Conventional Commits 规范生成 Message
3. **TAPD 关联**：支持关联已有单据或自动创建新单据
4. **MR 创建**：自动创建工蜂 MR，填充完整信息

## MCP 依赖

- `gongfengStreamable`：工蜂 Git 仓库操作（创建 MR、分支管理）
- `tapd_mcp_http`：TAPD 单据操作（创建/查询需求、任务、缺陷）

---

## 执行流程

### Phase 1: 变更分析与确认

**触发**：用户调用 `/gongfeng-mr` 或表达提交 MR 意图

**步骤**：

1. **获取 Git 状态**：
   ```bash
   cd {project_root} && git status --short
   ```

2. **获取变更详情**：
   ```bash
   cd {project_root} && git diff --stat
   cd {project_root} && git diff HEAD  # 或 git diff --cached（已暂存）
   ```

3. **生成变更摘要**，向用户确认：

   ```markdown
   ## 变更摘要
   
   ### 变更文件（共 N 个）
   | 状态 | 文件路径 | 变更行数 |
   |------|----------|----------|
   | M | src/api/user.py | +15 -3 |
   | A | src/utils/helper.py | +42 |
   | D | tests/old_test.py | -28 |
   
   ### 变更内容概述
   {根据 diff 内容总结核心变更}
   
   ### 建议 Commit Message
   ```
   {type}({scope}): {subject}
   
   {body}
   ```
   
   ---
   **请确认**：
   1. 以上变更是否都是本次提交需要的？
   2. Commit Message 是否准确描述了变更内容？
   
   回复「确认」继续，或提供修改意见。
   ```

**Commit Message 规范**（Conventional Commits）：

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat(user): add login API |
| `fix` | Bug 修复 | fix(auth): resolve token expiry issue |
| `docs` | 文档更新 | docs: update README |
| `style` | 代码格式（不影响逻辑） | style: format with black |
| `refactor` | 重构（不改功能） | refactor(db): extract query builder |
| `test` | 测试相关 | test: add user API tests |
| `chore` | 构建/工具变更 | chore: upgrade dependencies |

---

### Phase 2: TAPD 单据关联

**询问用户**：

```markdown
## TAPD 单据关联

本次提交需要关联 TAPD 单据。请选择：

1. **已有单据**：提供 TAPD 链接或单据 ID
   - 示例：https://tapd.woa.com/tapd_fe/123/story/detail/100000012345
   - 示例：story/100000012345 或 task/100000012345 或 bug/100000012345

2. **创建新单据**：我将根据变更内容自动创建
   - 需要提供：TAPD workspace_id（项目 ID）
   - 单据类型：需求(story) / 任务(task) / 缺陷(bug)

3. **跳过关联**：不关联 TAPD 单据（不推荐）

请选择（1/2/3）：
```

#### 选项1：关联已有单据

**解析 TAPD 链接**：
- 需求详情页：`https://tapd.woa.com/tapd_fe/{workspace_id}/story/detail/{story_id}`
- 任务详情页：`https://tapd.woa.com/tapd_fe/{workspace_id}/task/detail/{task_id}`
- 缺陷详情页：`https://tapd.woa.com/tapd_fe/{workspace_id}/bug/detail/{bug_id}`

**验证单据存在**：
- 调用 `tapd_mcp_http.stories_get` / `tasks_get` / `bugs_get` 验证
- 获取单据标题用于 MR 描述

#### 选项2：创建新单据

**获取 workspace_id**：
1. 询问用户提供
2. 或调用 `tapd_mcp_http.user_participant_workspace_get` 列出可选项目

**创建单据**：
- 根据 Phase 1 的变更摘要生成单据内容
- 调用对应 MCP 创建：
  - 需求：`tapd_mcp_http.stories_create`
  - 任务：`tapd_mcp_http.tasks_create`
  - 缺陷：`tapd_mcp_http.bugs_create`

**单据内容模板**：
```json
{
  "workspace_id": "{user_provided}",
  "name": "{从 commit message 提取}",
  "description": "{变更摘要 + 文件列表}"
}
```

**向用户确认创建结果**：
```markdown
## TAPD 单据已创建

- **类型**：{story/task/bug}
- **ID**：{tapd_id}
- **标题**：{name}
- **链接**：https://tapd.woa.com/tapd_fe/{workspace_id}/{type}/detail/{id}

继续创建 MR？
```

---

### Phase 3: Git 提交

**执行 Git 操作**：

```bash
cd {project_root}

# 1. 暂存变更
git add .  # 或用户指定的文件

# 2. 提交（用户确认的 commit message）
git commit -m "{commit_message}"

# 3. 推送到远程（如当前分支未推送）
git push origin {current_branch}
```

**错误处理**：
- 如果 push 失败（远程有更新），提示用户先 pull --rebase
- 如果认证失败，提示检查 Git 凭证配置

---

### Phase 4: 创建工蜂 MR

**询问目标分支**：

```markdown
## MR 目标分支

当前分支：`{current_branch}`

请选择合并目标分支：
1. `master` / `main`（默认）
2. `develop`
3. 其他（请输入分支名）

请选择或输入：
```

**获取工蜂项目信息**：

从 Git remote 解析项目路径：
```bash
git remote get-url origin
# 解析出：git@git.woa.com:group/project.git 或 https://git.woa.com/group/project.git
# 提取 project_id：group/project
```

**创建 MR**：

调用 `gongfengStreamable.create_merge_request`：

```json
{
  "project_id": "{group/project}",
  "source_branch": "{current_branch}",
  "target_branch": "{user_selected}",
  "title": "{commit_message_subject}",
  "description": "{MR 描述模板}",
  "tapd_info": "--{type}={tapd_id} {commit_message_subject}"
}
```

**MR 描述模板**：
```markdown
## 变更说明

{commit_message_body}

## 变更文件

{文件列表}

## 关联 TAPD

- [{type}#{tapd_short_id}] {tapd_title}
  - 链接：{tapd_url}
```

**TAPD 关联格式**（tapd_info 字段）：
- 需求：`--story={story_id} {描述}`
- 任务：`--task={task_id} {描述}`
- 缺陷：`--bug={bug_id} {描述}`

---

### Phase 5: 完成确认

**输出 MR 信息**：

```markdown
## MR 创建成功

- **MR 链接**：{mr_web_url}
- **标题**：{title}
- **源分支**：{source_branch} → **目标分支**：{target_branch}
- **TAPD 关联**：[{type}#{id}] {title}

### 后续操作
1. 在工蜂查看 MR 详情
2. 添加 Reviewer（如需要）
3. 等待 CI 检查通过
4. 合并 MR
```

---

## 快捷模式

如果用户在调用时提供了完整参数，可跳过交互步骤：

```
/gongfeng-mr --tapd=story/123456 --target=master
```

参数说明：
- `--tapd`：TAPD 单据（格式：type/id）
- `--target`：目标分支
- `--skip-confirm`：跳过变更确认（谨慎使用）

---

## 边缘情况处理

| 场景 | 处理方式 |
|------|----------|
| 无 Git 变更 | 提示用户没有需要提交的内容 |
| 当前在 master/main 分支 | 提示用户先创建功能分支 |
| 远程分支不存在 | 自动推送创建远程分支 |
| MR 已存在 | 提示用户已有相同分支的 MR，是否更新 |
| TAPD 单据不存在 | 提示用户检查 ID 或选择创建新单据 |
| Git push 失败 | 提示 pull --rebase 后重试 |
| MCP 调用失败 | 显示错误信息，提供手动操作指引 |

---

## 注意事项

1. **分支命名建议**：`feature/{tapd_type}-{tapd_id}-{brief_desc}`
   - 示例：`feature/story-123456-add-login`

2. **Commit Message 语言**：建议使用英文，保持一致性

3. **敏感信息检查**：提交前检查是否包含密钥、密码等敏感信息

4. **大文件警告**：如果变更包含大文件（>1MB），提醒用户确认

5. **Git 命令优先**：优先使用本地 git 命令操作，MCP 仅用于创建 MR 和 TAPD 单据
