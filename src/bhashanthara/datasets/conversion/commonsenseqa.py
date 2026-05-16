from __future__ import annotations

from pathlib import Path
from typing import Any

from bhashanthara.datasets.conversion.labelled_choices import (
    LabelledChoiceConversionError,
    extract_labelled_choice_mcq,
    string_value,
)
from bhashanthara.datasets.jsonl import read_jsonl
from bhashanthara.datasets.schema import MCQItem


class CommonsenseQAConversionError(Exception):
    """Raised when a CommonsenseQA JSONL row cannot be converted."""


def convert_commonsenseqa_jsonl(
    path: Path,
    *,
    subject: str,
    domain: str | None = None,
    source: str = "commonsenseqa",
    source_license: str = "unknown",
    id_prefix: str | None = None,
    require_five_choices: bool = True,
) -> list[MCQItem]:
    prefix = id_prefix or subject
    items: list[MCQItem] = []
    for row_number, raw in enumerate(read_jsonl(path), start=1):
        items.append(
            convert_commonsenseqa_record(
                raw,
                row_number=row_number,
                subject=subject,
                domain=domain,
                source=source,
                source_license=source_license,
                item_id=f"commonsenseqa_{prefix}_{row_number:06d}",
                require_five_choices=require_five_choices,
            )
        )
    return items


def convert_commonsenseqa_record(
    record: dict[str, Any],
    *,
    row_number: int,
    subject: str,
    domain: str | None,
    source: str,
    source_license: str,
    item_id: str,
    require_five_choices: bool = True,
) -> MCQItem:
    original_id = string_value(record.get("id")) or item_id
    try:
        mcq = extract_labelled_choice_mcq(
            record,
            row_number=row_number,
            require_four_choices=False,
        )
    except LabelledChoiceConversionError as exc:
        raise CommonsenseQAConversionError(str(exc)) from exc

    if require_five_choices and len(mcq.choices) != 5:
        raise CommonsenseQAConversionError(f"row {row_number}: expected exactly 5 choices")

    return MCQItem(
        id=item_id,
        question=mcq.stem,
        choices=mcq.choices,
        answer_index=mcq.answer_index,
        answer_label=mcq.answer_label,
        subject=subject,
        domain=domain,
        language_style="formal_english",
        source=source,
        metadata={
            "source_dataset": source,
            "source_license": source_license,
            "original_language": "en",
            "original_id": original_id,
            "commonsenseqa_answer_key": mcq.answer_key,
            "commonsenseqa_choice_labels": mcq.choice_labels,
            "commonsenseqa_row_number": row_number,
        },
    )
