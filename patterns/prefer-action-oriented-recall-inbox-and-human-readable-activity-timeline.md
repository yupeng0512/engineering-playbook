---
title: prefer-action-oriented-recall-inbox-and-human-readable-activity-timeline
type: note
tags: [pattern, product-language, observability, ux, operator-os]
permalink: engineering-playbook/patterns/prefer-action-oriented-recall-inbox-and-human-readable-activity-timeline
---

# Prefer Action-Oriented Recall Inbox And Human-Readable Activity Timeline

## Pattern

When a system is already doing meaningful work on the user's behalf, do not expose that state through:

- a generic notification center
- a raw system log page
- a feed that mixes low-value success events with urgent human interruptions

Instead, separate the product language into two layers:

- recall inbox:
  - only shows things the user must return to handle now
- activity timeline:
  - explains what the system already did, what it is waiting on, and what it will do next

## Why

Generic notification centers quickly become noisy:

- they over-count low-value events
- they hide urgent interruptions inside passive feed items
- they teach users to ignore the bell

Raw logs have the opposite problem:

- they maximize transparency
- but they externalize internal system complexity to the user

Operator-style products need a middle layer:

- action-oriented recall for interruption
- human-readable timeline for observability

## Recommended shape

Use a recall model with fields such as:

- `kind`
- `title`
- `summary`
- `priority`
- `reason`
- `recommended_action`
- `route`

And keep it limited to actionable states such as:

- needs context
- needs approval
- high-priority exception
- buyer reply
- human takeover required
- policy conflict

Use a separate timeline model with fields such as:

- `category`
- `status`
- `title`
- `summary`
- `occurred_at`
- `actor`
- `evidence_available`

## Rules

- The bell should count actionable recall items, not all events.
- The default drawer should open a recall inbox, not a notification feed.
- The primary work surface should show a compact activity summary for the current object or session.
- Product and customer views should show human-readable timelines, not raw traces.
- Default execution surfaces must not directly render machine terms such as `first-touch`, `follow-up`, `buyer reply`, `step-*`, or other raw workflow-engine tokens.
- Keep a small product-language mapping layer between machine codes and UI copy; expert/debug labels may survive in evidence layers, but default surfaces should speak in user task language.
- Default execution surfaces must not treat backend freeform English summaries as safe UI copy by default. Operator-facing automation language should still be derived from frontend-owned i18n/product-language mappings, or from tightly bounded label enums.
- Fallback behavior must obey the same rule: if a translation or label lookup misses, fall back to safe product-language copy, never to a raw enum or a quick `replace("_", " ")`.
- When the backend returns explanatory facts or evidence strings, separate the stable signal from the rendered sentence. Pass kinds, statuses, field paths, and counts forward; let the frontend compose the final operator-facing sentence.
- The same rule applies to missing-item or requirement lists. Pass stable keys such as `quote_basis` or `payment_terms`, not already-rendered English labels, so the frontend can localize and normalize them consistently.
- Recall timestamps must come from real event time. Never fabricate "just now" from the existence of a route or a recall item.
- Timeline badges must translate internal enums such as `needs_review` or `external_execution` into human-readable product language before rendering.
- Raw logs, traces, replay, and provider evidence should stay behind an evidence drawer or expert layer.
- Calm-running and done-for-now states should still be represented in the timeline, so the system feels active rather than silent.

## Validation

1. The recall inbox returns only actionable items.
2. Success events do not increase the bell count.
3. Recall freshness reflects real event timestamps, not UI-generated pseudo time.
4. The work surface can explain current progress without exposing raw system logs or raw internal enums.
5. Evidence remains available, but only after drill-down.
6. Backend explanatory English should not leak directly into operator-facing default surfaces unless it is already a bounded, localized label contract.
