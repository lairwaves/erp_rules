from frappe.utils import add_days, getdate
from erp_rules.rules.base import BaseRule

MIN_DUE_DATE_DAYS = 29  # per community billing guidelines


class DueDateRule(BaseRule):
    def applies_to(self, doc) -> bool:
        return bool(doc.posting_date and doc.due_date)

    def fix(self, doc) -> list[str]:
        earliest = add_days(doc.posting_date, MIN_DUE_DATE_DAYS)
        if getdate(doc.due_date) < getdate(earliest):
            old = doc.due_date
            doc.due_date = earliest
            return [f"due_date: {old} → {earliest} (minimum {MIN_DUE_DATE_DAYS} days)"]
        return []
