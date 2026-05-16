# Labelled-choice converter helper

ARC, CommonsenseQA, and OpenBookQA all use a similar labelled-choice JSON shape:

```json
{
  "question": {
    "stem": "...",
    "choices": [
      {"label": "A", "text": "..."},
      {"label": "B", "text": "..."}
    ]
  },
  "answerKey": "A"
}
```

The shared helper in `bhashanthara.datasets.conversion.labelled_choices` normalises that structure into:

```text
stem
choices
choice_labels
answer_key
answer_index
answer_label
```

Dataset-specific converters should still own their metadata, source names, licences, and item id format. The shared helper should only handle the boring labelled-choice mechanics. That keeps converters small without turning the codebase into abstraction soup.
