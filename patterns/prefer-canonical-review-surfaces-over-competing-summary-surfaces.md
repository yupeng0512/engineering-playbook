---
title: prefer-canonical-review-surfaces-over-competing-summary-surfaces
type: note
tags: [pattern, ux, product, surface-ownership, operator-os]
permalink: engineering-playbook/patterns/prefer-canonical-review-surfaces-over-competing-summary-surfaces
---

# Prefer Canonical Review Surfaces Over Competing Summary Surfaces

## Pattern

When a product contains both:

- a high-context object summary surface
- and a high-fidelity review surface for a narrower scope

do not let both surfaces grow into partial versions of the same workflow.

Instead:

- assign canonical ownership of the detailed review workflow to exactly one surface
- keep the broader surface focused on summary, recall, and lightweight preview
- route every "I need to actually review/approve/respond" action into the canonical review surface

## Why

Once two surfaces both start rendering:

- partial timelines
- partial draft review
- partial decision controls

users lose trust in which one is the truth.

The result is usually:

- duplicated data fetching
- inconsistent chronology
- duplicated actions
- "black box" feelings because each page shows a different slice of the same object

Canonical ownership fixes that by making the product language explicit:

- summary surface answers: "what is going on overall?"
- review surface answers: "what exactly happened, what is the current draft, and what should I do now?"

## Recommended shape

Use a lightweight preview model on the summary surface, for example:

- `thread_id`
- `subject`
- `latest_activity_at`
- `status`
- `has_pending_draft`
- `message_preview[]`
- `open_review_route`

Reserve the full review payload for the canonical review surface, for example:

- full message chronology
- draft body and approval state
- qualification / recommended next step
- linked context needed to complete the review

## Rules

- A summary surface may show the latest 1-3 events or messages, but not the full review flow.
- A review surface owns the exact chronology and final actions.
- Recall items tied to review work should route directly to the canonical review surface.
- The summary surface should expose one clear CTA such as `Open thread review`, not a second set of draft-review controls.
- Avoid naming both surfaces with the same "timeline" semantics when they operate at different scopes.

## Validation

1. Users can clearly answer which page they should open to review/respond/approve.
2. The summary surface no longer contains duplicated draft-review controls.
3. The canonical review surface exposes the full chronology and decision state.
4. Recall items that require detailed review route directly into the canonical review surface.
5. The summary surface still gives enough preview context that the handoff does not feel blind.
