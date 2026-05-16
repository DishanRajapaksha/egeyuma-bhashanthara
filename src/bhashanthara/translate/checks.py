from __future__ import annotations

import re

from bhashanthara.datasets.schema import AutomaticChecks, MCQItem, TranslatedMCQItem

SINHALA_RE = re.compile(r"[\u0D80-\u0DFF]")
LATIN_RE = re.compile(r"[A-Za-z]")


def character_ratio(pattern: re.Pattern[str], texts: list[str]) -> float:
    joined = " ".join(texts)
    if not joined:
        return 0.0
    return len(pattern.findall(joined)) / len(joined)


def has_no_empty_fields(item: TranslatedMCQItem) -> bool:
    return bool(item.question.strip()) and all(bool(choice.strip()) for choice in item.choices)


def has_no_duplicate_choices(item: TranslatedMCQItem) -> bool:
    normalised = [choice.strip().casefold() for choice in item.choices]
    return len(normalised) == len(set(normalised))


def run_automatic_checks(original: MCQItem, translated: TranslatedMCQItem) -> AutomaticChecks:
    texts = [translated.question, *translated.choices]
    issues: list[str] = []

    same_choice_count = len(original.choices) == len(translated.choices)
    if not same_choice_count:
        issues.append("choice_count_changed")

    answer_index_preserved = original.answer_index == translated.answer_index
    if not answer_index_preserved:
        issues.append("answer_index_changed")

    no_empty_fields = has_no_empty_fields(translated)
    if not no_empty_fields:
        issues.append("empty_question_or_choice")

    no_duplicate_choices = has_no_duplicate_choices(translated)
    if not no_duplicate_choices:
        issues.append("duplicate_translated_choices")

    sinhala_ratio = character_ratio(SINHALA_RE, texts)
    unexpected_english_ratio = character_ratio(LATIN_RE, texts)
    if sinhala_ratio < 0.35:
        issues.append("low_sinhala_ratio")

    return AutomaticChecks(
        same_choice_count=same_choice_count,
        answer_index_preserved=answer_index_preserved,
        no_empty_fields=no_empty_fields,
        no_duplicate_choices=no_duplicate_choices,
        sinhala_ratio=sinhala_ratio,
        unexpected_english_ratio=unexpected_english_ratio,
        issues=issues,
    )
