---
title: materialize-approved-packets-into-dispatch-ready-drafts
type: note
tags: [pattern, approval, drafts, operator-os, workflow]
permalink: engineering-playbook/patterns/materialize-approved-packets-into-dispatch-ready-drafts
---

# Materialize Approved Packets Into Dispatch-Ready Drafts

## Pattern

When an operator system already has:

- explicit runs
- prepared actions / carryover
- approval-ready packets

the next high-ROI step is often **not** more recommendations.  
It is making approval produce an explicit, user-visible **dispatch-ready draft outcome**.

## Why

Without this layer, the system still stops at:

- "here is the packet"
- "please approve it"

but the operator still has to infer:

- what concrete draft now exists
- where it lives
- whether it is already `ready_to_queue`

That leaves the last mile of execution ambiguous.

## Recommended shape

Add a narrow read model such as:

- `DispatchReadyDraft`

with fields like:

- `draft_kind`
- `dispatch_state`
- `target_surface`
- `target_ref`
- `route`
- `summary`
- `draft_payload`
- `confirmation_snapshot`
- `evidence_summary`
- `next_action_label`

## Rules

- Keep the draft outcome derived.
- Do not turn it into a parallel workflow truth object.
- Keep buyer-facing defaults on the real dispatch surface, not on the deal page.
- Keep the human boundary at `ready_to_queue` before introducing `ready_to_send`.
- Make approval explain its consequence:
  - what will be generated
  - where it will land
  - what the next action is

## Good defaults

- buyer-facing drafts:
  - default to `Inbox / reply queue`
- quote-specific editing:
  - stays on quote desk / deal surface
- internal readiness / handoff:
  - stay on their internal expert surfaces

## Validation

Use a layered proof:

1. service tests prove approval returns a dispatch-ready draft
2. batch detail tests prove approval preview explains what will materialize
3. browser proof verifies the operator lands on the concrete continuation surface

## Avoid

- stopping at packet-level explanation only
- making operators translate packets into drafts manually
- coupling E2E only to brittle intermediate request timing when the real contract is an operator-visible continuation surface
