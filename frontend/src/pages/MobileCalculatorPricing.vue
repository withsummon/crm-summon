<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <h1 class="text-lg font-semibold text-crm-text">
        {{ __('Kalkulator Pricing') }}
      </h1>
      <p class="text-xs text-crm-text-secondary mt-0.5">
        {{ __('Hitung angsuran kredit dengan cepat') }}
      </p>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border space-y-4">
        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Jenis Kredit') }}
          </label>
          <select
            v-model="form.loanType"
            class="w-full rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
            @change="calculate"
          >
            <option value="fixed">{{ __('Kredit Tetap (Fixed Rate)') }}</option>
            <option value="effective">{{ __('Efektif (Sliding Rate)') }}</option>
            <option value="annuity">{{ __('Anuitas') }}</option>
          </select>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Jumlah Pinjaman') }}
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-crm-muted font-medium">Rp</span>
            <input
              v-model="form.amount"
              type="text"
              inputmode="numeric"
              :placeholder="__('0')"
              class="w-full rounded-xl border border-crm-border pl-10 pr-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
              @input="formatInput('amount'); calculate()"
            />
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Bunga per Tahun') }}
          </label>
          <div class="relative">
            <input
              v-model="form.rate"
              type="number"
              step="0.01"
              min="0"
              max="100"
              :placeholder="__('e.g. 9.5')"
              class="w-full rounded-xl border border-crm-border px-3 py-2.5 pr-8 text-sm text-crm-text outline-none focus:border-crm-teal"
              @input="calculate"
            />
            <span class="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-crm-muted">%</span>
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-crm-text-secondary mb-1.5 block">
            {{ __('Jangka Waktu') }}
          </label>
          <div class="flex gap-3">
            <input
              v-model="form.tenor"
              type="number"
              min="1"
              :placeholder="__('e.g. 12')"
              class="flex-1 rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
              @input="calculate"
            />
            <select
              v-model="form.tenorUnit"
              class="w-28 rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal"
              @change="calculate"
            >
              <option value="months">{{ __('Bulan') }}</option>
              <option value="years">{{ __('Tahun') }}</option>
            </select>
          </div>
        </div>
      </div>

      <div
        v-if="result.monthlyPayment > 0"
        class="rounded-xl bg-white p-4 shadow-sm border border-crm-teal space-y-3"
      >
        <h2 class="text-sm font-semibold text-crm-text border-b border-crm-border pb-2">
          {{ __('Hasil Perhitungan') }}
        </h2>
        <div class="grid grid-cols-2 gap-3">
          <div class="rounded-lg bg-crm-surface p-3">
            <p class="text-[10px] text-crm-text-secondary uppercase tracking-wider">
              {{ form.loanType === 'fixed' ? __('Angsuran/Bulan') : __('Angsuran/Bulan') }}
            </p>
            <p class="text-lg font-bold text-crm-teal mt-1">
              Rp {{ formatNumber(result.monthlyPayment) }}
            </p>
          </div>
          <div class="rounded-lg bg-crm-surface p-3">
            <p class="text-[10px] text-crm-text-secondary uppercase tracking-wider">
              {{ __('Total Bunga') }}
            </p>
            <p class="text-lg font-bold text-amber-600 mt-1">
              Rp {{ formatNumber(result.totalInterest) }}
            </p>
          </div>
        </div>
        <div class="space-y-1.5 text-sm">
          <div class="flex justify-between">
            <span class="text-crm-text-secondary">{{ __('Pokok Pinjaman') }}</span>
            <span class="text-crm-text font-medium">Rp {{ formatNumber(result.principal) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-crm-text-secondary">{{ __('Total Pembayaran') }}</span>
            <span class="text-crm-text font-medium">Rp {{ formatNumber(result.totalPayment) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-crm-text-secondary">{{ __('Tenor') }}</span>
            <span class="text-crm-text font-medium">{{ result.tenorMonths }} {{ __('bulan') }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-crm-text-secondary">{{ __('Bunga Efektif') }}</span>
            <span class="text-crm-text font-medium">{{ form.rate }}% {{ __('per tahun') }}</span>
          </div>
        </div>
      </div>

      <div
        v-if="result.monthlyPayment > 0"
        class="rounded-xl bg-white p-4 shadow-sm border border-crm-border"
      >
        <h2 class="text-sm font-semibold text-crm-text mb-3">
          {{ __('Tabel Angsuran') }}
        </h2>
        <div class="max-h-48 overflow-y-auto space-y-1">
          <div
            v-for="(row, i) in amortizationSchedule"
            :key="i"
            class="grid grid-cols-4 gap-2 rounded-lg bg-crm-surface p-2 text-xs"
          >
            <span class="text-crm-muted">{{ __('Bln') }} {{ row.month }}</span>
            <span class="text-crm-text text-right">Rp {{ formatNumber(row.principal) }}</span>
            <span class="text-crm-text text-right">Rp {{ formatNumber(row.interest) }}</span>
            <span class="text-crm-text text-right font-medium">Rp {{ formatNumber(row.balance) }}</span>
          </div>
        </div>
      </div>

      <div class="rounded-xl bg-white p-4 shadow-sm border border-crm-border">
        <h2 class="text-sm font-semibold text-crm-text mb-3">{{ __('Simulasi Cepat') }}</h2>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="preset in presets"
            :key="preset.label"
            class="rounded-xl border border-crm-border p-3 text-center hover:border-crm-teal/50 transition-colors"
            @click="applyPreset(preset)"
          >
            <p class="text-xs font-semibold text-crm-text">Rp {{ preset.label }}</p>
            <p class="text-[10px] text-crm-text-secondary">{{ preset.tenor }} bln</p>
            <p class="text-[10px] text-crm-teal font-medium">
              Rp {{ formatNumber(preset.result) }}/bln
            </p>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { FeatherIcon, toast } from 'frappe-ui'

const form = reactive({
  loanType: 'fixed',
  amount: '100.000.000',
  rate: 9.5,
  tenor: 12,
  tenorUnit: 'months',
})

const result = reactive({
  monthlyPayment: 0,
  totalInterest: 0,
  totalPayment: 0,
  principal: 0,
  tenorMonths: 0,
})

const amortizationSchedule = ref([])

function formatInput(field) {
  const value = form[field].replace(/[^0-9]/g, '')
  if (value) form[field] = parseInt(value, 10).toLocaleString('id-ID')
  else form[field] = ''
}

function formatNumber(num) {
  return Math.round(num).toLocaleString('id-ID')
}

function parseNumber(str) {
  return parseInt(String(str).replace(/[^0-9]/g, ''), 10) || 0
}

function calculate() {
  const principal = parseNumber(form.amount)
  const annualRate = parseFloat(form.rate) || 0
  const tenor = parseInt(form.tenor, 10) || 0
  const tenorMonths = form.tenorUnit === 'years' ? tenor * 12 : tenor

  if (!principal || !annualRate || !tenorMonths) {
    result.monthlyPayment = 0
    result.totalInterest = 0
    result.totalPayment = 0
    result.principal = 0
    result.tenorMonths = 0
    amortizationSchedule.value = []
    return
  }

  const monthlyRate = annualRate / 100 / 12
  let monthlyPayment, totalPayment, totalInterest
  const schedule = []

  if (form.loanType === 'fixed') {
    monthlyPayment = (principal * monthlyRate * Math.pow(1 + monthlyRate, tenorMonths)) /
      (Math.pow(1 + monthlyRate, tenorMonths) - 1)
    totalPayment = monthlyPayment * tenorMonths
    totalInterest = totalPayment - principal

    let balance = principal
    for (let i = 1; i <= tenorMonths; i++) {
      const interest = balance * monthlyRate
      const principalPaid = monthlyPayment - interest
      balance -= principalPaid
      schedule.push({
        month: i,
        principal: Math.round(principalPaid),
        interest: Math.round(interest),
        balance: Math.round(Math.max(balance, 0)),
      })
    }
  } else if (form.loanType === 'effective') {
    totalInterest = 0
    const monthlyPrincipal = principal / tenorMonths
    let balance = principal
    for (let i = 1; i <= tenorMonths; i++) {
      const interest = balance * monthlyRate
      const payment = monthlyPrincipal + interest
      balance -= monthlyPrincipal
      totalInterest += interest
      schedule.push({
        month: i,
        principal: Math.round(monthlyPrincipal),
        interest: Math.round(interest),
        balance: Math.round(Math.max(balance, 0)),
      })
    }
    monthlyPayment = schedule[0].principal + schedule[0].interest
    totalPayment = principal + totalInterest
  } else {
    const pmt = (principal * monthlyRate * Math.pow(1 + monthlyRate, tenorMonths)) /
      (Math.pow(1 + monthlyRate, tenorMonths) - 1)
    totalInterest = 0
    let balance = principal
    for (let i = 1; i <= tenorMonths; i++) {
      const interest = balance * monthlyRate
      const principalPaid = pmt - interest
      balance -= principalPaid
      totalInterest += interest
      schedule.push({
        month: i,
        principal: Math.round(principalPaid),
        interest: Math.round(interest),
        balance: Math.round(Math.max(balance, 0)),
      })
    }
    monthlyPayment = pmt
    totalPayment = principal + totalInterest
  }

  result.monthlyPayment = Math.round(monthlyPayment)
  result.totalInterest = Math.round(totalInterest)
  result.totalPayment = Math.round(totalPayment)
  result.principal = principal
  result.tenorMonths = tenorMonths
  amortizationSchedule.value = schedule
}

const presets = [
  { label: '50 Juta', amount: 50000000, tenor: 12, result: 0 },
  { label: '100 Juta', amount: 100000000, tenor: 24, result: 0 },
  { label: '250 Juta', amount: 250000000, tenor: 36, result: 0 },
  { label: '500 Juta', amount: 500000000, tenor: 60, result: 0 },
  { label: '1 Miliar', amount: 1000000000, tenor: 120, result: 0 },
  { label: '5 Miliar', amount: 5000000000, tenor: 180, result: 0 },
]

presets.forEach((p) => {
  const monthlyRate = 9.5 / 100 / 12
  p.result = Math.round((p.amount * monthlyRate * Math.pow(1 + monthlyRate, p.tenor)) /
    (Math.pow(1 + monthlyRate, p.tenor) - 1))
})

function applyPreset(preset) {
  form.amount = preset.amount.toLocaleString('id-ID')
  form.tenor = preset.tenor
  form.tenorUnit = 'months'
  calculate()
  toast.info(__('Simulasi untuk Rp {0}', [preset.label]))
}

calculate()
</script>
