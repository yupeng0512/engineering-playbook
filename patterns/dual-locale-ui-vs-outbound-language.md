---
title: dual-locale-ui-vs-outbound-language
type: note
permalink: engineering-playbook/patterns/dual-locale-ui-vs-outbound-language
---

# Dual-Locale UI vs Outbound Language

## Context

AI-native B2B products often serve one operator language and a different buyer language at the same time.

Typical example:

- operator UI is Chinese
- buyer-facing outbound drafts default to English
- some markets should switch to a local language only when confidence is high

If the product uses a single "language" setting for both surfaces, one of two bad outcomes appears:

- the operator sees mixed-language UI and loses trust
- the system sends buyer-facing content in the wrong language

## Pattern

Split language into two explicit layers:

1. `ui_locale`
2. `outbound_language_policy`

`ui_locale` controls all user-facing product copy:

- buttons
- navigation
- errors
- empty states
- agent explanations
- task titles and reasons

`outbound_language_policy` controls only buyer-facing generated content:

- cold outreach drafts
- follow-up drafts
- reply drafts
- quote/package/order-document wording

Recommended default:

- UI locale follows operator preference
- outbound defaults to English
- local language is used only when market/language confidence is high

## Implementation Notes

- Return semantic codes from the backend for user-facing tasks and reasons when possible; render them in the frontend with locale-aware dictionaries.
- Pass outbound language explicitly into AI analyzers through a dedicated header or field such as `X-Outbound-Language`.
- Keep internal explanation prompts separate from buyer-facing generation prompts.
- Store a lightweight inferred buyer language profile, for example:
  - inferred country
  - inferred language
  - confidence
  - chosen outbound language

## Why It Works

- Preserves operator trust by keeping the workspace linguistically consistent.
- Keeps buyer-facing communication aligned with market expectations.
- Avoids the common anti-pattern where a global locale switch accidentally changes outbound draft language.
- Makes localization incremental: UI i18n and outbound-language heuristics can evolve independently.

## When To Use

- AI SDR / GTM tools
- cross-border commerce tools
- customer support copilots
- any product where operator language and audience language can differ

## Anti-Patterns

- One global `language` field used for both UI and outbound content
- Letting raw backend English reasons leak directly into localized UI
- Switching outbound to a local language without a confidence threshold