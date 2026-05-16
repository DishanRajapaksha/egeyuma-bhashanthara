from __future__ import annotations

from bhashanthara.datasets.schema import TranslatedMCQItem
from bhashanthara.reports.stats import collect_translation_stats, is_suspicious


def item_with_status(status: str) -> TranslatedMCQItem:
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


def test_is_suspicious_flags_needs_human_review() -> None:
    assert is_suspicious(item_with_status("needs_human_review")) is True


def test_is_suspicious_accepts_silver_without_issues() -> None:
    assert is_suspicious(item_with_status("silver")) is False


def test_collect_translation_stats_counts_statuses() -> None:
    stats = collect_translation_stats(
        [
            item_with_status("silver"),
            item_with_status("needs_human_review"),
        ]
    )

    assert stats.total == 2
    assert stats.by_status == {"needs_human_review": 1, "silver": 1}
    assert stats.suspicious_count == 1
