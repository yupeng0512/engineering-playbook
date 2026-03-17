---
title: default-collapse-supporting-surfaces-around-primary-goal
type: note
permalink: engineering-playbook/patterns/default-collapse-supporting-surfaces-around-primary-goal
date: 2026-03-17
tags:
- product
- ux
- ia
- navigation
- workbench
---

# Default-Collapse Supporting Surfaces Around The Primary Goal

## Problem

Operator products often improve capability faster than they improve startup clarity.

The common failure mode looks like this:

- the home page keeps every module visible
- analytics, queues, setup, summaries, and previews all compete at the same level
- a new AI surface is added on top of that density

The product technically becomes more capable, but the user pays a hidden cost:

- they do not know what to do first
- they cannot tell what is primary vs supporting
- blocked states and secondary context compete with the main action

## Pattern

Keep supporting surfaces available, but **collapse them by default**.

Recommended structure:

- show one primary goal above the fold
- show one why-now explanation
- show one blocked reason when relevant
- keep supporting queues, summaries, setup, and reports behind a secondary rail or drawer
- let the operator expand those surfaces only when needed

This is different from deleting modules:

- expert pages still exist
- supporting surfaces still exist
- the default view simply stops treating them as peers to the primary task

## Why It Works

This reduces two kinds of cognitive cost at the same time:

- **usage mindshare cost**: fewer same-level choices on first load
- **visual mindshare cost**: less dense competition for attention

It also keeps the system auditable:

- supporting context is compressed, not hidden forever
- expert routes remain the source of truth
- the user can still inspect details before acting

## Recommended Rules

- Default-open only the primary goal path.
- Collapse supporting surfaces into a rail or drawer.
- Persist collapse state locally first; do not introduce a new server preference object unless cross-device continuity is proven necessary.
- Treat support-surface expansion as a meaningful telemetry event.
- Preserve expert routes as inspect / edit / fallback destinations.
- Do not ship hard navigation removal before adoption data proves the compressed entry point works.

## Good Example

- `Today` shows one recommended goal, why-now, and the continue action.
- approvals, summary cards, setup checklists, streams, and autopilot diagnostics sit behind a collapsed support rail.
- `Goal Canvas` shows the main execution surface first.
- reports, sessions, memory, and safe actions move to a support drawer instead of staying in a permanent third column.

## Anti-Pattern

Avoid these designs:

- leaving every supporting card open by default because “power users might want it”
- hiding all secondary context entirely and forcing users to trust a black box
- treating dense dashboards as the only way to prove the system is powerful

The right move is usually:

**default-compress, not default-hide, and not default-sprawl**
