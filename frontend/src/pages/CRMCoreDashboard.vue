<template>
  <div class="flex flex-col h-full overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #008C95, #D9F3F4)"
          >
            <LucideLayoutDashboard class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-lg font-semibold text-ink-gray-9">
            {{ __('CRM Dashboard') }}
          </h1>
        </div>
      </template>
      <template #right-header>
        <Button
          :label="__('Refresh')"
          :iconLeft="LucideRefreshCcw"
          @click="refreshAll"
        />
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto crm-dashboard-bg">
      <div class="crm-dashboard-shell m-4">
        <div class="crm-main-content">
          <!-- Filter Bar -->
          <DashboardFilterBar
            v-model="activeFilter"
            :user="filterUser"
            @update:user="filterUser = $event"
          />

          <!-- Metric Cards -->
          <div class="crm-metrics-grid mt-4">
            <MetricCard
              v-for="(metric, idx) in metrics"
              :key="metric.label"
              :value="metric.value"
              :label="metric.label"
              :icon="metric.icon"
              :accentColor="metric.color"
              :style="{ animationDelay: `${idx * 80}ms` }"
              class="crm-animate-in"
            />
          </div>

          <!-- Analytics Section -->
          <div class="crm-analytics-grid">
            <GoalsGaugeCard
              :value="goalsValue"
              :target="goalsTarget"
              class="crm-animate-in"
              style="animation-delay: 500ms"
            />
            <LeadSourceCard
              class="crm-animate-in"
              style="animation-delay: 600ms"
            />
          </div>

          <!-- Bottom Section -->
          <div class="crm-bottom-grid">
            <UpcomingMeetingsCard
              class="crm-animate-in"
              style="animation-delay: 700ms"
            />
            <LatestLeadsCard
              class="crm-animate-in"
              style="animation-delay: 800ms"
            />
            <MostLeadChannelsCard
              class="crm-animate-in"
              style="animation-delay: 900ms"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import DashboardFilterBar from '@/components/Dashboard/DashboardFilterBar.vue'
import MetricCard from '@/components/Dashboard/MetricCard.vue'
import GoalsGaugeCard from '@/components/Dashboard/GoalsGaugeCard.vue'
import LeadSourceCard from '@/components/Dashboard/LeadSourceCard.vue'
import UpcomingMeetingsCard from '@/components/Dashboard/UpcomingMeetingsCard.vue'
import LatestLeadsCard from '@/components/Dashboard/LatestLeadsCard.vue'
import MostLeadChannelsCard from '@/components/Dashboard/MostLeadChannelsCard.vue'
import LucideLayoutDashboard from '~icons/lucide/layout-dashboard'
import LucideRefreshCcw from '~icons/lucide/refresh-ccw'
import { usePageMeta, createResource } from 'frappe-ui'
import { ref, computed } from 'vue'

const activeFilter = ref('Monthly')
const filterUser = ref(null)

// Dashboard data from API
const dashboardData = createResource({
  url: 'crm.api.dashboard.get_dashboard',
  makeParams() {
    return {
      from_date: getFromDate(),
      to_date: getToDate(),
      user: filterUser.value,
    }
  },
  auto: true,
})

function getFromDate() {
  const now = new Date()
  const periodMap = {
    Today: 0,
    Yesterday: 1,
    Weekly: 7,
    Monthly: 30,
  }
  const days = periodMap[activeFilter.value] ?? 30
  const from = new Date(now)
  from.setDate(from.getDate() - days)
  return from.toISOString().split('T')[0]
}

function getToDate() {
  return new Date().toISOString().split('T')[0]
}

function refreshAll() {
  dashboardData.reload()
}

// Metrics computed from API data or fallback
const metrics = computed(() => {
  const data = dashboardData.data
  return [
    {
      value: data?.total_leads ?? '7,089',
      label: __('New Leads'),
      icon: 'user-plus',
      color: 'crm-teal',
    },
    {
      value: data?.total_customers ?? '65',
      label: __('New Customers'),
      icon: 'users',
      color: 'crm-green',
    },
    {
      value: data?.total_invoices ?? '628',
      label: __('Sent Invoices'),
      icon: 'file-text',
      color: 'crm-blue',
    },
    {
      value: data?.current_tasks ?? '5',
      label: __('Current Tasks'),
      icon: 'check-square',
      color: 'crm-purple',
    },
    {
      value: data?.lead_tasks ?? '120',
      label: __('Leads Tasks'),
      icon: 'clipboard-list',
      color: 'crm-pink',
    },
    {
      value: data?.overdue_tasks ?? '48',
      label: __('Overdue Task'),
      icon: 'alert-circle',
      color: 'crm-teal',
    },
  ]
})

const goalsValue = computed(() => dashboardData.data?.goals_value ?? 7580)
const goalsTarget = computed(() => dashboardData.data?.goals_target ?? 7000)

usePageMeta(() => {
  return { title: __('CRM Dashboard') }
})
</script>
