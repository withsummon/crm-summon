# PLAN — MODULE 06 - WORKFLOW ENGINE (NO-CODE BUILDER)

> Source: `06_Workflow` / `List of Feature SUMMON (BNI) - Dev Only - 06_Workflow.csv`

## Ringkasan Modul

Drag-and-drop workflow builder with AI agent nodes, approvals, SLA timers and conditional branching (n8n/Camunda/Zapier-inspired)

Modul ini bertujuan menyediakan **no-code workflow engine** untuk membuat, menjalankan, menguji, merilis, memantau, dan membagikan workflow bisnis. Fokus utama mencakup visual builder, node-node workflow, approval, SLA, integrasi API/webhook, AI agent, versioning, analytics, permission, import/export, marketplace, dan template bisnis siap pakai.

## Sasaran Implementasi

- Admin dapat membuat workflow secara visual tanpa menulis kode.
- Workflow dapat berjalan berdasarkan trigger, kondisi, approval, jadwal, SLA, dan integrasi eksternal.
- Workflow dapat diuji, di-debug, di-versioning, di-rollback, dan diaudit melalui run history.
- Tim dapat mengelola akses, membagikan workflow, serta menggunakan template siap pakai.
- Sistem menyediakan analytics untuk mengukur durasi, bottleneck, failure rate, dan SLA breach.

## Milestone Delivery

### Phase 1 — Core Canvas & Builder Foundation

Membangun fondasi visual workflow builder agar admin bisa membuat flow tanpa kode.

**Scope:** #1 Workflow Builder Canvas, #2 Drag & Drop Nodes, #3 Node Connection (Edges), #4 Trigger Node Types, #5 Approval Node, #6 Decision Node (IF/ELSE)

### Phase 2 — Node Execution & Integrations

Menyediakan node operasional utama untuk trigger, approval, AI, webhook/API, notifikasi, cron, SLA, dan eskalasi.

**Scope:** #7 AI Agent Node, #8 Webhook Node, #9 API Node, #10 Notification Node, #11 Scheduled Jobs (Cron), #12 SLA Timer Node, #13 Escalation Path Builder, #14 Parallel Approval Node

### Phase 3 — Advanced Logic & Reusability

Mendukung branching kompleks, sub-workflow, variable mapping, dan parallel approval agar workflow scalable.

**Scope:** #15 Conditional Branching, #16 Sub-Workflow (Reusable), #17 Variable Mapping

### Phase 4 — Testing, Release, Audit & Governance

Memastikan workflow dapat diuji, dirilis, diaudit, dianalisis, dan dikelola permission-nya.

**Scope:** #18 Workflow Test/Debug, #19 Workflow Versioning, #20 Workflow Templates, #21 Workflow Run History, #22 Workflow Analytics, #23 Permission & Sharing, #24 Workflow Import/Export

### Phase 5 — Marketplace & Pre-built Templates

Menyediakan template siap pakai dan marketplace untuk akselerasi implementasi use case bisnis.

**Scope:** #25 Workflow Marketplace, #26 Pre-built: Credit Approval, #27 Pre-built: Collection Escalation, #28 Pre-built: KYC Verification, #29 Pre-built: Lead Assignment

## Backlog Detail

| No | Feature | User Story | Acceptance Criteria | Notes |
|---:|---|---|---|---|
| 1 | Workflow Builder Canvas | As admin, I want a visual canvas to build workflows, so that I design processes without code. | 1. Infinite canvas with pan/zoom.<br>2. Mini-map for navigation.<br>3. Snap-to-grid.<br>4. Undo/redo (Ctrl+Z/Y).<br>5. Auto-save every 30s. | n8n-style canvas |
| 2 | Drag & Drop Nodes | As admin, I want to drag nodes from a palette, so that I assemble flows fast. | 1. Node palette sidebar.<br>2. Drag node to canvas.<br>3. Search nodes.<br>4. Recent nodes section.<br>5. Categories (Triggers/Actions/AI/Logic). | Palette + search |
| 3 | Node Connection (Edges) | As admin, I want to connect nodes with edges, so that flow direction is clear. | 1. Drag from output port to input port.<br>2. Edge highlights on hover.<br>3. Delete edge via right-click.<br>4. Edge label optional.<br>5. Loop detection warning. | Visual flow |
| 4 | Trigger Node Types | As admin, I want various triggers, so that workflows start on different events. | 1. Triggers: Lead Created, App Submitted, SLA Breach, Schedule (Cron), Webhook, Manual.<br>2. Configure trigger params.<br>3. Test trigger. | 6+ triggers |
| 5 | Approval Node | As admin, I want approval nodes, so that workflows include human gates. | 1. Configure approver (user/role/dynamic).<br>2. SLA timer.<br>3. Approve/Reject/Refer outputs.<br>4. Reminder schedule.<br>5. Delegation support. | Human gate |
| 6 | Decision Node (IF/ELSE) | As admin, I want conditional branching, so that flow adapts to data. | 1. Visual condition builder.<br>2. AND/OR groups.<br>3. Compare fields, formulas, dates.<br>4. Multiple outputs per condition.<br>5. Default else path. | Visual logic |
| 7 | AI Agent Node | As admin, I want to invoke AI agents in flow, so that automation is intelligent. | 1. Pick AI agent from list.<br>2. Map input/output fields.<br>3. Set temperature/model.<br>4. Output captured to vars.<br>5. Fallback path on AI fail. | AI as a step |
| 8 | Webhook Node | As admin, I want to call external webhooks, so that we integrate systems. | 1. HTTP method (GET/POST/PUT/DELETE).<br>2. URL + headers + body.<br>3. Auth (Bearer/Basic/OAuth).<br>4. Response captured.<br>5. Retry on failure. | Outbound webhook |
| 9 | API Node | As admin, I want to call REST APIs, so that we orchestrate. | 1. Pre-built integration cards.<br>2. Auth profile reusable.<br>3. JSON path mapping.<br>4. Error handling branch.<br>5. Rate-limit aware. | Pre-built cards |
| 10 | Notification Node | As admin, I want to send notifications, so that users are informed. | 1. Channels: Email, WA, SMS, In-app.<br>2. Template selector.<br>3. Recipient dynamic.<br>4. Schedule send.<br>5. Delivery log. | Multi-channel |
| 11 | Scheduled Jobs (Cron) | As admin, I want to schedule workflows, so that they run periodically. | 1. Cron expression UI builder.<br>2. Timezone aware.<br>3. Next run shown.<br>4. Pause/resume.<br>5. Run history. | Cron UI |
| 12 | SLA Timer Node | As admin, I want SLA timers in flow, so that we enforce timeliness. | 1. Set duration (mins/hrs/days).<br>2. On breach action (notify/escalate/route).<br>3. Business hours aware.<br>4. Holiday calendar. | Business hours |
| 13 | Escalation Path Builder | As admin, I want to design escalations, so that breaches are auto-handled. | 1. Multi-level escalation chain.<br>2. Different actions per level.<br>3. Auto-resolve on action.<br>4. Notify chain. | Multi-level |
| 14 | Parallel Approval Node | As admin, I want parallel approvers, so that committee speeds up. | 1. N approvers in parallel.<br>2. Set rule (All/Majority/Any).<br>3. Quorum check.<br>4. Aggregated result. | Quorum logic |
| 15 | Conditional Branching | As admin, I want branches based on data, so that workflows adapt. | 1. Multi-way branch (Switch).<br>2. Conditions per branch.<br>3. Default branch.<br>4. Branch labels visible. | Switch logic |
| 16 | Sub-Workflow (Reusable) | As admin, I want reusable sub-flows, so that I avoid duplication. | 1. Save flow as sub-workflow.<br>2. Call sub-flow from any flow.<br>3. Pass input/output.<br>4. Version-aware. | Reusability |
| 17 | Variable Mapping | As admin, I want to map data across nodes, so that flow has context. | 1. Visual data picker (drag from prior step).<br>2. Expression/formula support.<br>3. Type validation.<br>4. Test eval. | Data picker |
| 18 | Workflow Test/Debug | As admin, I want to test workflows, so that I catch bugs before live. | 1. Test mode with sample data.<br>2. Step-by-step execution.<br>3. Inspect inputs/outputs per node.<br>4. Breakpoints.<br>5. Replay last run. | Debug mode |
| 19 | Workflow Versioning | As admin, I want versions, so that we manage releases. | 1. Save as version (Draft/Active/Archived).<br>2. Compare versions diff.<br>3. Promote/rollback.<br>4. Only one Active per workflow. | Version control |
| 20 | Workflow Templates | As admin, I want pre-built templates, so that we start fast. | 1. Templates: Credit Approval, Collection Escalation, KYC, Lead Assignment.<br>2. Clone & customize.<br>3. Marketplace tab.<br>4. Categorized. | 4+ templates |
| 21 | Workflow Run History | As admin, I want execution log, so that we audit and troubleshoot. | 1. List all runs with status.<br>2. Per-run timeline + duration.<br>3. Drill into node logs.<br>4. Re-run option.<br>5. Filter by status/date. | Execution log |
| 22 | Workflow Analytics | As admin, I want analytics, so that I optimize flows. | 1. Avg duration per workflow.<br>2. Bottleneck nodes highlighted.<br>3. Failure rate.<br>4. SLA breach %.<br>5. Export report. | Performance KPIs |
| 23 | Permission & Sharing | As admin, I want to share workflows, so that team collaborates. | 1. Owner + Editors + Viewers.<br>2. Comment-only role.<br>3. Public/Private toggle.<br>4. Activity feed. | RBAC on workflow |
| 24 | Workflow Import/Export | As admin, I want to import/export JSON, so that we migrate flows. | 1. Export as JSON.<br>2. Import validates schema.<br>3. Variable mapping prompt.<br>4. Conflict resolution UI. | JSON portable |
| 25 | Workflow Marketplace | As admin, I want a marketplace, so that I share with community. | 1. Browse public flows.<br>2. Install with one-click.<br>3. Rate/review.<br>4. Author profile. | Community |
| 26 | Pre-built: Credit Approval | As ops, I want a ready credit approval flow, so that we deploy fast. | 1. Receives application.<br>2. Auto credit checks.<br>3. Routes to committee per limit.<br>4. Decision logged.<br>5. Auto-generate agreement. | Template |
| 27 | Pre-built: Collection Escalation | As collection head, I want auto escalation flow, so that overdues are managed. | 1. Trigger on overdue.<br>2. D+1 reminder, D+7 call, D+15 visit, D+30 legal.<br>3. Each step logs activity.<br>4. Stop on payment. | Aging-based |
| 28 | Pre-built: KYC Verification | As compliance, I want KYC flow, so that we automate AML. | 1. Receives KYC data.<br>2. AML + PEP screening.<br>3. e-KTP Dukcapil check.<br>4. Approve/Refer based on score.<br>5. Status logged. | Compliance |
| 29 | Pre-built: Lead Assignment | As ops, I want auto assignment flow, so that leads get RM fast. | 1. Receives new lead.<br>2. Apply assignment rules (region/product/RR).<br>3. Notify assigned RM.<br>4. SLA start. | Round-robin |

## Rencana Eksekusi per Phase

### Phase 1 — Core Canvas & Builder Foundation

#### 1. Workflow Builder Canvas

**User story:** As admin, I want a visual canvas to build workflows, so that I design processes without code.

**Acceptance criteria:**
- Infinite canvas with pan/zoom.
- Mini-map for navigation.
- Snap-to-grid.
- Undo/redo (Ctrl+Z/Y).
- Auto-save every 30s.

**Catatan:** n8n-style canvas

#### 2. Drag & Drop Nodes

**User story:** As admin, I want to drag nodes from a palette, so that I assemble flows fast.

**Acceptance criteria:**
- Node palette sidebar.
- Drag node to canvas.
- Search nodes.
- Recent nodes section.
- Categories (Triggers/Actions/AI/Logic).

**Catatan:** Palette + search

#### 3. Node Connection (Edges)

**User story:** As admin, I want to connect nodes with edges, so that flow direction is clear.

**Acceptance criteria:**
- Drag from output port to input port.
- Edge highlights on hover.
- Delete edge via right-click.
- Edge label optional.
- Loop detection warning.

**Catatan:** Visual flow

#### 4. Trigger Node Types

**User story:** As admin, I want various triggers, so that workflows start on different events.

**Acceptance criteria:**
- Triggers: Lead Created, App Submitted, SLA Breach, Schedule (Cron), Webhook, Manual.
- Configure trigger params.
- Test trigger.

**Catatan:** 6+ triggers

#### 5. Approval Node

**User story:** As admin, I want approval nodes, so that workflows include human gates.

**Acceptance criteria:**
- Configure approver (user/role/dynamic).
- SLA timer.
- Approve/Reject/Refer outputs.
- Reminder schedule.
- Delegation support.

**Catatan:** Human gate

#### 6. Decision Node (IF/ELSE)

**User story:** As admin, I want conditional branching, so that flow adapts to data.

**Acceptance criteria:**
- Visual condition builder.
- AND/OR groups.
- Compare fields, formulas, dates.
- Multiple outputs per condition.
- Default else path.

**Catatan:** Visual logic

### Phase 2 — Node Execution & Integrations

#### 7. AI Agent Node

**User story:** As admin, I want to invoke AI agents in flow, so that automation is intelligent.

**Acceptance criteria:**
- Pick AI agent from list.
- Map input/output fields.
- Set temperature/model.
- Output captured to vars.
- Fallback path on AI fail.

**Catatan:** AI as a step

#### 8. Webhook Node

**User story:** As admin, I want to call external webhooks, so that we integrate systems.

**Acceptance criteria:**
- HTTP method (GET/POST/PUT/DELETE).
- URL + headers + body.
- Auth (Bearer/Basic/OAuth).
- Response captured.
- Retry on failure.

**Catatan:** Outbound webhook

#### 9. API Node

**User story:** As admin, I want to call REST APIs, so that we orchestrate.

**Acceptance criteria:**
- Pre-built integration cards.
- Auth profile reusable.
- JSON path mapping.
- Error handling branch.
- Rate-limit aware.

**Catatan:** Pre-built cards

#### 10. Notification Node

**User story:** As admin, I want to send notifications, so that users are informed.

**Acceptance criteria:**
- Channels: Email, WA, SMS, In-app.
- Template selector.
- Recipient dynamic.
- Schedule send.
- Delivery log.

**Catatan:** Multi-channel

#### 11. Scheduled Jobs (Cron)

**User story:** As admin, I want to schedule workflows, so that they run periodically.

**Acceptance criteria:**
- Cron expression UI builder.
- Timezone aware.
- Next run shown.
- Pause/resume.
- Run history.

**Catatan:** Cron UI

#### 12. SLA Timer Node

**User story:** As admin, I want SLA timers in flow, so that we enforce timeliness.

**Acceptance criteria:**
- Set duration (mins/hrs/days).
- On breach action (notify/escalate/route).
- Business hours aware.
- Holiday calendar.

**Catatan:** Business hours

#### 13. Escalation Path Builder

**User story:** As admin, I want to design escalations, so that breaches are auto-handled.

**Acceptance criteria:**
- Multi-level escalation chain.
- Different actions per level.
- Auto-resolve on action.
- Notify chain.

**Catatan:** Multi-level

#### 14. Parallel Approval Node

**User story:** As admin, I want parallel approvers, so that committee speeds up.

**Acceptance criteria:**
- N approvers in parallel.
- Set rule (All/Majority/Any).
- Quorum check.
- Aggregated result.

**Catatan:** Quorum logic

### Phase 3 — Advanced Logic & Reusability

#### 15. Conditional Branching

**User story:** As admin, I want branches based on data, so that workflows adapt.

**Acceptance criteria:**
- Multi-way branch (Switch).
- Conditions per branch.
- Default branch.
- Branch labels visible.

**Catatan:** Switch logic

#### 16. Sub-Workflow (Reusable)

**User story:** As admin, I want reusable sub-flows, so that I avoid duplication.

**Acceptance criteria:**
- Save flow as sub-workflow.
- Call sub-flow from any flow.
- Pass input/output.
- Version-aware.

**Catatan:** Reusability

#### 17. Variable Mapping

**User story:** As admin, I want to map data across nodes, so that flow has context.

**Acceptance criteria:**
- Visual data picker (drag from prior step).
- Expression/formula support.
- Type validation.
- Test eval.

**Catatan:** Data picker

### Phase 4 — Testing, Release, Audit & Governance

#### 18. Workflow Test/Debug

**User story:** As admin, I want to test workflows, so that I catch bugs before live.

**Acceptance criteria:**
- Test mode with sample data.
- Step-by-step execution.
- Inspect inputs/outputs per node.
- Breakpoints.
- Replay last run.

**Catatan:** Debug mode

#### 19. Workflow Versioning

**User story:** As admin, I want versions, so that we manage releases.

**Acceptance criteria:**
- Save as version (Draft/Active/Archived).
- Compare versions diff.
- Promote/rollback.
- Only one Active per workflow.

**Catatan:** Version control

#### 20. Workflow Templates

**User story:** As admin, I want pre-built templates, so that we start fast.

**Acceptance criteria:**
- Templates: Credit Approval, Collection Escalation, KYC, Lead Assignment.
- Clone & customize.
- Marketplace tab.
- Categorized.

**Catatan:** 4+ templates

#### 21. Workflow Run History

**User story:** As admin, I want execution log, so that we audit and troubleshoot.

**Acceptance criteria:**
- List all runs with status.
- Per-run timeline + duration.
- Drill into node logs.
- Re-run option.
- Filter by status/date.

**Catatan:** Execution log

#### 22. Workflow Analytics

**User story:** As admin, I want analytics, so that I optimize flows.

**Acceptance criteria:**
- Avg duration per workflow.
- Bottleneck nodes highlighted.
- Failure rate.
- SLA breach %.
- Export report.

**Catatan:** Performance KPIs

#### 23. Permission & Sharing

**User story:** As admin, I want to share workflows, so that team collaborates.

**Acceptance criteria:**
- Owner + Editors + Viewers.
- Comment-only role.
- Public/Private toggle.
- Activity feed.

**Catatan:** RBAC on workflow

#### 24. Workflow Import/Export

**User story:** As admin, I want to import/export JSON, so that we migrate flows.

**Acceptance criteria:**
- Export as JSON.
- Import validates schema.
- Variable mapping prompt.
- Conflict resolution UI.

**Catatan:** JSON portable

### Phase 5 — Marketplace & Pre-built Templates

#### 25. Workflow Marketplace

**User story:** As admin, I want a marketplace, so that I share with community.

**Acceptance criteria:**
- Browse public flows.
- Install with one-click.
- Rate/review.
- Author profile.

**Catatan:** Community

#### 26. Pre-built: Credit Approval

**User story:** As ops, I want a ready credit approval flow, so that we deploy fast.

**Acceptance criteria:**
- Receives application.
- Auto credit checks.
- Routes to committee per limit.
- Decision logged.
- Auto-generate agreement.

**Catatan:** Template

#### 27. Pre-built: Collection Escalation

**User story:** As collection head, I want auto escalation flow, so that overdues are managed.

**Acceptance criteria:**
- Trigger on overdue.
- D+1 reminder, D+7 call, D+15 visit, D+30 legal.
- Each step logs activity.
- Stop on payment.

**Catatan:** Aging-based

#### 28. Pre-built: KYC Verification

**User story:** As compliance, I want KYC flow, so that we automate AML.

**Acceptance criteria:**
- Receives KYC data.
- AML + PEP screening.
- e-KTP Dukcapil check.
- Approve/Refer based on score.
- Status logged.

**Catatan:** Compliance

#### 29. Pre-built: Lead Assignment

**User story:** As ops, I want auto assignment flow, so that leads get RM fast.

**Acceptance criteria:**
- Receives new lead.
- Apply assignment rules (region/product/RR).
- Notify assigned RM.
- SLA start.

**Catatan:** Round-robin

## Prioritas MVP

Untuk MVP awal, prioritaskan fitur yang memungkinkan workflow dapat dibuat, diuji, dan dijalankan end-to-end:

- #1 Workflow Builder Canvas
- #2 Drag & Drop Nodes
- #3 Node Connection (Edges)
- #4 Trigger Node Types
- #5 Approval Node
- #6 Decision Node (IF/ELSE)
- #7 AI Agent Node
- #8 Webhook Node
- #10 Notification Node
- #11 Scheduled Jobs (Cron)
- #12 SLA Timer Node
- #17 Variable Mapping
- #18 Workflow Test/Debug
- #19 Workflow Versioning
- #21 Workflow Run History
- #23 Permission & Sharing

## Dependensi Teknis

- **Workflow schema**: definisi JSON untuk node, edge, variable, trigger, approval, SLA, dan version.
- **Execution engine**: runner/asynchronous worker untuk mengeksekusi node, retry, error branch, dan run log.
- **Canvas engine**: visual graph editor dengan pan/zoom, minimap, snap-to-grid, undo/redo, dan auto-save.
- **RBAC**: kontrol akses owner, editor, viewer, comment-only, public/private, dan audit activity.
- **Integration layer**: reusable auth profile, webhook/API caller, notification provider, dan rate-limit handling.
- **Scheduler & SLA service**: cron runner, timezone handling, business hours, holiday calendar, timer breach, dan escalation.
- **Observability**: run history, node log, timeline, error tracking, analytics, export report.

## Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Workflow execution tidak konsisten | Run gagal, data tidak sinkron | Gunakan state machine, idempotency key, retry policy, dan run transaction log. |
| Canvas kompleks dan sulit digunakan | Adopsi admin rendah | Mulai dari MVP canvas, gunakan template, minimap, search node, dan UX testing. |
| Integrasi eksternal sering gagal | Workflow terhenti | Sediakan timeout, retry, fallback branch, credential validation, dan delivery log. |
| Approval/SLA ambigu | Salah routing atau telat eskalasi | Definisikan rule approval, business hours, holiday calendar, dan audit trail sejak awal. |
| Versioning/rollback merusak workflow aktif | Downtime proses bisnis | Batasi hanya satu Active version, gunakan draft/promotion flow, dan compare diff sebelum publish. |

## Definition of Done

- Semua acceptance criteria pada fitur terkait terpenuhi.
- Workflow dapat dibuat, disimpan, diuji, dipublish, dijalankan, dan diaudit.
- Error handling, fallback path, permission, dan run logging tersedia untuk fitur yang memerlukan eksekusi.
- Unit/integration test tersedia untuk workflow schema, execution engine, node runner, scheduler, dan permission.
- Dokumentasi admin tersedia untuk membuat workflow, mengelola node, melakukan test/debug, versioning, dan membaca analytics.

## Output Utama

- No-code workflow builder canvas.
- Library node: trigger, approval, decision, AI agent, webhook, API, notification, cron, SLA, escalation, parallel approval, variable mapping, dan sub-workflow.
- Workflow execution engine dengan test/debug, run history, analytics, dan versioning.
- Governance: permission, sharing, import/export, marketplace, dan pre-built templates.