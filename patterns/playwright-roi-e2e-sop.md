---
title: playwright-roi-e2e-sop
type: note
permalink: engineering-playbook/patterns/playwright-roi-e2e-sop
---

# Playwright ROI-First E2E SOP

## Purpose

Use Playwright as the default browser-level hard gate when the risk has moved from "code compiles" to "real users click through this flow."

This SOP is designed to keep browser testing:

- high-signal
- low-cost
- deterministic
- easy to expand from smoke tests into full end-to-end flows

## Core principle

Do not start with "cover everything in the browser."

Start with the smallest browser suite that can catch the most expensive real failures:

1. client-side crashes
2. broken navigation
3. missing approval/review handoffs
4. onboarding or first-run dead ends
5. state-dependent UI regressions that unit/build checks cannot see

## Testing ladder

### Level 0: Compile / unit

Use build, lint, type-check, service tests, and handler tests first.

Do **not** spend browser time on problems a compiler or service test can catch cheaper.

### Level 1: Browser smoke

Add a small Playwright suite only for the highest-risk user paths.

Typical size:

- 1 auth setup
- 3-6 smoke tests

Typical targets:

- top workbench CTA
- highest-frequency tab switch
- approval queue
- preview/deeplink flow
- onboarding / guide closure

### Level 2: Single-flow E2E

After the smoke layer proves stable, add one real business flow end to end.

Examples:

- product setup -> launch mining -> first draft approval
- inbox reply -> draft approval -> close-stage advance
- quote -> order doc -> handoff gate

Keep it to one or two golden paths first.

### Level 3: Scenario matrix

Only after Levels 1-2 are stable, expand to variations:

- empty vs non-empty states
- locale differences
- mobile behavior
- permission or plan differences
- retry / partial failure flows

Do not jump to this layer too early.

## SOP workflow

### 1. Choose the path by user pain, not feature count

Select flows based on:

- how often users touch them
- how expensive a failure is
- whether browser behavior is essential

Good triggers:

- "clicking this crashes the page"
- "this CTA says view all but does not navigate"
- "the guide stops halfway"
- "the state looks correct in API responses but fails in UI"

### 2. Stabilize the UI contract before writing the test

Before adding Playwright:

- add stable `data-testid` hooks
- add stable `data-tour` hooks for guided experiences
- normalize empty collections (`[]`, not `null`)
- make drill-down CTAs use real navigation semantics

If the UI contract is unstable, the test will only expose noise.

### 3. Add deterministic auth

Prefer a cheap, deterministic login path:

- dev OTP
- seeded test user
- storage state reuse

Avoid making every test re-run the full login flow unless auth itself is under test.

Recommended pattern:

- one `setup` project
- save storage state
- reuse storage state in browser project(s)

### 4. Test real runtime, not just local component state

Default the suite to the same runtime users actually hit:

- local production-like container
- staging URL
- preview URL

Avoid testing only dev-only behavior if production routing or middleware matters.

### 5. Keep each smoke test single-purpose

A smoke test should answer one question:

- Does this path crash?
- Does this CTA navigate?
- Does this sheet preview open?
- Can the guide complete?

If a test needs too many assertions to explain itself, split it.

### 6. Promote only proven smokes into deeper E2E

Once the smoke layer has stayed green for a while:

- choose one golden path
- seed or prepare just enough data
- verify the full user loop

Do not build a large E2E matrix before the smoke layer is trusted.

## Browser test design rules

### Prefer

- stable `data-testid`
- semantic links for navigation
- `expect(page).toHaveURL(...)`
- explicit empty-state assertions
- storage-state auth reuse
- one worker by default for small deterministic suites

### Avoid

- fragile text-only selectors for core flows
- relying on incidental animation timing
- testing against stale local dev state
- broad "everything on page" assertions
- browser tests for logic already fully covered in service/unit tests

## Data strategy

Use the cheapest data source that still exercises the real UI:

1. existing dev fixtures
2. seeded records
3. deterministic dev auth/test APIs
4. last resort: manual setup inside the test

If the UI is empty by default, decide explicitly:

- either assert the empty state
- or seed just enough data to test the intended behavior

Do not let tests silently depend on whatever data happened to be present.

### Add one noisy real-data walkthrough before sign-off

Seeded smoke tests are necessary, but they are not enough when the product already has:

- legacy records
- duplicate objects
- partially migrated state
- real user content

Before sign-off on a user-facing flow, add one lightweight walkthrough against a real account or a noisy fixture set and look for:

- duplicate cards or duplicated entities
- stale previews from a different object
- over-verbose or repetitive copy
- hidden polling / request storms / 429s
- mismatches between canonical surfaces and summary surfaces

The goal is not to replace deterministic smokes.

The goal is to catch the class of regressions that only appear once the UI meets real, messy product state.

## Failure triage loop

When a Playwright test fails:

1. check if the runtime actually contains the newest code
2. inspect screenshot + error context before patching
3. decide whether the problem is:
   - stale runtime
   - brittle selector
   - broken UI contract
   - real product bug
4. fix the product bug first when possible
5. only relax the test if the product behavior was actually valid

## Recommended repository structure

```text
web/
  playwright.config.ts
  tests/
    e2e/
      auth.setup.ts
      support.ts
      *.spec.ts
docs/
  QA-playwright-smoke.md
```

## Minimal command set

```bash
npm run test:e2e
npx playwright test --headed
npx playwright test tests/e2e/workbench-smoke.spec.ts
```

## Definition of done

A Playwright layer is "good enough" when:

- it catches real regressions users actually hit
- it stays small enough to run frequently
- its selectors are intentional, not accidental
- it helps close browser-only gaps that build/unit tests miss
- it provides a clean path to promote one smoke into one true E2E flow later

## Escalation rule

If the product keeps shipping browser regressions in the same flow,

- do not add more random smokes
- promote that flow into a real seeded end-to-end scenario
- make it part of the default release gate
