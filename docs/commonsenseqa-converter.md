# CommonsenseQA converter

Use the CommonsenseQA converter to turn CommonsenseQA JSONL into Bhashanthara canonical MCQ JSONL.

CommonsenseQA rows are expected to have this general shape:

```json
{
  "id": "075e483d21c29a511267ef62bedc0461",
  "question": {
    "stem": "Where would you find magazines along side many other printed works?",
    "choices": [
      {"label": "A", "text": "doctor"},
      {"label": "B", "text": "bookstore"},
      {"label": "C", "text": "market"},
      {"label": "D", "text": "train station"},
      {"label": "E", "text": "mortuary"}
    ]
  },
  "answerKey": "B"
}
```

Convert a split like this:

```bash
uv run bhashanthara datasets convert commonsenseqa \
  --input data/raw/commonsenseqa/dev_rand_split.jsonl \
  --output data/interim/commonsenseqa.jsonl \
  --subject commonsenseqa \
  --domain commonsense_reasoning \
  --source commonsenseqa \
  --source-license unknown
```

By default the converter requires exactly five choices. Use `--allow-variable-choices` only when you have checked that the downstream evaluation path can handle variable-choice MCQs.
