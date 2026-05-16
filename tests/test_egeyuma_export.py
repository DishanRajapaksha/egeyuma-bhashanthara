from __future__ import annotations

from bhashanthara.datasets.schema import TranslatedMCQItem
from bhashanthara.export.egeyuma import (
    export_egeyuma_items,
    should_export_item,
    to_egeyuma_item,
    translation_status,
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
        source="translated_from:cais/mmlu",
        metadata={"translation": {"status": status}},
    )


def test_translation_status_reads_metadata() -> None:
    assert translation_status(item("silver")) == "silver"


def test_should_export_item_respects_min_status() -> None:
    assert should_export_item(item("gold"), "gold") is True
    assert should_export_item(item("silver"), "gold") is False
    assert should_export_item(item("silver"), "bronze") is True
    assert should_export_item(item("rejected"), "bronze") is False


def test_to_egeyuma_item_maps_fields() -> None:
    exported = to_egeyuma_item(item("gold"), dataset_name="sinhala-mmlu", language="si")

    assert exported["dataset"] == "sinhala-mmlu"
    assert exported["task_type"] == "mcq"
    assert exported["language"] == "si"
    assert exported["answer_index"] == 1
    assert exported["category"] == "stem"
    assert exported["metadata"]["exported_from"] == "egeyuma-bhashanthara"
    assert exported["metadata"]["export_schema"] == "egeyuma.mcq.v1"


def test_export_egeyuma_items_filters_by_status() -> None:
    exported = export_egeyuma_items(
        [item("bronze"), item("silver"), item("gold"), item("needs_human_review")],
        dataset_name="sinhala-mmlu",
        min_status="silver",
    )

    assert [entry["id"] for entry in exported] == ["item_silver", "item_gold"]
