# CRM data audit, 1 October 2026

Source: authenticated production navigation at `crm.withsummon.com`, read-only MariaDB counts on the CRM site, and route/component inspection. A count is a stored record count, not proof that every record is visible to every role.

| Sidebar area | Observed state | Source / action |
| --- | --- | --- |
| CRM Core: Customer 360, Leads, Deals, Contacts, Organizations, Notes, Tasks | 34 stored customers (32 active after disabling two generated records), 46 leads, 9 deals, 12 contacts, 5 organizations, 4 notes, 22 tasks | Display active customers and the existing persisted lists. |
| CRM Core: Call Logs | Empty; zero `CRM Call Log` rows | Show related stored customer conversations without claiming they are calls. |
| CRM Core: Calendar | Current week has no events; 22 assigned tasks have no due date | Show actual scheduled events only and surface the assigned task list beside an empty calendar. |
| CRM Core: Dashboard, AI Agent Center | Executive dashboard contains invented widgets; Agent Center has saved messages | Route Dashboard to the existing database-backed CRM dashboard. |
| Lending: Loan Origination, Workflow, Credit Analysis | Four LOS cards, four workflows, three credit applications | Workflow and credit records exist; LOS has a fallback example dataset. |
| Lending: Collections, Portfolio, Product Configuration, Committee | Seven collection accounts, 33 facilities, one pending product, two committee meetings | Portfolio reads facilities; historical snapshots are absent. Collections overview mixes persisted sample records with static KPIs. |
| Lending: Covenant Monitoring | Populated example dashboard | Static scenario; no live covenant ledger behind the displayed aggregate. |
| Operations: Document Management, Notification Center, Partner & Vendor | Document view has example rows; 9 notifications for Administrator exist but UI shows zero; vendor dashboard has example data | Fix invalid user lookup and replace Notification Center's random analytics; hide its unsupported action tabs. Other dashboards still need database-backed aggregates. |
| Admin: Workflow, Reporting & BI, Administration, RBAC, Audit Trail, API Center, Rules | Workflow and audit records present; RBAC reads Frappe roles/users; several dashboard metrics are static examples | Keep clear distinction between live records and scenario-only figures. |
| Channels: Omnichannel, Customer Portal, Mobile RM | Eight conversations included two automatically generated examples; portal defaults to customer with no linked facilities; Mobile RM has existing leads/deals/notifications | Archive the two known generated conversations, stop generation on read, and select a staff portal customer with active facilities from the database. |

Verification after deployment: read back exact counts and open the affected routes in an authenticated browser. Do not interpret missing historical snapshots, real calls, payment histories, or external integrations as successful data coverage.

The two known generated conversations `CRM-OMNI-CONV-2026-00005` and `CRM-OMNI-CONV-2026-00006` were archived on the production site on 1 October 2026. Their prior statuses were `Closed` and `Open`; all other conversations were untouched. Their two generated Customer records were disabled, and Customer 360 now filters disabled records from the active directory.

After browser verification, the CRM site's FCRM currency was changed from INR to IDR, consistent with its existing global default, and the live dashboard displayed `Rp`. The two legacy lead-source names were renamed through Frappe to `IGLO Lead Workbook` and `IGLO Referral`; Frappe updated their Lead and Deal links (17 Lead rows and four Deal rows). The single legacy product label was changed to `KPR Subsidi IGLO 2026` without changing its status or identifier.

The nine Administrator notifications shown after fixing the loader match the historic sample notification messages from May 2026. They are persisted database rows, but they do not prove operational delivery. Some Omnichannel messages are also manual test content. No new activity records were invented during this audit.
