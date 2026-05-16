from __future__ import annotations

import csv
from pathlib import Path

from bhashanthara.datasets.schema import ANSWER_LABELS, MCQItem


class MMLUConversionError(Exception):
    """Raised when an MMLU CSV row cannot be converted."""


def convert_mmlu_csv(
    path: Path,
    *,
    subject: str,
    domain: str | None = None,
    source: str = "cais/mmlu",
    source_license: str = "MIT",
    id_prefix: str | None = None,
) -> list[MCQItem]:
    prefix = id_prefix or f"mmlu_{subject}"
    items: list[MCQItem] = []

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for row_number, row in enumerate(reader, start=1):
            if _is_empty_row(row):
                continue
            items.append(
                convert_mmlu_row(
                    row,
                    row_number=row_number,
                    subject=subject,
                    domain=domain,
                    source=source,
                    source_license=source_license,
                    item_id=f"{prefix}_{row_number:06d}",
                )
            )
    return items


def convert_mmlu_row(
    row: list[str],
    *,
    row_number: int,
    subject: str,
    domain: str | None,
    source: str,
    source_license: str,
    item_id: str,
) -> MCQItem:
    if len(row) != 6:
        raise MMLUConversionError(
            f"row {row_number}: expected 6 columns: question,A,B,C,D,answer"
        )

    question = row[0].strip()
    choices = [value.strip() for value in row[1:5]]
    answer_label = row[5].strip().upper()

    if not question:
        raise MMLUConversionError(f"row {row_number}: question is empty")
    if any(not choice for choice in choices):
        raise MMLUConversionError(f"row {row_number}: one or more choices are empty")
    if answer_label not in ANSWER_LABELS[:4]:
        raise MMLUConversionError(f"row {row_number}: answer must be one of A, B, C, D")

    answer_index = ANSWER_LABELS.index(answer_label)
    return MCQItem(
        id=item_id,
        question=question,
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
            "mmlu_subject": subject,
            "mmlu_row_number": row_number,
        },
    )


def _is_empty_row(row: list[str]) -> bool:
    return not row or all(not value.strip() for value in row)
