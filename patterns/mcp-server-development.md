# MCP Server 开发模式

> 来源项目: TrendRadar、pinme-mcp、mcp_excalidraw、next-ai-draw-io、digital-twin、github-sentinel、mcp-gateway
> 沉淀时间: 2026-02-25

---

## 适用场景

开发 MCP (Model Context Protocol) Server，将服务/库/工具暴露给 AI 编辑器（Cursor / Claude Desktop / VS Code）。

---

## 核心模式

### 1. 三种 MCP Server 架构

| 架构 | 技术栈 | 典型项目 | 适用场景 |
|------|--------|---------|---------|
| **FastMCP (Python)** | FastMCP 2.0 + stdio/HTTP | TrendRadar | Python 后端服务，工具数量多 |
| **SDK 原生 (Node.js)** | @modelcontextprotocol/sdk + Express | pinme-mcp, next-ai-draw-io | Node.js 项目，需要自定义 HTTP Server |
| **Docker Wrapper** | Python MCP Server + docker exec stdio | digital-twin | 将无 MCP 支持的库包装为 MCP |

### 2. FastMCP 声明式注册（推荐）

```python
from fastmcp import FastMCP

mcp = FastMCP("service-name")

@mcp.tool()
async def query_data(keyword: str, limit: int = 10) -> str:
    """查询数据（描述会自动成为工具的 description）"""
    result = await service.query(keyword, limit)
    return json.dumps(result)
```

**优势**: 声明式、自动 schema 推断、内置错误处理
**注意**: 版本锁定很重要（如 `>=2.12.0, <2.14.0`），大版本间有 breaking change

### 3. SDK 原生模式 (Node.js)

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({ name: "service-name", version: "1.0.0" }, {
  capabilities: { tools: {} }
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{ name: "deploy", description: "...", inputSchema: {...} }]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  // 处理工具调用
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### 4. Docker Wrapper 模式

将无 MCP 支持的 Python 库包装为 MCP 工具：

```json
// cursor-mcp.json
{
  "mcpServers": {
    "service-name": {
      "command": "docker",
      "args": ["exec", "-i", "container-name", "python", "/app/server.py"]
    }
  }
}
```

**注意**: 如果 Docker 需要特定用户组权限，可用 `sg docker -c "docker exec -i ..."` 包裹（`sg` 是 Linux 的 `newgrp` 替代命令，临时切换用户组）。一般环境直接 `docker exec -i` 即可。

---

## 工具设计最佳实践

### 工具分类组织

当工具数量 > 10 时，按职责分文件：

```
tools/
├── data_query.py      # 数据查询类工具
├── analytics.py       # 分析类工具
├── search.py          # 搜索类工具
├── config_mgmt.py     # 配置管理类工具
├── system.py          # 系统管理类工具
└── notification.py    # 通知类工具
```

每个文件导出工具注册函数，主 server.py 统一注册。TrendRadar 用此模式管理 26 个工具。

### 工具命名规范

| 模式 | 示例 | 说明 |
|------|------|------|
| `动词_名词` | `query_data`, `create_diagram` | 操作类工具 |
| `get_名词` | `get_status`, `get_timeline` | 查询类工具 |
| `名词_动词` | `storage_sync`, `article_read` | 按领域分组 |

### 工具描述要点

- 描述是 LLM 判断何时调用工具的唯一依据，必须精确
- 包含参数含义和预期格式
- 标注返回值结构
- 说明调用前提条件（如"必须先调用 get_diagram"）

---

## MCP 网关模式

当有多个 MCP Server 需要统一暴露时，使用 Nginx 反向代理：

```nginx
upstream trendradar_mcp { server trendradar_mcp:3333; }
upstream pinme_mcp      { server pinme_mcp:3000; }

location /trendradar { proxy_pass http://trendradar_mcp; }
location /pinme      { proxy_pass http://pinme_mcp; }
```

**关键配置（SSE 兼容）**:
```nginx
proxy_buffering off;
chunked_transfer_encoding on;
proxy_set_header Connection '';
proxy_read_timeout 300s;
```

**注意**: 上游容器重启时网关返回 502，需要配置健康检查或自动重试。

---

## MCP + GUI 同步模式

当 MCP 工具需要操作 GUI 应用时（如 draw.io、Excalidraw）：

```
MCP stdio ←──→ 内嵌 HTTP Server ←──→ 浏览器 (轮询/WebSocket) ←──→ GUI iframe
```

关键实现：
1. MCP Server 启动时开启内嵌 HTTP Server（动态端口，如 6002-6020）
2. 浏览器端定期轮询（2s）或 WebSocket 获取状态更新
3. 通过 `postMessage` 与 GUI iframe 通信
4. `syncRequested` 标志实现服务端主动请求浏览器推送

---

## 常见踩坑

### 1. FastMCP 版本锁定

FastMCP 2.x 大版本间有 breaking change，务必在 requirements.txt 中锁定上下界：
```
fastmcp>=2.12.0,<2.14.0
```

### 2. stdio vs HTTP 模式选择

| 场景 | 推荐模式 | 原因 |
|------|---------|------|
| Cursor/Claude Desktop 本地 | stdio | 零配置，直接启动 |
| 远程服务/多用户 | HTTP (SSE) | 网络可达，可负载均衡 |
| Docker 容器内 | stdio + docker exec | 隔离性好 |

### 3. 工具返回值格式

MCP 工具返回值必须是**字符串**。复杂数据用 JSON 序列化：
```python
return json.dumps({"status": "ok", "data": result}, ensure_ascii=False)
```

### 4. 长耗时工具

MCP 协议无原生超时机制，长耗时工具需要：
- 服务端设置 reasonable timeout
- 返回进度信息而非等待完成
- 考虑异步 + 轮询模式

### 5. Docker 网络

Docker 内 MCP 服务使用 bridge 网络互联，不暴露端口到宿主机：
```yaml
services:
  mcp-server:
    networks: [mcp-network]
    # 不设置 ports，只在内部网络可达
```

---

## 前后对比

| 维度 | 无此 Pattern | 使用此 Pattern |
|------|-------------|---------------|
| MCP 框架选型 | 反复调研对比 | 按语言/场景直接选型 |
| 工具组织 | 全部堆在一个文件 | 分类分文件，清晰可维护 |
| 部署模式 | 试错 stdio/HTTP/Docker | 按场景表直接选择 |
| 多服务暴露 | 每个服务单独配置 | 统一 Nginx 网关 |

---

## 注意事项

1. MCP 协议仍在快速演进，关注 `@modelcontextprotocol/sdk` 和 `fastmcp` 的版本更新
2. 工具数量建议控制在 30 个以内，过多会影响 LLM 选择准确性
3. 每个工具的 description 是 LLM 选择依据，投入时间打磨
4. 生产环境推荐 HTTP 模式 + 认证，stdio 适合本地开发
