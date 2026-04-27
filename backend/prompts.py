"""
Prompt templates for BriefForge backend.
"""

from rules import EXTRACTION_SCHEMA_HINT, SYSTEM_RULES, get_sheet_metal_rules_json

SHEET_METAL_RULES_JSON = get_sheet_metal_rules_json()


def build_chat_prompt(user_message: str) -> str:
    return f"""
SYSTEM RULES:
{SYSTEM_RULES}

SHEET METAL RULE ENGINE (JSON):
{SHEET_METAL_RULES_JSON}

MANDATORY RULE APPLICATION:
- Evaluate the user request against the rule engine above before answering.
- In every response, include a short "Rule Check" section.
- In "Rule Check", explicitly state PASS/FAIL/TBD per relevant rule category.
- If any value is missing, mark as TBD and request exact missing inputs.

USER MESSAGE:
{user_message}

Respond with clear sheet-metal-focused guidance.
""".strip()


def build_extract_prompt(raw_text: str) -> str:
    return f"""
SYSTEM RULES:
{SYSTEM_RULES}

SHEET METAL RULE ENGINE (JSON):
{SHEET_METAL_RULES_JSON}

TASK:
Extract a structured engineering brief from the input.
While extracting, evaluate constraints with the rule engine.

{EXTRACTION_SCHEMA_HINT}

INPUT:
{raw_text}

Return JSON only.
""".strip()


def build_markdown_prompt(brief_json: str) -> str:
    return f"""
SYSTEM RULES:
{SYSTEM_RULES}

SHEET METAL RULE ENGINE (JSON):
{SHEET_METAL_RULES_JSON}

TASK:
Turn the following brief JSON into a polished markdown engineering brief.
Use clear headings, bullet points, and a final "Open Questions" section.
Include a "Rule Check" section that evaluates the brief against the rule engine.

BRIEF JSON:
{brief_json}
""".strip()
