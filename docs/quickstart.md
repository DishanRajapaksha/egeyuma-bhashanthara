---
sidebar_position: 2
---

# Quickstart

## Install

```bash
uv sync --dev
```

Install the Docusaurus docs dependencies when working on the documentation site.

```bash
npm --prefix docs-site install
```

## Fetch and convert MMLU

```bash
uv run bhashanthara datasets fetch mmlu
```

Extract the CSV archive included in the downloaded MMLU snapshot:

```bash
mkdir -p data/raw/mmlu-csv
tar -xf data/raw/mmlu/data.tar -C data/raw/mmlu-csv
```

```bash
uv run bhashanthara datasets convert mmlu \
  --input data/raw/mmlu-csv/data/test/high_school_biology_test.csv \
  --output data/interim/mmlu-biology.jsonl \
  --subject high_school_biology \
  --domain science
```

## Validate input

```bash
uv run bhashanthara validate data/interim/mmlu-biology.jsonl
```

## Run a local translation pipeline

Start a local OpenAI-compatible server first, for example LM Studio on `http://localhost:1234/v1`.

```bash
uv run bhashanthara translate pipeline \
  --input data/interim/mmlu-biology.jsonl \
  --output data/generated/mmlu-biology-si-silver.jsonl \
  --translator qwen3-14b \
  --sinhala-reviewer gemma-3-12b \
  --answer-reviewer qwen3-32b \
  --base-url http://localhost:1234/v1 \
  --api-key local-key \
  --limit 2
```

## Export for Egeyuma

```bash
uv run bhashanthara export egeyuma \
  --input data/generated/mmlu-biology-si-silver.jsonl \
  --output data/export/egeyuma-mmlu-biology-si.jsonl \
  --dataset-name sinhala-mmlu-biology \
  --min-status silver \
  --language si
```

Use `--min-status gold` for serious leaderboard data.

## Repair existing translations

Use review mode with a `--repairer` when you want to correct the current translated JSONL without re-translating from English.

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

The command streams output item by item. If an item fails, it preserves that item unchanged in the output and can continue when `--continue-on-error` is set.

## Develop

```bash
uv run ruff check .
uv run mypy src tests
uv run pytest
```

## Build docs

```bash
npm --prefix docs-site run start
npm --prefix docs-site run build
```
