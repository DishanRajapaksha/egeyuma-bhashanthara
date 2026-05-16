from __future__ import annotations

from pathlib import Path

import pytest

from bhashanthara.datasets.conversion.commonsenseqa import (
    CommonsenseQAConversionError,
    convert_commonsenseqa_jsonl,
    convert_commonsenseqa_record,
)


def commonsenseqa_record() -> dict[str, object]:
    return {
        "id": "075e483d21c29a511267ef62bedc0461",
        "question": {
            "stem": "Where would you find magazines along side many other printed works?",
            "choices": [
                {"label": "A", "text": "doctor"},
                {"label": "B", "text": "bookstore"},
                {"label": "C", "text": "market"},
                {"label": "D", "text": "train station"},
                {"label": "E", "text": "mortuary"},
            ],
        },
        "answerKey": "B",
    }


def test_convert_commonsenseqa_record_creates_mcq_item() -> None:
    item = convert_commonsenseqa_record(
        commonsenseqa_record(),
        row_number=1,
        subject="commonsenseqa",
        domain="commonsense_reasoning",
        source="commonsenseqa",
        source_license="unknown",
        item_id="commonsenseqa_commonsenseqa_000001",
    )

    assert item.id == "commonsenseqa_commonsenseqa_000001"
    assert item.answer_index == 1
    assert item.answer_label == "B"
    assert item.metadata["original_id"] == "075e483d21c29a511267ef62bedc0461"
    assert item.metadata["commonsenseqa_answer_key"] == "B"
    assert item.metadata["commonsenseqa_choice_labels"] == ["A", "B", "C", "D", "E"]


def test_convert_commonsenseqa_record_rejects_non_five_choice_rows_by_default() -> None:
    record = commonsenseqa_record()
    question = record["question"]
    assert isinstance(question, dict)
    choices = question["choices"]
    assert isinstance(choices, list)
    question["choices"] = choices[:4]

    with pytest.raises(CommonsenseQAConversionError, match="expected exactly 5 choices"):
        convert_commonsenseqa_record(
            record,
            row_number=1,
            subject="commonsenseqa",
            domain="commonsense_reasoning",
            source="commonsenseqa",
            source_license="unknown",
            item_id="commonsenseqa_commonsenseqa_000001",
        )


def test_convert_commonsenseqa_record_rejects_missing_answer_label() -> None:
    record = commonsenseqa_record()
    record["answerKey"] = "Z"

    with pytest.raises(CommonsenseQAConversionError, match="answerKey does not match"):
        convert_commonsenseqa_record(
            record,
            row_number=1,
            subject="commonsenseqa",
            domain="commonsense_reasoning",
            source="commonsenseqa",
            source_license="unknown",
            item_id="commonsenseqa_commonsenseqa_000001",
        )


def test_convert_commonsenseqa_jsonl_reads_rows(tmp_path: Path) -> None:
    input_path = tmp_path / "commonsenseqa.jsonl"
    input_path.write_text(
        '{"id":"q1","question":{"stem":"Question 1?","choices":['
        '{"text":"A","label":"A"},{"text":"B","label":"B"},'
        '{"text":"C","label":"C"},{"text":"D","label":"D"},'
        '{"text":"E","label":"E"}]},"answerKey":"B"}\n'
        '{"id":"q2","question":{"stem":"Question 2?","choices":['
        '{"text":"A","label":"A"},{"text":"B","label":"B"},'
        '{"text":"C","label":"C"},{"text":"D","label":"D"},'
        '{"text":"E","label":"E"}]},"answerKey":"D"}\n',
        encoding="utf-8",
    )

    items = convert_commonsenseqa_jsonl(
        input_path,
        subject="commonsenseqa",
        domain="commonsense_reasoning",
    )

    assert len(items) == 2
    assert items[0].id == "commonsenseqa_commonsenseqa_000001"
    assert items[1].answer_label == "D"
