# Digital Twin 完整经验档案

> 项目周期: 2025 ~ 进行中
> 最后更新: 2026-02-25
> 状态: v1.0 Production Ready

---

## 项目概要

| 维度 | 说明 |
|------|------|
| **类型** | 知识图谱记忆管理平台 |
| **领域** | AI / 知识图谱 / 个人记忆 |
| **规模** | ~2K 行 Python + 6 个 Cursor Skills + Docker 5 服务 |
| **核心价值** | 让 AI 拥有长期记忆和关系推理能力 |

### 核心技术栈

| 层级 | 技术 | 版本 | 备注 |
|------|------|------|------|
| 记忆框架 | Graphiti (by Zep) | ≥0.3.0 | 时序知识图谱核心引擎 |
| 图数据库 | Neo4j Community | 5.26 | GDS 插件启用 |
| LLM 推理 | 智谱 GLM-4-Plus | API | 实体提取/关系推理 |
| Embedding | 智谱 embedding-3 | API | 2048 维向量 |
| 笔记 | Joplin Server | latest | Markdown 持久化 |
| 笔记 DB | PostgreSQL | 16 | Joplin 后端 |
| 内容生成 | Open-Notebook | v1-latest-single | AI 播客/学习指南 |
| 协议 | MCP | ≥0.9.0 | Cursor 集成 |
| 部署 | Docker Compose | 5 服务 | |

### 架构概览

```
用户 (Cursor) → 6 个 Skills (记录/查询/复盘/目标/习惯/同步)
    │
    ▼
Graphiti MCP Server (4 个工具: add_memory/search/timeline/related)
    │
    ├──→ LLM (智谱 GLM-4) → 实体提取 + 关系推理
    │
    ├──→ Neo4j (Entity + Episode + Relationship 图谱)
    │
    ├──→ Joplin Server → 笔记备份 → GitHub Actions → GitHub
    │
    └──→ Open-Notebook → AI 播客 / 学习指南 / FAQ
```

---

## 做得好的地方

### 技术选型

#### Graphiti vs Mem0 (最关键的选型决策)

- **技术**: Graphiti + Neo4j
- **考虑过的备选**: Mem0 (23k stars)
- **选择理由**:
  - Graphiti 有原生时序推理（理解"学 Python → 用 Flask → 优化性能"的递进关系）
  - 图原生关系提取，不是模糊的向量相似度
  - Neo4j Browser 直接可视化知识网络
  - Mem0 缺乏关系推理和时序感知，无法回答"我 1 月学了什么？"
- **实际效果**: 能做到跨会话关联、时间线复盘、深度关系查询
- **推荐指数**: 4/5（部署复杂度高于 Mem0）
- **适用建议**: 需要关系推理和时序感知的场景选 Graphiti；只需简单记忆检索选 Mem0
- **Trade-off**: Graphiti 部署需 Neo4j（2G heap + 1G pagecache），资源消耗显著高于 Mem0

#### 智谱 GLM-4 适配

- **技术**: 自建 ZhipuClient 适配 Graphiti
- **场景**: 国产 LLM 替代 OpenAI 做知识图谱实体提取
- **选择理由**: 国内网络稳定 + 中文理解优秀 + 价格合理
- **实际效果**: 成功运行，但需要自建适配层处理 json_schema vs json_object 差异
- **推荐指数**: 4/5
- **适用建议**: 需要结构化输出（json_schema）的场景优先选 Qwen（通义千问），智谱需自建适配

#### Open-Notebook vs NotebookLM

- **最终选择**: Open-Notebook（100% 本地部署）
- **放弃 NotebookLM**: 数据在 Google、非官方 API 不稳定
- **推荐指数**: 4/5
- **适用建议**: 隐私敏感场景用 Open-Notebook，不在意隐私用 NotebookLM

### 架构设计

#### 多 LLM 提供商策略模式

- **解决的问题**: 不同场景/预算需要切换 LLM 提供商
- **实现方式**: 环境变量 `LLM_PROVIDER` → 策略选择 → 每个提供商封装为 Client + Embedder + Reranker 三元组
- **支持提供商**: Qwen / Zhipu / Gemini / OpenAI / Deepseek / Ollama(本地)
- **可复用程度**: 高
- **复用注意事项**: 每个提供商的结构化输出能力不同，需要测试 json_schema 兼容性

#### MCP Server Wrapper 模式

- **解决的问题**: Graphiti 库无原生 MCP 支持，需要暴露给 Cursor
- **实现方式**: Python MCP Server 包装 Graphiti API，通过 Docker + stdio 暴露
- **接入方式**: `sg docker -c "docker exec -i {container} python /app/server.py"`
- **可复用程度**: 高
- **复用注意事项**: 适用于任何需要将 Python 库包装为 MCP 工具的场景

#### 双写存储 + 三层备份

- **解决的问题**: 知识图谱数据安全
- **实现方式**: Graphiti(图谱推理) + Joplin(结构化笔记) + GitHub(版本备份)
- **CI/CD**: GitHub Actions 每日凌晨 2 点自动同步 Joplin → GitHub
- **可复用程度**: 中
- **复用注意事项**: 三层备份增加维护复杂度，需确保数据一致性

#### Cursor Skills 渐进式披露

- **解决的问题**: 单个 Skill 文档过长，用户难以入手
- **实现方式**: 每个 Skill 三层文档 — SKILL.md(Quick Start) + examples.md(对话示例) + reference.md(高级用法)
- **可复用程度**: 高
- **复用注意事项**: 这是 engineering-playbook 中 Skills 编写的参考模式

---

## 做得不好的地方

### 踩坑清单

#### 坑 1: LLM 结构化输出兼容性 (最大坑)

- **影响程度**: 高
- **耗时**: 约 2 天
- **现象**: Graphiti 使用 `json_schema` 模式做实体提取，智谱 API 报错
- **排查过程**:
  1. 发现 Graphiti 内部硬编码 `response_format: { type: "json_schema", schema: ... }`
  2. 智谱 API 只支持 `json_object` 模式
  3. Deepseek 同样不支持 json_schema，排除
  4. 最终方案：自建 ZhipuClient 继承 OpenAIGenericClient，拦截请求
- **根因**: Graphiti 假设所有 LLM 都支持 OpenAI 的 json_schema 格式
- **解决方案**: ZhipuClient 将 json_schema 转为 json_object，并将 schema 注入 system prompt
- **预防建议**: 集成第三方 AI 框架前，先测试目标 LLM 的结构化输出能力

#### 坑 2: 智谱 API 返回格式不稳定

- **影响程度**: 中
- **现象**: 智谱有时返回 `[{...}]`（列表）而非 `{...}`（对象）
- **根因**: 智谱在某些 prompt 下倾向于返回列表格式
- **解决方案**: ZhipuClient 中增加 list-to-dict 转换逻辑
- **预防建议**: AI API 返回值永远做防御性解析，不要假设格式

#### 坑 3: Docker 权限问题

- **影响程度**: 中
- **现象**: 标准 `docker exec` 命令无法执行
- **根因**: 服务器 Docker 通过安全组（sg）管理权限
- **解决方案**: 使用 `sg docker -c "docker exec ..."` 包装
- **预防建议**: Docker 权限管理方式因环境而异，MCP 配置需针对具体部署环境调整

#### 坑 4: Joplin Server 安全漏洞

- **影响程度**: 中
- **现象**: 安全扫描发现 pdfjs-dist 有漏洞
- **根因**: Joplin Server 官方镜像依赖的 pdfjs-dist 版本过旧
- **解决方案**: 自建 Dockerfile 基于官方镜像升级 pdfjs-dist
- **预防建议**: 使用第三方 Docker 镜像前做安全扫描

### 决策失误

#### 失误 1: 智谱 vs Qwen 的选择

- **当时的决策**: 使用智谱 GLM-4 作为默认 LLM
- **当时的理由**: 智谱中文理解优秀
- **为什么错了**: Qwen（通义千问）完全支持 json_schema，无需自建适配层
- **正确做法**: 应该先测试各家 LLM 的 json_schema 支持情况再选型
- **代价**: 额外花了 2 天开发 ZhipuClient 适配层

---

## 可复用资产

### 代码模式

- **多 LLM 提供商策略**: `graphiti-mcp-server/server.py` — 环境变量驱动的 LLM 切换
- **ZhipuClient 适配器**: `graphiti-mcp-server/zhipu_client.py` — json_schema → json_object 转换
- **MCP Server Wrapper**: 将任意 Python 库包装为 MCP 工具的模式
- **Skills 渐进式披露**: SKILL.md + examples.md + reference.md 三层结构

### 配置模板

- **Docker Compose 5 服务**: Neo4j + MCP + Joplin + PostgreSQL + Open-Notebook
- **`.env.example` (212 行)**: 极其详细的配置模板，包含各 LLM 提供商对比

---

## 给未来自己的建议

### 如果重新做这个项目

1. 先测试各 LLM 的 json_schema 支持，选 Qwen 而非智谱
2. Neo4j 资源配置从小开始（512M heap），按需扩容，不要一开始就 2G
3. MCP Server 考虑 HTTP 模式而非 stdio + docker exec，部署更灵活

### 延伸到其他项目的通用建议

- **LLM 结构化输出**: 集成前必须验证目标 LLM 的 json_schema / json_object / function calling 支持
- **知识图谱选型**: 需要关系推理选 Graphiti/Neo4j，只需检索选 Mem0/Chroma
- **MCP Wrapper**: 任何 Python 库都可以通过 MCP Server Wrapper 暴露给 AI 编辑器

---

## 元数据

- **沉淀时间**: 2026-02-25
- **信息来源**: 代码分析 / README / Git log / docs/ 目录 / 归档文档
- **覆盖度评估**: 约 85%。遗漏：(1) Open-Notebook 的具体集成细节 (2) NotebookLM 远程桥接的完整实现 (3) 各 Skill 的使用频率和效果数据
