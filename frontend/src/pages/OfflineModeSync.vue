<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Offline Mode & Sync') }}
        </h1>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex size-3 rounded-full" :class="isOnline ? 'bg-green-500' : 'bg-red-500'" />
            <p class="text-sm font-semibold text-crm-text">
              {{ isOnline ? __('Online') : __('Offline') }}
            </p>
          </div>
          <span class="text-xs text-crm-text-secondary">
            {{ isOnline ? __('Terhubung ke server') : __('Tidak ada koneksi') }}
          </span>
        </div>
      </div>

      <div v-if="syncing" class="space-y-3">
        <div v-for="i in 4" :key="i" class="animate-pulse rounded-xl bg-crm-surface h-16" />
      </div>

      <div v-else-if="dataSources.every(ds => ds.status === 'synced')" class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <FeatherIcon name="check-circle" class="size-10 text-green-500 mx-auto mb-2" />
        <p class="text-sm font-medium text-crm-text">{{ __('Semua data tersinkronisasi') }}</p>
        <p class="text-xs text-crm-text-secondary mt-1">{{ __('Tidak ada data yang perlu disinkronisasi') }}</p>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-crm-text">{{ __('Data Sources') }}</h2>
          <Button variant="solid" size="sm" :disabled="syncing || !isOnline" @click="syncAll">
            <template #prefix>
              <FeatherIcon name="refresh-cw" class="size-3.5" :class="{ 'animate-spin': syncing }" />
            </template>
            {{ __('Sync All') }}
          </Button>
        </div>
        <div class="space-y-3">
          <div v-for="ds in dataSources" :key="ds.name" class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <FeatherIcon :name="ds.icon" class="size-4 text-crm-text-secondary" />
              <div>
                <p class="text-sm text-crm-text">{{ ds.label }}</p>
                <p class="text-[10px] text-crm-muted">
                  {{ ds.pending }} pending &middot; {{ timeAgo(ds.lastSync) }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-medium px-2 py-0.5 rounded-full" :class="statusBadgeClass(ds.status)">
                {{ statusLabel(ds.status) }}
              </span>
              <button
                v-if="ds.status === 'pending' || ds.status === 'error'"
                class="text-xs text-crm-teal font-medium"
                :disabled="!isOnline"
                @click="syncSource(ds)"
              >
                {{ __('Sync') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <h2 class="text-sm font-semibold text-crm-text mb-3">{{ __('Offline Queue') }}</h2>
        <div v-if="offlineQueue.length" class="space-y-2">
          <div v-for="item in offlineQueue" :key="item.id" class="flex items-center gap-3 rounded-lg bg-crm-surface p-3">
            <FeatherIcon :name="item.type === 'lead' ? 'user-plus' : item.type === 'visit' ? 'map-pin' : 'file'" class="size-4 shrink-0 text-crm-text-secondary" />
            <div class="min-w-0 flex-1">
              <p class="text-sm text-crm-text truncate">{{ item.title }}</p>
              <p class="text-xs text-crm-muted">{{ item.subtitle }}</p>
            </div>
            <button class="text-xs text-crm-teal font-medium" :disabled="!isOnline" @click="retryItem(item)">
              {{ __('Retry') }}
            </button>
          </div>
        </div>
        <div v-else class="py-4 text-center">
          <FeatherIcon name="inbox" class="size-6 text-crm-muted mx-auto mb-1" />
          <p class="text-xs text-crm-text-secondary">{{ __('Antrean offline kosong') }}</p>
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-crm-text">{{ __('Auto-sync') }}</p>
            <p class="text-xs text-crm-text-secondary">{{ __('Sinkronisasi otomatis saat online') }}</p>
          </div>
          <button
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
            :class="autoSync ? 'bg-crm-teal' : 'bg-gray-200'"
            @click="toggleAutoSync"
          >
            <span
              class="inline-block size-5 transform rounded-full bg-white shadow-sm transition-transform"
              :class="autoSync ? 'translate-x-[22px]' : 'translate-x-[2px]'"
            />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { FeatherIcon, Button, toast } from 'frappe-ui'
import { timeAgo } from '@/utils'

const isOnline = ref(navigator.onLine)
const syncing = ref(false)
const autoSync = ref(localStorage.getItem('offline_auto_sync') !== 'false')

const dataSources = ref([
  { name: 'leads', label: __('Leads'), icon: 'target', pending: 3, lastSync: new Date(Date.now() - 300000), status: 'pending' },
  { name: 'customers', label: __('Customers'), icon: 'users', pending: 0, lastSync: new Date(Date.now() - 120000), status: 'synced' },
  { name: 'visits', label: __('Visits'), icon: 'map-pin', pending: 5, lastSync: new Date(Date.now() - 600000), status: 'pending' },
  { name: 'documents', label: __('Documents'), icon: 'file', pending: 1, lastSync: new Date(Date.now() - 900000), status: 'error' },
  { name: 'approvals', label: __('Approvals'), icon: 'check-circle', pending: 0, lastSync: new Date(Date.now() - 1800000), status: 'synced' },
])

const offlineQueue = ref([
  { id: 1, title: 'Lead - Andi Pratama', subtitle: 'CRM Lead &middot; 28 Mei 2026', type: 'lead' },
  { id: 2, title: 'Visit Report - PT Maju', subtitle: 'Visit &middot; 27 Mei 2026', type: 'visit' },
  { id: 3, title: 'Foto KTP - Budi Santoso', subtitle: 'Document &middot; 27 Mei 2026', type: 'document' },
])

function handleOnline() { isOnline.value = true; if (autoSync.value) syncAll() }
function handleOffline() { isOnline.value = false }

onMounted(() => {
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})

onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})

function toggleAutoSync() {
  autoSync.value = !autoSync.value
  localStorage.setItem('offline_auto_sync', autoSync.value)
}

function statusBadgeClass(status) {
  if (status === 'synced') return 'bg-green-50 text-green-700'
  if (status === 'syncing') return 'bg-blue-50 text-blue-700'
  if (status === 'error') return 'bg-red-50 text-red-700'
  return 'bg-amber-50 text-amber-700'
}

function statusLabel(status) {
  if (status === 'synced') return __('Synced')
  if (status === 'syncing') return __('Syncing')
  if (status === 'error') return __('Error')
  return __('Pending')
}

async function syncAll() {
  if (!isOnline.value) {
    toast.error(__('Tidak ada koneksi internet'))
    return
  }
  syncing.value = true
  dataSources.value.forEach(ds => { if (ds.status !== 'synced') ds.status = 'syncing' })
  await new Promise(r => setTimeout(r, 2500))
  dataSources.value.forEach(ds => {
    ds.status = 'synced'
    ds.pending = 0
    ds.lastSync = new Date()
  })
  offlineQueue.value = []
  syncing.value = false
  toast.success(__('Sinkronisasi berhasil'))
}

async function syncSource(ds) {
  if (!isOnline.value) {
    toast.error(__('Tidak ada koneksi internet'))
    return
  }
  ds.status = 'syncing'
  await new Promise(r => setTimeout(r, 1000))
  ds.status = 'synced'
  ds.pending = 0
  ds.lastSync = new Date()
  toast.success(__('{0} tersinkronisasi', [ds.label]))
}

function retryItem(item) {
  toast.success(__('Mengirim ulang {0}', [item.title]))
  offlineQueue.value = offlineQueue.value.filter(i => i.id !== item.id)
}
</script>
