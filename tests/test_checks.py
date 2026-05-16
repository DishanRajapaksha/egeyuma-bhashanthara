from __future__ import annotations

from bhashanthara.datasets.schema import MCQItem, TranslatedMCQItem
from bhashanthara.translate.checks import run_automatic_checks


def test_automatic_checks_pass_for_clean_sinhala_translation() -> None:
    original = MCQItem(
        id="item_001",
        question="Which gas is used by plants for photosynthesis?",
        choices=["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"],
        answer_index=1,
        answer_label="B",
    )
    translated = TranslatedMCQItem(
        id="item_001_si",
        question="ප්‍රභාසංශ්ලේෂණය සඳහා ශාක භාවිතා කරන වායුව කුමක්ද?",
        choices=["ඔක්සිජන්", "කාබන් ඩයොක්සයිඩ්", "නයිට්‍රජන්", "හයිඩ්‍රජන්"],
        answer_index=1,
        answer_label="B",
    )

    checks = run_automatic_checks(original, translated)

    assert checks.passed is True
    assert checks.issues == []
    assert checks.sinhala_ratio > 0.35


def test_automatic_checks_flag_duplicate_choices() -> None:
    original = MCQItem(
        id="item_001",
        question="Question?",
        choices=["A", "B", "C", "D"],
        answer_index=1,
        answer_label="B",
    )
    translated = TranslatedMCQItem(
        id="item_001_si",
        question="ප්‍රශ්නය?",
        choices=["එක", "දෙක", "දෙක", "හතර"],
        answer_index=1,
        answer_label="B",
    )

    checks = run_automatic_checks(original, translated)

    assert checks.passed is False
    assert "duplicate_translated_choices" in checks.issues


def test_automatic_checks_flag_choice_count_change() -> None:
    original = MCQItem(
        id="item_001",
        question="Question?",
        choices=["A", "B", "C", "D"],
        answer_index=1,
        answer_label="B",
    )
    translated = TranslatedMCQItem(
        id="item_001_si",
        question="ප්‍රශ්නය?",
        choices=["එක", "දෙක", "තුන"],
        answer_index=1,
        answer_label="B",
    )

    checks = run_automatic_checks(original, translated)

    assert checks.passed is False
    assert "choice_count_changed" in checks.issues
