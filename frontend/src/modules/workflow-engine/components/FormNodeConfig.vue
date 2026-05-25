<template>
  <div class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-50 flex items-center justify-end">
    <!-- Sliding Sheet Panel -->
    <div class="h-full w-[85vw] max-w-[1100px] bg-white shadow-2xl border-l border-crm-border flex flex-col transition-all duration-300">
      <!-- Header -->
      <div class="p-4 border-b border-crm-border flex items-center justify-between bg-surface-gray-1/30">
        <div class="flex items-center gap-3">
          <div class="p-1.5 rounded-lg bg-blue-100 text-blue-600 shadow-sm">
            <LucideFileText class="w-5 h-5" />
          </div>
          <div>
            <h2 class="text-sm font-bold text-gray-800">{{ __('Form Stage Layout Designer') }}</h2>
            <p class="text-[10px] text-crm-muted mt-0.5">{{ __('Configure visible sections, fields, validations, and dynamic logic.') }}</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Load Template Dropdown -->
          <select
            v-model="selectedTemplate"
            class="px-2 py-1.5 text-xs rounded-lg border border-crm-border text-crm-text bg-white"
            @change="loadTemplate"
          >
            <option value="">{{ __('Apply Template...') }}</option>
            <option
              v-for="tpl in templateList.data"
              :key="tpl.name"
              :value="tpl.name"
            >
              {{ tpl.title }}
            </option>
          </select>

          <!-- Close / Save Buttons -->
          <Button
            :label="__('Cancel')"
            variant="outline"
            @click="closePanel"
          />
          <Button
            :label="__('Apply Configuration')"
            variant="solid"
            @click="applyConfig"
          />
        </div>
      </div>

      <!-- Main Design Studio Workspace -->
      <div class="flex-1 flex min-h-0 bg-surface-gray-1/10">
        <!-- 1. LEFT PANEL: Sections & Actions -->
        <div class="w-64 border-r border-crm-border bg-white flex flex-col p-4 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-xs font-bold text-gray-800 uppercase tracking-wider">{{ __('Form Sections') }}</h3>
            <button
              class="text-xs text-purple-600 hover:text-purple-700 font-semibold flex items-center gap-0.5"
              @click="addSection"
            >
              <LucidePlus class="w-3.5 h-3.5" />
              {{ __('Add') }}
            </button>
          </div>

          <!-- Sections list -->
          <div class="flex-1 overflow-y-auto space-y-1.5 max-h-[30vh]">
            <div
              v-for="(sect, idx) in localConfig.sections"
              :key="sect.sectionId"
              class="flex items-center justify-between p-2 rounded-lg border text-xs font-medium cursor-pointer transition-all"
              :class="[
                activeSectionId === sect.sectionId
                  ? 'bg-purple-50 border-purple-300 text-purple-700 font-bold'
                  : 'bg-surface-gray-1/30 border-crm-border text-crm-text hover:bg-surface-gray-1'
              ]"
              @click="activeSectionId = sect.sectionId"
            >
              <span class="truncate">{{ sect.label }}</span>
              <button
                class="text-crm-muted hover:text-red-600 ml-2"
                @click.stop="removeSection(sect.sectionId)"
              >
                ✕
              </button>
            </div>
            <div v-if="!localConfig.sections || localConfig.sections.length === 0" class="text-center py-4 text-xs text-crm-muted italic border border-dashed border-crm-border rounded-lg">
              {{ __('No sections created.') }}
            </div>
          </div>

          <!-- Reusable Actions selector -->
          <div class="pt-4 border-t border-crm-border">
            <ActionSelector
              v-model="localConfig.availableActions"
              :label="__('Stage Actions')"
            />
          </div>
        </div>

        <!-- 2. CENTER PANEL: Fields Grid -->
        <div class="flex-1 flex flex-col p-4 min-w-0">
          <div v-if="activeSection" class="flex-1 flex flex-col bg-white rounded-xl border border-crm-border shadow-sm p-4 overflow-hidden">
            <!-- Section title header -->
            <div class="flex items-center justify-between border-b border-gray-100 pb-3 mb-4">
              <div class="min-w-0">
                <span class="text-xs text-crm-muted uppercase tracking-wider font-bold">{{ __('Active Section') }}</span>
                <h3 class="text-sm font-bold text-gray-800 truncate mt-0.5">{{ activeSection.label }}</h3>
              </div>

              <!-- Add Field Dropdown -->
              <div class="relative">
                <select
                  class="px-2.5 py-1.5 text-xs rounded-lg border border-crm-border text-purple-700 bg-purple-50 font-bold hover:bg-purple-100 cursor-pointer"
                  @change="addFieldToSection($event.target.value); $event.target.value = ''"
                >
                  <option value="">+ {{ __('Add Application Field') }}</option>
                  <option
                    v-for="field in AVAILABLE_APP_FIELDS"
                    :key="field.name"
                    :value="field.name"
                    :disabled="isFieldAlreadyInForm(field.name)"
                  >
                    {{ field.label }} ({{ field.name }})
                  </option>
                </select>
              </div>
            </div>

            <!-- Fields Table/Grid inside Section -->
            <div class="flex-1 overflow-y-auto min-h-0">
              <div v-if="activeSectionFields.length > 0" class="space-y-2">
                <div
                  v-for="field in activeSectionFields"
                  :key="field.fieldname"
                  class="flex items-center justify-between p-3 rounded-xl border border-crm-border hover:border-purple-200 hover:shadow-sm transition-all cursor-pointer"
                  :class="activeFieldName === field.fieldname ? 'ring-1 ring-purple-500 bg-purple-50/20' : ''"
                  @click="activeFieldName = field.fieldname"
                >
                  <div class="flex items-center gap-3 min-w-0 flex-1">
                    <div class="p-1 rounded bg-gray-100 text-crm-muted">
                      <LucideSettings class="w-3.5 h-3.5" />
                    </div>
                    <div class="min-w-0">
                      <span class="block text-xs font-bold text-gray-800 truncate">{{ field.label }}</span>
                      <span class="block text-[9px] text-crm-muted font-mono truncate mt-0.5">{{ field.fieldname }} • {{ getFieldType(field.fieldname) }}</span>
                    </div>
                  </div>

                  <!-- Quick config status badges -->
                  <div class="flex items-center gap-3.5">
                    <span v-if="field.mandatory" class="text-[9px] bg-red-100 text-red-700 px-1.5 py-0.5 rounded font-bold uppercase">{{ __('Req') }}</span>
                    <span v-if="field.readOnly" class="text-[9px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-bold uppercase">{{ __('Read') }}</span>
                    <span v-if="!field.visible" class="text-[9px] bg-gray-100 text-gray-700 px-1.5 py-0.5 rounded font-bold uppercase">{{ __('Hidden') }}</span>

                    <button
                      class="text-crm-muted hover:text-red-600 transition-colors p-1"
                      @click.stop="removeField(field.fieldname)"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>

              <!-- Empty fields inside section -->
              <div v-else class="text-center py-16 text-xs text-crm-muted italic border border-dashed border-crm-border rounded-xl">
                {{ __('No fields in this section. Add fields from the top-right button.') }}
              </div>
            </div>
          </div>

          <!-- Case: No Active Section -->
          <div v-else class="flex-1 flex flex-col items-center justify-center bg-white rounded-xl border border-crm-border shadow-sm p-4">
            <LucideFileText class="w-12 h-12 text-crm-muted" />
            <p class="text-xs text-crm-muted mt-2">{{ __('Select or create a section to configure its fields.') }}</p>
          </div>
        </div>

        <!-- 3. RIGHT PANEL: Selected Field/Section Properties -->
        <div class="w-80 border-l border-crm-border bg-white flex flex-col p-4 space-y-4 overflow-y-auto">
          <!-- Case A: Field properties -->
          <div v-if="activeField" class="space-y-4">
            <div class="flex items-center gap-2 pb-2 border-b border-gray-100">
              <LucideSettings class="w-4 h-4 text-purple-600" />
              <h4 class="text-xs font-bold text-gray-800">{{ __('Field Properties') }}</h4>
            </div>

            <!-- Field Label -->
            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('Field Label') }}
              </label>
              <input
                v-model="activeField.label"
                type="text"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              />
            </div>

            <!-- Field Name (Readonly) -->
            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('Field Name (System)') }}
              </label>
              <input
                type="text"
                readonly
                :value="activeField.fieldname"
                class="w-full px-3 py-2 text-xs bg-surface-gray-1 rounded-lg border border-crm-border text-crm-muted cursor-not-allowed focus:outline-none"
              />
            </div>

            <!-- Move Section placement -->
            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('Section Placement') }}
              </label>
              <select
                v-model="activeField.placement"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              >
                <option
                  v-for="sect in localConfig.sections"
                  :key="sect.sectionId"
                  :value="sect.sectionId"
                >
                  {{ sect.label }}
                </option>
              </select>
            </div>

            <!-- Checkboxes settings -->
            <div class="space-y-2.5 pt-2">
              <div class="flex items-center gap-2">
                <input
                  id="f-visible"
                  v-model="activeField.visible"
                  type="checkbox"
                  class="rounded border-crm-border text-purple-600 focus:ring-purple-500 h-4 w-4"
                />
                <label for="f-visible" class="text-xs font-semibold text-gray-700 select-none cursor-pointer">
                  {{ __('Is Visible') }}
                </label>
              </div>

              <div class="flex items-center gap-2">
                <input
                  id="f-mandatory"
                  v-model="activeField.mandatory"
                  type="checkbox"
                  class="rounded border-crm-border text-purple-600 focus:ring-purple-500 h-4 w-4"
                />
                <label for="f-mandatory" class="text-xs font-semibold text-gray-700 select-none cursor-pointer">
                  {{ __('Is Mandatory (Required)') }}
                </label>
              </div>

              <div class="flex items-center gap-2">
                <input
                  id="f-readonly"
                  v-model="activeField.readOnly"
                  type="checkbox"
                  class="rounded border-crm-border text-purple-600 focus:ring-purple-500 h-4 w-4"
                />
                <label for="f-readonly" class="text-xs font-semibold text-gray-700 select-none cursor-pointer">
                  {{ __('Is Read Only') }}
                </label>
              </div>
            </div>

            <!-- Default Values -->
            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('Default Value') }}
              </label>
              <input
                v-model="activeField.defaultValue"
                type="text"
                placeholder="e.g. Draft status, or RM name"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              />
            </div>
          </div>

          <!-- Case B: Section properties (when activeSection is set and no field is clicked) -->
          <div v-else-if="activeSection" class="space-y-4">
            <div class="flex items-center gap-2 pb-2 border-b border-gray-100">
              <LucideSettings class="w-4 h-4 text-purple-600" />
              <h4 class="text-xs font-bold text-gray-800">{{ __('Section Properties') }}</h4>
            </div>

            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('Section Title') }}
              </label>
              <input
                v-model="activeSection.label"
                type="text"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              />
            </div>

            <div class="flex items-center gap-2 pt-2">
              <input
                id="s-collapsed"
                v-model="activeSection.collapsed"
                type="checkbox"
                class="rounded border-crm-border text-purple-600 focus:ring-purple-500 h-4 w-4"
              />
              <label for="s-collapsed" class="text-xs font-semibold text-gray-700 select-none cursor-pointer">
                {{ __('Default Collapsed') }}
              </label>
            </div>
          </div>

          <!-- Case C: No field/section details -->
          <div v-else class="text-center py-20 text-xs text-crm-muted italic">
            {{ __('Select a field or section to view its configuration.') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Button, toast, createListResource } from 'frappe-ui'

import ActionSelector from './ActionSelector.vue'

// Lucide Icons
import LucideFileText from '~icons/lucide/file-text'
import LucidePlus from '~icons/lucide/plus'
import LucideSettings from '~icons/lucide/settings'

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue', 'close'])

const localConfig = ref({
  formTemplate: '',
  sections: [],
  fields: [],
  availableActions: ['save_draft', 'submit'],
})

const activeSectionId = ref('')
const activeFieldName = ref('')
const selectedTemplate = ref('')

// Load Reusable Templates from backend for BNI/CRM Form Config
const templateList = createListResource({
  doctype: 'CRM Workflow Form Config',
  fields: ['name', 'title', 'doctype_target', 'sections', 'fields'],
  filters: { is_template: 1 },
  auto: true
})

onMounted(() => {
  if (props.modelValue) {
    const raw = JSON.parse(JSON.stringify(props.modelValue))
    localConfig.value = {
      formTemplate: raw.formTemplate || '',
      sections: raw.sections || [],
      fields: raw.fields || [],
      availableActions: raw.availableActions || ['save_draft', 'submit'],
    }
    
    // Auto-select first section
    if (localConfig.value.sections?.length > 0) {
      activeSectionId.value = localConfig.value.sections[0].sectionId
    }
  }
})

const activeSection = computed(() => {
  return localConfig.value.sections?.find((s) => s.sectionId === activeSectionId.value) || null
})

const activeSectionFields = computed(() => {
  if (!activeSectionId.value) return []
  return localConfig.value.fields?.filter((f) => f.placement === activeSectionId.value) || []
})

const activeField = computed(() => {
  if (!activeFieldName.value) return null
  return localConfig.value.fields?.find((f) => f.fieldname === activeFieldName.value) || null
})

// Application Fields list
const AVAILABLE_APP_FIELDS = [
  { name: 'borrower', label: 'Borrower Link', type: 'Link' },
  { name: 'borrower_name', label: 'Borrower Name', type: 'Data' },
  { name: 'borrower_type', label: 'Borrower Type', type: 'Select' },
  { name: 'requested_amount', label: 'Requested Amount', type: 'Currency' },
  { name: 'facility_type', label: 'Facility Type', type: 'Data' },
  { name: 'risk_grade', label: 'Risk Grade', type: 'Data' },
  { name: 'purpose', label: 'Purpose', type: 'Small Text' },
  { name: 'credit_limit', label: 'Credit Limit', type: 'Currency' },
  { name: 'plafond', label: 'Plafond', type: 'Currency' },
  { name: 'tenor_months', label: 'Tenor (Months)', type: 'Int' },
  { name: 'interest_rate', label: 'Interest Rate', type: 'Float' },
  { name: 'repayment_scheme', label: 'Repayment Scheme', type: 'Data' },
  { name: 'collateral_type', label: 'Collateral Type', type: 'Data' },
  { name: 'collateral_value', label: 'Collateral Value', type: 'Currency' },
  { name: 'ltv_percent', label: 'LTV Percent', type: 'Float' },
  { name: 'coverage_ratio', label: 'Coverage Ratio', type: 'Float' },
  { name: 'collateral_description', label: 'Collateral Description', type: 'Small Text' },
  { name: 'revenue', label: 'Revenue', type: 'Currency' },
  { name: 'ebitda', label: 'EBITDA', type: 'Currency' },
  { name: 'net_profit', label: 'Net Profit', type: 'Currency' },
  { name: 'total_assets', label: 'Total Assets', type: 'Currency' },
  { name: 'total_liabilities', label: 'Total Liabilities', type: 'Currency' },
  { name: 'equity', label: 'Equity', type: 'Currency' },
  { name: 'der', label: 'DER (Debt to Equity Ratio)', type: 'Float' },
  { name: 'current_ratio', label: 'Current Ratio', type: 'Float' },
  { name: 'branch', label: 'Branch', type: 'Data' },
  { name: 'segment', label: 'Segment', type: 'Data' },
  { name: 'priority', label: 'Priority', type: 'Data' },
  { name: 'npwp', label: 'NPWP', type: 'Data' }
]

function getFieldType(name) {
  const found = AVAILABLE_APP_FIELDS.find((f) => f.name === name)
  return found ? found.type : 'Data'
}

function isFieldAlreadyInForm(name) {
  return localConfig.value.fields?.some((f) => f.fieldname === name)
}

function addSection() {
  const newId = `sec_${Date.now()}`
  localConfig.value.sections.push({
    sectionId: newId,
    label: __('New Form Section'),
    collapsed: false,
    order: localConfig.value.sections.length + 1,
    visible: true,
  })
  activeSectionId.value = newId
  activeFieldName.value = null
  toast.success(__('Section added'))
}

function removeSection(secId) {
  localConfig.value.sections = localConfig.value.sections.filter((s) => s.sectionId !== secId)
  localConfig.value.fields = localConfig.value.fields.filter((f) => f.placement !== secId)
  if (activeSectionId.value === secId) {
    activeSectionId.value = localConfig.value.sections[0]?.sectionId || ''
  }
  activeFieldName.value = null
  toast.success(__('Section removed'))
}

function addFieldToSection(fieldname) {
  if (!fieldname || !activeSectionId.value) return

  const def = AVAILABLE_APP_FIELDS.find((f) => f.name === fieldname)
  if (!def) return

  localConfig.value.fields.push({
    fieldname: def.name,
    label: def.label,
    visible: true,
    mandatory: false,
    readOnly: false,
    defaultValue: '',
    placement: activeSectionId.value,
    order: activeSectionFields.value.length + 1,
  })

  activeFieldName.value = def.name
  toast.success(__('Field added to section'))
}

function removeField(fieldname) {
  localConfig.value.fields = localConfig.value.fields.filter((f) => f.fieldname !== fieldname)
  if (activeFieldName.value === fieldname) {
    activeFieldName.value = ''
  }
  toast.success(__('Field removed'))
}

function loadTemplate() {
  if (!selectedTemplate.value) return
  const found = templateList.data.find((t) => t.name === selectedTemplate.value)
  if (found) {
    try {
      const sect = typeof found.sections === 'string' ? JSON.parse(found.sections) : found.sections
      const fld = typeof found.fields === 'string' ? JSON.parse(found.fields) : found.fields
      localConfig.value.sections = sect || []
      localConfig.value.fields = fld || []
      localConfig.value.formTemplate = found.title

      if (localConfig.value.sections.length > 0) {
        activeSectionId.value = localConfig.value.sections[0].sectionId
      }
      activeFieldName.value = null
      toast.success(__('Form Template applied successfully'))
    } catch {
      toast.error(__('Failed to parse Template configurations'))
    }
  }
}

function applyConfig() {
  emit('update:modelValue', localConfig.value)
  toast.success(__('Configuration applied to properties panel'))
  closePanel()
}

function closePanel() {
  emit('close')
}
</script>
