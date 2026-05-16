from __future__ import annotations

import json
from typing import Any


class JSONExtractionError(Exception):
    """Raised when a model response does not contain usable JSON."""


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise JSONExtractionError("response did not contain a JSON object") from exc
        try:
            parsed = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as fallback_exc:
            raise JSONExtractionError(f"invalid JSON object: {fallback_exc.msg}") from fallback_exc

    if not isinstance(parsed, dict):
        raise JSONExtractionError("response JSON must be an object")
    return parsed
