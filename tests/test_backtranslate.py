from __future__ import annotations

from bhashanthara.datasets.schema import TranslatedMCQItem, TranslationCandidate
from bhashanthara.translate.backtranslate import attach_backtranslation, backtranslation_report


def item() -> TranslatedMCQItem:
    return TranslatedMCQItem(
        id="item_001_si",
        question="ප්‍රශ්නය?",
        choices=["එක", "දෙක", "තුන", "හතර"],
        answer_index=1,
        answer_label="B",
        subject="science",
        domain="stem",
        metadata={"translation": {"status": "silver"}},
    )


def test_attach_backtranslation_adds_metadata() -> None:
    translated = item()
    candidate = TranslationCandidate(
        question="Question?",
        choices=["One", "Two", "Three", "Four"],
        notes="",
    )

    updated = attach_backtranslation(translated, candidate, "qwen3-14b")

    backtranslation = updated.metadata["translation"]["backtranslation"]
    assert backtranslation["model"] == "qwen3-14b"
    assert backtranslation["question"] == "Question?"
    assert backtranslation["choices"] == ["One", "Two", "Three", "Four"]


def test_backtranslation_report_returns_compact_record() -> None:
    translated = item()
    candidate = TranslationCandidate(
        question="Question?",
        choices=["One", "Two", "Three", "Four"],
        notes="Looks close.",
    )
    updated = attach_backtranslation(translated, candidate, "qwen3-14b")

    report = backtranslation_report(updated)

    assert report is not None
    assert report["id"] == "item_001_si"
    assert report["question"] == "Question?"
    assert report["notes"] == "Looks close."


def test_backtranslation_report_returns_none_without_metadata() -> None:
    assert backtranslation_report(item()) is None
