<template>
  <div class="flex h-full min-h-0 flex-col bg-surface-gray-1">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px] shadow-sm"
            style="background: linear-gradient(135deg, #7c3aed, #c084fc)"
          >
            <LucideGitBranch class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-base font-bold text-crm-text">{{ __('Workflow Engine') }}</h1>
        </div>
      </template>
      <template #right-header>
        <Button :label="__('New Flow')" variant="solid" @click="createFlow">
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Filters & Search Toolbar -->
    <div class="bg-white border-b border-crm-border px-6 py-4 flex flex-wrap items-center justify-between gap-4">
      <div class="flex flex-wrap items-center gap-3 flex-1 min-w-0">
        <!-- Search bar -->
        <div class="relative w-64">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search flows...')"
            class="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 bg-surface-gray-1"
          />
          <LucideSearch class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-crm-muted" />
        </div>

        <!-- Status Filter -->
        <select
          v-model="statusFilter"
          class="px-3 py-1.5 text-xs rounded-lg border border-crm-border text-crm-text bg-white"
        >
          <option value="Any">{{ __('All Statuses') }}</option>
          <option value="Draft">{{ __('Draft') }}</option>
          <option value="Published">{{ __('Published') }}</option>
          <option value="Deactivated">{{ __('Deactivated') }}</option>
          <option value="Archived">{{ __('Archived') }}</option>
        </select>

        <!-- Product Filter -->
        <select
          v-model="productFilter"
          class="px-3 py-1.5 text-xs rounded-lg border border-crm-border text-crm-text bg-white max-w-[180px]"
        >
          <option value="Any">{{ __('All Products') }}</option>
          <option
            v-for="prod in productList.data"
            :key="prod.name"
            :value="prod.name"
          >
            {{ prod.product_name || prod.name }}
          </option>
        </select>

        <!-- Persona Filter -->
        <select
          v-model="personaFilter"
          class="px-3 py-1.5 text-xs rounded-lg border border-crm-border text-crm-text bg-white"
        >
          <option value="Any">{{ __('All Personas') }}</option>
          <option value="New Customer">{{ __('New Customer') }}</option>
          <option value="Existing Customer">{{ __('Existing Customer') }}</option>
        </select>
      </div>

      <div class="text-xs text-crm-muted font-medium">
        {{ __('Showing {0} flows', [filteredFlows.length]) }}
      </div>
    </div>

    <!-- Flows list -->
    <div class="flex-1 overflow-y-auto p-6">
      <div v-if="flowList.loading" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div v-for="i in 6" :key="i" class="h-40 animate-pulse rounded-xl bg-white shadow-sm border border-crm-border" />
      </div>

      <div v-else-if="filteredFlows.length" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="flow in filteredFlows"
          :key="flow.name"
          class="group rounded-xl bg-white p-5 shadow-sm border border-crm-border transition-all hover:shadow-md hover:border-purple-200 flex flex-col justify-between"
        >
          <div>
            <!-- Status Badge and Flow Title -->
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0 flex-1">
                <h3
                  class="font-bold text-sm text-gray-800 truncate group-hover:text-purple-600 transition-colors cursor-pointer"
                  @click="openFlow(flow.name)"
                >
                  {{ flow.title || flow.name }}
                </h3>
                <p v-if="flow.description" class="mt-1.5 line-clamp-2 text-xs text-crm-muted leading-normal">
                  {{ flow.description }}
                </p>
              </div>
              <span
                class="shrink-0 rounded-full px-2.5 py-0.5 text-[10px] font-bold"
                :class="statusClass(flow.status)"
              >
                {{ __(flow.status) }}
              </span>
            </div>

            <!-- Flow Details Info -->
            <div class="mt-4 flex flex-wrap gap-2">
              <span v-if="flow.product_type" class="bg-purple-50 text-purple-700 px-2 py-0.5 rounded text-[10px] font-semibold truncate max-w-[120px]">
                {{ flow.product_type }}
              </span>
              <span v-if="flow.applicant_persona" class="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-[10px] font-semibold">
                {{ __(flow.applicant_persona) }}
              </span>
              <span v-if="flow.is_pre_approved" class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded text-[10px] font-semibold">
                {{ __('Pre-Approved Only') }}
              </span>
            </div>
          </div>

          <div class="mt-5 pt-4 border-t border-gray-50 flex items-center justify-between text-[11px] text-crm-muted">
            <!-- Author / Edit Info -->
            <div class="flex flex-col gap-0.5">
              <span class="font-medium text-gray-600 font-mono">{{ flow.current_version ? `Version v${flow.current_version}` : 'Version v1' }}</span>
              <span class="mt-0.5">{{ __('Modified: {0}', [frappeDate(flow.modified)]) }}</span>
            </div>

            <!-- Card Actions -->
            <div class="flex items-center gap-1.5">
              <!-- Edit Canvas -->
              <button
                :title="__('Edit Designer')"
                class="p-1.5 rounded-lg text-crm-muted hover:text-purple-600 hover:bg-purple-50 transition-all border border-transparent hover:border-purple-200"
                @click="openFlow(flow.name)"
              >
                <LucideEdit class="h-3.5 w-3.5" />
              </button>

              <!-- Clone Flow -->
              <button
                :title="__('Clone Flow')"
                class="p-1.5 rounded-lg text-crm-muted hover:text-blue-600 hover:bg-blue-50 transition-all border border-transparent hover:border-blue-200"
                @click="handleClone(flow.name)"
              >
                <LucideCopy class="h-3.5 w-3.5" />
              </button>

              <!-- Toggle Active / Deactivate -->
              <button
                :title="flow.status === 'Deactivated' ? __('Reactivate Flow') : __('Deactivate Flow')"
                class="p-1.5 rounded-lg transition-all border border-transparent"
                :class="[
                  flow.status === 'Deactivated'
                    ? 'text-green-600 hover:bg-green-50 hover:border-green-200'
                    : 'text-red-600 hover:bg-red-50 hover:border-red-200'
                ]"
                @click="handleDeactivate(flow.name)"
              >
                <LucidePower class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-crm-border shadow-sm p-8">
        <LucideGitBranch class="h-16 w-16 text-purple-200 animate-bounce" />
        <h3 class="mt-4 text-sm font-bold text-gray-800">{{ __('No Workflows Found') }}</h3>
        <p class="mt-1 text-xs text-crm-muted text-center max-w-sm">
          {{ __('Get started by creating a new visual workflow flow, or adjust your active search filters above.') }}
        </p>
        <Button :label="__('New Flow')" variant="solid" class="mt-6" @click="createFlow">
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </div>
    </div>
  </div>

  <!-- Choose Template Dialog -->
  <Dialog
    v-model="showTemplateModal"
    :options="{
      title: __('Pilih Template Alur Kerja'),
      size: '4xl'
    }"
  >
    <template #body>
      <div class="p-6">
        <!-- Step 1: Select Template Card -->
        <div v-if="currentStep === 1">
          <p class="text-xs text-crm-muted mb-4">
            {{ __('Pilih template dasar untuk alur kerja baru Anda. Semua alur kerja dapat disesuaikan kembali nantinya.') }}
          </p>
          <div class="grid gap-4 sm:grid-cols-3">
            <div
              v-for="tmpl in templates"
              :key="tmpl.id"
              class="group relative flex flex-col justify-between rounded-xl border border-crm-border p-5 hover:border-purple-400 hover:shadow-md cursor-pointer transition-all bg-white"
              @click="selectTemplate(tmpl)"
            >
              <div>
                <!-- Icon Header -->
                <div
                  class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br text-white shadow-sm mb-3"
                  :class="tmpl.color"
                >
                  <component :is="getIcon(tmpl.icon)" class="h-5 w-5" />
                </div>
                <h4 class="text-xs font-bold text-gray-800 group-hover:text-purple-600 transition-colors">
                  {{ tmpl.title }}
                </h4>
                <p class="mt-1.5 text-[10px] text-crm-muted leading-normal">
                  {{ tmpl.description }}
                </p>
              </div>
              <div class="mt-5 pt-3 border-t border-gray-50 flex items-center justify-end text-[10px] font-bold text-purple-600 group-hover:translate-x-0.5 transition-transform">
                {{ __('Pilih Template') }} &rarr;
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Configure Details -->
        <div v-else-if="currentStep === 2 && selectedTmpl">
          <div class="flex items-center gap-3 pb-4 mb-4 border-b border-gray-100">
            <button
              class="px-2 py-1 text-[10px] font-semibold bg-gray-50 rounded hover:bg-gray-100 text-crm-muted hover:text-gray-700 transition-all"
              @click="currentStep = 1"
            >
              &larr; {{ __('Kembali ke Template') }}
            </button>
            <div>
              <h4 class="text-xs font-bold text-gray-800">
                {{ __('Konfigurasi Alur Kerja Baru') }}
              </h4>
              <p class="text-[10px] text-crm-muted mt-0.5">
                {{ __('Gunakan template: {0}', [selectedTmpl.title]) }}
              </p>
            </div>
          </div>

          <div class="space-y-4">
            <!-- Title -->
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-bold text-gray-700">{{ __('Nama Alur Kerja') }}</label>
              <input
                v-model="newFlowData.title"
                type="text"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 bg-surface-gray-1"
                placeholder="Contoh: Kualifikasi Kredit KMK"
                required
              />
            </div>

            <!-- Description -->
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-bold text-gray-700">{{ __('Deskripsi') }}</label>
              <textarea
                v-model="newFlowData.description"
                rows="2"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 bg-surface-gray-1"
                placeholder="Penjelasan singkat mengenai alur kerja ini..."
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <!-- Product Type -->
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-bold text-gray-700">{{ __('Product Type') }}</label>
                <select
                  v-model="newFlowData.productType"
                  class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border text-crm-text bg-white"
                >
                  <option value="">{{ __('Semua Produk (Any)') }}</option>
                  <option
                    v-for="prod in productList.data"
                    :key="prod.name"
                    :value="prod.name"
                  >
                    {{ prod.product_name || prod.name }}
                  </option>
                </select>
              </div>

              <!-- Applicant Persona -->
              <div class="flex flex-col gap-1.5">
                <label class="text-xs font-bold text-gray-700">{{ __('Applicant Persona') }}</label>
                <select
                  v-model="newFlowData.applicantPersona"
                  class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border text-crm-text bg-white"
                >
                  <option value="Any">{{ __('Any') }}</option>
                  <option value="New Customer">{{ __('New Customer') }}</option>
                  <option value="Existing Customer">{{ __('Existing Customer') }}</option>
                </select>
              </div>
            </div>

            <!-- Is Pre-Approved Checkbox -->
            <div class="flex items-center gap-2 mt-2">
              <input
                id="isPreApproved"
                v-model="newFlowData.isPreApproved"
                type="checkbox"
                class="h-4 w-4 text-purple-600 border-crm-border rounded focus:ring-purple-500"
              />
              <label for="isPreApproved" class="text-xs font-bold text-gray-700 cursor-pointer select-none">
                {{ __('Hanya untuk Aplikasi Pre-Approved (Is Pre-Approved)') }}
              </label>
            </div>
          </div>

          <div class="mt-6 flex justify-end gap-3 pt-4 border-t border-gray-100">
            <Button :label="__('Batal')" variant="light" @click="showTemplateModal = false" />
            <Button
              :label="__('Buat Alur Kerja')"
              variant="solid"
              :loading="isSaving"
              @click="submitCreateFromTemplate"
            />
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog, toast, usePageMeta, createListResource } from 'frappe-ui'

import LayoutHeader from '@/components/LayoutHeader.vue'
import { useWorkflow } from '../composables/useWorkflow'
import { workflowTemplates as templates } from '../data/workflowTemplates'

// Lucide Icons
import LucideGitBranch from '~icons/lucide/git-branch'
import LucidePlus from '~icons/lucide/plus'
import LucideSearch from '~icons/lucide/search'
import LucideEdit from '~icons/lucide/edit'
import LucideCopy from '~icons/lucide/copy'
import LucidePower from '~icons/lucide/power'
import LucideFile from '~icons/lucide/file'
import LucideUserCheck from '~icons/lucide/user-check'
import LucideShieldCheck from '~icons/lucide/shield-check'

const router = useRouter()
const { flowList, cloneFlow, deactivateFlow, saveFlowDraft, isSaving } = useWorkflow()

// Template Chooser State
const showTemplateModal = ref(false)
const currentStep = ref(1)
const selectedTmpl = ref(null)
const newFlowData = ref({
  title: '',
  description: '',
  productType: '',
  applicantPersona: 'Any',
  isPreApproved: false
})

function createFlow() {
  currentStep.value = 1
  selectedTmpl.value = null
  newFlowData.value = {
    title: '',
    description: '',
    productType: '',
    applicantPersona: 'Any',
    isPreApproved: false
  }
  showTemplateModal.value = true
}

function selectTemplate(tmpl) {
  selectedTmpl.value = tmpl
  newFlowData.value.title = tmpl.title === 'Kanvas Kosong' ? __('Alur Kerja Baru') : tmpl.title
  newFlowData.value.description = tmpl.description
  currentStep.value = 2
}

function getIcon(iconName) {
  if (iconName === 'LucideFile') return LucideFile
  if (iconName === 'LucideUserCheck') return LucideUserCheck
  if (iconName === 'LucideShieldCheck') return LucideShieldCheck
  return LucideGitBranch
}

async function submitCreateFromTemplate() {
  if (!newFlowData.value.title) {
    toast.error(__('Nama alur kerja wajib diisi'))
    return
  }
  try {
    const res = await saveFlowDraft('new', {
      title: newFlowData.value.title,
      description: newFlowData.value.description,
      productType: newFlowData.value.productType,
      applicantPersona: newFlowData.value.applicantPersona,
      isPreApproved: newFlowData.value.isPreApproved,
      flowJson: {
        xml: selectedTmpl.value.xml,
        elementConfigs: selectedTmpl.value.elementConfigs,
        nodes: selectedTmpl.value.nodes,
        edges: selectedTmpl.value.edges
      }
    })
    showTemplateModal.value = false
    toast.success(__('Alur kerja berhasil dibuat dari template'))
    if (res && res.name) {
      router.push(`workflow-engine/${res.name}`)
    }
  } catch (e) {
    toast.error(e.message || __('Gagal membuat alur kerja'))
  }
}

// Filters state
const searchQuery = ref('')
const statusFilter = ref('Any')
const productFilter = ref('Any')
const personaFilter = ref('Any')

const productList = createListResource({
  doctype: 'CRM Product',
  fields: ['name', 'product_name'],
  orderBy: 'product_name asc',
  pageLength: 100,
  auto: true,
})

function openFlow(flowId) {
  router.push(`workflow-engine/${flowId}`)
}

// Clone flow action
async function handleClone(flowId) {
  try {
    const res = await cloneFlow(flowId)
    toast.success(__('Flow cloned successfully'))
    if (res && res.name) {
      router.push(`workflow-engine/${res.name}`)
    }
  } catch (e) {
    toast.error(e.message || __('Failed to clone flow'))
  }
}

// Deactivate / Reactivate flow action
async function handleDeactivate(flowId) {
  try {
    const res = await deactivateFlow(flowId)
    const isDeactivated = res.status === 'Deactivated'
    toast.success(
      isDeactivated
        ? __('Flow deactivated successfully')
        : __('Flow reactivated successfully')
    )
  } catch (e) {
    toast.error(e.message || __('Action failed'))
  }
}

// Filtered and searched flows computed property
const filteredFlows = computed(() => {
  if (!flowList.data) return []

  return flowList.data.filter((flow) => {
    // Search query match
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const titleMatch = (flow.title || '').toLowerCase().includes(query)
      const descMatch = (flow.description || '').toLowerCase().includes(query)
      const idMatch = (flow.name || '').toLowerCase().includes(query)
      if (!titleMatch && !descMatch && !idMatch) return false
    }

    // Status filter match
    if (statusFilter.value !== 'Any' && flow.status !== statusFilter.value) {
      return false
    }

    // Product filter match
    if (productFilter.value !== 'Any' && flow.product_type !== productFilter.value) {
      return false
    }

    // Persona filter match
    if (personaFilter.value !== 'Any' && flow.applicant_persona !== personaFilter.value) {
      return false
    }

    return true
  })
})

function statusClass(status) {
  switch (status) {
    case 'Published':
      return 'bg-green-100 text-green-700'
    case 'Draft':
      return 'bg-amber-100 text-amber-700'
    case 'Archived':
      return 'bg-red-100 text-red-700'
    case 'Deactivated':
      return 'bg-gray-100 text-gray-700'
    default:
      return 'bg-gray-100 text-gray-600'
  }
}

function frappeDate(modifiedStr) {
  if (!modifiedStr) return '—'
  try {
    if (window.frappe?.datetime?.global_date_format) {
      return window.frappe.datetime.global_date_format(modifiedStr)
    }
  } catch {
    // ignore
  }
  return modifiedStr.split(' ')[0] || modifiedStr
}

usePageMeta(() => ({ title: __('Workflow Engine') }))
</script>
