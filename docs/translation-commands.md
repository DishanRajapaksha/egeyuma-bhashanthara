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

Use one model for translation and optional separate models for review. When reviewers are provided, translation and review happen in one pass. That is convenient, but slower because each item can require a translation call, a Sinhala quality review call, and an answer-preservation review call.

```bash
uv run bhashanthara translate pipeline \
  --input data/interim/mmlu-biology.jsonl \
  --output data/generated/mmlu-biology-si-silver.jsonl \
  --translator google/gemma-4-31b \
  --sinhala-reviewer google/gemma-4-31b \
  --answer-reviewer google/gemma-4-31b \
  --base-url http://localhost:1234/v1 \
  --api-key local-key \
  --max-tokens 4096 \
  --timeout-seconds 600 \
  --limit 2
```

Use resumable and failure logging options for larger runs.

```bash
uv run bhashanthara translate pipeline \
  --input data/interim/mmlu-biology.jsonl \
  --output data/generated/mmlu-biology-si-silver.jsonl \
  --translator google/gemma-4-31b \
  --base-url http://localhost:1234/v1 \
  --max-tokens 4096 \
  --timeout-seconds 600 \
  --failures-output audits/mmlu-biology-failures.jsonl \
  --continue-on-error \
  --max-retries 2 \
  --resume
```

## Review or repair existing translations

Use `translate review` when you already have translated JSONL and do not want to translate it again.

Review only:

```bash
uv run bhashanthara translate review \
  --input data/interim/mmlu-biology.jsonl \
  --translated data/generated/mmlu-biology-si-silver.jsonl \
  --output data/generated/mmlu-biology-si-reviewed.jsonl \
  --sinhala-reviewer google/gemma-4-31b \
  --answer-reviewer google/gemma-4-31b \
  --base-url http://localhost:1234/v1 \
  --max-tokens 4096 \
  --timeout-seconds 600 \
  --continue-on-error \
  --failures-output audits/mmlu-biology-review-failures.jsonl
```

Repair only, in place:

```bash
uv run bhashanthara translate review \
  --input data/interim/mmlu-biology.jsonl \
  --translated data/generated/mmlu-biology-si-silver.jsonl \
  --output data/generated/mmlu-biology-si-silver.jsonl \
  --repairer google/gemma-4-31b \
  --base-url http://localhost:1234/v1 \
  --max-tokens 4096 \
  --timeout-seconds 600 \
  --continue-on-error \
  --failures-output audits/mmlu-biology-repair-failures.jsonl
```

Review mode streams each completed item to the output JSONL immediately. With `--continue-on-error`, failed items are preserved unchanged and recorded in the failures file.

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
