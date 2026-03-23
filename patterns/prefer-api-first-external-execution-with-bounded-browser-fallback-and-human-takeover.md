---
title: prefer-api-first-external-execution-with-bounded-browser-fallback-and-human-takeover
type: note
tags: [pattern, adapters, automation, browser, control-plane, safety]
permalink: engineering-playbook/patterns/prefer-api-first-external-execution-with-bounded-browser-fallback-and-human-takeover
---

# Prefer API-First External Execution With Bounded Browser Fallback And Human Takeover

## Pattern

When a product needs to prepare state in external systems, do not default to a browser agent just because browser automation is available.

Instead:

- prefer official API adapters whenever they exist
- allow browser execution only as a bounded fallback
- record external runs as first-class evidence objects
- request human takeover only when the browser fallback reaches uncertainty

## Why

Browser automation is powerful, but it is a poor default interaction model for a control-plane product.

The control plane should keep answering:

- what is happening
- why it matters
- whether it succeeded
- why human takeover is needed

API-first execution makes those boundaries clearer, easier to test, and easier to audit.

## Recommended Shape

Each external action should declare:

- `execution_backend = api | external_browser`
- `human_takeover_allowed`
- `writes_external_state`
- `target_system`
- `customer_facing`

Represent each attempt as an `ExternalExecutionRun` with:

- adapter key
- backend
- status
- evidence
- last error
- takeover state

## Rules

- If an official API exists, do not route the action through browser fallback.
- Limit browser fallback to low-risk preparation work:
  - verification
  - draft sync
  - queue preparation
- Keep buyer-facing send actions behind stricter rails.
- Expose browser fallback as secondary execution evidence, not as the product's default UI.
- Human takeover requests must explain:
  - where execution stopped
  - why automation is no longer safe
  - how to resume after takeover

## Validation

1. service tests prove API-capable adapters do not fall back to browser mode
2. service tests prove only whitelisted low-risk actions can use browser fallback
3. service tests prove uncertainty creates takeover requests, not silent failure
4. UI tests prove the control plane stays native while showing external execution evidence

## Avoid

- making browser agents the default UI for operator-facing workflows
- letting browser fallback perform arbitrary multistep exploration
- exposing unbounded browser execution directly to end users
- hiding external execution uncertainty instead of escalating to human takeover
