import frappe
from frappe.utils import add_days, getdate
from erp_rules.rules.base import BaseRule

MIN_DUE_DATE_DAYS = 29  # per community billing guidelines
BYPASS_ROLE = "System Manager"
BYPASS_REMINDER = "due_date floor bypassed — confirm {due_date} is correct for this late/resubmitted invoice"


class DueDateRule(BaseRule):
    def applies_to(self, doc) -> bool:
        return bool(doc.posting_date and doc.due_date)

    def fix(self, doc) -> list[str]:
        # The bypass flag is honored only for BYPASS_ROLE. depends_on hides the
        # checkbox in the UI but is not a write guard, so re-check the role here:
        # a non-manager who sets the flag via API/import is ignored and the floor
        # is still enforced.
        if getattr(doc, "bypass_due_date_floor", False) and BYPASS_ROLE in frappe.get_roles():
            return [BYPASS_REMINDER.format(due_date=doc.due_date)]

        earliest = add_days(doc.posting_date, MIN_DUE_DATE_DAYS)
        if getdate(doc.due_date) < getdate(earliest):
            old = doc.due_date
            doc.due_date = earliest
            return [f"due_date: {old} → {earliest} (minimum {MIN_DUE_DATE_DAYS} days)"]
        return []
