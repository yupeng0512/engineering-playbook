---
title: Test Harness with Mock Services Pattern
tags: [testing, docker, mock, e2e, cost-control]
type: pattern
permalink: engineering-playbook/patterns/test-harness-mock-services
---

# Pattern: Test Harness with Mock Services

> Zero-cost end-to-end testing by replacing external APIs with Docker-based mock services.

## Problem

Systems that depend on paid external APIs (AI video generation, LLM, etc.) are expensive to test end-to-end. Manual testing is unreliable and not repeatable. Unit tests can't catch integration bugs.

## Solution

Use Docker Compose overlay (`docker-compose.test.yml`) that:
1. Adds mock services alongside real ones
2. Overrides service environment to point to mocks
3. Seeds test data automatically via init container
4. Supports mode switching: `TEST_MODE=mock` (zero cost) / `TEST_MODE=real` (real APIs)

```
docker-compose.yml          (base: real services)
  +
docker-compose.test.yml     (overlay: mock services + seed data)
  =
Complete test environment
```

## Key Design Decisions

### Mock Service Design
- **FastAPI-based**: Same framework as real services, minimal overhead
- **Deterministic**: Always succeed, return valid but minimal data
- **Stateful**: Track calls in-memory for assertion verification
- **Health-checked**: Support `GET /health` like real services

### Seed Data
- Use a `test-seed` init container with `restart: "no"`
- Run SQL directly via `psql` against the test database
- Use `ON CONFLICT DO NOTHING` for idempotent re-runs
- Use well-known UUIDs (`00000000-...`) for predictable references in tests

### Overlay, Not Replacement
```yaml
# docker-compose.test.yml — extends, not replaces
services:
  mock-kling-api:           # NEW: mock service
    build: ./tests/mocks
  content-planner:          # OVERRIDE: point to mock
    environment:
      - KLING_BASE_URL=http://mock-kling-api:8000
```

## Checklist

- [ ] Mock services implement the same API contract as real ones
- [ ] `docker compose -f ... -f ... config --quiet` validates cleanly
- [ ] All mock services have `/health` endpoint
- [ ] Seed data uses `ON CONFLICT DO NOTHING` for idempotency
- [ ] E2E tests use assertions, not just print statements
- [ ] `TEST_MODE` env var controls mock vs real behavior

## Observations

- [pattern] Docker Compose overlay is simpler than testcontainers for multi-service systems
- [technique] Minimal MP4 generation via struct.pack — avoids ffmpeg dependency in mocks
- [decision] Mock services share a single Dockerfile to minimize build time

## Relations

- extends [[Multi-Service Scaffolding]]
- relates_to [[Docker Traefik Dev Routing]]
