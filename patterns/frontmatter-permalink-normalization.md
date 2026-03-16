---
title: "Frontmatter & Permalink Normalization"
type: pattern
permalink: engineering-playbook/patterns/frontmatter-permalink-normalization
tags:
  - docs
  - metadata
  - knowledge-graph
  - pattern
---

# Frontmatter & Permalink Normalization

## Problem

When a project accumulates dozens of markdown files over many phases, document metadata drifts:

- some files have no frontmatter
- some have titles but no stable permalink
- some mix inconsistent `type` / `tags`
- graph-style tooling and later sessions can no longer rely on predictable metadata

This makes cross-session handoff, keyword-triggered retrieval, and knowledge-graph style indexing much less reliable.

## Pattern

Normalize the markdown corpus in one pass and treat metadata as a contract, not a nice-to-have.

Minimum contract for each project doc:

- `title`
- `type`
- `tags`
- `permalink`

Recommended permalink rule:

- prefix with the project namespace
- derive from the relative path
- keep it lowercase and stable
- do not encode dates or transient wording unless the path itself requires it

Example:

```yaml
---
title: "TradeRadar — 项目上下文"
type: context
tags: [trade-radar, docs, context]
permalink: trade-radar/docs/context
---
```

## When to do it

Do this when:

- the project has entered a multi-phase state
- docs are already being used as working memory
- different sessions or agents need to rediscover the same files reliably
- you want search/index/graph behavior to be deterministic

Do not wait until the corpus is already too messy to recover cheaply.

## Execution rules

1. Normalize in bulk, not file-by-file over many weeks.
2. Preserve existing frontmatter when present; merge instead of overwriting.
3. Use a deterministic permalink mapping from path, not ad hoc manual values.
4. Validate that every target doc now starts with frontmatter.
5. Update at least one project-level context file so future sessions know the corpus is normalized.

## Why it matters

The value is not cosmetic.

Stable metadata gives you:

- better retrieval by keyword and file identity
- cleaner cross-session handoff
- more reliable second-brain / graph linking
- lower drift when multiple agents or tools touch the same doc set

## Related

- relates_to [[Project Context Management]]
- relates_to [[Playwright ROI-First E2E SOP]]
