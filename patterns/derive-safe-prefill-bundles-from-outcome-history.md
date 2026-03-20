---
title: derive-safe-prefill-bundles-from-outcome-history
type: note
permalink: engineering-playbook/patterns/derive-safe-prefill-bundles-from-outcome-history
date: 2026-03-20
tags:
- product
- ai
- agent
- workflow
- orchestration
- defaults
- prefill
---

# Derive Safe Prefill Bundles From Outcome History

## Problem

An operator product can already:

- surface the right object
- explain why it is prioritized
- remember run continuity
- reopen work when outcomes change

And still leave too much work to the operator.

The failure mode looks like this:

- the system has a clear recommendation
- the operator agrees with it
- but still has to translate that guidance into a proposal patch, repair form, or draft by hand

At that point the product has guidance, but not prepared execution.

## Pattern

Derive **small, editable prepared-action bundles** from historical outcome patterns.

Do **not** introduce:

- auto-send
- auto-apply
- a generic workflow builder
- a black-box prefill engine

Instead:

- define a narrow context key from the current run
- require real historical success samples
- compute dominant defaults only for a fixed target action
- attach the prepared bundle to the existing run/workbench response
- let the target expert surface load those defaults as editable starting values

## Recommended Guardrails

- Keep the scope narrow:
  - close-side only
  - fixed action types
  - fixed supported fields
- Require a minimum historical threshold before prefill appears.
  - Example: at least `2` successful samples
- Exclude the current run from generating its own defaults.
- Never let prefill overwrite confirmed facts.
  - Use current facts and carryover first.
  - Only fill blanks or draft defaults.
- Make every prepared bundle:
  - reviewable
  - editable
  - dismissible

## Good Candidate Actions

High-signal prepared actions usually look like:

- commercial-context proposal patches
- package follow-up draft defaults
- order-readiness repair defaults
- finance-handoff repair defaults

These actions already have:

- structured fields
- repeated operator behavior
- real downstream outcomes

That makes them suitable for deterministic prefill.

## Why This Works

This pattern upgrades the system from:

- "the product can explain the next best step"

to:

- "the product already prepared the next safe draft for review"

It reduces the operator burden without removing human confirmation.

## Good Example

- Similar resolution runs repeatedly stabilize when a commercial proposal is applied before quote revision.
- The next matching resolution run surfaces:
  - a commercial proposal prepared-action bundle
  - defaults for the likely override fields
  - a short evidence summary
- The operator edits if needed, confirms, and applies.

The product is not auto-executing.
It is compressing the translation cost from guidance to action.

## Anti-Pattern

Avoid this sequence:

- infer arbitrary defaults from broad event history
- include the current run in its own evidence
- overwrite already confirmed facts
- silently submit the action

That is not safe prefill.
That is hidden automation with weak evidence.
