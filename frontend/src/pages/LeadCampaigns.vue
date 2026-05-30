<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Lead Campaigns" />
      </template>
      <template #right-header>
        <Button variant="outline" size="sm" label="Reload" @click="campaigns.reload()" />
        <Button variant="solid" label="New Campaign" @click="openCreate()">
          <template #prefix><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-6 py-3">
      <div class="flex items-center gap-2">
        <div class="text-xs uppercase tracking-wide text-ink-gray-5">Range</div>
        <div class="flex gap-1">
          <button
            v-for="r in RANGES"
            :key="r.key"
            class="rounded-md border px-2 py-1 text-xs"
            :class="filters.range === r.key ? 'border-[#FF6600] bg-[#FF6600] text-white' : 'border-outline-gray-2 bg-white text-ink-gray-7'"
            @click="filters.range = r.key"
          >
            {{ r.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 px-6 py-4">
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div
          v-for="kpi in kpiCards"
          :key="kpi.label"
          class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm"
        >
          <div class="text-[11px] uppercase tracking-wide text-ink-gray-5">{{ kpi.label }}</div>
          <div class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ kpi.value }}</div>
        </div>
      </div>

      <div class="mt-4 rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
        <table class="w-full text-sm">
          <thead class="bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
            <tr>
              <th class="px-3 py-2">Campaign</th>
              <th class="px-3 py-2">Status</th>
              <th class="px-3 py-2">Channel</th>
              <th class="px-3 py-2">Start–End</th>
              <th class="px-3 py-2 text-right">Cost</th>
              <th class="px-3 py-2 text-right">Leads</th>
              <th class="px-3 py-2 text-right">Conv. %</th>
              <th class="px-3 py-2 text-right">CPL</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="c in campaigns.data?.campaigns || []"
              :key="c.name"
              class="cursor-pointer border-t border-outline-gray-1 hover:bg-surface-gray-1"
              @click="openDetail(c.name)"
            >
              <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ c.campaign_name }}</td>
              <td class="px-3 py-1.5"><Badge :label="c.status || 'Draft'" :theme="statusTheme(c.status)" variant="subtle" size="sm" /></td>
              <td class="px-3 py-1.5 text-ink-gray-7">{{ c.source || '—' }}</td>
              <td class="px-3 py-1.5 text-xs text-ink-gray-6">{{ dateRange(c) }}</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ formatRupiah(c.cost) }}</td>
              <td class="px-3 py-1.5 text-right">{{ c.leads_count }}</td>
              <td class="px-3 py-1.5 text-right">{{ c.conversion_pct }}%</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ c.cost_per_lead ? formatRupiah(c.cost_per_lead) : '—' }}</td>
            </tr>
            <tr v-if="!campaigns.data?.campaigns?.length">
              <td colspan="8" class="px-3 py-8 text-center text-ink-gray-5">No campaigns yet. Click "New Campaign" to add one.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div
      v-if="selected"
      class="fixed right-0 top-0 z-40 flex h-full w-full flex-col border-l border-outline-gray-2 bg-white shadow-xl sm:w-[480px]"
    >
      <div class="flex items-center justify-between border-b border-outline-gray-2 px-4 py-3">
        <div class="min-w-0">
          <div class="truncate text-sm font-semibold text-ink-gray-9">{{ selected }}</div>
          <div class="text-xs text-ink-gray-5">Campaign detail</div>
        </div>
        <button class="text-ink-gray-5 hover:text-ink-gray-8" @click="selected = null">×</button>
      </div>
      <div class="flex-1 overflow-y-auto p-4">
        <div v-if="detail.loading" class="py-6 text-center text-sm text-ink-gray-5">Loading…</div>
        <template v-else-if="detail.data">
          <div class="grid grid-cols-2 gap-2">
            <div class="rounded border border-outline-gray-1 p-2">
              <div class="text-[10px] uppercase text-ink-gray-5">Leads</div>
              <div class="text-lg font-semibold">{{ detail.data.kpis.leads }}</div>
            </div>
            <div class="rounded border border-outline-gray-1 p-2">
              <div class="text-[10px] uppercase text-ink-gray-5">Converted</div>
              <div class="text-lg font-semibold">{{ detail.data.kpis.converted }}</div>
            </div>
            <div class="rounded border border-outline-gray-1 p-2">
              <div class="text-[10px] uppercase text-ink-gray-5">Conv. %</div>
              <div class="text-lg font-semibold">{{ detail.data.kpis.conversion_pct }}%</div>
            </div>
            <div class="rounded border border-outline-gray-1 p-2">
              <div class="text-[10px] uppercase text-ink-gray-5">CPL</div>
              <div class="text-lg font-semibold">{{ detail.data.kpis.cost_per_lead ? formatRupiah(detail.data.kpis.cost_per_lead) : '—' }}</div>
            </div>
          </div>

          <div class="mt-4">
            <div class="mb-1 text-xs font-semibold uppercase text-ink-gray-5">UTM Template</div>
            <div class="rounded border border-outline-gray-1 p-2 font-mono text-xs text-ink-gray-7">
              <div>utm_source = {{ detail.data.campaign.utm_source || '—' }}</div>
              <div>utm_medium = {{ detail.data.campaign.utm_medium || '—' }}</div>
              <div>utm_campaign = {{ detail.data.campaign.utm_campaign || '—' }}</div>
            </div>
          </div>

          <div class="mt-4">
            <div class="mb-1 text-xs font-semibold uppercase text-ink-gray-5">Per-day</div>
            <div class="h-24 w-full">
              <svg class="h-full w-full" :viewBox="`0 0 ${perDayWidth} 100`" preserveAspectRatio="none">
                <polyline
                  :points="perDayPoints"
                  fill="none"
                  stroke="#FF6600"
                  stroke-width="1.5"
                />
              </svg>
            </div>
          </div>

          <div class="mt-4">
            <div class="mb-1 text-xs font-semibold uppercase text-ink-gray-5">Top Sources</div>
            <div class="space-y-1">
              <div
                v-for="s in detail.data.top_sources"
                :key="s.source"
                class="flex justify-between text-xs"
              >
                <span class="text-ink-gray-7">{{ s.source }}</span>
                <span class="font-mono text-ink-gray-9">{{ s.count }}</span>
              </div>
              <div v-if="!detail.data.top_sources?.length" class="text-xs text-ink-gray-5">No source data.</div>
            </div>
          </div>

          <div class="mt-4">
            <div class="mb-1 flex items-center justify-between">
              <div class="text-xs font-semibold uppercase text-ink-gray-5">UTM Breakdown</div>
            </div>
            <table class="w-full text-xs">
              <thead class="bg-surface-gray-1 text-left text-[10px] uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-2 py-1">Source</th>
                  <th class="px-2 py-1">Medium</th>
                  <th class="px-2 py-1 text-right">Leads</th>
                  <th class="px-2 py-1 text-right">Conv.</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(u, i) in detail.data.utm_breakdown" :key="i" class="border-t border-outline-gray-1">
                  <td class="px-2 py-1 truncate">{{ u.utm_source }}</td>
                  <td class="px-2 py-1 truncate">{{ u.utm_medium }}</td>
                  <td class="px-2 py-1 text-right">{{ u.leads }}</td>
                  <td class="px-2 py-1 text-right">{{ u.converted }}</td>
                </tr>
                <tr v-if="!detail.data.utm_breakdown?.length">
                  <td colspan="4" class="px-2 py-3 text-center text-ink-gray-5">No UTM data.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="mt-4 flex gap-2">
            <Button variant="outline" size="sm" label="Edit" @click="openEdit(detail.data.campaign)" />
          </div>
        </template>
      </div>
    </div>

    <Dialog
      v-model="showDialog"
      :options="{
        title: editing.name ? 'Edit Campaign' : 'New Campaign',
        size: 'lg',
        actions: [
          { label: 'Cancel', onClick: () => (showDialog = false) },
          { label: 'Save', variant: 'solid', loading: saving, onClick: saveCampaign },
        ],
      }"
    >
      <template #body-content>
        <div class="grid gap-3 sm:grid-cols-2">
          <div class="sm:col-span-2">
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Name</label>
            <input
              v-model="editing.campaign_name"
              :disabled="!!editing.name"
              type="text"
              class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none disabled:bg-surface-gray-1"
            />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Status</label>
            <select v-model="editing.status" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none">
              <option>Draft</option>
              <option>Active</option>
              <option>Paused</option>
              <option>Completed</option>
              <option>Archived</option>
            </select>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Primary Source</label>
            <input v-model="editing.source" type="text" placeholder="e.g. Website" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Start Date</label>
            <input v-model="editing.start_date" type="date" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">End Date</label>
            <input v-model="editing.end_date" type="date" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Budget (Rp)</label>
            <input v-model.number="editing.budget" type="number" min="0" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>
          <div class="sm:col-span-2 mt-1 border-t border-outline-gray-1 pt-2">
            <div class="mb-1 text-xs font-semibold uppercase text-ink-gray-5">UTM Template</div>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">utm_source</label>
            <input v-model="editing.utm_source" type="text" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">utm_medium</label>
            <input v-model="editing.utm_medium" type="text" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>
          <div class="sm:col-span-2">
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">utm_campaign</label>
            <input v-model="editing.utm_campaign" type="text" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
            <div class="mt-1 text-[11px] text-ink-gray-5">New leads whose `utm_campaign` matches this value will auto-link to this campaign.</div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import { Badge, Button, Dialog, FeatherIcon, call, createResource, toast } from 'frappe-ui'
import { computed, reactive, ref, watch } from 'vue'

const viewControls = ref(null)
const RANGES = [
  { key: 'month', label: 'Month' },
  { key: 'quarter', label: 'Quarter' },
  { key: 'year', label: 'Year' },
  { key: 'all', label: 'All' },
]
const filters = reactive({ range: 'month' })

const campaigns = createResource({
  url: 'crm.api.lead_management.list_campaigns',
  makeParams: () => ({ range: filters.range }),
  auto: true,
})
watch(() => filters.range, () => campaigns.fetch())

const kpiCards = computed(() => {
  const k = campaigns.data?.kpis || {}
  return [
    { label: 'Active', value: k.active ?? 0 },
    { label: 'Leads', value: k.leads ?? 0 },
    { label: 'Avg CPL', value: k.avg_cpl ? formatRupiah(k.avg_cpl) : '—' },
    { label: 'Avg Conv. %', value: (k.avg_conversion ?? 0) + '%' },
  ]
})

const selected = ref(null)
const detail = createResource({
  url: 'crm.api.lead_management.get_campaign_detail',
  makeParams: () => ({ name: selected.value, range: filters.range }),
})
watch(selected, (v) => {
  if (v) detail.fetch()
})

function openDetail(name) {
  selected.value = name
}

const perDayWidth = computed(() => Math.max(20, (detail.data?.per_day?.length || 1) * 14))
const perDayPoints = computed(() => {
  const series = detail.data?.per_day || []
  if (!series.length) return ''
  const max = Math.max(1, ...series.map((p) => p.leads))
  const xStep = perDayWidth.value / Math.max(1, series.length - 1)
  return series.map((p, i) => `${i * xStep},${100 - (p.leads / max) * 90}`).join(' ')
})

const showDialog = ref(false)
const saving = ref(false)
const editing = reactive({
  name: '', campaign_name: '', status: 'Draft', source: '',
  start_date: '', end_date: '', budget: 0,
  utm_source: '', utm_medium: '', utm_campaign: '', description: '',
})

function resetEditing() {
  Object.assign(editing, { name: '', campaign_name: '', status: 'Draft', source: '', start_date: '', end_date: '', budget: 0, utm_source: '', utm_medium: '', utm_campaign: '', description: '' })
}

function openCreate() {
  resetEditing()
  showDialog.value = true
}
function openEdit(c) {
  Object.assign(editing, {
    name: c.name,
    campaign_name: c.campaign_name,
    status: c.status || 'Draft',
    source: c.source || '',
    start_date: c.start_date || '',
    end_date: c.end_date || '',
    budget: c.budget || 0,
    utm_source: c.utm_source || '',
    utm_medium: c.utm_medium || '',
    utm_campaign: c.utm_campaign || '',
    description: c.description || '',
  })
  showDialog.value = true
}

async function saveCampaign() {
  if (!editing.campaign_name.trim()) {
    toast.error('Name is required')
    return
  }
  saving.value = true
  try {
    await call('crm.api.lead_management.upsert_campaign', { payload: { ...editing } })
    showDialog.value = false
    toast.success(editing.name ? 'Campaign updated' : 'Campaign created')
    campaigns.reload()
    if (selected.value) detail.fetch()
  } catch (e) {
    toast.error(e?.message || 'Failed to save')
  } finally {
    saving.value = false
  }
}

function statusTheme(s) {
  const v = (s || '').toLowerCase()
  if (v === 'active') return 'green'
  if (v === 'paused') return 'orange'
  if (v === 'completed') return 'teal'
  if (v === 'archived') return 'gray'
  return 'gray'
}
function dateRange(c) {
  const s = c.start_date ? new Date(c.start_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '?'
  const e = c.end_date ? new Date(c.end_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '?'
  if (!c.start_date && !c.end_date) return '—'
  return `${s} → ${e}`
}
function formatRupiah(n) {
  const v = Number(n || 0)
  if (!v) return 'Rp 0'
  return 'Rp ' + v.toLocaleString('id-ID')
}
</script>
