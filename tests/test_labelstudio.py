from __future__ import annotations

from bhashanthara.datasets.schema import TranslatedMCQItem
from bhashanthara.review.labelstudio import LABEL_CONFIG, export_labelstudio_tasks


def item(status: str) -> TranslatedMCQItem:
    return TranslatedMCQItem(
        id=f"item_{status}",
        question="ප්‍රශ්නය?",
        choices=["එක", "දෙක", "තුන", "හතර"],
        answer_index=1,
        answer_label="B",
        subject="science",
        domain="stem",
        metadata={"translation": {"status": status}},
    )


def test_export_labelstudio_tasks_defaults_to_suspicious_items() -> None:
    tasks = export_labelstudio_tasks(
        [
            item("silver"),
            item("needs_human_review"),
        ]
    )

    assert len(tasks) == 1
    assert tasks[0]["data"]["id"] == "item_needs_human_review"


def test_export_labelstudio_tasks_can_include_all_items() -> None:
    tasks = export_labelstudio_tasks(
        [
            item("silver"),
            item("needs_human_review"),
        ],
        suspicious_only=False,
    )

    assert len(tasks) == 2


def test_label_config_contains_required_fields() -> None:
    assert "decision" in LABEL_CONFIG
    assert "failure_reason" in LABEL_CONFIG
    assert "notes" in LABEL_CONFIG
