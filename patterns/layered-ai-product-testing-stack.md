---
title: layered-ai-product-testing-stack
type: note
permalink: engineering-playbook/patterns/layered-ai-product-testing-stack
---

# Layered AI Product Testing Stack

For AI-native products, do not collapse every testing problem into browser E2E.

Use a layered stack instead:

1. `PTY / script layer`
2. `API / service layer`
3. `Browser E2E layer`
4. `LLM / evaluator layer`

## 1. PTY / script layer

Use this for:

- deploy scripts
- rollback scripts
- health checks
- scenario seed/reset helpers
- environment bootstrapping

Why:

- cheapest layer for shell and operator workflow correctness
- catches env/path/permission regressions before browser time is spent

## 2. API / service layer

Use this for:

- state machine semantics
- policy merges
- idempotency
- aggregation
- approval logic
- queue/batch formation

Why:

- most business regressions are semantic, not visual
- deterministic and fast enough to run often

## 3. Browser E2E layer

Use this only when the risk is browser-shaped:

- click -> route
- preview -> deeplink
- guide completion
- approval action visible in UI
- client-side exceptions

Why:

- browser tests are expensive
- they should prove real operator workflows, not replace domain tests

## 4. LLM / evaluator layer

Use this for:

- draft quality regression
- structured extraction consistency
- prompt or tool-routing changes
- guardrail and policy conformance

Why:

- browser success does not prove model quality
- model quality should be measured with explicit fixtures and evaluators

## Flaky convergence order

When a browser test flakes, resolve it in this order:

1. stale runtime / stale container
2. hidden or non-visible target
3. unstable selector
4. first-screen API budget exhaustion
5. non-idempotent seed data
6. only then add retries or repeat runs

Retries are a pressure valve, not a diagnosis.

## Shared-auth concurrency rule

If browser suites depend on a shared login bootstrap or shared storage state, treat parallel invocations as a separate risk category.

Symptoms:

- one command passes alone but fails when two Playwright commands run at the same time
- auth setup intermittently cannot find OTP/code fields
- failures cluster around bootstrap, not around the actual feature under test

Recommended order:

1. first serialize the competing suites
2. then verify whether the flake disappears
3. only after that decide whether isolated per-shard auth state is worth the extra complexity

Do not mask shared-auth races with retries.

## Recommended release gating

- `PTY + API/service` layers: normal CI
- `Browser smoke`: normal CI or local hard gate
- `Golden-path browser E2E`: preview / pre-release gate
- `LLM evaluators`: nightly or targeted gate, then promote when stable

This keeps release confidence high without turning every PR into a heavy end-to-end gauntlet.
