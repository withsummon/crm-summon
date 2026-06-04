<template>
  <div class="flex h-full flex-col bg-white overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #ff6600, #006699)"
          >
            <LucideWorkflow class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-gray-800">
              {{ __('Credit Flow Designer') }}
            </h1>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <div class="relative">
            <LucideSearch
              class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-400"
            />
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="__('Search flows...')"
              class="w-56 rounded-lg border border-gray-200 bg-gray-50 py-1.5 pl-8 pr-3 text-sm outline-none transition-colors brand-focus focus:bg-white"
            />
          </div>
          <Button
            :label="__('New Flow')"
            variant="solid"
            theme="gray"
            class="btn-brand-primary"
            @click="createNewFlow"
          >
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <!-- Filter Bar -->
    <div class="flex items-center gap-3 border-b border-gray-200 px-5 py-2.5">
      <button
        v-for="filter in statusFilters"
        :key="filter.value"
        class="rounded-full px-3 py-1 text-xs font-medium transition-colors"
        :class="
          activeFilter === filter.value
            ? 'bg-primary-100 text-primary-700'
            : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
        "
        @click="activeFilter = filter.value"
      >
        {{ __(filter.label) }}
        <span
          v-if="filter.count > 0"
          class="ml-1 text-[10px]"
          :class="activeFilter === filter.value ? 'text-secondary-500' : 'text-gray-400'"
        >
          {{ filter.count }}
        </span>
      </button>
    </div>

    <!-- Flow List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="filteredFlows.length > 0" class="divide-y divide-gray-100">
        <div
          v-for="flow in filteredFlows"
          :key="flow.id"
          class="group flex cursor-pointer items-center gap-4 px-5 py-4 transition-colors hover:bg-gray-50/80"
          @click="openFlow(flow)"
        >
          <!-- Status indicator bar -->
          <div
            class="h-12 w-1 rounded-full"
            :class="getStatusBarColor(flow.status)"
          />

          <!-- Flow info -->
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <h3 class="truncate text-sm font-semibold text-gray-800">
                {{ flow.title }}
              </h3>
              <Badge
                :label="flow.status"
                :theme="getStatusTheme(flow.status)"
                :class="{ 'badge-brand-primary': flow.status === 'Published' }"
                variant="subtle"
                size="sm"
              />
              <span class="text-[11px] text-gray-400">
                v{{ flow.version }}
              </span>
            </div>
            <p class="mt-0.5 truncate text-xs text-gray-500">
              {{ flow.description }}
            </p>
          </div>

          <!-- Product type -->
          <div v-if="flow.productType" class="hidden items-center gap-1.5 sm:flex">
            <LucidePackage class="h-3.5 w-3.5 text-gray-400" />
            <span class="text-xs text-gray-500">{{ flow.productType }}</span>
          </div>

          <!-- Active executions -->
          <div class="hidden items-center gap-1.5 md:flex">
            <LucideActivity class="h-3.5 w-3.5 text-gray-400" />
            <span class="text-xs text-gray-500">
              {{ flow.activeExecutions }} {{ __('active') }}
            </span>
          </div>

          <!-- Last modified -->
          <div class="hidden text-xs text-gray-400 lg:block">
            {{ flow.lastModified }}
          </div>

          <!-- Actions -->
          <Dropdown :options="getFlowActions(flow)">
            <template v-slot="{ open }">
              <Button
                variant="ghost"
                class="opacity-0 group-hover:opacity-100"
                @click.stop="open"
              >
                <LucideMoreVertical class="h-4 w-4 text-gray-400" />
              </Button>
            </template>
          </Dropdown>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else
        class="flex flex-col items-center justify-center py-20 text-center"
      >
        <div
          class="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-100 to-primary-200"
        >
          <LucideWorkflow class="h-8 w-8 text-secondary-600" />
        </div>
        <h3 class="mt-4 text-base font-semibold text-gray-800">
          {{ __('No credit flows yet') }}
        </h3>
        <p class="mt-1 max-w-sm text-sm text-gray-500">
          {{ __('Design your first credit application flow to dynamically control forms, approvals, and routing.') }}
        </p>
        <Button
          variant="solid"
          theme="gray"
          class="mt-4 btn-brand-primary"
          :label="__('Create Your First Flow')"
          @click="createNewFlow"
        >
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, Dropdown, usePageMeta } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

import LucideWorkflow from '~icons/lucide/workflow'
import LucideSearch from '~icons/lucide/search'
import LucidePlus from '~icons/lucide/plus'
import LucidePackage from '~icons/lucide/package'
import LucideActivity from '~icons/lucide/activity'
import LucideMoreVertical from '~icons/lucide/more-vertical'

const router = useRouter()
const searchQuery = ref('')
const activeFilter = ref('all')

usePageMeta(() => ({ title: __('Credit Flow Designer') }))

// Mock data (until backend DocTypes are created)
const flows = ref([
  {
    id: 'CF-001',
    title: 'General Credit Application Flow',
    description:
      'Standard end-to-end flow for all credit applications including KYC, scoring, analysis, and multi-level approval.',
    status: 'Published',
    productType: 'All Products',
    version: 3,
    activeExecutions: 12,
    lastModified: '2 hours ago',
  },
  {
    id: 'CF-002',
    title: 'Pre-Approved TPI Flow',
    description:
      'Simplified flow for pre-approved TPI applications with skip gates and minimal data collection.',
    status: 'Published',
    productType: 'TPI',
    version: 1,
    activeExecutions: 5,
    lastModified: '1 day ago',
  },
  {
    id: 'CF-003',
    title: 'High-Value Corporate Flow',
    description:
      'Complex flow for corporate credit >50B with director committee approval, collateral validation, and extended KYC.',
    status: 'Draft',
    productType: 'Corporate',
    version: 0,
    activeExecutions: 0,
    lastModified: '3 days ago',
  },
])

const statusFilters = computed(() => [
  { label: 'All', value: 'all', count: flows.value.length },
  {
    label: 'Published',
    value: 'Published',
    count: flows.value.filter((f) => f.status === 'Published').length,
  },
  {
    label: 'Draft',
    value: 'Draft',
    count: flows.value.filter((f) => f.status === 'Draft').length,
  },
  {
    label: 'Archived',
    value: 'Archived',
    count: flows.value.filter((f) => f.status === 'Archived').length,
  },
])

const filteredFlows = computed(() => {
  let result = flows.value

  if (activeFilter.value !== 'all') {
    result = result.filter((f) => f.status === activeFilter.value)
  }

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(
      (f) =>
        f.title.toLowerCase().includes(q) ||
        f.description.toLowerCase().includes(q)
    )
  }

  return result
})

function getStatusTheme(status) {
  if (status === 'Published') return 'orange'
  if (status === 'Draft') return 'gray'
  if (status === 'Archived') return 'orange'
  return 'gray'
}

function getStatusBarColor(status) {
  if (status === 'Published') return 'bg-primary-400'
  if (status === 'Draft') return 'bg-gray-300'
  if (status === 'Archived') return 'bg-amber-400'
  return 'bg-gray-300'
}

function createNewFlow() {
  router.push({ name: 'Credit Flow New' })
}

function openFlow(flow) {
  router.push({ name: 'Credit Flow Detail', params: { flowId: flow.id } })
}

function getFlowActions(flow) {
  return [
    {
      label: __('Edit'),
      icon: 'edit',
      onClick: () => openFlow(flow),
    },
    {
      label: __('Clone'),
      icon: 'copy',
      onClick: () => cloneFlow(flow),
    },
    {
      label: __('Monitor'),
      icon: 'activity',
      onClick: () =>
        router.push({
          name: 'Credit Flow Monitor',
          params: { flowId: flow.id },
        }),
    },
    {
      label: flow.status === 'Published' ? __('Archive') : __('Publish'),
      icon: flow.status === 'Published' ? 'archive' : 'send',
      onClick: () => toggleStatus(flow),
    },
  ]
}

function cloneFlow(flow) {
  const cloned = {
    ...flow,
    id: `CF-${String(flows.value.length + 1).padStart(3, '0')}`,
    title: `${flow.title} (Copy)`,
    status: 'Draft',
    version: 0,
    activeExecutions: 0,
    lastModified: 'Just now',
  }
  flows.value.push(cloned)
}

function toggleStatus(flow) {
  flow.status = flow.status === 'Published' ? 'Archived' : 'Published'
}
</script>
