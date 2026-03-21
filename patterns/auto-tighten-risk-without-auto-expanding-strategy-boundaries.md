---
title: auto-tighten-risk-without-auto-expanding-strategy-boundaries
type: note
tags: [pattern, automation, guardrails, safety, operator-os]
permalink: engineering-playbook/patterns/auto-tighten-risk-without-auto-expanding-strategy-boundaries
---

# Auto-Tighten Risk Without Auto-Expanding Strategy Boundaries

## Pattern

When an operator product starts allowing policy-approved automation to continue beyond a first step, let the system automatically **tighten** risk boundaries, but do not let it automatically **expand** strategy boundaries.

In practice:

- the system may reduce send rate
- the system may delay the next send window
- the system may block low-confidence locales or variants
- the system may downgrade follow-up eligibility from `eligible` to `watch` or `blocked`

But the system should not automatically:

- widen auto-dispatch scope
- change ICP or target markets
- change sender identity
- change core positioning or value proposition

## Why

This preserves a trustworthy HITL boundary while still giving automation room to protect itself.

The operator mental model becomes:

- approve the strategy once
- let the system keep running while conditions stay safe
- only step back in when safety or quality forces a contraction

That feels much safer than a system that quietly expands what it is allowed to do.

## Recommended shape

Keep strategy decisions and safety decisions separate:

- strategy objects:
  - `AutopilotContract`
  - `AutopilotPolicy`
- safety/read models:
  - `AutopilotSafetySnapshot`
  - `AutopilotTuningHint`
  - `AutopilotException`

The safety layer can reduce operational risk, but the strategy layer still owns scope.

## Good defaults

- first-touch:
  - can unlock earlier under strategy approval
- follow-up:
  - expand only one low-risk step at a time
- tuning:
  - auto-apply only risk-tightening moves
- exceptions:
  - explain why automation paused
  - explain what must be fixed
  - explain what state automation will resume into

## Validation

Use layered proof:

1. service tests prove safety snapshots and tuning hints are derived deterministically
2. approval tests prove scope expands only to the explicitly approved safe boundary
3. browser smoke proves control-plane surfaces explain whether the system will or will not continue automatically

## Avoid

- letting automation silently widen the approved scope
- coupling long-lived automation state to short-lived execution-run semantics
- calling a system “safe autopilot” if it can tighten nothing and only either run or fail
