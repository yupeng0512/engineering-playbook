---
title: structured-intent-launcher-over-static-agent-prompt
type: note
permalink: engineering-playbook/patterns/structured-intent-launcher-over-static-agent-prompt
---

# Structured Intent Launcher Over Static Agent Prompt

## Context

Agent-centric products often start with a simple CTA:

- user clicks a button
- frontend sends a fixed prompt into chat
- agent starts working

This works only while the product has:

- one obvious object
- one stable stage
- one consistent bottleneck

Once the workspace grows into:

- multiple products
- multiple pipeline stages
- setup gaps
- competing bottlenecks such as approvals, replies, or closing work

the fixed CTA prompt becomes misleading.

## Pattern

Replace hard-coded prompt CTAs with a two-step launch flow:

1. frontend launches a structured intent
2. backend prepares the final agent prompt from current context

Recommended shape:

- `intent`
- `recommended_object_ids`
- `alternate_object_ids`
- `why_now_code`
- `required_review_points[]`
- `launch_mode`

Then add a prepare endpoint such as:

- `POST /agent/intents/prepare`

The backend turns the structured intent into:

- final `agent_prompt`
- localized `why now` explanation
- required review notes
- object-specific execution scope

## Why It Works

- The system can explain **why this is the right action now**, instead of pretending every state maps to the same prompt.
- Multi-object products no longer force the user to manually rebuild context every time.
- The frontend keeps a stable interaction contract while the backend evolves launch heuristics.
- It becomes much easier to switch behavior by stage:
  - missing context -> fill context
  - pending approvals -> review approvals
  - low supply -> continue discovery
  - active opportunity -> advance close

## Implementation Notes

- Keep the frontend intent layer semantic, not prompt-heavy.
- Let the backend own stage-aware prompt assembly.
- Support a `launch_mode` to distinguish:
  - direct launch
  - launcher/select flow
  - route to setup/detail page
- Keep user-facing explanation localized, but let outbound language policy remain separate.
- When multi-select is allowed, cap it to a small number such as `3` to avoid bloated prompts and unclear execution scope.

## When To Use

- AI workbenches
- agent copilots with multiple objects or products
- GTM / SDR tools
- workflow products where the top CTA changes with stage and bottleneck

## Anti-Patterns

- Frontend buttons that always inject the same long prompt into chat
- Static CTA copy that ignores setup completeness or current bottleneck
- Treating “continue” as a universal action across all products and stages
- Mixing user-facing explanation with buyer-facing generated language in the same launch string
