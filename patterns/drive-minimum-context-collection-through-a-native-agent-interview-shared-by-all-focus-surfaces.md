---
title: drive-minimum-context-collection-through-a-native-agent-interview-shared-by-all-focus-surfaces
type: note
tags: [pattern, agent, control-plane, interview, operator-os, ux]
permalink: engineering-playbook/patterns/drive-minimum-context-collection-through-a-native-agent-interview-shared-by-all-focus-surfaces
---

# Drive Minimum Context Collection Through A Native Agent Interview Shared By All Focus Surfaces

## Pattern

When the system already knows which focused object is blocked and why, do not make users jump across multiple pages to fill `required_context`.

Instead:

- derive one shared `LaunchInterviewState` from the same focus context used by the control plane
- compress missing context into 3-7 high-leverage questions
- open the native agent in interview mode
- keep `Today`, `Goal Canvas`, and `Product` showing the same summary while the agent handles the actual Q&A

## Why

If the UI says:

- here is the one focused object
- here is the one missing thing

but the user still has to navigate several pages to answer it, the system knows the next step but has not yet compressed the work.

The highest-ROI move is to turn scattered configuration holes into one minimal guided interview.

## Recommended Shape

Use one interview state with:

- `focus_object_id`
- `goal_key`
- `questions[]`
- `current_question`
- `portfolio_impact`
- `readiness_delta`
- `next_after_complete`

Question priority should stay fixed:

1. reusable defaults
2. reusable memory candidates
3. product- or record-specific gaps
4. low-risk operational requirements

## Rules

- Keep the native agent as the default interview host; do not create a second wizard unless the agent model cannot support the flow.
- Write answers back by scope:
  - safe defaults -> draft/revision scope
  - reusable memory -> confirm/reject scope
  - object-specific answers -> current object only
- Return a `readiness delta` after each meaningful answer or at completion.
- Pause or suppress the interview if a truly high-priority exception appears.
- Do not silently convert agent answers into unreviewed live truth.

## Validation

1. service tests prove question priority order is stable
2. service tests prove answers write only to the intended scope
3. browser smoke proves the main CTA opens the native agent interview instead of routing to a new wizard
4. browser smoke proves the control-plane summary remains consistent while the interview is active

## Avoid

- giant onboarding centers
- per-page manual context filling once the system already knows the missing fields
- agent interviews that bypass scope boundaries and mutate approved defaults directly
- generic “continue with agent” UI when the system already knows the exact missing context
