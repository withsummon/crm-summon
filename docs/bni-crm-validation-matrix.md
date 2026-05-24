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

## AI Agent Center vs `08_AIAgent`

| Area | Status | Notes |
| --- | --- | --- |
| Rename AI Desk to AI Agent Center | `implemented` | Primary route is `/crm-core/ai-agent-center`; legacy `/crm-core/ai-desk` and `/ai-desk` redirect to the new route. |
| 10 specialized AI agents | `implemented` | Agent registry exposes Credit Analyst, RM, Collection, Document Validator, Financial Analyst, Proposal, Risk, Support, Compliance, and Portfolio agents from the UAT sheet. |
| Kimi K2.6 real LLM path | `implemented` | Server-side Moonshot/Kimi settings call `kimi-k2.6` through the OpenAI-compatible chat-completions endpoint. |
| RAGAnything-backed retrieval | `implemented` | RAG service indexes structured CRM and Customer 360 records, attempts RAGAnything direct content insertion, and keeps fallback chunks for source retrieval. |
| Local embeddings | `implemented` | RAGAnything integration is configured for `BAAI/bge-m3` via `sentence-transformers`. |
| Universal chat, Markdown, tables, attachments, voice | `implemented` | AI Agent Center has full-page chat, Markdown/table rendering, file selection metadata, and browser speech input. |
| Context memory, action logs, audit, feedback, cost | `implemented` | Added first-class AI DocTypes plus runtime tables for sessions, messages, memory, action log, audit log, feedback, cost, performance, prompts, recommendations, automation, and RAG chunks. |
| Action execution governance | `implemented` | Low-risk actions can create tasks/notes/draft records; high-risk actions are queued for confirmation. |
| Customer 360 RAG summary | `implemented` | Customer detail page can generate TL;DR/Standard/Detailed RAG summaries and store the result as `AI Customer Summary` plus `CRM AI Insight`. |
| External channel sending | `partial` | Implemented as draft + queue unless WA/email/SMS adapters are configured. |
| Full parser dependencies | `requires deploy setup` | Python dependencies are declared; production image/server still needs LibreOffice and parser runtime packages installed. |

## Credit Analysis vs `07_CreditAnalysis`

| Area | Status | Notes |
| --- | --- | --- |
| Financial statement input | `implemented` | Credit Analysis workspace exposes 3-5 year PL/BS/CF PSAK spreading rows, adjusted/original values, draft save, and balance validation. |
| AI PDF extraction | `implemented` | `extract_statement_pdf` uses the RAGAnything/Kimi review path and stores per-cell confidence plus low-confidence review evidence. |
| Multi-period comparison | `implemented` | Workspace payload includes five-year comparison, YoY deltas, >20% flags, and common-size values. |
| Ratio analysis | `implemented` | Liquidity, leverage, profitability, and efficiency ratios are calculated with threshold status and benchmark medians. |
| DSCR and cashflow | `implemented` | DSCR formula, -20/base/+20 sensitivity, minimum DSCR alert, and 3-5 year cashflow projection are available. |
| Trend analysis | `implemented` | CAGR, regression projection, and anomaly comments are generated per line item. |
| Industry benchmark and peers | `implemented` | KBLI benchmark, median/quartile payload, three seeded peers, ranking, and comments are available. |
| Risk grading engine | `implemented` | 0-1000 score, A-E grade, weights, score breakdown, override artifact, and audit trail are returned. |
| Scenario and sensitivity | `implemented` | Best/Base/Worst scenario simulation and two-variable heatmap are generated and persisted as artifacts. |
| Collateral coverage | `implemented` | Multiple collateral rows, computed LTV, >80% alert, and re-appraisal trigger are shown in the workspace. |
| AI executive summary, memo, recommendation | `implemented` | AI calls use the existing AI Agent Center/Kimi path with deterministic fallback, source/confidence payloads, memo versions, and decision conditions. |
| Bureau and news adapters | `implemented` | Adapter-ready APIs return demo/manual/provider-not-configured status with score/history, adverse flags, sentiment, and citations. |
| Approval routing and export | `implemented` | Memo submit creates a route/status tracking artifact; export creates watermark/PDF/email queue payload. |
| UAT proof pack | `implemented` | `get_uat_proof_pack` and the in-app UAT Proof tab map each Excel row to route, API, seed, and test evidence. See `docs/credit-analysis-uat-proof.md`. |
