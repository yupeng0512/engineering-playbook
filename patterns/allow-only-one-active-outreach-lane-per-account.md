---
title: allow-only-one-active-outreach-lane-per-account
type: note
tags: [pattern, outbound, sequencing, operator-trust, deliverability]
permalink: engineering-playbook/patterns/allow-only-one-active-outreach-lane-per-account
---

# Allow Only One Active Outreach Lane Per Account

## Pattern

In B2B outbound systems, do not let multiple contacts from the same account enter live outreach at the same time by default.

Keep one explicit `active lane` per account, and only allow a second contact when a bounded expansion rule is satisfied.

## Why

When a system gets better at prospect discovery and route confidence, a common regression appears:

- the system finds multiple good contacts in the same company
- all of them look individually sendable
- the system starts contacting them in parallel

That may improve raw activity metrics, but it hurts:

- deliverability
- trust
- operator confidence
- account-level sequencing quality

The product starts to feel spammy, even if each single contact looked like a reasonable candidate.

## Recommended shape

Keep two layers distinct:

- `dispatch decision`
  - is this person individually safe and worthwhile to contact?
- `account coverage decision`
  - should this account already be considered “covered” by another active lane?

Model the account layer explicitly:

- `AccountCoverageState`
  - `has_active_lane`
  - `active_lane`
  - `waiting_window_until`
  - `can_expand_to_second_contact`

- `ContactLaneDecision`
  - `active_primary`
  - `eligible_secondary`
  - `hold_for_lane_window`
  - `exclude_duplicate_lane`

## Safe expansion rule

Only allow a second contact when all of these are true:

- the no-reply or waiting window has elapsed
- the current lane has not converted
- buyer-role evidence is strong enough
- the contact route is trusted
- the second lane is not a duplicate or conflicting contact

## Operator-facing rendering

In the default surface, show:

1. which account is currently active
2. which contact is the active lane
3. why the other contacts are being held

Do not force the operator to infer this from raw timestamps or a dense outreach timeline.

## Validation

- service tests prove a second contact cannot enter live dispatch before the lane window clears
- UI rendering distinguishes:
  - active primary
  - eligible secondary
  - held for lane window
  - duplicate lane exclusion

## TradeRadar example

In `Phase 28BH`, `TradeRadar` introduced account-aware sequencing before `dispatch_now`.

The system now:

- keeps one active outreach lane per account
- prefers the strongest buyer-role + route candidate as the primary lane
- only expands to a secondary contact after the waiting window clears and safety gates still pass

This preserved operator trust while keeping dispatch quality high.
