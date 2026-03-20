---
title: derive-explicit-goal-landing-plans-from-run-continuity
type: note
permalink: engineering-playbook/patterns/derive-explicit-goal-landing-plans-from-run-continuity
date: 2026-03-20
tags:
- product
- ai
- agent
- workflow
- navigation
- orchestration
---

# Derive Explicit Goal Landing Plans From Run Continuity

## Problem

Operator products often evolve into this shape:

- the dashboard exposes a small set of goals
- the backend already knows active runs, blocked repairs, approvals, and prepared actions
- the frontend still treats the goal CTA as a generic launcher

The result is a subtle but expensive UX failure:

- the user clicks a high-level goal such as "advance close"
- the system opens a generic AI workspace or tool page
- the user must reconstruct the next step by hand

At that point, the product knows more than the user-facing flow admits.

## Pattern

Introduce a small backend-owned **goal landing plan**.

Instead of letting the frontend guess where a goal should go, return an explicit continuation such as:

- active run
- successor run
- approval batch
- guided repair
- prepared action
- resolution prepare
- generic fallback only when nothing concrete exists

Recommended shape:

- `mode`
- `reason`
- `run_id`
- `approval_batch_id`
- `prepared_action_key`
- `target_ref`
- `missing_fields[]`
- `route`

The goal CTA should launch this landing plan directly, not a generic workspace by default.

## Recommended Rules

- Let the backend own landing priority, because only it has the full workflow context.
- Prefer concrete continuation over generic tooling.
- Keep fallback explicit:
  - only use a generic workspace when there is no actionable continuation
  - explain why the fallback was needed
- Treat guided repair as the **minimum gap to continue the chain**, not a restart.
- Let approval sheets count as workflow checkpoints, not as a separate subsystem.
- Keep expert surfaces available, but do not use them as the default landing when a more specific continuation already exists.

## Why This Works

This pattern removes a hidden cognitive tax:

- the user no longer translates a goal into a page choice
- the product can behave like a continuous execution system instead of a guided tool collection
- close-side work becomes "continue this chain" instead of "open workspace and decide again"

It improves:

- time from goal click to concrete action
- trust that the system actually knows the next step
- continuity between dashboard, run canvas, approvals, and repairs

## Good Example

- `Today` surfaces `advance_close`.
- The backend sees an active reopened resolution run.
- The returned landing plan is `execution_run`, not generic workspace.
- The CTA copy becomes "Continue this close chain".
- If the next best action is a close-side approval batch, the landing switches to `approval_batch_sheet`.
- If the chain is blocked on product linkage, the landing switches to `guided_repair` and explains what will continue after repair.

## Anti-Pattern

Avoid this sequence:

- compute active runs, repairs, prepared actions, and approvals on the backend
- ignore that context at the goal click boundary
- always route the user into a generic AI workspace

That does not simplify execution.
It hides the system's best knowledge behind one extra manual decision.
