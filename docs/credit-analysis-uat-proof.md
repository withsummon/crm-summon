# Credit Analysis UAT Proof Pack

Source of truth: `List of Feature SUMMON (BNI) - Dev Only.xlsx`, sheet `07_CreditAnalysis`.

Demo entry points:
- Route: `/crm/crm-core/credit-analysis`
- Detail route: `/crm/crm-core/credit-analysis/<application>`
- Seed: `crm.demo.bni_uat.create_bni_uat_seed`
- Proof API: `crm.api.credit_analysis.get_uat_proof_pack`
- Workspace API: `crm.api.credit_analysis.get_credit_workspace`

## Presenter Flow

1. Run or confirm the BNI UAT seed, then open `Credit Analysis`.
2. Select the seeded BNI credit application.
3. Walk tabs from left to right: spreading, AI extraction, ratios, DSCR, benchmark, risk, scenarios, collateral/news, memo, proof.
4. Use `Refresh Proof` to regenerate deterministic evidence rows for `07_CreditAnalysis` and AI Agent Center.
5. Open `UAT Proof` tab and show every Excel feature row has route, API, seed, and test evidence.

## `07_CreditAnalysis` Evidence Map

| Excel Feature | Product Evidence | API Evidence | Demo Proof |
| --- | --- | --- | --- |
| Financial Statement Input | Financial Spreading tab with 3-5 year PL/BS/CF PSAK rows, editable adjusted values, balance checks | `save_spreading` | Seed creates five-year spreading rows |
| AI Extraction from PDF | AI Extraction Review tab with parser, cell count, low-confidence review table | `extract_statement_pdf` | Demo adapter creates low-confidence cells |
| Multi-Period Comparison | Ratios & Trends tab plus spreading table by year | `get_credit_workspace` | YoY and common-size payload in workspace |
| Ratio Analysis - Liquidity | Current, quick, cash ratios with status and benchmark median | `calculate_ratios` | Deterministic ratio snapshot artifact |
| Ratio Analysis - Leverage | DER, debt-to-equity, debt-to-assets, interest coverage | `calculate_ratios` | Threshold status stored in ratio snapshot |
| Ratio Analysis - Profitability | Gross margin, EBITDA margin, net margin, ROA, ROE | `calculate_ratios` | Benchmark overlay in ratios payload |
| Ratio Analysis - Efficiency | Asset turnover, inventory days, receivable days, payable days, working capital cycle | `calculate_ratios` | Efficiency rows shown in ratio table |
| DSCR Calculation | DSCR & Cashflow tab with -20/base/+20 sensitivity and alert status | `calculate_dscr` | Min DSCR stored as artifact |
| Trend Analysis | Revenue CAGR, projection, anomaly comments | `run_trend_projection` | Trend payload available in workspace |
| Industry Benchmarking | KBLI benchmark panel with median and quartile payload | `get_credit_workspace` | Seeded KBLI benchmark data |
| Risk Grading Engine | Risk Grade tab with 0-1000 score, A-E grade, weights, breakdown | `get_credit_workspace` | Risk grade artifact and audit comments |
| Scenario Simulation | Best/Base/Worst cards with drivers and recalculated DSCR | `run_scenario` | Scenario artifact stored |
| Sensitivity Analysis | Two-variable heatmap | `run_sensitivity` | Export-ready matrix payload |
| Cashflow Projection | 3-5 year period and cumulative cashflow with gap alert | `run_cashflow_projection` | Cashflow projection artifact |
| Collateral Coverage | Collateral & News tab with multiple collateral rows, LTV, re-appraisal trigger | `get_credit_workspace` | Seed creates collateral record |
| AI Executive Summary | Memo tab summary bullets generated through AI Agent Center fallback path | `generate_credit_summary` | Summary artifact with sources/confidence |
| AI Credit Memo Draft | Memo editor, version, PDF export control | `generate_credit_memo` | Memo and memo-version artifacts |
| AI Recommendation | Decision, reasoning, conditions, confidence | `generate_credit_recommendation` | Recommendation artifact |
| Peer Comparison | Benchmark & Peers tab with 3 peers and borrower row | `get_credit_workspace` | Peer comparison payload |
| Notes & Adjustments | Editable adjusted amount column and save draft | `save_spreading` | Original vs adjusted values preserved |
| Credit Bureau Integration | Bureau adapter panel with score/history/adverse status | `refresh_bureau_report` | Demo adapter or provider-not-configured status |
| News & Sentiment Scan | News panel with sentiment score, flags, citations | `scan_news_sentiment` | Seeded source citations |
| Approval Routing from Memo | Submit Memo action with amount/risk route and tracking | `submit_memo_for_approval` | Approval route artifact |
| Memo Export & Print | Export PDF action with watermark and email queue payload | `export_credit_memo_pdf` | Memo export artifact |

## AI Agent Center Proof

AI Agent Center proof is returned from the same proof API with `scope="ai_agent_center"`. The rows cover:
- 10 specialized agents.
- Kimi K2.6 server-side call path.
- RAGAnything retrieval and source guardrails.
- Action confirmation, audit, cost, feedback, and memory records.
- Customer 360 RAG summary.

## Verification

Run:

```bash
../my-frappe-bench/env/bin/python -m unittest crm.tests.test_credit_analysis_uat
../my-frappe-bench/env/bin/python -m unittest crm.tests.test_ai_agent_center crm.tests.test_bni_uat_seed
yarn --cwd frontend build
```
