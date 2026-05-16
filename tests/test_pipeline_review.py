from __future__ import annotations

import pytest

from bhashanthara.datasets.schema import (
    AnswerPreservationReview,
    MCQItem,
    SinhalaQualityReview,
    TranslatedMCQItem,
    TranslationRepairCandidate,
)
from bhashanthara.translate import pipeline
from bhashanthara.translate.pipeline import review_existing_translation


def original() -> MCQItem:
    return MCQItem(
        id="item_001",
        question="Question?",
        choices=["A", "B", "C", "D"],
        answer_index=1,
        answer_label="B",
    )


def translated() -> TranslatedMCQItem:
    return TranslatedMCQItem(
        id="item_001_si",
        question="ප්‍රශ්නය?",
        choices=["එක", "දෙක", "තුන", "හතර"],
        answer_index=1,
        answer_label="B",
        metadata={"original_id": "item_001", "translation": {"status": "bronze"}},
    )


def test_review_existing_translation_marks_silver_when_reviewers_accept(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeClient:
        model = "reviewer-model"

    def fake_sinhala_review(*args: object, **kwargs: object) -> SinhalaQualityReview:
        return SinhalaQualityReview(decision="accept", score=4, notes="Good.")

    def fake_answer_review(*args: object, **kwargs: object) -> AnswerPreservationReview:
        return AnswerPreservationReview(
            decision="accept",
            meaning_preserved=True,
            answer_preserved=True,
            notes="Answer preserved.",
        )

    monkeypatch.setattr(pipeline, "review_sinhala_quality", fake_sinhala_review)
    monkeypatch.setattr(pipeline, "review_answer_preservation", fake_answer_review)

    reviewed = review_existing_translation(
        original(),
        translated(),
        sinhala_reviewer=FakeClient(),  # type: ignore[arg-type]
        answer_reviewer=FakeClient(),  # type: ignore[arg-type]
    )

    translation = reviewed.metadata["translation"]
    assert translation["status"] == "silver"
    assert translation["sinhala_reviewer_model"] == "reviewer-model"
    assert translation["answer_reviewer_model"] == "reviewer-model"
    assert translation["automatic_checks"]["answer_index_preserved"] is True


def test_review_existing_translation_blocks_answer_preservation_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeClient:
        model = "reviewer-model"

    def fake_answer_review(*args: object, **kwargs: object) -> AnswerPreservationReview:
        return AnswerPreservationReview(
            decision="reject",
            meaning_preserved=False,
            answer_preserved=False,
            notes="Changed answer.",
        )

    monkeypatch.setattr(pipeline, "review_answer_preservation", fake_answer_review)

    reviewed = review_existing_translation(
        original(),
        translated(),
        answer_reviewer=FakeClient(),  # type: ignore[arg-type]
    )

    assert reviewed.metadata["translation"]["status"] == "needs_human_review"


def test_review_existing_translation_applies_model_repair(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeClient:
        model = "repair-model"

    def fake_repair(*args: object, **kwargs: object) -> TranslationRepairCandidate:
        return TranslationRepairCandidate(
            question="නව ප්‍රශ්නය?",
            choices=["නව එක", "නව දෙක", "නව තුන", "නව හතර"],
            notes="Fixed wording.",
        )

    monkeypatch.setattr(pipeline, "repair_translation", fake_repair)

    reviewed = review_existing_translation(
        original(),
        translated(),
        repairer=FakeClient(),  # type: ignore[arg-type]
    )

    assert reviewed.question == "නව ප්‍රශ්නය?"
    assert reviewed.choices == ["නව එක", "නව දෙක", "නව තුන", "නව හතර"]
    assert reviewed.answer_index == 1
    assert reviewed.answer_label == "B"
    assert reviewed.metadata["repair"]["status"] == "model_applied"
    assert reviewed.metadata["repair"]["model"] == "repair-model"


def test_review_existing_translation_rejects_repair_choice_count_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeClient:
        model = "repair-model"

    def fake_repair(*args: object, **kwargs: object) -> TranslationRepairCandidate:
        return TranslationRepairCandidate(
            question="නව ප්‍රශ්නය?",
            choices=["එක", "දෙක", "තුන"],
            notes="Bad repair.",
        )

    monkeypatch.setattr(pipeline, "repair_translation", fake_repair)

    with pytest.raises(ValueError, match="changes choice count"):
        review_existing_translation(
            original(),
            translated(),
            repairer=FakeClient(),  # type: ignore[arg-type]
        )
