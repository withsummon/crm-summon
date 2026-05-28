<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <h1 class="text-lg font-semibold text-crm-text">{{ __('Geo-Fence') }}</h1>
      <p class="text-xs text-crm-text-secondary mt-0.5">{{ __('Pengingat berbasis lokasi') }}</p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-3">
      <div v-if="loading" class="space-y-2 pt-2">
        <div v-for="i in 3" :key="i" class="animate-pulse rounded-xl bg-white p-4 border border-crm-border h-24" />
      </div>

      <div v-else-if="error" class="rounded-xl bg-red-50 border border-red-200 p-4 text-center">
        <p class="text-xs text-red-600 mb-2">{{ error }}</p>
        <Button variant="outline" size="sm" @click="loadReminders">{{ __('Coba Lagi') }}</Button>
      </div>

      <div v-else-if="reminders.length === 0" class="py-16 text-center">
        <FeatherIcon name="navigation" class="size-10 text-crm-muted mx-auto mb-2" />
        <p class="text-sm font-medium text-crm-text">{{ __('Belum ada pengingat lokasi') }}</p>
        <p class="text-xs text-crm-text-secondary mt-1">{{ __('Tambahkan pengingat baru') }}</p>
      </div>

      <div v-else class="space-y-2">
        <div v-for="reminder in reminders" :key="reminder.name" class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2 min-w-0 flex-1">
              <FeatherIcon name="map-pin" class="size-4 text-crm-teal shrink-0" />
              <h3 class="text-sm font-medium text-crm-text truncate">{{ reminder.location_name }}</h3>
            </div>
            <div class="flex items-center gap-2 shrink-0 ml-2">
              <span class="text-[10px] font-semibold rounded-full px-2 py-0.5" :class="reminder.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'">
                {{ reminder.is_active ? __('Aktif') : __('Nonaktif') }}
              </span>
            </div>
          </div>
          <p v-if="reminder.address" class="text-xs text-crm-text-secondary mb-1 truncate">{{ reminder.address }}</p>
          <div class="flex items-center justify-between mt-2">
            <div class="flex items-center gap-3 text-xs text-crm-muted">
              <span>{{ reminder.radius_meters }}m</span>
            </div>
            <div class="flex items-center gap-2">
              <button class="text-xs text-crm-teal font-medium" @click="toggleReminder(reminder)">
                {{ reminder.is_active ? __('Nonaktifkan') : __('Aktifkan') }}
              </button>
              <button class="text-xs text-red-500 font-medium" @click="deleteReminder(reminder)">
                {{ __('Hapus') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <button class="fixed bottom-6 right-6 z-20 flex size-12 items-center justify-center rounded-full bg-crm-teal text-white shadow-lg active:scale-95 transition-transform" @click="showForm = true">
      <FeatherIcon name="plus" class="size-6" />
    </button>

    <TransitionRoot :show="showForm">
      <div class="fixed inset-0 z-50 flex items-end">
        <TransitionChild as="template" enter="transition-opacity duration-200" enter-from="opacity-0" enter-to="opacity-100" leave="transition-opacity duration-200" leave-from="opacity-100" leave-to="opacity-0">
          <div class="fixed inset-0 bg-black/30" @click="showForm = false" />
        </TransitionChild>
        <TransitionChild as="template" enter="transition-transform duration-300 ease-out" enter-from="translate-y-full" enter-to="translate-y-0" leave="transition-transform duration-200 ease-in" leave-from="translate-y-0" leave-to="translate-y-full">
          <div class="relative w-full rounded-t-2xl bg-white px-4 pb-8 pt-5 shadow-xl">
            <div class="mx-auto mb-4 h-1 w-10 rounded-full bg-gray-300" />
            <h2 class="text-base font-semibold text-crm-text mb-4">{{ __('Pengingat Baru') }}</h2>
            <div class="space-y-3">
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Nama Lokasi') }}</label>
                <input v-model="newReminder.location_name" type="text" :placeholder="__('Nama lokasi')" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal" />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Alamat') }}</label>
                <input v-model="newReminder.address" type="text" :placeholder="__('Alamat lokasi')" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal" />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Radius') }}</label>
                <select v-model="newReminder.radius_meters" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal">
                  <option :value="100">100m</option>
                  <option :value="200">200m</option>
                  <option :value="500">500m</option>
                  <option :value="1000">1km</option>
                  <option :value="2000">2km</option>
                  <option :value="5000">5km</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">{{ __('Catatan') }}</label>
                <textarea v-model="newReminder.note" rows="2" :placeholder="__('Catatan...')" class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm outline-none focus:border-crm-teal resize-none" />
              </div>
            </div>
            <div class="flex gap-2 mt-5">
              <Button variant="ghost" class="flex-1" @click="showForm = false">{{ __('Batal') }}</Button>
              <Button variant="solid" class="flex-1" :loading="saving" :disabled="!newReminder.location_name" @click="saveReminder">{{ __('Simpan') }}</Button>
            </div>
          </div>
        </TransitionChild>
      </div>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'
import { TransitionRoot, TransitionChild } from '@headlessui/vue'

const reminders = ref([])
const showForm = ref(false)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const newReminder = ref({
  location_name: '',
  address: '',
  radius_meters: 500,
  note: '',
})

async function loadReminders() {
  loading.value = true
  error.value = ''
  try {
    reminders.value = await call('crm.api.geo.list_reminders')
  } catch (err) {
    error.value = err.messages?.[0] || __('Gagal memuat pengingat')
  } finally {
    loading.value = false
  }
}

async function saveReminder() {
  if (!newReminder.value.location_name) return
  saving.value = true
  try {
    await call('crm.api.geo.create_reminder', {
      location_name: newReminder.value.location_name,
      address: newReminder.value.address,
      radius_meters: newReminder.value.radius_meters,
      note: newReminder.value.note,
    })
    toast.success(__('Pengingat berhasil ditambahkan'))
    showForm.value = false
    newReminder.value = { location_name: '', address: '', radius_meters: 500, note: '' }
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

onMounted(loadReminders)
</script>
