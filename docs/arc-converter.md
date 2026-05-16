# ARC converter

Use the ARC converter to turn AI2 ARC JSONL into Bhashanthara canonical MCQ JSONL.

ARC rows are expected to have this general shape:

```json
{
  "id": "Mercury_7015875",
  "question": {
    "stem": "Which gas do plants use for photosynthesis?",
    "choices": [
      {"text": "Oxygen", "label": "A"},
      {"text": "Carbon dioxide", "label": "B"},
      {"text": "Nitrogen", "label": "C"},
      {"text": "Hydrogen", "label": "D"}
    ]
  },
  "answerKey": "B"
}
```

Convert ARC Challenge or ARC Easy like this:

```bash
uv run bhashanthara datasets convert arc \
  --input data/raw/arc/ARC-Challenge-Test.jsonl \
  --output data/interim/arc-challenge.jsonl \
  --subject arc_challenge \
  --domain science \
  --source ai2_arc \
  --source-license cc-by-sa-4.0
```

By default the converter requires exactly four choices. Use `--allow-variable-choices` only when you have checked that the downstream evaluation path can handle variable-choice MCQs.
