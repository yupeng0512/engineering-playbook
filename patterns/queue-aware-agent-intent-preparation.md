---
title: queue-aware-agent-intent-preparation
type: note
permalink: engineering-playbook/patterns/queue-aware-agent-intent-preparation
---

# Queue-Aware Agent Intent Preparation

## Problem

Agent launch buttons often start as static prompts like "continue outreach" or "advance the deal."
This is easy to ship, but it breaks down quickly:

- The same button means different things at different stages.
- Multi-product workspaces need different scope each time.
- Users cannot tell why the system wants this action now.
- The prompt drifts away from the real queue state and loses trust.

## Pattern

Split the launch flow into two layers:

1. `intent`
   A stable semantic action such as `prepare_outreach`, `advance_close`, `discover_customers`.
2. `prepare`
   A server-side step that converts the intent plus live queue state into the actual agent prompt.

The prepare step should pull:

- current bucket counts
- top targets
- known blockers
- approval edge items
- fallback behavior when the queue is empty

The UI should send structure, not prose:

- `intent`
- `focus`
- optional `product_ids`
- `locale`

The backend should return:

- `agent_prompt`
- `why_now_code`
- `required_review_points`

## Why It Works

- The button keeps a stable meaning while the prompt stays situation-aware.
- Queue counts and top targets make the agent feel grounded in the user's current work.
- Empty-state fallbacks become explicit instead of degrading into vague generic prompts.
- Product and workflow changes no longer require copying prompt text across multiple clients.

## Anti-Pattern

Do not bind agent launch behavior to:

- fixed prompt strings in the frontend
- array position like "the second goal is outreach"
- UI copy that assumes the same stage forever

These shortcuts create silent mismatch between UI intent and backend reality.

## TradeRadar Example

- `prepare_outreach` should mention live outreach queue counts and top targets.
- `advance_close` should mention live close queue counts, blockers, and the next intervention point.
- When the queue is empty, the agent should pivot to "what is closest to send-ready" or "which thread should enter the close flow first" instead of pretending there is already a queue.