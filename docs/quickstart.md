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
npm install
```

## Fetch and convert MMLU

```bash
uv run bhashanthara datasets fetch mmlu
```

```bash
uv run bhashanthara datasets convert mmlu \
  --input data/raw/mmlu/test/high_school_biology_test.csv \
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

## Develop

```bash
uv run ruff check .
uv run mypy src tests
uv run pytest
```

## Build docs

```bash
npm run start
npm run build
```
