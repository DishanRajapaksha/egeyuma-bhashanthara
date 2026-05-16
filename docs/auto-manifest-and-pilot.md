# Auto manifests and 50-item pilot workflow

This workflow keeps small Sinhala benchmark pilots reproducible without making every run a paperwork safari.

## Create a 50-item pilot input

Start from any canonical MCQ JSONL file, for example an MMLU or ARC conversion output.

```bash
uv run bhashanthara pilot create \
  --input data/interim/mmlu-biology.jsonl \
  --output data/pilots/mmlu-biology-50.jsonl \
  --count 50 \
  --manifest-output audits/mmlu-biology-50-pilot-manifest.json \
  --manifest-notes "First 50-item Sinhala pilot input"
```

The command takes the first N canonical MCQ items and writes them unchanged. It is intentionally boring. Random sampling can come later, after deterministic pilots are working.

## Run translation with an automatic manifest

```bash
uv run bhashanthara translate pipeline \
  --input data/pilots/mmlu-biology-50.jsonl \
  --output data/generated/mmlu-biology-50-si-silver.jsonl \
  --translator qwen3-14b \
  --sinhala-reviewer gemma-3-12b \
  --answer-reviewer qwen3-32b \
  --base-url http://localhost:1234/v1 \
  --failures-output audits/mmlu-biology-50-failures.jsonl \
  --continue-on-error \
  --max-retries 2 \
  --manifest-output audits/mmlu-biology-50-translation-manifest.json \
  --manifest-notes "50-item Sinhala pilot translation"
```

The manifest captures source and output file hashes, prompt hashes, model names, and key run parameters.

## Export for Egeyuma with an automatic manifest

```bash
uv run bhashanthara export egeyuma \
  --input data/generated/mmlu-biology-50-si-silver.jsonl \
  --output data/export/egeyuma-mmlu-biology-50-si.jsonl \
  --dataset-name sinhala-mmlu-biology-50 \
  --min-status silver \
  --language si \
  --manifest-output audits/mmlu-biology-50-egeyuma-export-manifest.json \
  --manifest-notes "50-item pilot export for Egeyuma"
```

Use `--min-status silver` for development pilots. Use `--min-status gold` when claiming leaderboard-quality results.

## Why this exists

A 50-item pilot is small enough to inspect and cheap enough to rerun. It catches schema errors, prompt rot, broken local model output, and review-loop nonsense before a larger run starts chewing GPU time like a rented wood chipper.
