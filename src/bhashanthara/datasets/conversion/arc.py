from __future__ import annotations

from pathlib import Path
from typing import Any

from bhashanthara.datasets.jsonl import read_jsonl
from bhashanthara.datasets.schema import ANSWER_LABELS, MCQItem


class ARCConversionError(Exception):
    """Raised when an ARC JSONL row cannot be converted."""


def convert_arc_jsonl(
    path: Path,
    *,
    subject: str,
    domain: str | None = None,
    source: str = "ai2_arc",
    source_license: str = "cc-by-sa-4.0",
    id_prefix: str | None = None,
    require_four_choices: bool = True,
) -> list[MCQItem]:
    prefix = id_prefix or subject
    items: list[MCQItem] = []
    for row_number, raw in enumerate(read_jsonl(path), start=1):
        items.append(
            convert_arc_record(
                raw,
                row_number=row_number,
                subject=subject,
                domain=domain,
                source=source,
                source_license=source_license,
                item_id=f"arc_{prefix}_{row_number:06d}",
                require_four_choices=require_four_choices,
            )
        )
    return items


def convert_arc_record(
    record: dict[str, Any],
    *,
    row_number: int,
    subject: str,
    domain: str | None,
    source: str,
    source_license: str,
    item_id: str,
    require_four_choices: bool = True,
) -> MCQItem:
    original_id = _string_value(record.get("id")) or item_id
    answer_key = _string_value(record.get("answerKey")).upper()
    question = record.get("question")
    if not isinstance(question, dict):
        raise ARCConversionError(f"row {row_number}: question must be an object")

    stem = _string_value(question.get("stem"))
    if not stem:
        raise ARCConversionError(f"row {row_number}: question.stem is empty")

    raw_choices = question.get("choices")
    if not isinstance(raw_choices, list):
        raise ARCConversionError(f"row {row_number}: question.choices must be a list")
    if require_four_choices and len(raw_choices) != 4:
        raise ARCConversionError(f"row {row_number}: expected exactly 4 choices")
    if len(raw_choices) < 2 or len(raw_choices) > 5:
        raise ARCConversionError(f"row {row_number}: expected between 2 and 5 choices")

    choice_labels: list[str] = []
    choices: list[str] = []
    for index, raw_choice in enumerate(raw_choices):
        if not isinstance(raw_choice, dict):
            raise ARCConversionError(f"row {row_number}: choice {index + 1} must be an object")
        label = _string_value(raw_choice.get("label"))
        text = _string_value(raw_choice.get("text"))
        if not label:
            raise ARCConversionError(f"row {row_number}: choice {index + 1} has empty label")
        if not text:
            raise ARCConversionError(f"row {row_number}: choice {index + 1} has empty text")
        choice_labels.append(label.upper())
        choices.append(text)

    try:
        answer_index = choice_labels.index(answer_key)
    except ValueError as exc:
        raise ARCConversionError(
            f"row {row_number}: answerKey does not match any choice label"
        ) from exc

    answer_label = ANSWER_LABELS[answer_index]
    return MCQItem(
        id=item_id,
        question=stem,
        choices=choices,
        answer_index=answer_index,
        answer_label=answer_label,
        subject=subject,
        domain=domain,
        language_style="formal_english",
        source=source,
        metadata={
            "source_dataset": source,
            "source_license": source_license,
            "original_language": "en",
            "original_id": original_id,
            "arc_answer_key": answer_key,
            "arc_choice_labels": choice_labels,
            "arc_row_number": row_number,
        },
    )


def _string_value(value: Any) -> str:
    return str(value).strip() if value is not None else ""
