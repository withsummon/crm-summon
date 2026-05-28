<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Pengeluaran & Perjalanan') }}
        </h1>
      </div>
    </div>

    <div class="flex gap-1 bg-white px-4 pb-3">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="flex-1 rounded-lg py-2 text-sm font-medium transition-colors"
        :class="activeTab === tab.key
          ? 'bg-crm-teal text-white'
          : 'bg-crm-surface text-crm-text-secondary hover:text-crm-text'"
        @click="activeTab = tab.key"
      >
        <FeatherIcon :name="tab.icon" class="size-4 mx-auto mb-0.5" />
        {{ tab.label }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div v-if="loading" class="space-y-3">
        <div class="animate-pulse rounded-xl bg-crm-surface h-20" />
        <div class="animate-pulse rounded-xl bg-crm-surface h-20" />
        <div class="animate-pulse rounded-xl bg-crm-surface h-20" />
      </div>

      <div v-else-if="error" class="rounded-xl bg-red-50 border border-red-200 p-4 text-center">
        <p class="text-xs text-red-600 mb-2">{{ error }}</p>
        <Button variant="outline" size="sm" @click="loadAll">{{ __('Coba Lagi') }}</Button>
      </div>

      <template v-if="!loading && !error && activeTab === 'expenses'">
        <div v-if="expenses.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
          <FeatherIcon name="credit-card" class="size-12 text-crm-muted mb-4" />
          <p class="text-sm text-crm-text-secondary max-w-xs">
            {{ __('Belum ada catatan pengeluaran') }}
          </p>
        </div>

        <template v-else>
          <div
            v-for="expense in expenses"
            :key="expense.name"
            class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-2"
          >
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-3 flex-1 min-w-0">
                <div class="mt-0.5 rounded-lg p-2 shrink-0" :class="getCategoryMeta(expense.category).bg">
                  <FeatherIcon :name="getCategoryMeta(expense.category).icon" class="size-4" :class="getCategoryMeta(expense.category).color" />
                </div>
                <div class="min-w-0 flex-1">
                  <h3 class="text-sm font-medium text-crm-text">{{ expense.description }}</h3>
                  <p class="text-xs text-crm-text-secondary mt-0.5">{{ expense.expense_date }}</p>
                </div>
              </div>
              <div class="text-right shrink-0">
                <p class="text-sm font-semibold text-red-500">-Rp {{ formatAmount(expense.amount) }}</p>
                <span
                  class="inline-block rounded-full px-2 py-0.5 text-[11px] font-medium mt-1"
                  :class="statusClass(expense.status)"
                >
                  {{ expense.status }}
                </span>
              </div>
            </div>
          </div>
        </template>
      </template>

      <template v-if="!loading && !error && activeTab === 'mileage'">
        <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
          <div class="grid grid-cols-2 gap-4">
            <div class="text-center">
              <p class="text-2xl font-bold text-crm-teal">{{ totalDistance }} km</p>
              <p class="text-xs text-crm-text-secondary">{{ __('Total Jarak') }}</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-crm-teal">Rp {{ formatAmount(totalCost) }}</p>
              <p class="text-xs text-crm-text-secondary">{{ __('Total Biaya') }}</p>
            </div>
          </div>
          <p class="text-xs text-center text-crm-muted mt-2">
            {{ __('Tarif: Rp 4.500/km') }}
          </p>
        </div>

        <div v-if="mileageTrips.length === 0" class="flex flex-col items-center justify-center py-16 text-center">
          <FeatherIcon name="map" class="size-12 text-crm-muted mb-4" />
          <p class="text-sm text-crm-text-secondary max-w-xs">
            {{ __('Belum ada catatan perjalanan') }}
          </p>
        </div>

        <template v-else>
          <div
            v-for="trip in mileageTrips"
            :key="trip.name"
            class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-2"
          >
            <div class="flex items-start gap-3">
              <div class="mt-0.5 rounded-lg bg-crm-surface p-2 shrink-0">
                <FeatherIcon name="navigation" class="size-4 text-crm-teal" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-1 text-sm">
                  <span class="text-crm-text font-medium truncate">{{ trip.start_location }}</span>
                  <FeatherIcon name="arrow-right" class="size-3 text-crm-muted shrink-0" />
                  <span class="text-crm-text font-medium truncate">{{ trip.end_location }}</span>
                </div>
                <p class="text-xs text-crm-text-secondary mt-0.5">{{ trip.trip_date }}</p>
                <div class="flex items-center gap-3 mt-1.5">
                  <span class="text-xs font-medium text-crm-text">{{ trip.distance_km }} km</span>
                  <span class="text-xs text-crm-muted">|</span>
                  <span class="text-xs font-medium text-crm-text">Rp {{ formatAmount(trip.cost) }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </template>
    </div>

    <div class="sticky bottom-6 flex justify-center px-4">
      <button
        class="flex items-center gap-2 rounded-full bg-crm-teal px-6 py-3 text-sm font-medium text-white shadow-lg hover:bg-crm-teal/90 transition-colors"
        @click="showAddForm = true"
      >
        <FeatherIcon name="plus" class="size-4" />
        {{ activeTab === 'expenses' ? __('Tambah Pengeluaran') : __('Tambah Perjalanan') }}
      </button>
    </div>

    <Transition name="slide-up">
      <div
        v-if="showAddForm"
        class="fixed inset-0 z-50 flex flex-col justify-end bg-black/30"
        @click.self="showAddForm = false"
      >
        <div class="rounded-t-2xl bg-white px-4 pb-8 pt-6 space-y-4 max-h-[80vh] overflow-y-auto">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-semibold text-crm-text">
              {{ activeTab === 'expenses' ? __('Pengeluaran Baru') : __('Perjalanan Baru') }}
            </h2>
            <button class="rounded-lg p-1 text-crm-muted hover:bg-crm-surface" @click="showAddForm = false">
              <FeatherIcon name="x" class="size-5" />
            </button>
          </div>

          <template v-if="activeTab === 'expenses'">
            <div class="space-y-3">
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Kategori') }} <span class="text-red-500">*</span>
                </label>
                <select
                  v-model="expenseForm.category"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
                >
                  <option value="Bensin">{{ __('Bensin') }}</option>
                  <option value="Makan">{{ __('Makan') }}</option>
                  <option value="Parkir">{{ __('Parkir') }}</option>
                  <option value="Tol">{{ __('Tol') }}</option>
                  <option value="Lainnya">{{ __('Lainnya') }}</option>
                </select>
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Deskripsi') }} <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="expenseForm.description"
                  type="text"
                  :placeholder="__('Contoh: Bensin Pertalite')"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
                />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Jumlah (Rp)') }} <span class="text-red-500">*</span>
                </label>
                <input
                  v-model.number="expenseForm.amount"
                  type="number"
                  min="0"
                  :placeholder="__('50000')"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
                />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Tanggal') }}
                </label>
                <input
                  v-model="expenseForm.date"
                  type="date"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
                />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Catatan') }}
                </label>
                <textarea
                  v-model="expenseForm.notes"
                  rows="2"
                  :placeholder="__('Catatan tambahan...')"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted resize-none"
                />
              </div>
            </div>
            <Button
              variant="solid"
              class="w-full"
              :loading="saving"
              :disabled="!expenseForm.description || !expenseForm.amount"
              @click="saveExpense"
            >
              {{ __('Simpan Pengeluaran') }}
            </Button>
          </template>

          <template v-else>
            <div class="space-y-3">
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Lokasi Awal') }} <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="mileageForm.start"
                  type="text"
                  :placeholder="__('Contoh: Kantor Cabang Sudirman')"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
                />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Lokasi Akhir') }} <span class="text-red-500">*</span>
                </label>
                <input
                  v-model="mileageForm.end"
                  type="text"
                  :placeholder="__('Contoh: Nasabah PT Maju Jaya')"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
                />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Jarak (km)') }} <span class="text-red-500">*</span>
                </label>
                <input
                  v-model.number="mileageForm.distance"
                  type="number"
                  min="0"
                  step="0.1"
                  :placeholder="__('12.5')"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
                />
              </div>
              <div>
                <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
                  {{ __('Tanggal') }}
                </label>
                <input
                  v-model="mileageForm.date"
                  type="date"
                  class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
                />
              </div>
            </div>
            <Button
              variant="solid"
              class="w-full"
              :loading="saving"
              :disabled="!mileageForm.start || !mileageForm.end || !mileageForm.distance"
              @click="saveMileage"
            >
              {{ __('Simpan Perjalanan') }}
            </Button>
          </template>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { FeatherIcon, Button, call, toast } from 'frappe-ui'

const loading = ref(true)
const error = ref('')
const saving = ref(false)
const activeTab = ref('expenses')
const showAddForm = ref(false)

const tabs = [
  { key: 'expenses', label: __('Pengeluaran'), icon: 'credit-card' },
  { key: 'mileage', label: __('Perjalanan'), icon: 'map' },
]

const expenses = ref([])
const mileageTrips = ref([])

const expenseForm = ref({
  category: 'Bensin',
  description: '',
  amount: null,
  date: new Date().toISOString().split('T')[0],
  notes: '',
})

const mileageForm = ref({
  start: '',
  end: '',
  distance: null,
  date: new Date().toISOString().split('T')[0],
})



const totalDistance = computed(() => {
  return mileageTrips.value.reduce((sum, t) => sum + (t.distance_km || 0), 0).toFixed(1)
})

const totalCost = computed(() => {
  return mileageTrips.value.reduce((sum, t) => sum + (t.cost || 0), 0)
})

function getCategoryMeta(category) {
  const map = {
    Bensin: { icon: 'fuel', bg: 'bg-orange-50', color: 'text-orange-600' },
    Makan: { icon: 'coffee', bg: 'bg-yellow-50', color: 'text-yellow-600' },
    Parkir: { icon: 'map-pin', bg: 'bg-blue-50', color: 'text-blue-600' },
    Tol: { icon: 'credit-card', bg: 'bg-purple-50', color: 'text-purple-600' },
    Lainnya: { icon: 'more-horizontal', bg: 'bg-crm-surface', color: 'text-crm-text-secondary' },
  }
  return map[category] || { icon: 'more-horizontal', bg: 'bg-crm-surface', color: 'text-crm-text-secondary' }
}

function formatAmount(amount) {
  return Number(amount || 0).toLocaleString('id-ID')
}

function statusClass(status) {
  if (status === 'Approved') return 'bg-green-50 text-green-700'
  if (status === 'Rejected') return 'bg-red-50 text-red-600'
  return 'bg-yellow-50 text-yellow-700'
}

function resetExpenseForm() {
  expenseForm.value = {
    category: 'Bensin',
    description: '',
    amount: null,
    date: new Date().toISOString().split('T')[0],
    notes: '',
  }
}

function resetMileageForm() {
  mileageForm.value = {
    start: '',
    end: '',
    distance: null,
    date: new Date().toISOString().split('T')[0],
  }
}

async function loadExpenses() {
  try {
    expenses.value = await call('crm.api.expense.list_expenses')
  } catch { /* silent */ }
}

async function loadMileage() {
  try {
    mileageTrips.value = await call('crm.api.expense.list_mileage_trips')
  } catch { /* silent */ }
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadExpenses(), loadMileage()])
  } catch (err) {
    error.value = err.messages?.[0] || __('Gagal memuat data')
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)

async function saveExpense() {
  if (!expenseForm.value.description || !expenseForm.value.amount) return
  saving.value = true
  try {
    await call('crm.api.expense.create_expense', {
      category: expenseForm.value.category,
      description: expenseForm.value.description,
      amount: expenseForm.value.amount,
      expense_date: expenseForm.value.date,
      notes: expenseForm.value.notes,
    })
    toast.success(__('Pengeluaran berhasil dicatat'))
    showAddForm.value = false
    resetExpenseForm()
    loadExpenses()
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal mencatat pengeluaran'))
  } finally {
    saving.value = false
  }
}

async function saveMileage() {
  if (!mileageForm.value.start || !mileageForm.value.end || !mileageForm.value.distance) return
  saving.value = true
  try {
    await call('crm.api.expense.create_mileage_trip', {
      start_location: mileageForm.value.start,
      end_location: mileageForm.value.end,
      distance_km: mileageForm.value.distance,
      trip_date: mileageForm.value.date,
    })
    toast.success(__('Perjalanan berhasil dicatat'))
    showAddForm.value = false
    resetMileageForm()
    loadMileage()
  } catch (err) {
    toast.error(err.messages?.[0] || __('Gagal mencatat perjalanan'))
  } finally {
    saving.value = false
  }
}
</script>
