---
title: move-hitl-from-batch-approval-to-strategy-approval-plus-exceptions
type: note
tags: [pattern, automation, hitl, operator-os, control-plane]
permalink: engineering-playbook/patterns/move-hitl-from-batch-approval-to-strategy-approval-plus-exceptions
---

# Move HITL From Batch Approval To Strategy Approval Plus Exceptions

## Pattern

When an operator product wants users to "follow the system" instead of manually operating every tool page, one of the highest-ROI moves is often:

- stop interrupting humans on every batch
- move the human boundary up to a **strategy approval**
- interrupt again only on **exceptions**

## Why

Batch-level approval still forces users to understand:

- policy
- cadence
- templates
- sender constraints
- queue state

on every cycle.

That keeps the product feeling like a tool bundle.

Strategy approval plus exception-only interruption changes the default mental model to:

- fill minimum context
- approve policy once
- only handle exceptions

## Recommended shape

Keep facts on the existing domain objects, but add narrow orchestration/read models such as:

- `AutopilotContract`
- `AutopilotControlState`
- `AutopilotException`

Typical states:

- `needs_strategy_approval`
- `running`
- `paused_by_exception`
- `cooldown`
- `stopped`

## Rules

- Do not reuse short-lived execution-run primitives for long-lived, product-scoped automation.
- Do not create a new giant “automation center” page if Today/Goal Canvas can act as the control plane.
- Keep exception kinds explicit and high-signal.
- Let expert surfaces remain the source-of-truth editing pages.
- Let the default control plane explain:
  - what policy is being approved
  - why the system is paused
  - what exception needs human attention

## Good defaults

- first-touch:
  - eligible for strategy-approved automation earlier
- follow-up / replies / close-side:
  - keep stronger human confirmation longer
- exceptions:
  - concrete object + reason + route
  - not abstract counters only

## Validation

Use layered proof:

1. service tests prove contracts, control states, and exceptions are derived deterministically
2. command-center tests prove strategy approval / exception entries outrank lower-level tool work
3. browser smoke proves Today and Goal Canvas show concrete control-plane CTAs instead of generic tooling language

## Avoid

- forcing users to read policy, sequence, mining, and approval pages separately
- modeling long-lived automation as a single all-purpose run
- calling something “autopilot” when the system still interrupts on ordinary batches rather than true exceptions
