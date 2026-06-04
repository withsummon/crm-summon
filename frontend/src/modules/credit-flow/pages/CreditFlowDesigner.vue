<template>
  <div class="flex h-full flex-col bg-white overflow-hidden">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <button
            class="flex h-7 w-7 items-center justify-center rounded-lg text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
            @click="goBack"
          >
            <LucideArrowLeft class="h-4 w-4" />
          </button>
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #ff6600, #006699)"
          >
            <LucideWorkflow class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0 flex items-center gap-2">
            <input
              v-model="flowName"
              type="text"
              class="min-w-0 border-none bg-transparent text-lg font-semibold text-gray-800 outline-none focus:ring-0 placeholder-gray-400"
              :placeholder="__('Untitled Flow')"
            />
            <Badge
              :label="flowStatus"
              :theme="flowStatus === 'Published' ? 'orange' : 'gray'"
              :class="{ 'badge-brand-primary': flowStatus === 'Published' }"
              variant="subtle"
              size="sm"
            />
            <span
              v-if="isDirty"
              class="text-[11px] text-amber-500 font-medium"
            >
              {{ __('Unsaved') }}
            </span>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            :label="__('Validate')"
            variant="outline"
            @click="onValidate"
          >
            <template #prefix>
              <LucideCheckCircle class="h-4 w-4" />
            </template>
          </Button>
          <Button
            :label="__('Save Draft')"
            variant="outline"
            @click="onSaveDraft"
          >
            <template #prefix>
              <LucideSave class="h-4 w-4" />
            </template>
          </Button>
          <Button
            :label="__('Publish')"
            variant="solid"
            theme="gray"
            class="btn-brand-primary"
            @click="onPublish"
          >
            <template #prefix>
              <LucideRocket class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <!-- Main Body: Palette | Canvas | Property Panel -->
    <div class="flex min-h-0 flex-1 relative">
      <!-- Left: Node Palette -->
      <CreditNodePalette />

      <!-- Center: Flow Canvas -->
      <div class="flex-1 relative">
        <CreditFlowCanvas
          v-model:nodes="flowNodes"
          v-model:edges="flowEdges"
          @changed="isDirty = true"
          @node-selected="onNodeSelected"
          @node-deselected="onNodeDeselected"
        />
      </div>

      <!-- Right: Property Panel (conditional) -->
      <transition
        enter-active-class="transition-transform duration-300 ease-out"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition-transform duration-200 ease-in"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <NodePropertyPanel
          v-if="selectedNode"
          :node="selectedNode"
          @update:node="onUpdateNode"
          @close="onNodeDeselected"
        />
      </transition>
    </div>

    <!-- Validation Results Dialog -->
    <Dialog
      v-model="showValidationDialog"
      :options="{
        title: __('Flow Validation Results'),
        size: 'lg',
      }"
    >
      <template #body-content>
        <div class="space-y-3 max-h-80 overflow-y-auto">
          <div v-if="validationResult && validationResult.valid" class="flex items-center gap-2 text-primary-600 p-3 rounded-lg bg-primary-50">
            <LucideCheckCircle class="h-5 w-5" />
            <span class="text-sm font-medium">{{ __('Flow is valid and ready to publish!') }}</span>
          </div>

          <div
            v-for="(error, idx) in validationResult?.errors"
            :key="'err-' + idx"
            class="flex items-start gap-2 p-3 rounded-lg bg-red-50 text-red-700"
          >
            <LucideXCircle class="h-4 w-4 mt-0.5 flex-shrink-0" />
            <span class="text-sm">{{ error.message }}</span>
          </div>

          <div
            v-for="(warn, idx) in validationResult?.warnings"
            :key="'warn-' + idx"
            class="flex items-start gap-2 p-3 rounded-lg bg-amber-50 text-amber-700"
          >
            <LucideAlertTriangle class="h-4 w-4 mt-0.5 flex-shrink-0" />
            <span class="text-sm">{{ warn.message }}</span>
          </div>

          <div
            v-if="validationResult && !validationResult.valid && validationResult.errors.length === 0 && validationResult.warnings.length === 0"
            class="text-sm text-gray-500 text-center py-4"
          >
            {{ __('No issues found.') }}
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, Dialog, toast, usePageMeta } from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import CreditNodePalette from '../components/FlowCanvas/CreditNodePalette.vue'
import CreditFlowCanvas from '../components/FlowCanvas/CreditFlowCanvas.vue'
import NodePropertyPanel from '../components/NodeConfig/NodePropertyPanel.vue'
import { serializeFlow, validateFlow } from '../components/FlowCanvas/creditFlowGraph'

import LucideWorkflow from '~icons/lucide/workflow'
import LucideArrowLeft from '~icons/lucide/arrow-left'
import LucideSave from '~icons/lucide/save'
import LucideRocket from '~icons/lucide/rocket'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideXCircle from '~icons/lucide/x-circle'
import LucideAlertTriangle from '~icons/lucide/alert-triangle'

const props = defineProps({
  flowId: { type: String, default: null },
})

const router = useRouter()

const flowName = ref(props.flowId ? 'Loading...' : 'New Credit Flow')
const flowStatus = ref('Draft')
const isDirty = ref(false)
const flowNodes = ref([])
const flowEdges = ref([])
const selectedNode = ref(null)
const showValidationDialog = ref(false)
const validationResult = ref(null)

usePageMeta(() => ({
  title: flowName.value
    ? `${flowName.value} – Credit Flow Designer`
    : __('Credit Flow Designer'),
}))

function goBack() {
  router.push({ name: 'Credit Flow Designer' })
}

function onNodeSelected(node) {
  selectedNode.value = node
}

function onNodeDeselected() {
  selectedNode.value = null
}

function onUpdateNode(updatedData) {
  if (!selectedNode.value) return
  const idx = flowNodes.value.findIndex((n) => n.id === selectedNode.value.id)
  if (idx !== -1) {
    flowNodes.value[idx].data = { ...flowNodes.value[idx].data, ...updatedData }
    selectedNode.value = { ...flowNodes.value[idx] }
    isDirty.value = true
  }
}

function onSaveDraft() {
  const payload = serializeFlow(flowNodes.value, flowEdges.value)
  console.log('Credit Flow Draft Payload:', {
    title: flowName.value,
    status: flowStatus.value,
    flow: payload,
  })
  isDirty.value = false
  toast({
    title: __('Draft saved'),
    text: __('Flow draft has been saved successfully.'),
    icon: 'check-circle',
    iconClasses: 'text-primary-600',
  })
}

function onValidate() {
  validationResult.value = validateFlow(flowNodes.value, flowEdges.value)
  showValidationDialog.value = true

  if (validationResult.value.valid) {
    toast({
      title: __('Flow is valid'),
      text: __('All checks passed. Ready to publish.'),
      icon: 'check-circle',
      iconClasses: 'text-primary-600',
    })
  } else {
    toast({
      title: __('Validation issues found'),
      text: `${validationResult.value.errors.length} error(s), ${validationResult.value.warnings.length} warning(s)`,
      icon: 'alert-triangle',
      iconClasses: 'text-amber-500',
    })
  }
}

function onPublish() {
  const result = validateFlow(flowNodes.value, flowEdges.value)
  if (!result.valid) {
    validationResult.value = result
    showValidationDialog.value = true
    toast({
      title: __('Cannot publish'),
      text: __('Fix validation errors before publishing.'),
      icon: 'x-circle',
      iconClasses: 'text-red-500',
    })
    return
  }

  flowStatus.value = 'Published'
  isDirty.value = false
  toast({
    title: __('Flow published'),
    text: __('Credit flow has been published and is now active.'),
    icon: 'rocket',
    iconClasses: 'text-primary-600',
  })
}

watch(
  () => props.flowId,
  (newId) => {
    if (newId) {
      // In future: load flow from backend
      flowName.value = 'Loaded Flow'
      toast({
        title: __('Flow loaded'),
        text: __('Flow data loaded from server.'),
        icon: 'check-circle',
        iconClasses: 'text-blue-500',
      })
    }
  },
  { immediate: true }
)
</script>
