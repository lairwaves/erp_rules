import unittest
from unittest.mock import MagicMock, patch
from erp_rules.engine import run_rules
from erp_rules.rules.base import BaseRule


class AlwaysAppliesRule(BaseRule):
    def applies_to(self, doc):
        return True

    def fix(self, doc):
        return ["field: old → new"]


class NeverAppliesRule(BaseRule):
    def applies_to(self, doc):
        return False

    def fix(self, doc):
        return ["should not appear"]


class ExplodingRule(BaseRule):
    def applies_to(self, doc):
        return True

    def fix(self, doc):
        raise RuntimeError("intentional failure")


class TestEngine(unittest.TestCase):
    def _make_doc(self):
        doc = MagicMock()
        doc.doctype = "Sales Invoice"
        doc.name = "SINV-TEST-001"
        return doc

    @patch("erp_rules.engine.frappe")
    def test_notifies_user_when_changes_made(self, mock_frappe):
        mock_frappe.logger.return_value = MagicMock()
        doc = self._make_doc()
        run_rules(doc, [AlwaysAppliesRule()])
        mock_frappe.msgprint.assert_called_once()
        call_args = mock_frappe.msgprint.call_args[0][0]
        self.assertIn("[AlwaysAppliesRule]", call_args)
        self.assertIn("field: old → new", call_args)

    @patch("erp_rules.engine.frappe")
    def test_skips_non_applicable_rules(self, mock_frappe):
        mock_frappe.logger.return_value = MagicMock()
        doc = self._make_doc()
        run_rules(doc, [NeverAppliesRule()])
        mock_frappe.msgprint.assert_not_called()

    @patch("erp_rules.engine.frappe")
    def test_broken_rule_does_not_block_other_rules(self, mock_frappe):
        mock_frappe.logger.return_value = MagicMock()
        doc = self._make_doc()
        run_rules(doc, [ExplodingRule(), AlwaysAppliesRule()])
        mock_frappe.msgprint.assert_called_once()
        call_args = mock_frappe.msgprint.call_args[0][0]
        self.assertIn("[AlwaysAppliesRule]", call_args)

    @patch("erp_rules.engine.frappe")
    def test_broken_rule_logs_error(self, mock_frappe):
        mock_logger = MagicMock()
        mock_frappe.logger.return_value = mock_logger
        doc = self._make_doc()
        run_rules(doc, [ExplodingRule()])
        mock_logger.error.assert_called_once()

    @patch("erp_rules.engine.frappe")
    def test_no_notification_when_no_changes(self, mock_frappe):
        mock_frappe.logger.return_value = MagicMock()
        doc = self._make_doc()
        run_rules(doc, [NeverAppliesRule()])
        mock_frappe.msgprint.assert_not_called()
