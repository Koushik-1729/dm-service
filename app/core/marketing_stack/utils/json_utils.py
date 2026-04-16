import re
import json
from typing import Any, Union
from loguru import logger


def extract_json(text: str) -> str:
    """Robustly extract JSON from AI response that may contain markdown, thinking blocks, etc."""
    if not text:
        return "{}"

    # Try 1: Direct parse (already clean JSON)
    stripped = text.strip()
    if stripped.startswith(("{", "[")):
        return stripped

    # Try 2: Extract from ```json ... ``` blocks
    json_block = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if json_block:
        return json_block.group(1).strip()

    # Try 3: Find first { or [ and last } or ]
    first_brace = None
    last_brace = None

    for i, ch in enumerate(text):
        if ch in ('{', '[') and first_brace is None:
            first_brace = i
            break

    for i in range(len(text) - 1, -1, -1):
        if text[i] in ('}', ']'):
            last_brace = i
            break

    if first_brace is not None and last_brace is not None and last_brace > first_brace:
        return text[first_brace:last_brace + 1]

    # Try 4: Return as-is and let caller handle
    return stripped


def safe_parse_json(text: str, fallback: Any = None) -> Union[dict, list, Any]:
    """Parse JSON from AI response with robust extraction and fallback."""
    extracted = extract_json(text)
    try:
        return json.loads(extracted)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed: {e}. Extracted: {extracted[:200]}")
        return fallback if fallback is not None else {}
