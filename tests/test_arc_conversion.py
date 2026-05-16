from __future__ import annotations

from pathlib import Path

import pytest

from bhashanthara.datasets.conversion.arc import (
    ARCConversionError,
    convert_arc_jsonl,
    convert_arc_record,
)


def arc_record() -> dict[str, object]:
    return {
        "id": "Mercury_7015875",
        "question": {
            "stem": "Which gas do plants use for photosynthesis?",
            "choices": [
                {"text": "Oxygen", "label": "A"},
                {"text": "Carbon dioxide", "label": "B"},
                {"text": "Nitrogen", "label": "C"},
                {"text": "Hydrogen", "label": "D"},
            ],
        },
        "answerKey": "B",
    }


def test_convert_arc_record_creates_mcq_item() -> None:
    item = convert_arc_record(
        arc_record(),
        row_number=1,
        subject="arc_challenge",
        domain="science",
        source="ai2_arc",
        source_license="cc-by-sa-4.0",
        item_id="arc_arc_challenge_000001",
    )

    assert item.id == "arc_arc_challenge_000001"
    assert item.question == "Which gas do plants use for photosynthesis?"
    assert item.answer_index == 1
    assert item.answer_label == "B"
    assert item.metadata["original_id"] == "Mercury_7015875"
    assert item.metadata["arc_answer_key"] == "B"
    assert item.metadata["arc_choice_labels"] == ["A", "B", "C", "D"]


def test_convert_arc_record_rejects_non_four_choice_rows_by_default() -> None:
    record = arc_record()
    question = record["question"]
    assert isinstance(question, dict)
    question["choices"] = question["choices"][:3]

    with pytest.raises(ARCConversionError, match="expected exactly 4 choices"):
        convert_arc_record(
            record,
            row_number=1,
            subject="arc_challenge",
            domain="science",
            source="ai2_arc",
            source_license="cc-by-sa-4.0",
            item_id="arc_arc_challenge_000001",
        )


def test_convert_arc_record_rejects_missing_answer_label() -> None:
    record = arc_record()
    record["answerKey"] = "E"

    with pytest.raises(ARCConversionError, match="answerKey does not match"):
        convert_arc_record(
            record,
            row_number=1,
            subject="arc_challenge",
            domain="science",
            source="ai2_arc",
            source_license="cc-by-sa-4.0",
            item_id="arc_arc_challenge_000001",
        )


def test_convert_arc_jsonl_reads_rows(tmp_path: Path) -> None:
    input_path = tmp_path / "arc.jsonl"
    input_path.write_text(
        '{"id":"q1","question":{"stem":"Question 1?","choices":['
        '{"text":"A","label":"A"},{"text":"B","label":"B"},'
        '{"text":"C","label":"C"},{"text":"D","label":"D"}]},"answerKey":"B"}\n'
        '{"id":"q2","question":{"stem":"Question 2?","choices":['
        '{"text":"A","label":"A"},{"text":"B","label":"B"},'
        '{"text":"C","label":"C"},{"text":"D","label":"D"}]},"answerKey":"D"}\n',
        encoding="utf-8",
    )

    items = convert_arc_jsonl(
        input_path,
        subject="arc_challenge",
        domain="science",
    )

    assert len(items) == 2
    assert items[0].id == "arc_arc_challenge_000001"
    assert items[1].answer_label == "D"
