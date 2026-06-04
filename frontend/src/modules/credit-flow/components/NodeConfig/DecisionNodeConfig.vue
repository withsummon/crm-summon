<template>
  <div class="space-y-4">
    <div>
      <label class="config-label">{{ __('Data Source') }}</label>
      <select
        :value="config.dataSource || 'application'"
        class="config-select"
        @change="update('dataSource', $event.target.value)"
      >
        <option
          v-for="src in CONDITION_DATA_SOURCES"
          :key="src.id"
          :value="src.id"
        >
          {{ __(src.label) }}
        </option>
      </select>
    </div>

    <!-- Conditions -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label class="config-label mb-0">{{ __('Conditions') }}</label>
        <button
          class="text-xs brand-link font-medium"
          @click="addCondition"
        >
          + {{ __('Add Condition') }}
        </button>
      </div>

      <div class="space-y-2">
        <div
          v-for="(cond, idx) in conditions"
          :key="idx"
          class="rounded-lg border border-gray-200 bg-gray-50/80 p-3"
        >
          <div class="flex items-center gap-2 mb-2" v-if="idx > 0">
            <select
              :value="cond.logic || 'AND'"
              class="rounded border border-gray-200 bg-white px-2 py-0.5 text-xs font-medium text-gray-600"
              @change="updateCondition(idx, 'logic', $event.target.value)"
            >
              <option value="AND">AND</option>
              <option value="OR">OR</option>
            </select>
          </div>

          <div class="grid grid-cols-3 gap-2">
            <!-- Field -->
            <select
              :value="cond.field || ''"
              class="config-select-sm"
              @change="updateCondition(idx, 'field', $event.target.value)"
            >
              <option value="" disabled>{{ __('Field') }}</option>
              <option
                v-for="field in currentFields"
                :key="field.name"
                :value="field.name"
              >
                {{ __(field.label) }}
              </option>
            </select>

            <!-- Operator -->
            <select
              :value="cond.operator || '=='"
              class="config-select-sm"
              @change="updateCondition(idx, 'operator', $event.target.value)"
            >
              <option
                v-for="op in getOperators(cond.field)"
                :key="op.value"
                :value="op.value"
              >
                {{ op.label }}
              </option>
            </select>

            <!-- Value -->
            <div class="flex gap-1">
              <input
                :value="cond.value || ''"
                type="text"
                class="config-input-sm flex-1"
                :placeholder="__('Value')"
                @input="updateCondition(idx, 'value', $event.target.value)"
              />
              <button
                class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500"
                @click="removeCondition(idx)"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Expression Preview -->
    <div class="rounded-lg bg-slate-50 border border-slate-200 p-3">
      <div class="text-[11px] font-medium text-slate-500 uppercase tracking-wider mb-1">
        {{ __('Expression Preview') }}
      </div>
      <code class="text-xs text-slate-700 break-all">
        {{ expressionPreview }}
      </code>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  CONDITION_DATA_SOURCES,
  CONDITION_OPERATORS,
} from '../../data/creditFlowNodeTypes'

const props = defineProps({
  config: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:config'])

const conditions = computed(() => props.config.conditions || [])

const currentDataSource = computed(() =>
  CONDITION_DATA_SOURCES.find((s) => s.id === (props.config.dataSource || 'application'))
)

const currentFields = computed(() => currentDataSource.value?.fields || [])

function getOperators(fieldName) {
  const field = currentFields.value.find((f) => f.name === fieldName)
  return CONDITION_OPERATORS[field?.type || 'data'] || CONDITION_OPERATORS.data
}

const expressionPreview = computed(() => {
  if (!conditions.value.length) return 'IF (no conditions) THEN → true'
  return conditions.value
    .map((c, i) => {
      const prefix = i > 0 ? ` ${c.logic || 'AND'} ` : 'IF '
      return `${prefix}${c.field || '?'} ${c.operator || '=='} ${c.value || '?'}`
    })
    .join('')
    + ' THEN → true ELSE → false'
})

function update(key, value) {
  emit('update:config', { ...props.config, [key]: value })
}

function addCondition() {
  const newConditions = [...conditions.value, { field: '', operator: '==', value: '', logic: 'AND' }]
  emit('update:config', { ...props.config, conditions: newConditions })
}

function updateCondition(idx, key, value) {
  const newConditions = [...conditions.value]
  newConditions[idx] = { ...newConditions[idx], [key]: value }
  emit('update:config', { ...props.config, conditions: newConditions })
}

function removeCondition(idx) {
  const newConditions = conditions.value.filter((_, i) => i !== idx)
  emit('update:config', { ...props.config, conditions: newConditions })
}
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-select-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
.config-input-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
</style>
