---
sidebar_position: 3
---

# Egeyuma export

Export only trusted translated items into Egeyuma-compatible MCQ JSONL.

```bash
uv run bhashanthara export egeyuma \
  --input data/generated/mmlu-si-gold-candidates.jsonl \
  --output data/export/egeyuma-mmlu-si.jsonl \
  --dataset-name sinhala-mmlu-translated \
  --min-status gold \
  --language si
```

`--min-status` accepts `bronze`, `silver`, or `gold`. Use `gold` for serious leaderboard data.

You can also write a manifest during export.

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
