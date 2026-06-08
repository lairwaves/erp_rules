from erp_rules.rules.base import BaseRule


class LineItemSyncRule(BaseRule):
    def applies_to(self, doc) -> bool:
        return bool(doc.project or doc.cost_center)

    def fix(self, doc) -> list[str]:
        changes = []
        for item in doc.items:
            item_changes = []
            if doc.project and item.project != doc.project:
                item.project = doc.project
                item_changes.append(f"project={doc.project}")
            if doc.cost_center and item.cost_center != doc.cost_center:
                item.cost_center = doc.cost_center
                item_changes.append(f"cost_center={doc.cost_center}")
            if item_changes:
                changes.append(f"{item.item_code} ({', '.join(item_changes)})")
        return changes
