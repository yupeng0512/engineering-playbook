---
title: 交付验证前重启服务（使最新变更生效）
category: ops
tags:
  - docker
  - handoff
  - verification
  - deployment
created: 2026-03-12
project: trade-radar
permalink: engineering-playbook/patterns/handoff-verify-restart-service
---

# 交付验证前重启服务（使最新变更生效）

## 问题

修复完成、commit 已推，但用户刷新页面或调用接口时看到的仍是**旧行为**。原因：受影响的容器/进程没有用最新代码重新构建或重启，变更未生效。

该问题容易在「改代码 → 自测/commit → 交给用户验证」的流程中反复出现，若 Agent 或开发者不主动重启服务，用户会误以为修复无效。

## 规则

在**修复完成、交给用户体验验证**之前，**必须**主动让受影响的容器/服务加载最新变更：

| 部署方式 | 操作 |
|----------|------|
| Docker，代码打进镜像、无 bind-mount | `docker compose build <service> && docker compose up -d <service> --force-recreate` |
| Docker，仅改 .env | `docker compose up -d <service> --force-recreate`（不要用 `restart`，不重新读 .env） |
| 本地进程（如 npm run dev） | 若改的是需重启才加载的代码，提示用户重启或自行执行重启 |

## 适用场景

- 前端页面/交互（用户刷新浏览器验证）
- API 行为（用户通过界面或接口验证）
- 任何由「当前运行中的代码」决定的可验证功能

## 检查清单（交付前）

- [ ] 本次修改是否影响运行中的服务（前端/API/worker）？
- [ ] 若是，该服务是否通过镜像运行且无源码挂载？→ 执行 build + up -d --force-recreate
- [ ] 若仅改 .env → 执行 up -d --force-recreate，勿用 restart

## 参考

- AGENTS.md：Execution Rules →「交付验证前重启服务」
- TradeRadar：前端无 bind-mount，改 web 后需 `docker compose build web && docker compose up -d web --force-recreate`（2026-03-12 多次遗漏后沉淀）
