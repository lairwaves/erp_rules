import frappe
from erp_rules.rules.base import BaseRule


def run_rules(doc, rules: list[BaseRule]) -> None:
    messages = _collect_changes(doc, rules)
    if messages:
        frappe.msgprint(
            "<br>".join(messages),
            alert=True,
            indicator="blue",
        )


def _collect_changes(doc, rules: list[BaseRule]) -> list[str]:
    logger = frappe.logger("erp_rules", allow_site=True)
    messages = []

    for rule in rules:
        if not rule.applies_to(doc):
            continue
        try:
            changes = rule.fix(doc)
        except Exception:
            logger.error(
                f"[erp-rules] {doc.doctype} {doc.name} — {rule.__class__.__name__} failed",
                exc_info=True,
            )
            continue
        if changes:
            rule_name = rule.__class__.__name__
            logger.info(
                f"[erp-rules] {doc.doctype} {doc.name} — {rule_name}: {changes}"
            )
            messages.append(f"[{rule_name}] " + "; ".join(changes))

    return messages
