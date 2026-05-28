<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Notifications') }}
        </h1>
        <button
          v-if="notifications.data?.length"
          class="text-xs font-medium text-crm-teal"
          @click="markAllRead"
        >
          {{ __('Mark all read') }}
        </button>
      </div>
    </div>

    <div v-if="error" class="rounded-xl bg-red-50 border border-red-200 p-4 mx-4 mb-4">
      <div class="flex items-center gap-2">
        <FeatherIcon name="alert-triangle" class="size-4 text-red-500 shrink-0" />
        <p class="text-xs text-red-600 flex-1">{{ error }}</p>
        <button class="text-xs font-medium text-red-700" @click="loadNotifications">{{ __('Coba Lagi') }}</button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-1">
      <div v-if="notifications.loading" class="space-y-2 pt-2">
        <div v-for="i in 5" :key="i" class="animate-pulse rounded-xl bg-white p-4 border border-crm-border">
          <div class="flex items-center gap-3">
            <div class="size-9 rounded-full bg-crm-surface" />
            <div class="flex-1 space-y-2">
              <div class="h-3 w-3/4 rounded bg-crm-surface" />
              <div class="h-2.5 w-1/2 rounded bg-crm-surface" />
            </div>
          </div>
        </div>
      </div>

      <template v-else-if="groupedNotifications.length">
        <div v-for="(group, dateLabel) in groupedNotifications" :key="dateLabel">
          <p class="px-1 py-2 text-[10px] font-semibold uppercase tracking-wider text-crm-muted">
            {{ dateLabel }}
          </p>
          <div
            v-for="n in group"
            :key="n.comment || n.name"
            class="rounded-xl bg-white p-4 border border-crm-border mb-1 transition-colors cursor-pointer"
            :class="n.read ? '' : 'border-l-[3px] border-l-crm-teal'"
            @click="openNotification(n)"
          >
            <div class="flex items-start gap-3">
              <div
                class="flex size-9 shrink-0 items-center justify-center rounded-xl"
                :class="getNotifBg(n)"
              >
                <FeatherIcon
                  :name="getNotifIcon(n)"
                  class="size-4"
                  :class="getNotifColor(n)"
                />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-crm-text" :class="n.read ? '' : 'font-semibold'">
                  {{ n.from_user?.full_name || 'System' }}
                </p>
                <p
                  v-if="n.notification_text"
                  class="text-xs text-crm-text-secondary mt-0.5 line-clamp-2"
                  v-html="sanitizeHTML(n.notification_text)"
                />
                <p v-else class="text-xs text-crm-text-secondary mt-0.5">
                  {{ getNotifText(n) }}
                </p>
                <p class="text-[10px] text-crm-muted mt-1">
                  {{ timeAgo(n.creation) }}
                </p>
              </div>
              <div v-if="!n.read" class="mt-1.5 size-2 shrink-0 rounded-full bg-crm-teal" />
            </div>
          </div>
        </div>
      </template>

      <div v-else class="py-16 text-center">
        <FeatherIcon name="bell-off" class="size-10 text-crm-muted mx-auto mb-2" />
        <p class="text-sm font-medium text-crm-text">{{ __('Tidak ada notifikasi') }}</p>
        <p class="text-xs text-crm-text-secondary mt-1">{{ __('Notifikasi baru akan muncul di sini') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { FeatherIcon, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'
import { notifications, notificationsStore } from '@/stores/notifications'
import { globalStore } from '@/stores/global'
import { timeAgo, sanitizeHTML } from '@/utils'

const error = ref('')

const router = useRouter()
const { $socket } = globalStore()
const { mark_as_read, mark_doc_as_read } = notificationsStore()

async function loadNotifications() {
  error.value = ''
  try {
    await notifications.reload()
  } catch {
    error.value = __('Gagal memuat notifikasi')
  }
}

if (notifications.promise) {
  notifications.promise.catch(() => {
    error.value = __('Gagal memuat notifikasi')
  })
}

onMounted(() => {
  $socket.on('crm_notification', () => loadNotifications())
  loadNotifications()
})

onBeforeUnmount(() => {
  $socket.off('crm_notification')
})

const groupedNotifications = computed(() => {
  const data = notifications.data || []
  const groups = {}
  data.forEach((n) => {
    const date = new Date(n.creation)
    const today = new Date()
    let label
    if (date.toDateString() === today.toDateString()) {
      label = __('Hari Ini')
    } else {
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)
      label = date.toDateString() === yesterday.toDateString()
        ? __('Kemarin')
        : date.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'short' })
    }
    if (!groups[label]) groups[label] = []
    groups[label].push(n)
  })
  return groups
})

function getNotifIcon(n) {
  if (n.type === 'WhatsApp') return 'message-circle'
  if (n.notification_type?.includes('lead')) return 'user-plus'
  if (n.notification_type?.includes('deal') || n.route_name === 'Deal') return 'briefcase'
  if (n.notification_type?.includes('comment') || n.comment) return 'message-square'
  if (n.notification_type?.includes('assign')) return 'user-check'
  return 'bell'
}

function getNotifBg(n) {
  if (n.type === 'WhatsApp') return 'bg-green-50'
  if (n.notification_type?.includes('lead')) return 'bg-crm-surface'
  if (n.notification_type?.includes('deal')) return 'bg-amber-50'
  if (n.notification_type?.includes('comment') || n.comment) return 'bg-blue-50'
  return 'bg-gray-50'
}

function getNotifColor(n) {
  if (n.type === 'WhatsApp') return 'text-green-600'
  if (n.notification_type?.includes('lead')) return 'text-crm-teal'
  if (n.notification_type?.includes('deal')) return 'text-amber-600'
  if (n.notification_type?.includes('comment') || n.comment) return 'text-blue-600'
  return 'text-gray-600'
}

function getNotifText(n) {
  const type = n.route_name || n.reference_doctype || ''
  if (type.includes('Lead')) return __('Mentioned you in Lead {0}', [n.reference_name])
  if (type.includes('Deal')) return __('Mentioned you in Deal {0}', [n.reference_name])
  return n.notification_type || n.reference_name || '-'
}

function openNotification(n) {
  if (!n.read) mark_doc_as_read(n.comment || n.notification_type_doc)
  if (n.route_name) {
    const params = n.route_name === 'Deal' ? { dealId: n.reference_name } : { leadId: n.reference_name }
    router.push({ name: n.route_name, params, hash: '#' + (n.comment || '') })
  }
}

function markAllRead() {
  mark_as_read.reload()
  toast.success(__('Semua notifikasi ditandai sudah dibaca'))
}
</script>
