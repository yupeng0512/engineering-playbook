---
title: workbench-local-guided-tours
type: note
permalink: engineering-playbook/patterns/workbench-local-guided-tours
---

# Workbench-Local Guided Tours

## Pattern

Keep product tours anchored inside the primary daily workbench whenever possible instead of hopping across multiple routes.

## Why

- Cross-route tours are fragile because they depend on route timing, page readiness, and selector availability across several screens.
- When the product's main promise is "do your daily work from one command center," a tour that keeps pulling users out to secondary pages teaches the wrong mental model.
- Stable in-page anchors are easier to test with Playwright and easier for users to resume after interruption.

## Use when

- The product has a primary workbench or command center.
- Secondary pages exist, but they are meant to be entered only when needed.
- You need a short onboarding or re-onboarding flow that should survive layout and routing changes.

## Example shape

1. Start from today's main action card.
2. Point to the door for adding missing context.
3. Point to the door for configuring defaults or policy.
4. Point to the main execution trigger.
5. End at the approval or review boundary.

## Anti-pattern

Avoid tours like:

`dashboard -> products -> settings -> dashboard -> inbox`

unless the product truly requires users to internalize that multi-page flow on day one.

## Notes

- Prefer stable `data-tour` anchors over selectors tied to transient content.
- Keep drill-down pages available from the tour narrative, but present them as "doors" rather than mandatory stops.
- Validate the tour with a real browser smoke test, not only unit or DOM-level checks.