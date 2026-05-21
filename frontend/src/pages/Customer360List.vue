<template>
  <div class="h-full overflow-y-auto bg-slate-50 font-sans">
    <div class="mx-auto max-w-7xl px-6 py-6">
      <div class="mb-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">{{ __('Customer 360') }}</h1>
          <p class="mt-1 text-sm text-slate-500">
            {{ __('Table-first customer workspace. Click a row to open the full 360 profile.') }}
          </p>
        </div>
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
          <div class="relative w-full sm:w-96">
            <input
              v-model="query"
              type="text"
              :placeholder="__('Search name, NPWP, KTP, group, territory')"
              class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm text-slate-700 shadow-sm outline-none transition focus:border-teal-500"
            />
            <FeatherIcon name="search" class="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          </div>
          <Button variant="outline" :loading="customers.loading" :label="__('Refresh')" @click="customers.fetch()" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <SummaryCard :label="__('Customers')" :value="String(rows.length)" icon="users" />
        <SummaryCard :label="__('Active Facilities')" :value="String(totalFacilities)" icon="briefcase" />
        <SummaryCard :label="__('Outstanding')" :value="formatCurrency(totalOutstanding)" icon="dollar-sign" />
        <SummaryCard :label="__('Watchlist')" :value="String(watchlistCount)" icon="alert-triangle" />
      </div>

      <div class="mt-5 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <div class="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
          {{ __('Customer Directory') }}
        </div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[980px] text-sm">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <th class="px-4 py-3 font-bold">{{ __('Customer') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Segment') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('KYC') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Risk') }}</th>
                <th class="px-4 py-3 text-right font-bold">{{ __('Outstanding') }}</th>
                <th class="px-4 py-3 text-right font-bold">{{ __('Facilities') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Tags') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Modified') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in rows"
                :key="row.name"
                class="cursor-pointer border-b border-slate-100 transition hover:bg-teal-50/60"
                @click="openCustomer(row)"
              >
                <td class="px-4 py-4">
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-teal-100 text-sm font-black text-teal-700">
                      {{ initials(row.customer_name || row.name) }}
                    </div>
                    <div class="min-w-0">
                      <div class="truncate font-bold text-slate-800">{{ row.customer_name || row.name }}</div>
                      <div class="mt-0.5 truncate text-xs text-slate-500">{{ row.name }} · {{ row.npwp || row.nik || __('No ID') }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-4 text-slate-600">
                  <div class="font-semibold text-slate-700">{{ row.customer_type || __('Customer') }}</div>
                  <div class="text-xs text-slate-500">{{ row.customer_group || row.territory || '-' }}</div>
                </td>
                <td class="px-4 py-4">
                  <Badge :label="row.kyc_status || 'Pending'" :theme="row.kyc_status === 'Verified' ? 'green' : 'orange'" variant="subtle" />
                </td>
                <td class="px-4 py-4">
                  <div class="font-bold text-slate-800">{{ row.risk_grade || __('Unrated') }}</div>
                  <div class="text-xs text-slate-500">{{ __('Score') }} {{ row.score || 0 }}</div>
                </td>
                <td class="px-4 py-4 text-right font-mono text-slate-700">{{ formatCurrency(row.total_outstanding) }}</td>
                <td class="px-4 py-4 text-right font-semibold text-slate-700">{{ row.active_facilities || 0 }}</td>
                <td class="px-4 py-4">
                  <div class="flex flex-wrap gap-1">
                    <Badge v-if="row.watchlist" label="Watchlist" theme="red" variant="subtle" />
                    <Badge v-for="tag in tagList(row.tags)" :key="tag" :label="tag" theme="gray" variant="subtle" />
                    <span v-if="!row.watchlist && !tagList(row.tags).length" class="text-xs text-slate-400">-</span>
                  </div>
                </td>
                <td class="px-4 py-4 text-slate-500">{{ formatDate(row.modified) }}</td>
              </tr>
              <tr v-if="!customers.loading && rows.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-sm text-slate-400">{{ __('No customer rows found') }}</td>
              </tr>
              <tr v-if="customers.loading">
                <td colspan="8" class="px-4 py-12 text-center text-sm text-slate-400">{{ __('Loading customer table...') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Badge, Button, FeatherIcon, createResource, usePageMeta } from 'frappe-ui'
import { computed, h, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const query = ref('')
let searchTimer = null

const customers = createResource({
  url: 'crm.api.credit.get_customer_360_table',
  auto: true,
  makeParams() {
    return { query: query.value, limit: 200 }
  },
})

const rows = computed(() => customers.data || [])
const totalFacilities = computed(() => rows.value.reduce((sum, row) => sum + Number(row.active_facilities || 0), 0))
const totalOutstanding = computed(() => rows.value.reduce((sum, row) => sum + Number(row.total_outstanding || 0), 0))
const watchlistCount = computed(() => rows.value.filter((row) => row.watchlist).length)

function openCustomer(row) {
  router.push({ name: 'Customer 360 Detail', params: { customer: row.name } })
}

function tagList(value) {
  return String(value || '').split(',').map((tag) => tag.trim()).filter(Boolean).slice(0, 3)
}

function initials(value) {
  return String(value || 'CU').slice(0, 2).toUpperCase()
}

function formatCurrency(value) {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(Number(value || 0))
}

function formatDate(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('id-ID', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value))
}

watch(query, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => customers.fetch(), 250)
})

usePageMeta(() => ({ title: 'Customer 360' }))

const SummaryCard = {
  props: ['label', 'value', 'icon'],
  setup(props) {
    return () => h('div', { class: 'rounded-lg border border-slate-200 bg-white p-4 shadow-sm' }, [
      h('div', { class: 'flex items-center justify-between gap-3' }, [
        h('div', { class: 'text-xs font-bold uppercase tracking-wide text-slate-500' }, props.label),
        h('div', { class: 'flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50 text-teal-600' }, [
          h(FeatherIcon, { name: props.icon, class: 'h-4 w-4' }),
        ]),
      ]),
      h('div', { class: 'mt-3 text-2xl font-black text-slate-900' }, props.value),
    ])
  },
}
</script>
