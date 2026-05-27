<template>
  <div class="flex h-full min-h-0 flex-col bg-crm-bg">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <button class="shrink-0 text-crm-muted hover:text-crm-text" @click="goBack">
            <LucideArrowLeft class="h-5 w-5" />
          </button>
          <div class="flex h-8 w-8 items-center justify-center rounded-[10px]" style="background: linear-gradient(135deg, #0d9488, #06b6d4)">
            <LucideActivity class="h-4 w-4 text-white" />
          </div>
          <h1 class="text-base font-bold text-crm-text">{{ __('Flow Monitor') }}</h1>
          <span v-if="flowId" class="text-xs text-crm-muted font-medium border-l border-crm-border pl-3">{{ flowId }}</span>
        </div>
      </template>
    </LayoutHeader>

    <!-- Main Workspace with Split Pane Layout -->
    <div class="flex flex-1 min-h-0 overflow-hidden">
      
      <!-- LEFT SIDEBAR: Executions List & Search Filters -->
      <div 
        v-if="!isMobile || !selectedExecution"
        class="w-full md:w-[380px] shrink-0 border-r border-crm-border bg-white flex flex-col min-h-0"
      >
        
        <!-- Search & Filter section -->
        <div class="p-4 border-b border-crm-border space-y-3 bg-gray-50/50">
          <div class="relative">
            <LucideSearch class="absolute left-3 top-2.5 h-4 w-4 text-crm-muted" />
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="__('Search executions...')"
              class="w-full bg-white border border-crm-border rounded-lg pl-9 pr-4 py-2 text-xs focus:outline-none focus:border-crm-teal text-crm-text"
            />
          </div>
          
          <div class="flex items-center gap-1.5 overflow-x-auto">
            <button
              v-for="status in ['All', 'Running', 'Completed', 'Failed']"
              :key="status"
              class="px-3 py-1 rounded-full text-[10px] font-semibold border transition-all shrink-0"
              :class="filterStatus === status
                ? 'bg-crm-teal text-white border-crm-teal shadow-xs'
                : 'bg-white text-crm-muted border-crm-border hover:bg-gray-50'"
              @click="filterStatus = status"
            >
              {{ __(status) }}
            </button>
          </div>
        </div>

        <!-- Executions List -->
        <div class="flex-1 overflow-y-auto divide-y divide-crm-border min-h-0">
          <div v-if="executions.loading" class="p-4 space-y-3">
            <div v-for="i in 5" :key="i" class="h-16 animate-pulse rounded-lg bg-gray-50 border border-crm-border/40" />
          </div>

          <div v-else-if="filteredExecutions.length" class="divide-y divide-crm-border">
            <div
              v-for="exec in filteredExecutions"
              :key="exec.name"
              class="p-4 hover:bg-gray-50/70 transition-all cursor-pointer relative border-l-4"
              :class="[
                selectedExecution?.name === exec.name ? 'bg-crm-teal/5 border-crm-teal' : 'border-transparent',
              ]"
              @click="selectExecution(exec)"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-crm-text truncate">{{ exec.name }}</span>
                    <span
                      class="text-[9px] font-bold px-2 py-0.5 rounded-full shrink-0"
                      :class="executionStatusClass(exec.status)"
                    >
                      {{ __(exec.status) }}
                    </span>
                  </div>
                  
                  <div class="mt-1 text-[11px] text-crm-muted flex items-center gap-1.5 truncate">
                    <span class="font-medium text-gray-700">{{ exec.current_node_label || exec.current_node || __('Completed') }}</span>
                    <span>·</span>
                    <span>v{{ exec.flow_version }}</span>
                  </div>

                  <div class="mt-2 text-[10px] text-crm-muted flex items-center gap-1">
                    <LucideClock class="h-3.5 w-3.5 shrink-0" />
                    <span>{{ formatDateTime(exec.started_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="p-10 text-center">
            <LucideActivity class="mx-auto h-8 w-8 text-crm-muted/80" />
            <p class="mt-2 text-xs text-crm-muted font-medium">{{ __('No matching executions found.') }}</p>
          </div>
        </div>
      </div>

      <!-- RIGHT DETAIL PANEL: Visual Monitor and Timeline -->
      <div 
        v-if="!isMobile || selectedExecution"
        class="flex-1 bg-crm-bg flex flex-col min-h-0"
      >
        <div v-if="selectedExecution" class="flex-1 flex flex-col min-h-0 overflow-y-auto p-4 md:p-6 space-y-6">
          
          <!-- Detail Header Card -->
          <div class="rounded-xl border border-crm-border bg-white p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div class="space-y-1">
              <!-- Back button on mobile -->
              <button 
                v-if="isMobile" 
                @click="selectedExecution = null" 
                class="inline-flex items-center gap-1 text-xs font-extrabold text-crm-teal hover:underline mb-2"
              >
                <LucideArrowLeft class="h-4 w-4" />
                <span>{{ __('Back to Executions') }}</span>
              </button>
              <div class="flex items-center gap-2.5">
                <span class="text-sm font-semibold text-crm-muted">{{ __('Execution Detail') }}</span>
                <span class="h-1.5 w-1.5 rounded-full bg-gray-300" />
                <span class="text-xs font-mono font-bold text-gray-700 bg-gray-100 px-2 py-0.5 rounded">{{ selectedExecution.name }}</span>
              </div>
              <h2 class="text-lg font-bold text-crm-text flex items-center gap-2">
                <span>{{ __('Application:') }}</span>
                <a
                  :href="`/crm/lending-risk/credit-application/${selectedExecution.application}`"
                  class="text-crm-teal hover:underline font-extrabold flex items-center gap-1"
                >
                  {{ selectedExecution.application }}
                </a>
              </h2>
            </div>
            
            <div class="flex items-center gap-3">
              <div v-if="selectedExecution.status === 'Running' && activeNodeState?.sla_deadline" class="text-right">
                <div class="text-[10px] font-bold uppercase tracking-wider text-crm-muted">{{ __('SLA Time Remaining') }}</div>
                <div class="text-xs font-semibold text-crm-text flex items-center gap-1 justify-end mt-0.5">
                  <LucideClock class="h-3.5 w-3.5" :class="activeNodeState.sla_status === 'breached' ? 'text-red-500 animate-pulse' : 'text-crm-teal'" />
                  <span :class="activeNodeState.sla_status === 'breached' ? 'text-red-600 font-bold' : 'text-crm-text'">
                    {{ getSlaTimeRemaining(activeNodeState.sla_deadline) }}
                  </span>
                </div>
              </div>

              <span
                class="text-xs font-bold px-3.5 py-1 rounded-full shadow-2xs"
                :class="executionStatusClass(selectedExecution.status)"
              >
                {{ __(selectedExecution.status) }}
              </span>
            </div>
          </div>

          <!-- Mobile tab selector -->
          <div v-if="isMobile" class="flex border border-crm-border rounded-xl bg-white p-1 shrink-0 animate-fade">
            <button
              v-for="tab in [
                { id: 'canvas', label: __('Visual Path') },
                { id: 'timeline', label: __('Timeline') },
                { id: 'state', label: __('State Details') }
              ]"
              :key="tab.id"
              class="flex-1 py-2 text-xs font-bold rounded-lg transition-all"
              :class="activeSidebar === tab.id
                ? 'bg-crm-teal text-white shadow-xs'
                : 'text-crm-muted hover:text-crm-text'"
              @click="activeSidebar = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Grid layout: Visual BPMN Diagram (left/top) + Timeline/Config (right/bottom) -->
          <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 flex-1 min-h-0">
            
            <!-- Visual Flow Canvas Modeler/Viewer (3/5 Columns) -->
            <div 
              v-if="!isMobile || activeSidebar === 'canvas'"
              class="lg:col-span-3 flex flex-col border border-crm-border rounded-xl bg-white p-4 shadow-2xs h-[500px]"
            >
              <div class="flex items-center justify-between border-b border-gray-100 pb-3 mb-4 shrink-0">
                <div class="flex items-center gap-2">
                  <LucideGitBranch class="h-4 w-4 text-crm-teal" />
                  <h3 class="text-xs font-bold text-crm-text">{{ __('Visual Execution Path') }}</h3>
                </div>
                <!-- Legend badges -->
                <div class="flex items-center gap-3 text-[9px] font-bold">
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[#10b981]" /> {{ __('Completed') }}</span>
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-[#0d9488]" /> {{ __('Active') }}</span>
                  <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-slate-300" /> {{ __('Skipped') }}</span>
                </div>
              </div>

              <!-- BPMN container element -->
              <div class="flex-1 min-h-0 relative rounded-lg border border-crm-border bg-gray-50/50 overflow-hidden">
                <div ref="viewerContainerRef" class="w-full h-full"></div>
              </div>
            </div>

            <!-- Tabs container: Timeline + Current state details (2/5 Columns) -->
            <div 
              v-if="!isMobile || activeSidebar === 'timeline' || activeSidebar === 'state'"
              class="lg:col-span-2 flex flex-col border border-crm-border rounded-xl bg-white shadow-2xs h-[500px] overflow-hidden"
            >
              <div 
                v-if="!isMobile"
                class="flex border-b border-crm-border bg-gray-50/60 p-2 shrink-0"
              >
                <button
                  class="flex-1 py-2 text-xs font-bold rounded-lg transition-all"
                  :class="activeTab === 'timeline'
                    ? 'bg-white text-crm-text shadow-xs border border-crm-border/60'
                    : 'text-crm-muted hover:text-crm-text'"
                  @click="activeTab = 'timeline'"
                >
                  {{ __('Execution Timeline') }}
                </button>
                <button
                  class="flex-1 py-2 text-xs font-bold rounded-lg transition-all"
                  :class="activeTab === 'state'
                    ? 'bg-white text-crm-text shadow-xs border border-crm-border/60'
                    : 'text-crm-muted hover:text-crm-text'"
                  @click="activeTab = 'state'"
                >
                  {{ __('Node State Details') }}
                </button>
              </div>

              <!-- Content wrapper -->
              <div class="flex-1 overflow-y-auto p-4 min-h-0">
                
                <!-- TAB 1: IMMUTABLE AUDIT TIMELINE -->
                <div v-show="activeTab === 'timeline'" class="space-y-4 pr-1">
                  <div v-if="auditLogsList.loading" class="space-y-4 py-4">
                    <div v-for="i in 3" :key="i" class="flex gap-4 animate-pulse">
                      <div class="w-6 h-6 rounded-full bg-gray-100" />
                      <div class="flex-1 space-y-2">
                        <div class="h-3 w-1/3 bg-gray-100 rounded" />
                        <div class="h-2 w-2/3 bg-gray-50 rounded" />
                      </div>
                    </div>
                  </div>

                  <div v-else-if="auditLogsList.data?.length" class="relative pl-6 space-y-5 border-l border-gray-100 ml-3 py-2">
                    <div
                      v-for="log in auditLogsList.data"
                      :key="log.name"
                      class="relative group"
                    >
                      <!-- Timeline Node Dot -->
                      <div
                        class="absolute -left-[33px] top-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-white border-2"
                        :class="getTimelineDotClass(log.event_type, log.decision)"
                      >
                        <component :is="getTimelineIcon(log.event_type, log.decision)" class="h-3 w-3" />
                      </div>

                      <div class="space-y-1">
                        <div class="flex items-center justify-between gap-2">
                          <span class="text-xs font-bold text-crm-text group-hover:text-crm-teal transition-all">
                            {{ getEventTitle(log) }}
                          </span>
                          <span class="text-[10px] text-crm-muted whitespace-nowrap">
                            {{ formatDateTime(log.timestamp) }}
                          </span>
                        </div>

                        <p class="text-[11px] text-crm-muted leading-relaxed">
                          {{ getEventDescription(log) }}
                        </p>

                        <!-- Decision and Reason block -->
                        <div v-if="log.reason" class="mt-1.5 text-[10px] bg-gray-50 border border-gray-100 text-crm-muted rounded-lg p-2 italic">
                          "{{ log.reason }}"
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-else class="text-center py-20">
                    <LucideInfo class="mx-auto h-8 w-8 text-crm-muted" />
                    <p class="mt-2 text-xs text-crm-muted font-medium">{{ __('No audit events recorded yet.') }}</p>
                  </div>
                </div>

                <!-- TAB 2: CURRENT STATE DETAILS -->
                <div v-show="activeTab === 'state'" class="space-y-5 pr-1">
                  <div v-if="activeNodeState" class="space-y-4">
                    <div class="bg-gray-50 rounded-xl p-4 border border-crm-border/60 space-y-3">
                      <div class="flex items-center justify-between">
                        <span class="text-[10px] font-bold uppercase tracking-wider text-crm-muted">{{ __('Current Active Stage') }}</span>
                        <span class="text-xs font-bold text-crm-teal bg-crm-teal/10 px-2 py-0.5 rounded-full">
                          {{ selectedExecution.current_node_type }}
                        </span>
                      </div>
                      
                      <div class="text-sm font-black text-crm-text">
                        {{ selectedExecution.current_node_label || selectedExecution.current_node }}
                      </div>
                    </div>

                    <!-- Assignee details -->
                    <div class="border border-crm-border/60 rounded-xl p-4 space-y-3 bg-white">
                      <div class="text-[10px] font-bold uppercase tracking-wider text-crm-muted border-b border-gray-50 pb-1.5">{{ __('Assignment Details') }}</div>
                      
                      <div class="grid grid-cols-2 gap-3 text-xs">
                        <div>
                          <div class="text-crm-muted">{{ __('Assigned User') }}</div>
                          <div class="font-bold text-crm-text mt-0.5 flex items-center gap-1">
                            <LucideUser class="h-3.5 w-3.5 text-crm-muted shrink-0" />
                            <span>{{ activeNodeState.assigned_to || __('Unassigned') }}</span>
                          </div>
                        </div>

                        <div>
                          <div class="text-crm-muted">{{ __('Assigned Role') }}</div>
                          <div class="font-bold text-crm-text mt-0.5">
                            {{ activeNodeState.assigned_role || __('—') }}
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- SLA Details -->
                    <div class="border border-crm-border/60 rounded-xl p-4 space-y-3 bg-white">
                      <div class="text-[10px] font-bold uppercase tracking-wider text-crm-muted border-b border-gray-50 pb-1.5">{{ __('SLA & Schedule') }}</div>
                      
                      <div class="grid grid-cols-2 gap-3 text-xs">
                        <div>
                          <div class="text-crm-muted">{{ __('Stage Deadline') }}</div>
                          <div class="font-bold text-crm-text mt-0.5">
                            {{ formatDateTime(activeNodeState.sla_deadline) || __('No Limit') }}
                          </div>
                        </div>

                        <div>
                          <div class="text-crm-muted">{{ __('SLA Status') }}</div>
                          <div class="mt-0.5">
                            <span
                              class="text-[10px] font-bold px-2 py-0.5 rounded-full"
                              :class="getSlaStatusClass(activeNodeState.sla_status)"
                            >
                              {{ activeNodeState.sla_status === 'breached' ? __('Breached') : (activeNodeState.sla_status === 'warning' ? __('Warning') : __('On Time')) }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Captured variables JSON view -->
                    <div v-if="executionDataParsed" class="border border-crm-border/60 rounded-xl p-4 space-y-2 bg-white">
                      <div class="text-[10px] font-bold uppercase tracking-wider text-crm-muted border-b border-gray-50 pb-1.5">{{ __('Captured Flow Data') }}</div>
                      
                      <div class="text-xs divide-y divide-gray-50">
                        <div v-for="(val, key) in executionDataParsed" :key="key" class="flex justify-between py-1.5">
                          <span class="text-crm-muted font-medium capitalize">{{ key.replace('_', ' ') }}</span>
                          <span class="font-bold text-crm-text">{{ val }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div v-else class="text-center py-20">
                    <LucideCheckCircle class="mx-auto h-8 w-8 text-green-500" />
                    <p class="mt-2 text-xs text-crm-muted font-medium">{{ __('This execution has successfully completed!') }}</p>
                  </div>
                </div>

              </div>
            </div>

          </div>

        </div>

        <!-- No Execution Selected State -->
        <div v-else class="flex-1 flex flex-col items-center justify-center p-12 text-center bg-gray-50/30">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-white shadow-sm border border-crm-border/50 text-crm-muted">
            <LucideActivity class="h-8 w-8 text-crm-teal" />
          </div>
          <h3 class="mt-4 text-sm font-extrabold text-crm-text">{{ __('Select an execution') }}</h3>
          <p class="mt-1 text-xs text-crm-muted max-w-xs leading-relaxed">
            {{ __('Select a workflow credit flow execution from the list on the left to monitor its real-time path, timeline, and variables.') }}
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onBeforeUnmount, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePageMeta, createListResource } from 'frappe-ui'
import BpmnViewer from 'bpmn-js/lib/Viewer'

import LayoutHeader from '@/components/LayoutHeader.vue'
import { useWorkflowExecution } from '../composables/useWorkflowExecution'

// bpmn-js library default styles
import 'bpmn-js/dist/assets/diagram-js.css'
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css'
import 'bpmn-js/dist/assets/bpmn-js.css'
import '../components/FlowCanvas/bpmnViewerCustom.css'

// Lucide Icons
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideActivity from '~icons/lucide/activity'
import LucidePlayCircle from '~icons/lucide/play-circle'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideAlertCircle from '~icons/lucide/alert-circle'
import LucideGitBranch from '~icons/lucide/git-branch'
import LucideSearch from '~icons/lucide/search'
import LucideClock from '~icons/lucide/clock'
import LucideUser from '~icons/lucide/user'
import LucideShieldAlert from '~icons/lucide/shield-alert'
import LucideCheck from '~icons/lucide/check'
import LucideXCircle from '~icons/lucide/x-circle'
import LucideCornerDownRight from '~icons/lucide/corner-down-right'
import LucideRotateCcw from '~icons/lucide/rotate-ccw'
import LucideInfo from '~icons/lucide/info'

const router = useRouter()
const route = useRoute()
const flowId = route.params.flowId

// Left sidebar filters
const searchQuery = ref('')
const filterStatus = ref('All')
const selectedExecution = ref(null)
const activeTab = ref('timeline')
const activeSidebar = ref('canvas')

const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// Watch activeSidebar on mobile to synchronize activeTab for the nested pane content
watch(activeSidebar, (newVal) => {
  if (newVal === 'timeline' || newVal === 'state') {
    activeTab.value = newVal
  }
  
  if (newVal === 'canvas' && bpmnViewer) {
    setTimeout(() => {
      try {
        const canvas = bpmnViewer.get('canvas')
        canvas.zoom('fit-viewport')
      } catch (err) {
        console.error('Failed to fit viewport on tab change:', err)
      }
    }, 150)
  }
})

// bpmn-js viewer container
const viewerContainerRef = ref(null)
let bpmnViewer = null

const { executions } = useWorkflowExecution(flowId)

// Setup execution details & node states query
const activeNodeState = ref(null)
const nodeStatesList = ref([])

// Immutable Audit Log resource
const auditLogsList = ref({ data: [], loading: false })

// Filtered executions
const filteredExecutions = computed(() => {
  if (!executions.data) return []
  return executions.data.filter((e) => {
    // search filter
    const matchesSearch =
      !searchQuery.value ||
      e.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      e.application.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    // status filter
    const matchesStatus =
      filterStatus.value === 'All' ||
      e.status === filterStatus.value

    return matchesSearch && matchesStatus
  })
})

// Autoselect first execution once list loads
watch(
  () => executions.data,
  (newVal) => {
    if (newVal && newVal.length && !selectedExecution.value) {
      selectExecution(newVal[0])
    }
  },
  { immediate: true }
)

// Watch selection change to load audits, states, and render BPMN XML
watch(
  () => selectedExecution.value,
  async (newExec) => {
    if (!newExec) {
      activeNodeState.value = null
      return
    }

    // Load Audit Log list
    loadAuditLogs(newExec.name)

    // Load active/completed states of elements
    loadNodeStates(newExec.name)

    // Re-render visual canvas
    setTimeout(() => {
      renderVisualDiagram(newExec)
    }, 100)
  }
)

function goBack() {
  router.push('/lending-risk/workflow-engine')
}

function selectExecution(exec) {
  selectedExecution.value = exec
}

// Fetch node states using reactive list resource
function loadNodeStates(executionName) {
  const resource = createListResource({
    doctype: 'CRM Workflow Node State',
    fields: [
      'name',
      'node_id',
      'node_type',
      'status',
      'entered_at',
      'exited_at',
      'assigned_to',
      'assigned_role',
      'sla_deadline',
      'sla_status',
      'action_taken',
      'form_data'
    ],
    filters: { execution: executionName },
    auto: true
  })
  
  watch(
    () => resource.data,
    (states) => {
      if (states) {
        nodeStatesList.value = states
        activeNodeState.value = states.find(s => s.status === 'active') || null
      }
    },
    { immediate: true }
  )
}

// Fetch audit logs list manually to retain performance
function loadAuditLogs(executionName) {
  auditLogsList.value.loading = true
  const resource = createListResource({
    doctype: 'CRM Workflow Audit Log',
    fields: [
      'name',
      'node_id',
      'node_type',
      'node_label',
      'event_type',
      'timestamp',
      'user',
      'original_assignee',
      'delegated_to',
      'decision',
      'reason',
    ],
    filters: { execution: executionName },
    orderBy: 'timestamp asc',
    pageLength: 200,
    auto: true
  })

  watch(
    () => resource.data,
    (data) => {
      if (data) {
        auditLogsList.value.data = data
        auditLogsList.value.loading = false
      }
    },
    { immediate: true }
  )
}

// Visual highlighting mapping
async function renderVisualDiagram(exec) {
  if (!viewerContainerRef.value) return

  // Destroy previous viewer to avoid duplicates
  if (bpmnViewer) {
    bpmnViewer.destroy()
  }

  bpmnViewer = new BpmnViewer({
    container: viewerContainerRef.value,
  })

  // Parse frozen version JSON to extract BPMN XML
  let xml = ''
  try {
    const flowData = typeof exec.flow_version_json === 'string'
      ? JSON.parse(exec.flow_version_json)
      : exec.flow_version_json
    xml = flowData?.xml || ''
  } catch (err) {
    console.error('Failed to parse flow XML:', err)
  }

  if (!xml) return

  try {
    await bpmnViewer.importXML(xml)
    const canvas = bpmnViewer.get('canvas')
    
    // Autofit canvas
    canvas.zoom('fit-viewport')

    // Parse list arrays
    let completed = []
    let skipped = []

    try {
      completed = typeof exec.completed_nodes === 'string'
        ? JSON.parse(exec.completed_nodes || '[]')
        : exec.completed_nodes || []
    } catch {
      completed = []
    }

    try {
      skipped = typeof exec.skipped_nodes === 'string'
        ? JSON.parse(exec.skipped_nodes || '[]')
        : exec.skipped_nodes || []
    } catch {
      skipped = []
    }

    // Apply color markers to BPMN elements
    completed.forEach((nodeId) => {
      if (nodeId) canvas.addMarker(nodeId, 'bpmn-node-completed')
    })

    if (exec.current_node && exec.status === 'Running') {
      canvas.addMarker(exec.current_node, 'bpmn-node-active')
    }

    skipped.forEach((nodeId) => {
      if (nodeId) canvas.addMarker(nodeId, 'bpmn-node-skipped')
    })

  } catch (err) {
    console.error('bpmn-js importXML failed:', err)
  }
}

// Computed execution data variables
const executionDataParsed = computed(() => {
  if (!selectedExecution.value?.execution_data) return null
  try {
    return typeof selectedExecution.value.execution_data === 'string'
      ? JSON.parse(selectedExecution.value.execution_data)
      : selectedExecution.value.execution_data
  } catch {
    return null
  }
})

// SLA Deadline calculation string
function getSlaTimeRemaining(deadlineStr) {
  if (!deadlineStr) return __('No Limit')
  const diffMs = new Date(deadlineStr) - new Date()
  if (diffMs < 0) {
    return __('Breached!')
  }
  const diffHrs = Math.floor(diffMs / 3600000)
  const diffMins = Math.floor((diffMs % 3600000) / 60000)
  return `${diffHrs}h ${diffMins}m remaining`
}

// Formatting helpers
function formatDateTime(datetimeStr) {
  if (!datetimeStr) return ''
  const dt = new Date(datetimeStr)
  return dt.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function executionStatusClass(status) {
  switch (status) {
    case 'Running':
      return 'bg-blue-100 text-blue-700 border border-blue-200'
    case 'Completed':
      return 'bg-green-100 text-green-700 border border-green-200'
    case 'Failed':
      return 'bg-red-100 text-red-700 border border-red-200'
    default:
      return 'bg-gray-100 text-gray-600 border border-gray-200'
  }
}

function getSlaStatusClass(slaStatus) {
  switch (slaStatus) {
    case 'breached': return 'bg-red-100 text-red-700 font-bold'
    case 'warning': return 'bg-yellow-100 text-yellow-700 font-semibold'
    default: return 'bg-green-100 text-green-700 font-medium'
  }
}

// Audit log helper mapping methods
function getTimelineDotClass(eventType, decision) {
  switch (eventType) {
    case 'node_enter':
      return 'border-blue-400 text-blue-500'
    case 'node_exit':
      return 'border-green-400 text-green-500'
    case 'action_taken':
      if (decision === 'approved') return 'border-emerald-500 bg-emerald-50 text-emerald-600'
      if (decision === 'rejected') return 'border-rose-500 bg-rose-50 text-rose-600'
      return 'border-amber-500 bg-amber-50 text-amber-600'
    case 'delegation':
      return 'border-purple-400 bg-purple-50 text-purple-600'
    case 'notification_sent':
      return 'border-sky-400 text-sky-500'
    case 'sla_breach':
      return 'border-red-600 bg-red-100 text-red-600 font-black'
    default:
      return 'border-gray-300 text-gray-400'
  }
}

function getTimelineIcon(eventType, decision) {
  switch (eventType) {
    case 'node_enter': return LucidePlayCircle
    case 'node_exit': return LucideCheckCircle
    case 'action_taken':
      if (decision === 'approved') return LucideCheck
      if (decision === 'rejected') return LucideXCircle
      return LucideRotateCcw
    case 'delegation': return LucideCornerDownRight
    case 'notification_sent': return LucideInfo
    case 'sla_breach': return LucideShieldAlert
    default: return LucideActivity
  }
}

function getEventTitle(log) {
  switch (log.event_type) {
    case 'node_enter':
      return `Entered: ${log.node_label || log.node_id}`
    case 'node_exit':
      return `Completed: ${log.node_label || log.node_id}`
    case 'action_taken':
      const desc = log.decision === 'approved' ? 'Approved' : (log.decision === 'rejected' ? 'Rejected' : 'Returned')
      return `${desc} stage`
    case 'delegation':
      return 'Stage Reassigned'
    case 'notification_sent':
      return 'Alert Triggered'
    case 'sla_breach':
      return 'SLA Deadline Breached'
    default:
      return log.event_type
  }
}

function getEventDescription(log) {
  switch (log.event_type) {
    case 'node_enter':
      return `Workflow process reached the stage "${log.node_label || log.node_id}".`
    case 'node_exit':
      return `Transition logic evaluated; stage processing complete.`
    case 'action_taken':
      return `User ${log.user || __('Assignee')} submitted visual action decision.`
    case 'delegation':
      return `Workflow reassigned from original "${log.original_assignee || 'Unassigned'}" to replacement "${log.delegated_to || 'System Override'}".`
    case 'notification_sent':
      return `Notification auto-dispatched to ${log.reason || 'Supervisor'}.`
    case 'sla_breach':
      return `Standard time limit for this stage expired without active resolution.`
    default:
      return log.reason || ''
  }
}

// Page title meta binding
usePageMeta(() => ({ title: __('Workflow Monitor') }))

onBeforeUnmount(() => {
  if (bpmnViewer) {
    bpmnViewer.destroy()
  }
})
</script>

<style scoped>
.bg-crm-bg {
  background-color: #f8fafc;
}
</style>
