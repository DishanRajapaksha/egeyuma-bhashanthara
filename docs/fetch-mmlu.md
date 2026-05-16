# Fetch MMLU

Fetch MMLU into a local raw-data folder before conversion.

```bash
uv run bhashanthara datasets fetch mmlu
```

Defaults:

```text
alias: mmlu -> cais/mmlu
output: data/raw/mmlu
```

Override the dataset name when needed:

```bash
uv run bhashanthara datasets fetch mmlu \
  --dataset-name cais/mmlu \
  --output-dir data/raw/mmlu
```

Then convert the subject CSV you want:

```bash
uv run bhashanthara datasets convert mmlu \
  --input data/raw/mmlu/test/high_school_biology_test.csv \
  --output data/interim/mmlu-biology.jsonl \
  --subject high_school_biology \
  --domain science
```

Fetching and converting are separate on purpose. Fetching touches the network. Conversion stays local and reproducible.
