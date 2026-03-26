---
title: keep-account-plan-as-a-read-model-over-primary-and-assist-lanes
type: note
tags: [pattern, crm, inbox, operator-trust, account-plan]
permalink: engineering-playbook/patterns/keep-account-plan-as-a-read-model-over-primary-and-assist-lanes
---

# Keep Account Plan as a Read Model Over Primary and Assist Lanes

## Pattern

When an agentic B2B sales product starts coordinating buyer, ops, compliance, logistics, and finance stakeholders for the same company, keep one explicit account plan read model instead of turning the product into a giant CRM workspace.

The account plan should summarize:

- the one active `primary lane`
- any bounded `assist lanes`
- the active opportunity
- current blockers
- the next best action

## Why

After account memory exists, a common regression appears:

- the buyer becomes the commercial primary contact
- compliance asks for certificates
- ops asks about samples or shipping
- finance asks about payment or documents

Each thread is individually correct, but the operator still has to reconstruct:

- who is the real commercial owner?
- which stakeholder is only assisting?
- is there already an active opportunity?
- what is blocking progression now?

Without an explicit account plan, the system looks advanced but still feels cognitively expensive.

## Recommended shape

Keep the lane model explicit:

- one `primary commercial lane` per account
- bounded `assist lanes` only when there is an active opportunity
- assist lanes may cover:
  - compliance
  - sample coordination
  - logistics
  - finance / documents
- assist lanes must not become a parallel outbound sales motion

Model the account layer as a read model:

- `AccountPlanState`
- `AssistLaneState`
- `AccountBlocker`
- `AccountNextBestAction`

This read model should aggregate thread truth, opportunity state, and stakeholder roles without replacing them.

## Operator-facing rendering

In the default customer surface, answer only:

1. what is this account currently progressing?
2. who is the primary lane?
3. are assist lanes active?
4. what is blocked?
5. what is the next best action?

Do not turn the account surface into a giant CRM record browser.

## Validation

- service tests prove assist lanes only appear when an active opportunity exists
- UI rendering distinguishes primary lane from assist lanes
- blockers are explicit and localized
- the default surface reduces mental stitching across buyer / ops / compliance / finance threads

## TradeRadar example

In `Phase 28BN`, `TradeRadar` introduced `AccountPlanState` over the existing account memory layer.

This let:

- `Customers` answer the account-plan question first
- `Inbox` keep thread truth ownership
- `Work` stay focused on portfolio decisions

The important product boundary remained intact:

- one primary commercial lane
- bounded assist lanes only after real opportunity progression begins
