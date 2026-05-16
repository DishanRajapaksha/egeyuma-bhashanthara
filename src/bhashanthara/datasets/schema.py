from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

ANSWER_LABELS = tuple("ABCDE")
ReviewDecision = Literal["accept", "repair", "reject", "needs_human_review"]
TranslationStatus = Literal["bronze", "silver", "gold", "rejected", "needs_human_review"]


class MCQItem(BaseModel):
    id: str
    task_type: Literal["mcq"] = "mcq"
    question: str = Field(min_length=1)
    choices: list[str] = Field(min_length=2, max_length=5)
    answer_index: int = Field(ge=0, le=4)
    answer_label: str
    subject: str | None = None
    domain: str | None = None
    difficulty: str | None = None
    language_style: str = "formal_english"
    source: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("answer_label")
    @classmethod
    def normalise_answer_label(cls, value: str) -> str:
        label = value.strip().upper()
        if label not in ANSWER_LABELS:
            raise ValueError(f"answer_label must be one of {ANSWER_LABELS}")
        return label

    @model_validator(mode="after")
    def validate_answer_alignment(self) -> MCQItem:
        if self.answer_index >= len(self.choices):
            raise ValueError("answer_index points outside choices")
        expected = ANSWER_LABELS[self.answer_index]
        if self.answer_label != expected:
            raise ValueError(
                f"answer_label {self.answer_label!r} does not match answer_index "
                f"{self.answer_index}; expected {expected!r}"
            )
        return self


class AutomaticChecks(BaseModel):
    same_choice_count: bool
    answer_index_preserved: bool
    no_empty_fields: bool
    no_duplicate_choices: bool
    sinhala_ratio: float = Field(ge=0.0, le=1.0)
    unexpected_english_ratio: float = Field(ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            self.same_choice_count
            and self.answer_index_preserved
            and self.no_empty_fields
            and self.no_duplicate_choices
            and not self.issues
        )


class SinhalaQualityReview(BaseModel):
    decision: ReviewDecision
    score: int = Field(ge=1, le=5)
    notes: str = ""


class AnswerPreservationReview(BaseModel):
    decision: ReviewDecision
    meaning_preserved: bool
    answer_preserved: bool
    notes: str = ""


class TranslationMetadata(BaseModel):
    source_language: str = "en"
    target_language: str = "si"
    status: TranslationStatus = "bronze"
    translator_model: str | None = None
    sinhala_reviewer_model: str | None = None
    answer_reviewer_model: str | None = None
    automatic_checks: AutomaticChecks | None = None
    sinhala_quality: SinhalaQualityReview | None = None
    answer_preservation: AnswerPreservationReview | None = None


class TranslationCandidate(BaseModel):
    question: str
    choices: list[str] = Field(min_length=2, max_length=5)
    notes: str = ""


class TranslationRepairCandidate(TranslationCandidate):
    repaired: bool = True


class TranslatedMCQItem(MCQItem):
    language_style: str = "translated_sinhala"


def translated_item_from_candidate(
    *,
    original: MCQItem,
    candidate: TranslationCandidate,
    translator_model: str,
) -> TranslatedMCQItem:
    metadata = dict(original.metadata)
    metadata.update(
        {
            "original_id": original.id,
            "source_dataset": metadata.get("source_dataset") or original.source,
            "translation": TranslationMetadata(translator_model=translator_model).model_dump(),
        }
    )
    return TranslatedMCQItem(
        id=f"{original.id}_si",
        question=candidate.question,
        choices=candidate.choices,
        answer_index=original.answer_index,
        answer_label=original.answer_label,
        subject=original.subject,
        domain=original.domain,
        difficulty=original.difficulty,
        source=f"translated_from:{original.source or 'unknown'}",
        metadata=metadata,
    )
