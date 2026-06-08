import unittest
from unittest.mock import MagicMock
from erp_rules.rules.due_date_rule import DueDateRule


class TestDueDateRule(unittest.TestCase):
    def setUp(self):
        self.rule = DueDateRule()

    def _make_doc(self, posting_date=None, due_date=None):
        doc = MagicMock()
        doc.posting_date = posting_date
        doc.due_date = due_date
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
