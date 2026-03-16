---
title: protect-first-screen-api-budget
type: note
permalink: engineering-playbook/patterns/protect-first-screen-api-budget
---

# Protect First-Screen API Budget

## Problem

Interactive workbenches often fail for the wrong reason:

- the main page requests are valid
- the side widgets are also valid
- the chat/session panel is also valid
- the notification bell is also valid

But all of them fire at once on first paint.

With a modest per-user rate limit, the result is self-inflicted instability:

- summary previews return `429`
- click-to-open sheets fail intermittently
- browser smoke tests become flaky
- users see `too_many_requests` on pages that should feel calm

## Pattern

Treat the first screen like a fixed API budget.

Split requests into two groups:

1. **critical first-screen reads**
   Requests required to render the user's primary task area.
2. **secondary chrome reads**
   Requests for helpful but non-blocking UI such as:
   - notification popovers
   - agent session history
   - sidebar diagnostics
   - secondary counters that do not affect the main CTA

Critical reads may load immediately.

Secondary chrome should use one of:

- lazy load on open
- delayed prefetch after the page stabilizes
- background refresh only after the initial render is complete

## Recommended Rules

- Do not auto-fetch side-panel history if the panel is closed.
- Do not fetch notification lists at page mount just to render a bell.
- If a secondary widget still needs early freshness, use delayed prefetch instead of first-paint fetch.
- Keep retry ownership explicit so background widgets do not silently multiply request pressure.
- Reserve rate-limit headroom for post-load user actions such as opening previews, approving drafts, or switching focus.

## Trade-off

This pattern deliberately prefers:

- stable first interaction
- fewer false `429`
- calmer dashboards

over:

- instantly fresh secondary chrome

That trade is usually correct for an operator workbench.

## When To Use

- dashboards with 6+ initial API reads
- pages protected by per-user or per-IP rate limiting
- workbenches where the first click must be reliable
- apps with chat panels, notifications, and other mounted chrome

## Anti-Pattern

Avoid mounting all of these at once:

- main task queries
- header/profile fetches
- notification feed fetches
- chat/session history fetches
- preview requests triggered immediately after load

Even if each request is reasonable alone, the aggregate behavior is not.
