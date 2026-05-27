<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Audit Trail" />
      </template>
      <template #right-header>
        <div class="flex shrink-0 items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            :label="__('Record Event')"
            @click="showRecordDialog = true"
          >
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
          </Button>
          <Button
            variant="outline"
            size="sm"
            :label="__('Export Evidence')"
            @click="exportEvidence"
          >
            <template #prefix>
              <FeatherIcon name="download" class="h-4 w-4" />
            </template>
          </Button>
          <Button
            variant="solid"
            size="sm"
            :label="__('Refresh')"
            :loading="loading"
            @click="fetchAuditData"
          >
            <template #prefix>
              <FeatherIcon name="refresh-cw" class="h-4 w-4" />
            </template>
          </Button>
          <Button
            variant="outline"
            size="sm"
            :label="__('Open Desk View')"
            @click="openDeskView"
          >
            <template #prefix>
              <FeatherIcon name="external-link" class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="shrink-0 overflow-x-auto border-b border-outline-gray-2 bg-surface-white px-10 py-5">
      <div class="flex min-w-max items-center justify-start gap-10">
        <div class="flex items-center gap-8">
          <button
            v-for="tab in TABS"
            :key="tab.key"
            class="whitespace-nowrap border-b-2 px-1 py-3.5 text-base leading-5 transition-colors"
            :class="
              activeTab === tab.key
                ? 'border-ink-gray-8 font-medium text-ink-gray-9'
                : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'
            "
            @click="activeTab = tab.key"
          >
            {{ __(tab.label) }}
          </button>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <button
            class="flex items-center gap-2 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm text-ink-gray-7"
            :class="liveTail ? 'border-crm-teal text-crm-teal' : ''"
            @click="liveTail = !liveTail"
          >
            <span
              class="h-2 w-2 rounded-full"
              :class="liveTail ? 'bg-crm-teal' : 'bg-ink-gray-3'"
            />
            {{ __('Live Tail') }}
          </button>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1">
      <div class="w-full px-10 py-6">
        <ErrorMessage
          v-if="errorMessage"
          class="mb-4"
          :message="errorMessage"
        />

        <div v-if="loading" class="flex h-48 items-center justify-center">
          <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
        </div>

        <template v-else>
          <template v-if="activeTab === 'activity'">
            <div class="mb-4 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <StatCard
                v-for="card in complianceCards"
                :key="card.label"
                :label="card.label"
                :value="card.value"
                :sub="card.sub"
                :icon="card.icon"
                :warn="card.warn"
              />
            </div>

            <div class="mb-4 rounded-[14px] border border-outline-gray-2 bg-white p-4 shadow-sm">
              <div class="grid gap-3 lg:grid-cols-[minmax(220px,1fr)_repeat(5,minmax(140px,auto))]">
                <div class="relative">
                  <FeatherIcon
                    name="search"
                    class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4"
                  />
                  <input
                    v-model="filters.query"
                    type="text"
                    :placeholder="__('Search user, entity, IP, payload...')"
                    class="h-9 w-full rounded-md border border-outline-gray-2 bg-white pl-9 pr-3 text-sm text-ink-gray-8 outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20"
                  />
                </div>
                <select v-model="filters.category" class="audit-select">
                  <option value="">{{ __('All categories') }}</option>
                  <option v-for="category in categoryOptions" :key="category" :value="category">
                    {{ labelize(category) }}
                  </option>
                </select>
                <select v-model="filters.action" class="audit-select">
                  <option value="">{{ __('All actions') }}</option>
                  <option v-for="action in actionOptions" :key="action" :value="action">
                    {{ labelize(action) }}
                  </option>
                </select>
                <select v-model="filters.actor" class="audit-select">
                  <option value="">{{ __('All actors') }}</option>
                  <option v-for="actor in actorOptions" :key="actor" :value="actor">
                    {{ actor }}
                  </option>
                </select>
                <select v-model="filters.severity" class="audit-select">
                  <option value="">{{ __('All severity') }}</option>
                  <option value="info">{{ __('Info') }}</option>
                  <option value="warning">{{ __('Warning') }}</option>
                  <option value="critical">{{ __('Critical') }}</option>
                </select>
                <select v-model="selectedSavedQuery" class="audit-select" @change="applySavedQuery">
                  <option value="">{{ __('Saved Queries') }}</option>
                  <option v-for="query in savedQueries" :key="query.name" :value="query.name">
                    {{ query.label }}
                  </option>
                </select>
              </div>
            </div>

            <AuditTable :rows="filteredEvents" @open="openDrawer" />
          </template>

          <template v-else-if="activeTab === 'field_changes'">
            <SectionHeader
              title="Field-Level Change History"
              description="Before/after field changes from Frappe Version plus CRM audit diff payloads."
            />
            <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm">
              <EmptyState
                v-if="!fieldChangeRows.length"
                icon="git-compare"
                title="No field changes found"
                description="Version history will appear here once tracked documents are edited."
              />
              <div v-else class="divide-y divide-outline-gray-1">
                <button
                  v-for="row in fieldChangeRows"
                  :key="row.name"
                  class="w-full p-4 text-left hover:bg-surface-gray-1"
                  @click="openDrawer(row)"
                >
                  <div class="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p class="font-medium text-ink-gray-9">
                        {{ row.target_doctype }} · {{ row.target_name }}
                      </p>
                      <p class="mt-1 text-sm text-ink-gray-5">
                        {{ row.actor }} · {{ formatDate(row.timestamp) }}
                      </p>
                    </div>
                    <Badge :label="`${row.change_count} fields`" theme="teal" variant="subtle" />
                  </div>
                  <div class="mt-3 grid gap-2 md:grid-cols-2">
                    <div
                      v-for="change in row.diff_preview"
                      :key="change.field"
                      class="rounded-md border border-outline-gray-1 bg-surface-gray-1 px-3 py-2 text-sm"
                    >
                      <span class="font-medium text-ink-gray-8">{{ change.field }}</span>
                      <div class="mt-1 flex min-w-0 items-center gap-2 text-xs">
                        <span class="truncate text-ink-red-3">{{ change.old || '—' }}</span>
                        <FeatherIcon name="arrow-right" class="h-3 w-3 shrink-0 text-ink-gray-4" />
                        <span class="truncate text-crm-teal">{{ change.new || '—' }}</span>
                      </div>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          </template>

          <template v-else-if="activeTab === 'logins'">
            <SectionHeader
              title="Login & Authentication Log"
              description="Success/failure activity with IP, device, geolocation, and suspicious flags."
            />
            <div class="mb-4 grid gap-4 md:grid-cols-4">
              <StatCard label="Success Today" :value="String(loginStats.success)" icon="log-in" />
              <StatCard label="Failed Today" :value="String(loginStats.failed)" icon="alert-circle" :warn="loginStats.failed > 0" />
              <StatCard label="Unique IPs" :value="String(loginStats.ips)" icon="map-pin" />
              <StatCard label="Suspicious Flags" :value="String(loginStats.flags)" icon="flag" :warn="loginStats.flags > 0" />
            </div>
            <SimpleTable :rows="loginRows" :columns="loginColumns" empty-title="No login audit found" @open="openDrawer" />
          </template>

          <template v-else-if="activeTab === 'approvals'">
            <SectionHeader
              title="Approval Audit"
              description="Approval, rejection, committee vote, and override decisions."
            />
            <SimpleTable :rows="approvalRows" :columns="approvalColumns" empty-title="No approval events found" @open="openDrawer" />
          </template>

          <template v-else-if="activeTab === 'access_exports'">
            <SectionHeader
              title="Access & Export Audit"
              description="Sensitive record views and outbound file exports."
            />
            <SegmentedControl v-model="accessMode" :options="accessModes" />
            <SimpleTable
              :rows="accessMode === 'views' ? viewRows : exportRows"
              :columns="accessMode === 'views' ? viewColumns : exportColumns"
              :empty-title="accessMode === 'views' ? 'No sensitive views found' : 'No export events found'"
              @open="openDrawer"
            />
          </template>

          <template v-else-if="activeTab === 'api_ai'">
            <SectionHeader
              title="API & AI Audit"
              description="Integration calls, endpoint latency, AI prompts, responses, tokens, and model usage."
            />
            <SegmentedControl v-model="apiMode" :options="apiModes" />
            <SimpleTable
              :rows="apiMode === 'api' ? apiRows : aiRows"
              :columns="apiMode === 'api' ? apiColumns : aiColumns"
              :empty-title="apiMode === 'api' ? 'No API calls found' : 'No AI actions found'"
              @open="openDrawer"
            />
          </template>

          <template v-else-if="activeTab === 'alerts'">
            <SectionHeader
              title="Real-Time Alerts"
              description="Suspicious activity rules, triggered alerts, and acknowledgement workflow."
            />
            <div class="grid gap-5 lg:grid-cols-2">
              <RulePanel :rules="alertRules" />
              <SimpleTable :rows="alertRows" :columns="alertColumns" empty-title="No fired alerts found" @open="openDrawer" />
            </div>
          </template>

          <template v-else-if="activeTab === 'reports'">
            <SectionHeader
              title="Audit Reports"
              description="Regulatory report templates with schedules, recipients, and digital signatures."
            />
            <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              <ReportCard
                v-for="report in reportTemplates"
                :key="report.name"
                :report="report"
                @run="openDrawer(report)"
              />
            </div>
          </template>

          <template v-else-if="activeTab === 'compliance'">
            <SectionHeader
              title="Compliance Dashboard"
              description="Compliance health, trends, and drill-down entry points."
            />
            <div class="mb-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
              <StatCard
                v-for="card in complianceCards"
                :key="card.label"
                :label="card.label"
                :value="card.value"
                :sub="card.sub"
                :icon="card.icon"
                :warn="card.warn"
              />
            </div>
            <div class="grid gap-5 lg:grid-cols-2">
              <TrendPanel title="Events by Category" :items="categoryBreakdown" />
              <TrendPanel title="Severity Heatmap" :items="severityBreakdown" />
            </div>
          </template>

          <template v-else-if="activeTab === 'settings'">
            <SectionHeader
              title="Tamper Detection & Retention"
              description="Hash-chain verification, retention rules, immutable storage, and legal hold."
            />
            <div class="grid gap-5 lg:grid-cols-2">
              <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <h3 class="text-base font-medium text-ink-gray-9">{{ __('Tamper Detection') }}</h3>
                    <p class="mt-1 text-sm text-ink-gray-5">
                      {{ __('Verify entry hashes across the selected audit range.') }}
                    </p>
                  </div>
                  <Badge :label="hashStatus.label" :theme="hashStatus.theme" variant="subtle" />
                </div>
                <Button class="mt-4" variant="solid" size="sm" label="Verify Hash Chain" @click="verifyHashChain">
                  <template #prefix><FeatherIcon name="shield-check" class="h-4 w-4" /></template>
                </Button>
                <p class="mt-3 text-sm text-ink-gray-5">
                  {{ __('Last verified') }}: {{ lastVerified || __('Not verified in this session') }}
                </p>
              </div>
              <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
                <h3 class="text-base font-medium text-ink-gray-9">{{ __('Retention Policy') }}</h3>
                <div class="mt-4 space-y-3">
                  <div
                    v-for="policy in retentionPolicies"
                    :key="policy.category"
                    class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2"
                  >
                    <div>
                      <p class="text-sm font-medium text-ink-gray-8">{{ labelize(policy.category) }}</p>
                      <p class="text-xs text-ink-gray-5">{{ policy.storage }}</p>
                    </div>
                    <Badge :label="`${policy.days} days`" theme="gray" variant="subtle" />
                  </div>
                </div>
              </div>
            </div>
          </template>
        </template>
      </div>
    </div>

    <Dialog v-model="showRecordDialog" :options="{ title: __('Record Audit Event') }">
      <template #body-content>
        <div class="space-y-3 text-sm">
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Category') }}</label>
            <select v-model="recordForm.category" class="audit-select mt-1 w-full">
              <option value="">{{ __('Select category') }}</option>
              <option value="login">Login</option>
              <option value="approval">Approval</option>
              <option value="export">Export</option>
              <option value="view">View</option>
              <option value="api">API</option>
              <option value="ai">AI</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Action') }}</label>
            <input v-model="recordForm.action" type="text" :placeholder="__('e.g. override, export, view')" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm text-ink-gray-8 outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Actor') }}</label>
            <input v-model="recordForm.actor" type="text" :placeholder="__('User name or email')" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm text-ink-gray-8 outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20" />
          </div>
          <div class="grid gap-3 md:grid-cols-2">
            <div>
              <label class="text-xs text-ink-gray-5">{{ __('Target Doctype') }}</label>
              <input v-model="recordForm.target_doctype" type="text" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm text-ink-gray-8 outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20" />
            </div>
            <div>
              <label class="text-xs text-ink-gray-5">{{ __('Target Name') }}</label>
              <input v-model="recordForm.target_name" type="text" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm text-ink-gray-8 outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20" />
            </div>
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Severity') }}</label>
            <select v-model="recordForm.severity" class="audit-select mt-1 w-full">
              <option value="">{{ __('Select severity') }}</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Summary') }}</label>
            <textarea v-model="recordForm.summary" rows="3" class="mt-1 w-full rounded-md border border-outline-gray-2 bg-white px-3 py-2 text-sm text-ink-gray-8 outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20" />
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="ghost" :label="__('Cancel')" @click="close" />
        <Button variant="solid" :label="__('Save')" :loading="recordLoading" @click="recordEvent().then(close)" />
      </template>
    </Dialog>

    <Dialog v-model="drawer.open" :options="{ title: drawer.title }">
      <template #body-content>
        <div v-if="drawer.row" class="space-y-4 text-sm">
          <div class="grid gap-3 md:grid-cols-2">
            <DetailItem label="Timestamp" :value="formatDate(drawer.row.timestamp)" />
            <DetailItem label="Actor" :value="drawer.row.actor || '—'" />
            <DetailItem label="Category" :value="labelize(drawer.row.category)" />
            <DetailItem label="Action" :value="labelize(drawer.row.action)" />
            <DetailItem label="Target" :value="targetLabel(drawer.row)" />
            <DetailItem label="IP Address" :value="drawer.row.ip || '—'" />
          </div>
          <div>
            <p class="mb-2 text-xs font-medium uppercase tracking-wider text-ink-gray-4">
              {{ __('Payload') }}
            </p>
            <pre class="max-h-72 overflow-auto rounded-md bg-surface-gray-1 p-3 text-xs text-ink-gray-7">{{ prettyPayload(drawer.row) }}</pre>
          </div>
          <div class="grid gap-3 md:grid-cols-2">
            <DetailItem label="Entry Hash" :value="drawer.row.entry_hash || 'Pending capture layer'" />
            <DetailItem label="Previous Hash" :value="drawer.row.prev_hash || 'Pending capture layer'" />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import {
  Badge,
  Button,
  Dialog,
  ErrorMessage,
  FeatherIcon,
  LoadingIndicator,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { computed, defineComponent, h, onMounted, reactive, ref } from 'vue'

const TABS = [
  { key: 'activity', label: 'Activity' },
  { key: 'field_changes', label: 'Field Changes' },
  { key: 'logins', label: 'Logins' },
  { key: 'approvals', label: 'Approvals' },
  { key: 'access_exports', label: 'Access & Exports' },
  { key: 'api_ai', label: 'API & AI' },
  { key: 'alerts', label: 'Alerts' },
  { key: 'reports', label: 'Reports' },
  { key: 'compliance', label: 'Compliance' },
  { key: 'settings', label: 'Settings' },
]

const viewControls = ref(null)

const activeTab = ref('activity')
const loading = ref(false)
const liveTail = ref(false)
const auditEvents = ref([])
const errorMessage = ref('')
const selectedSavedQuery = ref('')
const accessMode = ref('views')
const apiMode = ref('api')
const lastVerified = ref('')
const drawer = reactive({ open: false, title: __('Audit Event'), row: null })
const filters = reactive({
  query: '',
  category: '',
  action: '',
  actor: '',
  severity: '',
})
const showRecordDialog = ref(false)
const recordLoading = ref(false)
const recordForm = reactive({
  category: '',
  action: '',
  actor: '',
  target_doctype: '',
  target_name: '',
  severity: '',
  summary: '',
})
const retentionPolicies = ref([])
const alertRules = ref([])

const accessModes = [
  { key: 'views', label: 'Views' },
  { key: 'exports', label: 'Exports' },
]
const apiModes = [
  { key: 'api', label: 'API' },
  { key: 'ai', label: 'AI' },
]
const savedQueries = [
  { name: 'failed-logins', label: 'Failed logins', filters: { category: 'login', action: 'fail' } },
  { name: 'overrides', label: 'Override approvals', filters: { category: 'approval', severity: 'warning' } },
  { name: 'exports', label: 'Large exports', filters: { category: 'export' } },
]

async function fetchAuditData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await call('crm.api.audit.get_audit_events', { filters: {}, limit: 300 })
    auditEvents.value = data || []
  } catch (e) {
    errorMessage.value = __('Unable to load audit events: ') + (e.message || '')
    auditEvents.value = []
  }
  loading.value = false
}

const normalizedEvents = computed(() => (
  auditEvents.value.length ? auditEvents.value : demoEvents.value
))

const demoEvents = computed(() => {
  const actor = 'Compliance Officer'
  const base = new Date()
  const daysAgo = (days, hour = 9) => {
    const date = new Date(base)
    date.setDate(date.getDate() - days)
    date.setHours(hour, 30, 0, 0)
    return date.toISOString()
  }
  return [
    {
      name: 'DEMO-APPROVAL-OVERRIDE',
      timestamp: daysAgo(1, 14),
      category: 'approval',
      action: 'override',
      actor,
      target_doctype: 'CRM Credit Application',
      target_name: 'APP-DEMO-001',
      severity: 'warning',
      ip: '10.20.18.44',
      geo: 'ID-JK',
      summary: 'Director override approval with committee comment',
      metadata: { approver_comment: 'Approved with covenant monitoring', override: true },
    },
    {
      name: 'DEMO-BULK-EXPORT',
      timestamp: daysAgo(2, 16),
      category: 'export',
      action: 'export',
      actor,
      target_doctype: 'CRM Lead',
      target_name: 'Lead CSV',
      severity: 'warning',
      ip: '10.20.18.45',
      geo: 'ID-JK',
      summary: 'Large CSV export with watermark SUMMON-AUD-24',
      metadata: { format: 'CSV', row_count: 2500, watermark_id: 'SUMMON-AUD-24' },
    },
    {
      name: 'DEMO-PII-VIEW',
      timestamp: daysAgo(3, 11),
      category: 'view',
      action: 'view',
      actor,
      target_doctype: 'Customer',
      target_name: 'BNI Corporate Customer',
      severity: 'info',
      ip: '10.20.18.41',
      geo: 'ID-JK',
      summary: 'PII record viewed for KYC review',
      metadata: { purpose: 'KYC review', sensitive_fields: ['tax_id', 'address', 'financials'] },
    },
    {
      name: 'DEMO-AI-CALL',
      timestamp: daysAgo(4, 13),
      category: 'ai',
      action: 'invoke',
      actor,
      target_doctype: 'CRM Credit Application',
      target_name: 'APP-DEMO-001',
      severity: 'info',
      ip: '10.20.18.42',
      geo: 'ID-JK',
      summary: 'AI risk insight generated using 2.4k tokens',
      metadata: { model: 'gpt-4.1', prompt_tokens: 1400, completion_tokens: 1000, cost: 0.048 },
    },
    {
      name: 'DEMO-FAILED-LOGIN',
      timestamp: daysAgo(0, 8),
      category: 'login',
      action: 'fail',
      actor: 'unknown@example.com',
      target_doctype: 'User',
      target_name: 'unknown@example.com',
      severity: 'critical',
      ip: '103.55.12.8',
      geo: 'ID-JK',
      summary: '6 failed login attempts in 10 minutes',
      metadata: { attempts: 6, window: '10m', suspicious: true },
    },
  ]
})

const filteredEvents = computed(() => {
  let rows = normalizedEvents.value
  if (filters.category) rows = rows.filter((row) => row.category === filters.category)
  if (filters.action) rows = rows.filter((row) => row.action === filters.action)
  if (filters.actor) rows = rows.filter((row) => row.actor === filters.actor)
  if (filters.severity) rows = rows.filter((row) => row.severity === filters.severity)
  if (filters.query) {
    const query = filters.query.toLowerCase()
    rows = rows.filter((row) =>
      [
        row.summary,
        row.actor,
        row.target_doctype,
        row.target_name,
        row.ip,
        row.geo,
        row.action,
        row.category,
        JSON.stringify(row.metadata || {}),
      ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query)),
    )
  }
  return rows
})

const categoryOptions = computed(() => unique(normalizedEvents.value.map((row) => row.category)))
const actionOptions = computed(() => unique(normalizedEvents.value.map((row) => row.action)))
const actorOptions = computed(() => unique(normalizedEvents.value.map((row) => row.actor)))
const fieldChangeRows = computed(() =>
  normalizedEvents.value
    .filter((row) => row.category === 'field_change' || row.diff_preview?.length)
    .map((row) => ({
      ...row,
      change_count: row.diff_preview?.length || Object.keys(row.diff || {}).length || 1,
      diff_preview: row.diff_preview?.length
        ? row.diff_preview
        : [{ field: 'data', old: 'Previous value', new: 'Updated value' }],
    })),
)
const loginRows = computed(() => normalizedEvents.value.filter((row) => row.category === 'login'))
const approvalRows = computed(() => normalizedEvents.value.filter((row) => row.category === 'approval'))
const viewRows = computed(() => normalizedEvents.value.filter((row) => row.category === 'view'))
const exportRows = computed(() => normalizedEvents.value.filter((row) => row.category === 'export'))
const apiRows = computed(() => normalizedEvents.value.filter((row) => row.category === 'api'))
const aiRows = computed(() => normalizedEvents.value.filter((row) => row.category === 'ai'))
const alertRows = computed(() =>
  normalizedEvents.value
    .filter((row) => row.severity && row.severity !== 'info')
    .map((row) => ({
      ...row,
      rule: row.rule || labelize(row.category || row.action || 'Audit alert'),
      status: row.status || 'Open',
    })),
)

const loginStats = computed(() => ({
  success: loginRows.value.filter((row) => row.action === 'success').length,
  failed: loginRows.value.filter((row) => row.action === 'fail').length,
  ips: unique(loginRows.value.map((row) => row.ip)).length,
  flags: loginRows.value.filter((row) => row.severity !== 'info').length,
}))
const complianceCards = computed(() => [
  { label: 'Audit Volume', value: String(normalizedEvents.value.length), sub: 'Loaded events', icon: 'activity' },
  { label: 'Overrides', value: String(approvalRows.value.filter((row) => row.action === 'override').length), sub: '30 days', icon: 'shield', warn: approvalRows.value.some((row) => row.action === 'override') },
  { label: 'AML Alerts Open', value: String(alertRows.value.filter((row) => row.status !== 'Acknowledged').length), sub: 'Pending ack', icon: 'flag', warn: alertRows.value.some((row) => row.status !== 'Acknowledged') },
  { label: 'Failed Logins', value: String(loginStats.value.failed), sub: 'Current sample', icon: 'log-in', warn: loginStats.value.failed > 0 },
])
const categoryBreakdown = computed(() => countBy(normalizedEvents.value, 'category'))
const severityBreakdown = computed(() => countBy(normalizedEvents.value, 'severity'))

const loginColumns = [
  { key: 'timestamp', label: 'Timestamp', format: formatDate },
  { key: 'actor', label: 'User' },
  { key: 'action', label: 'Result', format: labelize, badge: true },
  { key: 'ip', label: 'IP' },
  { key: 'geo', label: 'Geo' },
  { key: 'severity', label: 'Flag', badge: true },
]
const approvalColumns = [
  { key: 'timestamp', label: 'Timestamp', format: formatDate },
  { key: 'actor', label: 'Approver' },
  { key: 'summary', label: 'Decision' },
  { key: 'target_name', label: 'Reference' },
  { key: 'severity', label: 'Severity', badge: true },
]
const viewColumns = [
  { key: 'timestamp', label: 'Timestamp', format: formatDate },
  { key: 'actor', label: 'User' },
  { key: 'target_doctype', label: 'Entity' },
  { key: 'target_name', label: 'Record' },
  { key: 'summary', label: 'Purpose' },
]
const exportColumns = [
  { key: 'timestamp', label: 'Timestamp', format: formatDate },
  { key: 'actor', label: 'User' },
  { key: 'target_doctype', label: 'Data' },
  { key: 'summary', label: 'Export' },
  { key: 'severity', label: 'Alert', badge: true },
]
const apiColumns = [
  { key: 'timestamp', label: 'Timestamp', format: formatDate },
  { key: 'action', label: 'Method', badge: true },
  { key: 'target_name', label: 'Endpoint' },
  { key: 'summary', label: 'Status' },
  { key: 'ip', label: 'IP' },
]
const aiColumns = [
  { key: 'timestamp', label: 'Timestamp', format: formatDate },
  { key: 'actor', label: 'User' },
  { key: 'summary', label: 'Action' },
  { key: 'target_name', label: 'Reference' },
  { key: 'severity', label: 'Severity', badge: true },
]
const alertColumns = [
  { key: 'timestamp', label: 'Fired At', format: formatDate },
  { key: 'rule', label: 'Rule' },
  { key: 'severity', label: 'Severity', badge: true },
  { key: 'status', label: 'Status', badge: true },
]
const reportTemplates = [
  { name: 'User Access', schedule: 'Weekly', recipients: 'compliance@summon.local', format: 'PDF', signed: true, last_run_at: '2026-05-20' },
  { name: 'Override Activity', schedule: 'Monthly', recipients: 'risk@summon.local', format: 'PDF, Excel', signed: true, last_run_at: '2026-05-01' },
  { name: 'AML Activity', schedule: 'Weekly', recipients: 'aml@summon.local', format: 'Excel', signed: true, last_run_at: '2026-05-17' },
  { name: 'KYC Overdue', schedule: 'Daily', recipients: 'ops@summon.local', format: 'PDF', signed: false, last_run_at: '2026-05-24' },
  { name: 'Failed Logins', schedule: 'Daily', recipients: 'security@summon.local', format: 'Excel', signed: true, last_run_at: '2026-05-24' },
]
const hashStatus = computed(() => ({
  label: normalizedEvents.value.some((row) => row.entry_hash) ? 'Verified' : 'Not computed',
  theme: normalizedEvents.value.some((row) => row.entry_hash) ? 'green' : 'orange',
}))

function applySavedQuery() {
  const query = savedQueries.find((item) => item.name === selectedSavedQuery.value)
  if (!query) return
  Object.assign(filters, { query: '', category: '', action: '', actor: '', severity: '' }, query.filters)
}

function openDrawer(row) {
  drawer.row = row
  drawer.title = row.summary || row.name || __('Audit Event')
  drawer.open = true
}

function openDeskView() {
  window.location.href = '/app/activity-log'
}

async function exportEvidence() {
  loading.value = true
  try {
    const result = await call('crm.api.audit.export_evidence', { format: 'CSV' })
    if (result.file_url) {
      window.location.href = result.file_url
    }
    toast.success(__(`Evidence export ready: ${result.row_count} rows`))
  } catch (e) {
    toast.error(__('Export failed: ') + (e.message || ''))
  }
  loading.value = false
}

async function verifyHashChain() {
  loading.value = true
  try {
    const result = await call('crm.api.audit.verify_hash_chain', { events: normalizedEvents.value })
    lastVerified.value = formatDate(new Date().toISOString())
    if (result.valid) {
      toast.success(__(result.message))
    } else {
      toast.error(__(`Hash chain broken at event ${result.broken_at}: ${result.message}`))
    }
  } catch (e) {
    toast.error(__('Verification failed: ') + (e.message || ''))
  }
  loading.value = false
}

function prettyPayload(row) {
  return JSON.stringify(row.metadata || row, null, 2)
}

function targetLabel(row) {
  return [row?.target_doctype, row?.target_name].filter(Boolean).join(' · ') || '—'
}

function stripHtml(value) {
  if (!value) return ''
  return String(value).replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort()
}

function countBy(rows, key) {
  const counts = rows.reduce((acc, row) => {
    const value = row[key] || 'unknown'
    acc[value] = (acc[value] || 0) + 1
    return acc
  }, {})
  return Object.entries(counts)
    .map(([label, value]) => ({ label: labelize(label), value }))
    .sort((a, b) => b.value - a.value)
}

function labelize(value) {
  if (!value) return '—'
  return String(value)
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function severityTheme(value) {
  if (value === 'critical' || value === 'fail') return 'red'
  if (value === 'warning' || value === 'override') return 'orange'
  if (value === 'success' || value === 'Acknowledged') return 'green'
  if (value === 'info') return 'blue'
  return 'gray'
}

const DetailItem = defineComponent({
  props: { label: String, value: [String, Number] },
  setup(props) {
    return () =>
      h('div', { class: 'rounded-md border border-outline-gray-1 bg-surface-gray-1 px-3 py-2' }, [
        h('p', { class: 'text-xs font-medium uppercase tracking-wider text-ink-gray-4' }, props.label),
        h('p', { class: 'mt-1 break-words text-sm text-ink-gray-8' }, props.value || '—'),
      ])
  },
})

const SectionHeader = defineComponent({
  props: { title: String, description: String },
  setup(props) {
    return () =>
      h('div', { class: 'mb-4 flex flex-wrap items-end justify-between gap-3' }, [
        h('div', [
          h('h2', { class: 'text-xl font-semibold text-ink-gray-9' }, __(props.title)),
          h('p', { class: 'mt-1 text-sm text-ink-gray-5' }, __(props.description)),
        ]),
      ])
  },
})

const StatCard = defineComponent({
  props: { label: String, value: String, sub: String, icon: String, warn: Boolean },
  setup(props) {
    return () =>
      h('div', { class: 'rounded-[14px] border border-outline-gray-2 bg-white p-4 shadow-sm' }, [
        h('div', { class: 'flex items-center justify-between gap-3' }, [
          h('p', { class: 'text-sm text-ink-gray-5' }, __(props.label)),
          h(FeatherIcon, {
            name: props.icon || 'activity',
            class: props.warn ? 'h-4 w-4 text-crm-warning' : 'h-4 w-4 text-crm-teal',
          }),
        ]),
        h('p', { class: 'mt-2 text-2xl font-semibold text-ink-gray-9' }, props.value),
        props.sub ? h('p', { class: 'mt-1 text-xs text-ink-gray-4' }, __(props.sub)) : null,
      ])
  },
})

const EmptyState = defineComponent({
  props: { icon: String, title: String, description: String },
  setup(props) {
    return () =>
      h('div', { class: 'flex flex-col items-center justify-center px-6 py-16 text-center' }, [
        h(FeatherIcon, { name: props.icon || 'inbox', class: 'mb-3 h-8 w-8 text-ink-gray-3' }),
        h('p', { class: 'text-base font-medium text-ink-gray-8' }, __(props.title)),
        h('p', { class: 'mt-1 max-w-md text-sm text-ink-gray-5' }, __(props.description)),
      ])
  },
})

const AuditTable = defineComponent({
  props: { rows: Array },
  emits: ['open'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'overflow-hidden rounded-[14px] border border-outline-gray-2 bg-white shadow-sm' }, [
        props.rows?.length
          ? h('div', { class: 'overflow-x-auto' }, [
              h('table', { class: 'w-full min-w-[980px] text-sm' }, [
                h('thead', { class: 'border-b border-outline-gray-2 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5' }, [
                  h('tr', [
                    h('th', { class: 'px-4 py-2.5 font-medium' }, __('Timestamp')),
                    h('th', { class: 'px-4 py-2.5 font-medium' }, __('Category')),
                    h('th', { class: 'px-4 py-2.5 font-medium' }, __('Action')),
                    h('th', { class: 'px-4 py-2.5 font-medium' }, __('Actor')),
                    h('th', { class: 'px-4 py-2.5 font-medium' }, __('Target')),
                    h('th', { class: 'px-4 py-2.5 font-medium' }, __('Severity')),
                    h('th', { class: 'px-4 py-2.5 font-medium' }, __('IP / Geo')),
                  ]),
                ]),
                h('tbody', props.rows.map((row) =>
                  h('tr', {
                    key: row.name,
                    class: 'cursor-pointer border-b border-outline-gray-1 last:border-b-0 hover:bg-surface-gray-1',
                    onClick: () => emit('open', row),
                  }, [
                    h('td', { class: 'whitespace-nowrap px-4 py-3 text-ink-gray-6' }, formatDate(row.timestamp)),
                    h('td', { class: 'px-4 py-3' }, h(Badge, { label: labelize(row.category), theme: 'teal', variant: 'subtle' })),
                    h('td', { class: 'px-4 py-3 text-ink-gray-8' }, labelize(row.action)),
                    h('td', { class: 'px-4 py-3 text-ink-gray-8' }, row.actor || '—'),
                    h('td', { class: 'px-4 py-3' }, [
                      h('div', { class: 'font-medium text-ink-gray-9' }, row.target_doctype || '—'),
                      h('div', { class: 'text-xs text-ink-gray-5' }, row.target_name || row.summary || '—'),
                    ]),
                    h('td', { class: 'px-4 py-3' }, h(Badge, { label: labelize(row.severity), theme: severityTheme(row.severity), variant: 'subtle' })),
                    h('td', { class: 'px-4 py-3 text-ink-gray-6' }, [row.ip, row.geo].filter(Boolean).join(' · ') || '—'),
                  ]),
                )),
              ]),
            ])
          : h(EmptyState, { icon: 'file-search', title: 'No audit activity found', description: 'Try changing the search or filter criteria.' }),
      ])
  },
})

const SimpleTable = defineComponent({
  props: { rows: Array, columns: Array, emptyTitle: String },
  emits: ['open'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'overflow-hidden rounded-[14px] border border-outline-gray-2 bg-white shadow-sm' }, [
        props.rows?.length
          ? h('div', { class: 'overflow-x-auto' }, [
              h('table', { class: 'w-full min-w-[760px] text-sm' }, [
                h('thead', { class: 'border-b border-outline-gray-2 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5' }, [
                  h('tr', props.columns.map((column) => h('th', { class: 'px-4 py-2.5 font-medium', key: column.key }, __(column.label)))),
                ]),
                h('tbody', props.rows.map((row) =>
                  h('tr', {
                    key: row.name,
                    class: 'cursor-pointer border-b border-outline-gray-1 last:border-b-0 hover:bg-surface-gray-1',
                    onClick: () => emit('open', row),
                  }, props.columns.map((column) => {
                    const value = column.format ? column.format(row[column.key]) : row[column.key]
                    return h('td', { class: 'px-4 py-3 text-ink-gray-8', key: column.key }, column.badge
                      ? h(Badge, { label: labelize(value), theme: severityTheme(row[column.key]), variant: 'subtle' })
                      : value || '—')
                  })),
                )),
              ]),
            ])
          : h(EmptyState, { icon: 'inbox', title: props.emptyTitle, description: 'The capture layer will populate this section as events are recorded.' }),
      ])
  },
})

const SegmentedControl = defineComponent({
  props: { modelValue: String, options: Array },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'mb-4 inline-flex rounded-md border border-outline-gray-2 bg-white p-1' },
        props.options.map((option) =>
          h('button', {
            key: option.key,
            class: [
              'rounded px-3 py-1.5 text-sm transition-colors',
              props.modelValue === option.key ? 'bg-crm-teal text-white' : 'text-ink-gray-6 hover:bg-surface-gray-1',
            ],
            onClick: () => emit('update:modelValue', option.key),
          }, __(option.label)),
        ),
      )
  },
})

const RulePanel = defineComponent({
  props: { rules: Array },
  setup(props) {
    return () =>
      h('div', { class: 'rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm' }, [
        h('h3', { class: 'text-base font-medium text-ink-gray-9' }, __('Active Rules')),
        h('div', { class: 'mt-4 space-y-3' }, props.rules.map((rule) =>
          h('div', { key: rule.name, class: 'rounded-md border border-outline-gray-1 p-3' }, [
            h('div', { class: 'flex items-start justify-between gap-3' }, [
              h('div', [
                h('p', { class: 'font-medium text-ink-gray-8' }, rule.name),
                h('p', { class: 'mt-1 text-sm text-ink-gray-5' }, rule.condition),
                h('p', { class: 'mt-1 text-xs text-ink-gray-4' }, rule.channels),
              ]),
              h(Badge, { label: rule.active ? __('Active') : __('Paused'), theme: rule.active ? 'green' : 'gray', variant: 'subtle' }),
            ]),
          ]),
        )),
      ])
  },
})

const ReportCard = defineComponent({
  props: { report: Object },
  emits: ['run'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm' }, [
        h('div', { class: 'flex items-start justify-between gap-3' }, [
          h('div', [
            h('h3', { class: 'font-medium text-ink-gray-9' }, props.report.name),
            h('p', { class: 'mt-1 text-sm text-ink-gray-5' }, `${props.report.schedule} · ${props.report.format}`),
          ]),
          h(Badge, { label: props.report.signed ? __('Signed') : __('Unsigned'), theme: props.report.signed ? 'green' : 'gray', variant: 'subtle' }),
        ]),
        h('p', { class: 'mt-4 text-sm text-ink-gray-5' }, props.report.recipients),
        h('p', { class: 'mt-1 text-xs text-ink-gray-4' }, `${__('Last run')}: ${props.report.last_run_at}`),
        h(Button, { class: 'mt-4', size: 'sm', variant: 'outline', label: __('Run Now'), onClick: () => emit('run', props.report) }),
      ])
  },
})

const TrendPanel = defineComponent({
  props: { title: String, items: Array },
  setup(props) {
    return () =>
      h('div', { class: 'rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm' }, [
        h('h3', { class: 'text-base font-medium text-ink-gray-9' }, __(props.title)),
        h('div', { class: 'mt-4 space-y-3' }, props.items.map((item) =>
          h('div', { key: item.label }, [
            h('div', { class: 'mb-1 flex justify-between text-sm' }, [
              h('span', { class: 'text-ink-gray-7' }, item.label),
              h('span', { class: 'font-medium text-ink-gray-9' }, String(item.value)),
            ]),
            h('div', { class: 'h-2 overflow-hidden rounded-full bg-surface-gray-2' }, [
              h('div', {
                class: 'h-full rounded-full bg-crm-teal',
                style: { width: `${Math.max(8, Math.min(100, item.value * 14))}%` },
              }),
            ]),
          ]),
        )),
      ])
  },
})

async function fetchAuditContext() {
  try {
    const ctx = await call('crm.api.audit.get_audit_context')
    retentionPolicies.value = ctx?.retention_policies || []
    alertRules.value = ctx?.alert_rules || []
  } catch (e) {
    // silently fail so the page still loads
  }
}

async function recordEvent() {
  recordLoading.value = true
  try {
    await call('crm.api.audit.create_audit_entry', {
      category: recordForm.category,
      action: recordForm.action,
      actor: recordForm.actor,
      target_doctype: recordForm.target_doctype,
      target_name: recordForm.target_name,
      severity: recordForm.severity,
      summary: recordForm.summary,
    })
    toast.success(__('Audit event recorded'))
    Object.assign(recordForm, { category: '', action: '', actor: '', target_doctype: '', target_name: '', severity: '', summary: '' })
    fetchAuditData()
  } catch (e) {
    toast.error(__('Failed to record event: ') + (e.message || ''))
  }
  recordLoading.value = false
}

onMounted(async () => {
  await fetchAuditData()
  await fetchAuditContext()
  if (auditEvents.value.length < 5) {
    try {
      await call('crm.api.audit.seed_audit_sample_data')
      await fetchAuditData()
    } catch (e) {
      // ignore seed errors
    }
  }
})
usePageMeta(() => ({ title: __('Audit Trail') }))
</script>

<style scoped>
.audit-select {
  height: 36px;
  border-radius: 6px;
  border: 1px solid #d1d8dd;
  background: white;
  padding: 0 12px;
  font-size: 14px;
  color: #1f272e;
  outline: none;
}

.audit-select:focus {
  border-color: #008C95;
  box-shadow: 0 0 0 2px rgb(0 140 149 / 20%);
}
</style>
