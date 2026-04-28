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
    "material_grade_rules": {
        "S355": {
            "yield_strength_mpa": 355,
            "weldable": True,
            "minimum_bend_radius_rule": "r_min >= 1.5 * t",
        },
        "Al6061": {
            "minimum_bend_radius_rule": "r_min >= 2.0 * t",
            "laser_cutting_max_thickness_mm": 6.0,
            "preferred_surface_finishes": ["anodized", "alodine"],
        },
        "DX51D": {
            "coating": "HDG (hot-dip galvanized) present",
            "minimum_bend_radius_rule": "r_min >= 1.0 * t",
            "vent_hole_requirement": {
                "required": True,
                "diameter_mm": "8-10",
            },
        },
    },
    "tolerance_classes_iso_2768": {
        "unit": "mm",
        "ISO_2768-f": [
            {"range": "0.5-3", "tolerance": "±0.05"},
            {"range": ">3-6", "tolerance": "±0.05"},
            {"range": ">6-30", "tolerance": "±0.10"},
            {"range": ">30-120", "tolerance": "±0.15"},
            {"range": ">120-400", "tolerance": "±0.20"},
            {"range": ">400-1000", "tolerance": "±0.30"},
            {"range": ">1000-2000", "tolerance": "±0.50"},
        ],
        "ISO_2768-m": [
            {"range": "0.5-3", "tolerance": "±0.10"},
            {"range": ">3-6", "tolerance": "±0.10"},
            {"range": ">6-30", "tolerance": "±0.20"},
            {"range": ">30-120", "tolerance": "±0.30"},
            {"range": ">120-400", "tolerance": "±0.50"},
            {"range": ">400-1000", "tolerance": "±0.80"},
            {"range": ">1000-2000", "tolerance": "±1.20"},
        ],
        "ISO_2768-c": [
            {"range": "0.5-3", "tolerance": "±0.20"},
            {"range": ">3-6", "tolerance": "±0.30"},
            {"range": ">6-30", "tolerance": "±0.50"},
            {"range": ">30-120", "tolerance": "±0.80"},
            {"range": ">120-400", "tolerance": "±1.20"},
            {"range": ">400-1000", "tolerance": "±2.00"},
            {"range": ">1000-2000", "tolerance": "±3.00"},
        ],
    },
    "surface_finish_rules": {
        "raw": {
            "compatible_materials": ["S235", "S304", "Al5083", "S355", "Al6061", "DX51D"],
            "minimum_thickness_mm": {
                "S235": 1.0,
                "S304": 0.8,
                "Al5083": 1.2,
                "S355": 1.2,
                "Al6061": 1.0,
                "DX51D": 0.8,
            },
            "notes": [
                "No coating build-up allowance required.",
                "Deburr and edge-break still required for handling safety.",
            ],
        },
        "painted": {
            "compatible_materials": ["S235", "S304", "Al5083", "S355", "Al6061", "DX51D"],
            "minimum_thickness_mm": {
                "S235": 1.0,
                "S304": 1.0,
                "Al5083": 1.2,
                "S355": 1.2,
                "Al6061": 1.2,
                "DX51D": 0.8,
            },
            "notes": [
                "Surface cleaning and primer compatibility check required.",
                "Mask functional contact or grounding surfaces when needed.",
            ],
        },
        "galvanized": {
            "compatible_materials": ["S235", "S355", "DX51D"],
            "minimum_thickness_mm": {
                "S235": 2.0,
                "S355": 2.0,
                "DX51D": 0.8,
            },
            "notes": [
                "Typically not applied to S304 and Al5083 in this rule set.",
                "Vent/drain holes required for hot-dip galvanizing geometry.",
                "DX51D has HDG coating already; validate coating continuity after forming.",
            ],
        },
        "powder_coated": {
            "compatible_materials": ["S235", "S304", "Al5083", "S355", "Al6061", "DX51D"],
            "minimum_thickness_mm": {
                "S235": 1.0,
                "S304": 1.0,
                "Al5083": 1.5,
                "S355": 1.2,
                "Al6061": 1.2,
                "DX51D": 0.8,
            },
            "notes": [
                "Account for coating thickness on fit-critical interfaces.",
                "Use pre-treatment suitable for stainless and aluminum grades.",
            ],
        },
        "electroplated": {
            "compatible_materials": ["S235", "S304", "S355"],
            "minimum_thickness_mm": {
                "S235": 0.8,
                "S304": 0.8,
                "S355": 1.0,
            },
            "notes": [
                "Al5083 requires special process route; excluded by default.",
                "Hydrogen embrittlement mitigation may be required for high-strength steels.",
            ],
        },
        "anodized": {
            "compatible_materials": ["Al5083", "Al6061"],
            "minimum_thickness_mm": {
                "Al5083": 1.0,
                "Al6061": 1.0,
            },
            "notes": [
                "Suitable aluminum alloy pre-treatment required before anodizing.",
                "Mask threaded and electrical contact faces where required.",
            ],
        },
        "alodine": {
            "compatible_materials": ["Al5083", "Al6061"],
            "minimum_thickness_mm": {
                "Al5083": 1.0,
                "Al6061": 1.0,
            },
            "notes": [
                "Conversion coating for corrosion protection and paint adhesion.",
                "Process bath control and post-rinse quality checks are required.",
            ],
        },
    },
    "minimum_bend_radius": {
        "unit": "x_thickness",
        "S235": {"value": 1.0, "rule": "r_min >= 1.0 * t"},
        "S304": {"value": 1.5, "rule": "r_min >= 1.5 * t"},
        "Al5083": {"value": 1.2, "rule": "r_min >= 1.2 * t"},
        "S355": {"value": 1.5, "rule": "r_min >= 1.5 * t"},
        "Al6061": {"value": 2.0, "rule": "r_min >= 2.0 * t"},
        "DX51D": {"value": 1.0, "rule": "r_min >= 1.0 * t"},
    },
    "minimum_flange_height": {
        "unit": "x_thickness_plus_radius",
        "S235": {"rule": "h_min >= max(4.0 * t, r + 1.0 * t)"},
        "S304": {"rule": "h_min >= max(5.0 * t, r + 1.5 * t)"},
        "Al5083": {"rule": "h_min >= max(4.0 * t, r + 1.2 * t)"},
        "S355": {"rule": "h_min >= max(4.5 * t, r + 1.5 * t)"},
        "Al6061": {"rule": "h_min >= max(5.0 * t, r + 2.0 * t)"},
        "DX51D": {"rule": "h_min >= max(4.0 * t, r + 1.0 * t)"},
    },
    "hole_edge_distance": {
        "unit": "x_hole_diameter_or_thickness",
        "S235": {"rule": "e_min >= max(1.5 * D, 2.0 * t)"},
        "S304": {"rule": "e_min >= max(2.0 * D, 2.5 * t)"},
        "Al5083": {"rule": "e_min >= max(1.75 * D, 2.0 * t)"},
        "S355": {"rule": "e_min >= max(1.75 * D, 2.5 * t)"},
        "Al6061": {"rule": "e_min >= max(2.0 * D, 2.0 * t)"},
        "DX51D": {"rule": "e_min >= max(1.5 * D, 2.0 * t)"},
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
        "S355": {
            "required_if": "adjacent_bends_or_high_stress_forming",
            "relief_width_rule": "w >= max(1.5 * t, 1.5 mm)",
            "relief_depth_rule": "d >= r + 1.5 * t",
            "recommended_shape": "obround",
        },
        "Al6061": {
            "required_if": "adjacent_bends_or_crack_risk_at_outer_fiber",
            "relief_width_rule": "w >= max(2.0 * t, 2.0 mm)",
            "relief_depth_rule": "d >= r + 2.0 * t",
            "recommended_shape": "obround",
        },
        "DX51D": {
            "required_if": "adjacent_bends_or_coating_damage_risk",
            "relief_width_rule": "w >= max(1.0 * t, 1.0 mm)",
            "relief_depth_rule": "d >= r + 1.0 * t",
            "recommended_shape": "obround",
        },
    },
}


def get_sheet_metal_rules_json() -> str:
    return json.dumps(SHEET_METAL_RULES, ensure_ascii=False, indent=2)
