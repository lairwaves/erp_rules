import unittest
from unittest.mock import MagicMock, patch
from erp_rules.rules.cost_center_rule import CostCenterRule


class TestCostCenterRule(unittest.TestCase):
    def setUp(self):
        self.rule = CostCenterRule()

    def _make_doc(self, project=None, cost_center=None, company="508.dev"):
        doc = MagicMock()
        doc.project = project
        doc.cost_center = cost_center
        doc.company = company
        return doc

    def test_always_applies(self):
        self.assertTrue(self.rule.applies_to(self._make_doc(project="Coverbase")))
        self.assertTrue(self.rule.applies_to(self._make_doc(project=None)))

    # --- has project, project has default cost center ---

    @patch("erp_rules.rules.cost_center_rule.frappe")
    def test_project_with_default_cc_fills_empty(self, mock_frappe):
        mock_frappe.db.get_value.return_value = "Projects - 5"
        doc = self._make_doc(project="Coverbase", cost_center=None)
        changes = self.rule.fix(doc)
        self.assertEqual(doc.cost_center, "Projects - 5")
        self.assertTrue(len(changes) > 0)

    @patch("erp_rules.rules.cost_center_rule.frappe")
    def test_project_with_default_cc_overwrites_wrong(self, mock_frappe):
        mock_frappe.db.get_value.return_value = "Projects - 5"
        doc = self._make_doc(project="Coverbase", cost_center="Main - 5")
        changes = self.rule.fix(doc)
        self.assertEqual(doc.cost_center, "Projects - 5")
        self.assertTrue(len(changes) > 0)

    @patch("erp_rules.rules.cost_center_rule.frappe")
    def test_project_with_default_cc_no_change_when_correct(self, mock_frappe):
        mock_frappe.db.get_value.return_value = "Projects - 5"
        doc = self._make_doc(project="Coverbase", cost_center="Projects - 5")
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])

    # --- has project, project has NO default cost center → fallback to "Projects" ---

    @patch("erp_rules.rules.cost_center_rule.frappe")
    def test_project_without_default_cc_falls_back_to_projects(self, mock_frappe):
        def get_value(doctype, filters_or_name, fieldname=None):
            if doctype == "Project":
                return None
            if doctype == "Cost Center":
                return "Projects - 5"
        mock_frappe.db.get_value.side_effect = get_value
        doc = self._make_doc(project="Coverbase", cost_center="Main - 5")
        changes = self.rule.fix(doc)
        self.assertEqual(doc.cost_center, "Projects - 5")
        self.assertTrue(len(changes) > 0)

    @patch("erp_rules.rules.cost_center_rule.frappe")
    def test_project_without_default_cc_no_change_if_projects_not_found(self, mock_frappe):
        mock_frappe.db.get_value.return_value = None
        doc = self._make_doc(project="Coverbase", cost_center=None)
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])

    # --- no project → fallback to "Main" ---

    @patch("erp_rules.rules.cost_center_rule.frappe")
    def test_no_project_sets_main(self, mock_frappe):
        mock_frappe.db.get_value.return_value = "Main - 5"
        doc = self._make_doc(project=None, cost_center=None)
        changes = self.rule.fix(doc)
        self.assertEqual(doc.cost_center, "Main - 5")
        self.assertTrue(len(changes) > 0)

    @patch("erp_rules.rules.cost_center_rule.frappe")
    def test_no_project_no_change_when_already_main(self, mock_frappe):
        mock_frappe.db.get_value.return_value = "Main - 5"
        doc = self._make_doc(project=None, cost_center="Main - 5")
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])

    @patch("erp_rules.rules.cost_center_rule.frappe")
    def test_no_project_no_change_if_main_not_found(self, mock_frappe):
        mock_frappe.db.get_value.return_value = None
        doc = self._make_doc(project=None, cost_center=None)
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])

    def test_no_change_when_company_missing(self):
        doc = self._make_doc(project=None, cost_center=None, company=None)
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])
