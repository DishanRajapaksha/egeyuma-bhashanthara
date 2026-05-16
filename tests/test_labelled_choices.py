from __future__ import annotations

import pytest

from bhashanthara.datasets.conversion.labelled_choices import (
    LabelledChoiceConversionError,
    extract_labelled_choice_mcq,
)


def record() -> dict[str, object]:
    return {
        "id": "q1",
        "question": {
            "stem": "Which gas do plants use?",
            "choices": [
                {"label": "A", "text": "Oxygen"},
                {"label": "B", "text": "Carbon dioxide"},
                {"label": "C", "text": "Nitrogen"},
                {"label": "D", "text": "Hydrogen"},
            ],
        },
        "answerKey": "B",
    }


def test_extract_labelled_choice_mcq_normalises_arc_shape() -> None:
    mcq = extract_labelled_choice_mcq(record(), row_number=1)

    assert mcq.stem == "Which gas do plants use?"
    assert mcq.choices == ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"]
    assert mcq.choice_labels == ["A", "B", "C", "D"]
    assert mcq.answer_key == "B"
    assert mcq.answer_index == 1
    assert mcq.answer_label == "B"


def test_extract_labelled_choice_mcq_rejects_missing_answer() -> None:
    bad = record()
    bad["answerKey"] = "E"

    with pytest.raises(LabelledChoiceConversionError, match="answerKey does not match"):
        extract_labelled_choice_mcq(bad, row_number=1)


def test_extract_labelled_choice_mcq_rejects_non_four_choice_by_default() -> None:
    bad = record()
    question = bad["question"]
    assert isinstance(question, dict)
    choices = question["choices"]
    assert isinstance(choices, list)
    question["choices"] = choices[:3]

    with pytest.raises(LabelledChoiceConversionError, match="expected exactly 4 choices"):
        extract_labelled_choice_mcq(bad, row_number=1)


def test_extract_labelled_choice_mcq_can_allow_variable_choices() -> None:
    variable = record()
    question = variable["question"]
    assert isinstance(question, dict)
    choices = question["choices"]
    assert isinstance(choices, list)
    question["choices"] = choices[:3]

    mcq = extract_labelled_choice_mcq(
        variable,
        row_number=1,
        require_four_choices=False,
    )

    assert mcq.choices == ["Oxygen", "Carbon dioxide", "Nitrogen"]
