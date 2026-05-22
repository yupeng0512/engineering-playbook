---
title: queue-executability-before-approval
type: note
permalink: engineering-playbook/patterns/queue-executability-before-approval
---

# Queue Executability Before Approval

## Problem

A queue item can look ready long before the final action is actually executable.

Common failure shape:

- the list says `ready`
- the operator clicks approve
- the very last API call discovers a missing recipient, missing artifact, or missing binding

That is the worst possible moment to learn the item was not truly ready.

## Pattern

Gate approval on the same prerequisites that the final side effect will need.

If the final action requires:

- a safe recipient
- a valid target object
- a deliverable artifact
- a non-expired policy window

then the queue builder must verify those conditions before the item enters an approvable state.

## Recommended Rules

- Reuse the same readiness helper in both queue building and final execution.
- Prefer `blocked(reason_code)` over “approve first, fail later”.
- Make the blocking reason visible to both operators and tests.
- Seeded E2E data must satisfy the real execution prerequisites, not only the UI prerequisites.

## Benefit

- operators trust the queue
- approvals stop failing at the last click
- E2E tests stop certifying fake-ready data
