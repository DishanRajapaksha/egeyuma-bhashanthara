from __future__ import annotations

from collections.abc import Iterable

from bhashanthara.datasets.schema import MCQItem, TranslatedMCQItem, TranslationMetadata
from bhashanthara.models.openai_compatible import OpenAICompatibleClient
from bhashanthara.translate.checks import run_automatic_checks
from bhashanthara.translate.decide import decide_status
from bhashanthara.translate.generate import translate_item
from bhashanthara.translate.verify import (
    review_answer_preservation,
    review_sinhala_quality,
)


def _set_translation_metadata(
    translated: TranslatedMCQItem,
    metadata: TranslationMetadata,
) -> TranslatedMCQItem:
    item_metadata = dict(translated.metadata)
    item_metadata["translation"] = metadata.model_dump()
    return translated.model_copy(update={"metadata": item_metadata})


def translate_and_check(
    item: MCQItem,
    translator: OpenAICompatibleClient,
) -> TranslatedMCQItem:
    translated = translate_item(item, translator)
    checks = run_automatic_checks(item, translated)
    metadata = TranslationMetadata(
        status=decide_status(automatic_checks=checks),
        translator_model=translator.model,
        automatic_checks=checks,
    )
    return _set_translation_metadata(translated, metadata)


def translate_verify_item(
    item: MCQItem,
    translator: OpenAICompatibleClient,
    sinhala_reviewer: OpenAICompatibleClient | None = None,
    answer_reviewer: OpenAICompatibleClient | None = None,
) -> TranslatedMCQItem:
    translated = translate_and_check(item, translator)
    translation = TranslationMetadata.model_validate(translated.metadata["translation"])

    sinhala_review = None
    answer_review = None

    if sinhala_reviewer is not None:
        sinhala_review = review_sinhala_quality(item, translated, sinhala_reviewer)
        translation.sinhala_reviewer_model = sinhala_reviewer.model
        translation.sinhala_quality = sinhala_review

    if answer_reviewer is not None:
        answer_review = review_answer_preservation(item, translated, answer_reviewer)
        translation.answer_reviewer_model = answer_reviewer.model
        translation.answer_preservation = answer_review

    if translation.automatic_checks is None:
        raise RuntimeError("translation metadata is missing automatic checks")

    translation.status = decide_status(
        automatic_checks=translation.automatic_checks,
        sinhala_quality=sinhala_review,
        answer_preservation=answer_review,
    )
    return _set_translation_metadata(translated, translation)


def translate_many(
    items: Iterable[MCQItem],
    translator: OpenAICompatibleClient,
    limit: int | None = None,
) -> list[TranslatedMCQItem]:
    output: list[TranslatedMCQItem] = []
    for index, item in enumerate(items):
        if limit is not None and index >= limit:
            break
        output.append(translate_and_check(item, translator))
    return output
