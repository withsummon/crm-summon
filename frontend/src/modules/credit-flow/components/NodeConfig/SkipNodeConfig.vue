<template>
  <div class="space-y-4">
    <p class="text-xs text-gray-500">
      {{ __('Configure conditions to determine when this stage should be skipped (e.g., for pre-approved applications).') }}
    </p>

    <!-- Skip Conditions -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label class="config-label mb-0">{{ __('Skip Conditions') }}</label>
        <button class="text-xs brand-link font-medium" @click="addCondition">+ {{ __('Add Condition') }}</button>
      </div>
      <div class="space-y-2">
        <div v-for="(cond, idx) in conditions" :key="idx" class="rounded-lg border border-gray-200 bg-gray-50/60 p-2.5">
          <div class="flex items-center gap-2 mb-2" v-if="idx > 0">
            <select :value="cond.logic || 'AND'" class="rounded border border-gray-200 bg-white px-2 py-0.5 text-xs font-medium text-gray-600" @change="updateCondition(idx, 'logic', $event.target.value)">
              <option value="AND">AND</option>
              <option value="OR">OR</option>
            </select>
          </div>
          <div class="grid grid-cols-3 gap-2">
            <input :value="cond.field || ''" type="text" class="config-input-sm" :placeholder="__('Field')" @input="updateCondition(idx, 'field', $event.target.value)" />
            <select :value="cond.operator || '=='" class="config-select-sm" @change="updateCondition(idx, 'operator', $event.target.value)">
              <option value="==">{{ __('equals') }}</option>
              <option value="!=">{{ __('not equals') }}</option>
              <option value=">">{{ __('greater than') }}</option>
              <option value="<">{{ __('less than') }}</option>
              <option value="in">{{ __('in') }}</option>
            </select>
            <div class="flex gap-1">
              <input :value="cond.value || ''" type="text" class="config-input-sm flex-1" :placeholder="__('Value')" @input="updateCondition(idx, 'value', $event.target.value)" />
              <button class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500" @click="removeCondition(idx)">×</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Skip Reason -->
    <div>
      <label class="config-label">{{ __('Skip Reason') }}</label>
      <input :value="config.skipReason || ''" type="text" class="config-input" :placeholder="__('e.g., Pre-approved application')" @input="update('skipReason', $event.target.value)" />
    </div>

    <!-- Preview -->
    <div class="rounded-lg bg-slate-50 border border-slate-200 p-3">
      <div class="text-[11px] font-medium text-slate-500 uppercase tracking-wider mb-1">{{ __('Logic Preview') }}</div>
      <div class="text-xs text-slate-700">
        <span class="text-primary-600 font-medium">{{ __('SKIP') }}</span>
        {{ __('when:') }}
        {{ previewText }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:config'])
const conditions = computed(() => props.config.skipConditions || [])
const previewText = computed(() => {
  if (!conditions.value.length) return '(no conditions)'
  return conditions.value.map((c, i) => {
    const prefix = i > 0 ? ` ${c.logic || 'AND'} ` : ''
    return `${prefix}${c.field || '?'} ${c.operator || '=='} ${c.value || '?'}`
  }).join('')
})
function update(key, value) { emit('update:config', { ...props.config, [key]: value }) }
function addCondition() { emit('update:config', { ...props.config, skipConditions: [...conditions.value, { field: '', operator: '==', value: '', logic: 'AND' }] }) }
function updateCondition(idx, key, value) { const arr = [...conditions.value]; arr[idx] = { ...arr[idx], [key]: value }; emit('update:config', { ...props.config, skipConditions: arr }) }
function removeCondition(idx) { emit('update:config', { ...props.config, skipConditions: conditions.value.filter((_, i) => i !== idx) }) }
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
.config-input { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
</style>
