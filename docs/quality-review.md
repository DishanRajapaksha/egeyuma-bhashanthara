---
sidebar_position: 1
---

# Quality and review

## What Bhashanthara checks

The pipeline verifies that the translated item preserves:

- Original meaning
- Original answer key
- Distinction between answer options
- Natural Sinhala wording
- Domain terminology
- Dataset provenance and licence metadata

The most important rule:

> A single answer-preservation failure must block the item from becoming a trusted benchmark item.

## Automatic checks

Before spending model time on review, Bhashanthara runs cheap structural checks.

Examples:

- Same number of choices
- Answer index unchanged
- No empty question or choice
- No duplicate translated choices
- Sinhala character ratio above a threshold
- No unexpected English leftovers
- Valid JSON output from the translator
- Translated choices are not absurdly short or long
- Model did not include explanations outside JSON

## Human review

Bhashanthara supports human review for suspicious items through Label Studio export/import.

Suspicious items include:

- Automatic checks failed
- Sinhala reviewer rejected or requested repair
- Answer-preservation reviewer rejected
- Backtranslation drift is high
- English model answers the original correctly but Sinhala model fails the translation
- All models choose the same wrong Sinhala option

## Licence note

Translated datasets are derivative works. The original dataset licence still matters.

Every generated item must preserve source metadata:

```json
{
  "metadata": {
    "source_dataset": "cais/mmlu",
    "source_license": "MIT",
    "original_id": "..."
  }
}
```

Avoid publishing translated datasets when the original licence is unclear.
