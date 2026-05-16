# Run manifest

Use a run manifest to record provenance for translated benchmark outputs.

The manifest records SHA256 hashes for source files, output files, prompt files, model names, run parameters, notes, and a timestamp.

```bash
uv run bhashanthara manifest create \
  --output audits/mmlu-si-run-manifest.json \
  --source-file data/generated/mmlu-si-silver.jsonl \
  --output-file data/export/egeyuma-mmlu-si.jsonl \
  --prompt-file src/bhashanthara/translate/prompts/translate_mcq_si_v1.txt \
  --prompt-file src/bhashanthara/translate/prompts/review_answer_preservation_v1.txt \
  --model translator=qwen3-14b \
  --model sinhala_reviewer=gemma-3-12b \
  --model answer_reviewer=qwen3-32b \
  --parameter min_status=gold \
  --notes "Pilot Sinhala MMLU export"
```

The manifest is the receipt. Keep it with the exported benchmark data.
