<template>
  <div class="h-full overflow-y-auto bg-slate-50 font-sans">
    <div class="mx-auto max-w-7xl px-6 py-6">
      <div class="mb-5 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 class="text-2xl font-bold text-slate-900">{{ __('Credit Analysis') }}</h1>
          <p class="mt-1 text-sm text-slate-500">
            {{ __('Individual credit application table. Click a row to open the analysis workspace.') }}
          </p>
        </div>
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
          <div class="relative w-full sm:w-96">
            <input
              v-model="query"
              type="text"
              :placeholder="__('Search borrower, app ID, facility, ticker')"
              class="h-10 w-full rounded-lg border border-slate-200 bg-white pl-10 pr-3 text-sm text-slate-700 shadow-sm outline-none transition focus:border-teal-500"
            />
            <FeatherIcon name="search" class="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          </div>
          <Button variant="outline" :loading="applications.loading" :label="__('Refresh')" @click="applications.fetch()" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-4">
        <SummaryCard :label="__('Applications')" :value="String(rows.length)" icon="file-text" />
        <SummaryCard :label="__('Requested')" :value="formatCurrency(totalRequested)" icon="dollar-sign" />
        <SummaryCard :label="__('In Progress')" :value="String(statusCount('In Progress'))" icon="clock" />
        <SummaryCard :label="__('With PT Tbk')" :value="String(withTicker)" icon="briefcase" />
      </div>

      <div class="mt-5 overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
        <div class="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
          {{ __('Credit Application Register') }}
        </div>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[980px] text-sm">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <th class="px-4 py-3 font-bold">{{ __('Application') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Borrower') }}</th>
                <th class="px-4 py-3 text-right font-bold">{{ __('Amount') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Facility') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Status') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Employer / Ticker') }}</th>
                <th class="px-4 py-3 font-bold">{{ __('Risk Grade') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in rows"
                :key="row.name"
                class="cursor-pointer border-b border-slate-100 transition hover:bg-teal-50/60"
                @click="openApplication(row)"
              >
                <td class="px-4 py-4">
                  <div class="font-mono font-bold text-slate-800">{{ row.name }}</div>
                  <div class="mt-0.5 text-xs text-slate-500">{{ formatDate(row.modified || row.creation) }}</div>
                </td>
                <td class="px-4 py-4">
                  <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-teal-100 text-sm font-black text-teal-700">
                      {{ initials(row.borrower_name) }}
                    </div>
                    <div class="min-w-0">
                      <div class="truncate font-bold text-slate-800">{{ row.borrower_name || row.borrower || row.name }}</div>
                      <div class="text-xs text-slate-500">{{ __('Individual borrower') }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-4 text-right font-mono text-slate-700">{{ formatCurrency(row.requested_amount) }}</td>
                <td class="px-4 py-4 text-slate-700">{{ row.facility_type || __('Credit Facility') }}</td>
                <td class="px-4 py-4">
                  <Badge :label="row.status || 'Pending Review'" :theme="statusTheme(row.status)" variant="subtle" />
                </td>
                <td class="px-4 py-4">
                  <div class="font-semibold text-slate-700">{{ row.employer_name || '-' }}</div>
                  <Badge v-if="row.public_company_ticker" :label="row.public_company_ticker" theme="teal" variant="subtle" />
                </td>
                <td class="px-4 py-4 font-bold text-slate-800">{{ row.risk_grade || __('Unrated') }}</td>
              </tr>
              <tr v-if="!applications.loading && rows.length === 0">
                <td colspan="7" class="px-4 py-12 text-center text-sm text-slate-400">{{ __('No credit applications found') }}</td>
              </tr>
              <tr v-if="applications.loading">
                <td colspan="7" class="px-4 py-12 text-center text-sm text-slate-400">{{ __('Loading application table...') }}</td>
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

const applications = createResource({
  url: 'crm.api.credit.get_credit_analysis_table',
  auto: true,
  makeParams() {
    return { query: query.value, limit: 200 }
  },
})

const rows = computed(() => applications.data || [])
const totalRequested = computed(() => rows.value.reduce((sum, row) => sum + Number(row.requested_amount || 0), 0))
const withTicker = computed(() => rows.value.filter((row) => row.public_company_ticker).length)

function openApplication(row) {
  router.push({ name: 'Credit Analysis Detail', params: { applicationId: row.name } })
}

function statusCount(status) {
  return rows.value.filter((row) => row.status === status).length
}

function statusTheme(status) {
  if (status === 'Approved') return 'green'
  if (status === 'Rejected') return 'red'
  if (status === 'Pending Review') return 'orange'
  return 'teal'
}

function initials(value) {
  return String(value || 'CA').slice(0, 2).toUpperCase()
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
  searchTimer = setTimeout(() => applications.fetch(), 250)
})

usePageMeta(() => ({ title: 'Credit Analysis' }))

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
