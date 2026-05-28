<template>
  <div class="flex h-full flex-col bg-white overflow-hidden">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <button class="shrink-0 text-crm-muted hover:text-crm-text" @click="goBack">
            <LucideArrowLeft class="h-5 w-5" />
          </button>
          <div class="min-w-0">
            <h1 class="truncate text-base font-bold text-crm-text">
              {{ title }}
            </h1>
            <p v-if="subtitle" class="truncate text-[10px] text-crm-muted mt-0.5">{{ subtitle }}</p>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <!-- Flow status badge -->
          <span
            v-if="flow?.data?.status"
            class="text-[10px] font-bold px-2 py-0.5 rounded-full mr-2"
            :class="statusClass(flow.data.status)"
          >
            {{ flow.data.status }}
          </span>

          <!-- Templates button -->
          <Button
            v-if="isNew"
            :label="__('Choose Template')"
            variant="outline"
            @click="showTemplateModal = true"
          >
            <template #prefix>
              <LucideLayers class="h-4 w-4" />
            </template>
          </Button>

          <!-- Run History button -->
          <Button
            v-if="!isNew"
            :label="__('Run History')"
            variant="outline"
            @click="openRunHistory"
          >
            <template #prefix>
              <LucideActivity class="h-4 w-4" />
            </template>
          </Button>

          <!-- Version History button -->
          <Button
            v-if="!isNew"
            :label="__('Versions')"
            variant="outline"
            @click="toggleVersionPanel"
          >
            <template #prefix>
              <LucideHistory class="h-4 w-4" />
            </template>
          </Button>

          <!-- Validate button -->
          <Button
            :label="__('Validate')"
            variant="outline"
            @click="runLocalValidation"
          >
            <template #prefix>
              <LucideCheckSquare class="h-4 w-4" />
            </template>
          </Button>

          <!-- Save Draft button -->
          <Button
            :label="__('Save Draft')"
            variant="outline"
            :loading="isSaving"
            @click="saveDraft"
          >
            <template #prefix>
              <LucideSave class="h-4 w-4" />
            </template>
          </Button>

          <!-- Publish button -->
          <Button
            :label="__('Publish')"
            variant="solid"
            :loading="isPublishing"
            @click="showPublishDialog"
          >
            <template #prefix>
              <LucideRocket class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <!-- Mobile Tabs -->
    <div v-if="isMobile" class="flex border-b border-slate-200 shrink-0 bg-white justify-around text-xs py-2.5 z-20">
      <button 
        v-for="t in [
          { key: 'canvas', label: 'Canvas' },
          { key: 'palette', label: 'Palette' },
          { key: 'settings', label: selectedNode ? 'Node Settings' : 'Flow Settings' }
        ]"
        :key="t.key"
        :class="activeSidebar === t.key ? 'text-purple-600 font-bold border-b-2 border-purple-600 pb-1' : 'text-slate-500 pb-1'"
        @click="activeSidebar = t.key"
      >
        {{ t.label }}
      </button>
    </div>

    <!-- Main Workspace -->
    <div class="flex min-h-0 flex-1 bg-white relative">
      <!-- Left Sidebar Palette -->
      <WorkflowNodePalette v-if="!isMobile || activeSidebar === 'palette'" />

      <!-- Center Canvas -->
      <div v-if="!isMobile || activeSidebar === 'canvas'" class="flex-1 relative">
        <WorkflowCanvas
          :flowXml="flowXml"
          :elementConfigs="elementConfigs"
          @changed="handleFlowChange"
          @node-selected="handleNodeSelected"
          @pane-clicked="handlePaneClicked"
          @config-created="handleConfigCreated"
          @config-deleted="handleConfigDeleted"
        />

        <!-- Validation Results Panel Overlay -->
        <div
          v-if="validationResults && (validationResults.errors?.length || validationResults.warnings?.length)"
          class="absolute top-4 right-4 bg-white/95 backdrop-blur-sm border border-crm-border rounded-xl shadow-lg p-4 max-w-sm max-h-[300px] overflow-y-auto z-20"
        >
          <div class="flex items-center justify-between border-b border-gray-100 pb-2 mb-2">
            <span class="text-xs font-bold text-gray-800">{{ __('Validation Results') }}</span>
            <button class="text-crm-muted hover:text-crm-text text-xs" @click="validationResults = null">✕</button>
          </div>
          
          <div class="space-y-2">
            <!-- Errors -->
            <div
              v-for="(err, idx) in validationResults.errors"
              :key="'err-' + idx"
              class="flex items-start gap-2 text-[11px] text-red-600 bg-red-50 p-2 rounded-lg"
            >
              <span class="font-bold">Error:</span>
              <span>{{ __(err.message) }}</span>
            </div>

            <!-- Warnings -->
            <div
              v-for="(warn, idx) in validationResults.warnings"
              :key="'warn-' + idx"
              class="flex items-start gap-2 text-[11px] text-amber-600 bg-amber-50/60 p-2 rounded-lg"
            >
              <span class="font-bold">Warning:</span>
              <span>{{ __(warn.message) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Properties Panel -->
      <!-- Case 1: A node is selected -->
      <NodePropertyPanel
        v-if="selectedNode && (!isMobile || activeSidebar === 'settings')"
        :node="selectedNode"
        @update-node="handleUpdateNode"
        @delete-node="handleDeleteNode"
        @close="selectedNode = null"
      />

      <!-- Case 2: No node selected -> Show general flow settings -->
      <div v-else-if="!isMobile || activeSidebar === 'settings'" class="flex h-full w-full md:w-80 flex-col border-l border-crm-border bg-white shadow-sm p-4 space-y-4 overflow-y-auto">
        <div class="flex items-center gap-2 pb-3 border-b border-crm-border">
          <LucideSettings class="w-4.5 h-4.5 text-purple-600" />
          <h2 class="text-sm font-semibold text-gray-800">{{ __('Flow settings') }}</h2>
        </div>

        <!-- Flow Title -->
        <div>
          <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
            {{ __('Flow Title') }}
          </label>
          <input
            v-model="flowTitle"
            type="text"
            class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text font-semibold"
            @input="flowChanged = true"
          />
        </div>

        <!-- Flow Description -->
        <div>
          <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
            {{ __('Description') }}
          </label>
          <textarea
            v-model="flowDescription"
            rows="3"
            class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text leading-normal resize-none"
            @input="flowChanged = true"
          ></textarea>
        </div>

        <!-- Product Type Link -->
        <div>
          <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
            {{ __('Product Type') }}
          </label>
          <select
            v-model="flowProductType"
            class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
            @change="flowChanged = true"
          >
            <option value="">{{ __('Select Product...') }}</option>
            <option
              v-for="prod in computedProductList"
              :key="prod.name"
              :value="prod.name"
            >
              {{ prod.product_name || prod.name }}
            </option>
          </select>
        </div>

        <!-- Applicant Persona -->
        <div>
          <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
            {{ __('Applicant Persona') }}
          </label>
          <select
            v-model="flowApplicantPersona"
            class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
            @change="flowChanged = true"
          >
            <option value="Any">{{ __('Any Persona') }}</option>
            <option value="New Customer">{{ __('New Customer') }}</option>
            <option value="Existing Customer">{{ __('Existing Customer') }}</option>
          </select>
        </div>

        <!-- Pre-Approved Checkbox -->
        <div class="flex items-center gap-2 pt-2">
          <input
            id="is-pre-approved"
            v-model="flowIsPreApproved"
            type="checkbox"
            class="rounded border-crm-border text-purple-600 focus:ring-purple-500 h-4 w-4"
            @change="flowChanged = true"
          />
          <label for="is-pre-approved" class="text-xs font-semibold text-gray-700 select-none cursor-pointer">
            {{ __('Is Pre-Approved Flow') }}
          </label>
        </div>

        <div class="pt-4 border-t border-crm-border flex flex-col gap-2">
          <h3 class="text-[10px] font-bold text-crm-muted uppercase tracking-wider">
            {{ __('Version Information') }}
          </h3>
          <div class="text-xs text-crm-text flex justify-between bg-surface-gray-1 p-2 rounded-lg">
            <span class="text-crm-muted">{{ __('Current Version:') }}</span>
            <span class="font-bold font-mono">v{{ flow?.data?.current_version || 1 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Publish Change Note Modal -->
    <div
      v-if="showPublishModal"
      class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-5 border border-crm-border">
        <h3 class="text-sm font-bold text-gray-800 mb-2">{{ __('Publish Workflow') }}</h3>
        <p class="text-xs text-crm-muted mb-4">
          {{ __('Enter a change note summarizing the enhancements in this new version. This version will become active immediately for new applications.') }}
        </p>
        
        <textarea
          v-model="changeNote"
          rows="3"
          :placeholder="__('e.g., Added parallel approval tier for large SME amounts')"
          class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text leading-normal mb-4"
        ></textarea>
        
        <div class="flex justify-end gap-2">
          <Button
            :label="__('Cancel')"
            variant="outline"
            @click="showPublishModal = false"
          />
          <Button
            :label="__('Confirm & Publish')"
            variant="solid"
            :loading="isPublishing"
            @click="confirmPublish"
          />
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
          <p class="text-xs text-crm-muted mb-4">
            {{ __('Pilih template dasar untuk alur kerja baru Anda. Semua alur kerja dapat disesuaikan kembali nantinya.') }}
          </p>
          <div class="grid gap-4 sm:grid-cols-3">
            <div
              v-for="tmpl in workflowTemplates"
              :key="tmpl.id"
              class="group relative flex flex-col justify-between rounded-xl border border-crm-border p-5 hover:border-purple-400 hover:shadow-md cursor-pointer transition-all bg-white"
              @click="applyTemplate(tmpl)"
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
                {{ __('Gunakan Template') }} &rarr;
              </div>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Version History Slide-over Panel -->
    <div
      v-if="showVersionPanel"
      class="fixed inset-0 bg-gray-900/40 backdrop-blur-sm z-50 flex justify-end"
      @click.self="showVersionPanel = false"
    >
      <div class="bg-white w-full max-w-md h-full shadow-2xl flex flex-col animate-slide-in-right">
        <!-- Panel Header -->
        <div class="flex items-center justify-between p-5 border-b border-crm-border">
          <div class="flex items-center gap-2.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-violet-600 text-white shadow-sm">
              <LucideHistory class="h-4 w-4" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-gray-800">{{ __('Version History') }}</h3>
              <p class="text-[10px] text-crm-muted mt-0.5">{{ __('View and manage workflow versions') }}</p>
            </div>
          </div>
          <button
            class="p-1.5 rounded-lg text-crm-muted hover:text-crm-text hover:bg-surface-gray-1 transition-colors"
            @click="showVersionPanel = false"
          >
            ✕
          </button>
        </div>

        <!-- Current Version Highlight -->
        <div class="px-5 py-4 bg-purple-50/50 border-b border-crm-border">
          <div class="flex items-center justify-between">
            <span class="text-xs text-crm-muted font-medium">{{ __('Current Version') }}</span>
            <span class="text-sm font-black text-purple-700 bg-purple-100 px-3 py-0.5 rounded-full">v{{ flow?.data?.current_version || 1 }}</span>
          </div>
          <div class="flex items-center justify-between mt-1.5">
            <span class="text-xs text-crm-muted font-medium">{{ __('Status') }}</span>
            <span
              class="text-[10px] font-bold px-2 py-0.5 rounded-full"
              :class="statusClass(flow?.data?.status || 'Draft')"
            >
              {{ flow?.data?.status || 'Draft' }}
            </span>
          </div>
        </div>

        <!-- Version List -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <div v-if="isLoadingVersions" class="space-y-3">
            <div v-for="i in 4" :key="i" class="h-20 animate-pulse rounded-xl bg-surface-gray-1 border border-crm-border/40" />
          </div>

          <div v-else-if="versionList.length">
            <div
              v-for="ver in versionList"
              :key="ver.name"
              class="group rounded-xl border border-crm-border bg-white p-4 transition-all hover:shadow-sm hover:border-purple-200"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-black text-gray-800 font-mono">v{{ ver.version }}</span>
                    <span
                      class="text-[9px] font-bold px-2 py-0.5 rounded-full"
                      :class="ver.status === 'Published' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
                    >
                      {{ __(ver.status) }}
                    </span>
                  </div>
                  <p v-if="ver.change_note" class="mt-1.5 text-[11px] text-crm-muted leading-relaxed line-clamp-2">
                    {{ ver.change_note }}
                  </p>
                  <div class="mt-2 flex items-center gap-3 text-[10px] text-crm-muted">
                    <span class="flex items-center gap-1">
                      <LucideUser class="h-3 w-3" />
                      {{ ver.published_by || __('System') }}
                    </span>
                    <span>{{ formatDate(ver.published_at) }}</span>
                  </div>
                </div>

                <button
                  v-if="ver.version !== (flow?.data?.current_version || 1)"
                  class="shrink-0 px-2.5 py-1.5 rounded-lg text-[10px] font-bold text-purple-600 bg-purple-50 border border-purple-200 hover:bg-purple-100 transition-all opacity-0 group-hover:opacity-100"
                  @click="handleRollback(ver.version)"
                >
                  {{ __('Rollback') }}
                </button>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-16">
            <LucideHistory class="mx-auto h-10 w-10 text-gray-200" />
            <h4 class="mt-3 text-xs font-bold text-gray-600">{{ __('No versions yet') }}</h4>
            <p class="mt-1 text-[10px] text-crm-muted max-w-xs mx-auto">{{ __('Publish this workflow to create the first version snapshot.') }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Button, Dialog, toast, usePageMeta, createListResource } from 'frappe-ui'

import LayoutHeader from '@/components/LayoutHeader.vue'
import WorkflowNodePalette from '../components/WorkflowNodePalette.vue'
import WorkflowCanvas from '../components/WorkflowCanvas.vue'
import NodePropertyPanel from '../components/NodePropertyPanel.vue'
import { useWorkflow } from '../composables/useWorkflow'
import { validateFlow } from '../components/FlowCanvas/workflowGraph'
import { INITIAL_XML } from '../components/FlowCanvas/bpmnParser'
import { workflowTemplates } from '../data/workflowTemplates'

// Lucide Icons
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideSave from '~icons/lucide/save'
import LucideRocket from '~icons/lucide/rocket'
import LucideCheckSquare from '~icons/lucide/check-square'
import LucideSettings from '~icons/lucide/settings'
import LucideFile from '~icons/lucide/file'
import LucideUserCheck from '~icons/lucide/user-check'
import LucideShieldCheck from '~icons/lucide/shield-check'
import LucideLayers from '~icons/lucide/layers'
import LucideHistory from '~icons/lucide/history'
import LucideActivity from '~icons/lucide/activity'
import LucideUser from '~icons/lucide/user'
import LucideFileText from '~icons/lucide/file-text'

const router = useRouter()
const route = useRoute()
const flowId = route.params.flowId
const isNew = !flowId || flowId === 'new'

const showTemplateModal = ref(false)
const isMobile = ref(false)
const activeSidebar = ref('canvas')
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) activeSidebar.value = 'canvas'
}

const flowXml = ref('')
const elementConfigs = ref({})
const workflowNodes = ref([])
const workflowEdges = ref([])
const flowChanged = ref(false)
const selectedNode = ref(null)
const validationResults = ref(null)

const showPublishModal = ref(false)
const changeNote = ref('')
const showVersionPanel = ref(false)
const versionList = ref([])
const isLoadingVersions = ref(false)

// Flow Settings state
const flowTitle = ref('Untitled Flow')
const flowDescription = ref('')
const flowProductType = ref('')
const flowApplicantPersona = ref('Any')
const flowIsPreApproved = ref(false)

const title = computed(() => {
  if (isNew) return flowTitle.value || __('New Workflow')
  return flow?.data?.title || __('Workflow Designer')
})

const subtitle = computed(() => {
  if (flowProductType.value) {
    return `${flowProductType.value} • ${flowApplicantPersona.value}`
  }
  return flowDescription.value || ''
})

const { flow, saveFlowDraft, publishFlow: doPublish, loadVersions, rollbackFlow, isSaving, isPublishing } = useWorkflow(isNew ? null : flowId)

// Load CRM Products list for settings
const productList = createListResource({
  doctype: 'CRM Product',
  fields: ['name', 'product_name'],
  orderBy: 'name asc',
  pageLength: 200,
  auto: true
})

const computedProductList = computed(() => {
  const dbProducts = productList.data || []
  const defaultCategories = [
    { name: 'Credit Application', product_name: 'Credit Application' },
    { name: 'Lead Qualification', product_name: 'Lead Qualification' },
    { name: 'Deal Pipeline', product_name: 'Deal Pipeline' },
    { name: 'Customer Service SLA', product_name: 'Customer Service SLA' }
  ]
  const merged = [...dbProducts]
  defaultCategories.forEach(cat => {
    if (!merged.some(p => p.name === cat.name)) {
      merged.push(cat)
    }
  })
  return merged
})

function getIcon(iconName) {
  if (iconName === 'LucideFile') return LucideFile
  if (iconName === 'LucideFileText') return LucideFileText
  if (iconName === 'LucideUserCheck') return LucideUserCheck
  if (iconName === 'LucideShieldCheck') return LucideShieldCheck
  return LucideLayers
}

function applyTemplate(tmpl) {
  flowXml.value = tmpl.xml
  elementConfigs.value = JSON.parse(JSON.stringify(tmpl.elementConfigs))
  workflowNodes.value = JSON.parse(JSON.stringify(tmpl.nodes))
  workflowEdges.value = JSON.parse(JSON.stringify(tmpl.edges))
  flowTitle.value = tmpl.title === 'Kanvas Kosong' ? __('Alur Kerja Baru') : tmpl.title
  flowDescription.value = tmpl.description
  showTemplateModal.value = false
  flowChanged.value = true
  toast.success(__('Template applied successfully'))
}

onMounted(async () => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  if (!isNew) {
    // Wait for flow resource to fetch
    watch(
      () => flow?.data,
      (data) => {
        if (data) {
          flowTitle.value = data.title || ''
          flowDescription.value = data.description || ''
          flowProductType.value = data.product_type || ''
          flowApplicantPersona.value = data.applicant_persona || 'Any'
          flowIsPreApproved.value = !!data.is_pre_approved

          if (data.flow_json) {
            try {
              const parsed = typeof data.flow_json === 'string'
                ? JSON.parse(data.flow_json)
                : data.flow_json
              workflowNodes.value = parsed.nodes || []
              workflowEdges.value = parsed.edges || []
              flowXml.value = parsed.xml || ''
              elementConfigs.value = parsed.elementConfigs || {}
            } catch {
              // ignore parse errors
            }
          }
        }
      },
      { immediate: true }
    )
  } else {
    // Scaffold default start and end nodes configs mapping for bpmn-js canvas
    flowXml.value = INITIAL_XML
    elementConfigs.value = {
      'StartEvent_1': {
        nodeType: 'StartNode',
        label: 'Mulai',
        description: 'Submission of loan request',
        config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
        actions: []
      },
      'EndEvent_1': {
        nodeType: 'EndNode',
        label: 'Selesai',
        description: 'Successful flow termination',
        config: { outcome: 'approved', finalActions: [], notifications: [] },
        actions: []
      }
    }
    workflowNodes.value = []
    workflowEdges.value = []
    
    // Automatically trigger template selection modal for new workflows
    showTemplateModal.value = true
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

function goBack() {
  router.push('/lending-risk/workflow-engine')
}

function openRunHistory() {
  if (!isNew && flowId) {
    router.push(`/lending-risk/workflow-engine/${flowId}/monitor`)
  }
}

async function toggleVersionPanel() {
  showVersionPanel.value = !showVersionPanel.value
  if (showVersionPanel.value) {
    isLoadingVersions.value = true
    try {
      const result = await loadVersions()
      versionList.value = result || []
    } catch (e) {
      versionList.value = []
    } finally {
      isLoadingVersions.value = false
    }
  }
}

async function handleRollback(version) {
  if (!confirm(__('Are you sure you want to rollback to version v{0}? This will replace the current draft with that version.', [version]))) {
    return
  }
  try {
    await rollbackFlow(flowId, version)
    showVersionPanel.value = false
    toast.success(__('Rolled back to version v{0}', [version]))
  } catch (e) {
    toast.error(e.message || __('Failed to rollback'))
  }
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    const dt = new Date(dateStr)
    return dt.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr
  }
}

function handleFlowChange(change) {
  if (change) {
    if (change.xml) flowXml.value = change.xml
    if (change.nodes) workflowNodes.value = change.nodes
    if (change.edges) workflowEdges.value = change.edges
  }
  flowChanged.value = true
}

function handleNodeSelected(node) {
  selectedNode.value = node
  if (isMobile.value) {
    activeSidebar.value = 'settings'
  }
}

function handlePaneClicked() {
  selectedNode.value = null
}

function handleConfigCreated({ id, config }) {
  elementConfigs.value[id] = config
}

function handleConfigDeleted(id) {
  delete elementConfigs.value[id]
  if (selectedNode.value?.id === id) {
    selectedNode.value = null
  }
}

function handleUpdateNode(updatedNode) {
  // Sync to elementConfigs mapping
  elementConfigs.value[updatedNode.id] = {
    nodeType: updatedNode.data.nodeType,
    label: updatedNode.data.label,
    description: updatedNode.data.description,
    config: updatedNode.data.config,
    actions: updatedNode.data.actions
  }

  // Keep workflowNodes in sync
  workflowNodes.value = workflowNodes.value.map((n) =>
    n.id === updatedNode.id ? updatedNode : n
  )
  if (selectedNode.value?.id === updatedNode.id) {
    selectedNode.value = updatedNode
  }
  flowChanged.value = true
}

function handleDeleteNode(nodeId) {
  // Delete from configs mapping
  delete elementConfigs.value[nodeId]
  
  workflowNodes.value = workflowNodes.value.filter((n) => n.id !== nodeId)
  workflowEdges.value = workflowEdges.value.filter(
    (e) => e.source !== nodeId && e.target !== nodeId
  )
  selectedNode.value = null
  flowChanged.value = true
  toast.success(__('Node deleted'))
}

async function saveDraft() {
  try {
    const res = await saveFlowDraft(isNew ? 'new' : flowId, {
      title: flowTitle.value,
      description: flowDescription.value,
      productType: flowProductType.value,
      applicantPersona: flowApplicantPersona.value,
      isPreApproved: flowIsPreApproved.value,
      flowJson: {
        xml: flowXml.value,
        elementConfigs: elementConfigs.value,
        nodes: workflowNodes.value,
        edges: workflowEdges.value
      },
    })
    flowChanged.value = false
    toast.success(__('Draft saved successfully'))
    
    // Redirect if it was a new flow creation
    if (isNew && res && res.name) {
      router.push(`/lending-risk/workflow-engine/${res.name}`)
    }
  } catch (e) {
    toast.error(e.message || __('Failed to save draft'))
  }
}

function runLocalValidation() {
  const result = validateFlow(workflowNodes.value, workflowEdges.value)
  validationResults.value = result
  
  if (result.valid) {
    toast.success(__('Logical structures validated successfully.'))
  } else {
    toast.error(__('Validation failed. Check the error list.'))
  }
}

function showPublishDialog() {
  if (isNew) {
    toast.warning(__('Please save a draft of the new flow first.'))
    return
  }
  
  // Pre-validate locally
  const result = validateFlow(workflowNodes.value, workflowEdges.value)
  if (!result.valid) {
    validationResults.value = result
    toast.error(__('Cannot publish: Flow has validation errors.'))
    return
  }
  
  changeNote.value = ''
  showPublishModal.value = true
}

async function confirmPublish() {
  try {
    await doPublish(flowId, changeNote.value)
    showPublishModal.value = false
    flowChanged.value = false
    toast.success(__('Workflow published successfully'))
  } catch (e) {
    toast.error(e.message || __('Failed to publish'))
  }
}

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

usePageMeta(() => ({ title: title.value }))
</script>
