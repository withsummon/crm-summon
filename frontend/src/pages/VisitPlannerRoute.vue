<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Visit Planner') }}
        </h1>
      </div>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Rencanakan dan atur kunjungan') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div ref="mapContainer" class="w-full h-44 rounded-lg bg-crm-surface" />
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-crm-text">
            {{ __('Kunjungan Saya') }}
            <span class="text-xs text-crm-text-secondary ml-1">({{ visits.length }})</span>
          </h2>
        </div>

        <div v-if="loadingVisits" class="space-y-2">
          <div v-for="i in 3" :key="i" class="animate-pulse rounded-xl bg-crm-surface h-20" />
        </div>

        <div v-else-if="visits.length === 0" class="py-8 text-center">
          <FeatherIcon name="map-pin" class="size-10 text-crm-muted mx-auto mb-2" />
          <p class="text-sm text-crm-text-secondary">{{ __('Belum ada kunjungan direncanakan') }}</p>
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="visit in visits"
            :key="visit.name"
            class="rounded-xl border border-crm-border p-3 transition-colors hover:bg-crm-surface"
          >
            <div class="flex items-start justify-between mb-1">
              <h3 class="text-sm font-medium text-crm-text">{{ visit.customer_name || visit.customer }}</h3>
              <span
                class="text-[10px] font-semibold rounded-full px-2 py-0.5 shrink-0 ml-2"
                :class="statusBadgeClass(visit.status)"
              >
                {{ visit.status }}
              </span>
            </div>
            <p class="text-xs text-crm-text-secondary mb-1">{{ visit.purpose || '-' }}</p>
            <div class="flex items-center gap-2 text-xs text-crm-text-secondary">
              <FeatherIcon name="calendar" class="size-3" />
              {{ visit.visit_date }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <button
      class="fixed bottom-6 right-6 z-20 flex size-12 items-center justify-center rounded-full bg-crm-teal text-white shadow-lg active:scale-95 transition-transform"
      @click="showForm = true"
    >
      <FeatherIcon name="plus" class="size-6" />
    </button>

    <div
      v-if="showForm"
      class="fixed inset-0 z-30 flex items-end bg-black/40"
      @click.self="showForm = false"
    >
      <div class="w-full max-w-lg mx-auto rounded-t-2xl bg-white p-5 shadow-2xl max-h-[85vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-semibold text-crm-text">{{ __('Kunjungan Baru') }}</h2>
          <button @click="showForm = false">
            <FeatherIcon name="x" class="size-5 text-crm-text-secondary" />
          </button>
        </div>

        <div class="space-y-3">
          <div class="relative">
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('Nama Nasabah') }}
            </label>
            <input
              v-model="newVisit.customer_name"
              type="text"
              :placeholder="__('Masukkan nama nasabah')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
              @input="onCustomerInput"
              @focus="onCustomerFocus"
              @blur="onCustomerBlur"
            />
            <div
              v-if="showSuggestions && filteredCustomers.length > 0"
              class="absolute z-40 w-full mt-1 rounded-xl border border-crm-border bg-white shadow-lg max-h-40 overflow-y-auto"
            >
              <button
                v-for="c in filteredCustomers"
                :key="c.name"
                class="w-full text-left px-3 py-2 text-sm text-crm-text hover:bg-crm-surface transition-colors"
                @mousedown.prevent="selectCustomer(c)"
              >
                <span class="font-medium">{{ c.customer_name || c.name }}</span>
                <span v-if="c.mobile_no" class="text-crm-text-secondary ml-2 text-xs">{{ c.mobile_no }}</span>
              </button>
            </div>
          </div>

          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('Tanggal') }}
            </label>
            <input
              v-model="newVisit.visit_date"
              type="date"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            />
          </div>

          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('Tujuan') }}
            </label>
            <select
              v-model="newVisit.purpose"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            >
              <option value="">{{ __('Pilih tujuan') }}</option>
              <option value="Survey">{{ __('Survey') }}</option>
              <option value="Collection">{{ __('Collection') }}</option>
              <option value="Promotion">{{ __('Promotion') }}</option>
              <option value="Follow-up">{{ __('Follow-up') }}</option>
              <option value="Evaluation">{{ __('Evaluation') }}</option>
              <option value="Lainnya">{{ __('Lainnya') }}</option>
            </select>
          </div>

          <div>
            <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
              {{ __('Catatan') }}
            </label>
            <textarea
              v-model="newVisit.notes"
              rows="3"
              :placeholder="__('Catatan tambahan...')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted resize-none"
            />
          </div>
        </div>

        <Button variant="solid" class="w-full mt-5" :loading="saving" :disabled="!newVisit.customer_name || !newVisit.visit_date" @click="addVisit">
          <template #prefix>
            <FeatherIcon name="calendar-plus" class="size-4" />
          </template>
          {{ __('Tambah Kunjungan') }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'

const mapContainer = ref(null)
const showForm = ref(false)
const loadingVisits = ref(false)
const saving = ref(false)
let map = null
let markers = []

const visits = ref([])
const allCustomers = ref([])
const filteredCustomers = ref([])
const showSuggestions = ref(false)

const newVisit = ref({
  customer: '',
  customer_name: '',
  visit_date: new Date().toISOString().split('T')[0],
  purpose: '',
  notes: '',
})

function statusBadgeClass(status) {
  if (status === 'Planned') return 'bg-blue-100 text-blue-700'
  if (status === 'Checked In') return 'bg-amber-100 text-amber-700'
  if (status === 'Checked Out') return 'bg-green-100 text-green-700'
  if (status === 'Cancelled') return 'bg-red-100 text-red-700'
  return 'bg-gray-100 text-gray-700'
}

async function fetchVisits() {
  loadingVisits.value = true
  try {
    visits.value = await call('crm.api.visit.list_visits')
    updateMapMarkers()
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || __('Gagal memuat kunjungan'))
  } finally {
    loadingVisits.value = false
  }
}

async function fetchCustomers() {
  try {
    allCustomers.value = await call('crm.api.visit.get_customers')
  } catch {
    // silent
  }
}

function onCustomerInput() {
  const text = newVisit.value.customer_name.trim()
  if (text.length < 2) {
    filteredCustomers.value = []
    showSuggestions.value = false
    newVisit.value.customer = ''
    return
  }
  const lower = text.toLowerCase()
  filteredCustomers.value = allCustomers.value.filter(
    (c) => (c.customer_name || c.name).toLowerCase().includes(lower)
  )
  showSuggestions.value = filteredCustomers.value.length > 0
}

function onCustomerFocus() {
  if (filteredCustomers.value.length > 0) {
    showSuggestions.value = true
  }
}

function onCustomerBlur() {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

function selectCustomer(c) {
  newVisit.value.customer = c.name
  newVisit.value.customer_name = c.customer_name || c.name
  showSuggestions.value = false
}

async function addVisit() {
  if (!newVisit.value.customer_name || !newVisit.value.visit_date) return
  saving.value = true
  try {
    await call('crm.api.visit.create_visit', {
      customer: newVisit.value.customer || newVisit.value.customer_name,
      visit_date: newVisit.value.visit_date,
      purpose: newVisit.value.purpose,
      notes: newVisit.value.notes,
    })
    toast.success(__('Kunjungan berhasil ditambahkan'))
    showForm.value = false
    newVisit.value = {
      customer: '',
      customer_name: '',
      visit_date: new Date().toISOString().split('T')[0],
      purpose: '',
      notes: '',
    }
    await fetchVisits()
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || __('Gagal menambah kunjungan'))
  } finally {
    saving.value = false
  }
}

async function initMap() {
  if (!mapContainer.value) return
  const L = await import('leaflet')
  map = L.map(mapContainer.value, {
    zoomControl: false,
    attributionControl: false,
  }).setView([-6.2088, 106.8456], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map)
  updateMapMarkers()
}

function updateMapMarkers() {
  if (!map) return
  import('leaflet').then((L) => {
    markers.forEach((m) => map.removeLayer(m))
    markers = []
    visits.value.forEach((v) => {
      const lat = parseFloat(v.gps_latitude)
      const lng = parseFloat(v.gps_longitude)
      if (!lat || !lng) return
      const color = v.status === 'Checked Out' || v.status === 'Completed'
        ? '#22c55e'
        : v.status === 'Cancelled'
          ? '#ef4444'
          : '#3b82f6'
      const marker = L.circleMarker([lat, lng], {
        radius: 7,
        fillColor: color,
        color: '#fff',
        weight: 2,
        fillOpacity: 0.9,
      }).addTo(map)
      marker.bindPopup(`<b>${v.customer_name || v.customer}</b><br/>${v.status}`)
      markers.push(marker)
    })
  })
}

onMounted(() => {
  initMap()
  fetchVisits()
  fetchCustomers()
})

onUnmounted(() => {
  if (map) { map.remove(); map = null }
})
</script>
