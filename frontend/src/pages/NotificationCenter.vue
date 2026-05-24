<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <header class="flex min-h-[72px] items-center justify-between gap-6 px-10 py-3">
        <div class="flex min-w-0 items-center gap-4">
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px] bg-crm-teal">
            <FeatherIcon name="bell" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-ink-gray-9">{{ __('Notification Center') }}</h1>
          </div>
        </div>
        <div class="flex shrink-0 items-center gap-3">
          <Button variant="outline" size="sm" :label="__('Mark All Read')" @click="markAllAsRead">
            <template #prefix><FeatherIcon name="check-circle" class="h-4 w-4" /></template>
          </Button>
          <Button variant="outline" size="sm" :label="__('Archive All')" @click="archiveAll">
            <template #prefix><FeatherIcon name="archive" class="h-4 w-4" /></template>
          </Button>
          <Button variant="outline" size="sm" :label="__('Preferences')" @click="showPrefs = true">
            <template #prefix><FeatherIcon name="settings" class="h-4 w-4" /></template>
          </Button>
        </div>
      </header>
    </LayoutHeader>

    <div class="shrink-0 overflow-x-auto border-b border-outline-gray-2 bg-surface-white px-10 py-4">
      <div class="flex min-w-max items-center justify-start gap-6">
        <button
          v-for="tab in TABS"
          :key="tab.key"
          class="whitespace-nowrap border-b-2 px-1 py-3 text-base leading-5 transition-colors"
          :class="activeTab === tab.key ? 'border-ink-gray-8 font-medium text-ink-gray-9' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          @click="activeTab = tab.key"
        >
          {{ __(tab.label) }}
          <Badge v-if="tabBadge(tab) != null" :label="String(tabBadge(tab))" variant="subtle" theme="teal" size="sm" class="ml-1" />
        </button>
        <div class="flex-1"></div>
        <div class="relative">
          <FeatherIcon name="search" class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4" />
          <input v-model="query" type="text" :placeholder="__('Search notifications…')" class="h-9 w-64 rounded-md border border-outline-gray-2 bg-white pl-9 pr-3 text-sm text-ink-gray-8 outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20" />
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1">
      <div class="w-full px-10 py-6">
        <div v-if="loading" class="flex h-48 items-center justify-center">
          <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
        </div>
        <div v-else-if="!filteredNotifications.length" class="flex flex-col items-center justify-center py-16 text-center">
          <FeatherIcon name="inbox" class="mb-3 h-8 w-8 text-ink-gray-3" />
          <p class="text-base font-medium text-ink-gray-8">{{ __('No notifications') }}</p>
          <p class="mt-1 text-sm text-ink-gray-5">{{ __('You have no notifications matching the current filter.') }}</p>
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="n in filteredNotifications"
            :key="n.name"
            class="flex cursor-pointer items-start gap-4 rounded-[14px] border border-outline-gray-2 bg-white p-4 shadow-sm hover:bg-surface-gray-1"
            @click="openNotification(n)"
          >
            <div class="mt-0.5 flex items-center gap-2.5">
              <div class="size-[5px] rounded-full" :class="[n.read ? 'bg-transparent' : 'bg-crm-teal']" />
              <UserAvatar :user="n.from_user.name" size="lg" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <span class="font-medium text-ink-gray-9">{{ n.from_user.full_name }}</span>
                <Badge :label="labelize(n.type)" theme="teal" variant="subtle" size="sm" />
                <span v-if="!n.read" class="text-xs text-crm-teal">{{ __('Unread') }}</span>
              </div>
              <p class="mt-1 text-sm text-ink-gray-7" v-html="sanitizeHTML(n.notification_text || n.message || '')" />
              <div class="mt-2 flex items-center gap-3 text-xs text-ink-gray-5">
                <span>{{ formatDate(n.creation) }}</span>
                <span v-if="n.reference_doctype && n.reference_name">
                  {{ n.reference_doctype }} · {{ n.reference_name }}
                </span>
              </div>
            </div>
            <div class="shrink-0 flex items-center gap-1">
              <Button
                v-if="!n.read"
                variant="ghost"
                size="sm"
                :label="__('Mark read')"
                @click.stop="markOneAsRead(n)"
              />
              <Button
                variant="ghost"
                size="sm"
                @click.stop="deleteNotification(n)"
              >
                <template #prefix><FeatherIcon name="trash-2" class="h-4 w-4 text-ink-gray-5" /></template>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Dialog v-model="showPrefs" :options="{ title: __('Notification Preferences') }">
      <template #body-content>
        <div class="space-y-4 text-sm">
          <div v-for="pref in preferences" :key="pref.type" class="flex items-center justify-between rounded-md border border-outline-gray-1 px-3 py-2">
            <div>
              <p class="font-medium text-ink-gray-8">{{ pref.label }}</p>
              <p class="text-xs text-ink-gray-5">{{ pref.description }}</p>
            </div>
            <div class="flex items-center gap-3">
              <label class="flex items-center gap-1 text-xs">
                <input v-model="pref.email" type="checkbox" class="rounded" />
                {{ __('Email') }}
              </label>
              <label class="flex items-center gap-1 text-xs">
                <input v-model="pref.in_app" type="checkbox" class="rounded" />
                {{ __('In-app') }}
              </label>
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="ghost" label="Cancel" @click="close" />
        <Button variant="solid" label="Save" @click="savePreferences().then(close)" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import {
  Badge,
  Button,
  Dialog,
  FeatherIcon,
  LoadingIndicator,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('all')
const query = ref('')
const loading = ref(false)
const notifications = ref([])
const showPrefs = ref(false)

const TABS = [
  { key: 'all', label: 'All', badge: computed(() => notifications.value.length) },
  { key: 'unread', label: 'Unread', badge: computed(() => notifications.value.filter((n) => !n.read).length) },
  { key: 'mentions', label: 'Mentions' },
  { key: 'tasks', label: 'Tasks' },
  { key: 'assignments', label: 'Assignments' },
]

function tabBadge(tab) {
  return tab.badge?.value ?? tab.badge ?? null
}

const preferences = ref([
  { type: 'Mention', label: 'Mentions', description: 'When someone mentions you', email: true, in_app: true },
  { type: 'Task', label: 'Tasks', description: 'Task assignments and updates', email: true, in_app: true },
  { type: 'Assignment', label: 'Assignments', description: 'Lead/deal assignments', email: true, in_app: true },
  { type: 'WhatsApp', label: 'WhatsApp', description: 'WhatsApp message notifications', email: false, in_app: true },
])

const filteredNotifications = computed(() => {
  let rows = notifications.value
  if (activeTab.value === 'unread') rows = rows.filter((n) => !n.read)
  if (activeTab.value === 'mentions') rows = rows.filter((n) => n.type === 'Mention')
  if (activeTab.value === 'tasks') rows = rows.filter((n) => n.type === 'Task')
  if (activeTab.value === 'assignments') rows = rows.filter((n) => n.type === 'Assignment')
  if (query.value) {
    const q = query.value.toLowerCase()
    rows = rows.filter((n) =>
      [n.notification_text, n.message, n.from_user?.full_name, n.reference_name]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q)),
    )
  }
  return rows
})

async function fetchNotifications() {
  loading.value = true
  try {
    const data = await call('crm.api.notifications.get_notifications')
    notifications.value = data || []
  } catch (e) {
    toast.error(__('Failed to load notifications'))
  }
  loading.value = false
}

async function markAllAsRead() {
  try {
    await call('crm.api.notifications.mark_as_read')
    toast.success(__('All marked as read'))
    fetchNotifications()
  } catch (e) {
    toast.error(__('Failed to mark as read'))
  }
}

async function markOneAsRead(n) {
  try {
    await call('crm.api.notifications.mark_as_read', { doc: n.name })
    n.read = true
  } catch (e) {
    toast.error(__('Failed to mark as read'))
  }
}

async function openNotification(n) {
  if (!n.read) await markOneAsRead(n)
  const route = notificationRoute(n)
  if (!route) {
    toast.info(__('This notification is not linked to a CRM record.'))
    return
  }
  router.push(route)
}

async function deleteNotification(n) {
  try {
    await call('crm.api.notifications.delete_notification', { name: n.name })
    notifications.value = notifications.value.filter((item) => item.name !== n.name)
    toast.success(__('Notification deleted'))
  } catch (e) {
    toast.error(__('Failed to delete notification'))
  }
}

function notificationRoute(n) {
  const doctype = n.reference_doctype || n.notification_type_doctype
  const name = n.reference_name || n.notification_type_doc
  if (doctype === 'CRM Deal' && name) return { name: 'Deal', params: { dealId: name }, hash: n.hash || '' }
  if (doctype === 'CRM Lead' && name) return { name: 'Lead', params: { leadId: name }, hash: n.hash || '' }
  if (doctype === 'CRM Task') return { name: 'Tasks', hash: n.hash || '#tasks' }
  return null
}

async function archiveAll() {
  try {
    await call('crm.api.notifications.archive_all_notifications')
    toast.success(__('All notifications archived'))
    fetchNotifications()
  } catch (e) {
    toast.error(__('Failed to archive notifications'))
  }
}

async function fetchPreferences() {
  try {
    const data = await call('crm.api.notifications.get_preferences')
    if (data) {
      preferences.value.forEach((pref) => {
        const row = data[pref.type]
        if (row) {
          pref.email = Boolean(row.email)
          pref.in_app = Boolean(row.in_app)
        }
      })
    }
  } catch (e) {
    // silently fail
  }
}

async function savePreferences() {
  try {
    await call('crm.api.notifications.save_preferences', { preferences: preferences.value })
    toast.success(__('Preferences saved'))
  } catch (e) {
    toast.error(__('Failed to save preferences'))
  }
}

function sanitizeHTML(html) {
  if (!html) return ''
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

function labelize(value) {
  if (!value) return '—'
  return String(value).replace(/[_-]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

onMounted(async () => {
  await fetchNotifications()
  await fetchPreferences()
  if (!notifications.value.length) {
    try {
      await call('crm.api.notifications.seed_notification_sample_data')
      await fetchNotifications()
    } catch (e) {
      // ignore seed errors
    }
  }
})
usePageMeta(() => ({ title: __('Notification Center') }))
</script>
