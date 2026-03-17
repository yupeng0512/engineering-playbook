---
title: agent-safe-action-adapters-wrap-bounded-services
type: note
permalink: engineering-playbook/patterns/agent-safe-action-adapters-wrap-bounded-services
date: 2026-03-17
tags:
- agent
- actions
- hitl
- workflow
- safety
---

# Agent Safe Action Adapters Should Wrap Bounded Services

## Problem

When an AI workspace starts doing more than read-only analysis, the easiest mistake is also the most dangerous one:

- let the model call broad write APIs directly
- let the UI say "execute" without clearly stating boundaries
- let the system decide readiness late, only after a deep write path has already started

This usually creates the worst mix of outcomes:

- action scope is hard to audit
- readiness checks are inconsistent
- blocked states surface too late
- AI appears more autonomous than the product can safely support

## Pattern

Instead of giving the AI a broad mutation surface, introduce **safe action adapters**.

Each adapter should:

- represent one narrow user intent
- wrap an existing bounded domain service
- declare its benefit and its boundary in the UI
- compute readiness before execution
- return a blocked reason and a recovery route when execution is unsafe

The adapter layer is not a new write engine.
It is a **translation layer** between:

- user-scoped AI intent
- existing audited product services

## Recommended Rules

- Prefer adapters that call existing services with known side effects, such as:
  - start or refresh an internal task
  - trigger a bounded preparation pass
  - pin, archive, or label a safe object
- Keep each adapter single-purpose. One adapter should map to one clearly named action.
- Readiness should be computed before execution, not discovered halfway through a write path.
- If an action is blocked, return:
  - a human-readable blocked reason
  - the exact route or object the user should open next
- Adapters must stay user-scoped and ownership-checked.
- Adapters that cross into outbound send, approval, handoff, payment, or live promises should remain proposal-gated or HITL-gated.
- UI cards should always show:
  - expected benefit
  - explicit boundary
  - current readiness
  - key evidence or policy inputs

## Why This Works

This pattern keeps the AI useful without pretending it has authority the product does not actually grant.

It improves:

- auditability
- predictability
- user trust
- reuse of existing business logic

And it reduces:

- duplicate write paths
- hidden side effects
- late execution failures
- pressure to make the AI "fully autonomous" too early

## Good Example

- "Launch mining cadence" wraps the existing autopilot launch service.
- "Prepare workbench now" wraps the existing bounded run-now preparation path.

Both actions are useful, but neither bypasses outbound approval or HITL boundaries.

## Anti-Pattern

Avoid this shape:

- model decides an action
- UI renders a generic "Apply"
- request hits a broad mutation endpoint
- downstream services discover missing context or blocked policy late

That is not safe action design.
That is just hiding uncontrolled writes behind an AI-flavored button.
