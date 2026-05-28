<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-4 pt-3">
      <div class="flex items-center justify-between">
        <div class="min-w-0 flex-1">
          <p class="text-xs text-crm-text-secondary">
            {{ __(greetingText) }}
          </p>
          <h1 class="text-xl font-semibold text-crm-text truncate">
            {{ displayName }}
          </h1>
        </div>
        <div
          class="flex size-10 shrink-0 items-center justify-center rounded-full bg-crm-teal text-sm font-semibold text-white"
        >
          {{ initials }}
        </div>
      </div>
    </div>

    <div v-if="error" class="rounded-xl bg-red-50 border border-red-200 p-4 mx-4 mb-4">
      <div class="flex items-center gap-2">
        <FeatherIcon name="alert-triangle" class="size-4 text-red-500 shrink-0" />
        <p class="text-xs text-red-600 flex-1">{{ error }}</p>
        <button class="text-xs font-medium text-red-700" @click="loadData">{{ __('Coba Lagi') }}</button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pt-4 pb-28 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <div
          v-for="kpi in kpis"
          :key="kpi.label"
          class="rounded-xl bg-white p-4 shadow-sm border border-crm-border"
        >
          <div class="flex items-center gap-2 mb-2.5">
            <div
              class="flex size-8 items-center justify-center rounded-lg"
              :class="kpi.bg"
            >
              <FeatherIcon
                :name="kpi.icon"
                class="size-4"
                :class="kpi.color"
              />
            </div>
          </div>
          <p class="text-2xl font-bold text-crm-text">
            {{ kpi.loading ? '...' : kpi.value }}
          </p>
          <p class="text-xs text-crm-text-secondary mt-0.5">
            {{ __(kpi.label) }}
          </p>
        </div>
      </div>

      <div
        class="rounded-xl bg-white p-4 shadow-sm border border-crm-border"
      >
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-crm-text">
            {{ __('Aktivitas Terbaru') }}
          </h2>
          <button
            v-if="notifications.data?.length"
            class="text-xs font-medium text-crm-teal"
            @click="viewAllNotifications"
          >
            {{ __('Lihat Semua') }}
          </button>
        </div>

        <div
          v-if="notifications.loading"
          class="flex items-center justify-center py-8"
        >
          <FeatherIcon
            name="loader"
            class="size-5 animate-spin text-crm-muted"
          />
        </div>

        <template v-else-if="notifications.data?.length">
          <div
            v-for="(item, i) in recentActivities"
            :key="item.name || i"
            class="flex items-start gap-3 py-2 first:pt-0 last:pb-0"
          >
            <div
              class="flex size-8 shrink-0 items-center justify-center rounded-lg"
              :class="getActivityBg(item)"
            >
              <FeatherIcon
                :name="getActivityIcon(item)"
                class="size-4"
                :class="getActivityColor(item)"
              />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-crm-text truncate">
                {{ item.subject || item.type || '-' }}
              </p>
              <p class="text-xs text-crm-text-secondary mt-0.5">
                {{ timeAgo(item.creation) }}
              </p>
            </div>
          </div>
        </template>

        <div v-else class="py-8 text-center">
          <FeatherIcon
            name="bell"
            class="size-8 text-crm-muted mx-auto mb-2"
          />
          <p class="text-sm text-crm-text-secondary">
            {{ __('Belum ada aktivitas') }}
          </p>
        </div>
      </div>

      <div
        class="rounded-xl bg-white p-4 shadow-sm border border-crm-border"
      >
        <h2 class="text-sm font-semibold text-crm-text mb-3">
          {{ __('Quick Actions') }}
        </h2>
        <div class="grid grid-cols-3 gap-3">
          <button
            v-for="action in quickActions"
            :key="action.label"
            class="flex flex-col items-center gap-1.5 rounded-xl p-3 transition-colors active:scale-95"
            :class="action.bg"
            @click="action.onClick"
          >
            <FeatherIcon
              :name="action.icon"
              class="size-5"
              :class="action.color"
            />
            <span
              class="text-[10px] font-medium text-crm-text text-center leading-tight"
            >
              {{ __(action.label) }}
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { FeatherIcon, createListResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'
import { notifications } from '@/stores/notifications'
import { timeAgo } from '@/utils'

const router = useRouter()
const session = sessionStore()
const { getUser } = usersStore()

const userInfo = computed(() => getUser(session.user.value))

const displayName = computed(() => {
  const u = userInfo.value
  return u?.full_name || u?.name || session.user.value || 'User'
})

const initials = computed(() => {
  const name = displayName.value
  if (!name) return 'U'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
})

const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Selamat Pagi'
  if (hour < 15) return 'Selamat Siang'
  if (hour < 18) return 'Selamat Sore'
  return 'Selamat Malam'
})

const todayLeads = createListResource({
  type: 'list',
  doctype: 'CRM Lead',
  fields: ['name'],
  filters: [['creation', '>=', new Date().toISOString().split('T')[0]]],
  pageLength: 0,
  auto: false,
})

const openLeads = createListResource({
  type: 'list',
  doctype: 'CRM Lead',
  fields: ['name'],
  filters: [['status', 'not in', ['Converted', 'Lost', 'Rejected']]],
  pageLength: 0,
  auto: false,
})

const activeDeals = createListResource({
  type: 'list',
  doctype: 'CRM Deal',
  fields: ['name'],
  filters: [['status', 'not in', ['Closed Won', 'Closed Lost']]],
  pageLength: 0,
  auto: false,
})

const kpis = computed(() => [
  {
    label: 'Leads Hari Ini',
    value: todayLeads.data?.length ?? 0,
    icon: 'target',
    bg: 'bg-crm-surface',
    color: 'text-crm-teal',
    loading: todayLeads.loading,
  },
  {
    label: 'Open Leads',
    value: openLeads.data?.length ?? 0,
    icon: 'mail',
    bg: 'bg-blue-50',
    color: 'text-blue-600',
    loading: openLeads.loading,
  },
  {
    label: 'Active Deals',
    value: activeDeals.data?.length ?? 0,
    icon: 'briefcase',
    bg: 'bg-amber-50',
    color: 'text-amber-600',
    loading: activeDeals.loading,
  },
  {
    label: 'Notifications',
    value: notifications.data?.length ?? 0,
    icon: 'bell',
    bg: 'bg-purple-50',
    color: 'text-purple-600',
    loading: notifications.loading,
  },
])

const recentActivities = computed(() => {
  const items = notifications.data || []
  return items.slice(0, 5)
})

function getActivityBg(item) {
  if (!item) return 'bg-crm-surface'
  const type = item.notification_type || ''
  if (type.includes('lead') || type.includes('Lead')) return 'bg-crm-surface'
  if (type.includes('deal') || type.includes('Deal')) return 'bg-amber-50'
  if (type.includes('comment')) return 'bg-blue-50'
  if (type.includes('assign')) return 'bg-purple-50'
  return 'bg-crm-surface'
}

function getActivityIcon(item) {
  if (!item) return 'bell'
  const type = item.notification_type || ''
  if (type.includes('lead') || type.includes('Lead')) return 'user-plus'
  if (type.includes('deal') || type.includes('Deal')) return 'briefcase'
  if (type.includes('comment')) return 'message-square'
  if (type.includes('assign')) return 'user-check'
  return 'bell'
}

function getActivityColor(item) {
  if (!item) return 'text-crm-teal'
  const type = item.notification_type || ''
  if (type.includes('lead') || type.includes('Lead')) return 'text-crm-teal'
  if (type.includes('deal') || type.includes('Deal')) return 'text-amber-600'
  if (type.includes('comment')) return 'text-blue-600'
  if (type.includes('assign')) return 'text-purple-600'
  return 'text-crm-teal'
}

function viewAllNotifications() {
  router.push({ name: 'Mobile Push Notifications' })
}

const quickActions = [
  {
    label: 'New Lead',
    icon: 'user-plus',
    bg: 'bg-crm-surface',
    color: 'text-crm-teal',
    onClick: () => router.push({ name: 'Mobile Lead Capture' }),
  },
  {
    label: 'Scan Dokumen',
    icon: 'camera',
    bg: 'bg-blue-50',
    color: 'text-blue-600',
    onClick: () => router.push({ name: 'Document Scanner' }),
  },
  {
    label: 'Visit Check-In',
    icon: 'map-pin',
    bg: 'bg-green-50',
    color: 'text-green-600',
    onClick: () => router.push({ name: 'Visit Check-In/Out GPS' }),
  },
  {
    label: 'Customers',
    icon: 'users',
    bg: 'bg-purple-50',
    color: 'text-purple-600',
    onClick: () => router.push({ name: 'My Customers Mobile' }),
  },
  {
    label: 'Calculator',
    icon: 'percent',
    bg: 'bg-amber-50',
    color: 'text-amber-600',
    onClick: () => router.push({ name: 'Mobile Calculator Pricing' }),
  },
  {
    label: 'AI Assistant',
    icon: 'zap',
    bg: 'bg-rose-50',
    color: 'text-rose-600',
    onClick: () => router.push({ name: 'AI Assistant Mobile' }),
  },
]

const error = ref('')

async function loadData() {
  error.value = ''
  try {
    await Promise.all([
      todayLeads.reload(),
      openLeads.reload(),
      activeDeals.reload(),
      notifications.reload(),
    ])
  } catch (err) {
    error.value = err.messages?.[0] || __('Gagal memuat data dashboard')
  }
}

onMounted(loadData)
</script>
