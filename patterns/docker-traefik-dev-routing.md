---
title: docker-traefik-dev-routing
type: note
permalink: engineering-playbook/patterns/docker-traefik-dev-routing
---

# Pattern: Docker + Traefik 开发环境域名路由

> 适用场景：在 Linux 开发机上部署多个 Docker 服务，通过域名统一访问，支持远程 Mac 开发。

## 问题

多个 Docker 服务各占不同端口（6001, 7001, 8000, 9090...），记忆负担大且端口冲突频发。
远程开发时（Mac → Linux），需要同时访问多个服务的前端和 API。

## 解决方案

```
Mac 浏览器
  │ http://trading.dev.local  （hosts → Linux IP）
  ▼
Linux Traefik (:80)
  │ 按 Host header 路由
  ├─ trading.dev.local    → trading-api:7001
  ├─ ops.dev.local        → ops-dashboard:9090
  ├─ sentinel.dev.local   → sentinel-frontend:80
  └─ ...
```

## 实施步骤

### 1. Traefik 基础设施（一次性）

```yaml
# infrastructure/docker-compose.yml
services:
  traefik:
    image: traefik:v3.0
    command:
      - "--api.dashboard=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    ports:
      - "${HOST_IP}:80:80"
      - "${HOST_IP}:8181:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - traefik-net

networks:
  traefik-net:
    external: true
```

```bash
docker network create traefik-net
docker compose up -d
```

### 2. 服务接入（每个项目）

在项目的 `docker-compose.yml` 中添加 Traefik labels：

```yaml
services:
  api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.myproject.rule=Host(`myproject.dev.local`)"
      - "traefik.http.routers.myproject.entrypoints=web"
      - "traefik.http.services.myproject.loadbalancer.server.port=8000"
    networks:
      - traefik-net
      - internal

networks:
  traefik-net:
    external: true
  internal:
    driver: bridge
```

关键点：
- **不暴露端口**：去掉 `ports` 映射，流量全走 Traefik
- **双网络**：`traefik-net`（外部路由） + `internal`（DB/Redis 内部通信）
- **router 名称唯一**：每个服务的 router 名不能重复
- **⚠️ 多网络陷阱**：只让入口容器连 `traefik-net`，后端服务仅用内部网络，否则 HTTPS 出站可能被 Traefik 拦截 → 详见 [[docker-multi-network-isolation]]

### 3. Mac hosts 配置

```bash
# 查看现有配置
grep "dev.local" /etc/hosts

# 追加新域名（替换 IP 为实际 Linux 机器 IP）
echo "9.135.86.144 trading.dev.local" | sudo tee -a /etc/hosts
```

批量添加（新项目接入时）：
```bash
sudo tee -a /etc/hosts <<'EOF'
9.135.86.144 myproject.dev.local
EOF
```

### 4. 前端根路由

确保 FastAPI 服务在 `/` 路径返回前端页面（redirect 或直接 serve）：

```python
# 方式 A：重定向到 dashboard
@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")

# 方式 B：直接返回 index.html（参考 ops-dashboard）
@app.get("/")
async def root():
    return FileResponse("static/index.html")
```

### 5. 端口注册表（可选但推荐）

维护一份 `infrastructure/ports-registry.yaml`，记录所有服务的域名映射：

```yaml
routes:
  - domain: myproject.dev.local
    service: myproject-api
    container_port: 8000
    status: active
```

纯文档用途，不参与自动化配置，方便查阅全景。

## Checklist：新项目接入

- [ ] `docker-compose.yml` 添加 Traefik labels
- [ ] 加入 `traefik-net` 外部网络
- [ ] 去掉不必要的 `ports` 直接映射
- [ ] FastAPI `@app.get("/")` 返回前端页面
- [ ] Mac `/etc/hosts` 追加域名
- [ ] `ports-registry.yaml` 注册新路由
- [ ] 浏览器验证 `http://xxx.dev.local/`

## 踩坑记录

### 1. Traefik 返回 404 但 labels 正确
容器 healthcheck 未通过时，Traefik 不会将流量转发到该容器。等 `(healthy)` 状态后再测试。

### 2. curl 127.0.0.1 不通但 IP 可通
Traefik 绑定到 `${HOST_IP}:80` 而非 `0.0.0.0:80`，本机 curl 需用实际 IP。

### 3. 重建容器后访问不通
`docker compose up -d --force-recreate` 后需等待 healthcheck interval（通常 10-30 秒）。

## 实际项目参考

| 项目 | 域名 | 前端方式 |
|------|------|---------|
| ops-dashboard | ops.dev.local | FastAPI mount `/static` + `@get("/")` |
| infohunter | infohunter.dev.local | FastAPI mount `src/web/` + `@get("/")` |
| github-sentinel | sentinel.dev.local | 独立 nginx 容器（前端构建产物） |
| trading-system | trading.dev.local | FastAPI `@get("/")` → redirect `/dashboard` |
| claws | claws.dev.local | FastAPI `@get("/")` → redirect `/dashboard` |