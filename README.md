# ඇගැයුම භාෂාන්තර - Egeyuma Bhashanthara

**Egeyuma Bhashanthara** is a local-first translation and verification pipeline for building Sinhala benchmark datasets from English multiple-choice question datasets.

It is designed to work with [Egeyuma](https://github.com/DishanRajapaksha/egeyuma), the evaluation engine and benchmark dashboard for Sinhala, Singlish, and Sri Lankan-context LLMs.

```text
egeyuma-bhashanthara  -> creates translated and verified Sinhala datasets
egeyuma               -> evaluates models using those datasets
```

## Current scaffold

This repository now contains the first Python scaffold using `uv`:

- canonical MCQ JSONL schema
- translated MCQ schema with translation metadata
- OpenAI-compatible local model client
- prompt templates for translation and verification
- automatic translation checks
- Bronze/Silver decision logic
- Label Studio export/import for human audit
- translation statistics reporting
- `bhashanthara` Typer CLI
- sample English MCQ JSONL data
- pytest tests
- GitHub Actions CI using `uv`

## Install

```bash
uv sync --dev
```

## Validate the sample dataset

```bash
uv run bhashanthara validate data/samples/mmlu_biology_sample.jsonl
```

## Generate Bronze translations

Start a local OpenAI-compatible server first, for example LM Studio on `http://localhost:1234/v1`.

```bash
uv run bhashanthara translate generate \
  --input data/samples/mmlu_biology_sample.jsonl \
  --output data/generated/mmlu-si-bronze.jsonl \
  --model qwen3-14b \
  --base-url http://localhost:1234/v1 \
  --api-key local-key \
  --limit 2
```

## Run the full local pipeline

Use one model for translation and optional separate models for review.

```bash
uv run bhashanthara translate pipeline \
  --input data/samples/mmlu_biology_sample.jsonl \
  --output data/generated/mmlu-si-silver.jsonl \
  --translator qwen3-14b \
  --sinhala-reviewer gemma-3-12b \
  --answer-reviewer qwen3-32b \
  --base-url http://localhost:1234/v1 \
  --api-key local-key \
  --limit 2
```

## Inspect translation stats

```bash
uv run bhashanthara stats \
  --input data/generated/mmlu-si-silver.jsonl \
  --output audits/mmlu-si-stats.json
```

## Export suspicious items for Label Studio

By default, this exports only suspicious items.

```bash
uv run bhashanthara review export-labelstudio \
  --input data/generated/mmlu-si-silver.jsonl \
  --output review/labelstudio_tasks.json \
  --label-config-output review/labelstudio_config.xml
```

Use `--include-all` when you want a full audit batch.

## Import Label Studio decisions

After reviewing tasks in Label Studio, export the annotated task JSON and merge it back into the translated JSONL.

```bash
uv run bhashanthara review import-labelstudio \
  --input data/generated/mmlu-si-silver.jsonl \
  --labels review/labelstudio_export.json \
  --output data/generated/mmlu-si-gold-candidates.jsonl
```

Human `accept` marks an item as `gold`; human `reject` marks it as `rejected`; `repair` and `needs_human_review` keep the item in `needs_human_review`.

## Development

```bash
uv run ruff check .
uv run mypy src tests
uv run pytest
```

## Why this exists

Machine-translated benchmarks are dangerous if they are treated as finished datasets.

A translated question can sound fluent while quietly changing the correct answer. A distractor can become correct. Two options can collapse into the same Sinhala phrase. A technical term can be softened into nonsense. At that point, the benchmark is no longer measuring model reasoning. It is measuring translation damage.

Bhashanthara exists to detect that damage before translated data is used for evaluation.

## Core idea

Bhashanthara turns English MCQ datasets into Sinhala benchmark candidates through a staged pipeline:

```text
English MCQ JSONL
  -> local LLM translation
  -> automatic structural checks
  -> Sinhala quality review
  -> answer-preservation review
  -> optional back-translation audit
  -> Bronze / Silver / Gold Sinhala JSONL
  -> Egeyuma evaluation
```

The project is local-first. It should work with local model servers such as LM Studio, Ollama, and llama.cpp server. Cloud APIs may be supported, but should not be required for the core workflow.

## What Bhashanthara checks

The pipeline should verify that the translated item preserves:

- the original meaning
- the original answer key
- the distinction between answer options
- natural Sinhala wording
- domain terminology
- dataset provenance and licence metadata

The most important rule:

> A single answer-preservation failure must block the item from becoming a trusted benchmark item.

## Relationship with Egeyuma

Bhashanthara and Egeyuma are separate on purpose.

```text
egeyuma-bhashanthara
  translation
  verification
  review
  dataset generation

egeyuma
  evaluation
  scoring
  reporting
  benchmark dashboard
```

Translation is a data-generation pipeline. Evaluation should remain deterministic. Mixing the two would make benchmark runs slippery and hard to reproduce.

## Dataset format

### Input

Bhashanthara starts with canonical English MCQ JSONL.

```json
{
  "id": "mmlu_biology_001",
  "task_type": "mcq",
  "question": "Which gas is used by plants for photosynthesis?",
  "choices": [
    "Oxygen",
    "Carbon dioxide",
    "Nitrogen",
    "Hydrogen"
  ],
  "answer_index": 1,
  "answer_label": "B",
  "subject": "biology",
  "domain": "science",
  "language_style": "formal_english",
  "source": "cais/mmlu",
  "metadata": {
    "source_dataset": "cais/mmlu",
    "source_license": "MIT",
    "original_language": "en"
  }
}
```

### Output

The Sinhala item keeps the original answer index and records translation metadata.

```json
{
  "id": "mmlu_biology_001_si",
  "task_type": "mcq",
  "question": "ප්‍රභාසංශ්ලේෂණය සඳහා ශාක භාවිතා කරන වායුව කුමක්ද?",
  "choices": [
    "ඔක්සිජන්",
    "කාබන් ඩයොක්සයිඩ්",
    "නයිට්‍රජන්",
    "හයිඩ්‍රජන්"
  ],
  "answer_index": 1,
  "answer_label": "B",
  "subject": "biology",
  "domain": "science",
  "language_style": "translated_sinhala",
  "source": "translated_from:cais/mmlu",
  "metadata": {
    "original_id": "mmlu_biology_001",
    "source_dataset": "cais/mmlu",
    "source_license": "MIT",
    "translation": {
      "source_language": "en",
      "target_language": "si",
      "status": "silver",
      "translator_model": "lmstudio/qwen3-14b",
      "sinhala_reviewer_model": "lmstudio/gemma-3-12b",
      "answer_reviewer_model": "lmstudio/qwen3-32b",
      "automatic_checks": {
        "same_choice_count": true,
        "answer_index_preserved": true,
        "no_empty_fields": true,
        "no_duplicate_choices": true,
        "sinhala_ratio": 0.86
      },
      "reviews": {
        "sinhala_quality": {
          "decision": "accept",
          "score": 4,
          "notes": ""
        },
        "answer_preservation": {
          "decision": "accept",
          "meaning_preserved": true,
          "answer_preserved": true,
          "notes": ""
        }
      },
      "human_review": {
        "decision": "accept",
        "failure_reasons": [],
        "notes": "Looks correct."
      }
    }
  }
}
```

## Quality tiers

Bhashanthara separates translated data into explicit trust levels.

```text
Bronze
  Machine translated
  Automatic structural checks passed

Silver
  Bronze
  LLM verifier accepted Sinhala quality and answer preservation

Gold
  Silver
  Human reviewed or adjudicated
```

Bronze and Silver are useful for development. Gold is the only tier that should be used for serious leaderboard claims.

## Model roles

The pipeline should use different models where possible.

```text
Translator model
  Translates English MCQs into Sinhala.

Sinhala reviewer model
  Checks fluency, grammar, exam-style Sinhala, and terminology.

Answer-preservation reviewer model
  Compares the English original and Sinhala translation, then decides whether the same answer remains correct.

Back-translator model, optional
  Translates Sinhala back into English to help detect meaning drift.
```

Using the same model to translate and verify is acceptable for experiments, but weak. The translator should not be the only judge of its own work.

## Automatic checks

Before spending model time on review, Bhashanthara should run cheap structural checks.

Examples:

- same number of choices
- answer index unchanged
- no empty question or choice
- no duplicate translated choices
- Sinhala character ratio above a threshold
- no unexpected English leftovers
- valid JSON output from the translator
- translated choices are not absurdly short or long
- model did not include explanations outside JSON

## Verification decisions

Verifier output should use strict decisions.

```text
accept
repair
reject
needs_human_review
```

Failure reasons should be explicit.

```text
answer_changed
meaning_changed
ambiguous_question
duplicate_choices
bad_sinhala
domain_term_error
formatting_error
json_error
```

## Human review

Bhashanthara supports human review for suspicious items through Label Studio export/import.

Suspicious items include:

- automatic checks failed
- Sinhala reviewer rejected or requested repair
- answer-preservation reviewer rejected
- back-translation drift is high
- English model answers the original correctly but Sinhala model fails the translation
- all models choose the same wrong Sinhala option

## Licence note

Translated datasets are derivative works. The original dataset licence still matters.

Every generated item must preserve source metadata:

```json
{
  "metadata": {
    "source_dataset": "cais/mmlu",
    "source_license": "MIT",
    "original_id": "..."
  }
}
```

Avoid publishing translated datasets when the original licence is unclear.
