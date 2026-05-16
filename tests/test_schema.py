from __future__ import annotations

import pytest
from pydantic import ValidationError

from bhashanthara.datasets.schema import (
    MCQItem,
    TranslationCandidate,
    translated_item_from_candidate,
)


def test_mcq_item_validates_answer_alignment() -> None:
    item = MCQItem(
        id="item_001",
        question="Question?",
        choices=["A", "B", "C", "D"],
        answer_index=1,
        answer_label="B",
    )

    assert item.answer_label == "B"


def test_mcq_item_rejects_mismatched_answer_label() -> None:
    with pytest.raises(ValidationError, match="answer_label 'A' does not match answer_index 1"):
        MCQItem(
            id="bad_item",
            question="Question?",
            choices=["A", "B", "C", "D"],
            answer_index=1,
            answer_label="A",
        )


def test_translated_item_from_candidate_preserves_answer_key() -> None:
    original = MCQItem(
        id="mmlu_biology_001",
        question="Which gas is used by plants for photosynthesis?",
        choices=["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"],
        answer_index=1,
        answer_label="B",
        source="cais/mmlu",
    )
    candidate = TranslationCandidate(
        question="ප්‍රශ්නය?",
        choices=["ඔක්සිජන්", "කාබන් ඩයොක්සයිඩ්", "නයිට්‍රජන්", "හයිඩ්‍රජන්"],
    )

    translated = translated_item_from_candidate(
        original=original,
        candidate=candidate,
        translator_model="lmstudio/qwen3-14b",
    )

    assert translated.id == "mmlu_biology_001_si"
    assert translated.answer_index == original.answer_index
    assert translated.answer_label == original.answer_label
    assert translated.language_style == "translated_sinhala"
    assert translated.metadata["original_id"] == original.id
    assert translated.metadata["translation"]["translator_model"] == "lmstudio/qwen3-14b"
