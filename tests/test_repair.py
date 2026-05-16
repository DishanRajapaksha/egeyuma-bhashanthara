from __future__ import annotations

import pytest

from bhashanthara.datasets.schema import TranslatedMCQItem
from bhashanthara.repair.patches import RepairError, apply_repair_records, export_repair_items


def item(status: str = "needs_human_review") -> TranslatedMCQItem:
    return TranslatedMCQItem(
        id="item_001",
        question="පරණ ප්‍රශ්නය?",
        choices=["පරණ එක", "පරණ දෙක", "පරණ තුන", "පරණ හතර"],
        answer_index=1,
        answer_label="B",
        subject="science",
        domain="stem",
        metadata={"translation": {"status": status}},
    )


def test_export_repair_items_defaults_to_suspicious_items() -> None:
    repairs = export_repair_items(
        [
            item("silver"),
            item("needs_human_review"),
        ]
    )

    assert len(repairs) == 1
    assert repairs[0]["id"] == "item_001"
    assert repairs[0]["repair"]["question"] == "පරණ ප්‍රශ්නය?"


def test_export_repair_items_can_include_all_items() -> None:
    repairs = export_repair_items(
        [
            item("silver"),
            item("needs_human_review"),
        ],
        suspicious_only=False,
    )

    assert len(repairs) == 2


def test_apply_repair_records_updates_question_and_choices() -> None:
    original = item()
    repairs = [
        {
            "id": original.id,
            "repair": {
                "question": "නව ප්‍රශ්නය?",
                "choices": ["නව එක", "නව දෙක", "නව තුන", "නව හතර"],
                "notes": "Fixed wording.",
            },
        }
    ]

    updated = apply_repair_records([original], repairs)[0]

    assert updated.question == "නව ප්‍රශ්නය?"
    assert updated.choices == ["නව එක", "නව දෙක", "නව තුන", "නව හතර"]
    assert updated.answer_index == original.answer_index
    assert updated.answer_label == original.answer_label
    assert updated.metadata["repair"]["status"] == "applied"
    assert updated.metadata["repair"]["notes"] == "Fixed wording."
    assert updated.metadata["translation"]["status"] == "needs_human_review"


def test_apply_repair_records_rejects_choice_count_changes() -> None:
    original = item()
    repairs = [
        {
            "id": original.id,
            "repair": {
                "question": "නව ප්‍රශ්නය?",
                "choices": ["එක", "දෙක", "තුන"],
            },
        }
    ]

    with pytest.raises(RepairError, match="changes choice count"):
        apply_repair_records([original], repairs)
