---
title: clear scope-bound state before async refresh
type: pattern
tags:
- frontend
- async
- operator-surface
- trust
- state-management
permalink: engineering-playbook/patterns/clear-scope-bound-state-before-async-refresh
---

# Clear Scope-Bound State Before Async Refresh

## When to use

Use this pattern when a UI surface is always supposed to represent **one currently focused object**:

- current product
- current customer
- current thread
- current ticket

This is especially important for operator surfaces where showing the wrong object's data for even a moment can damage trust.

## Problem

Many scope-bound pages fetch data asynchronously when the current object changes.

If the implementation:

- keeps the old object's state visible while the new request is loading, or
- allows an older request to resolve after a newer one,

then the UI can briefly show stale data for the wrong object.

That kind of bug is easy to miss because:

- TypeScript still passes
- happy-path manual testing may not catch it
- the failure only appears during fast switching or slow network conditions

## Recommended pattern

When the scope changes:

1. Clear scope-bound state immediately.
2. Start a new request token / request id.
3. Only let the latest request write back to UI state.
4. Only let the latest request clear loading state.

## Why

For operator products, trust depends on the UI always answering:

- which object is the system currently working on?
- why is this shown right now?

Showing the previous object's summary or review packet, even briefly, makes the system feel unreliable.

## Example

- [technique] On `TradeRadar`, `Work` and `Inbox` both needed request-id guards so switching products/threads could not show stale prospecting summaries or stale thread details. #async #trust
- [insight] Count summaries should represent the true result set, not the truncated display slice; otherwise the operator gets the wrong mental model of scale. #ux #operator-surface
- [problem] Async scope switches often fail silently in happy-path testing because compile/build checks do not exercise late-arriving responses. #testing #state-management

## Relations

- relates_to [[manage-agent-skills-through-a-versioned-registry-with-channel-rollouts]]
- relates_to [[review-before-write-generic-agent-context-capture]]