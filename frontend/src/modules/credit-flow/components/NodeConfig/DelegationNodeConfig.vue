<template>
  <div class="space-y-4">
    <!-- Check Statuses -->
    <div>
      <label class="config-label">{{ __('Check Approver Statuses') }}</label>
      <div class="space-y-1.5 mt-1">
        <label v-for="status in allStatuses" :key="status.id" class="flex items-center gap-2 cursor-pointer rounded-lg px-3 py-2 hover:bg-gray-50">
          <input type="checkbox" :checked="checkedStatuses.includes(status.id)" class="h-4 w-4 rounded border-gray-300 text-secondary-600" @change="toggleStatus(status.id)" />
          <span class="text-sm text-gray-700">{{ __(status.label) }}</span>
        </label>
      </div>
    </div>

    <!-- Delegation Matrix -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label class="config-label mb-0">{{ __('Delegation Matrix') }}</label>
        <button class="text-xs brand-link font-medium" @click="addRule">+ {{ __('Add Rule') }}</button>
      </div>
      <div class="space-y-2">
        <div v-for="(rule, idx) in delegationRules" :key="idx" class="rounded-lg border border-gray-200 bg-gray-50/60 p-2.5 space-y-2">
          <div class="grid grid-cols-3 gap-2">
            <div>
              <label class="text-[10px] text-gray-400">{{ __('When Status') }}</label>
              <select :value="rule.status" class="config-select-sm" @change="updateRule(idx, 'status', $event.target.value)">
                <option value="on_leave">{{ __('On Leave') }}</option>
                <option value="resigned">{{ __('Resigned') }}</option>
                <option value="inactive">{{ __('Inactive') }}</option>
                <option value="suspended">{{ __('Suspended') }}</option>
              </select>
            </div>
            <div>
              <label class="text-[10px] text-gray-400">{{ __('Action') }}</label>
              <select :value="rule.action" class="config-select-sm" @change="updateRule(idx, 'action', $event.target.value)">
                <option value="delegate">{{ __('Delegate') }}</option>
                <option value="escalate">{{ __('Escalate') }}</option>
                <option value="fallback">{{ __('Fallback') }}</option>
              </select>
            </div>
            <div class="flex gap-1">
              <div class="flex-1">
                <label class="text-[10px] text-gray-400">{{ __('Target') }}</label>
                <input :value="rule.target" type="text" class="config-input-sm" :placeholder="__('Role/User')" @input="updateRule(idx, 'target', $event.target.value)" />
              </div>
              <button class="mt-4 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500" @click="removeRule(idx)">×</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Fallback -->
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="config-label">{{ __('Fallback Type') }}</label>
        <select :value="config.fallbackType || 'role'" class="config-select" @change="update('fallbackType', $event.target.value)">
          <option value="role">{{ __('Role-based') }}</option>
          <option value="hierarchy">{{ __('Hierarchy-based') }}</option>
          <option value="committee">{{ __('Committee') }}</option>
          <option value="manual">{{ __('Manual') }}</option>
        </select>
      </div>
      <div>
        <label class="config-label">{{ __('Max Depth') }}</label>
        <input :value="config.maxDelegationDepth || 3" type="number" min="1" max="10" class="config-input" @input="update('maxDelegationDepth', parseInt($event.target.value))" />
      </div>
    </div>
    <div>
      <label class="config-label">{{ __('Fallback Target') }}</label>
      <input :value="config.fallbackTarget || ''" type="text" class="config-input" :placeholder="__('Role, position, or user')" @input="update('fallbackTarget', $event.target.value)" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:config'])

const allStatuses = [
  { id: 'on_leave', label: 'On Leave' },
  { id: 'resigned', label: 'Resigned' },
  { id: 'inactive', label: 'Inactive' },
  { id: 'suspended', label: 'Suspended' },
]

const checkedStatuses = computed(() => props.config.checkStatuses || [])
const delegationRules = computed(() => props.config.delegationMatrix || [])

function update(key, value) { emit('update:config', { ...props.config, [key]: value }) }

function toggleStatus(id) {
  const current = [...checkedStatuses.value]
  const idx = current.indexOf(id)
  if (idx >= 0) current.splice(idx, 1)
  else current.push(id)
  update('checkStatuses', current)
}

function addRule() {
  emit('update:config', { ...props.config, delegationMatrix: [...delegationRules.value, { status: 'on_leave', action: 'delegate', target: '' }] })
}

function updateRule(idx, key, value) {
  const arr = [...delegationRules.value]
  arr[idx] = { ...arr[idx], [key]: value }
  emit('update:config', { ...props.config, delegationMatrix: arr })
}

function removeRule(idx) {
  emit('update:config', { ...props.config, delegationMatrix: delegationRules.value.filter((_, i) => i !== idx) })
}
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-select-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
.config-input { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
</style>
