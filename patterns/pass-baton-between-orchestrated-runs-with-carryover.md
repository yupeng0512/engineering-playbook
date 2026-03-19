---
title: pass-baton-between-orchestrated-runs-with-carryover
type: note
permalink: engineering-playbook/patterns/pass-baton-between-orchestrated-runs-with-carryover
date: 2026-03-19
tags:
- product
- ai
- agent
- workflow
- orchestration
- continuity
---

# Pass Baton Between Orchestrated Runs With Carryover

## Problem

An agentic operator product can successfully orchestrate one run at a time and still feel discontinuous.

The common failure mode looks like this:

- a resolution chain finishes
- the system knows the result
- the next close-side chain should obviously start
- but the user still has to manually open a new run and restate context

At that point the product has continuity **inside** a run, but not continuity **between** runs.

## Pattern

Use lightweight predecessor/successor lineage on top of existing run primitives.

Do **not** introduce:

- a new workflow engine
- a task-center page
- a generic BPM platform

Instead:

- persist predecessor/successor run ids
- emit small transition events such as `successor_prepared` and `successor_refreshed`
- attach a structured carryover context to the successor run
- pause the successor when the predecessor reopens
- refresh the successor in place when the predecessor completes again

## Carryover Rules

Carry over only continuity context, not business truth.

Good carryover fields:

- summary of what just completed
- source refs
- confirmed commercial context snapshot
- quote refs / last transition summary
- open consistency issues
- resolved missing fields

Keep truth in the original records:

- quote
- opportunity
- commercial context
- readiness / handoff objects

Carryover is a continuity cache, not a new source of truth.

## Recommended Baton Rules

- Only prepare successors on high-confidence facts such as:
  - quote accepted
  - order readiness promoted
  - package chain reaching handoff boundary
- Reuse the latest active successor for the same root object instead of creating duplicates.
- If the predecessor reopens, set successor dependency to something explicit like `waiting_on_predecessor`.
- Do not let a paused successor keep winning the main workbench priority slot.
- If the predecessor closes lost, close the successor as well.

## Why This Works

This pattern removes a subtle but expensive operator burden:

- no manual “start next run”
- no re-entering already confirmed context
- no fake continuity where downstream work keeps moving after upstream reopened

It upgrades orchestration from:

- “the system remembers this run”

to:

- “the system knows how the next run inherits and depends on the previous one”

## Good Example

- A resolution run ends in `quote_accepted`.
- The system prepares a package progression successor.
- The successor already knows the confirmed commercial context and resolved missing fields.
- `Today` surfaces it as `continued from resolution`.
- Later, the buyer reopens negotiation.
- The predecessor resolution run reopens and the package successor is paused as `waiting_on_predecessor`.

The operator never needs to manually restart or manually pause the downstream chain.

## Anti-Pattern

Avoid this sequence:

- finish a run
- surface a new object with no lineage
- ask the user to re-confirm the same product, commercial commitment, or quote context
- keep downstream work active even after the upstream chain reopened

That is not baton passing.
That is state fragmentation.
