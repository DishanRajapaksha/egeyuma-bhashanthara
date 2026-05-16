# Dataset commands

Dataset commands are grouped by lifecycle step.

```text
bhashanthara datasets
  fetch
    mmlu
  convert
    mmlu
    arc
    commonsenseqa
```

## Fetch MMLU

```bash
uv run bhashanthara datasets fetch mmlu
```

With an explicit dataset name:

```bash
uv run bhashanthara datasets fetch mmlu \
  --dataset-name cais/mmlu \
  --output-dir data/raw/mmlu
```

## Convert MMLU

```bash
uv run bhashanthara datasets convert mmlu \
  --input data/raw/mmlu/test/high_school_biology_test.csv \
  --output data/interim/mmlu-biology.jsonl \
  --subject high_school_biology \
  --domain science
```

## Convert ARC

```bash
uv run bhashanthara datasets convert arc \
  --input data/raw/arc/ARC-Challenge-Test.jsonl \
  --output data/interim/arc-challenge.jsonl \
  --subject arc_challenge \
  --domain science
```

## Convert CommonsenseQA

```bash
uv run bhashanthara datasets convert commonsenseqa \
  --input data/raw/commonsenseqa/dev_rand_split.jsonl \
  --output data/interim/commonsenseqa.jsonl \
  --subject commonsenseqa \
  --domain commonsense_reasoning
```

The old flat `convert-mmlu` / `convert-arc` / `convert-commonsenseqa` command style was removed before 1.0. The nested command structure is cleaner and easier to extend.
