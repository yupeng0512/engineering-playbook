# Pattern: Token 效率优先的工具选择

> 来源项目: ops-dashboard | 推荐指数: 4/5 | 适用范围: 所有 AI 辅助开发场景（Cursor / Copilot 等）

## 适用场景

- AI Agent 需要执行 Git 操作（提交、推送、创建仓库等）
- AI Agent 需要操作文件系统（读取、写入、搜索等）
- 存在多种工具可以完成同一任务时的选择决策

## 问题根因

AI Agent 在选择工具时，容易"就近"使用看起来功能最匹配的 API，而忽略了 token 开销。典型案例：

**反面案例**：使用 GitHub MCP `push_files` 推送代码到 GitHub
1. 先用 Read 工具逐一读取 13 个文件的全部内容 → 消耗大量 input token
2. 将所有文件内容作为 `push_files` 的参数传入 → 消耗大量 output token
3. 总计浪费数万 token，而 `git push` 只需一行命令

**正面案例**：用 `git push` 命令推送
1. `git remote add origin <url>` → 几十个 token
2. `git push -u origin main` → 几十个 token
3. 总计 ≈ 100 token，完成同样的事

## 核心原则

**能用轻量命令完成的事，不要用重量级 API。**

选择工具时，按以下优先级排序：

1. **Shell 命令**（token 开销最低）：命令本身只有几十个 token
2. **专用工具**（如 Read / Write / Grep）：按需传输，开销可控
3. **MCP API**（按需使用）：参数可能很大，开销不可控

## 决策矩阵

### Git / GitHub 操作

| 任务 | 推荐方式 | 避免方式 | 原因 |
|------|----------|----------|------|
| 创建远程仓库 | `create_repository` MCP | 手动去网页创建 | 只传仓库名+描述，开销极小 |
| 推送代码 | `git push` 命令 | `push_files` MCP | push_files 需传入每个文件内容 |
| 提交代码 | `git add && git commit` | 无替代 | 标准操作 |
| 查看 diff | `git diff` 命令 | 逐文件 Read 后对比 | diff 输出精准且紧凑 |
| 查看历史 | `git log` 命令 | 无替代 | 标准操作 |
| 查看文件列表 | `git ls-files` 命令 | 多层 Glob 搜索 | 一步到位 |

### 文件操作

| 任务 | 推荐方式 | 避免方式 | 原因 |
|------|----------|----------|------|
| 搜索文本 | Grep 工具 | Shell `grep/rg` | Grep 工具已优化，输出更可控 |
| 查找文件 | Glob 工具 | Shell `find` | Glob 更快，格式更规范 |
| 读取文件 | Read 工具 | Shell `cat` | Read 带行号，支持 offset/limit |
| 编辑文件 | StrReplace 工具 | Shell `sed/awk` | StrReplace 精准替换，不易出错 |
| 批量重命名 | Shell `mv` 命令 | 逐一 Read + Write | 命令行批量操作更高效 |

### 判断标准

遇到工具选择时，问自己两个问题：

1. **这个操作需要传输文件内容吗？** 如果需要，优先找不传内容的替代方案
2. **有没有等效的一行命令？** 如果有，用命令而非 API

## 推广到其他场景

此原则不仅限于 Git 操作，同样适用于：

- **数据库操作**：能用 SQL 命令就不要逐行读取再拼接
- **Docker 操作**：`docker logs/exec/cp` 优于通过 API 获取
- **文件打包**：`tar/zip` 命令优于逐文件读取再组装
- **信息查询**：`curl` 一行命令优于多步 MCP 调用

## 使用注意事项

1. **MCP 不是不能用**：创建仓库、查询 PR 状态等低开销操作完全合理
2. **命令行不是万能的**：需要结构化输出时（如 JSON 解析），专用工具更合适
3. **安全性考量**：涉及密钥的操作，MCP 可能比明文命令更安全
4. **可用性前提**：如果环境中没有 git（如纯浏览器 IDE），那 MCP 是唯一选择
