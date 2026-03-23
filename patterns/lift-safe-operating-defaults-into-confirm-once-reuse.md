---
title: lift-safe-operating-defaults-into-confirm-once-reuse
type: note
tags: [pattern, automation, control-plane, defaults, operator-os]
permalink: engineering-playbook/patterns/lift-safe-operating-defaults-into-confirm-once-reuse
---

# Lift Safe Operating Defaults Into Confirm-Once Reuse

## Pattern

When an operator product manages many similar objects, do not make the user repeat the same low-risk operating setup for each object.

Instead:

- let the system detect reusable default bundles
- show one reusable suggestion with clear reasons
- ask the user to confirm or reject it once
- let future similar objects inherit those defaults automatically

## Good Scope

Only lift defaults that are operational and low-risk, such as:

- sender identity
- send window
- safety budget
- locale policy
- template skeletons
- disclaimer/compliance blocks

Do **not** auto-reuse strategy or positioning fields such as:

- ICP
- value proposition
- commercial offer
- buyer pain
- product-specific claims

## Why

Once the default IA is already compressed into a single-focus control plane, the next major source of friction is usually repetition across many similar objects.

If the user still has to re-approve the same sender, window, locale, and template setup for every product or campaign, the product remains efficient per object but not efficient per portfolio.

## Recommended Shape

Use three layers:

1. `FamilyCandidate`
   - system-suggested grouping
   - carries reason, confidence, shared default preview, eligible object ids
2. `DefaultBundle`
   - approved reusable defaults
   - scoped to the confirmed family candidate
3. `InheritedDefaultPreview`
   - shown on each object control plane so the operator can see what came from reuse vs. what still needs object-specific confirmation

## Rules

- Do not require users to create and maintain taxonomy first.
- Prefer system-suggested family candidates plus one user confirmation.
- Rejected family suggestions should not keep reappearing unchanged.
- Keep the default UI single-focus even when the backend is doing portfolio-level supervision.
- Let reusable gaps outrank repeated per-object setup gaps when fixing one gap unlocks many objects.

## Validation

1. service tests prove low-risk defaults inherit across similar objects
2. service tests prove strategy fields do not inherit
3. service tests prove rejected family candidates stop repeating
4. browser smoke proves the default UI still shows one CTA, not a giant portfolio list

## Avoid

- forcing users to define product families before they can benefit from reuse
- silently auto-inheriting strategy/positioning fields
- reintroducing a giant portfolio center just because the backend now understands reuse
