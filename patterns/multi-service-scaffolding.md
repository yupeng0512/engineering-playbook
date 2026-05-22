---
title: Multi-Service Project Scaffolding Pattern
tags:
- architecture
- docker
- microservices
- python
- fastapi
type: pattern
permalink: engineering-playbook/patterns/multi-service-scaffolding
---

# Multi-Service Project Scaffolding Pattern

## Context
When building a system with 4+ microservices (like ai-video-matrix), the scaffolding approach matters for long-term maintainability.

## Pattern

### Directory Structure
```
project/
├── docker-compose.yml          # Single entry point
├── .env.example                # All env vars documented
├── Makefile                    # Developer-friendly commands
├── services/
│   └── {service-name}/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── config.py           # Pydantic Settings (env-driven)
│       ├── api.py              # FastAPI app with lifespan
│       └── {domain}.py         # Core business logic
├── storage/
│   └── postgres/migrations/    # Ordered SQL migrations
├── scripts/                    # Operational scripts
└── configs/                    # Service configs (Grafana, etc.)
```

### Key Decisions
1. **One Pydantic Settings per service** — each reads its own env vars, no shared config
2. **SQL migrations as init scripts** — mounted into PostgreSQL's docker-entrypoint-initdb.d
3. **Health endpoints on every service** — enables docker-compose healthchecks and monitoring
4. **Makefile as developer UX** — `make setup`, `make health`, `make logs`, `make db-shell`

### Common Bugs to Watch
- **Database URL protocol**: SQLAlchemy async requires `postgresql+asyncpg://`, not `postgresql://`
- **Docker restart vs recreate**: After changing `.env`, use `docker compose up -d --force-recreate`, not `restart`
- **Browser context leaks**: When using Playwright with many accounts, implement LRU eviction (max 20 contexts per worker)
- **SQL parameterization in intervals**: `interval ':hours hours'` doesn't work — use `interval '1 hour' * :hours`

## Observations
- [pattern] Each service should own its database connection and not share SQLAlchemy engines
- [technique] Use `asyncio.gather()` for parallel task execution in worker pools, not sequential loops
- [decision] For video deduplication, perceptual hashing (videohash) is sufficient as a "pre-check gate" — platforms do their own deep analysis

## Relations
- implements [[Multi-Service Architecture]]
- relates_to [[Docker Compose Patterns]]
- relates_to [[FastAPI Best Practices]]