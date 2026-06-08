from erp_rules.engine import run_rules
from erp_rules.rules.cost_center_rule import CostCenterRule
from erp_rules.rules.line_item_sync_rule import LineItemSyncRule

# Order matters: CostCenterRule must run before LineItemSyncRule so that
# line items are synced against the already-corrected invoice cost_center.
RULES = [CostCenterRule(), LineItemSyncRule()]


def before_save(doc, method):
    run_rules(doc, RULES)
