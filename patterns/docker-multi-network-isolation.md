---
title: Docker 多网络服务隔离
type: pattern
tags:
- docker
- networking
- traefik
- architecture
- security
permalink: engineering-playbook/patterns/docker-multi-network-isolation
---

# Pattern: Docker 多网络服务隔离

> 适用场景：使用 Traefik 等反向代理时，后端服务需要正常访问外部 HTTPS API（如 Resend、OpenAI、Stripe 等）。

## 问题

容器同时连接 `traefik-net`（反向代理网络）和内部网络时，出站 HTTPS 请求可能被 Traefik 拦截，导致 TLS 握手失败（`wrong version number`）。

Docker 多网络容器的默认网关选择不可控：
- 网络连接顺序不确定默认网关
- `priority` 字段在不同 Docker 版本行为不一致
- 硬编码 `dns` 在换服务器后失效

## 正确架构

只让面向用户的入口容器连接 `traefik-net`，后端服务仅使用内部网络。

```
                    ┌─── traefik-net ───┐
                    │                   │
                 Traefik              web
                    │              (桥接点)
                    │                   │
                    └───────────────────┘
                                        │
                    ┌─── internal ──────┤
                    │                   │
                   api              ai-service
                    │
              ┌─────┼─────┐
           postgres redis  ...
```

### 关键原则

1. **单一入口**：web 是唯一连接 `traefik-net` 的业务容器
2. **内部代理**：API 调用通过 web 的 rewrite/proxy 间接暴露（如 Next.js rewrites、Nginx proxy_pass）
3. **出站安全**：后端容器只在内部 bridge 网络上，出站走宿主机默认网关，HTTPS 天然正常

## 实施

### docker-compose.yml

```yaml
services:
  api:
    build: ./api
    # 无 traefik labels — 不直接暴露
    networks:
      - internal

  ai-service:
    build: ./ai-service
    # 无 traefik labels
    networks:
      - internal

  web:
    build: ./web
    environment:
      API_INTERNAL_URL: http://api:8080        # 内部 DNS
      AI_INTERNAL_URL: http://ai-service:8000
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.web.rule=Host(`app.dev.local`)"
      - "traefik.http.services.web.loadbalancer.server.port=3000"
    networks:
      - internal
      - traefik-net    # 唯一桥接

  postgres:
    networks: [internal]

  redis:
    networks: [internal]

networks:
  internal:
    driver: bridge
  traefik-net:
    name: traefik-net
    external: true
```

### 前端代理配置（Next.js 示例）

```typescript
// next.config.ts
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_INTERNAL_URL}/api/:path*`,
      },
    ];
  },
};
```

> **注意**：`API_INTERNAL_URL` 必须作为 Docker build arg 传入，因为 Next.js rewrites 在构建时编译。

## 反模式

### 1. 所有服务都连 traefik-net

```yaml
# ❌ 后端容器出站 HTTPS 可能被 Traefik 拦截
services:
  api:
    networks: [internal, traefik-net]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.app.dev.local`)"
```

### 2. 用 DNS 或 priority 绕过

```yaml
# ❌ Workaround：换服务器就挂，不可移植
services:
  api:
    dns: [8.8.8.8]           # 可能被防火墙拦截
    networks:
      internal:
        priority: 1000       # 行为不可靠
      traefik-net:
        priority: 100
```

### 3. 自定义 HTTP Transport

```go
// ❌ 侵入业务代码，第三方 SDK 可能不支持自定义 client
client := &http.Client{
    Transport: &http.Transport{
        DialContext: customDialer,
    },
}
```

## 检查清单

- [ ] 后端服务（API、AI、Worker）仅连接内部网络
- [ ] 只有面向用户的入口（web / nginx）连接 `traefik-net`
- [ ] API 调用通过 web 的 rewrite 或 proxy 暴露
- [ ] `API_INTERNAL_URL` 作为 build arg 和 runtime env 双重传入
- [ ] 验证：`docker inspect <api> --format '{{json .NetworkSettings.Networks}}'` 只有内部网络
- [ ] 验证：`docker exec <api> wget -q -O /dev/null https://api.resend.com` HTTPS 出站正常

## 适用范围

| 适用 | 不适用 |
|------|--------|
| Traefik + 微服务 | 单容器应用 |
| 后端需调用外部 API | 纯内网无出站需求 |
| 多服务 Docker Compose | K8s（Ingress 机制不同） |

## 源自项目

- TradeRadar：Go API 调用 Resend 邮件 API 时发现 TLS 被 Traefik 拦截
