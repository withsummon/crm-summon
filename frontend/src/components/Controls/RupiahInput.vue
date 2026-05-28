<template>
  <input
    :value="displayValue"
    inputmode="numeric"
    autocomplete="off"
    class="form-input w-full rounded border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
    :placeholder="placeholder || '0'"
    @input="updateValue"
    @blur="emitFormattedValue"
  />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: [Number, String], default: null },
  placeholder: { type: String, default: '0' },
})

const emit = defineEmits(['update:modelValue'])

const displayValue = computed(() => formatRupiahNumber(props.modelValue))

function parseRupiah(value) {
  const digits = String(value || '').replace(/[^\d-]/g, '')
  if (!digits || digits === '-') return null
  return Number(digits)
}

function formatRupiahNumber(value) {
  const amount = parseRupiah(value)
  if (amount === null || Number.isNaN(amount)) return ''
  return new Intl.NumberFormat('id-ID', { maximumFractionDigits: 0 }).format(amount)
}

function updateValue(event) {
  emit('update:modelValue', parseRupiah(event.target.value))
}

function emitFormattedValue(event) {
  event.target.value = formatRupiahNumber(event.target.value)
}
</script>
