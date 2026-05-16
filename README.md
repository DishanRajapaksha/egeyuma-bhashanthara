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
- backtranslation audit support
- automatic translation checks
- Bronze/Silver decision logic
- Label Studio export/import for human audit
- repair batch export/apply workflow
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

## Backtranslate for drift inspection

Backtranslation translates Sinhala items back into English so a reviewer can quickly spot meaning drift.

```bash
uv run bhashanthara translate backtranslate \
  --input data/generated/mmlu-si-silver.jsonl \
  --output data/generated/mmlu-si-with-backtranslation.jsonl \
  --model qwen3-14b \
  --base-url http://localhost:1234/v1 \
  --api-key local-key \
  --report-output audits/mmlu-si-backtranslations.json
```

Backtranslation is an audit signal, not proof of quality. It helps find smoke; it does not certify the building.

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

## Export repair batches

Repair batches are plain JSON files. Edit the `repair.question`, `repair.choices`, and `repair.notes` fields, then apply the batch back into the dataset.

```bash
uv run bhashanthara repair export \
  --input data/generated/mmlu-si-gold-candidates.jsonl \
  --output review/repair_batch.json
```

Use `--include-all` if you want to export every item, not just suspicious ones.

## Apply repairs

Applying repairs preserves the answer index and answer label. It only replaces the translated question and choice text. Repaired items are set back to `needs_human_review`, because they must be reviewed again before becoming Gold.

```bash
uv run bhashanthara repair apply \
  --input data/generated/mmlu-si-gold-candidates.jsonl \
  --repairs review/repair_batch.json \
  --output data/generated/mmlu-si-repaired.jsonl
```

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
  repair
  dataset generation

egeyuma
  evaluation
  scoring
  reporting
  benchmark dashboard
```

Translation and repair are data-generation steps. Evaluation should remain deterministic. Mixing the two would make benchmark runs slippery and hard to reproduce.

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
