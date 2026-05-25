<template>
  <div class="flex items-center gap-2 px-4 py-2 border-b border-crm-border bg-surface-gray-1">
    <div
      v-for="chip in chips"
      :key="chip.key"
      class="cursor-pointer select-none rounded-full border px-3 py-1 text-xs font-medium transition-colors"
      :class="chipClass(chip)"
      @click="$emit('filter', chip.key)"
    >
      <span>{{ chip.label }}: {{ chip.value }}</span>
    </div>
  </div>
</template>

<script setup>
import { createResource } from 'frappe-ui'
import { computed } from 'vue'

const emit = defineEmits(['filter'])

const ribbon = createResource({
  url: 'crm.api.lead_management.get_kpi_ribbon',
  auto: true,
})

const chips = computed(() => {
  const d = ribbon.data || {}
  return [
    { key: 'new_today', label: __('New today'), value: d.new_today ?? 0, warn: false },
    { key: 'aging_stale', label: __('Aging >14d'), value: d.aging_stale ?? 0, warn: (d.aging_stale || 0) > 0 },
    { key: 'sla_breaching', label: __('SLA breaching'), value: d.sla_breaching ?? 0, warn: (d.sla_breaching || 0) > 0 },
    { key: 'dedupe_pending', label: __('Dedupe queue'), value: d.dedupe_pending ?? 0, warn: (d.dedupe_pending || 0) > 0 },
  ]
})

function chipClass(chip) {
  const base = 'border-outline-gray-2 bg-white text-ink-gray-7 hover:bg-surface-gray-2'
  if (chip.key === 'sla_breaching' && chip.warn) {
    return 'border-red-200 bg-red-50 text-red-700 hover:bg-red-100'
  }
  if (chip.key === 'aging_stale' && chip.warn) {
    return 'border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100'
  }
  if (chip.warn) {
    return 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100'
  }
  return base
}
</script>
