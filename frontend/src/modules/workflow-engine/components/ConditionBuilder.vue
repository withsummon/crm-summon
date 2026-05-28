<template>
  <div class="space-y-3 p-3 bg-surface-gray-1/40 rounded-xl border border-crm-border">
    <div class="flex items-center justify-between">
      <span class="text-[10px] font-bold text-crm-muted uppercase tracking-wider">{{ label || __('Routing Conditions') }}</span>
      <button
        class="text-xs text-purple-600 hover:text-purple-700 font-semibold flex items-center gap-1"
        @click="addCondition"
      >
        <LucidePlus class="w-3.5 h-3.5" />
        {{ __('Add Rule') }}
      </button>
    </div>

    <!-- Conditions List -->
    <div v-if="conditions.length > 0" class="space-y-2.5">
      <div
        v-for="(rule, idx) in conditions"
        :key="idx"
        class="flex flex-col gap-2 p-2.5 bg-white rounded-lg border border-crm-border relative shadow-sm hover:border-purple-200 transition-colors"
      >
        <!-- Top row: Group Join Operator & Delete Button -->
        <div class="flex items-center justify-between">
          <!-- AND / OR Toggle (only for index > 0) -->
          <div v-if="idx > 0" class="flex items-center rounded bg-gray-100 p-0.5 z-0">
            <button
              class="px-2 py-0.5 text-[9px] font-bold rounded uppercase transition-colors"
              :class="rule.join === 'AND' ? 'bg-purple-600 text-white shadow-sm' : 'text-crm-muted hover:text-crm-text'"
              @click="updateRuleJoin(idx, 'AND')"
            >
              {{ __('AND') }}
            </button>
            <button
              class="px-2 py-0.5 text-[9px] font-bold rounded uppercase transition-colors"
              :class="rule.join === 'OR' ? 'bg-purple-600 text-white shadow-sm' : 'text-crm-muted hover:text-crm-text'"
              @click="updateRuleJoin(idx, 'OR')"
            >
              {{ __('OR') }}
            </button>
          </div>
          <div v-else class="text-[9px] text-crm-muted italic font-medium">
            {{ __('Initial Condition Match:') }}
          </div>

          <!-- Delete Row Button -->
          <button
            class="text-crm-muted hover:text-red-600 transition-colors p-1 hover:bg-red-50 rounded"
            @click="removeCondition(idx)"
          >
            <LucideTrash class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Rule inputs row -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <!-- Field Selector -->
          <div class="flex flex-col gap-0.5">
            <select
              v-model="rule.field"
              class="w-full px-2 py-1 text-xs rounded border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="onFieldChange(idx)"
            >
              <option value="">{{ __('Select Field...') }}</option>
              <optgroup
                v-for="group in CONDITION_DATA_SOURCES"
                :key="group.id"
                :label="group.label"
              >
                <option
                  v-for="f in group.fields"
                  :key="f.name"
                  :value="f.name"
                >
                  {{ f.label }}
                </option>
              </optgroup>
            </select>
          </div>

          <!-- Operator Selector -->
          <div class="flex flex-col gap-0.5">
            <select
              v-model="rule.operator"
              class="w-full px-2 py-1 text-xs rounded border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="triggerChange"
            >
              <option value="">{{ __('Operator...') }}</option>
              <option
                v-for="op in getOperators(rule.field)"
                :key="op.value"
                :value="op.value"
              >
                {{ op.label }}
              </option>
            </select>
          </div>

          <!-- Value Input -->
          <div class="flex flex-col gap-0.5">
            <!-- Case 1: Select type -->
            <select
              v-if="getFieldType(rule.field) === 'select'"
              v-model="rule.value"
              class="w-full px-2 py-1 text-xs rounded border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="triggerChange"
            >
              <option value="">{{ __('Select Value...') }}</option>
              <option
                v-for="opt in getFieldOptions(rule.field)"
                :key="opt"
                :value="opt"
              >
                {{ opt }}
              </option>
            </select>

            <!-- Case 2: Checkbox -->
            <div
              v-else-if="getFieldType(rule.field) === 'check'"
              class="flex items-center gap-1.5 h-full pt-1"
            >
              <input
                :id="'chk-' + idx"
                v-model="rule.value"
                type="checkbox"
                class="rounded border-crm-border text-purple-600 focus:ring-purple-500"
                @change="triggerChange"
              />
              <label :for="'chk-' + idx" class="text-xs text-gray-700 select-none cursor-pointer">{{ __('True') }}</label>
            </div>

            <!-- Case 3: Text / Numeric input -->
            <input
              v-else
              v-model="rule.value"
              :type="getFieldType(rule.field) === 'int' || getFieldType(rule.field) === 'float' ? 'number' : 'text'"
              class="w-full px-2 py-1 text-xs rounded border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              :placeholder="__('Enter value...')"
              @input="triggerChange"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5 text-xs text-crm-muted italic bg-white rounded-lg border border-crm-border border-dashed p-4">
      {{ __('No conditions defined. This branch will execute by default.') }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useNodeDefinitions } from '../composables/useNodeDefinitions'

// Lucide Icons
import LucidePlus from '~icons/lucide/plus'
import LucideTrash from '~icons/lucide/trash'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  label: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'changed'])

const { CONDITION_DATA_SOURCES, CONDITION_OPERATORS } = useNodeDefinitions()

const conditions = ref([])

watch(
  () => props.modelValue,
  (newVal) => {
    if (JSON.stringify(newVal) !== JSON.stringify(conditions.value)) {
      conditions.value = newVal ? JSON.parse(JSON.stringify(newVal)) : []
    }
  },
  { immediate: true, deep: true }
)

// Helper: Get field type from field name
function getFieldType(fieldName) {
  if (!fieldName) return 'data'
  for (const group of CONDITION_DATA_SOURCES) {
    const found = group.fields.find((f) => f.name === fieldName)
    if (found) return found.type
  }
  return 'data'
}

// Helper: Get field options if field is link/select
function getFieldOptions(fieldName) {
  if (!fieldName) return []
  for (const group of CONDITION_DATA_SOURCES) {
    const found = group.fields.find((f) => f.name === fieldName)
    if (found && found.options) {
      if (Array.isArray(found.options)) return found.options
      // E.g. "CRM Product" -> link to loaded DocType, can just let select handle list or text
    }
  }
  return []
}

// Helper: Get available operators for field type
function getOperators(fieldName) {
  const type = getFieldType(fieldName)
  return CONDITION_OPERATORS[type] || CONDITION_OPERATORS.data
}

function addCondition() {
  conditions.value.push({
    join: 'AND',
    field: '',
    operator: '==',
    value: '',
  })
  triggerChange()
}

function removeCondition(index) {
  conditions.value.splice(index, 1)
  triggerChange()
}

function updateRuleJoin(index, val) {
  conditions.value[index].join = val
  triggerChange()
}

function onFieldChange(index) {
  const rule = conditions.value[index]
  const operators = getOperators(rule.field)
  rule.operator = operators[0]?.value || '=='
  rule.value = getFieldType(rule.field) === 'check' ? false : ''
  triggerChange()
}

function triggerChange() {
  emit('update:modelValue', conditions.value)
  emit('changed', conditions.value)
}
</script>
