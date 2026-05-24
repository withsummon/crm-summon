# BNI CRM Validation Matrix

Updated for the BNI teal alignment workstream.

## Lead Management vs `Lead Gen Data.xlsx`

| Area | Status | Notes |
| --- | --- | --- |
| Workbook parsing with leading blank column | `implemented` | XML/openpyxl fallback parser handles sparse cells and ignores helper column A. |
| Column mapping for `COMPANY`, `Industry`, `PHONE`, `NAME`, `POSITION`, `EMAIL`, `PIC`, `STATUS`, `DATE`, `FEEDBACK`, `FOLLOW UP`, `LINKEDIN` | `implemented` | Preview now exposes detected mapping and missing columns. |
| Preview warnings for dirty rows and unmapped columns | `implemented` | Workbook and row-level warnings are summarized before import. |
| Duplicate-safe import through lead capture flow | `implemented` | Reuses `capture_lead` and reports duplicate skips. |
| PIC ownership mapping | `partial` | PIC is stored as lead referrer and resolves to `lead_owner` only when it matches an existing user. |
| Feedback persistence | `implemented` | Imported as `FCRM Note` on created leads when enabled. |
| Follow-up persistence | `implemented` | Imported as `CRM Task` on created leads when enabled. |
| Dashboard coverage for workbook-driven lead metrics | `implemented` | `get_bni_crm_dashboard` now exposes company, PIC, funnel, and follow-up sections. |

## Customer 360 vs Banking UAT Scope

| Area | Status | Notes |
| --- | --- | --- |
| Directory search and customer profile shell | `implemented` | Search, profile header, tabs, and summary cards already exist. |
| KYC, relationships, bank accounts, documents, communications, transactions, risk profile, AI insight, customer tags | `implemented` | Supported through `create_or_update_customer360_record` and aggregated by `get_customer_360`. |
| Shareholder validation and watchlist enforcement | `implemented` | Existing validation in credit API. |
| Export profile watermark/password capture | `implemented` | Export request record already supports watermark and password-protected note metadata. |
| Seeded banking customer records for UAT | `implemented` | Separate BNI UAT seed creates customers plus related credit/customer 360 records. |
| Live external bureau / market enrichment | `partial` | Public company and bureau data are modeled, but external adapters still fall back to manual/source-unavailable behavior. |
