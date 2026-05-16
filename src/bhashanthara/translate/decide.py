from __future__ import annotations

from bhashanthara.datasets.schema import (
    AnswerPreservationReview,
    AutomaticChecks,
    SinhalaQualityReview,
    TranslationStatus,
)


def decide_status(
    *,
    automatic_checks: AutomaticChecks,
    sinhala_quality: SinhalaQualityReview | None = None,
    answer_preservation: AnswerPreservationReview | None = None,
) -> TranslationStatus:
    if not automatic_checks.passed:
        return "needs_human_review"

    if answer_preservation is None and sinhala_quality is None:
        return "bronze"

    if answer_preservation is not None:
        if not answer_preservation.meaning_preserved or not answer_preservation.answer_preserved:
            return "needs_human_review"
        if answer_preservation.decision in {"reject", "needs_human_review"}:
            return "needs_human_review"

    if sinhala_quality is not None:
        if sinhala_quality.decision in {"reject", "needs_human_review"}:
            return "needs_human_review"
        if sinhala_quality.decision == "repair":
            return "needs_human_review"

    if sinhala_quality is not None and answer_preservation is not None:
        return "silver"

    return "bronze"
