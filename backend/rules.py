"""
Domain rules and guardrails for the Sheet Metal Engineering Briefing Agent.
"""

import json

SYSTEM_RULES = """
You are BriefForge, a sheet metal engineering briefing assistant.

Your job:
- Convert user intent into actionable engineering briefs.
- Keep output practical for fabrication, manufacturing, and review workflows.
- Use concise, technical language.

Always include relevant engineering details when available:
- Material and thickness
- Manufacturing process (laser cut, bend, punch, weld, etc.)
- Tolerances and critical dimensions
- Surface finish or coating
- Quantity, lead time, and quality constraints
- Risks, open questions, and assumptions

Safety and quality rules:
- Never fabricate unknown specs. Mark unknown values clearly as TBD.
- Call out missing details that can cause manufacturing defects.
- Prioritize DFM (Design for Manufacturability) and inspection readiness.
- If requirements conflict, list the conflict explicitly.
""".strip()


EXTRACTION_SCHEMA_HINT = """
Return a JSON object with this shape:
{
  "title": "string",
  "project_context": "string",
  "requirements": ["string"],
  "constraints": ["string"],
  "assumptions": ["string"],
  "open_questions": ["string"],
  "manufacturing_notes": ["string"],
  "acceptance_criteria": ["string"]
}
""".strip()


SHEET_METAL_RULES = {
    "minimum_bend_radius": {
        "unit": "x_thickness",
        "S235": {"value": 1.0, "rule": "r_min >= 1.0 * t"},
        "S304": {"value": 1.5, "rule": "r_min >= 1.5 * t"},
        "Al5083": {"value": 1.2, "rule": "r_min >= 1.2 * t"},
    },
    "minimum_flange_height": {
        "unit": "x_thickness_plus_radius",
        "S235": {"rule": "h_min >= max(4.0 * t, r + 1.0 * t)"},
        "S304": {"rule": "h_min >= max(5.0 * t, r + 1.5 * t)"},
        "Al5083": {"rule": "h_min >= max(4.0 * t, r + 1.2 * t)"},
    },
    "hole_edge_distance": {
        "unit": "x_hole_diameter_or_thickness",
        "S235": {"rule": "e_min >= max(1.5 * D, 2.0 * t)"},
        "S304": {"rule": "e_min >= max(2.0 * D, 2.5 * t)"},
        "Al5083": {"rule": "e_min >= max(1.75 * D, 2.0 * t)"},
    },
    "corner_relief_requirements": {
        "unit": "mm_and_x_thickness",
        "S235": {
            "required_if": "adjacent_bends_or_thickness_change",
            "relief_width_rule": "w >= max(1.0 * t, 1.0 mm)",
            "relief_depth_rule": "d >= r + t",
            "recommended_shape": "obround",
        },
        "S304": {
            "required_if": "adjacent_bends_or_tight_internal_corner",
            "relief_width_rule": "w >= max(1.5 * t, 1.5 mm)",
            "relief_depth_rule": "d >= r + 1.5 * t",
            "recommended_shape": "obround",
        },
        "Al5083": {
            "required_if": "adjacent_bends_or_material_flow_risk",
            "relief_width_rule": "w >= max(1.2 * t, 1.2 mm)",
            "relief_depth_rule": "d >= r + 1.2 * t",
            "recommended_shape": "obround",
        },
    },
}


def get_sheet_metal_rules_json() -> str:
    return json.dumps(SHEET_METAL_RULES, ensure_ascii=False, indent=2)
