---
title: clip-budget-summaries-to-the-actual-allocation-window
type: note
tags: [pattern, allocation, budgeting, operator-trust, manager-summary]
permalink: engineering-playbook/patterns/clip-budget-summaries-to-the-actual-allocation-window
---

# Clip Budget Summaries To The Actual Allocation Window

## Pattern

When a product shows a budgeted manager summary such as:

- stable slots
- experiment slots
- daily dispatch slots
- remaining allocation capacity

the displayed counts must reflect the actual allocation window, not the whole pool of eligible candidates.

## Why

A common regression appears after an allocator becomes explainable:

- the system correctly ranks many lanes as eligible
- the UI starts counting all prioritized lanes
- but the actual daily budget only covers a smaller subset

The result is a summary that looks mathematically inconsistent:

- `stable + experiment > total budget`
- “today's budget” quietly becomes “all theoretically good options”

This is especially dangerous because:

- the code may still compile
- each individual lane may still look correct
- but the default manager surface starts to feel untrustworthy

## Recommended shape

Keep two layers distinct:

- candidate pool
  - all currently prioritized or eligible lanes
- allocation window
  - the subset that today's budget can actually cover

Budget summaries must only count the allocation window.

Recommended rules:

- clip counted lanes to the active budget window first
- then classify them into:
  - stable budget
  - experiment budget
- if no budget remains, render an explicit zero-budget state instead of synthetic slot counts

## Operator-facing rendering

In the default manager surface, answer only:

1. how many slots are actually available today?
2. how many of those are stable?
3. how many of those are experiments?
4. why are the rest not being funded today?

Do not let “all prioritized lanes” leak into the budget badge.

## Validation

- tests prove `stable_slots + experiment_slots <= total_slots`
- tests cover the case where more lanes are prioritized than the daily budget allows
- the zero-budget state renders explicitly instead of showing misleading synthetic slots

## TradeRadar example

In `Phase 28BP`, `TradeRadar` added `experiment_budget` to the portfolio allocator.

The review follow-up tightened the contract:

- slot counts are clipped to the actual `daily_dispatch_budget` window
- the UI no longer implies that all prioritized lanes are funded today
- the manager summary remains trustworthy even when the eligible pool is larger than the current budget
