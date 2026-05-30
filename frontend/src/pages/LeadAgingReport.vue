<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Lead Aging Report" />
      </template>
      <template #right-header>
        <Button variant="outline" size="sm" label="Reload" @click="report.reload()" />
      </template>
    </LayoutHeader>

    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-6 py-3">
      <div class="flex flex-wrap items-center gap-2">
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
        <div class="ml-3 text-xs uppercase tracking-wide text-ink-gray-5">Owner</div>
        <input
          v-model="filters.owner"
          type="text"
          placeholder="user@…"
          class="h-7 w-44 rounded-md border border-outline-gray-2 bg-white px-2 text-xs focus:border-ink-gray-5 focus:outline-none"
        />
        <div class="ml-3 text-xs uppercase tracking-wide text-ink-gray-5">Source</div>
        <input
          v-model="filters.source"
          type="text"
          placeholder="any"
          class="h-7 w-32 rounded-md border border-outline-gray-2 bg-white px-2 text-xs focus:border-ink-gray-5 focus:outline-none"
        />
        <Button
          size="sm"
          variant="outline"
          class="ml-auto"
          label="Export"
          @click="exportReport"
        />
      </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 px-6 py-4">
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div
          v-for="band in BANDS"
          :key="band.key"
          class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm"
        >
          <div class="text-[11px] uppercase tracking-wide text-ink-gray-5">{{ band.label }}</div>
          <div class="mt-1 flex items-baseline justify-between">
            <div class="text-2xl font-semibold" :class="bandColor(band.key, bandCount(band.key))">
              {{ bandCount(band.key) }}
            </div>
            <div class="text-[11px] text-ink-gray-5">{{ band.range }}</div>
          </div>
        </div>
      </div>

      <div class="mt-4 rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
        <div class="mb-2 text-sm font-semibold text-ink-gray-9">Aging Trend</div>
        <div class="h-32 w-full">
          <svg class="h-full w-full" :viewBox="`0 0 ${trendWidth} 100`" preserveAspectRatio="none">
            <g v-for="(series, i) in trendSeries" :key="series.key">
              <polyline
                :points="series.points"
                fill="none"
                :stroke="series.color"
                stroke-width="1.5"
              />
            </g>
          </svg>
        </div>
        <div class="mt-2 flex gap-3 text-[11px] text-ink-gray-6">
          <div v-for="series in trendSeries" :key="series.key" class="flex items-center gap-1">
            <span class="inline-block size-2 rounded-full" :style="{ backgroundColor: series.color }" />
            {{ series.label }}
          </div>
        </div>
      </div>

      <div class="mt-4 grid gap-3 lg:grid-cols-2">
        <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
          <div class="border-b border-outline-gray-1 px-3 py-2 text-sm font-semibold text-ink-gray-9">By Owner</div>
          <table class="w-full text-xs">
            <thead class="bg-surface-gray-1 text-left text-[11px] uppercase tracking-wide text-ink-gray-5">
              <tr>
                <th class="px-3 py-1.5">Owner</th>
                <th class="px-3 py-1.5 text-right">Fresh</th>
                <th class="px-3 py-1.5 text-right">Warm</th>
                <th class="px-3 py-1.5 text-right">Stale</th>
                <th class="px-3 py-1.5 text-right">Frozen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in report.data?.by_owner || []" :key="r.owner" class="border-t border-outline-gray-1">
                <td class="px-3 py-1.5 truncate max-w-[180px]">{{ r.owner }}</td>
                <td class="px-3 py-1.5 text-right">{{ r.fresh }}</td>
                <td class="px-3 py-1.5 text-right">{{ r.warm }}</td>
                <td class="px-3 py-1.5 text-right text-amber-600">{{ r.stale }}</td>
                <td class="px-3 py-1.5 text-right text-red-600">{{ r.frozen }}</td>
              </tr>
              <tr v-if="!report.data?.by_owner?.length">
                <td colspan="5" class="px-3 py-6 text-center text-ink-gray-5">No data in range</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
          <div class="border-b border-outline-gray-1 px-3 py-2 text-sm font-semibold text-ink-gray-9">By Source</div>
          <table class="w-full text-xs">
            <thead class="bg-surface-gray-1 text-left text-[11px] uppercase tracking-wide text-ink-gray-5">
              <tr>
                <th class="px-3 py-1.5">Source</th>
                <th class="px-3 py-1.5 text-right">Fresh</th>
                <th class="px-3 py-1.5 text-right">Warm</th>
                <th class="px-3 py-1.5 text-right">Stale</th>
                <th class="px-3 py-1.5 text-right">Frozen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in report.data?.by_source || []" :key="r.source" class="border-t border-outline-gray-1">
                <td class="px-3 py-1.5 truncate max-w-[180px]">{{ r.source }}</td>
                <td class="px-3 py-1.5 text-right">{{ r.fresh }}</td>
                <td class="px-3 py-1.5 text-right">{{ r.warm }}</td>
                <td class="px-3 py-1.5 text-right text-amber-600">{{ r.stale }}</td>
                <td class="px-3 py-1.5 text-right text-red-600">{{ r.frozen }}</td>
              </tr>
              <tr v-if="!report.data?.by_source?.length">
                <td colspan="5" class="px-3 py-6 text-center text-ink-gray-5">No data in range</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="mt-4 rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
        <div class="border-b border-outline-gray-1 px-3 py-2 text-sm font-semibold text-ink-gray-9">Top Stale Leads</div>
        <table class="w-full text-xs">
          <thead class="bg-surface-gray-1 text-left text-[11px] uppercase tracking-wide text-ink-gray-5">
            <tr>
              <th class="px-3 py-1.5">Lead</th>
              <th class="px-3 py-1.5">Owner</th>
              <th class="px-3 py-1.5">Source</th>
              <th class="px-3 py-1.5 text-right">Score</th>
              <th class="px-3 py-1.5 text-right">Days Idle</th>
              <th class="px-3 py-1.5">Band</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="r in report.data?.top_stale || []"
              :key="r.name"
              class="cursor-pointer border-t border-outline-gray-1 hover:bg-surface-gray-1"
              @click="openLead(r.name)"
            >
              <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ r.lead_name || r.name }}</td>
              <td class="px-3 py-1.5 truncate max-w-[160px]">{{ r.lead_owner || '—' }}</td>
              <td class="px-3 py-1.5">{{ r.source || '—' }}</td>
              <td class="px-3 py-1.5 text-right">{{ r.score }}</td>
              <td class="px-3 py-1.5 text-right">{{ r.days_inactive }}</td>
              <td class="px-3 py-1.5">
                <Badge :label="r.band" :theme="badgeTheme(r.band)" variant="subtle" size="sm" />
              </td>
            </tr>
            <tr v-if="!report.data?.top_stale?.length">
              <td colspan="6" class="px-3 py-6 text-center text-ink-gray-5">No stale leads — nice!</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import { Badge, Button, call, createResource, toast } from 'frappe-ui'
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const viewControls = ref(null)

const RANGES = [
  { key: '7d', label: '7 days' },
  { key: '30d', label: '30 days' },
  { key: '90d', label: '90 days' },
]

const BANDS = [
  { key: 'fresh', label: 'Fresh', range: '0–7d' },
  { key: 'warm', label: 'Warm', range: '8–14d' },
  { key: 'stale', label: 'Stale', range: '15–30d' },
  { key: 'frozen', label: 'Frozen', range: '30d+' },
]

const filters = reactive({ range: '30d', owner: '', source: '' })

const report = createResource({
  url: 'crm.api.lead_management.get_aging_report',
  makeParams: () => ({
    range: filters.range,
    owner: filters.owner || undefined,
    source: filters.source || undefined,
  }),
  auto: true,
})

watch(() => [filters.range, filters.owner, filters.source], () => report.fetch())

function bandCount(key) {
  return report.data?.bands_count?.[key] ?? 0
}

function bandColor(key, count) {
  if (!count) return 'text-ink-gray-4'
  if (key === 'stale') return 'text-amber-600'
  if (key === 'frozen') return 'text-red-600'
  return 'text-ink-gray-9'
}

function badgeTheme(band) {
  if (band === 'frozen') return 'red'
  if (band === 'stale') return 'orange'
  if (band === 'warm') return 'teal'
  return 'gray'
}

function openLead(name) {
  router.push({ name: 'Lead', params: { leadId: name } })
}

const trendWidth = computed(() => Math.max(20, (report.data?.trend?.length || 1) * 20))

const trendSeries = computed(() => {
  const trend = report.data?.trend || []
  if (!trend.length) return []
  const maxVal = Math.max(1, ...trend.flatMap((p) => [p.fresh, p.warm, p.stale, p.frozen]))
  const xStep = trendWidth.value / Math.max(1, trend.length - 1)
  const make = (key, label, color) => ({
    key,
    label,
    color,
    points: trend.map((p, i) => `${i * xStep},${100 - (p[key] / maxVal) * 90}`).join(' '),
  })
  return [
    make('fresh', 'Fresh', '#94a3b8'),
    make('warm', 'Warm', '#0f766e'),
    make('stale', 'Stale', '#FF6600'),
    make('frozen', 'Frozen', '#dc2626'),
  ]
})

const exportFilters = computed(() => {
  const f = { converted: 0 }
  if (filters.owner) f.lead_owner = filters.owner
  if (filters.source) f.source = filters.source
  return f
})
async function exportReport() {
  try {
    const res = await call('crm.api.lead_management.export_leads', {
      filters: exportFilters.value,
      format: 'CSV',
    })
    if (res?.async) {
      toast.success(`Export queued (${res.row_count} rows) — we'll email when ready`)
    } else if (res?.file_url) {
      window.open(res.file_url, '_blank')
    } else {
      toast.success('Export complete')
    }
  } catch (e) {
    toast.error(e?.message || 'Export failed')
  }
}
</script>
