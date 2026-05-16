# ඇගැයුම භාෂාන්තර

**භාෂාන්තර** is a local LLM-assisted translation and verification pipeline for creating Sinhala benchmark datasets from English multiple-choice question datasets.
It is designed to work alongside [Egeyuma](https://github.com/DishanRajapaksha/egeyuma), which evaluates Sinhala, Singlish, and Sri Lankan-context LLMs.
## Purpose
Egeyuma Bhashanthara turns English MCQ datasets into verified Sinhala benchmark candidates.
The pipeline is not only translation. It also checks whether the translated question still preserves:
- the original meaning
- the original answer key
- the distinction between answer options
- natural Sinhala wording
- domain terminology
The goal is to produce Sinhala benchmark datasets that can be fed into Egeyuma for evaluation.
```text
English MCQ dataset
  -> local LLM translation
  -> automatic structural checks
  -> Sinhala quality review
  -> answer-preservation review
  -> optional back-translation audit
  -> Bronze / Silver / Gold Sinhala JSONL
  -> Egeyuma evaluation

Why this exists

Machine-translated benchmarks are risky.

A translation can sound fluent while quietly changing the correct answer. For example, an option like “carbon dioxide” may become “carbon”, or two distractors may collapse into the same Sinhala phrase. At that point the benchmark is no longer measuring model reasoning. It is measuring translation damage.

Bhashanthara exists to make that damage visible before the dataset is used.

Relationship with Egeyuma

egeyuma
  Evaluation engine, benchmark dashboard, result reporting
egeyuma-bhashanthara
  Translation, verification, review, and Sinhala dataset generation

Bhashanthara creates benchmark datasets. Egeyuma evaluates models against them.

The evaluator should stay deterministic and cold. Translation is a separate pipeline with its own provenance, review metadata, and quality gates.

Dataset flow

Input

Bhashanthara starts with canonical MCQ JSONL.

{
  "id": "mmlu_biology_001",
  "task_type": "mcq",
  "question": "Which gas is used by plants for photosynthesis?",
  "choices": [
    "Oxygen",
    "Carbon dioxide",
    "Nitrogen",
    "Hydrogen"
  ],
  "answer_index": 1,
  "answer_label": "B",
  "subject": "biology",
  "domain": "science",
  "language_style": "formal_english",
  "source": "cais/mmlu",
  "metadata": {
    "license": "MIT",
    "original_language": "en"
  }
}

Output

The translated item keeps the original answer index and records translation metadata.

{
  "id": "mmlu_biology_001_si",
  "task_type": "mcq",
  "question": "ප්‍රභාසංශ්ලේෂණය සඳහා ශාක භාවිතා කරන වායුව කුමක්ද?",
  "choices": [
    "ඔක්සිජන්",
    "කාබන් ඩයොක්සයිඩ්",
    "නයිට්‍රජන්",
    "හයිඩ්‍රජන්"
  ],
  "answer_index": 1,
  "answer_label": "B",
  "subject": "biology",
  "domain": "science",
  "language_style": "translated_sinhala",
  "source": "translated_from:cais/mmlu",
  "metadata": {
    "original_id": "mmlu_biology_001",
    "translation": {
      "source_language": "en",
      "target_language": "si",
      "status": "silver",
      "translator_model": "lmstudio/qwen3-14b",
      "sinhala_reviewer_model": "lmstudio/gemma-3-12b",
      "answer_reviewer_model": "lmstudio/qwen3-32b",
      "automatic_checks": {
        "same_choice_count": true,
        "answer_index_preserved": true,
        "no_empty_fields": true,
        "no_duplicate_choices": true,
        "sinhala_ratio": 0.86
      },
      "reviews": {
        "sinhala_quality": {
          "decision": "accept",
          "score": 4,
          "notes": ""
        },
        "answer_preservation": {
          "decision": "accept",
          "meaning_preserved": true,
          "answer_preserved": true,
          "notes": ""
        }
      }
    }
  }
}

Quality tiers

Bhashanthara separates translated data into quality tiers.

Bronze
  Machine translated
  Automatic structural checks passed
Silver
  Bronze
  LLM verifier accepted Sinhala quality and answer preservation
Gold
  Silver
  Human reviewed or adjudicated

Only Gold should be used for serious leaderboard claims. Bronze and Silver are useful for development, smoke tests, and triage.

Planned CLI

Generate translations

bhashanthara translate generate \
  --input data/mmlu-en.jsonl \
  --output data/mmlu-si-bronze.jsonl \
  --model lmstudio/qwen3-14b \
  --base-url http://localhost:1234/v1

Validate translated data

bhashanthara translate validate \
  --input data/mmlu-si-bronze.jsonl \
  --output audits/mmlu-si-checks.jsonl

Verify with separate models

bhashanthara translate verify \
  --input data/mmlu-si-bronze.jsonl \
  --output data/mmlu-si-silver.jsonl \
  --sinhala-reviewer lmstudio/gemma-3-12b \
  --answer-reviewer lmstudio/qwen3-32b \
  --base-url http://localhost:1234/v1

Run the full local pipeline

bhashanthara translate pipeline \
  --input data/mmlu-en.jsonl \
  --output data/mmlu-si-silver.jsonl \
  --translator lmstudio/qwen3-14b \
  --sinhala-reviewer lmstudio/gemma-3-12b \
  --answer-reviewer lmstudio/qwen3-32b \
  --base-url http://localhost:1234/v1 \
  --limit 200

Model roles

The pipeline should use different models where possible.

Translator model
  Translates English MCQ into Sinhala.
Sinhala reviewer model
  Checks fluency, naturalness, grammar, exam-style Sinhala, and terminology.
Answer-preservation reviewer model
  Compares English original and Sinhala translation, then decides whether the same answer remains correct.
Back-translator model, optional
  Translates Sinhala back to English to help detect meaning drift.

Using the same model to translate and verify is allowed for experiments, but weaker. That is a kangaroo court with tensor cores.

Automatic checks

Before spending model time on review, Bhashanthara should run cheap structural checks.

Examples:

* same number of choices
* answer index unchanged
* no empty question or choice
* no duplicate translated choices
* Sinhala character ratio above a threshold
* no unexpected English leftovers
* valid JSON output from the translator
* translated choices are not absurdly short or long
* model did not include explanations outside JSON

Verification decisions

Verifier output should use strict decisions.

accept
repair
reject
needs_human_review

Failure reasons should be explicit.

answer_changed
meaning_changed
ambiguous_question
duplicate_choices
bad_sinhala
domain_term_error
formatting_error
json_error

A single answer-preservation failure should block the item from Silver or Gold.

Human review

Bhashanthara should support exporting suspicious items to a local review tool such as Label Studio.

Suspicious items include:

* automatic checks failed
* Sinhala reviewer rejected or requested repair
* answer-preservation reviewer rejected
* back-translation drift is high
* English model answers original correctly but Sinhala model fails translated version
* all models choose the same wrong Sinhala option

Future command shape:

bhashanthara review export-labelstudio \
  --input data/mmlu-si-silver-candidates.jsonl \
  --output review/labelstudio_tasks.json
bhashanthara review import-labelstudio \
  --input data/mmlu-si-silver-candidates.jsonl \
  --labels review/labelstudio_export.json \
  --output data/mmlu-si-gold.jsonl

Suggested package structure

egeyuma-bhashanthara/
  README.md
  pyproject.toml
  src/
    bhashanthara/
      __init__.py
      cli.py
      datasets/
        schema.py
        jsonl.py
      models/
        openai_compatible.py
        ollama.py
      translate/
        generate.py
        checks.py
        verify.py
        backtranslate.py
        decide.py
        pipeline.py
        prompts/
          translate_mcq_si_v1.txt
          review_sinhala_quality_v1.txt
          review_answer_preservation_v1.txt
          backtranslate_v1.txt
      review/
        labelstudio.py
      reports/
        stats.py
  tests/
    test_schema.py
    test_checks.py
    test_generate.py
    test_verify.py
    test_pipeline.py

Local-first design

Bhashanthara should work with local model servers first.

Supported target backends:

* LM Studio OpenAI-compatible API
* Ollama
* llama.cpp server
* OpenAI-compatible endpoints

The project should not require cloud APIs for the core workflow.

First milestone

Build a small, defensible pilot.

Input:
  200 English MCQs from an open dataset
Pipeline:
  local LLM translation
  automatic checks
  two-model verification
  suspicious item export
Output:
  mmlu-si-bronze.jsonl
  mmlu-si-silver.jsonl
  audit report

Do not begin with 10,000 questions. That is how one manufactures a JSON landfill with a Sinhala label.

Licence note

Translated datasets are derivative works. The original dataset licence still matters.

Every generated item must preserve source metadata:

{
  "metadata": {
    "source_dataset": "cais/mmlu",
    "source_license": "MIT",
    "original_id": "..."
  }
}

Avoid publishing translated datasets when the original licence is unclear.
