---
sidebar_position: 1
---

# Translation commands

## Generate Bronze translations

Start a local OpenAI-compatible server first.

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

Use resumable and failure logging options for larger runs.

```bash
uv run bhashanthara translate pipeline \
  --input data/interim/mmlu-biology.jsonl \
  --output data/generated/mmlu-biology-si-silver.jsonl \
  --translator qwen3-14b \
  --sinhala-reviewer gemma-3-12b \
  --answer-reviewer qwen3-32b \
  --base-url http://localhost:1234/v1 \
  --failures-output audits/mmlu-biology-failures.jsonl \
  --continue-on-error \
  --max-retries 2 \
  --resume
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

Backtranslation is an audit signal, not proof of quality.

## Inspect translation stats

```bash
uv run bhashanthara stats \
  --input data/generated/mmlu-si-silver.jsonl \
  --output audits/mmlu-si-stats.json
```
