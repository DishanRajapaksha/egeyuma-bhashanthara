from __future__ import annotations

from dataclasses import dataclass

from bhashanthara.datasets.schema import MCQItem


@dataclass(frozen=True)
class PilotSelection:
    items: list[MCQItem]
    requested: int
    selected: int


def select_pilot_items(items: list[MCQItem], *, count: int = 50) -> PilotSelection:
    if count <= 0:
        raise ValueError("pilot count must be greater than zero")
    selected = items[:count]
    return PilotSelection(items=selected, requested=count, selected=len(selected))
