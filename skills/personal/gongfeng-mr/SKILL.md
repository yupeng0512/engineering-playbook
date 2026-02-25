---
name: gongfeng-mr
description: 工蜂 MR 提交助手。当用户表达"提交代码"、"创建 MR"、"提 MR"、"push 代码"、"合并请求"、"关联 TAPD"、"commit"、"提交到工蜂"、"代码审查"、"code review"、"自检"等意图时触发。自动总结变更、生成规范 Commit Message、关联 TAPD 单据、创建 Merge Request，并提供 Code Review 自检清单。
---

# 工蜂 MR 提交助手

## 概述

规范化的工蜂 Merge Request 提交流程，核心价值：
- 自动分析变更，生成符合 Conventional Commits 规范的 Message（中文描述）
- 自动关联或创建 TAPD 单据（支持需求/任务/缺陷）
- Commit 和 MR 同时关联 TAPD（通过 `--story=xxx` 关键字）
- **提交前强制 Code Review 自检**，提高代码质量
- 一键创建工蜂 MR，填充完整信息

## MCP 依赖

- `gongfengStreamable`：工蜂 Git 仓库操作（创建 MR、分支管理）
- `tapd_mcp_http`：TAPD 单据操作（创建/查询需求、任务、缺陷）

---

## 0. Code Review 自检（提交前强制）

### 0.1 自检核心原则

**提交前必须通过 Code Review 自检**，确保代码质量达标。

```
┌─────────────────────────────────────────────────────────────────┐
│                    提交前自检流程                                │
├─────────────────────────────────────────────────────────────────┤
│  📋 功能检查  →  🔍 代码质量  →  🛡️ 安全检查  →  ✅ 确认提交  │
│  功能完整？      代码规范？       有漏洞？         可以提交     │
└─────────────────────────────────────────────────────────────────┘
```

### 0.2 Code Review 检查清单

在创建 MR 前，必须完成以下自检项目：

#### 📋 功能完整性检查

| 检查项 | 说明 | 状态 |
|--------|------|------|
| 需求实现 | 所有需求点都已实现 | [ ] |
| 边界处理 | 边界条件和异常场景已处理 | [ ] |
| 向后兼容 | 不破坏现有功能和接口 | [ ] |
| 单元测试 | 新增/修改代码有对应测试 | [ ] |
| 测试通过 | 本地测试全部通过 | [ ] |

#### 🔍 代码质量检查

| 检查项 | 说明 | 状态 |
|--------|------|------|
| 命名规范 | 变量、函数、类命名清晰且符合规范 | [ ] |
| 代码风格 | 遵循项目编码规范（PEP8/Flake8） | [ ] |
| 注释完整 | 关键逻辑有注释，docstring 完整 | [ ] |
| 类型注解 | 函数参数和返回值有类型注解 | [ ] |
| 无硬编码 | 无魔法数字，使用常量或枚举 | [ ] |
| 无重复代码 | 重复逻辑已抽取为公共方法 | [ ] |
| 无死代码 | 删除无用的代码和注释 | [ ] |

#### ⚡ 性能检查

| 检查项 | 说明 | 状态 |
|--------|------|------|
| N+1 查询 | 无 N+1 查询问题（使用 select_related/prefetch_related） | [ ] |
| 批量操作 | 循环中的数据库操作已优化为批量 | [ ] |
| 缓存使用 | 频繁访问的数据使用缓存 | [ ] |
| 查询优化 | 复杂查询有索引支持 | [ ] |

#### 🛡️ 安全检查

| 检查项 | 说明 | 状态 |
|--------|------|------|
| 敏感信息 | 无硬编码的密钥、密码、Token | [ ] |
| SQL 注入 | 使用 ORM 或参数化查询 | [ ] |
| XSS 防护 | 用户输入已转义 | [ ] |
| 权限验证 | 接口有权限校验 | [ ] |
| 输入校验 | 用户输入有校验和清理 | [ ] |

#### 📝 文档与日志

| 检查项 | 说明 | 状态 |
|--------|------|------|
| API 文档 | 新增/修改的 API 有文档说明 | [ ] |
| 变更记录 | 重大变更有记录 | [ ] |
| 日志完善 | 关键操作有日志记录 | [ ] |
| 错误信息 | 错误信息清晰可排查 | [ ] |

### 0.3 自检执行流程

**提交代码时自动执行**：

1. **分析变更文件**：识别修改的文件类型和范围
2. **生成检查报告**：根据变更生成针对性的检查项
3. **确认自检结果**：用户确认已完成自检
4. **继续提交流程**：通过自检后才能创建 MR

### 0.4 检查报告模板

```markdown
## 🔍 Code Review 自检报告

### 变更概览
- 修改文件数：{count} 个
- 新增行数：{additions}
- 删除行数：{deletions}

### 必检项目

#### 功能检查
- [ ] ✅ 需求点都已实现
- [ ] ✅ 边界条件已处理
- [ ] ✅ 单元测试已编写并通过

#### 代码质量
- [ ] ✅ 代码符合规范（Flake8 无报错）
- [ ] ✅ 类型注解完整
- [ ] ✅ 无重复/死代码

#### 安全检查
- [ ] ✅ 无敏感信息硬编码
- [ ] ✅ 输入已校验

### 自检结论
{通过/需要修改}

---
确认以上自检已完成？
```

---

## 执行流程

### Phase 0: Code Review 自检（新增）

**触发**：用户调用 `/gongfeng-mr` 或表达提交意图

**步骤**：

1. **获取变更详情**
2. **生成自检清单**
3. **用户确认自检结果**
4. 自检通过后进入 Phase 1

### Phase 1: 信息收集

**触发**：用户调用 `/gongfeng-mr` 或表达提交意图

**步骤**：

1. **获取项目信息**：
   ```bash
   git remote get-url origin    # 解析 project_id
   git branch --show-current    # 当前分支
   ```

2. **获取变更详情**：
   ```bash
   git status --short
   git log -1 --oneline         # 最新提交
   git diff --stat              # 变更统计
   git diff HEAD                # 或 git diff --cached
   ```

3. **解析 project_id**：
   - SSH 格式：`git@<GIT_HOST>:GROUP/PROJECT.git` → `GROUP/PROJECT`
   - HTTPS 格式：`https://<GIT_HOST>/GROUP/PROJECT.git` → `GROUP/PROJECT`

---

### Phase 2: TAPD 单据处理

**确认用户 TAPD 情况**（必须询问）：

| 情况 | 处理流程 |
|------|----------|
| **已有单据** | 用户提供链接或 ID → 验证存在 → 获取 19 位 ID |
| **需要创建** | 获取 workspace_id → 根据变更生成描述 → 创建单据 |
| **跳过关联** | 不推荐，仅限临时/紧急提交 |

**获取 workspace_id 策略**：
1. 用户直接提供
2. 调用 `user_participant_workspace_get` 获取用户参与的项目列表
3. 根据项目名称匹配（需用户确认）

**创建 TAPD 单据**：
```
调用对应 MCP：
- 需求：tapd_mcp_http.stories_create
- 任务：tapd_mcp_http.tasks_create  
- 缺陷：tapd_mcp_http.bugs_create

参数：
- workspace_id: 项目 ID
- name/title: 根据变更内容生成的标题（中文）
- description: 变更说明、影响范围
```

**TAPD 关联格式**（用于 Commit Message 和 MR）：
```
--story={19位ID}     # 关联需求
--task={19位ID}      # 关联任务
--bug={19位ID}       # 关联缺陷
```

---

### Phase 3: 生成 Commit Message

**格式规范**：
```
{type}({scope}): {中文描述}

{可选的详细说明}

{TAPD关联信息}
```

**type 类型**：
| type | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 Bug |
| docs | 文档变更 |
| style | 代码格式（不影响功能） |
| refactor | 重构（非新功能/非修复） |
| test | 测试相关 |
| chore | 构建/工具/依赖变更 |

**示例**：
```
feat(codebuddy): 新增 Command/Skill 创建专家和工蜂 MR 助手技能包

--story=<TAPD_STORY_ID> 新增 CodeBuddy 技能包
```

**关键规则**：
- ⚠️ **描述必须使用中文**
- TAPD 关联信息放在 commit message 中，工蜂会自动识别并关联

---

### Phase 4: Git 提交与推送

**向用户确认**后执行：
```bash
git add .                      # 或指定文件
git commit -m "{commit_message}"
git push origin {branch}
```

**错误处理**：
| 错误 | 解决方案 |
|------|----------|
| push 被拒绝 | 提示 `git pull --rebase` 后重试 |
| 认证失败 | 提示检查 Git 凭证配置 |
| 分支保护 | 提示需要通过 MR 合并 |

---

### Phase 5: 创建工蜂 MR

**收集信息**：
1. 目标分支（用户指定，常用：`master`、`main`、`v3_dev`）
2. MR 标题（使用 Commit Message 的 subject）

**调用 MCP**：`gongfengStreamable.create_merge_request`

```json
{
  "project_id": "{GROUP/PROJECT}",
  "source_branch": "{current_branch}",
  "target_branch": "{target}",
  "title": "{type}({scope}): {中文描述}",
  "description": "## 变更说明\n{详细描述}\n\n## 变更文件\n{file_table}\n\n## Code Review 自检\n{checklist}\n\n## 关联 TAPD\n{tapd_link}",
  "tapd_info": "--{type}={tapd_id} {中文描述}"
}
```

**description 模板**（增强版）：
```markdown
## 变更说明
{根据 diff 生成的变更概述}

## 变更文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `path/to/file1` | 新增/修改/删除 | 说明 |
| `path/to/file2` | 新增/修改/删除 | 说明 |

## Code Review 自检

### 功能检查
- [x] 需求点都已实现
- [x] 边界条件已处理
- [x] 单元测试已编写并通过

### 代码质量
- [x] 代码符合规范
- [x] 类型注解完整

### 安全检查
- [x] 无敏感信息硬编码
- [x] 输入已校验

## 关联 TAPD
- {类型}：{TAPD链接}
```

---

### Phase 6: 完成确认

**输出结果摘要**：
```
## ✅ 提交完成

### Code Review 自检
| 类别 | 状态 |
|------|------|
| 功能检查 | ✅ 通过 |
| 代码质量 | ✅ 通过 |
| 安全检查 | ✅ 通过 |

### TAPD 单据
| 项目 | 详情 |
|------|------|
| 类型 | {需求/任务/缺陷} |
| ID | {tapd_id} |
| 标题 | {title} |
| 链接 | {url} |

### 工蜂 MR
| 项目 | 详情 |
|------|------|
| MR ID | !{iid} |
| 标题 | {title} |
| 分支 | {source} → {target} |
| 状态 | {merge_status} |
| 链接 | {url} |

### 后续操作
1. 添加 Reviewer
2. 等待 CI 检查
3. 审查通过后合并
```

---

## 完整流程示例

**场景**：用户完成代码变更，需要提交并关联 TAPD

```
用户: 帮我提交代码并创建 MR，目标分支 v3_dev

AI执行:
0. 🔍 Code Review 自检
   - 分析变更文件
   - 生成自检清单
   - 用户确认自检结果
1. 获取 git 状态和变更
2. 询问："是否已有 TAPD 单据？"
   - 若无 → 获取 workspace_id → 创建 TAPD 需求
   - 若有 → 验证单据存在
3. 生成 Commit Message（中文描述 + TAPD 关联）
4. 确认后执行 git add/commit/push
5. 创建工蜂 MR（描述中包含 Code Review 自检清单 + TAPD 链接）
6. 输出结果摘要
```

---

## 边缘情况处理

| 场景 | 处理 |
|------|------|
| 无 Git 变更 | 提示没有需要提交的内容 |
| 当前在 master/main | 提示先创建功能分支 |
| 远程分支不存在 | 自动 push 创建 |
| MR 已存在 | 提示更新现有 MR 或返回链接 |
| TAPD 单据不存在 | 提示创建或检查 ID |
| workspace_id 未知 | 调用 API 获取用户项目列表 |
| MCP 调用失败 | 显示错误，提供手动操作指引 |
| **自检未通过** | 阻止提交，提示修复问题 |

---

## 注意事项

1. **提交前必须完成 Code Review 自检**
2. **Commit Message 使用中文描述**（type 和 scope 保持英文）
3. **TAPD 关联信息**同时放入 Commit Message 和 MR 的 `tapd_info` 字段
4. **先创建 TAPD 再提交**：确保 commit 可以通过 `--story=xxx` 关联
5. **敏感信息检查**：提交前检查是否包含密钥、密码
6. **大文件警告**：变更包含 >1MB 文件时提醒

---

## 快速命令

```bash
# 查看变更状态
git status --short

# 查看变更详情
git diff --stat

# 运行代码检查
.venv/py310/bin/python -m flake8 {changed_files}

# 运行单元测试
.venv/py310/bin/python tests/pytest_main.py unit --modules {module}
```
