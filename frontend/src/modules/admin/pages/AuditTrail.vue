<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #7c3aed, #c084fc)"
          >
            <LucideClock class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Audit Trail') }}
            </h1>
            <p class="truncate text-xs text-crm-muted">
              {{ __('Activity Log') }}
            </p>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            :label="__('Refresh')"
            variant="subtle"
            :loading="loading"
            @click="fetchActivityLogs"
          >
            <template #prefix>
              <LucideRefreshCw class="h-4 w-4" />
            </template>
          </Button>
          <Button
            :label="__('Open Desk View')"
            variant="outline"
            @click="openDeskView"
          >
            <template #prefix>
              <LucideExternalLink class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 p-6">
      <div class="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="card in summaryCards"
          :key="card.label"
          class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm"
        >
          <div class="text-xs font-medium text-crm-muted">
            {{ __(card.label) }}
          </div>
          <div class="mt-2 text-2xl font-semibold text-crm-text">
            {{ card.value }}
          </div>
        </div>
      </div>

      <div
        class="mb-4 flex flex-col gap-3 rounded-[14px] border border-crm-border bg-white p-4 shadow-sm lg:flex-row lg:items-center"
      >
        <div class="relative min-w-0 flex-1">
          <LucideSearch
            class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-crm-muted"
          />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search subject, user, document, or IP address...')"
            class="h-9 w-full rounded-[10px] border border-crm-border bg-white pl-9 pr-4 text-sm outline-none transition-all focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20"
          />
        </div>
        <select
          v-model="operationFilter"
          class="h-9 rounded-[10px] border border-crm-border bg-white px-3 text-sm text-crm-text outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20"
        >
          <option value="">{{ __('All Operations') }}</option>
          <option
            v-for="operation in operationOptions"
            :key="operation"
            :value="operation"
          >
            {{ operation }}
          </option>
        </select>
        <select
          v-model="statusFilter"
          class="h-9 rounded-[10px] border border-crm-border bg-white px-3 text-sm text-crm-text outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20"
        >
          <option value="">{{ __('All Status') }}</option>
          <option v-for="status in statusOptions" :key="status" :value="status">
            {{ status }}
          </option>
        </select>
      </div>

      <div class="overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
        <div
          class="grid grid-cols-[minmax(220px,1.4fr)_minmax(120px,0.8fr)_minmax(150px,0.9fr)_minmax(140px,0.8fr)_minmax(170px,0.8fr)] gap-4 border-b border-crm-border bg-surface-gray-2 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-crm-muted"
        >
          <div>{{ __('Activity') }}</div>
          <div>{{ __('Operation') }}</div>
          <div>{{ __('User') }}</div>
          <div>{{ __('Reference') }}</div>
          <div>{{ __('Date') }}</div>
        </div>

        <div v-if="loading" class="divide-y divide-crm-border">
          <div
            v-for="index in 8"
            :key="index"
            class="grid grid-cols-[minmax(220px,1.4fr)_minmax(120px,0.8fr)_minmax(150px,0.9fr)_minmax(140px,0.8fr)_minmax(170px,0.8fr)] gap-4 px-4 py-4"
          >
            <div class="h-4 animate-pulse rounded bg-surface-gray-3" />
            <div class="h-4 animate-pulse rounded bg-surface-gray-3" />
            <div class="h-4 animate-pulse rounded bg-surface-gray-3" />
            <div class="h-4 animate-pulse rounded bg-surface-gray-3" />
            <div class="h-4 animate-pulse rounded bg-surface-gray-3" />
          </div>
        </div>

        <div
          v-else-if="filteredLogs.length"
          class="divide-y divide-crm-border"
        >
          <div
            v-for="log in filteredLogs"
            :key="log.name"
            class="grid grid-cols-[minmax(220px,1.4fr)_minmax(120px,0.8fr)_minmax(150px,0.9fr)_minmax(140px,0.8fr)_minmax(170px,0.8fr)] gap-4 px-4 py-4 text-sm hover:bg-crm-surface/40"
          >
            <div class="min-w-0">
              <div class="truncate font-medium text-crm-text">
                {{ log.subject || __('No subject') }}
              </div>
              <div class="mt-1 line-clamp-1 text-xs text-crm-muted">
                {{ stripHtml(log.content) || log.ip_address || log.name }}
              </div>
            </div>
            <div class="flex items-start">
              <Badge
                :label="log.operation || __('Activity')"
                variant="subtle"
                :theme="operationTheme(log.operation)"
              />
            </div>
            <div class="min-w-0">
              <div class="truncate text-crm-text">
                {{ log.full_name || log.user || log.owner || '-' }}
              </div>
              <div v-if="log.ip_address" class="truncate text-xs text-crm-muted">
                {{ log.ip_address }}
              </div>
            </div>
            <div class="min-w-0">
              <div class="truncate text-crm-text">
                {{ log.reference_doctype || log.link_doctype || '-' }}
              </div>
              <div class="truncate text-xs text-crm-muted">
                {{ log.reference_name || log.link_name || '' }}
              </div>
            </div>
            <div class="text-sm text-crm-muted">
              {{ formatDate(log.communication_date || log.creation) }}
            </div>
          </div>
        </div>

        <div v-else class="flex flex-col items-center justify-center py-20">
          <LucideFileSearch class="mb-4 h-12 w-12 text-crm-muted/40" />
          <h3 class="text-base font-semibold text-crm-text">
            {{ __('No audit activity found') }}
          </h3>
          <p class="mt-1 text-sm text-crm-muted">
            {{ __('Try changing the search or filter criteria.') }}
          </p>
        </div>
      </div>

      <ErrorMessage
        v-if="errorMessage"
        class="mt-4"
        :message="errorMessage"
      />
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LucideClock from '~icons/lucide/clock'
import LucideExternalLink from '~icons/lucide/external-link'
import LucideFileSearch from '~icons/lucide/file-search'
import LucideRefreshCw from '~icons/lucide/refresh-cw'
import LucideSearch from '~icons/lucide/search'
import { Badge, Button, ErrorMessage, call, usePageMeta } from 'frappe-ui'
import { computed, onMounted, ref } from 'vue'

const loading = ref(false)
const activityLogs = ref([])
const searchQuery = ref('')
const operationFilter = ref('')
const statusFilter = ref('')
const errorMessage = ref('')

const activityFields = [
  'name',
  'creation',
  'owner',
  'subject',
  'content',
  'communication_date',
  'operation',
  'status',
  'reference_doctype',
  'reference_name',
  'link_doctype',
  'link_name',
  'user',
  'full_name',
  'ip_address',
]

async function fetchActivityLogs() {
  loading.value = true
  errorMessage.value = ''
  try {
    activityLogs.value = await call('frappe.client.get_list', {
      doctype: 'Activity Log',
      fields: activityFields,
      order_by: 'creation desc',
      limit_page_length: 100,
    })
  } catch (error) {
    console.error('Unable to load Activity Log', error)
    errorMessage.value =
      error?.messages?.[0] ||
      error?.message ||
      __('Unable to load Activity Log. Check your permissions.')
  } finally {
    loading.value = false
  }
}

const operationOptions = computed(() =>
  uniqueValues(activityLogs.value.map((log) => log.operation)),
)

const statusOptions = computed(() =>
  uniqueValues(activityLogs.value.map((log) => log.status)),
)

const filteredLogs = computed(() => {
  let logs = activityLogs.value || []

  if (operationFilter.value) {
    logs = logs.filter((log) => log.operation === operationFilter.value)
  }

  if (statusFilter.value) {
    logs = logs.filter((log) => log.status === statusFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    logs = logs.filter((log) =>
      [
        log.subject,
        log.content,
        log.user,
        log.full_name,
        log.owner,
        log.reference_doctype,
        log.reference_name,
        log.link_doctype,
        log.link_name,
        log.ip_address,
      ]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(query)),
    )
  }

  return logs
})

const summaryCards = computed(() => {
  const logs = activityLogs.value || []
  const today = new Date().toDateString()
  return [
    { label: 'Loaded Logs', value: logs.length },
    {
      label: 'Today',
      value: logs.filter(
        (log) => new Date(log.communication_date || log.creation).toDateString() === today,
      ).length,
    },
    { label: 'Operations', value: operationOptions.value.length },
    { label: 'Users', value: uniqueValues(logs.map((log) => log.user || log.owner)).length },
  ]
})

function uniqueValues(values) {
  return [...new Set(values.filter(Boolean))].sort()
}

function stripHtml(value) {
  if (!value) return ''
  return String(value).replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()
}

function formatDate(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function operationTheme(operation) {
  const normalized = String(operation || '').toLowerCase()
  if (normalized.includes('login') || normalized.includes('success')) return 'green'
  if (normalized.includes('error') || normalized.includes('fail')) return 'red'
  if (normalized.includes('delete') || normalized.includes('cancel')) return 'orange'
  return 'blue'
}

function openDeskView() {
  window.location.href = '/app/activity-log'
}

onMounted(fetchActivityLogs)

usePageMeta(() => ({ title: __('Audit Trail') }))
</script>
