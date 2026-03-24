---
title: Stable Empty Collection Contracts
type: note
tags:
- pattern
- api
- golang
- frontend
- reliability
permalink: engineering-playbook/patterns/stable-empty-collection-contracts
---

# Stable Empty Collection Contracts

When an API returns UI-facing collections, treat `[]` as part of the contract. Do not let nil slices leak into JSON as `null` when the frontend expects “an empty list that can still render”.

## Observations

- [insight] In Go, a nil slice serializes to `null`, while an initialized empty slice serializes to `[]`; that difference is often invisible on the backend but can crash frontend code that calls `.length`, `.map`, or iterates without null guards. #golang #json #api-contract
- [technique] The most reliable pattern is backend-first plus frontend-normalize: initialize response slices to empty arrays in the service/handler layer, then normalize again in the UI fetch layer to protect against older deployments, partial rollouts, or malformed payloads. #defense-in-depth #frontend-reliability
- [problem] “Click -> client-side exception” bugs are often data-contract bugs rather than button bugs; if a focus switch or tab change loads a different API payload, the first debugging step should be to inspect the real user-facing JSON contract. #debugging #contract-first
- [solution] Regression tests should cover the “no mapped items and no fallback items” path explicitly, because that is where nil slices most often escape into production. #testing #edge-cases
- [insight] The same contract applies to schema-bound AI requests, not just browser-facing APIs: if an LLM or agent service validates request bodies with Pydantic/JSON Schema, `null` for a list-or-dict field can fail the entire action before model inference even begins. #ai-systems #schema-validation
- [technique] When building AI request envelopes with optional context blocks, initialize top-level list/dict fields to empty arrays/objects first, then selectively populate them. This keeps the payload semantically explicit and avoids “saved nothing, sent null” validation failures. #backend #reliability
- [solution] Add at least one serialization test that asserts important collection/map fields do not marshal as `null`; this catches regressions earlier than an expensive end-to-end “click generate draft” repro. #testing #roi

## Relations

- implements [[frontend-backend-data-sync]]
- relates_to [[single-retry-owner-in-client-stack]]
