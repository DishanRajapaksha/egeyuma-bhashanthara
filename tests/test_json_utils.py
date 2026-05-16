from __future__ import annotations

import pytest

from bhashanthara.translate.json_utils import JSONExtractionError, extract_json_object


def test_extract_json_object_accepts_plain_json() -> None:
    assert extract_json_object('{"question": "x"}') == {"question": "x"}


def test_extract_json_object_accepts_fenced_json() -> None:
    assert extract_json_object('```json\n{"question": "x"}\n```') == {"question": "x"}


def test_extract_json_object_extracts_json_from_extra_text() -> None:
    assert extract_json_object('Here: {"question": "x"} done') == {"question": "x"}


def test_extract_json_object_rejects_missing_json() -> None:
    with pytest.raises(JSONExtractionError):
        extract_json_object("no json here")
