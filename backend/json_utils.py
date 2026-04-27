"""
Utilities for robust JSON extraction from LLM responses.
"""

import json
import re
from typing import Any, Dict


def _strip_markdown_fences(text: str) -> str:
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(fence_pattern, text)
    if match:
        return match.group(1).strip()
    return text.strip()


def parse_json_response(raw_text: str) -> Dict[str, Any]:
    """
    Parse potentially fenced JSON content into a Python dictionary.
    """
    cleaned = _strip_markdown_fences(raw_text)
    return json.loads(cleaned)


def safe_json_dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
