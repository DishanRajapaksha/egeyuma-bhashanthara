---
sidebar_position: 1
slug: /
---

# Egeyuma Bhashanthara

Egeyuma Bhashanthara is a local-first translation and verification pipeline for building Sinhala benchmark datasets from English multiple-choice question datasets.

It is designed to work with [Egeyuma](https://github.com/DishanRajapaksha/egeyuma), the evaluation engine and benchmark dashboard for Sinhala, Singlish, and Sri Lankan-context LLMs.

```text
egeyuma-bhashanthara  -> creates translated and verified Sinhala datasets
egeyuma               -> evaluates models using those datasets
```

## What is included

- Canonical MCQ JSONL schema
- MMLU, ARC, and CommonsenseQA converters
- Hugging Face dataset fetch support
- OpenAI-compatible local model client
- Prompt templates for translation, Sinhala review, answer-preservation review, and backtranslation
- Automatic structural checks
- Bronze, Silver, and Gold quality tiers
- Label Studio export/import for human audit
- Repair batch export/apply workflow
- Egeyuma-compatible export
- Run manifests, pilot datasets, and translation statistics
- `bhashanthara` Typer CLI
- Pytest, Ruff, Mypy, and GitHub Actions CI

## Pipeline shape

```text
English MCQ JSONL
  -> local LLM translation
  -> automatic structural checks
  -> Sinhala quality review
  -> answer-preservation review
  -> optional backtranslation audit
  -> Bronze / Silver / Gold Sinhala JSONL
  -> Egeyuma evaluation
```

Start with the [quickstart](./quickstart.md), then use the dataset and workflow pages for command-level details.
