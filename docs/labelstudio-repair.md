---
sidebar_position: 2
---

# Label Studio and repairs

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
