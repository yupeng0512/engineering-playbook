---
title: assert-cta-semantics-not-just-visibility
type: note
permalink: engineering-playbook/patterns/assert-cta-semantics-not-just-visibility
---

# Assert CTA Semantics, Not Just Visibility

## Problem

UI tests often prove that a CTA exists and is clickable, but miss the more important question:

- does this button still mean what the product says it means?

That gap lets obvious product bugs survive:

- duplicate CTAs with different labels but the same route
- onboarding steps anchored to the wrong control
- “primary” actions that silently drift into settings or fallback states

## Pattern

For important CTAs, test all three layers:

1. the control exists
2. the control has the expected semantic identity (`data-testid`, `data-tour`, route contract, or launch contract)
3. the click causes the intended outcome

## Recommended Rules

- Give important CTAs stable semantic anchors, not only visible text.
- If two CTAs look different, assert that they launch different intents or routes.
- For onboarding/tour steps, bind to the exact semantic anchor instead of permissive fallbacks.
- Add at least one browser smoke that verifies the CTA outcome, not only its presence.

## Benefit

- obvious UX regressions are caught before humans trip over them
- onboarding stays aligned with the real interface
- browser tests validate product meaning instead of shallow rendering
