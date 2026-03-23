---
title: derive-reusable-memory-candidates-from-repeated-accepted-fixes-without-live-auto-write
type: note
tags: [pattern, automation, control-plane, memory, reuse, operator-os]
permalink: engineering-playbook/patterns/derive-reusable-memory-candidates-from-repeated-accepted-fixes-without-live-auto-write
---

# Derive Reusable Memory Candidates From Repeated Accepted Fixes Without Live Auto-Write

## Pattern

When users repeatedly accept the same product- or record-specific fix across similar objects, do not keep forcing them to repeat that fix forever.

Instead:

- detect repeated accepted fixes inside a confirmed family or reuse scope
- propose a reusable memory candidate once
- ask the user to confirm or reject it
- apply the result as future **suggested prefills**, not as direct live writes

## Good Scope

Good candidates are high-signal but still require per-object confirmation, such as:

- keyword seed sets
- ICP hints
- value-proposition skeletons
- localized intro lines

Do **not** auto-promote:

- sender identity
- send windows
- safety budgets
- locale policies
- template skeleton defaults
- commercial offers
- buyer pain claims
- quote/package/handoff content

## Why

After a product already has:

- a single-focus control plane
- confirm-once operating defaults
- exception-first automation

the next source of friction is often repeated “small but not fully safe to inherit” fixes.

If those fixes stay fully manual forever, the system remains helpful but never learns enough to reduce repetitive confirmation work across a portfolio.

## Recommended Shape

Use three layers:

1. `DefaultBundle`
   - safe operating defaults
   - approved once and inherited automatically
2. `MemoryCandidate`
   - derived from repeated accepted fixes
   - requires one portfolio-level confirmation
3. `DerivedReusePreview`
   - shown on each object as a suggested prefill
   - still requires per-object confirmation

## Rules

- Only derive memory inside a confirmed family or approved reuse scope.
- Use a threshold greater than one; `2 accepted examples` is a strong default.
- Require at least one other similar object that is still missing the field before surfacing a candidate.
- Never convert memory directly into live truth.
- Rejected candidates should not keep reappearing unchanged.
- Memory candidates should never outrank true high-priority exceptions.

## Validation

1. service tests prove two accepted examples create a candidate, one example does not
2. service tests prove confirm creates previews but not live writes
3. service tests prove reject suppresses repeated unchanged suggestions
4. service tests prove high-priority exceptions still outrank memory suggestions

## Avoid

- promoting repeated fixes straight into live facts
- mixing safe operating defaults and derived memory into one reuse mechanism
- surfacing memory candidates before exception handling and safety-critical work
- forcing users to manually maintain a taxonomy before they can benefit from memory reuse
