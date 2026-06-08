import frappe
from erp_rules.rules.base import BaseRule


class CostCenterRule(BaseRule):
    def applies_to(self, doc) -> bool:
        return True

    def fix(self, doc) -> list[str]:
        expected = self._resolve_cost_center(doc)
        if expected and doc.cost_center != expected:
            old = doc.cost_center
            doc.cost_center = expected
            return [f"cost_center: {old!r} → {expected!r}"]
        return []

    def _resolve_cost_center(self, doc) -> str | None:
        if not doc.company:
            return None
        if doc.project:
            cc = frappe.db.get_value("Project", doc.project, "cost_center")
            if cc:
                return cc
            return frappe.db.get_value(
                "Cost Center",
                {"cost_center_name": "Projects", "company": doc.company},
                "name",
            )
        return frappe.db.get_value(
            "Cost Center",
            {"cost_center_name": "Main", "company": doc.company},
            "name",
        )
