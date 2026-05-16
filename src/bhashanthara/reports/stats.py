from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from bhashanthara.datasets.schema import TranslatedMCQItem


@dataclass(frozen=True)
class TranslationStats:
    total: int
    by_status: dict[str, int]
    by_subject: dict[str, int]
    by_domain: dict[str, int]
    suspicious_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "by_status": self.by_status,
            "by_subject": self.by_subject,
            "by_domain": self.by_domain,
            "suspicious_count": self.suspicious_count,
        }


def _translation_status(item: TranslatedMCQItem) -> str:
    translation = item.metadata.get("translation")
    if not isinstance(translation, dict):
        return "unknown"
    status = translation.get("status")
    return str(status or "unknown")


def is_suspicious(item: TranslatedMCQItem) -> bool:
    status = _translation_status(item)
    if status in {"needs_human_review", "rejected"}:
        return True

    translation = item.metadata.get("translation")
    if not isinstance(translation, dict):
        return True

    automatic_checks = translation.get("automatic_checks")
    if isinstance(automatic_checks, dict) and automatic_checks.get("issues"):
        return True

    answer_preservation = translation.get("answer_preservation")
    if isinstance(answer_preservation, dict):
        if answer_preservation.get("answer_preserved") is False:
            return True
        if answer_preservation.get("meaning_preserved") is False:
            return True

    sinhala_quality = translation.get("sinhala_quality")
    if isinstance(sinhala_quality, dict) and sinhala_quality.get("decision") in {
        "repair",
        "reject",
        "needs_human_review",
    }:
        return True

    return False


def collect_translation_stats(items: list[TranslatedMCQItem]) -> TranslationStats:
    by_status = Counter(_translation_status(item) for item in items)
    by_subject = Counter(item.subject or "unknown" for item in items)
    by_domain = Counter(item.domain or "unknown" for item in items)
    suspicious_count = sum(1 for item in items if is_suspicious(item))

    return TranslationStats(
        total=len(items),
        by_status=dict(sorted(by_status.items())),
        by_subject=dict(sorted(by_subject.items())),
        by_domain=dict(sorted(by_domain.items())),
        suspicious_count=suspicious_count,
    )
