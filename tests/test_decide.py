from __future__ import annotations

from bhashanthara.datasets.schema import (
    AnswerPreservationReview,
    AutomaticChecks,
    SinhalaQualityReview,
)
from bhashanthara.translate.decide import decide_status


def passing_checks() -> AutomaticChecks:
    return AutomaticChecks(
        same_choice_count=True,
        answer_index_preserved=True,
        no_empty_fields=True,
        no_duplicate_choices=True,
        sinhala_ratio=0.8,
        unexpected_english_ratio=0.0,
    )


def test_decide_status_returns_bronze_after_checks_only() -> None:
    assert decide_status(automatic_checks=passing_checks()) == "bronze"


def test_decide_status_returns_silver_when_reviews_accept() -> None:
    assert (
        decide_status(
            automatic_checks=passing_checks(),
            sinhala_quality=SinhalaQualityReview(decision="accept", score=4),
            answer_preservation=AnswerPreservationReview(
                decision="accept",
                meaning_preserved=True,
                answer_preserved=True,
            ),
        )
        == "silver"
    )


def test_decide_status_blocks_answer_preservation_failure() -> None:
    assert (
        decide_status(
            automatic_checks=passing_checks(),
            sinhala_quality=SinhalaQualityReview(decision="accept", score=4),
            answer_preservation=AnswerPreservationReview(
                decision="reject",
                meaning_preserved=True,
                answer_preserved=False,
            ),
        )
        == "needs_human_review"
    )


def test_decide_status_blocks_failed_automatic_checks() -> None:
    checks = passing_checks().model_copy(update={"issues": ["duplicate_translated_choices"]})

    assert decide_status(automatic_checks=checks) == "needs_human_review"
