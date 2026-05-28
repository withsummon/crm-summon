<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-lg font-semibold text-crm-text">
            {{ __('Approval') }}
          </h1>
          <p class="text-xs text-crm-text-secondary mt-0.5">
            {{ __('Approve atau reject aplikasi secara mobile') }}
          </p>
        </div>
        <div class="flex gap-1 rounded-xl bg-crm-surface p-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="rounded-lg px-3 py-1.5 text-xs font-medium transition-colors"
            :class="activeTab === tab.key ? 'bg-white text-crm-text shadow-sm' : 'text-crm-text-secondary'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
            <span v-if="tab.count" class="ml-1 text-crm-muted">({{ tab.count }})</span>
          </button>
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-2.5">
      <div v-if="loading" class="space-y-2.5">
        <div v-for="n in 3" :key="n" class="rounded-xl bg-white p-4 shadow-sm border border-crm-border animate-pulse">
          <div class="flex items-start gap-3">
            <div class="size-10 rounded-xl bg-gray-200 shrink-0" />
            <div class="min-w-0 flex-1 space-y-2">
              <div class="h-4 w-3/4 rounded bg-gray-200" />
              <div class="h-3 w-1/2 rounded bg-gray-100" />
              <div class="h-3 w-1/3 rounded bg-gray-100" />
            </div>
          </div>
          <div class="mt-3 flex gap-2">
            <div class="h-8 flex-1 rounded-xl bg-gray-200" />
            <div class="h-8 flex-1 rounded-xl bg-gray-200" />
          </div>
        </div>
      </div>

      <div v-else-if="error" class="py-16 text-center">
        <FeatherIcon name="alert-circle" class="size-10 text-red-400 mx-auto mb-2" />
        <p class="text-sm font-medium text-crm-text">{{ __('Gagal memuat data') }}</p>
        <p class="text-xs text-crm-text-secondary mt-1 mb-4">{{ error }}</p>
        <Button variant="outline" size="sm" @click="loadPending">
          {{ __('Coba Lagi') }}
        </Button>
      </div>

      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="rounded-xl bg-white p-4 shadow-sm border border-crm-border"
      >
        <div class="flex items-start gap-3">
          <div
            class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-blue-50"
          >
            <FeatherIcon
              name="briefcase"
              class="size-5 text-blue-600"
            />
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <p class="text-sm font-semibold text-crm-text truncate">
                {{ item.title }}
              </p>
              <span
                class="rounded-full px-2 py-0.5 text-[10px] font-medium shrink-0"
                :class="statusClass(item.status)"
              >
                {{ item.status }}
              </span>
            </div>
            <p class="text-xs text-crm-text-secondary mt-0.5">
              {{ item.subtitle }}
            </p>
            <p v-if="item.date" class="text-xs text-crm-muted mt-0.5">
              {{ item.date }}
            </p>
          </div>
        </div>

        <div v-if="activeTab === 'pending'" class="mt-3 flex gap-2">
          <Button
            variant="outline"
            class="flex-1 !border-red-200 !text-red-600 hover:!bg-red-50"
            size="sm"
            @click="rejectItem(item)"
          >
            <template #prefix>
              <FeatherIcon name="x" class="size-3.5" />
            </template>
            {{ __('Reject') }}
          </Button>
          <Button
            variant="solid"
            class="flex-1 !bg-green-600 hover:!bg-green-700"
            size="sm"
            @click="approveItem(item)"
          >
            <template #prefix>
              <FeatherIcon name="check" class="size-3.5" />
            </template>
            {{ __('Approve') }}
          </Button>
        </div>
      </div>

      <div v-if="!loading && !error && !filteredItems.length" class="py-16 text-center">
        <FeatherIcon :name="activeTab === 'pending' ? 'check-circle' : 'clock'" class="size-10 text-crm-muted mx-auto mb-2" />
        <p class="text-sm font-medium text-crm-text">
          {{ activeTab === 'pending' ? __('Tidak ada approval pending') : __('Belum ada riwayat') }}
        </p>
        <p class="text-xs text-crm-text-secondary mt-1">
          {{ __('Semua sudah diproses') }}
        </p>
      </div>
    </div>

    <TransitionRoot :show="showRejectDialog">
      <div class="fixed inset-0 z-50 flex items-end">
        <TransitionChild
          as="template"
          enter="transition-opacity duration-200"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="transition-opacity duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black/30" @click="showRejectDialog = false" />
        </TransitionChild>
        <TransitionChild
          as="template"
          enter="transition-transform duration-300 ease-out"
          enter-from="translate-y-full"
          enter-to="translate-y-0"
          leave="transition-transform duration-200 ease-in"
          leave-from="translate-y-0"
          leave-to="translate-y-full"
        >
          <div class="relative w-full rounded-t-2xl bg-white px-4 pb-8 pt-5 shadow-xl">
            <div class="mx-auto mb-4 h-1 w-10 rounded-full bg-gray-300" />
            <h2 class="text-base font-semibold text-crm-text mb-4">
              {{ __('Alasan Reject') }}
            </h2>
            <textarea
              v-model="rejectReason"
              rows="3"
              :placeholder="__('Jelaskan alasan reject...')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal resize-none mb-4"
            />
            <div class="flex gap-2">
              <Button variant="ghost" class="flex-1" @click="showRejectDialog = false">
                {{ __('Batal') }}
              </Button>
              <Button variant="solid" class="flex-1 !bg-red-500" :disabled="!rejectReason" @click="confirmReject">
                {{ __('Reject') }}
              </Button>
            </div>
          </div>
        </TransitionChild>
      </div>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'
import { TransitionRoot, TransitionChild } from '@headlessui/vue'

const activeTab = ref('pending')
const showRejectDialog = ref(false)
const rejectReason = ref('')
const selectedItem = ref(null)
const loading = ref(false)
const error = ref('')

const pendingItems = ref([])
const historyItems = ref([])

const tabs = [
  { key: 'pending', label: __('Pending') },
  { key: 'history', label: __('Riwayat') },
]

async function loadPending() {
  loading.value = true
  error.value = ''
  try {
    pendingItems.value = await call('crm.api.mobile_approval.list_pending')
  } catch (err) {
    error.value = err.messages?.[0] || __('Gagal memuat data')
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  try {
    historyItems.value = await call('crm.api.mobile_approval.list_history')
  } catch { /* silent */ }
}

const filteredItems = computed(() => {
  if (activeTab.value === 'pending') {
    return pendingItems.value.map(mapItem)
  }
  return historyItems.value.map(mapItem)
})

function mapItem(item) {
  return {
    id: item.name,
    title: item.borrower_name || item.borrower,
    subtitle: `${item.facility_type || ''} - ${formatCurrency(item.requested_amount)}`,
    date: formatDate(item.creation),
    status: item.status,
    original: item,
  }
}

function formatCurrency(amount) {
  if (!amount) return 'Rp 0'
  return 'Rp ' + Number(amount).toLocaleString('id-ID')
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

function statusClass(status) {
  const map = {
    'Pending Approval': 'bg-amber-50 text-amber-700',
    Pending: 'bg-amber-50 text-amber-700',
    Approved: 'bg-green-50 text-green-700',
    Rejected: 'bg-red-50 text-red-700',
  }
  return map[status] || 'bg-gray-50 text-gray-700'
}

async function approveItem(item) {
  try {
    await call('crm.api.mobile_approval.approve_application', { application_id: item.original.name })
    toast.success(__('Aplikasi {0} disetujui', [item.title]))
    loadPending()
    loadHistory()
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal menyetujui'))
  }
}

function rejectItem(item) {
  selectedItem.value = item
  rejectReason.value = ''
  showRejectDialog.value = true
}

async function confirmReject() {
  if (!selectedItem.value || !rejectReason.value) return
  try {
    await call('crm.api.mobile_approval.reject_application', {
      application_id: selectedItem.value.original.name,
      reason: rejectReason.value,
    })
    toast.success(__('Aplikasi {0} ditolak', [selectedItem.value.title]))
    showRejectDialog.value = false
    rejectReason.value = ''
    selectedItem.value = null
    loadPending()
    loadHistory()
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal menolak'))
  }
}

onMounted(() => {
  loadPending()
  loadHistory()
})
</script>
