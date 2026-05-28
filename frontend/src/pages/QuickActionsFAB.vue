<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <h1 class="text-lg font-semibold text-crm-text">
        {{ __('Quick Actions') }}
      </h1>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Aksi cepat favorit Anda') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div v-if="favoriteActions.length" class="grid grid-cols-4 gap-3">
        <div
          v-for="action in favoriteActions"
          :key="action.label"
          class="relative rounded-xl bg-white p-3 shadow-sm border border-crm-border text-center"
        >
          <button
            class="absolute -top-1.5 -right-1.5 flex size-5 items-center justify-center rounded-full bg-red-500 text-white shadow-sm"
            @click="removeFavorite(action)"
          >
            <FeatherIcon name="x" class="size-3" />
          </button>
          <button class="flex flex-col items-center gap-1.5 w-full" @click="navigate(action)">
            <FeatherIcon :name="action.icon" class="size-6 text-crm-teal" />
            <span class="text-[10px] font-medium text-crm-text">{{ __(action.label) }}</span>
          </button>
        </div>
      </div>

      <div v-else class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <FeatherIcon name="star" class="size-10 text-crm-muted mx-auto mb-2" />
        <p class="text-sm font-medium text-crm-text">{{ __('Belum ada aksi favorit') }}</p>
        <p class="text-xs text-crm-text-secondary mt-1">{{ __('Tambah dari daftar di bawah') }}</p>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <h2 class="text-sm font-semibold text-crm-text mb-3">{{ __('All Actions') }}</h2>
        <div class="space-y-1">
          <div
            v-for="action in allActions"
            :key="action.label"
            class="flex items-center justify-between rounded-xl p-3 hover:bg-crm-surface transition-colors"
          >
            <div class="flex items-center gap-3 min-w-0 flex-1">
              <FeatherIcon :name="action.icon" class="size-5 text-crm-text-secondary shrink-0" />
              <div>
                <p class="text-sm text-crm-text">{{ __(action.label) }}</p>
                <p class="text-xs text-crm-text-secondary">{{ __(action.description) }}</p>
              </div>
            </div>
            <button
              class="text-xs font-medium shrink-0 ml-2"
              :class="isFavorite(action) ? 'text-crm-muted' : 'text-crm-teal'"
              :disabled="isFavorite(action)"
              @click="addFavorite(action)"
            >
              {{ isFavorite(action) ? __('Tersimpan') : __('+ Favorit') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FeatherIcon, toast } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

const FAVORITES_KEY = 'quick_actions_favorites'

const allActions = [
  { label: 'New Lead', icon: 'user-plus', description: 'Buat lead baru', route: 'Mobile Lead Capture' },
  { label: 'New Customer', icon: 'user-check', description: 'Tambah nasabah baru', route: 'My Customers Mobile' },
  { label: 'Scan Document', icon: 'camera', description: 'Scan KTP, NPWP, dokumen', route: 'Document Scanner' },
  { label: 'Plan Visit', icon: 'map-pin', description: 'Rencanakan kunjungan', route: 'Visit Planner & Route' },
  { label: 'Check-In', icon: 'log-in', description: 'GPS check-in kunjungan', route: 'Visit Check-In/Out GPS' },
  { label: 'New Report', icon: 'file-text', description: 'Laporan hasil kunjungan', route: 'Visit Report Capture' },
  { label: 'Calculator', icon: 'bar-chart', description: 'Kalkulator pricing KPR', route: 'Mobile Calculator Pricing' },
  { label: 'AI Assistant', icon: 'message-circle', description: 'Tanya AI Assistant', route: 'AI Assistant Mobile' },
  { label: 'Find Customer', icon: 'search', description: 'Cari nasabah', route: 'My Customers Mobile' },
]

function loadFavorites() {
  try {
    const stored = localStorage.getItem(FAVORITES_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function saveFavorites(favs) {
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(favs))
}

const favoriteLabels = ref(loadFavorites())

const favoriteActions = ref(
  allActions.filter(a => favoriteLabels.value.includes(a.label))
)

function isFavorite(action) {
  return favoriteLabels.value.includes(action.label)
}

function addFavorite(action) {
  if (isFavorite(action)) return
  favoriteLabels.value.push(action.label)
  saveFavorites(favoriteLabels.value)
  favoriteActions.value = allActions.filter(a => favoriteLabels.value.includes(a.label))
  toast.success(__('{0} ditambahkan ke favorit', [action.label]))
}

function removeFavorite(action) {
  favoriteLabels.value = favoriteLabels.value.filter(l => l !== action.label)
  saveFavorites(favoriteLabels.value)
  favoriteActions.value = allActions.filter(a => favoriteLabels.value.includes(a.label))
  toast.success(__('{0} dihapus dari favorit', [action.label]))
}

function navigate(action) {
  router.push({ name: action.route })
}
</script>
