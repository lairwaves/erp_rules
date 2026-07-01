# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-01

### Added
- `DueDateRule` bypass: a **Bypass Due Date Floor** checkbox (Custom Field,
  deployed via fixtures) on Purchase Invoices. When ticked, the rule skips the
  29-day minimum for late/resubmitted invoices and shows a confirmation reminder
  instead of auto-bumping `due_date`.
- The bypass is restricted to the **System Manager** role. The role is
  re-checked server-side in `DueDateRule.fix()`, so the flag cannot be set via
  the API/import by non-managers — `depends_on` only hides the field in the UI.

### Notes
- The bypass field is Purchase Invoice only, matching the single doctype that
  `DueDateRule` runs on.
- Deploying this version installs a Custom Field via fixtures; run
  `bench --site <site> migrate` after install/upgrade so the field is created.

## [0.0.1] - 2026-06-08

### Added
- Initial release. Server-side rule engine running on `before_save` with
  `CostCenterRule`, `LineItemSyncRule` (Sales + Purchase Invoice) and
  `DueDateRule` (Purchase Invoice).
