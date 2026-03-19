---
title: write-back-expert-surface-mutations-into-orchestrated-runs
type: note
permalink: engineering-playbook/patterns/write-back-expert-surface-mutations-into-orchestrated-runs
date: 2026-03-19
tags:
- product
- ai
- agent
- workflow
- orchestration
- ux
---

# Write Back Expert-Surface Mutations Into Orchestrated Runs

## Problem

Agentic operator products often evolve into this shape:

- a workbench or goal hub decides what should happen next
- a guided canvas tracks the current execution chain
- expert surfaces remain the source of truth for real edits

The failure mode appears when the user leaves the canvas, completes a real mutation in an expert surface, and the orchestration layer does **not** automatically learn that anything happened.

Then the user must:

- go back to the canvas
- re-open the same run
- manually advance or re-explain the state

This turns the run into a smart note, not a continuous execution system.

## Pattern

Treat successful expert-surface mutations as **writeback events** into the active orchestrated run.

Keep it lightweight:

- no generic event bus
- no BPM platform
- no new task-center page

Instead:

- persist a small run event record
- match it to the latest active run for that root object
- rebuild run state from **facts first**, with events only filling continuity gaps
- let the workbench/canvas automatically show the new checkpoint

## Recommended Rules

- Keep business truth in the underlying records, not in the run event alone.
- Use events only to bridge continuity between surfaces.
- Match runs by the user’s real working object:
  - thread-first for buyer-change resolution
  - opportunity for package/handoff progression
- Only write back on successful mutation boundaries such as:
  - proposal applied
  - product linked
  - quote revised
  - package generated
  - reply queued
  - order readiness promoted
  - finance handoff prepared
- Do not require a “refresh run” or “I finished this” button if the system already observed a successful write.
- Keep expert pages available as inspect / edit / fallback; do not force everything through the canvas.

## Why This Works

This pattern removes a hidden but expensive cognitive tax:

- the user no longer needs to synchronize the system manually
- the run becomes a continuous execution rail instead of a second state machine to babysit
- guided repair stops being a local patch and becomes part of one end-to-end flow

It improves:

- time from action completion to next recommended step
- confidence that the system “knows what just happened”
- continuity between workbench, canvas, and expert pages

## Good Example

- `Today` surfaces a package progression run.
- The user opens the opportunity expert page to link a missing product.
- The product-link mutation succeeds.
- A small `product_linked` run event is recorded.
- Re-opening the run shows the product repair checkpoint already cleared and the next package step ready.

## Anti-Pattern

Avoid this sequence:

- tell the user to go to the expert page
- let them complete the real action
- require them to come back and click “continue” just so the system can catch up

That is not orchestration.
That is manual synchronization disguised as workflow.
