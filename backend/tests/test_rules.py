import json
import unittest

from rules import SHEET_METAL_RULES, get_sheet_metal_rules_json


class TestNewMaterialRules(unittest.TestCase):
    def test_minimum_bend_radius_contains_new_materials(self):
        bend_rules = SHEET_METAL_RULES["minimum_bend_radius"]
        self.assertEqual(bend_rules["S355"]["value"], 1.5)
        self.assertEqual(bend_rules["Al6061"]["value"], 2.0)
        self.assertEqual(bend_rules["DX51D"]["value"], 1.0)

    def test_material_grade_rules_contains_requested_properties(self):
        material_rules = SHEET_METAL_RULES["material_grade_rules"]
        self.assertEqual(material_rules["S355"]["yield_strength_mpa"], 355)
        self.assertTrue(material_rules["S355"]["weldable"])
        self.assertEqual(material_rules["Al6061"]["laser_cutting_max_thickness_mm"], 6.0)
        self.assertIn("anodized", material_rules["Al6061"]["preferred_surface_finishes"])
        self.assertIn("alodine", material_rules["Al6061"]["preferred_surface_finishes"])
        self.assertTrue(material_rules["DX51D"]["vent_hole_requirement"]["required"])
        self.assertEqual(material_rules["DX51D"]["vent_hole_requirement"]["diameter_mm"], "8-10")

    def test_json_export_contains_new_materials(self):
        payload = json.loads(get_sheet_metal_rules_json())
        self.assertIn("S355", payload["minimum_bend_radius"])
        self.assertIn("Al6061", payload["minimum_bend_radius"])
        self.assertIn("DX51D", payload["minimum_bend_radius"])


if __name__ == "__main__":
    unittest.main()
