---
title: use-one-dominant-control-plane-surface-and-inline-agent-completion
type: note
tags: [pattern, control-plane, agent, ux, operator-os]
permalink: engineering-playbook/patterns/use-one-dominant-control-plane-surface-and-inline-agent-completion
---

# Use One Dominant Control-Plane Surface And Inline Agent Completion

## Pattern

When a product already knows:

- the current focus object
- the current blocker
- the current next action

the default experience should not keep bouncing the user across separate goal pages, workbenches, and setup flows.

Instead, choose one dominant control-plane surface and keep most default actions inside it:

- use the native agent for text input, minimal interviews, and explanation
- use inline sheets or confirm modals for structured yes/no boundary checks
- reserve route changes for true expert work or external execution

## Why

Without this, the system may already know the current step, but the user still experiences:

- one page to discover the step
- another page to explain it
- another page to fill context
- another page to confirm it

That recreates workbench-style cognitive load even after the backend has already compressed the workflow into a single focused action.

## Recommended shape

Use one shared inline-action model such as:

- `kind`
- `label`
- `presentation`
- `focus_object_id`
- `reason`
- `deep_link_route`

Then keep the default routing rules simple:

- launcher surface:
  - only decides what the current step is
- dominant control-plane surface:
  - shows current state, blocker, next automatic action, one CTA
- native agent:
  - asks questions
  - explains blockers
  - collects minimal input
- inline confirm UI:
  - handles approval / confirm / reject boundaries

## Rules

- Do not make a generic goal/workbench page the default landing surface if the system already knows the focused object.
- Do not route to a second page just to collect a few missing inputs.
- Use the native agent for free-text answers and minimal interviews.
- Use confirm sheets or modals for explicit boundary approval.
- Keep expert routes for:
  - deep editing
  - diagnostics
  - external execution evidence
  - human takeover
- Keep browser-agent infrastructure behind the scenes; do not let it become the default UI.

## Validation

1. service responses for launcher, explainer, and control-plane surfaces resolve the same focus object and the same primary inline action
2. browser smoke proves “fill context” opens inline agent completion instead of routing to a separate workbench page
3. confirm actions resolve inline and refresh the same control-plane surface without route churn

## Avoid

- making the user bounce between launcher page, goal page, product page, and wizard for one logical step
- using the agent as a second generic workspace instead of the inline input rail for the current step
- turning browser fallback into the explanation layer for why the system chose the current action
