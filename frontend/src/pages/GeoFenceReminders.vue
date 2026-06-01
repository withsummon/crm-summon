<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <!-- Header Page -->
    <div class="bg-white px-4 pb-3 pt-3 border-b border-crm-border flex items-center justify-between">
      <div>
        <h1 class="text-lg font-semibold text-crm-text">{{ __('Geo-Fence Reminders') }}</h1>
        <p class="text-xs text-crm-text-secondary mt-0.5">{{ __('Pengingat berbasis lokasi & hari spesial') }}</p>
      </div>
      <!-- GPS Status indicator -->
      <div class="flex items-center gap-1.5 bg-crm-surface px-2.5 py-1 rounded-full border border-crm-border">
        <div class="size-2 rounded-full animate-pulse" :class="gpsActive ? 'bg-green-500' : 'bg-amber-400'" />
        <span class="text-[10px] font-medium text-crm-text-secondary">
          {{ gpsActive ? (simulated ? __('Simulasi GPS') : __('GPS Aktif')) : __('GPS Standby') }}
        </span>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      
      <!-- UAT Geolocation Simulation Control Panel (Harmonious Teal/Teal-Gray Premium Card) -->
      <div class="rounded-xl border border-crm-teal/30 bg-gradient-to-br from-crm-teal/5 to-white p-4 shadow-sm space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <FeatherIcon name="compass" class="size-4.5 text-crm-teal" />
            <h2 class="text-xs font-semibold uppercase tracking-wider text-crm-teal">{{ __('Simulasi Lokasi Andi (RM)') }}</h2>
          </div>
          <span v-if="currentPosition" class="text-[10px] font-mono text-crm-text-secondary bg-white px-2 py-0.5 rounded border border-crm-border">
            {{ currentPosition.lat.toFixed(5) }}, {{ currentPosition.lng.toFixed(5) }}
          </span>
        </div>
        <p class="text-xs text-crm-text-secondary leading-relaxed">
          {{ __('Gunakan tombol simulasi di bawah untuk menempatkan posisi GPS Andi di area Sudirman, berdekatan dengan koordinat PT Indofood atau nasabah terdaftar guna memicu alarm momen spesial secara instan.') }}
        </p>
        <div class="flex gap-2">
          <Button variant="solid" size="sm" class="flex-1 bg-crm-teal hover:bg-crm-teal/90 border-crm-teal" @click="simulateNearNasabah('indofood')">
            <template #prefix>
              <FeatherIcon name="map-pin" class="size-3.5" />
            </template>
            {{ __('Dekat PT Indofood') }}
          </Button>
          <Button variant="solid" size="sm" class="flex-1 bg-indigo-600 hover:bg-indigo-700 border-indigo-600" @click="simulateNearNasabah('anisa')">
            <template #prefix>
              <FeatherIcon name="user" class="size-3.5" />
            </template>
            {{ __('Dekat Anisa Putri') }}
          </Button>
          <Button v-if="currentPosition" variant="outline" size="sm" class="shrink-0" @click="resetGPS">
            <FeatherIcon name="refresh-cw" class="size-3.5" />
          </Button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="space-y-2 pt-2">
        <div v-for="i in 3" :key="i" class="animate-pulse rounded-xl bg-white p-4 border border-crm-border h-24" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-xl bg-red-50 border border-red-200 p-4 text-center">
        <p class="text-xs text-red-600 mb-2">{{ error }}</p>
        <Button variant="outline" size="sm" @click="loadReminders">{{ __('Coba Lagi') }}</Button>
      </div>

      <!-- Empty State -->
      <div v-else-if="reminders.length === 0" class="py-16 text-center bg-white rounded-xl border border-crm-border p-6 shadow-sm">
        <FeatherIcon name="navigation" class="size-10 text-crm-muted mx-auto mb-2" />
        <p class="text-sm font-medium text-crm-text">{{ __('Belum ada pengingat lokasi') }}</p>
        <p class="text-xs text-crm-text-secondary mt-1 mb-4">{{ __('Aktifkan pengingat berbasis lokasi untuk mendeteksi momen spesial nasabah.') }}</p>
        <Button variant="solid" class="bg-crm-teal border-crm-teal" @click="showForm = true">
          <template #prefix>
            <FeatherIcon name="plus" class="size-4" />
          </template>
          {{ __('Tambahkan Pengingat Baru') }}
        </Button>
      </div>

      <!-- Reminders List -->
      <div v-else class="space-y-2.5">
        <div v-for="reminder in reminders" :key="reminder.name" class="rounded-xl bg-white p-4 shadow-sm border border-crm-border transition-all hover:border-crm-teal/40">
          <div class="flex items-start justify-between mb-1.5">
            <div class="flex items-center gap-2 min-w-0 flex-1">
              <FeatherIcon name="map-pin" class="size-4.5 text-crm-teal shrink-0" />
              <div class="min-w-0">
                <h3 class="text-sm font-semibold text-crm-text truncate">{{ reminder.location_name }}</h3>
                <span v-if="reminder.customer" class="inline-flex items-center mt-0.5 text-[10px] font-medium bg-crm-surface text-crm-teal px-2 py-0.5 rounded-full border border-crm-teal/20">
                  <FeatherIcon name="user" class="size-2.5 mr-1" />
                  {{ reminder.customer }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0 ml-2">
              <span class="text-[10px] font-bold rounded-full px-2 py-0.5 uppercase tracking-wider" :class="reminder.is_active ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-gray-100 text-gray-500 border border-gray-200'">
                {{ reminder.is_active ? __('Aktif') : __('Nonaktif') }}
              </span>
            </div>
          </div>
          
          <p v-if="reminder.address" class="text-xs text-crm-text-secondary mb-2 truncate pl-6">{{ reminder.address }}</p>
          <p v-if="reminder.note" class="text-xs text-crm-text-secondary bg-crm-surface p-2 rounded-lg pl-3 italic mb-2 border-l-2 border-crm-teal/30">{{ reminder.note }}</p>

          <div class="flex items-center justify-between mt-3 pt-2 border-t border-crm-border/60 pl-6">
            <div class="flex items-center gap-3 text-xs text-crm-muted font-mono">
              <span class="bg-crm-surface px-2 py-0.5 rounded border border-crm-border">Radius: {{ reminder.radius_meters }}m</span>
              <span v-if="currentPosition && reminder.latitude" class="text-crm-teal font-medium">
                {{ getDistanceText(reminder) }}
              </span>
            </div>
            <div class="flex items-center gap-3">
              <button class="text-xs text-crm-teal font-bold hover:underline" @click="toggleReminder(reminder)">
                {{ reminder.is_active ? __('Nonaktifkan') : __('Aktifkan') }}
              </button>
              <button class="text-xs text-red-500 font-bold hover:underline" @click="deleteReminder(reminder)">
                {{ __('Hapus') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Floating Action Button -->
    <button class="fixed bottom-6 right-6 z-20 flex size-12 items-center justify-center rounded-full bg-crm-teal text-white shadow-lg active:scale-95 transition-transform" @click="showForm = true">
      <FeatherIcon name="plus" class="size-6" />
    </button>

    <!-- PROXIMITY ALERT POPUP MODAL (Wow Birthday Proximity Alert Card with BNI Teal branding) -->
    <TransitionRoot :show="showProximityAlert">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <TransitionChild as="template" enter="transition-opacity duration-200" enter-from="opacity-0" enter-to="opacity-100" leave="transition-opacity duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-black/40 backdrop-blur-sm" @click="showProximityAlert = false" />
        </TransitionChild>
        
        <TransitionChild as="template" enter="transition-all duration-300 ease-out" enter-from="opacity-0 scale-95" enter-to="opacity-100 scale-100" leave="transition-all duration-200 ease-in" leave-from="opacity-100 scale-100" leave-to="opacity-0 scale-95">
          <div v-if="activeAlertReminder" class="relative w-full max-w-sm rounded-2xl bg-white border border-crm-teal/40 p-5 shadow-2xl overflow-hidden">
            <!-- Top Premium Teal background accents -->
            <div class="absolute top-0 inset-x-0 h-2 bg-gradient-to-r from-crm-teal to-indigo-600" />
            
            <div class="flex items-center gap-3 mb-3.5 mt-2">
              <div class="size-10 rounded-xl bg-crm-teal/10 flex items-center justify-center shrink-0">
                <FeatherIcon name="gift" class="size-5.5 text-crm-teal animate-bounce" />
              </div>
              <div>
                <h3 class="text-xs font-bold text-crm-teal uppercase tracking-wider">{{ __('Momen Penting Terdeteksi') }}</h3>
                <p class="text-sm font-bold text-crm-text">{{ __('Peringatan Geo-Fence!') }}</p>
              </div>
            </div>

            <!-- Proximity information -->
            <div class="bg-crm-teal/5 rounded-xl p-3.5 border border-crm-teal/20 space-y-2 mb-4">
              <p class="text-xs text-crm-text leading-relaxed">
                {{ __('Andi, posisi Anda saat ini terdeteksi sangat dekat dengan lokasi nasabah:') }}
              </p>
              <div class="font-semibold text-sm text-crm-text flex items-center gap-1.5 pl-1">
                <FeatherIcon name="user" class="size-4 text-crm-teal" />
                {{ activeAlertReminder.customer || activeAlertReminder.location_name }}
              </div>
              <div class="text-xs text-crm-text-secondary flex items-center gap-1.5 pl-1">
                <FeatherIcon name="map-pin" class="size-3.5 text-crm-muted" />
                {{ activeAlertReminder.address || __('Lokasi Terdaftar') }}
              </div>
              <div class="text-[11px] text-crm-teal font-mono font-medium pl-1 bg-white inline-block px-2 py-0.5 rounded border border-crm-teal/20 mt-1">
                {{ __('Jarak: ') }}{{ activeAlertReminder.distance }}{{ __(' meter') }}
              </div>
            </div>

            <!-- Special message (Birthday simulated highlight) -->
            <div class="space-y-2.5 mb-5 pl-1">
              <div class="flex items-center gap-2">
                <span class="inline-flex size-2 rounded-full bg-red-500" />
                <span class="text-xs font-bold text-red-600 uppercase tracking-wider">{{ __('HARI SPESIAL HARI INI') }}</span>
              </div>
              <p class="text-xs text-crm-text leading-relaxed">
                {{ __('Hari ini adalah ') }}<strong class="text-crm-text">{{ __('Hari Ulang Tahun') }}</strong>{{ __(' beliau! Berikan sentuhan personal hangat sebagai Relationship Manager profesional sekarang juga.') }}
              </p>
              <div class="bg-crm-surface p-2.5 rounded-lg border border-crm-border text-xs text-crm-text-secondary italic pl-3 border-l-4 border-crm-teal leading-relaxed">
                {{ __('"Selamat Ulang Tahun! Semoga sukses dan sehat selalu. Terima kasih atas loyalitas bersama BNI..."') }}
              </div>
            </div>

            <!-- Modal CTAs -->
            <div class="flex gap-2">
              <Button variant="ghost" class="flex-1 text-xs" @click="showProximityAlert = false">
                {{ __('Tutup') }}
              </Button>
              <Button variant="solid" class="flex-1 bg-crm-teal border-crm-teal text-xs" @click="handleSendPersonalTouch(activeAlertReminder)">
                <template #prefix>
                  <FeatherIcon name="send" class="size-3.5" />
                </template>
                {{ __('Kirim Ucapan WA') }}
              </Button>
            </div>
          </div>
        </TransitionChild>
      </div>
    </TransitionRoot>

    <!-- Create Reminder Sheet Modal -->
    <TransitionRoot :show="showForm">
      <div class="fixed inset-0 z-50 flex items-end">
        <TransitionChild as="template" enter="transition-opacity duration-200" enter-from="opacity-0" enter-to="opacity-100" leave="transition-opacity duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-black/30" @click="showForm = false" />
        </TransitionChild>
        <TransitionChild as="template" enter="transition-transform duration-300 ease-out" enter-from="translate-y-full" enter-to="translate-y-0" leave="transition-transform duration-200 ease-in" leave-from="translate-y-0" leave-to="translate-y-full">
          <div class="relative w-full rounded-t-2xl bg-white px-4 pb-8 pt-5 shadow-xl">
            <div class="mx-auto mb-4 h-1 w-10 rounded-full bg-gray-300" />
            <h2 class="text-base font-semibold text-crm-text mb-4">{{ __('Tambahkan Pengingat Baru') }}</h2>
            <div class="space-y-3">
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Pilih Nasabah (Customer)') }}</label>
                <select v-model="newReminder.customer" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal" @change="onCustomerSelected">
                  <option value="">{{ __('-- Hubungkan dengan Nasabah (Opsional) --') }}</option>
                  <option v-for="c in customersList" :key="c.name" :value="c.name">{{ c.customer_name }}</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Nama Lokasi') }}</label>
                <input v-model="newReminder.location_name" type="text" :placeholder="__('Nama lokasi, misal: Kantor Pusat Indofood')" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal" />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Alamat') }}</label>
                <input v-model="newReminder.address" type="text" :placeholder="__('Alamat lengkap')" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal" />
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Radius') }}</label>
                  <select v-model="newReminder.radius_meters" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal">
                    <option :value="100">100m</option>
                    <option :value="200">200m</option>
                    <option :value="500">500m</option>
                    <option :value="1000">1km</option>
                    <option :value="2000">2km</option>
                  </select>
                </div>
                <div>
                  <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Kategori Momen') }}</label>
                  <select class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal">
                    <option value="birthday">{{ __('Ulang Tahun') }}</option>
                    <option value="anniversary">{{ __('Anniversary') }}</option>
                    <option value="covenant">{{ __('Covenant Due') }}</option>
                    <option value="visit">{{ __('Rapat Kerja') }}</option>
                  </select>
                </div>
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Catatan') }}</label>
                <textarea v-model="newReminder.note" rows="2" :placeholder="__('Catatan penting untuk pengingat lokasi...')" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal resize-none" />
              </div>
            </div>
            <div class="flex gap-2 mt-5">
              <Button variant="ghost" class="flex-1" @click="showForm = false">{{ __('Batal') }}</Button>
              <Button variant="solid" class="flex-1 bg-crm-teal border-crm-teal" :loading="saving" :disabled="!newReminder.location_name" @click="saveReminder">{{ __('Simpan') }}</Button>
            </div>
          </div>
        </TransitionChild>
      </div>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'
import { TransitionRoot, TransitionChild } from '@headlessui/vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const reminders = ref([])
const customersList = ref([])
const showForm = ref(false)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const newReminder = ref({
  customer: '',
  location_name: '',
  address: '',
  radius_meters: 500,
  note: '',
})

// GPS & Proximity alert simulation/states
const currentPosition = ref(null)
const gpsActive = ref(false)
const simulated = ref(false)
const showProximityAlert = ref(false)
const activeAlertReminder = ref(null)
let watchId = null

async function loadReminders() {
  loading.value = true
  error.value = ''
  try {
    reminders.value = await call('crm.api.geo.list_reminders')
    checkProximity()
  } catch (err) {
    error.value = err.messages?.[0] || __('Gagal memuat pengingat')
  } finally {
    loading.value = false
  }
}

async function loadCustomers() {
  try {
    customersList.value = await call('crm.api.omnichannel.search_customers', { query: '' })
  } catch (err) {
    console.error('Gagal mengambil daftar nasabah:', err)
  }
}

function onCustomerSelected() {
  if (!newReminder.value.customer) return
  const cust = customersList.value.find(c => c.name === newReminder.value.customer)
  if (cust) {
    newReminder.value.location_name = `Momen Spesial: ${cust.customer_name}`
    newReminder.value.address = cust.registered_address || `Area Terdaftar Nasabah ${cust.customer_name}`
    newReminder.value.note = `Ulang tahun ${cust.customer_name}. Beliau menyukai produk KMK BNI.`
  }
}

async function saveReminder() {
  if (!newReminder.value.location_name) return
  saving.value = true
  try {
    await call('crm.api.geo.create_reminder', {
      location_name: newReminder.value.location_name,
      customer: newReminder.value.customer,
      address: newReminder.value.address,
      radius_meters: newReminder.value.radius_meters,
      note: newReminder.value.note,
    })
    toast.success(__('Pengingat berhasil ditambahkan'))
    showForm.value = false
    newReminder.value = { customer: '', location_name: '', address: '', radius_meters: 500, note: '' }
    loadReminders()
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal menambah pengingat'))
  } finally {
    saving.value = false
  }
}

async function toggleReminder(reminder) {
  try {
    const result = await call('crm.api.geo.toggle_reminder', {
      reminder_id: reminder.name,
      is_active: !reminder.is_active,
    })
    reminder.is_active = result.is_active
    toast.success(result.is_active ? __('Pengingat diaktifkan') : __('Pengingat dinonaktifkan'))
    checkProximity()
  } catch {
    toast.error(__('Gagal mengubah status'))
  }
}

async function deleteReminder(reminder) {
  try {
    await call('crm.api.geo.delete_reminder', { reminder_id: reminder.name })
    reminders.value = reminders.value.filter(r => r.name !== reminder.name)
    toast.success(__('Pengingat berhasil dihapus'))
  } catch {
    toast.error(__('Gagal menghapus pengingat'))
  }
}

// Haversine formula to compute distance in meters
function getDistance(lat1, lon1, lat2, lon2) {
  if (!lat1 || !lon1 || !lat2 || !lon2) return null
  const R = 6371e3 // metres
  const φ1 = lat1 * Math.PI / 180
  const φ2 = lat2 * Math.PI / 180
  const Δφ = (lat2 - lat1) * Math.PI / 180
  const Δλ = (lon2 - lon1) * Math.PI / 180

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  return Math.round(R * c) // meters
}

function getDistanceText(reminder) {
  if (!currentPosition.value || !reminder.latitude) return ''
  const dist = getDistance(currentPosition.value.lat, currentPosition.value.lng, reminder.latitude, reminder.longitude)
  if (dist === null) return ''
  return dist > 1000 ? `${(dist / 1000).toFixed(1)}km` : `${dist}m`
}

function checkProximity() {
  if (!currentPosition.value || reminders.value.length === 0) return
  
  for (const reminder of reminders.value) {
    if (!reminder.is_active || !reminder.latitude || !reminder.longitude) continue
    
    const dist = getDistance(
      currentPosition.value.lat,
      currentPosition.value.lng,
      reminder.latitude,
      reminder.longitude
    )
    
    if (dist !== null && dist <= reminder.radius_meters) {
      // Proximity matched! Trigger the awesome Special Birthday popup modal
      activeAlertReminder.value = {
        ...reminder,
        distance: dist
      }
      showProximityAlert.value = true
      // Play a premium micro-vibrate or sound alert inside Mobile WebView if available
      if ('vibrate' in navigator) navigator.vibrate([100, 50, 100])
      return // Trigger one notification popup at a time for focus
    }
  }
}

// UAT Location Simulator Hooks
function simulateNearNasabah(type) {
  simulated.value = true
  gpsActive.value = true
  if (watchId) {
    navigator.geolocation.clearWatch(watchId)
    watchId = null
  }
  
  if (type === 'indofood') {
    // Put Andi's RM coordinates within 180 meters of PT Indofood's default coordinate (-6.2210, 106.8180)
    currentPosition.value = {
      lat: -6.2202,
      lng: 106.8172,
      accuracy: 10
    }
    toast.success(__('Simulasi GPS: Andi diposisikan dekat PT Indofood Tbk (UAT)'))
  } else if (type === 'anisa') {
    // Put Andi's coordinates close to Anisa Putri (-6.2185, 106.8150)
    currentPosition.value = {
      lat: -6.2189,
      lng: 106.8146,
      accuracy: 12
    }
    toast.success(__('Simulasi GPS: Andi diposisikan dekat kediaman Anisa Putri'))
  }
  checkProximity()
}

function resetGPS() {
  simulated.value = false
  currentPosition.value = null
  startGPS()
}

function startGPS() {
  if (!navigator.geolocation) {
    gpsActive.value = false
    return
  }
  gpsActive.value = true
  watchId = navigator.geolocation.watchPosition(
    (pos) => {
      if (simulated.value) return // Don't override simulator in UAT
      currentPosition.value = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        accuracy: Math.round(pos.coords.accuracy)
      }
      checkProximity()
    },
    () => {
      gpsActive.value = false
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 5000 }
  )
}

function handleSendPersonalTouch(reminder) {
  showProximityAlert.value = false
  // Pre-fill a sweet approved personal greeting draft and navigate to omnichannel conversation page
  toast.success(__('Membuka Omnichannel untuk mengirim ucapan selamat ulang tahun!'))
  // Strip special characters and redirect to Omnichannel Workspace
  router.push({ name: 'Mobile Omnichannel Chat' })
}

onMounted(() => {
  loadReminders()
  loadCustomers()
  startGPS()
})

onUnmounted(() => {
  if (watchId) navigator.geolocation.clearWatch(watchId)
})
</script>
