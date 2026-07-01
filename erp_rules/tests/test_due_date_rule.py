import unittest
from unittest.mock import MagicMock, patch
from erp_rules.rules.due_date_rule import DueDateRule


class TestDueDateRule(unittest.TestCase):
    def setUp(self):
        self.rule = DueDateRule()

    def _make_doc(self, posting_date=None, due_date=None):
        doc = MagicMock()
        doc.posting_date = posting_date
        doc.due_date = due_date
        doc.bypass_due_date_floor = False
        return doc

    def test_applies_when_both_dates_set(self):
        doc = self._make_doc(posting_date="2026-01-01", due_date="2026-02-01")
        self.assertTrue(self.rule.applies_to(doc))

    def test_does_not_apply_when_missing_posting_date(self):
        doc = self._make_doc(due_date="2026-02-01")
        self.assertFalse(self.rule.applies_to(doc))

    def test_does_not_apply_when_missing_due_date(self):
        doc = self._make_doc(posting_date="2026-01-01")
        self.assertFalse(self.rule.applies_to(doc))

    def test_fixes_due_date_when_too_close(self):
        doc = self._make_doc(posting_date="2026-01-01", due_date="2026-01-10")
        changes = self.rule.fix(doc)
        self.assertEqual(doc.due_date, "2026-01-30")
        self.assertTrue(len(changes) > 0)

    def test_no_change_when_due_date_is_exactly_29_days(self):
        doc = self._make_doc(posting_date="2026-01-01", due_date="2026-01-30")
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])

    def test_no_change_when_due_date_is_more_than_29_days(self):
        doc = self._make_doc(posting_date="2026-01-01", due_date="2026-03-01")
        changes = self.rule.fix(doc)
        self.assertEqual(changes, [])

    def test_bypass_by_system_manager_skips_floor_and_reminds(self):
        doc = self._make_doc(posting_date="2026-01-01", due_date="2026-01-10")
        doc.bypass_due_date_floor = True
        with patch("frappe.get_roles", return_value=["System Manager"]):
            changes = self.rule.fix(doc)
        self.assertEqual(doc.due_date, "2026-01-10")  # date must NOT be changed
        self.assertEqual(len(changes), 1)
        self.assertIn("bypassed", changes[0])

    def test_bypass_by_non_manager_is_ignored_and_floor_enforced(self):
        # depends_on only hides the checkbox; a non-manager who sets the flag via
        # API/import must NOT bypass the floor — the server re-checks the role.
        doc = self._make_doc(posting_date="2026-01-01", due_date="2026-01-10")
        doc.bypass_due_date_floor = True
        with patch("frappe.get_roles", return_value=["508_Engineer"]):
            changes = self.rule.fix(doc)
        self.assertEqual(doc.due_date, "2026-01-30")  # floor still enforced
        self.assertEqual(len(changes), 1)
        self.assertIn("minimum", changes[0])
        self.assertNotIn("bypassed", changes[0])

    def test_bypass_flag_false_still_enforces_floor(self):
        doc = self._make_doc(posting_date="2026-01-01", due_date="2026-01-10")
        doc.bypass_due_date_floor = False
        changes = self.rule.fix(doc)
        self.assertEqual(doc.due_date, "2026-01-30")
        self.assertTrue(len(changes) > 0)

    def test_bypass_by_manager_with_date_already_above_floor_still_reminds(self):
        # Ticking bypass when the date is already fine leaves the date untouched
        # and still emits the confirm reminder (never silently no-ops).
        doc = self._make_doc(posting_date="2026-01-01", due_date="2026-03-01")
        doc.bypass_due_date_floor = True
        with patch("frappe.get_roles", return_value=["System Manager"]):
            changes = self.rule.fix(doc)
        self.assertEqual(doc.due_date, "2026-03-01")  # date must NOT be changed
        self.assertEqual(len(changes), 1)
        self.assertIn("bypassed", changes[0])
