---
title: drive-native-agent-guidance-from-the-same-focus-context-as-the-control-plane
type: note
tags: [pattern, agent, control-plane, ux, operator-os]
permalink: engineering-playbook/patterns/drive-native-agent-guidance-from-the-same-focus-context-as-the-control-plane
---

# Drive Native Agent Guidance From The Same Focus Context As The Control Plane

## Pattern

When a product has already compressed its default UI into a single-focus control plane, the native agent should not speak from a separate generic capability model.

Instead, `Today`, `Goal Canvas`, `Product`, and `Agent` should all derive from the same focus context:

- `focus_object_id`
- `primary_cta`
- `required_context`
- `top_exception`
- `automation_state`
- `next_automatic_action`
- `primary_reason`
- `focus_explanation`

## Why

Without this, the UI says:

- here is the one thing to do now

while the agent says:

- I can help with many different tools

That reintroduces ambiguity right after the product already worked to remove it.

## Recommended shape

Use one shared read model and let every default surface render or broadcast the same focus context.

Practical implementation options:

- derive the focus context directly from the same API response on each surface
- or dispatch a small shared client-side focus event/store that keeps the agent aligned with the current surface

## Rules

- Keep the default agent welcome copy specific to the current focus object.
- Keep quick actions limited to the current step:
  - explain missing context
  - explain the top exception
  - guide approval
  - explain what happens automatically next
- Reset the focus context when the user leaves the scoped control-plane path.
- Do not fall back to generic “continue with agent” wording unless there is truly no focused object.

## Validation

1. service responses for `Today / Goal Canvas / Product` resolve the same focus object and reason
2. browser smoke proves the agent opens with the same focused step the page is already explaining
3. CTA copy avoids generic “agent” verbs when the system already knows the current action

## Avoid

- agent panels that default to marketing their generic abilities
- separate agent-only reasoning models that disagree with the current control plane
- default browser-agent UI as the explanation layer for why the current step matters
