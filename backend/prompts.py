"""
Prompt templates for BriefForge backend.
"""

from rules import EXTRACTION_SCHEMA_HINT, SYSTEM_RULES


def build_chat_prompt(user_message: str) -> str:
    return f"""
SYSTEM RULES:
{SYSTEM_RULES}

USER MESSAGE:
{user_message}

Respond with clear sheet-metal-focused guidance.
""".strip()


def build_extract_prompt(raw_text: str) -> str:
    return f"""
SYSTEM RULES:
{SYSTEM_RULES}

TASK:
Extract a structured engineering brief from the input.

{EXTRACTION_SCHEMA_HINT}

INPUT:
{raw_text}

Return JSON only.
""".strip()


def build_markdown_prompt(brief_json: str) -> str:
    return f"""
SYSTEM RULES:
{SYSTEM_RULES}

TASK:
Turn the following brief JSON into a polished markdown engineering brief.
Use clear headings, bullet points, and a final "Open Questions" section.

BRIEF JSON:
{brief_json}
""".strip()
