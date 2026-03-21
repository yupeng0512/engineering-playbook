---
title: combine-rule-extraction-with-bounded-llm-fallback-before-user-confirmation
type: note
permalink: engineering-playbook/patterns/combine-rule-extraction-with-bounded-llm-fallback-before-user-confirmation
date: 2026-03-21
tags:
- pattern
- ai
- extraction
- intake
- operator-os
- confirmation
---

# Combine Rule Extraction With Bounded LLM Fallback Before User Confirmation

## Problem

For intake-heavy operator products, pure rule extraction is often too brittle:

- it works when the text has explicit markers
- it fails on weak or natural-language-heavy inputs
- it leaves the operator to manually fill too much missing context

But pure LLM extraction is also risky:

- it can hallucinate fields
- it can overwrite strong deterministic evidence
- it can make the system feel opaque

## Pattern

Use a four-step pipeline:

1. run deterministic extraction first
2. detect which fields are missing, weak, or conflicting
3. call an LLM only for those bounded gaps
4. show the operator field-level candidates with source, confidence, and evidence before confirmation

The goal is not “more AI”.
The goal is making intake feel like:

- the system understood most of it
- the user only confirms or edits the uncertain parts

## Recommended Output Shape

For each extracted field, return something like:

- `final_candidate`
- `candidate_source = rule | llm | merged`
- `confidence`
- `evidence[]`
- `confirmation_required`

For keywords or tags, explicitly distinguish:

- `rule-derived`
- `llm-derived`

## Guardrails

- Run rules first. Treat them as the deterministic anchor.
- Trigger LLM fallback only for bounded gaps:
  - missing required fields
  - weak low-signal candidates
  - scope conflicts
- Keep the LLM on a narrow schema.
- Do not let the LLM directly write live facts.
- Require human confirmation before proposal apply / record mutation.
- Preserve evidence so the user can understand why a value was suggested.

## Why This Works

This avoids the two common failure modes:

- pure rules:
  - too much operator cleanup
- pure LLM:
  - too much hidden guesswork

Instead the product feels system-led but still trustworthy:

- deterministic where possible
- probabilistic only where needed
- human-confirmed before writeback

## Good Fit

This pattern works especially well for:

- product / artifact intake
- commercial context extraction
- reply or handoff preparation
- any workflow where the system should prepare structure without silently committing truth

## Avoid

- calling the LLM for every artifact even when rules are already sufficient
- returning only one opaque merged value without source or confidence
- letting LLM output skip the confirmation step
- using the fallback path to hide incomplete schema design
