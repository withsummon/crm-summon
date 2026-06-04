<template>
  <div class="space-y-5">
    <!-- Form Template -->
    <section>
      <h4 class="config-section-title">{{ __('Form Template') }}</h4>
      <TextInput
        v-model="localConfig.formTemplate"
        :placeholder="__('e.g. Credit Application Form')"
        @change="emitUpdate"
      />
    </section>

    <!-- Sections Manager -->
    <section>
      <div class="flex items-center justify-between mb-2">
        <h4 class="config-section-title mb-0">{{ __('Sections') }}</h4>
        <Button variant="ghost" size="sm" @click="addSection">
          <template #prefix><LucidePlus class="h-3.5 w-3.5" /></template>
          {{ __('Add Section') }}
        </Button>
      </div>

      <div v-if="localConfig.sections.length === 0" class="empty-state">
        {{ __('No sections configured. Add a section to start building the form.') }}
      </div>

      <div class="space-y-2">
        <div
          v-for="(section, sIdx) in localConfig.sections"
          :key="sIdx"
          class="border border-gray-200 rounded-lg overflow-hidden transition-all duration-200"
        >
          <!-- Section Header -->
          <div
            class="flex items-center gap-2 px-3 py-2.5 bg-gray-50 cursor-pointer select-none"
            @click="toggleSection(sIdx)"
          >
            <LucideChevronRight
              class="h-4 w-4 text-gray-400 transition-transform duration-200"
              :class="{ 'rotate-90': expandedSections[sIdx] }"
            />
            <input
              v-model="section.name"
              class="flex-1 text-sm font-medium bg-transparent border-none outline-none text-gray-800 placeholder-gray-400"
              :placeholder="__('Section Name')"
              @click.stop
              @change="emitUpdate"
            />
            <label class="flex items-center gap-1.5 text-xs text-gray-500 cursor-pointer" @click.stop>
              <input
                type="checkbox"
                v-model="section.visible"
                class="form-checkbox h-3.5 w-3.5 rounded text-blue-600"
                @change="emitUpdate"
              />
              {{ __('Visible') }}
            </label>
            <button
              class="p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
              @click.stop="removeSection(sIdx)"
            >
              <LucideTrash2 class="h-3.5 w-3.5" />
            </button>
          </div>

          <!-- Section Fields (expanded) -->
          <div v-if="expandedSections[sIdx]" class="p-3 space-y-2 border-t border-gray-100">
            <!-- Field Header -->
            <div v-if="section.fields && section.fields.length > 0" class="grid grid-cols-12 gap-2 text-[11px] uppercase tracking-wider text-gray-400 font-medium px-1">
              <span class="col-span-3">{{ __('Name') }}</span>
              <span class="col-span-3">{{ __('Label') }}</span>
              <span class="col-span-2">{{ __('Type') }}</span>
              <span class="col-span-1 text-center">{{ __('Req') }}</span>
              <span class="col-span-1 text-center">{{ __('R/O') }}</span>
              <span class="col-span-1 text-center">{{ __('Vis') }}</span>
              <span class="col-span-1"></span>
            </div>

            <!-- Field Rows -->
            <div
              v-for="(field, fIdx) in section.fields"
              :key="fIdx"
              class="grid grid-cols-12 gap-2 items-center group"
            >
              <input
                v-model="field.name"
                class="col-span-3 field-input"
                :placeholder="__('field_name')"
                @change="emitUpdate"
              />
              <input
                v-model="field.label"
                class="col-span-3 field-input"
                :placeholder="__('Label')"
                @change="emitUpdate"
              />
              <select v-model="field.type" class="col-span-2 field-input" @change="emitUpdate">
                <option v-for="t in fieldTypes" :key="t" :value="t">{{ t }}</option>
              </select>
              <div class="col-span-1 flex justify-center">
                <input type="checkbox" v-model="field.required" class="form-checkbox h-3.5 w-3.5 rounded text-blue-600" @change="emitUpdate" />
              </div>
              <div class="col-span-1 flex justify-center">
                <input type="checkbox" v-model="field.readOnly" class="form-checkbox h-3.5 w-3.5 rounded text-blue-600" @change="emitUpdate" />
              </div>
              <div class="col-span-1 flex justify-center">
                <input type="checkbox" v-model="field.visible" class="form-checkbox h-3.5 w-3.5 rounded text-blue-600" @change="emitUpdate" />
              </div>
              <div class="col-span-1 flex justify-center">
                <button
                  class="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-50 text-gray-400 hover:text-red-500 transition-all"
                  @click="removeField(sIdx, fIdx)"
                >
                  <LucideX class="h-3.5 w-3.5" />
                </button>
              </div>
            </div>

            <button
              class="flex items-center gap-1.5 text-xs text-blue-600 hover:text-blue-700 font-medium mt-1 transition-colors"
              @click="addField(sIdx)"
            >
              <LucidePlus class="h-3 w-3" />
              {{ __('Add Field') }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Validation Rules -->
    <section>
      <div class="flex items-center justify-between mb-2">
        <h4 class="config-section-title mb-0">{{ __('Validation Rules') }}</h4>
        <Button variant="ghost" size="sm" @click="addValidationRule">
          <template #prefix><LucidePlus class="h-3.5 w-3.5" /></template>
          {{ __('Add Rule') }}
        </Button>
      </div>

      <div v-if="localConfig.validationRules.length === 0" class="empty-state">
        {{ __('No validation rules.') }}
      </div>

      <div class="space-y-2">
        <div
          v-for="(rule, rIdx) in localConfig.validationRules"
          :key="rIdx"
          class="flex items-center gap-2 p-2.5 bg-gray-50 rounded-lg group"
        >
          <span class="text-xs font-medium text-gray-500 shrink-0">{{ __('IF') }}</span>
          <input v-model="rule.field" class="field-input flex-1" :placeholder="__('field')" @change="emitUpdate" />
          <select v-model="rule.operator" class="field-input w-24" @change="emitUpdate">
            <option value="==">{{ __('equals') }}</option>
            <option value="!=">{{ __('not equals') }}</option>
            <option value=">">{{ __('greater than') }}</option>
            <option value="<">{{ __('less than') }}</option>
            <option value="is_empty">{{ __('is empty') }}</option>
          </select>
          <input v-model="rule.value" class="field-input flex-1" :placeholder="__('value')" @change="emitUpdate" />
          <span class="text-xs font-medium text-gray-500 shrink-0">{{ __('THEN') }}</span>
          <select v-model="rule.action" class="field-input w-28" @change="emitUpdate">
            <option value="error">{{ __('Show Error') }}</option>
            <option value="warning">{{ __('Show Warning') }}</option>
            <option value="hide">{{ __('Hide Field') }}</option>
            <option value="disable">{{ __('Disable') }}</option>
          </select>
          <button
            class="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-50 text-gray-400 hover:text-red-500 transition-all"
            @click="removeValidationRule(rIdx)"
          >
            <LucideX class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </section>

    <!-- Default Values -->
    <section>
      <div class="flex items-center justify-between mb-2">
        <h4 class="config-section-title mb-0">{{ __('Default Values') }}</h4>
        <Button variant="ghost" size="sm" @click="addDefaultValue">
          <template #prefix><LucidePlus class="h-3.5 w-3.5" /></template>
          {{ __('Add') }}
        </Button>
      </div>

      <div v-if="defaultValuePairs.length === 0" class="empty-state">
        {{ __('No default values set.') }}
      </div>

      <div class="space-y-2">
        <div
          v-for="(pair, pIdx) in defaultValuePairs"
          :key="pIdx"
          class="flex items-center gap-2 group"
        >
          <input
            v-model="pair.key"
            class="field-input flex-1"
            :placeholder="__('field_name')"
            @change="syncDefaultValues"
          />
          <input
            v-model="pair.value"
            class="field-input flex-1"
            :placeholder="__('default value')"
            @change="syncDefaultValues"
          />
          <button
            class="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-50 text-gray-400 hover:text-red-500 transition-all"
            @click="removeDefaultValue(pIdx)"
          >
            <LucideX class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </section>

    <!-- Available Actions -->
    <section>
      <h4 class="config-section-title">{{ __('Available Actions') }}</h4>
      <div class="grid grid-cols-2 gap-2">
        <label
          v-for="action in actionOptions"
          :key="action.id"
          class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <input
            type="checkbox"
            :checked="localConfig.availableActions.includes(action.id)"
            class="form-checkbox h-4 w-4 rounded text-blue-600"
            @change="toggleAction(action.id)"
          />
          <span class="text-sm text-gray-700">{{ __(action.label) }}</span>
        </label>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Button, TextInput } from 'frappe-ui'
import LucidePlus from '~icons/lucide/plus'
import LucideTrash2 from '~icons/lucide/trash-2'
import LucideX from '~icons/lucide/x'
import LucideChevronRight from '~icons/lucide/chevron-right'

const props = defineProps({
  nodeData: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update:config'])

const fieldTypes = ['Data', 'Int', 'Float', 'Currency', 'Date', 'Select', 'Link', 'Check', 'Text', 'Attach']

const actionOptions = [
  { id: 'save_draft', label: 'Save Draft' },
  { id: 'submit', label: 'Submit' },
  { id: 'continue', label: 'Continue' },
  { id: 'validate_data', label: 'Validate Data' },
  { id: 'request_document', label: 'Request Document' },
  { id: 'cancel', label: 'Cancel' },
]

const localConfig = reactive({
  formTemplate: props.nodeData.config?.formTemplate || '',
  sections: props.nodeData.config?.sections || [],
  fields: props.nodeData.config?.fields || [],
  validationRules: props.nodeData.config?.validationRules || [],
  defaultValues: props.nodeData.config?.defaultValues || {},
  computedValues: props.nodeData.config?.computedValues || {},
  availableActions: props.nodeData.config?.availableActions || ['save_draft', 'submit'],
})

const expandedSections = reactive({})
const defaultValuePairs = ref(
  Object.entries(localConfig.defaultValues).map(([key, value]) => ({ key, value }))
)

watch(
  () => props.nodeData.config,
  (newConfig) => {
    if (!newConfig) return
    Object.assign(localConfig, {
      formTemplate: newConfig.formTemplate || '',
      sections: newConfig.sections || [],
      fields: newConfig.fields || [],
      validationRules: newConfig.validationRules || [],
      defaultValues: newConfig.defaultValues || {},
      computedValues: newConfig.computedValues || {},
      availableActions: newConfig.availableActions || ['save_draft', 'submit'],
    })
    defaultValuePairs.value = Object.entries(localConfig.defaultValues).map(([key, value]) => ({ key, value }))
  },
  { deep: true }
)

function emitUpdate() {
  emit('update:config', { ...localConfig })
}

function toggleSection(idx) {
  expandedSections[idx] = !expandedSections[idx]
}

function addSection() {
  localConfig.sections.push({
    name: '',
    visible: true,
    fields: [],
  })
  expandedSections[localConfig.sections.length - 1] = true
  emitUpdate()
}

function removeSection(idx) {
  localConfig.sections.splice(idx, 1)
  emitUpdate()
}

function addField(sectionIdx) {
  if (!localConfig.sections[sectionIdx].fields) {
    localConfig.sections[sectionIdx].fields = []
  }
  localConfig.sections[sectionIdx].fields.push({
    name: '',
    label: '',
    type: 'Data',
    required: false,
    readOnly: false,
    visible: true,
  })
  emitUpdate()
}

function removeField(sectionIdx, fieldIdx) {
  localConfig.sections[sectionIdx].fields.splice(fieldIdx, 1)
  emitUpdate()
}

function addValidationRule() {
  localConfig.validationRules.push({
    field: '',
    operator: '==',
    value: '',
    action: 'error',
  })
  emitUpdate()
}

function removeValidationRule(idx) {
  localConfig.validationRules.splice(idx, 1)
  emitUpdate()
}

function addDefaultValue() {
  defaultValuePairs.value.push({ key: '', value: '' })
}

function removeDefaultValue(idx) {
  defaultValuePairs.value.splice(idx, 1)
  syncDefaultValues()
}

function syncDefaultValues() {
  const obj = {}
  defaultValuePairs.value.forEach((p) => {
    if (p.key) obj[p.key] = p.value
  })
  localConfig.defaultValues = obj
  emitUpdate()
}

function toggleAction(actionId) {
  const idx = localConfig.availableActions.indexOf(actionId)
  if (idx >= 0) {
    localConfig.availableActions.splice(idx, 1)
  } else {
    localConfig.availableActions.push(actionId)
  }
  emitUpdate()
}
</script>

<style scoped>
.config-section-title {
  @apply text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2;
}
.field-input {
  @apply text-sm px-2 py-1.5 border border-gray-200 rounded-md bg-white text-gray-700
    placeholder-gray-400 outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100
    transition-all duration-150;
}
.empty-state {
  @apply text-sm text-gray-400 italic py-3 text-center bg-gray-50 rounded-lg;
}
</style>
