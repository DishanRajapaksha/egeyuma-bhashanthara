---
sidebar_position: 3
---

# Concepts

## Why this exists

Machine-translated benchmarks are risky when they are treated as finished datasets.

A translated question can sound fluent while changing the correct answer. A distractor can become correct. Two options can collapse into the same Sinhala phrase. A technical term can be softened into nonsense. At that point, the benchmark is no longer measuring model reasoning. It is measuring translation damage.

Bhashanthara exists to detect that damage before translated data is used for evaluation.

## Local-first workflow

The project is designed for local model servers such as LM Studio, Ollama, and llama.cpp server. Cloud APIs may be supported, but they should not be required for the core workflow.

The CLI talks to OpenAI-compatible endpoints so translation, review, and backtranslation can all run against local models.

## Relationship with Egeyuma

Bhashanthara and Egeyuma are separate on purpose.

```text
egeyuma-bhashanthara
  dataset conversion
  translation
  verification
  review
  repair
  dataset generation
  Egeyuma export

egeyuma
  evaluation
  scoring
  reporting
  benchmark dashboard
```

Translation and repair are data-generation steps. Evaluation should remain deterministic. Mixing the two would make benchmark runs hard to reproduce.

## Quality tiers

Bhashanthara separates translated data into explicit trust levels.

```text
Bronze
  Machine translated
  Automatic structural checks passed

Silver
  Bronze
  LLM verifier accepted Sinhala quality and answer preservation

Gold
  Silver
  Human reviewed or adjudicated
```

Bronze and Silver are useful for development. Gold is the only tier that should be used for serious leaderboard claims.

## Model roles

```text
Translator model
  Translates English MCQs into Sinhala.

Sinhala reviewer model
  Checks fluency, grammar, exam-style Sinhala, and terminology.

Answer-preservation reviewer model
  Compares the English original and Sinhala translation, then decides whether the same answer remains correct.

Backtranslator model, optional
  Translates Sinhala back into English to help detect meaning drift.
```

Using the same model to translate and verify is acceptable for experiments, but weak. The translator should not be the only judge of its own work.
