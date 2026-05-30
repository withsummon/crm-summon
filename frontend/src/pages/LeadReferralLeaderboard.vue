<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Lead Referrals" />
      </template>
      <template #right-header>
        <Button variant="outline" size="sm" label="Reload" @click="board.reload()" />
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
        <div class="ml-3 text-xs uppercase tracking-wide text-ink-gray-5">Type</div>
        <div class="flex gap-1">
          <button
            v-for="t in TYPES"
            :key="t.key"
            class="rounded-md border px-2 py-1 text-xs"
            :class="filters.type === t.key ? 'border-[#0f766e] bg-[#0f766e] text-white' : 'border-outline-gray-2 bg-white text-ink-gray-7'"
            @click="filters.type = t.key"
          >
            {{ t.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 px-6 py-4">
      <div v-if="podium.length" class="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div
          v-for="(p, idx) in podium"
          :key="p.referrer"
          class="rounded-[10px] border bg-white p-3 shadow-sm"
          :class="podiumBorder(idx)"
        >
          <div class="flex items-center justify-between">
            <div class="text-xs uppercase tracking-wide text-ink-gray-5">
              {{ ['Gold', 'Silver', 'Bronze'][idx] }}
            </div>
            <div class="text-xs font-semibold" :class="podiumText(idx)">#{{ idx + 1 }}</div>
          </div>
          <div class="mt-1 truncate text-sm font-semibold text-ink-gray-9">{{ p.referrer }}</div>
          <div class="text-xs text-ink-gray-6">{{ p.referrer_type }}</div>
          <div class="mt-2 grid grid-cols-3 gap-1 text-center">
            <div>
              <div class="text-base font-semibold text-ink-gray-9">{{ p.leads_count }}</div>
              <div class="text-[10px] uppercase text-ink-gray-5">Leads</div>
            </div>
            <div>
              <div class="text-base font-semibold text-ink-gray-9">{{ p.converted_count }}</div>
              <div class="text-[10px] uppercase text-ink-gray-5">Won</div>
            </div>
            <div>
              <div class="text-base font-semibold text-ink-gray-9">{{ formatRupiah(p.total_referral_fee) }}</div>
              <div class="text-[10px] uppercase text-ink-gray-5">Fee</div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
        <table class="w-full text-sm">
          <thead class="bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
            <tr>
              <th class="px-3 py-2">#</th>
              <th class="px-3 py-2">Referrer</th>
              <th class="px-3 py-2">Type</th>
              <th class="px-3 py-2 text-right">Leads</th>
              <th class="px-3 py-2 text-right">Converted</th>
              <th class="px-3 py-2 text-right">Conv. %</th>
              <th class="px-3 py-2 text-right">Total Fee</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in board.data?.rows || []" :key="r.referrer + r.referrer_type" class="border-t border-outline-gray-1">
              <td class="px-3 py-1.5 text-ink-gray-6">{{ r.rank }}</td>
              <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ r.referrer || '—' }}</td>
              <td class="px-3 py-1.5"><Badge :label="r.referrer_type" theme="teal" variant="subtle" size="sm" /></td>
              <td class="px-3 py-1.5 text-right">{{ r.leads_count }}</td>
              <td class="px-3 py-1.5 text-right">{{ r.converted_count }}</td>
              <td class="px-3 py-1.5 text-right">{{ r.conversion_pct }}%</td>
              <td class="px-3 py-1.5 text-right font-mono">{{ formatRupiah(r.total_referral_fee) }}</td>
            </tr>
            <tr v-if="!board.data?.rows?.length">
              <td colspan="7" class="px-3 py-8 text-center text-ink-gray-5">No referrals in this range.</td>
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
import { Badge, Button, createResource } from 'frappe-ui'
import { computed, reactive, ref, watch } from 'vue'

const viewControls = ref(null)

const RANGES = [
  { key: 'month', label: 'Month' },
  { key: 'quarter', label: 'Quarter' },
  { key: 'year', label: 'Year' },
  { key: 'all', label: 'All time' },
]
const TYPES = [
  { key: 'all', label: 'All' },
  { key: 'Customer', label: 'Customer' },
  { key: 'RM', label: 'RM' },
  { key: 'Partner', label: 'Partner' },
  { key: 'Other', label: 'Other' },
]

const filters = reactive({ range: 'month', type: 'all' })

const board = createResource({
  url: 'crm.api.lead_management.list_referrer_leaderboard',
  makeParams: () => ({ range: filters.range, type: filters.type }),
  auto: true,
})

watch(() => [filters.range, filters.type], () => board.fetch())

const podium = computed(() => (board.data?.rows || []).slice(0, 3))

function podiumBorder(i) {
  return ['border-amber-300', 'border-slate-300', 'border-orange-200'][i] || 'border-outline-gray-2'
}
function podiumText(i) {
  return ['text-amber-600', 'text-slate-500', 'text-orange-600'][i] || 'text-ink-gray-6'
}
function formatRupiah(n) {
  const v = Number(n || 0)
  if (!v) return 'Rp 0'
  return 'Rp ' + v.toLocaleString('id-ID')
}
</script>
