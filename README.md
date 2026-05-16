# Egeyuma Bhashanthara

Egeyuma Bhashanthara is a local-first Python CLI for translating English multiple-choice benchmark datasets into Sinhala, checking answer preservation, and exporting trusted items for [Egeyuma](https://github.com/DishanRajapaksha/egeyuma).

```text
egeyuma-bhashanthara  -> creates translated and verified Sinhala datasets
egeyuma               -> evaluates models using those datasets
```

## Install

```bash
uv sync --dev
npm --prefix docs-site install
```

## Common commands

End-to-end local MMLU biology run:

```bash
uv run bhashanthara datasets fetch mmlu

mkdir -p data/raw/mmlu-csv
tar -xf data/raw/mmlu/data.tar -C data/raw/mmlu-csv

uv run bhashanthara datasets convert mmlu \
  --input data/raw/mmlu-csv/data/test/high_school_biology_test.csv \
  --output data/interim/mmlu-biology.jsonl \
  --subject high_school_biology \
  --domain science

uv run bhashanthara validate data/interim/mmlu-biology.jsonl

uv run bhashanthara translate pipeline \
  --input data/interim/mmlu-biology.jsonl \
  --output data/generated/mmlu-biology-si-silver.jsonl \
  --translator google/gemma-4-31b \
  --sinhala-reviewer google/gemma-4-31b \
  --answer-reviewer google/gemma-4-31b \
  --base-url http://localhost:1234/v1 \
  --max-tokens 4096 \
  --timeout-seconds 600 \
  --resume \
  --continue-on-error \
  --max-retries 2 \
  --failures-output audits/mmlu-biology-pipeline-failures.jsonl

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

uv run bhashanthara stats \
  --input data/generated/mmlu-biology-si-silver.jsonl \
  --output audits/mmlu-biology-si-stats.json

uv run bhashanthara export egeyuma \
  --input data/generated/mmlu-biology-si-silver.jsonl \
  --output data/export/egeyuma-mmlu-biology-si.jsonl \
  --dataset-name sinhala-mmlu-biology \
  --min-status silver \
  --language si \
  --manifest-output audits/mmlu-biology-egeyuma-export-manifest.json
```

For faster iteration, add `--limit 2` or `--limit 5` to translation or repair commands.

## Docs

The full project guide lives in `docs/` and is published with Docusaurus.

```bash
npm --prefix docs-site run start
npm --prefix docs-site run build
```

## Development

```bash
uv run ruff check .
uv run mypy src tests
uv run pytest
```
