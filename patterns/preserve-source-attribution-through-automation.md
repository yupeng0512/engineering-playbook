---
title: preserve-source-attribution-through-automation
type: note
permalink: engineering-playbook/patterns/preserve-source-attribution-through-automation
---

# Preserve Source Attribution Through Automation

When an AI or automation pipeline discovers entities on behalf of a specific source object, keep that source attribution attached all the way through downstream queueing, approval, and execution.

## Why

If source attribution is lost after discovery, later stages can still "look" operational while silently degrading into generic/manual behavior:

- approval batches cannot inherit the right policy
- risk and threshold rules fall back to defaults
- UI explanations lose the answer to "why this now?"
- tests may pass on page shape but fail on real workflow semantics

## Practical rule

For every discovered or auto-prepared entity, preserve enough source context to reconstruct the originating object later.

Typical fields:

- `source_product_id`
- `source_product_name`
- `source_workflow_id`
- `source_campaign_id`

These fields do not need a heavy relational model on day one; lightweight structured metadata is often enough, as long as downstream services read from it consistently.

## Propagation chain

The source attribution should survive:

1. discovery / ingestion
2. prioritization or next-action generation
3. workstream/task projection
4. approval batching
5. execution or send boundary

If any layer drops the attribution, later automation becomes harder to explain and harder to validate.

## Testing implication

Golden-path E2E tests should verify not only that items appear, but that they appear with the correct source-derived behavior:

- correct policy mode
- correct batch threshold
- correct explanation / "why now"
- correct target route or ownership

Otherwise the system may be functionally alive but semantically wrong.