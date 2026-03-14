---
title: single-retry-owner-in-client-stack
type: note
permalink: engineering-playbook/patterns/single-retry-owner-in-client-stack
---

# Single Retry Owner In Client Stack

## Context

When a frontend has both:

- a global `window.fetch` patch or interceptor
- a local API client with its own retry/backoff logic

it is easy to accidentally retry the same request twice.

That creates hidden request amplification:

- one logical read becomes multiple network calls
- rate limits get worse instead of better
- UI noise increases because more failures race back into the page

## Pattern

Choose one clear retry owner for each request path.

Recommended split:

- `global fetch` layer: cross-cutting concerns for raw page fetches that do not use the API client
- `api client` layer: owned retry/backoff for requests that go through the typed client

If both layers must coexist, add an explicit opt-out flag so one layer can skip retry when the other already owns it.

## Example

- API client adds a sentinel header like `x-traderadar-no-layout-retry: 1`
- layout-level `fetch` patch checks that header before retrying `429 GET`

This keeps:

- one retry policy per request path
- predictable backoff behavior
- smaller blast radius during rate limiting

## Why It Matters

Duplicate retries are easy to miss in review because each layer looks reasonable in isolation.

The bug only appears at runtime:

- more `429`
- more duplicate toasts
- slower recovery
- noisier logs

## Use When

- the app mixes raw `fetch(...)` and a custom API wrapper
- some pages live outside the wrapper for historical reasons
- rate-limited APIs or quota-limited backends are involved

## Avoid

- stacking retries in interceptors, wrappers, and page code at the same time
- adding silent retries in a second layer without first mapping existing retry ownership