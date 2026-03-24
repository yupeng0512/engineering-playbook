---
title: "Prefer Lightweight Structured File Parsers Before Heavy ML Document Stacks"
type: note
tags: [engineering-playbook, patterns, ingestion, parsing, containers]
permalink: engineering-playbook/patterns/prefer-lightweight-structured-file-parsers-before-heavy-ml-document-stacks
---

# Prefer Lightweight Structured File Parsers Before Heavy ML Document Stacks

## Summary

When a product only needs:

- readable extracted text
- section/table-ish structure
- review-first operator workflows
- local/self-hosted execution

start with lightweight parsers before adopting a heavy document AI stack.

## Observations

- [decision] Prefer lightweight local parsers first when the product contract only requires LLM-friendly text, section blocks, and parse warnings instead of high-end document reconstruction. #architecture #ingestion
- [problem] Document AI frameworks can silently pull very heavy runtime trees such as `torch` and `CUDA`, which inflate Docker build time, image size, and operational complexity well beyond the feature’s actual needs. #containers #cost
- [solution] Preserve the higher-level API contract, but swap the parser implementation to simpler libraries such as `pypdf`, `python-docx`, and `openpyxl` when they already satisfy the current supported file types. #python #backend
- [insight] A review-first operator workflow usually benefits more from stable structured extraction and low operational risk than from maximal parser sophistication. #product #tradeoff

## Relations

- relates_to [[engineering-playbook/patterns/stable-empty-collection-contracts]]
- relates_to [[TradeRadar]]
