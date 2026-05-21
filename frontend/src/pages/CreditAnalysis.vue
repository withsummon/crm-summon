<template>
  <div class="flex h-full bg-slate-50 font-sans">
    <div v-if="!routeApplication" class="w-80 border-r border-slate-200 bg-white flex flex-col shrink-0">
      <div class="p-4 border-b border-slate-200">
        <h2 class="text-lg font-bold text-slate-800 mb-3">{{ __('Individual Credit Queue') }}</h2>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search borrower or application')"
            class="w-full pl-9 pr-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-600 focus:bg-white transition-all"
          />
          <span class="absolute left-3 top-2.5 text-slate-400">
            <FeatherIcon name="search" class="h-4 w-4" />
          </span>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div
          v-for="app in filteredApps"
          :key="app.name"
          @click="selectApp(app)"
          class="flex flex-col gap-1 p-3 rounded-lg cursor-pointer transition-all hover:bg-slate-50 border"
          :class="selectedApp?.name === app.name ? 'bg-teal-50 border-teal-200' : 'border-transparent'"
        >
          <div class="flex justify-between items-start gap-2">
            <div class="font-semibold text-sm text-slate-800 truncate">{{ app.borrower_name }}</div>
            <Badge :label="app.status" :theme="statusTheme(app.status)" size="sm" variant="subtle" />
          </div>
          <div class="text-xs text-slate-500 truncate flex items-center gap-2 mt-0.5">
            <span class="font-mono text-slate-600">{{ app.name }}</span>
            <span class="w-1 h-1 rounded-full bg-slate-300"></span>
            <span>{{ app.facility_type || __('Credit Facility') }}</span>
          </div>
          <div class="text-xs font-bold text-slate-700 mt-1">
            {{ formatCurrency(app.requested_amount) }}
          </div>
        </div>
        <div v-if="!queue.loading && filteredApps.length === 0" class="p-6 text-center text-sm text-slate-400">
          {{ __('No individual applications found') }}
        </div>
      </div>
    </div>

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <div v-if="!selectedApp" class="flex-1 flex flex-col items-center justify-center text-slate-400 p-8">
        <div class="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center mb-4">
          <FeatherIcon name="user-check" class="h-10 w-10 text-slate-300" />
        </div>
        <h3 class="text-lg font-semibold text-slate-700">{{ __('No Application Selected') }}</h3>
        <p class="text-sm text-slate-500 mt-1 max-w-sm text-center">
          {{ __('Select an individual borrower to run credit analysis and PT Tbk enrichment when available.') }}
        </p>
      </div>

      <div v-else class="flex-1 flex flex-col overflow-hidden">
        <div class="bg-white border-b border-slate-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shrink-0 shadow-sm">
          <div class="flex items-center gap-4 min-w-0">
            <div class="w-16 h-16 rounded-xl bg-teal-600 text-white flex items-center justify-center font-black text-2xl shadow-md shadow-teal-600/10 shrink-0">
              {{ initials(selectedApp.borrower_name) }}
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-3 flex-wrap">
                <h1 class="text-2xl font-bold text-slate-800 truncate">{{ selectedApp.borrower_name }}</h1>
                <Badge label="Individual" theme="teal" variant="subtle" />
                <Badge :label="selectedApp.status" :theme="statusTheme(selectedApp.status)" variant="solid" />
              </div>
              <div class="text-sm text-slate-500 flex flex-wrap items-center gap-4 mt-1.5">
                <span class="flex items-center gap-1">
                  <FeatherIcon name="hash" class="h-3.5 w-3.5 text-slate-400" />
                  App: {{ selectedApp.name }}
                </span>
                <span class="flex items-center gap-1">
                  <FeatherIcon name="briefcase" class="h-3.5 w-3.5 text-slate-400" />
                  {{ selectedApp.employer_name || __('No employer enrichment') }}
                </span>
                <span class="flex items-center gap-1 font-bold text-slate-700">
                  <FeatherIcon name="dollar-sign" class="h-3.5 w-3.5 text-slate-500" />
                  Req: {{ formatCurrency(selectedApp.requested_amount) }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <Button v-if="routeApplication" variant="outline" :label="__('Back to List')" @click="goToCreditList">
              <template #prefix>
                <FeatherIcon name="arrow-left" class="h-4 w-4" />
              </template>
            </Button>
            <Button variant="outline" :label="__('Save Draft')" @click="triggerSave" />
            <Button variant="solid" :label="__('Submit to Committee')" @click="triggerSubmit">
              <template #prefix>
                <FeatherIcon name="check-circle" class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>

        <div class="px-6 pt-4 shrink-0 bg-white border-b border-slate-200">
          <div class="flex gap-6 overflow-x-auto">
            <button
              v-for="t in tabs"
              :key="t.key"
              @click="activeTab = t.key"
              class="pb-3 text-sm font-semibold border-b-2 transition-all whitespace-nowrap"
              :class="activeTab === t.key ? 'border-teal-600 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'"
            >
              {{ t.label }}
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6 min-h-0">
          <div v-if="analysis.loading" class="text-sm text-slate-500">{{ __('Loading credit analysis...') }}</div>

          <div v-else-if="activeTab === 'financials'" class="space-y-6">
            <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm xl:col-span-2">
                <div class="flex justify-between items-start gap-4 mb-4">
                  <div>
                    <h3 class="font-bold text-slate-800 text-lg">{{ __('Individual Credit Profile') }}</h3>
                    <p class="text-sm text-slate-500 mt-1">
                      {{ __('Personal credit data must come from authorized SLIK/OJK report upload or approved integration, not public scraping.') }}
                    </p>
                  </div>
                  <Badge :label="latestBureau?.kol_status || __('Bureau Pending')" :theme="latestBureau ? 'teal' : 'orange'" />
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MetricCard :label="__('Requested Amount')" :value="formatCurrency(selectedApp.requested_amount)" icon="dollar-sign" />
                  <MetricCard :label="__('Risk Grade')" :value="selectedApp.risk_grade || 'Unrated'" icon="activity" />
                  <MetricCard :label="__('External Exposure')" :value="formatCurrency(latestBureau?.external_exposure || 0)" icon="shield" />
                </div>
              </div>

              <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <h3 class="font-bold text-slate-800">{{ __('PT Tbk Public Enrichment') }}</h3>
                    <p class="text-xs text-slate-500 mt-1">
                      {{ selectedApp.public_company_ticker ? __('Employer or affiliation context only') : __('No ticker configured') }}
                    </p>
                  </div>
                  <Badge v-if="selectedApp.public_company_ticker" :label="selectedApp.public_company_ticker" theme="teal" />
                </div>

                <div class="mt-4 rounded-lg border border-slate-100 bg-slate-50 p-3 text-xs text-slate-600">
                  <div class="font-semibold text-slate-800">{{ publicSnapshot?.company_name || selectedApp.employer_name || __('No cached snapshot') }}</div>
                  <div class="mt-1">{{ publicSnapshotStatus }}</div>
                  <a
                    v-if="publicSnapshot?.source_url"
                    :href="publicSnapshot.source_url"
                    target="_blank"
                    rel="noreferrer"
                    class="mt-2 inline-flex text-teal-700 font-semibold hover:underline"
                  >
                    {{ __('Open source reference') }}
                  </a>
                </div>

                <Button
                  class="mt-4 w-full"
                  variant="outline"
                  :disabled="!selectedApp.public_company_ticker"
                  :loading="publicRefresh.loading"
                  :label="__('Gather Public Data')"
                  @click="refreshPublicData"
                >
                  <template #prefix>
                    <FeatherIcon name="refresh-cw" class="h-4 w-4" />
                  </template>
                </Button>
              </div>
            </div>

            <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm overflow-x-auto">
              <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-slate-800 text-lg">{{ __('Manual Financial Inputs / Public Snapshot') }}</h3>
                <Button variant="outline" size="sm" :label="__('AI OCR Extract from PDF')" @click="triggerOCR" iconLeft="zap" />
              </div>
              <table class="w-full text-sm min-w-[700px]">
                <thead>
                  <tr class="bg-slate-50 text-slate-500 border-b border-slate-200">
                    <th class="py-3 px-4 text-left font-bold">{{ __('Metric') }}</th>
                    <th class="py-3 px-4 text-right font-bold">{{ __('Year') }}</th>
                    <th class="py-3 px-4 text-right font-bold">{{ __('Amount') }}</th>
                    <th class="py-3 px-4 text-left font-bold">{{ __('Source') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="row in financialRows" :key="row.name || `${row.metric}-${row.year}`" class="border-b border-slate-100">
                    <td class="py-3 px-4 text-slate-800 font-semibold">{{ row.metric }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ row.year }}</td>
                    <td class="py-3 px-4 text-right font-mono">{{ formatCurrency(row.amount) }}</td>
                    <td class="py-3 px-4 text-slate-500">{{ row.source || __('Manual') }}</td>
                  </tr>
                  <tr v-if="financialRows.length === 0">
                    <td colspan="4" class="py-8 text-center text-slate-400">{{ __('No financial rows yet. Upload a report or add records from Customer 360.') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-else-if="activeTab === 'risk'" class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 class="font-bold text-slate-800 text-lg mb-4">{{ __('Authorized Bureau Review') }}</h3>
                <div class="space-y-3 text-sm">
                  <InfoRow :label="__('Source')" :value="latestBureau?.source || __('Manual report required')" />
                  <InfoRow :label="__('KOL Status')" :value="latestBureau?.kol_status || __('Pending')" />
                  <InfoRow :label="__('Score')" :value="latestBureau?.score ? String(latestBureau.score) : __('Not available')" />
                  <InfoRow :label="__('Exposure')" :value="formatCurrency(latestBureau?.external_exposure || 0)" />
                </div>
              </div>

              <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 class="font-bold text-slate-800 text-lg mb-4">{{ __('Collateral Coverage') }}</h3>
                <div class="space-y-3">
                  <div v-for="col in collaterals" :key="col.name" class="p-3 border border-slate-100 rounded-lg bg-slate-50">
                    <div class="flex justify-between gap-3">
                      <span class="font-semibold text-slate-800 text-sm">{{ col.asset }}</span>
                      <span class="font-mono text-sm text-teal-700">{{ formatCurrency(col.collateral_value) }}</span>
                    </div>
                    <div class="text-xs text-slate-500 mt-1">{{ col.status }} · {{ col.expiry_date || __('No expiry') }}</div>
                  </div>
                  <div v-if="collaterals.length === 0" class="text-sm text-slate-400">{{ __('No collateral records yet.') }}</div>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="activeTab === 'scenarios'" class="space-y-6">
            <h3 class="font-bold text-slate-800 text-lg">{{ __('Scenario Simulation & Stress Testing') }}</h3>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <ScenarioCard label="Best Case" detail="+10% income, stable KOL" badge="Approval likely" theme="emerald" />
              <ScenarioCard label="Base Case" detail="Current income and collateral" badge="Manual review" theme="teal" active />
              <ScenarioCard label="Worst Case" detail="-15% income, KOL deterioration" badge="Mitigation required" theme="red" />
            </div>
          </div>

          <div v-else-if="activeTab === 'memo'" class="space-y-6">
            <div class="flex justify-between items-center">
              <h3 class="font-bold text-slate-800 text-lg">{{ __('Credit Analysis Memorandum (CAM)') }}</h3>
              <Button variant="solid" size="sm" :label="__('Generate AI Draft')" @click="generateMemo" iconLeft="cpu" />
            </div>
            <div class="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-[500px]">
              <div class="bg-slate-50 border-b border-slate-200 p-2 flex gap-2">
                <Button variant="subtle" size="sm" icon="bold" />
                <Button variant="subtle" size="sm" icon="italic" />
                <Button variant="subtle" size="sm" icon="list" />
                <div class="w-px h-6 bg-slate-300 mx-2"></div>
                <Button variant="subtle" size="sm" :label="__('Insert Bureau Summary')" />
                <Button variant="subtle" size="sm" :label="__('Insert Public Snapshot')" />
              </div>
              <textarea
                v-model="memoContent"
                class="flex-1 w-full p-6 focus:outline-none resize-none text-sm text-slate-700 leading-relaxed"
                :placeholder="__('Generate or write the memorandum...')"
              ></textarea>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, FeatherIcon, Badge, usePageMeta, toast, createResource } from 'frappe-ui'
import { computed, h, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const MetricCard = {
  props: ['label', 'value', 'icon'],
  setup(props) {
    return () => h('div', { class: 'rounded-lg border border-slate-100 bg-slate-50 p-4' }, [
      h('div', { class: 'flex items-center gap-2 text-xs font-semibold uppercase text-slate-400' }, [
        h(FeatherIcon, { name: props.icon, class: 'h-4 w-4 text-teal-600' }),
        props.label,
      ]),
      h('div', { class: 'mt-2 text-lg font-bold text-slate-800' }, props.value),
    ])
  },
}

const InfoRow = {
  props: ['label', 'value'],
  setup(props) {
    return () => h('div', { class: 'flex justify-between gap-4 border-b border-slate-100 pb-2' }, [
      h('span', { class: 'text-slate-500' }, props.label),
      h('span', { class: 'font-semibold text-slate-800 text-right' }, props.value),
    ])
  },
}

const ScenarioCard = {
  props: ['label', 'detail', 'badge', 'theme', 'active'],
  setup(props) {
    const border = props.active ? 'border-2 border-teal-500 shadow-teal-500/20' : 'border border-slate-200'
    return () => h('div', { class: `bg-white ${border} rounded-xl p-5 shadow-sm flex flex-col items-center justify-center text-center` }, [
      h('h4', { class: 'font-bold text-slate-800 mb-2' }, props.label),
      h('p', { class: 'text-xs text-slate-500 mb-4' }, props.detail),
      h(Badge, { label: props.badge, theme: props.theme }),
    ])
  },
}

const searchQuery = ref('')
const selectedApp = ref(null)
const activeTab = ref('financials')
const memoContent = ref('')
const route = useRoute()
const router = useRouter()
const routeApplication = computed(() => String(route.params.applicationId || ''))

const tabs = [
  { key: 'financials', label: 'Credit Profile' },
  { key: 'risk', label: 'Risk & Bureau' },
  { key: 'scenarios', label: 'Scenarios' },
  { key: 'memo', label: 'CAM Memo' },
]

const queue = createResource({
  url: 'crm.api.credit.get_credit_application_queue',
  auto: true,
  onSuccess(data) {
    if (routeApplication.value) loadRouteApplication()
    else if (!selectedApp.value && data?.length) selectApp(data[0])
  },
})

const analysis = createResource({
  url: 'crm.api.credit.get_credit_analysis',
  makeParams() {
    return { application_id: selectedApp.value?.name }
  },
})

const publicRefresh = createResource({
  url: 'crm.api.credit.refresh_public_company_snapshot',
  makeParams() {
    return { ticker: selectedApp.value?.public_company_ticker }
  },
  onSuccess(data) {
    if (analysis.data) analysis.data.public_snapshot = data
    toast.success(__('Public company snapshot refreshed'))
  },
  onError() {
    toast.error(__('Unable to refresh public company snapshot'))
  },
})

const applications = computed(() => queue.data || [])
const filteredApps = computed(() => {
  const q = searchQuery.value.toLowerCase()
  if (!q) return applications.value
  return applications.value.filter((app) =>
    [app.borrower_name, app.name, app.facility_type, app.public_company_ticker]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(q)),
  )
})

const latestBureau = computed(() => analysis.data?.bureau || null)
const collaterals = computed(() => analysis.data?.collaterals || [])
const financialRows = computed(() => analysis.data?.financials || [])
const publicSnapshot = computed(() => analysis.data?.public_snapshot || null)
const publicSnapshotStatus = computed(() => {
  if (!selectedApp.value?.public_company_ticker) return __('Add PT Tbk ticker to enable public enrichment.')
  if (!publicSnapshot.value) return __('No cached snapshot yet.')
  return `${publicSnapshot.value.status || __('Unknown')} · ${publicSnapshot.value.fetched_at || __('not fetched')}`
})

function selectApp(app) {
  selectedApp.value = app
  activeTab.value = 'financials'
  analysis.fetch()
}

function loadRouteApplication() {
  if (!routeApplication.value) return
  const row = (queue.data || []).find((app) => app.name === routeApplication.value)
  selectApp(row || { name: routeApplication.value, borrower_name: routeApplication.value, status: 'Pending Review' })
}

function goToCreditList() {
  router.push({ name: 'Credit Analysis' })
}

function refreshPublicData() {
  if (!selectedApp.value?.public_company_ticker) return
  publicRefresh.submit()
}

function initials(value) {
  return (value || 'NA').slice(0, 2).toUpperCase()
}

function statusTheme(status) {
  if (status === 'Approved') return 'green'
  if (status === 'Rejected') return 'red'
  if (status === 'Pending Review') return 'orange'
  return 'teal'
}

function formatCurrency(value) {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function generateMemo() {
  const app = selectedApp.value
  memoContent.value = `EXECUTIVE SUMMARY
${app.borrower_name} is an individual borrower requesting ${formatCurrency(app.requested_amount)} for ${app.facility_type || 'credit facility'}.

1. BORROWER PROFILE
Borrower type is Individual. Personal credit data must be supported by authorized SLIK/OJK report upload or approved integration.

2. PUBLIC COMPANY ENRICHMENT
${app.public_company_ticker ? `${app.employer_name || 'Employer'} is linked to ticker ${app.public_company_ticker}. Public PT Tbk data is used only as employer or affiliation context.` : 'No PT Tbk enrichment ticker is configured.'}

3. RECOMMENDATION
Proceed with manual bureau verification, collateral validation, and committee review before final approval.`
  toast.success(__('CAM draft generated'))
}

function triggerSave() {
  toast.success(__('Analysis draft saved'))
}

function triggerSubmit() {
  toast.success(__('CAM submitted to Credit Committee routing'))
}

function triggerOCR() {
  toast.success(__('Upload/OCR workflow prepared for manual reports'))
}

onMounted(() => {
  if (routeApplication.value) loadRouteApplication()
  else if (queue.data?.length && !selectedApp.value) selectApp(queue.data[0])
})

watch(routeApplication, () => {
  loadRouteApplication()
})

usePageMeta(() => ({ title: 'Credit Analysis' }))
</script>

<style scoped>
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
