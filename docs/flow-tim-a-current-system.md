# Flow Tim A Berdasarkan Sistem Saat Ini

Dokumen ini menyesuaikan flow dengan kode yang ada di repo saat ini. Fokusnya bukan menambah scope baru, tetapi menjelaskan alur kerja yang paling realistis untuk demo/UAT Tim A berdasarkan route frontend, API backend, dan DocType yang sudah tersedia.

## Ringkasan Kesesuaian Modul

| No | Modul | Status Saat Ini | Kesimpulan Tim A |
| --- | --- | --- | --- |
| 03 | Customer 360 | Halaman list/detail, tab data customer, relationship graph, timeline, AI summary, export, merge, global search. | Cukup untuk Tim A dengan data demo/seed dan konfigurasi AI. |
| 08 | AI Agent Center | Universal chat, streaming response, banyak agent, RAG table, memory/session/message, action confirmation. | Cukup untuk Tim A jika API key Kimi/Moonshot dikonfigurasi. |
| 06 | Workflow Engine | Designer, palette 13 node, save draft, publish, versioning, execution state, SLA deadline, monitor. | Cukup untuk Tim A untuk workflow kredit/lead sederhana; template saat ini belum persis tiga template yang diminta. |
| 02 | CRM & Lead Management | Lead list/kanban/timeline/calendar, capture, duplicate preview, scoring model berbasis rules, routing, reassignment, tagging, export. | Cukup untuk Tim A, tetapi AI/ML scoring saat ini rule-based, bukan model ML statistik. |
| 10 | Omnichannel Communication | Unified inbox, WhatsApp/email/in-app/voice model, reply suggestion via AI, Customer 360 context panel, SLA, routing. | Cukup untuk Tim A dengan sandbox/demo WhatsApp; produksi perlu credential channel. |
| 12 | Portfolio Monitoring | Dashboard, EWS signals, watchlist, exposure industry/geography, stress test, simulation, report. | Cukup untuk Tim A dengan data portfolio yang sudah di-seed. |
| 26 | Mobile RM Workspace | Layout mobile untuk CRM core, mobile detail pages, geolocation control, voice input di AI Agent Center, notifications. | Cukup sebagai mobile responsive web; PWA/push/OCR KTP/business card belum lengkap sebagai flow end-to-end khusus. |
| 07 | Credit Analysis | Workspace, upload/import PDF/XLSX/CSV, spreading, ratios, DSCR, AI memo, recommendation, approval submission. | Cukup untuk Tim A jika AI key aktif dan file statement valid. |
| 15 | RBAC | 9 FCRM roles, permission matrix, branch assignment, field permission, approval matrix, SoD, JIT, audit. | Lebih dari cukup untuk minimum 3 role; perlu seed role dan assignment user. |

## Alur Umum Sistem

1. User login ke Frappe CRM melalui `/crm`.
2. Router frontend mengarahkan user ke dashboard atau modul berdasarkan menu.
3. Permission dicek oleh `frontend/src/router.js` dan helper RBAC backend.
4. Modul frontend memanggil API Frappe menggunakan `frappe-ui` `call` atau `createResource`.
5. Data disimpan di DocType FCRM/CRM, misalnya `CRM Lead`, `CRM Credit Application`, `CRM Workflow`, `CRM AI Session`, `CRM Omnichannel Conversation`, dan lain-lain.
6. Jika fitur memakai AI, backend membaca konfigurasi dari `FCRM Settings`, lalu memanggil Kimi/Moonshot melalui `crm/ai/kimi.py`.
7. Aktivitas penting dicatat sebagai note/task/audit/artifact agar bisa muncul di Customer 360, timeline, audit, atau dashboard.

## 03 Customer 360

Route utama:

- List: `/crm/crm-core/customer-360`
- Detail: `/crm/crm-core/customer-360/:customer`
- Frontend: `frontend/src/pages/Customer360List.vue`, `frontend/src/pages/Customer360.vue`
- API utama: `crm.api.credit.get_customer_360`

DocType/data utama:

- `Customer`
- `CRM KYC Review`
- `CRM Relationship`
- `CRM Credit Facility`
- `CRM Collateral`
- `CRM Bureau Report`
- `CRM Financial Statement`
- `CRM Site Visit`
- `CRM Bank Account`
- `CRM Customer Document`
- `CRM Customer Communication`
- `CRM Transaction History`
- `CRM Risk Profile`
- `CRM AI Insight`
- `CRM Credit Application`
- `CRM Task`
- `FCRM Note`
- `Event`

Flow detail:

1. RM atau Credit Analyst membuka menu `CRM Core > Customer 360`.
2. User mencari customer dari list atau global search.
3. Sistem memanggil `crm.api.credit.get_customer_360_table` untuk list dan `crm.api.credit.get_customer_360` saat detail dibuka.
4. Input minimal yang harus tersedia adalah `Customer.name`.
5. Backend mengambil profil customer, KYC, fasilitas aktif, collateral, bureau, relationship, financial statement, komunikasi, transaksi, risk profile, task, note, dan event.
6. Sistem mengelompokkan relationship menjadi:
   - Shareholders
   - Directors/Commissioners
   - Related Entities
7. Sistem membentuk `relationship_graph` dari relationship, facilities, collaterals, bank accounts, risk profile, dan tags.
8. Sistem membentuk `timeline` dari credit application, bureau report, site visit, task, note, event, communication, transaction, dan risk profile.
9. User dapat menambah atau mengubah data tab melalui form di Customer 360.
10. Frontend mengirim data ke `crm.api.credit.create_or_update_customer360_record`.
11. User dapat memperbarui profil dasar customer via `crm.api.credit.update_customer_profile`.
12. User dapat meminta AI summary.
13. Frontend memanggil `crm.api.ai_agent_center.generate_summary` dengan `scope=Customer` dan `docname=<customer>`.
14. Backend AI Agent Center mengambil konteks RAG/customer, memanggil Kimi jika API key aktif, lalu mengembalikan structured response.
15. Summary disimpan via `crm.api.credit.save_customer_summary`.
16. User dapat export profile via `crm.api.credit.export_customer_profile`.
17. Jika ada duplicate customer, user dapat merge via `crm.api.credit.merge_customers`.

Output yang diharapkan:

- Ringkasan customer.
- Tab personal/profile dan risk.
- Shareholders, directors, related entities.
- Active facilities dan collateral.
- Relationship graph.
- Timeline aktivitas.
- AI customer summary.
- Next action dan data quality/compliance status.

Catatan current system:

- AI summary benar-benar punya jalur LLM melalui `crm.ai.kimi`, tetapi wajib ada API key di `FCRM Settings`.
- External adapter seperti Dukcapil, AML/PEP, SLIK/Pefindo, core banking masih berupa status/configuration check, bukan integrasi produksi otomatis.

## 08 AI Agent Center

Route utama:

- `/crm/crm-core/ai-agent-center`
- Alias lama: `/crm/ai-agent-center`, `/crm/ai-desk`
- Frontend: `frontend/src/pages/AIAgentCenter.vue`
- API utama: `crm.api.ai_agent_center`

Agent yang tersedia di kode:

- `AI Credit Analyst Agent`
- `AI Relationship Manager Agent`
- `AI Collection Officer Agent`
- `AI Document Validator Agent`
- `AI Financial Analyst Agent`
- `AI Proposal Generator Agent`
- `AI Risk Analyst Agent`
- `AI Customer Support Agent`
- `AI Compliance Checker Agent`
- `AI Portfolio Monitor Agent`
- `AI Agent Center` general agent

Flow chat:

1. User membuka `CRM Core > AI Agent Center`.
2. Frontend memanggil `crm.api.ai_agent_center.get_agents`.
3. User memilih agent, misalnya `relationship_manager`, `portfolio_monitor`, `credit_analyst`, atau `proposal_generator`.
4. User mengetik prompt atau memakai voice input browser.
5. Frontend mengirim request streaming ke `/api/method/crm.api.ai_agent_center.query_agent_stream`.
6. Backend membuat atau melanjutkan session melalui `CRM AI Session`.
7. Backend menyimpan pesan user ke `CRM AI Message`.
8. Backend mengambil context dari RAG melalui `crm.ai.rag.query_rag`.
9. Backend membentuk system prompt sesuai agent.
10. Backend memanggil Kimi/Moonshot via `stream_kimi_chat_events`.
11. Response dikirim kembali sebagai stream ke UI.
12. Backend menyimpan jawaban assistant, token, cost estimate, audit log, dan source.
13. Jika jawaban mengandung action, backend membedakan:
    - Low risk: `create_task`, `create_note`, `draft_communication`, `create_recommendation`, `book_follow_up`, `generate_pdf_report`.
    - High risk: `update_record`, `send_communication`, `fire_workflow`, `export_regulatory_draft`.
14. Low-risk action dapat dieksekusi atau dibuat sebagai draft/action log.
15. High-risk action masuk queue dan perlu konfirmasi user.
16. User klik confirm/reject.
17. Frontend memanggil `confirm_action` atau `reject_action`.

Flow RAG dan memory:

1. Admin membuka panel AI Agent Center.
2. Admin klik reindex.
3. Frontend memanggil `crm.api.ai_agent_center.reindex_rag`.
4. Backend mengumpulkan data structured dari DocType seperti Lead, Deal, Customer 360 related doctypes, Credit Application, Credit Facility, Task, Note, dan Artifact.
5. Data dipotong menjadi chunk dan disimpan di `CRM AI RAG Chunk`.
6. Status dokumen disimpan di `CRM AI RAG Document`.
7. Query agent berikutnya memakai chunk ini sebagai sumber.

Output yang diharapkan:

- Jawaban chat universal.
- Structured response per agent.
- Source/citation internal.
- Action draft atau action confirmation.
- Audit log dan cost dashboard.
- Feedback rating user.

Catatan current system:

- Sistem memakai tabel RAG native (`CRM AI RAG Chunk`), bukan vector DB eksternal seperti Qdrant/Pinecone.
- LLM call nyata tersedia jika API key Kimi/Moonshot dikonfigurasi.

## 06 Workflow Engine

Route utama:

- List: `/crm/lending-risk/workflow-engine`
- New: `/crm/lending-risk/workflow-engine/new`
- Detail: `/crm/lending-risk/workflow-engine/:flowId`
- Monitor: `/crm/lending-risk/workflow-engine/:flowId/monitor`

Frontend:

- `frontend/src/modules/workflow-engine/pages/WorkflowList.vue`
- `frontend/src/modules/workflow-engine/pages/WorkflowDesigner.vue`
- `frontend/src/modules/workflow-engine/pages/WorkflowMonitor.vue`

API utama:

- `crm.api.workflow.get_flow`
- `crm.api.workflow.save_flow_draft`
- `crm.api.workflow.publish_flow`
- `crm.api.workflow.validate_flow`
- `crm.api.workflow.clone_flow`
- `crm.api.workflow.rollback_flow`
- `crm.api.workflow_execution.start_execution`
- `crm.api.workflow_execution.submit_action`
- `crm.api.workflow_execution.get_current_state`
- `crm.api.workflow_execution.get_execution_history`
- `crm.api.workflow_execution.get_execution_stats`

Node palette yang tersedia:

- `StartNode`
- `EndNode`
- `DecisionNode`
- `SkipNode`
- `FormNode`
- `DocumentNode`
- `AssignmentNode`
- `ApprovalNode`
- `CommitteeNode`
- `DelegationNode`
- `IntegrationNode`
- `NotificationNode`
- `SLANode`

Template yang tersedia saat ini:

- `Kanvas Kosong`
- `Kualifikasi & Pengisian Data Prospek`
- `Persetujuan Manajer Multilevel`

Flow desain workflow:

1. Admin atau Branch Manager membuka `Lending & Risk > Workflow Engine`.
2. User klik create workflow atau pilih template.
3. Input awal:
   - `title`
   - `description`
   - `product_type`
   - `applicant_persona`
   - `is_pre_approved`
4. User drag node dari palette ke canvas.
5. User konfigurasi node:
   - Form fields untuk `FormNode`.
   - Condition/expression untuk `DecisionNode`.
   - Assignment target untuk `AssignmentNode`.
   - Approver/rule/timeout untuk `ApprovalNode`.
   - Deadline/escalation untuk `SLANode`.
   - Channel untuk `NotificationNode`.
6. Frontend menyimpan canvas sebagai `flow_json`.
7. Sistem memanggil `crm.api.workflow.save_flow_draft`.
8. Backend menyimpan data ke `CRM Workflow` dengan status `Draft`.
9. User klik validate.
10. Sistem memanggil `crm.api.workflow.validate_flow`.
11. Jika valid, user klik publish.
12. Backend membuat `CRM Workflow Version`, mengarsipkan versi lama, dan mengubah status flow menjadi `Published`.

Flow eksekusi workflow:

1. Credit application dibuat atau dipilih.
2. Sistem memanggil `crm.api.workflow_execution.start_execution(application_id)`.
3. Backend mencari published workflow yang cocok dengan application/product/persona.
4. Backend membuat `CRM Workflow Execution`.
5. Backend membuat state aktif di `CRM Workflow Node State`.
6. User membuka application atau monitor.
7. Frontend memanggil `get_current_state`.
8. Sistem mengembalikan:
   - current node
   - node type
   - label
   - form config
   - available actions
   - SLA deadline
9. User mengisi form atau memilih action seperti `submit`, `approve`, `reject`, atau `return`.
10. Frontend memanggil `submit_action`.
11. Backend menjalankan transisi node melalui `crm.utils.workflow_engine`.
12. Backend menulis audit ke `CRM Workflow Audit Log`.
13. Jika node SLA/notification aktif, sistem dapat mencatat deadline, escalation, dan notification event.
14. Monitor menampilkan execution history dan statistik.

Output yang diharapkan:

- Workflow published dan versioned.
- Execution nyata per application.
- Current node dan action available.
- SLA deadline.
- Audit trail.
- Monitor statistik.

Catatan current system:

- Requirement awal menyebut template `Lead Assignment`, `Collection Escalation`, dan `Customer Lifecycle Touch`. Di kode saat ini template yang ada belum persis tiga itu, jadi untuk Tim A bisa pakai template yang tersedia atau rename/menambah template pada phase berikutnya.
- Node `Webhook`, `Delay`, dan `Loop` belum terlihat sebagai node eksplisit di palette saat ini; fungsi serupa bisa didekati lewat `IntegrationNode`, `SLANode`, dan action engine.

## 02 CRM and Lead Management

Route utama:

- `/crm/crm-core/leads/view/:viewType?`
- `/crm/crm-core/leads/:leadId`
- `/crm/crm-core/deals/view/:viewType?`
- `/crm/crm-core/contacts/view/:viewType?`
- `/crm/crm-core/organizations/view/:viewType?`
- `/crm/crm-core/tasks/view/:viewType?`
- `/crm/crm-core/calendar`

API utama:

- `crm.api.lead_management.capture_lead`
- `crm.api.lead_management.preview_duplicates`
- `crm.api.lead_management.score_lead`
- `crm.api.lead_management.route_lead`
- `crm.api.lead_management.reassign_leads`
- `crm.api.lead_management.bulk_tag_leads`
- `crm.api.lead_management.merge_leads`
- `crm.api.lead_management.close_lead`
- `crm.api.lead_management.delete_lead`
- `crm.api.lead_management.get_lead_funnel`
- `crm.api.lead_management.get_kpi_ribbon`
- `crm.api.lead_management.export_leads`

Flow lead capture:

1. RM membuka `CRM Core > Leads`.
2. User memilih list, kanban, calendar, atau timeline view.
3. User input lead baru dari modal/manual form.
4. Input minimal:
   - `lead_name` atau `first_name`
   - `mobile_no` atau `email`
   - `source`
   - optional: `campaign`, `organization`, `npwp`, `territory`, `lead_owner`
5. Frontend memanggil `crm.api.lead_management.capture_lead`.
6. Backend normalisasi phone dan NPWP.
7. Backend membuat atau memastikan `CRM Lead Source` dan `CRM Lead Campaign`.
8. Backend menjalankan duplicate preview.
9. Jika exact duplicate dan `allow_duplicate=false`, lead tidak dibuat dan sistem mengembalikan candidate duplicate.
10. Jika aman, backend membuat `CRM Lead`.
11. Backend menjalankan `score_lead`.
12. Backend menjalankan `route_lead` untuk assignment awal.
13. Backend mencatat intake ke `CRM Lead Intake Log`.
14. User masuk ke detail lead.
15. RM menambah activity, note, task, email, call, atau WhatsApp.

Flow lead scoring:

1. Admin menyiapkan `CRM Lead Scoring Model` aktif.
2. Model berisi rules dengan field, operator, value, dan weight.
3. Saat `score_lead` dipanggil, backend membaca lead dan rule aktif.
4. Jika rule match, weight ditambahkan.
5. Score dibatasi maksimal 100.
6. Sistem mengisi:
   - `lead_score`
   - `lead_score_band`
   - `lead_quality_probability`
   - `lead_quality_confidence`
7. Band ditentukan sebagai:
   - `Hot` jika score >= 75
   - `Warm` jika score >= 40
   - `Cold` jika di bawah 40

Flow pipeline/opportunity:

1. RM membuka view kanban lead/deal.
2. RM memindahkan lead/deal antar status/stage.
3. Sistem menyimpan status dan status change log.
4. Jika lead qualified, RM convert menjadi deal atau credit application sesuai flow bisnis.
5. Opportunity tracking dilakukan di `CRM Deal`.
6. Follow-up dibuat sebagai `CRM Task` atau `Event`.
7. Reminder muncul melalui notification dan task/calendar.

Output yang diharapkan:

- Lead tersimpan, dedupe tercatat, scoring muncul.
- Lead ter-assign ke RM.
- Pipeline dapat dipantau dari list/kanban/timeline.
- Task follow-up dan activity history tersedia.
- Export lead bisa CSV/XLSX/email.

Catatan current system:

- Requirement menyebut AI lead scoring dengan ML model nyata. Implementasi saat ini adalah scoring model berbasis rules/weight, bukan model ML training/prediction.
- Stage sembilan tahap perlu dipastikan melalui master `CRM Lead Status`/`CRM Deal Status`; frontend sudah mendukung status pipeline, tetapi jumlah stage bergantung data master.

## 10 Omnichannel Communication

Route utama:

- `/crm/channels-portal/omnichannel-workspace`
- Frontend: `frontend/src/pages/OmnichannelWorkspace.vue`
- API utama: `crm.api.omnichannel`

DocType utama:

- `CRM Omnichannel Conversation`
- `CRM Omnichannel Message`
- `CRM Omnichannel Channel Account`
- `CRM Omnichannel SLA Policy`
- `CRM Omnichannel Template`
- `CRM Omnichannel Transfer`
- `CRM Customer Communication`
- `Communication`
- `CRM Call Log`

Flow unified inbox:

1. RM atau customer support membuka `Channels & Portal > Omnichannel Workspace`.
2. Frontend memanggil `crm.api.omnichannel.get_conversations`.
3. User filter channel/status/assignee/tag.
4. User memilih conversation.
5. Frontend memanggil `crm.api.omnichannel.get_conversation`.
6. Backend mengambil conversation, message list, participant, SLA payload, dan customer context.
7. Jika conversation punya customer, backend memanggil `crm.api.credit.get_customer_360`.
8. UI menampilkan customer context panel dari Customer 360.

Flow inbound message:

1. Pesan masuk dari WhatsApp/email/in-app/voice atau webhook.
2. Backend menerima melalui `upsert_inbound_message` atau sync hook channel.
3. Backend mencari conversation existing berdasarkan provider/channel/reference/customer.
4. Jika belum ada, backend membuat `CRM Omnichannel Conversation`.
5. Backend membuat `CRM Omnichannel Message`.
6. Backend menerapkan SLA melalui policy.
7. Conversation di-touch agar last message, status, unread, dan SLA ter-update.

Flow outbound message:

1. User membuka conversation.
2. User mengetik content, memilih template, atau attach file.
3. Frontend memanggil `crm.api.omnichannel.send_message`.
4. Backend menentukan provider channel.
5. Untuk WhatsApp, backend memakai `crm.api.whatsapp.create_whatsapp_message` atau `send_whatsapp_template`.
6. Untuk email/in-app, backend membuat communication/message sesuai channel.
7. Sistem mencatat message ke `CRM Omnichannel Message`.

Flow AI reply suggestion:

1. User klik reply suggestion.
2. Frontend memanggil `crm.api.omnichannel.generate_reply_suggestions`.
3. Backend membaca detail conversation.
4. Backend mencoba memanggil `crm.api.ai_agent_center.query_agent`.
5. Jika AI tersedia, suggestion berdasarkan context customer dan percakapan.
6. Jika AI tidak tersedia, fallback menggunakan template suggestion.

Flow routing dan transfer:

1. User klik evaluate routing.
2. Frontend memanggil `crm.api.omnichannel.evaluate_routing`.
3. Backend mengevaluasi routing rule.
4. User bisa bulk assign, tag, close, reopen, atau transfer conversation.

Output yang diharapkan:

- Inbox terpadu.
- Detail chat per conversation.
- Customer context dari Customer 360.
- AI reply suggestions.
- SLA status.
- Routing/assignment.

Catatan current system:

- WhatsApp production membutuhkan app/credential aktif. Untuk Tim A bisa memakai sandbox/demo helper seperti `ensure_demo_whatsapp_customer` dan `start_external_conversation`.
- `OmnichannelCommunication.vue` terlihat sebagai mock/demo page lama; flow yang lebih kuat ada di `OmnichannelWorkspace.vue`.

## 12 Portfolio Monitoring

Route utama:

- `/crm/lending-risk/portfolio-monitoring`
- Frontend: `frontend/src/pages/PortfolioMonitoring.vue`
- API utama: `crm.api.portfolio_monitoring`

API yang dipakai frontend:

- `get_portfolio_dashboard`
- `get_portfolio_overview`
- `get_trend_chart`
- `get_industry_exposure`
- `get_geographic_exposure`
- `get_sbl_monitoring`
- `get_top_exposures`
- `get_concentration_matrix`
- `get_ews_signals`
- `get_covenant_breaches`
- `get_stress_test_scenarios`
- `get_ecl_summary`
- `get_watchlist`
- `run_stress_test`
- `acknowledge_ews_signal`
- `cure_covenant`
- `add_to_watchlist`
- `request_watchlist_removal`
- `run_portfolio_simulation`
- `generate_report`

Flow dashboard monitoring:

1. Risk/Portfolio user membuka `Lending & Risk > Portfolio Monitoring`.
2. Frontend load beberapa resource sekaligus.
3. Input filter opsional:
   - `from_date`
   - `to_date`
4. Backend membaca exposure account/facility dari data CRM/portfolio.
5. Backend menghitung overview, trend, industry exposure, geographic exposure, SBL, top exposure, concentration matrix, ECL, EWS, covenant breach, dan watchlist.
6. Frontend menampilkan KPI, chart, heatmap, table, dan alert list.

Flow EWS:

1. User membuka tab/signals EWS.
2. Sistem menampilkan signal dari `get_ews_signals`.
3. User review borrower, severity, trigger, exposure, dan recommended action.
4. User klik acknowledge.
5. Frontend memanggil `acknowledge_ews_signal(signal_id, action_notes)`.
6. Backend menyimpan status/action notes.
7. Jika perlu, user add borrower ke watchlist.
8. Frontend memanggil `add_to_watchlist`.

Flow stress test/simulation:

1. User memilih scenario atau input shock.
2. Frontend memanggil `run_stress_test` atau `run_portfolio_simulation`.
3. Backend menghitung dampak rate shock/NPL shock atau scenario JSON.
4. Hasil dikembalikan ke UI sebagai impact summary.

Flow report:

1. User memilih template report.
2. User klik generate.
3. Frontend memanggil `generate_report`.
4. Backend menghasilkan package/report summary.

Output yang diharapkan:

- Portfolio overview.
- Industry/geographic exposure heatmap.
- EWS signals.
- Watchlist.
- Covenant breach list.
- Stress test dan simulation result.
- Report package.

Catatan current system:

- AI portfolio alert terhubung secara konseptual melalui AI Agent `portfolio_monitor`; untuk otomatisasi daily scan perlu job/scheduler dan policy yang jelas.
- Akurasi anomaly/payment detection bergantung kelengkapan `CRM Transaction History`, `CRM Credit Facility`, dan data repayment/outstanding.

## 26 Mobile RM Workspace

Route dan komponen yang relevan:

- Mobile layout: `frontend/src/components/Layouts/MobileLayout.vue`
- Mobile sidebar/header: `frontend/src/components/Mobile/*`
- Mobile detail pages:
  - `MobileLead.vue`
  - `MobileDeal.vue`
  - `MobileContact.vue`
  - `MobileOrganization.vue`
  - `MobileNotification.vue`
- Geolocation control: `frontend/src/components/Controls/GeolocationControl.vue`
- Voice input: `frontend/src/pages/AIAgentCenter.vue`

Flow mobile RM yang sesuai kode saat ini:

1. RM membuka CRM dari browser mobile.
2. Router memakai `handleMobileView`, sehingga detail Lead/Deal/Contact/Organization memakai halaman mobile jika lebar layar kurang dari 768px.
3. RM membuka `Leads`, `Deals`, `Contacts`, `Organizations`, `Tasks`, atau `Calendar`.
4. RM membuat lead baru atau follow-up task.
5. Untuk customer visit, RM membuka Customer 360 dan menambah `CRM Site Visit`.
6. Input visit:
   - `visit_date`
   - `next_visit_date`
   - `gps_coordinates`
   - `photo_attachment`
   - `report_pdf`
   - `notes`
7. Field geolocation dapat memakai browser geolocation dan Leaflet map melalui `GeolocationControl`.
8. RM dapat membuka AI Agent Center dan memakai voice input browser untuk mengisi prompt atau visit note draft.
9. Notification mobile dibuka via `MobileNotification.vue`.
10. Notification real-time dikirim oleh `CRM Notification` melalui `frappe.publish_realtime("crm_notification")`.

Output yang diharapkan:

- CRM dapat dipakai dari mobile browser.
- Detail lead/deal/contact/organization tampil mobile.
- RM bisa capture lead, update customer, buat task, dan log visit.
- GPS coordinate dapat disimpan.
- Voice input tersedia untuk AI prompt.
- Notification muncul di mobile notification center.

Catatan current system:

- PWA manifest/service worker tidak terlihat di frontend saat ini.
- Push notification browser/native belum terlihat sebagai implementasi lengkap; yang ada adalah realtime in-app notification.
- OCR KTP/business card belum terlihat sebagai flow khusus mobile. OCR umum ada di Document Management dan mock OCR lead intake, tetapi bukan pipeline KTP/business card end-to-end.

## 07 Credit Analysis

Route utama:

- List: `/crm/crm-core/credit-analysis`
- Detail: `/crm/crm-core/credit-analysis/:applicationId`
- Frontend: `frontend/src/pages/CreditAnalysisList.vue`, `frontend/src/pages/CreditAnalysis.vue`

API utama:

- `crm.api.credit_analysis.get_credit_workspace`
- `crm.api.credit_analysis.save_spreading`
- `crm.api.credit_analysis.import_statement_file`
- `crm.api.credit_analysis.extract_statement_pdf`
- `crm.api.credit_analysis.calculate_ratios`
- `crm.api.credit_analysis.calculate_dscr`
- `crm.api.credit_analysis.run_cashflow_projection`
- `crm.api.credit_analysis.run_scenario`
- `crm.api.credit_analysis.run_sensitivity`
- `crm.api.credit_analysis.refresh_bureau_report`
- `crm.api.credit_analysis.scan_news_sentiment`
- `crm.api.credit_analysis.generate_credit_summary`
- `crm.api.credit_analysis.generate_credit_memo`
- `crm.api.credit_analysis.generate_credit_recommendation`
- `crm.api.credit_analysis.submit_memo_for_approval`
- `crm.api.credit_analysis.export_credit_memo_pdf`

DocType utama:

- `CRM Credit Application`
- `CRM Financial Statement`
- `CRM Credit Spread Line`
- `CRM Credit Analysis Artifact`
- `CRM Bureau Report`
- `CRM Collateral`
- `CRM Risk Profile`

Flow spreading dari file:

1. Credit Analyst membuka `CRM Core > Credit Analysis`.
2. User memilih credit application.
3. Frontend memanggil `get_credit_workspace(application_id)`.
4. User upload financial statement PDF/XLSX/CSV.
5. Frontend memanggil `import_statement_file(application_id, file_url, file_type)`.
6. Backend menentukan file type.
7. Jika CSV/XLSX, backend memakai structured spreadsheet parser.
8. Jika PDF, backend memakai text extraction + Kimi.
9. Backend menghasilkan rows financial spreading.
10. Backend memanggil `save_spreading`.
11. Data disimpan ke `CRM Credit Spread Line`.
12. Backend membuat artifact `statement_import` dan `extraction`.
13. Jika import sukses, backend mencoba auto generate:
    - credit summary
    - credit memo
    - credit recommendation
14. Workspace direfresh.

Flow manual spreading:

1. User edit rows di table spreading.
2. Frontend memanggil `save_spreading(application_id, rows, status)`.
3. Backend menghapus spread line lama untuk application tersebut.
4. Backend insert row baru.
5. Backend menghitung ulang balance checks dan artifact status.

Flow ratio dan DSCR:

1. User klik recalculate ratios.
2. Frontend memanggil `calculate_ratios`.
3. Backend menghitung ratios dan benchmark dari spread rows.
4. User klik calculate DSCR.
5. Frontend memanggil `calculate_dscr`.
6. Backend menghitung DSCR dari rows, requested amount, tenor, dan rate.
7. Artifact DSCR disimpan.

Flow AI credit memo:

1. User klik generate credit memo.
2. Frontend memanggil `generate_credit_memo`.
3. Backend membuat workspace payload.
4. Backend memanggil AI Agent Center melalui `_call_credit_agent`.
5. Jika RAG/LLM tersedia, memo dibuat oleh AI.
6. Jika AI tidak tersedia, sistem memakai fallback lokal.
7. Memo/recommendation disimpan sebagai `CRM Credit Analysis Artifact`.

Flow approval:

1. Setelah memo siap, user klik submit memo.
2. Frontend memanggil `submit_memo_for_approval`.
3. Backend menyiapkan status approval.
4. Jika workflow credit flow aktif, UI juga dapat submit action melalui flow execution.

Output yang diharapkan:

- Extracted spreading rows.
- Balance checks.
- Ratio analysis.
- DSCR.
- Bureau/collateral/risk summary.
- AI credit summary.
- AI credit memo.
- AI recommendation.
- Approval submission.

Catatan current system:

- PDF extraction akurat bergantung kualitas PDF dan Kimi API key.
- Jika API key tidak ada, beberapa AI output akan fallback lokal atau gagal dengan pesan konfigurasi.

## 15 RBAC

Route utama:

- `/crm/admin-platform/rbac`
- `/crm/admin-platform/users`
- `/crm/admin-platform/roles`
- `/crm/admin-platform/role-permissions`
- `/crm/admin-platform/user-permissions`
- `/crm/admin-platform/branches`
- `/crm/admin-platform/approval-matrix`
- `/crm/admin-platform/field-permissions`
- `/crm/admin-platform/delegations`
- `/crm/admin-platform/sod-rules`
- `/crm/admin-platform/jit-requests`
- `/crm/admin-platform/audit-trail`

API utama:

- `crm.api.rbac.seed_default_roles`
- `crm.api.rbac.get_roles`
- `crm.api.rbac.get_user_permissions`
- `crm.api.rbac.get_branches`
- `crm.api.rbac.assign_user_branch`
- `crm.api.rbac.remove_user_branch`
- `crm.api.rbac.get_approval_matrices`
- `crm.api.rbac.get_field_permissions_list`
- `crm.api.rbac.get_field_permissions_map`
- `crm.api.rbac.get_delegations`
- `crm.api.rbac.get_sod_rules`
- `crm.api.rbac.create_jit_request`
- `crm.api.rbac.approve_jit_request`
- `crm.api.rbac.reject_jit_request`
- `crm.api.rbac.get_permission_audit_log`

Role yang tersedia di kode:

- `FCRM Super Admin`
- `FCRM Director`
- `FCRM Credit Analyst`
- `FCRM RM`
- `FCRM Collection Officer`
- `FCRM Legal Officer`
- `FCRM Operations`
- `FCRM Committee Member`
- `FCRM Customer`

Minimum role Tim A:

- RM: gunakan `FCRM RM`.
- Credit Analyst: gunakan `FCRM Credit Analyst`.
- Branch Manager: belum ada nama role eksplisit `FCRM Branch Manager`; paling dekat untuk Tim A adalah `FCRM Director` atau role custom baru lewat `create_fcrm_role`.

Flow setup RBAC:

1. Super Admin membuka `Admin & Platform > RBAC`.
2. Jalankan seed role melalui `crm.api.rbac.seed_default_roles`.
3. Sistem membuat 9 role FCRM jika belum ada.
4. Sistem menerapkan permission matrix default.
5. Admin membuka User List.
6. Admin memilih user.
7. Admin assign role FCRM ke user.
8. Admin membuka Branch Management.
9. Admin membuat/memilih branch.
10. Admin assign user ke branch melalui `assign_user_branch`.
11. Jika `is_primary=true`, assignment menjadi primary branch user.
12. Admin membuka Field Permissions untuk masking atau read-only field tertentu.
13. Admin membuka Approval Matrix untuk batas approval berdasarkan doctype, amount, role, dan branch.
14. Sistem mencatat permission/audit event melalui `FCRM Permission Audit`.

Flow branch isolation:

1. User login.
2. Backend membaca branch user dari `FCRM User Branch`.
3. Helper `get_branch_filter_condition(doctype)` menentukan filter berdasarkan branch field doctype.
4. Query permission dapat membatasi data sesuai branch.
5. User hanya melihat data cabang sendiri jika doctype memiliki branch field dan permission query diterapkan.

Flow field permission:

1. Admin membuat rule di `FCRM Field Permission`.
2. User membuka record.
3. Frontend/backend meminta permission map via `get_field_permissions_map`.
4. Field dapat di-hide, read-only, atau dimasking sesuai role.
5. Masking memakai `mask_field_value`.

Flow approval authority matrix:

1. Admin mengisi `FCRM Approval Matrix`.
2. Saat approval diperlukan, sistem memanggil `get_approval_matrix(doctype, amount, role, branch)`.
3. Backend mengembalikan approver/authority yang cocok dengan amount, role, dan branch.
4. Workflow/approval UI memakai hasil tersebut untuk routing approval.

Output yang diharapkan:

- Role FCRM tersedia.
- User punya role dan branch.
- Menu/route CRM dibatasi untuk user non-CRM.
- CRUD permission diterapkan ke DocType.
- Field permission dan masking tersedia.
- Approval matrix tersedia.
- Audit permission tercatat.

Catatan current system:

- Sistem sudah punya 9 role, jadi minimum 3 role terpenuhi.
- Nama `Branch Manager` perlu diputuskan: mapping ke `FCRM Director` untuk Tim A, atau tambah role custom `FCRM Branch Manager`.

## Flow End-to-End yang Disarankan untuk Demo Tim A

### Flow 1: Lead sampai Customer 360

1. Login sebagai `FCRM RM`.
2. Buka `CRM Core > Leads`.
3. Input lead:
   - nama
   - phone/email
   - source
   - campaign jika ada
   - company/organization jika ada
4. Sistem cek duplicate.
5. Sistem hitung lead score rule-based.
6. Sistem assign lead ke RM.
7. RM buat task follow-up.
8. RM convert/lanjutkan ke customer/application sesuai kebutuhan.
9. Buka `Customer 360`.
10. Tambahkan KYC, relationship, facility, risk profile, dan site visit.
11. Generate AI customer summary.
12. Output: customer profile lengkap, relationship graph, timeline, dan next action.

### Flow 2: Omnichannel sampai AI Reply

1. Login sebagai RM/support.
2. Buka `Channels & Portal > Omnichannel Workspace`.
3. Buat demo WhatsApp conversation atau pilih existing conversation.
4. Sistem menampilkan message list.
5. Sistem mengambil Customer 360 context panel.
6. User klik AI reply suggestion.
7. Sistem memanggil AI Agent Center.
8. User review suggestion.
9. User send message.
10. Output: reply terkirim/tercatat, conversation ter-update, SLA berjalan.

### Flow 3: Credit Analysis sampai Approval

1. Login sebagai `FCRM Credit Analyst`.
2. Buka `CRM Core > Credit Analysis`.
3. Pilih credit application.
4. Upload PDF/XLSX/CSV laporan keuangan.
5. Sistem import spreading.
6. User review low-confidence cells.
7. User hitung ratio.
8. User hitung DSCR.
9. User generate AI credit memo.
10. User generate AI recommendation.
11. User submit memo for approval.
12. Output: spreading, ratio, DSCR, memo, recommendation, approval submission.

### Flow 4: Workflow Execution

1. Login sebagai admin/manager.
2. Buka `Lending & Risk > Workflow Engine`.
3. Buat workflow dari template atau blank.
4. Tambahkan Start, Form, Decision, Approval, SLA, Notification, End.
5. Save draft.
6. Validate.
7. Publish.
8. Pilih credit application.
9. Start execution.
10. User mengisi action sesuai current node.
11. Approver approve/reject/return.
12. Monitor execution history.
13. Output: workflow berjalan nyata dengan audit log.

### Flow 5: Portfolio Monitoring sampai Watchlist

1. Login sebagai Risk/Portfolio user.
2. Buka `Lending & Risk > Portfolio Monitoring`.
3. Review overview, trend, exposure, dan heatmap.
4. Buka EWS signals.
5. Acknowledge signal.
6. Tambahkan borrower ke watchlist jika perlu.
7. Jalankan stress test.
8. Generate report.
9. Jika perlu, buka AI Agent Center dengan `AI Portfolio Monitor Agent`.
10. Output: signal ditangani, watchlist update, stress result, report.

### Flow 6: RBAC Setup Minimal

1. Login sebagai Super Admin.
2. Seed default roles.
3. Assign user A sebagai `FCRM RM`.
4. Assign user B sebagai `FCRM Credit Analyst`.
5. Assign user C sebagai `FCRM Director` atau role custom `FCRM Branch Manager`.
6. Buat branch.
7. Assign user ke branch.
8. Atur approval matrix.
9. Atur field permission untuk field sensitif.
10. Test login per role.
11. Output: akses, data, field, dan approval authority sesuai role/cabang.

## Hal yang Perlu Disiapkan Sebelum UAT Tim A

1. Jalankan seed/demo data untuk customer, lead, portfolio, dan credit application.
2. Isi `FCRM Settings` untuk AI provider Kimi/Moonshot:
   - API key
   - model
   - base URL jika berbeda
   - cost limit
3. Jalankan RAG reindex dari AI Agent Center.
4. Seed RBAC roles dengan `seed_default_roles`.
5. Assign user ke role dan branch.
6. Siapkan sample file financial statement PDF/XLSX/CSV.
7. Siapkan WhatsApp sandbox/demo customer jika channel produksi belum tersedia.
8. Pastikan master status lead/deal sudah sesuai stage pipeline yang ingin didemokan.
9. Jika perlu persis sesuai requirement awal, tambahkan template workflow:
   - Lead Assignment
   - Collection Escalation
   - Customer Lifecycle Touch

## Gap yang Perlu Dinyatakan Secara Jelas

1. AI/LLM nyata tersedia, tetapi bergantung pada konfigurasi API key.
2. Lead scoring saat ini rule-based, bukan ML model statistik.
3. RAG saat ini memakai tabel native, bukan vector DB eksternal.
4. Workflow template belum persis tiga template requirement awal.
5. PWA/service worker/push notification native belum terlihat lengkap.
6. OCR KTP dan business card mobile belum terlihat sebagai flow end-to-end khusus.
7. External banking/AML/SLIK/core banking adapter masih perlu credential/integrasi produksi.

