<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Check-In/Out GPS') }}
        </h1>
      </div>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Catat lokasi kunjungan Anda') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
          {{ __('Pilih Kunjungan') }}
        </label>
        <select
          v-if="plannedVisits.length > 0"
          v-model="selectedVisit"
          :disabled="checkedIn"
          class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal disabled:opacity-50"
        >
          <option :value="null">{{ __('Pilih kunjungan untuk check-in') }}</option>
          <option v-for="v in plannedVisits" :key="v.name" :value="v">
            {{ v.customer_name || v.customer }} - {{ v.visit_date }}
          </option>
        </select>
        <div v-else-if="!loadingVisits && !showCreateForm" class="text-center py-4 space-y-3">
          <FeatherIcon name="calendar" class="size-8 text-crm-muted mx-auto" />
          <p class="text-sm text-crm-text-secondary">{{ __('Belum ada kunjungan terjadwal') }}</p>
          <Button variant="solid" size="sm" @click="showCreateForm = true">
            <template #prefix>
              <FeatherIcon name="plus" class="size-4" />
            </template>
            {{ __('Buat Kunjungan Baru') }}
          </Button>
        </div>
        <div v-else-if="showCreateForm" class="space-y-3 py-2">
          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1 block">{{ __('Nama Nasabah') }}</label>
            <input
              v-model="newVisitCustomer"
              type="text"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
              :placeholder="__('Masukkan nama nasabah')"
            />
          </div>
          <div class="flex gap-2">
            <Button variant="ghost" size="sm" class="flex-1" @click="cancelCreate">
              {{ __('Batal') }}
            </Button>
            <Button variant="solid" size="sm" class="flex-1" :disabled="!newVisitCustomer.trim()" :loading="creatingVisit" @click="quickCreateVisit">
              {{ __('Simpan & Pilih') }}
            </Button>
          </div>
        </div>
        <div v-else class="text-center py-4">
          <FeatherIcon name="loader" class="size-6 animate-spin text-crm-teal mx-auto" />
        </div>
      </div>

      <div v-if="gpsDenied" class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <div class="flex justify-center mb-3">
          <div class="flex size-14 items-center justify-center rounded-2xl bg-red-50">
            <FeatherIcon name="alert-triangle" class="size-6 text-red-500" />
          </div>
        </div>
        <p class="text-sm font-medium text-crm-text mb-1">{{ __('GPS Tidak Aktif') }}</p>
        <p class="text-xs text-crm-text-secondary mb-4">{{ __('Aktifkan GPS di pengaturan perangkat') }}</p>
        <Button variant="outline" class="w-full" @click="startGPS">
          {{ __('Coba Lagi') }}
        </Button>
      </div>

      <div v-if="gpsLoading && !gpsDenied" class="rounded-xl bg-white p-6 shadow-sm border border-crm-border text-center">
        <div class="flex justify-center mb-3">
          <FeatherIcon name="loader" class="size-8 animate-spin text-crm-teal" />
        </div>
        <p class="text-sm text-crm-text-secondary">{{ __('Mendapatkan lokasi...') }}</p>
      </div>

      <div v-if="currentPosition && !gpsDenied" class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-3">
        <h2 class="text-sm font-semibold text-crm-text">{{ __('Lokasi Saat Ini') }}</h2>
        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-xl bg-crm-surface p-3">
            <p class="text-xs text-crm-text-secondary mb-0.5">{{ __('Latitude') }}</p>
            <p class="text-sm font-mono font-medium text-crm-text">{{ currentPosition.lat.toFixed(6) }}</p>
          </div>
          <div class="rounded-xl bg-crm-surface p-3">
            <p class="text-xs text-crm-text-secondary mb-0.5">{{ __('Longitude') }}</p>
            <p class="text-sm font-mono font-medium text-crm-text">{{ currentPosition.lng.toFixed(6) }}</p>
          </div>
        </div>
        <div class="flex items-center justify-between rounded-xl bg-crm-surface p-3">
          <div class="flex items-center gap-2">
            <div class="size-3 rounded-full" :class="accuracyClass" />
            <span class="text-xs text-crm-text-secondary">{{ __('Akurasi') }}</span>
          </div>
          <span class="text-sm font-mono font-medium text-crm-text">{{ currentPosition.accuracy }}m</span>
        </div>

        <div class="flex gap-2 pt-1">
          <Button
            v-if="!checkedIn"
            variant="solid"
            class="flex-1"
            :disabled="!selectedVisit"
            :loading="checkingIn"
            @click="checkIn"
          >
            <template #prefix>
              <FeatherIcon name="log-in" class="size-4" />
            </template>
            {{ __('Start Visit') }}
          </Button>
          <Button
            v-if="checkedIn"
            variant="solid"
            class="flex-1 bg-red-500 hover:bg-red-600 border-red-500"
            :loading="checkingOut"
            @click="checkOut"
          >
            <template #prefix>
              <FeatherIcon name="log-out" class="size-4" />
            </template>
            {{ __('End Visit') }}
          </Button>
          <Button
            variant="outline"
            class="shrink-0"
            @click="refreshGPS"
          >
            <template #prefix>
              <FeatherIcon name="crosshair" class="size-4" />
            </template>
          </Button>
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <h2 class="text-sm font-semibold text-crm-text mb-3">{{ __('Riwayat Check-In') }}</h2>

        <div v-if="historyVisits.length === 0" class="py-6 text-center">
          <FeatherIcon name="history" class="size-8 text-crm-muted mx-auto mb-1" />
          <p class="text-xs text-crm-text-secondary">{{ __('Belum ada riwayat check-in') }}</p>
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="item in historyVisits"
            :key="item.name"
            class="rounded-xl border border-crm-border p-3"
          >
            <div class="flex items-start justify-between mb-1">
              <h3 class="text-sm font-medium text-crm-text">{{ item.customer_name || item.customer }}</h3>
              <span class="text-[10px] font-semibold rounded-full px-2 py-0.5 bg-green-100 text-green-700">
                Completed
              </span>
            </div>
            <div class="space-y-1 text-xs text-crm-text-secondary">
              <div class="flex items-center gap-2">
                <FeatherIcon name="log-in" class="size-3 shrink-0" />
                {{ __('Check-In') }}: {{ formatTime(item.check_in_time) }}
              </div>
              <div v-if="item.check_out_time" class="flex items-center gap-2">
                <FeatherIcon name="log-out" class="size-3 shrink-0" />
                {{ __('Check-Out') }}: {{ formatTime(item.check_out_time) }}
              </div>
              <div v-if="item.check_in_time && item.check_out_time" class="flex items-center gap-2">
                <FeatherIcon name="clock" class="size-3 shrink-0" />
                {{ __('Durasi') }}: {{ computeDuration(item.check_in_time, item.check_out_time) }}
              </div>
              <div v-if="item.check_in_latitude" class="flex items-center gap-2">
                <FeatherIcon name="map-pin" class="size-3 shrink-0" />
                {{ Number(item.check_in_latitude).toFixed(4) }}, {{ Number(item.check_in_longitude).toFixed(4) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'

const gpsLoading = ref(true)
const gpsDenied = ref(false)
const checkedIn = ref(false)
const currentPosition = ref(null)
let watchId = null

const plannedVisits = ref([])
const loadingVisits = ref(false)
const selectedVisit = ref(null)

const checkingIn = ref(false)
const checkingOut = ref(false)
const creatingVisit = ref(false)
const showCreateForm = ref(false)
const newVisitCustomer = ref('')

const historyVisits = ref([])

const accuracyClass = computed(() => {
  if (!currentPosition.value) return 'bg-gray-300'
  const acc = currentPosition.value.accuracy
  if (acc < 10) return 'bg-green-500'
  if (acc < 50) return 'bg-amber-500'
  return 'bg-red-500'
})

function formatTime(iso) {
  if (!iso) return '-'
  return iso.slice(0, 16).replace('T', ' ')
}

function computeDuration(checkIn, checkOut) {
  if (!checkIn || !checkOut) return null
  const start = new Date(checkIn)
  const end = new Date(checkOut)
  const diffMs = end - start
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return '< 1m'
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return h > 0 ? `${h}j ${m}m` : `${m}m`
}

function startGPS() {
  gpsDenied.value = false
  gpsLoading.value = true
  if (!navigator.geolocation) {
    gpsDenied.value = true
    gpsLoading.value = false
    return
  }
  watchId = navigator.geolocation.watchPosition(
    (pos) => {
      currentPosition.value = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        accuracy: Math.round(pos.coords.accuracy),
      }
      gpsLoading.value = false
    },
    () => {
      gpsDenied.value = true
      gpsLoading.value = false
    },
    { enableHighAccuracy: true, timeout: 15000, maximumAge: 5000 }
  )
}

function refreshGPS() {
  gpsLoading.value = true
  if (!navigator.geolocation) {
    gpsDenied.value = true
    gpsLoading.value = false
    return
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      currentPosition.value = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        accuracy: Math.round(pos.coords.accuracy),
      }
      gpsLoading.value = false
    },
    () => {
      gpsDenied.value = true
      gpsLoading.value = false
    },
    { enableHighAccuracy: true, timeout: 15000 }
  )
}

async function loadPlannedVisits() {
  loadingVisits.value = true
  try {
    plannedVisits.value = await call('crm.api.visit.list_visits', { status: 'Planned' })
  } finally {
    loadingVisits.value = false
  }
}

async function loadHistory() {
  historyVisits.value = await call('crm.api.visit.list_visits', { status: 'Checked Out' })
}

function cancelCreate() {
  showCreateForm.value = false
  newVisitCustomer.value = ''
}

async function quickCreateVisit() {
  const customerName = newVisitCustomer.value.trim()
  if (!customerName) return
  creatingVisit.value = true
  try {
    const doc = await call('crm.api.visit.create_visit', {
      customer_name: customerName,
      visit_date: new Date().toISOString().slice(0, 10),
    })
    await loadPlannedVisits()
    selectedVisit.value = plannedVisits.value.find(v => v.name === doc.name) || doc
    showCreateForm.value = false
    newVisitCustomer.value = ''
    toast.success(__('Kunjungan berhasil dibuat'))
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal membuat kunjungan'))
  } finally {
    creatingVisit.value = false
  }
}

async function checkIn() {
  if (!currentPosition.value || !selectedVisit.value) return
  checkingIn.value = true
  try {
    await call('crm.api.visit.check_in', {
      visit_id: selectedVisit.value.name,
      latitude: currentPosition.value.lat,
      longitude: currentPosition.value.lng,
      accuracy: currentPosition.value.accuracy,
    })
    toast.success(__('Check-In berhasil'))
    checkedIn.value = true
    loadHistory()
    loadPlannedVisits()
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal check-in'))
  } finally {
    checkingIn.value = false
  }
}

async function checkOut() {
  if (!currentPosition.value || !selectedVisit.value) return
  checkingOut.value = true
  try {
    await call('crm.api.visit.check_out', {
      visit_id: selectedVisit.value.name,
      latitude: currentPosition.value.lat,
      longitude: currentPosition.value.lng,
    })
    toast.success(__('Check-Out berhasil'))
    checkedIn.value = false
    selectedVisit.value = null
    loadHistory()
    loadPlannedVisits()
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal check-out'))
  } finally {
    checkingOut.value = false
  }
}

onMounted(() => {
  loadPlannedVisits()
  loadHistory()
  startGPS()
})

onUnmounted(() => {
  if (watchId !== null) navigator.geolocation.clearWatch(watchId)
})
</script>
