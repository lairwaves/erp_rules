import unittest
from unittest.mock import MagicMock
from erp_rules.rules.line_item_sync_rule import LineItemSyncRule


class TestLineItemSyncRule(unittest.TestCase):
    def setUp(self):
        self.rule = LineItemSyncRule()

    def _make_doc(self, project=None, cost_center=None, items=None):
        doc = MagicMock()
        doc.project = project
        doc.cost_center = cost_center
        doc.items = items or []
        return doc

    def _make_item(self, item_code="ITEM-001", project=None, cost_center=None):
        item = MagicMock()
        item.item_code = item_code
        item.project = project
        item.cost_center = cost_center
        return item

    def test_applies_when_project_set(self):
        doc = self._make_doc(project="Coverbase")
        self.assertTrue(self.rule.applies_to(doc))

    def test_applies_when_cost_center_set(self):
        doc = self._make_doc(cost_center="Projects - 5")
        self.assertTrue(self.rule.applies_to(doc))

    def test_does_not_apply_when_neither_set(self):
        doc = self._make_doc()
        self.assertFalse(self.rule.applies_to(doc))

    def test_syncs_project_to_line_items(self):
        item = self._make_item(project=None)
        doc = self._make_doc(project="Coverbase", items=[item])
        self.rule.fix(doc)
        self.assertEqual(item.project, "Coverbase")

    def test_syncs_cost_center_to_line_items(self):
        item = self._make_item(cost_center="Main - 508")
        doc = self._make_doc(cost_center="Projects - 5", items=[item])
        self.rule.fix(doc)
        self.assertEqual(item.cost_center, "Projects - 5")

    def test_no_change_when_items_already_correct(self):
        item = self._make_item(project="Coverbase", cost_center="Projects - 5")
        doc = self._make_doc(project="Coverbase", cost_center="Projects - 5", items=[item])
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])

    def test_empty_items_returns_no_changes(self):
        doc = self._make_doc(project="Coverbase", items=[])
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])
