from __future__ import annotations

import pytest

from bhashanthara.datasets.schema import MCQItem
from bhashanthara.pilot.sample import select_pilot_items


def item(index: int) -> MCQItem:
    return MCQItem(
        id=f"item_{index:03d}",
        question=f"Question {index}?",
        choices=["A", "B", "C", "D"],
        answer_index=1,
        answer_label="B",
    )


def test_select_pilot_items_selects_requested_count() -> None:
    items = [item(index) for index in range(10)]

    selection = select_pilot_items(items, count=5)

    assert selection.requested == 5
    assert selection.selected == 5
    assert [selected.id for selected in selection.items] == [
        "item_000",
        "item_001",
        "item_002",
        "item_003",
        "item_004",
    ]


def test_select_pilot_items_handles_short_input() -> None:
    items = [item(index) for index in range(3)]

    selection = select_pilot_items(items, count=50)

    assert selection.requested == 50
    assert selection.selected == 3


def test_select_pilot_items_rejects_non_positive_count() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        select_pilot_items([item(1)], count=0)
