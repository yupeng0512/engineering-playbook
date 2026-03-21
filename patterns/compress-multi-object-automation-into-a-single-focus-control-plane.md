---
title: compress-multi-object-automation-into-a-single-focus-control-plane
type: note
tags: [pattern, control-plane, operator-os, ux, automation]
permalink: engineering-playbook/patterns/compress-multi-object-automation-into-a-single-focus-control-plane
---

# Compress Multi-Object Automation Into A Single-Focus Control Plane

## Pattern

When an automation product spans many objects at once, the default UI should still focus the operator on **one current line of work** instead of exposing every target, list, and tool at the same time.

The most reliable shape is:

- `Today`:
  - only answer what to do now
- `Goal Canvas`:
  - only answer why this is the current move and what the system will do after it
- `Expert surface`:
  - only answer the full source-of-truth state for the focused object

## Why

Even when the backend already knows the top-priority object, many products still leak:

- support assets
- historical proposals
- multi-target lists
- raw tooling modules
- expert configuration

That keeps the experience feeling like a smart workbench instead of a true control plane.

## Recommended shape

Use a shared read model such as:

- `focus_object_id`
- `primary_cta`
- `required_context`
- `top_exception`
- `automation_state`
- `next_automatic_action`
- `other_objects_count`

Then make every default surface render the same focus object with the same primary CTA.

## Rules

- Default to one focused object, even if the system is managing many.
- Keep other objects in a switcher, drawer, or secondary list.
- Do not expose history/support/tooling panels on the primary path unless they are the current blocker.
- Keep expert mode available, but collapsed by default.
- Make the agent explain the current focus object, not its entire generic capability map.

## Good defaults

- Primary card:
  - can the system continue
  - what is missing
  - what exception matters most
  - what happens automatically after approval
  - one CTA
- Secondary layer:
  - history
  - support assets
  - reports
  - saved sessions
  - raw policy / sequence / mining details

## Validation

1. service tests prove `Today / Goal Canvas / Expert surface` resolve the same focus object
2. browser smoke proves the primary surface does not render competing same-priority lists
3. product/page smoke proves secondary objects move into a switcher instead of stacking in the main card

## Avoid

- default pages that ask the user to choose among many equally important objects
- mixing control-plane state with history/tooling in the same primary card
- using browser-agent UI as the default explanation layer for why the system chose the current step
