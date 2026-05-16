from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bhashanthara.datasets.schema import ANSWER_LABELS


class LabelledChoiceConversionError(Exception):
    """Raised when a labelled-choice MCQ record cannot be normalised."""


@dataclass(frozen=True)
class LabelledChoiceMCQ:
    stem: str
    choices: list[str]
    choice_labels: list[str]
    answer_key: str
    answer_index: int
    answer_label: str


def extract_labelled_choice_mcq(
    record: dict[str, Any],
    *,
    row_number: int,
    require_four_choices: bool = True,
) -> LabelledChoiceMCQ:
    answer_key = string_value(record.get("answerKey")).upper()
    question = record.get("question")
    if not isinstance(question, dict):
        raise LabelledChoiceConversionError(f"row {row_number}: question must be an object")

    stem = string_value(question.get("stem"))
    if not stem:
        raise LabelledChoiceConversionError(f"row {row_number}: question.stem is empty")

    raw_choices = question.get("choices")
    if not isinstance(raw_choices, list):
        raise LabelledChoiceConversionError(f"row {row_number}: question.choices must be a list")
    if require_four_choices and len(raw_choices) != 4:
        raise LabelledChoiceConversionError(f"row {row_number}: expected exactly 4 choices")
    if len(raw_choices) < 2 or len(raw_choices) > len(ANSWER_LABELS):
        raise LabelledChoiceConversionError(
            f"row {row_number}: expected between 2 and {len(ANSWER_LABELS)} choices"
        )

    choice_labels: list[str] = []
    choices: list[str] = []
    for index, raw_choice in enumerate(raw_choices):
        label, text = extract_choice(raw_choice, row_number=row_number, index=index)
        choice_labels.append(label)
        choices.append(text)

    try:
        answer_index = choice_labels.index(answer_key)
    except ValueError as exc:
        raise LabelledChoiceConversionError(
            f"row {row_number}: answerKey does not match any choice label"
        ) from exc

    return LabelledChoiceMCQ(
        stem=stem,
        choices=choices,
        choice_labels=choice_labels,
        answer_key=answer_key,
        answer_index=answer_index,
        answer_label=ANSWER_LABELS[answer_index],
    )


def extract_choice(raw_choice: Any, *, row_number: int, index: int) -> tuple[str, str]:
    choice_number = index + 1
    if not isinstance(raw_choice, dict):
        raise LabelledChoiceConversionError(
            f"row {row_number}: choice {choice_number} must be an object"
        )

    label = string_value(raw_choice.get("label")).upper()
    text = string_value(raw_choice.get("text"))
    if not label:
        raise LabelledChoiceConversionError(
            f"row {row_number}: choice {choice_number} has empty label"
        )
    if not text:
        raise LabelledChoiceConversionError(
            f"row {row_number}: choice {choice_number} has empty text"
        )
    return label, text


def string_value(value: Any) -> str:
    return str(value).strip() if value is not None else ""
