# erp-rules

A server-side rule engine for [ERPNext](https://erpnext.com/) / [Frappe](https://frappeframework.com/).

Automatically corrects common data entry errors on documents before they are saved — so problems are prevented rather than caught after the fact.

---

## What it does

Each rule is an independent class that inspects a document and returns a list of changes it made. The engine runs all applicable rules on `before_save`, logs every change, and shows a summary notification to the user.

**Built-in rules:**

| Rule | Applies to | What it fixes |
|------|-----------|---------------|
| `CostCenterRule` | Sales Invoice, Purchase Invoice | Sets invoice-level `cost_center`: follows the Project's Default Cost Center if set; falls back to the company's "Projects" cost center if the project has none configured; sets "Main" if no project is assigned |
| `LineItemSyncRule` | Sales Invoice, Purchase Invoice | Ensures all line items match the invoice-level `project` and `cost_center` |
| `DueDateRule` | Purchase Invoice | Enforces a minimum gap between `posting_date` and `due_date`. System Managers can tick **Bypass Due Date Floor** on an invoice to skip the minimum for late/resubmitted invoices (shows a reminder instead of auto-bumping) |

---

## Architecture

```
erp_rules/
├── engine.py            # Runs rules, handles errors, notifies user
├── handlers/            # Frappe doc_event entry points — declare which rules apply
│   ├── sales_invoice.py
│   └── purchase_invoice.py
├── rules/
│   ├── base.py          # BaseRule abstract class
│   ├── cost_center_rule.py
│   ├── line_item_sync_rule.py
│   └── due_date_rule.py
└── tests/
```

### Adding a new rule

1. Create `erp_rules/rules/my_rule.py` implementing `BaseRule`:

```python
from erp_rules.rules.base import BaseRule

class MyRule(BaseRule):
    def applies_to(self, doc) -> bool:
        return bool(doc.some_field)

    def fix(self, doc) -> list[str]:
        # mutate doc, return list of human-readable change descriptions
        return ["some_field: old → new"]
```

2. Add it to the relevant handler's `RULES` list.

That's it — no changes to existing code.

---

## Installation

```bash
bench get-app erp_rules <repo-url>
bench --site <your-site> install-app erp_rules
bench --site <your-site> migrate
```

---

## Configuration

**`DueDateRule` minimum days** — edit `rules/due_date_rule.py`:

```python
MIN_DUE_DATE_DAYS = 29  # change to suit your billing policy
```

**Disabling a rule for a doctype** — remove it from the relevant handler's `RULES` list.

**Bypassing `DueDateRule` on a single invoice** — Purchase Invoices carry a
**Bypass Due Date Floor** checkbox (a Custom Field deployed via fixtures),
visible to **System Managers only**. Ticking it skips the minimum-days floor
for that invoice and shows a confirmation reminder instead of auto-bumping the
date. The role is re-checked server-side, so the flag cannot be set via the API
by non-managers. To change the authorized role, edit `BYPASS_ROLE` in
`rules/due_date_rule.py`.

---

## Error handling

If a rule raises an exception, the engine logs the error and continues — the document save is never blocked. All errors appear in the Frappe error log under the `erp_rules` logger.

---

## Running tests

Tests use `unittest` with `unittest.mock` and run inside the Frappe bench environment.

```bash
bench --site <your-site> run-tests --app erp_rules
```

---

## License

MIT — see [license.txt](license.txt).
