---
title: serialize-shared-state-browser-e2e
type: note
permalink: engineering-playbook/patterns/serialize-shared-state-browser-e2e
---

# Serialize Shared-State Browser E2E

## Rule

If browser E2E tests share any of the following, default the suite to serial execution:

- one login account
- one reused storage state
- one seeded tenant or workspace
- one mutable queue or inbox
- one approval surface whose state changes during the test

Do **not** try to hide the instability with retries first.

## Why

Parallel browser execution only pays off when the tests are truly isolated.

If two Playwright specs share:

- one OTP/dev login bootstrap
- one seeded user
- one database namespace
- one mutable dashboard

then the suite is not parallel-safe, even if individual pages look independent.

Typical failure shapes:

- summary counts disappear or move unexpectedly
- inbox/reply tests stop seeing the seeded object
- approval queues drain under another test
- auth/bootstrap races create false negatives

## Preferred order

1. Run the shared-state browser suite serially.
2. Prove stability.
3. Only then introduce parallel shards with isolated state.

## What to isolate before re-enabling parallelism

- one auth state per shard
- one scenario namespace per shard
- one seeded user or tenant per shard
- one queue/inbox slice per shard

If those do not exist yet, serial is the professional default.

## Anti-pattern

Do **not** jump straight to:

- more retries
- longer timeouts
- random waits
- “rerun failed test” CI bandaids

Those treat the symptom, not the shared-state cause.

## Good fit

This rule is especially useful for:

- workbench-style SaaS products
- approval queues
- inbox/reply flows
- seeded preview/staging E2E
- any OTP/dev-login based suite
