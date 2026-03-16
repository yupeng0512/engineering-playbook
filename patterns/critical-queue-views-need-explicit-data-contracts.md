---
title: "Critical Queue Views Need Explicit Data Contracts"
type: pattern
tags: [testing, frontend, api, queues, e2e]
permalink: engineering-playbook/patterns/critical-queue-views-need-explicit-data-contracts
---

# Critical Queue Views Need Explicit Data Contracts

## Problem

Teams often render an operationally critical queue by deriving it from a broader list endpoint:

- pending drafts from a generic thread list
- approvals from a generic notifications feed
- urgent tasks from a broad workstream payload

This looks cheaper at first, but it creates a brittle contract:

- a partial failure in the broad list can make the queue look empty
- browser E2E starts failing on "empty state" even though the real bug is upstream contract drift
- workbench, detail page, and deep link can disagree about what is actually pending

## Pattern

Promote any operator-critical queue into an explicit API contract once it becomes a first-class workflow surface.

Examples:

- `GET /inbox/pending-drafts`
- `GET /approvals/batches`
- `GET /workbench/summary-cards/:kind/preview`

The queue endpoint should:

- return only the queue shape the UI actually needs
- preload the entities needed for preview and deep link
- keep empty collections stable (`[]`, not `null`)
- remain valid even when the broader list endpoint is degraded or filtered differently

## Why it matters

The user is not asking for “all threads” or “all tasks”.
They are asking:

- what do I need to approve now?
- which draft is pending?
- which batch is ready to review?

Those are workflow questions, so they deserve workflow-level contracts.

## Signals that it is time to promote

- the queue appears on the first screen of the product
- a summary card links into it
- Playwright/E2E treats it as part of a golden path
- partial page failures can make the queue silently disappear
- the UI needs different preload rules than the generic list

## Trade-off

You do add one more endpoint and one more contract to maintain.

That is usually cheaper than:

- debugging false empty states
- teaching the browser suite to compensate for hidden derivation logic
- explaining why workbench and detail views disagree

## Rule of thumb

If a queue is operationally important enough to block release-quality browser flows, it is important enough to have its own explicit API contract.
