---
title: promote-learned-defaults-only-after-evidence-threshold
type: note
tags: [pattern, automation, learning-loop, defaults, safety]
permalink: engineering-playbook/patterns/promote-learned-defaults-only-after-evidence-threshold
---

# Promote Learned Defaults Only After Evidence Threshold

## Pattern

When an automation system starts learning from outcomes, do not jump directly from:

- “the system noticed a pattern”

to:

- “the system changed the default”

Insert an explicit promotion layer with evidence thresholds.

## Why

Learning loops become untrustworthy when every directional hint is treated as a durable default.

Common failure modes:

- early noise gets promoted too aggressively
- operators stop understanding why defaults changed
- low-risk tuning and high-risk strategy changes get mixed together

## Recommended ladder

Keep learned output in four buckets:

1. `keep_current`
2. `recommend_change`
3. `recommend_experiment`
4. `promote_as_default`

Only the last bucket should be eligible to become the new default, and only for low-risk fields.

## Recommended contract

Every learned recommendation should carry:

- current bucket / recommendation kind
- explicit `promotion_eligibility`
- reason
- evidence threshold
- promoted scope, if promotion is allowed

## Good boundaries

Safe to promote by default:

- low-risk copy skeleton preferences
- target-market tightening
- weighting adjustments inside an already approved strategy

Not safe to promote silently:

- pricing commitments
- payment terms
- delivery promises
- strategy expansion
- any approval threshold changes

## Operator-facing rendering

The default surface should answer:

1. what the system learned
2. why it matters
3. whether it is just a recommendation or promotion-ready

Do not force operators to reverse-engineer the distinction from raw metrics.

## Validation

- service tests prove promotion eligibility is threshold-driven
- apply endpoints reject promotion when evidence is insufficient
- browser smoke proves the UI distinguishes recommendation vs promotion-ready states

## TradeRadar example

In `Phase 28BA`, `TradeRadar` introduced:

- `PromotionEligibility`
- `DefaultPromotionRecommendation`
- `recommendation` vs `promoted_default` apply modes

This let the product keep a recommendation-first learning loop while still allowing repeated, low-risk patterns to become reusable defaults once they crossed a clear evidence threshold.
