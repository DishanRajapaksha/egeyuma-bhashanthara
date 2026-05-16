# Resume, retry, and failure logging

Long local LLM translation runs should survive bad model output, transient API failures, and interrupted terminal sessions.

Use the resumable pipeline options when translating larger datasets.

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
  --max-retries 2
```

## Resume an interrupted run

```bash
uv run bhashanthara translate pipeline \
  --input data/interim/mmlu-biology.jsonl \
  --output data/generated/mmlu-biology-si-silver.jsonl \
  --translator qwen3-14b \
  --base-url http://localhost:1234/v1 \
  --resume
```

When `--resume` is used, existing translated items in the output JSONL are loaded and their original item ids are skipped.

## Failure logging

Use `--failures-output` to capture failed items as JSONL.

Each failure record includes:

```text
original_id
stage
error_type
error_message
item
```

## Retry behaviour

`--max-retries 2` means Bhashanthara will try the item once, then retry twice before treating it as failed.

## Continue-on-error

Without `--continue-on-error`, the pipeline stops at the first failed item.

With `--continue-on-error`, failed items are written to the failures file and the pipeline continues. This is the right choice for large batches. One cursed JSON response should not ruin the whole harvest.
