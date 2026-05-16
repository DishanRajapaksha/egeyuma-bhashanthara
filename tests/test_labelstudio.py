from __future__ import annotations

from bhashanthara.datasets.schema import TranslatedMCQItem
from bhashanthara.review.labelstudio import (
    LABEL_CONFIG,
    apply_labelstudio_reviews,
    export_labelstudio_tasks,
)


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


def test_apply_labelstudio_reviews_marks_accept_as_gold() -> None:
    original = item("needs_human_review")
    labelstudio_tasks = [
        {
            "data": {"id": original.id},
            "annotations": [
                {
                    "id": 123,
                    "result": [
                        {
                            "from_name": "decision",
                            "value": {"choices": ["accept"]},
                        },
                        {
                            "from_name": "notes",
                            "value": {"text": ["Looks correct."]},
                        },
                    ],
                }
            ],
        }
    ]

    updated = apply_labelstudio_reviews([original], labelstudio_tasks)[0]

    assert updated.metadata["translation"]["status"] == "gold"
    assert updated.metadata["human_review"]["decision"] == "accept"
    assert updated.metadata["human_review"]["notes"] == "Looks correct."


def test_apply_labelstudio_reviews_marks_reject_as_rejected() -> None:
    original = item("needs_human_review")
    labelstudio_tasks = [
        {
            "data": {"id": original.id},
            "annotations": [
                {
                    "id": 124,
                    "result": [
                        {
                            "from_name": "decision",
                            "value": {"choices": ["reject"]},
                        },
                        {
                            "from_name": "failure_reason",
                            "value": {"choices": ["answer_changed"]},
                        },
                    ],
                }
            ],
        }
    ]

    updated = apply_labelstudio_reviews([original], labelstudio_tasks)[0]

    assert updated.metadata["translation"]["status"] == "rejected"
    assert updated.metadata["human_review"]["failure_reasons"] == ["answer_changed"]


def test_label_config_contains_required_fields() -> None:
    assert "decision" in LABEL_CONFIG
    assert "failure_reason" in LABEL_CONFIG
    assert "notes" in LABEL_CONFIG
