# SUMMON OS — Project Source of Truth

**Client:** Bank BNI Indonesia  
**Platform:** Frappe Framework (Python + Vue 3)  
**Purpose:** Proof of Concept — demonstrate compelling user flows to win the client. Backend is minimal (Frappe CRUD + demo data); the priority is polished UI and believable end-to-end flows.  
**Inspired by:** CRMNext/BUSINESSNEXT, Salesforce Financial Services Cloud, modern AI workflow platforms (n8n, Camunda)

---

## What SUMMON OS Is

An **Enterprise AI-Native BFSI CRM & Lending Operating System** — a single platform for a bank's Relationship Managers (RMs), credit analysts, operations staff, and executives to manage the full customer lifecycle from lead capture to loan disbursement and post-disbursement monitoring.

### CRMNext Mental Model (reference baseline)

CRMNext (BUSINESSNEXT) is a BFSI-specific CRM. Key concepts we mirror:

| Concept | What it means |
|---|---|
| **Lead → Opportunity → Facility** | Sales funnel: prospect → qualified deal → active credit facility |
| **RM Workspace** | Single-screen productivity hub for Relationship Managers |
| **Customer 360** | Unified customer profile linking contacts, companies, facilities, documents, communications |
| **LOS** | Loan Origination System — step-by-step workflow from application to disbursement |
| **Credit Memo / Spreading** | Structured financial analysis output presented to credit committee |
| **Covenant Monitoring** | Ongoing surveillance of financial/non-financial conditions post-disbursement |
| **Collections / Aging Buckets** | Managing overdue loans by days-past-due buckets (DPD 1-30, 31-60, 60-90, 90+) |
| **Committee Approval** | Multi-level, quorum-based decision workflow for large credit decisions |

---

## 26 Modules — Route & Implementation Map

> **Rule:** Always use an existing route/page first. Only add new routes if no existing page fits.  
> Implementation types: **Vue** = custom Vue page, **Embedded** = iframe via `EmbeddedAppPage.vue`, **Placeholder** = `SummonModulePlaceholder.vue` (needs real page built)

| # | Module | Route | Vue File | Type |
|---|---|---|---|---|
| 01 | **Dashboard** | `/crm-core/dashboard` | `pages/CRMCoreDashboard.vue` | Vue |
| 02 | **CRM** | `/crm-core/leads`, `/crm-core/deals`, `/crm-core/contacts`, `/crm-core/organizations` | `Leads.vue`, `Deals.vue`, `Contacts.vue`, `Organizations.vue` | Vue |
| 03 | **Customer 360** | `/crm-core/customer-360` · `/crm-core/customer-360/:customer` | `Customer360List.vue` · `Customer360.vue` | Vue |
| 04 | **Lead Management** | `/crm-core/leads/view/:viewType?` · `/crm-core/leads/:leadId` | `Leads.vue` · `Lead.vue` | Vue |
| 05 | **LOS** | `/lending-risk/loan-origination-system` | `pages/EmbeddedAppPage.vue` → `/app/loans` | Embedded |
| 06 | **Workflow Engine** | `/admin-platform/workflow-engine` | `modules/admin/pages/WorkflowEngine.vue` | Vue |
| 07 | **Credit Analysis** | `/crm-core/credit-analysis` · `/crm-core/credit-analysis/:applicationId` | `CreditAnalysisList.vue` · `CreditAnalysis.vue` | Vue |
| 08 | **AI Agent Center** | `/crm-core/ai-desk` | `pages/AIDesk.vue` | Vue |
| 09 | **Document Management** | `/operations/document-management` | `EmbeddedAppPage.vue` → Frappe Drive | Embedded |
| 10 | **Omnichannel** | `/channels-portal/omnichannel-communication` | `pages/OmnichannelCommunication.vue` | Vue |
| 11 | **Collections** | `/lending-risk/collections` *(buat baru)* | *(belum ada — buat `pages/Collections.vue`)* | **Placeholder** |
| 12 | **Portfolio Monitoring** | `/lending-risk/portfolio-monitoring` | `EmbeddedAppPage.vue` → Insights | Embedded |
| 13 | **Reporting & BI** | `/admin-platform/reporting-bi` | `EmbeddedAppPage.vue` → Insights | Embedded |
| 14 | **Administration** | `/admin-platform/dashboard` | `pages/ModuleDashboard.vue` (grup Admin) | Vue |
| 15 | **RBAC** | `/admin-platform/users` · `/admin-platform/roles` · `/admin-platform/role-permissions` | `modules/rbac/pages/UserList.vue`, `RoleList.vue`, `RolePermissionManager.vue` | Vue |
| 16 | **Audit Trail** | `/admin-platform/audit-trail` | `modules/admin/pages/AuditTrail.vue` | Vue |
| 17 | **API & Integration** | `/admin-platform/api-integration-center` | `EmbeddedAppPage.vue` → Frappe Integrations | Embedded |
| 18 | **Task & SLA** | `/crm-core/tasks/view/:viewType?` | `pages/Tasks.vue` | Vue |
| 19 | **Notification Center** | `/operations/notification-center` | `EmbeddedAppPage.vue` → Frappe Notification | Embedded |
| 20 | **Product Config** | `/lending-risk/product-configuration` | `EmbeddedAppPage.vue` → Frappe Item | Embedded |
| 21 | **Rules Engine** | `/admin-platform/rules-engine` | `EmbeddedAppPage.vue` → Assignment Rule | Embedded |
| 22 | **Committee Approval** | `/lending-risk/committee-approval` *(buat baru)* | *(belum ada — buat `pages/CommitteeApproval.vue`)* | **Placeholder** |
| 23 | **Covenant Monitoring** | `/lending-risk/covenant-monitoring` *(buat baru)* | *(belum ada — buat `pages/CovenantMonitoring.vue`)* | **Placeholder** |
| 24 | **Partner & Vendor** | `/operations/partner-vendor-management` | `pages/PartnerVendorManagement.vue` | Vue |
| 25 | **Customer Portal** | `/channels-portal/customer-portal` | `EmbeddedAppPage.vue` → Frappe Helpdesk | Embedded |
| 26 | **Mobile RM** | Gunakan responsive layout di `/crm-core/dashboard` | `CRMCoreDashboard.vue` (mobile-aware) | Vue |

---

## Module 24: Partner & Vendor Management

Module **Partner & Vendor Management** merupakan pusat pengelolaan seluruh partner eksternal dan vendor yang bekerja sama dengan perusahaan, seperti **Appraiser**, **Insurance Provider**, **Legal Counsel**, **Technology Vendor**, dan **Referral Partner**.

### Posisi Module yang Disarankan

**Operations → Partner & Vendor Management**

Karena fokus utamanya adalah:
1. Operational coordination
2. Vendor governance
3. Service tracking
4. SLA monitoring
5. Partner performance management

### Tujuan Utama

Memastikan seluruh vendor dan partner dapat dikelola secara **terstruktur**, **compliant**, dan **measurable** dalam satu platform terintegrasi.

### Fitur Utama

1. Vendor Directory
2. Vendor Onboarding
3. Vendor Profile
4. Contract Management
5. SLA Management per Vendor
6. Service Request Workflow
7. Appraiser Engagement
8. Insurance Provider Management
9. Legal Counsel Engagement
10. Technology Vendor Management
11. Performance Scoring
12. Vendor Performance Review
13. Invoice & Payment Tracking
14. Vendor Portal
15. Compliance Monitoring
16. Vendor Blacklist
17. Referral Partner Management
18. Partner Tier Program
19. Vendor Analytics
20. Vendor Audit Trail

### Fungsi Strategis Module

Sebagai **centralized vendor governance system** untuk membantu:
1. Monitoring SLA vendor
2. Tracking engagement
3. Managing contracts
4. Handling compliance
5. Evaluating performance
6. Controlling operational risk

### Fokus PoC (Proof of Concept)

Untuk tahap PoC, fokus utama adalah:
1. Workflow vendor yang realistis
2. Dashboard operational yang enterprise-grade
3. Interaksi antar team dan vendor
4. User flow yang jelas dan mudah dipahami saat demo

Backend integration production-ready **belum menjadi prioritas**. Yang penting terlihat matang dan profesional:
1. Alur onboarding
2. Request workflow
3. SLA tracking
4. Performance scoring
5. Operational visibility

### Prinsip Desain

Module harus dirancang **modular**, **scalable**, dan **future-ready** agar nantinya dapat berkembang menjadi enterprise vendor governance platform yang terintegrasi dengan:
1. CRM
2. LOS
3. Procurement
4. Compliance system

### Modules yang perlu Vue page baru (Placeholder → Vue)

Tiga modul ini masih mengarah ke `SummonModulePlaceholder.vue` dan perlu halaman nyata:

| Module | Route baru | File baru | Daftarkan di router.js |
|---|---|---|---|
| 11 Collections | `/lending-risk/collections` | `pages/Collections.vue` | Di bawah grup `/lending-risk` |
| 22 Committee Approval | `/lending-risk/committee-approval` | `pages/CommitteeApproval.vue` | Di bawah grup `/lending-risk` |
| 23 Covenant Monitoring | `/lending-risk/covenant-monitoring` | `pages/CovenantMonitoring.vue` | Di bawah grup `/lending-risk` |

---

## PoC Implementation Philosophy

**Goal:** Convince BNI that SUMMON OS is the right platform. Every screen must look production-ready.

### Rules for building features:

1. **UI-first.** Build the page/form/flow first. Frappe backend wires in after UX is validated.
2. **Use existing routes.** Check the table above — if a route exists, extend the existing Vue file. Don't create parallel pages.
3. **Simple CRUD gimmick.** All forms save/read from Frappe doctypes. No complex business logic — a create/list/detail cycle is enough.
4. **Demo data seeded.** Every module must have realistic seeded data visible on first load (`crm/demo/api.py`).
5. **AI features = UI mockup + static response.** AI agent outputs can be hardcoded plausible strings for PoC unless real integration is trivial.
6. **No upstream conflicts.** All additions live in new doctypes, new API files, or new frontend pages. Never modify upstream core files — copy-then-extend.

### Key User Personas

| Persona | Module focus |
|---|---|
| **RM (Relationship Manager)** | Dashboard, CRM (#02), Lead Mgmt (#04), Customer 360 (#03), LOS (#05) |
| **Credit Analyst** | LOS Step 3, Credit Analysis (#07), Customer 360 financials |
| **Operations / Ops** | LOS Doc collection & disbursement, Doc Mgmt (#09), KYC |
| **Credit Committee** | Committee Approval (#22), Credit Memo view |
| **Risk Officer** | Portfolio Monitoring (#12), Covenant (#23), Collections (#11) |
| **Executive / Director** | Dashboard (#01), Reporting (#13) |
| **Admin** | RBAC (#15), Admin (#14), Workflow Engine (#06), Rules Engine (#21) |

---

## LOS — 8-Step Flow (Module 05)

Route: `/lending-risk/loan-origination-system` — saat ini embedded. Target PoC: buat stepper Vue page.

```
[1] Application Intake      → Dynamic form per product, OCR KTP/NPWP, KYC checks
[2] Document Collection     → Upload center, required-doc checklist, expiry tracking
[3] Credit Analysis         → Financial spreading, ratio auto-calc, AI credit memo
[4] Collateral Management   → Collateral registration, appraisal records, insurance
[5] Approval Workflow       → Multi-level approval, committee routing, SLA timer, voting
[6] Legal & Documentation   → Agreement generation, e-signature, covenant setup, CP tracking
[7] Disbursement            → Pre-disbursement checklist, payment instructions, multi-tranche
[8] Post-Disbursement       → Repayment schedule, covenant monitoring, site visit log
```

---

## Frappe Architecture Notes

- **Doctypes** = database tables + API layer. Setiap modul butuh doctypes sendiri.
- **Backend** jalan di Docker (`crm-frappe-1`). Push changes: `docker cp` (lihat CLAUDE.md).
- **Frontend** Vue 3 + Vite (`/frontend`). Hot-reload via `yarn dev`.
- **Router** → `frontend/src/router.js`. Grup route: `/crm-core`, `/lending-risk`, `/operations`, `/admin-platform`, `/channels-portal`.
- **Module registry** → `frontend/src/data/summonModules.js`. Update ini jika tambah modul baru ke sidebar.
- **API files** → `crm/api/`. Satu file per modul (misal `crm/api/collections.py`).
- **Demo data** → `crm/demo/api.py`. Extend untuk seeding modul baru.

---

## Glossary (BFSI terms)

| Term | Meaning |
|---|---|
| OS | Outstanding (sisa saldo pinjaman) |
| NPL | Non-Performing Loan (tunggakan > 90 hari) |
| LTV | Loan-to-Value (pinjaman ÷ nilai agunan) |
| DSCR | Debt Service Coverage Ratio (arus kas ÷ kewajiban hutang) |
| DER | Debt-to-Equity Ratio |
| PTP | Promise to Pay (komitmen debitor di collections) |
| KYC | Know Your Customer (verifikasi identitas) |
| AML/PEP | Anti-Money Laundering / Politically Exposed Person |
| SLIK | Sistem Layanan Informasi Keuangan — biro kredit OJK Indonesia |
| Pefindo | Lembaga pemeringkat kredit swasta Indonesia |
| NPWP | Nomor Pokok Wajib Pajak |
| KTP | Kartu Tanda Penduduk |
| SHM/BPKB | Sertifikat tanah (SHM) / BPKB kendaraan — jenis agunan |
| CP | Condition Precedent — syarat yang harus dipenuhi sebelum pencairan |
| MTD/YTD | Month-to-Date / Year-to-Date |
| RM | Relationship Manager |
| DPD | Days Past Due — hari keterlambatan pembayaran |
