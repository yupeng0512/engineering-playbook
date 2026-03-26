---
title: aggregate-thread-and-opportunity-signals-into-account-memory
type: note
tags: [pattern, crm, inbox, operator-trust, account-progress]
permalink: engineering-playbook/patterns/aggregate-thread-and-opportunity-signals-into-account-memory
---

# Aggregate Thread and Opportunity Signals into Account Memory

## Pattern

When an agentic sales product starts handling multiple contacts, threads, packets, and opportunities for the same company, add an explicit account-level memory summary instead of forcing the operator to reconstruct the state manually.

## Why

As automation gets better, the product often becomes fragmented:

- one contact has the active lane
- another contact produced the latest buyer reply
- a thread created the opportunity
- a packet now carries the commercial next step

Each object is locally correct, but the operator still has to ask:

- what is happening with this account overall?
- which contact is currently active?
- is there already an active opportunity?
- what is the latest hold reason?

Without account memory, the system looks smart at the object level but still feels cognitively expensive.

## Recommended shape

Add an explicit `AccountMemoryState` that summarizes:

- current active outreach lane
- current active contact
- current active opportunity
- latest buyer reply timestamp
- latest commercial packet
- latest hold reason

Keep downstream ownership intact:

- `Customers`
  - summary / recall / account overview
- `Inbox`
  - thread truth and review
- `Opportunity`
  - deal progression

The account memory layer should aggregate these objects, not replace them.

## Operator-facing rendering

In the default customer surface, answer only:

1. what state is this account in now?
2. which lane or contact is active?
3. what is the current packet / hold reason?
4. where should I go if I need the full progression detail?

Do not turn the account view into a giant CRM surface.

## Validation

- service tests prove thread + opportunity state aggregates into one account summary
- UI copy uses stable localized status / hold / packet keys
- default operator surface reduces “mental stitching” across contacts and threads

## TradeRadar example

In `Phase 28BK`, `TradeRadar` introduced:

- `AccountMemoryState`
- `AccountProgressSummary`
- `AccountOpportunityLink`

This let `Customers` answer the account-level question first, while keeping `Inbox` and `Work` focused on thread truth and dispatch decisions.
