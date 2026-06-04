<template>
  <div class="flex h-full flex-col bg-white overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <button
            class="flex h-7 w-7 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
            @click="router.push({ name: 'Credit Flow Designer' })"
          >
            <LucideArrowLeft class="h-4 w-4" />
          </button>
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #ff6600, #006699)"
          >
            <LucideActivity class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-gray-800">
              {{ __('Flow Monitor') }}
            </h1>
            <p class="text-xs text-gray-500">{{ flowId }}</p>
          </div>
        </div>
      </template>
      <template #right-header>
        <Button
          :label="__('Back to Designer')"
          variant="outline"
          @click="router.push({ name: 'Credit Flow Detail', params: { flowId } })"
        >
          <template #prefix>
            <LucideEdit class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Stats Bar -->
    <div class="grid grid-cols-4 gap-4 border-b border-gray-200 px-5 py-4">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="rounded-xl border p-4 transition-shadow hover:shadow-sm"
        :class="stat.borderClass"
      >
        <div class="flex items-center gap-2">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg"
            :class="stat.iconBg"
          >
            <component :is="stat.icon" class="h-4 w-4" :class="stat.iconColor" />
          </div>
          <div>
            <div class="text-2xl font-bold" :class="stat.valueColor">
              {{ stat.value }}
            </div>
            <div class="text-xs text-gray-500">{{ __(stat.label) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto px-5 py-4 space-y-6">
      <!-- Active Executions Table -->
      <div>
        <h2 class="mb-3 text-sm font-semibold text-gray-700">
          {{ __('Active Executions') }}
        </h2>
        <div class="rounded-xl border border-gray-200 overflow-hidden">
          <table class="w-full">
            <thead>
              <tr class="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <th class="px-4 py-3">{{ __('Application') }}</th>
                <th class="px-4 py-3">{{ __('Current Stage') }}</th>
                <th class="px-4 py-3">{{ __('Assignee') }}</th>
                <th class="px-4 py-3">{{ __('Status') }}</th>
                <th class="px-4 py-3">{{ __('SLA') }}</th>
                <th class="px-4 py-3">{{ __('Time in Stage') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr
                v-for="exec in executions"
                :key="exec.id"
                class="transition-colors hover:bg-gray-50/60"
              >
                <td class="px-4 py-3 text-sm font-medium text-gray-800">
                  {{ exec.applicationId }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600">
                  {{ exec.currentStage }}
                </td>
                <td class="px-4 py-3 text-sm text-gray-600">
                  {{ exec.assignee }}
                </td>
                <td class="px-4 py-3">
                  <Badge
                    :label="exec.status"
                    :theme="getExecStatusTheme(exec.status)"
                    :class="{ 'badge-brand-primary': exec.status === 'Completed' }"
                    variant="subtle"
                    size="sm"
                  />
                </td>
                <td class="px-4 py-3">
                  <Badge
                    :label="exec.slaStatus"
                    :theme="getSLATheme(exec.slaStatus)"
                    :class="{ 'badge-brand-primary': exec.slaStatus === 'On Time' }"
                    variant="subtle"
                    size="sm"
                  />
                </td>
                <td class="px-4 py-3 text-sm text-gray-500">
                  {{ exec.timeInStage }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recent Activity Timeline -->
      <div>
        <h2 class="mb-3 text-sm font-semibold text-gray-700">
          {{ __('Recent Activity') }}
        </h2>
        <div class="space-y-0">
          <div
            v-for="(event, idx) in recentActivity"
            :key="idx"
            class="flex gap-3 pb-4"
          >
            <!-- Timeline dot + line -->
            <div class="flex flex-col items-center">
              <div
                class="mt-1 h-2.5 w-2.5 rounded-full ring-2 ring-white"
                :class="getEventDotColor(event.type)"
              />
              <div
                v-if="idx < recentActivity.length - 1"
                class="mt-1 w-px flex-1 bg-gray-200"
              />
            </div>

            <!-- Event content -->
            <div class="min-w-0 flex-1 pb-2">
              <div class="flex items-center gap-2">
                <Badge
                  :label="event.type"
                  :theme="getEventTheme(event.type)"
                  :class="{ 'badge-brand-primary': event.type === 'Approval' }"
                  variant="subtle"
                  size="sm"
                />
                <span class="text-xs text-gray-400">{{ event.timestamp }}</span>
              </div>
              <p class="mt-1 text-sm text-gray-600">{{ event.description }}</p>
              <p class="mt-0.5 text-xs text-gray-400">
                {{ __('by') }} {{ event.user }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, usePageMeta } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'

import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideActivity from '~icons/lucide/activity'
import LucideEdit from '~icons/lucide/edit'
import LucidePlay from '~icons/lucide/play'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideXCircle from '~icons/lucide/x-circle'
import LucideClock from '~icons/lucide/clock'

const props = defineProps({
  flowId: { type: String, required: true },
})

const router = useRouter()

usePageMeta(() => ({ title: __('Flow Monitor') }))

// Mock stats
const stats = ref([
  {
    label: 'Active',
    value: 3,
    icon: LucidePlay,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    valueColor: 'text-blue-700',
    borderClass: 'border-blue-100',
  },
  {
    label: 'Completed',
    value: 45,
    icon: LucideCheckCircle,
    iconBg: 'bg-primary-100',
    iconColor: 'text-primary-600',
    valueColor: 'text-primary-700',
    borderClass: 'border-primary-100',
  },
  {
    label: 'Failed',
    value: 2,
    icon: LucideXCircle,
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    valueColor: 'text-red-700',
    borderClass: 'border-red-100',
  },
  {
    label: 'Avg Processing',
    value: '4.2d',
    icon: LucideClock,
    iconBg: 'bg-gray-100',
    iconColor: 'text-gray-600',
    valueColor: 'text-gray-700',
    borderClass: 'border-gray-100',
  },
])

// Mock executions
const executions = ref([
  {
    id: 'EX-001',
    applicationId: 'APP-2025-0142',
    currentStage: 'Director Approval',
    assignee: 'Ahmad Faisal',
    status: 'Running',
    slaStatus: 'On Time',
    timeInStage: '2h 15m',
  },
  {
    id: 'EX-002',
    applicationId: 'APP-2025-0139',
    currentStage: 'Risk Review',
    assignee: 'Siti Rahmawati',
    status: 'Running',
    slaStatus: 'Warning',
    timeInStage: '18h 30m',
  },
  {
    id: 'EX-003',
    applicationId: 'APP-2025-0137',
    currentStage: 'Document Validation',
    assignee: 'Budi Santoso',
    status: 'Running',
    slaStatus: 'Breached',
    timeInStage: '2d 4h',
  },
])

// Mock activity
const recentActivity = ref([
  {
    type: 'Approval',
    timestamp: '10 min ago',
    description: 'APP-2025-0140 approved by Regional Manager.',
    user: 'Dewi Anggraini',
  },
  {
    type: 'Delegation',
    timestamp: '1 hour ago',
    description:
      'APP-2025-0142 delegated from Rudi (on leave) to Ahmad Faisal.',
    user: 'System',
  },
  {
    type: 'SLA Breach',
    timestamp: '3 hours ago',
    description:
      'APP-2025-0137 breached 24h SLA at Document Validation stage.',
    user: 'System',
  },
  {
    type: 'Decision',
    timestamp: '5 hours ago',
    description:
      'APP-2025-0139 routed to Risk Review (risk_grade = High).',
    user: 'System',
  },
  {
    type: 'Enter',
    timestamp: '8 hours ago',
    description: 'APP-2025-0142 entered Director Approval stage.',
    user: 'System',
  },
])

function getExecStatusTheme(status) {
  const map = { Running: 'blue', Completed: 'orange', Failed: 'red', Cancelled: 'gray' }
  return map[status] || 'gray'
}

function getSLATheme(status) {
  const map = { 'On Time': 'orange', Warning: 'orange', Breached: 'red' }
  return map[status] || 'gray'
}

function getEventDotColor(type) {
  const map = {
    Approval: 'bg-primary-500',
    Delegation: 'bg-orange-400',
    'SLA Breach': 'bg-red-500',
    Decision: 'bg-amber-500',
    Enter: 'bg-blue-400',
    Exit: 'bg-gray-400',
    Escalation: 'bg-red-400',
  }
  return map[type] || 'bg-gray-400'
}

function getEventTheme(type) {
  const map = {
    Approval: 'orange',
    Delegation: 'orange',
    'SLA Breach': 'red',
    Decision: 'orange',
    Enter: 'blue',
    Exit: 'gray',
    Escalation: 'red',
  }
  return map[type] || 'gray'
}
</script>
