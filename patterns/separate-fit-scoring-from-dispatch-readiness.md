---
title: separate-fit-scoring-from-dispatch-readiness
type: note
tags: [pattern, automation, ranking, operator-trust, queue]
permalink: engineering-playbook/patterns/separate-fit-scoring-from-dispatch-readiness
---

# Separate Fit Scoring From Dispatch Readiness

## Pattern

Do not treat “this object looks like a good fit” as equivalent to “this object is ready to enter the next execution queue.”

Keep two distinct layers:

- `fit assessment`
  - how well the object matches the desired profile
- `dispatch readiness`
  - whether the system currently has enough evidence and context to act on it safely

## Why

Operator products lose trust quickly when the system jumps from rough ranking to execution without an explicit queue-admission decision.

Common failure mode:

- a candidate gets a strong score
- but the product context is incomplete, evidence is thin, or exclusion signals are present
- the system still moves it into a live execution queue

That feels like “the system is contacting the wrong people,” even if the raw fit score is defensible.

## Recommended shape

Model them separately:

- `FitAssessment`
  - score
  - positive evidence
  - exclusion evidence
- `QueueAdmissionDecision`
  - `ready`
  - `needs_more_context`
  - `excluded`
  - reason
  - missing context

## Operator-facing rendering

In the default surface, show:

1. how many are actually ready
2. how many still need context
3. how many are excluded

Do not show a giant scoring workspace by default.

The operator question is not:

- “Who scored 72?”

It is:

- “Who is safe and worthwhile to move forward right now?”

Keep the operator-facing reason specific.

Do not collapse:

- missing route
- missing buyer-role or profile evidence
- missing product context
- weak signal quality

into one generic “needs more context” summary.

If those reasons collapse into a single catch-all label, the queue may still be technically correct, but the operator will stop trusting why items were held or excluded.

## Validation

- service tests prove queue-admission state is derived deterministically
- UI tests prove ready / delayed / excluded buckets are rendered distinctly
- review checks prove excluded items cannot silently fall back into the ready queue

## TradeRadar example

In `Phase 28AY`, `TradeRadar` kept `fit_score` but added an explicit `DispatchReadinessState`:

- `ready_for_first_touch`
- `needs_more_context`
- `excluded`

This prevented signal-qualified but context-thin prospects from entering first-touch preparation just because their profile looked promising.
