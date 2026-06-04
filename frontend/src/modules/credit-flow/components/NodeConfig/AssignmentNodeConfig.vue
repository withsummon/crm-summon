<template>
  <div class="space-y-4">
    <div>
      <label class="config-label">{{ __('Assignment Type') }}</label>
      <select :value="config.assignmentType || 'role'" class="config-select" @change="update('assignmentType', $event.target.value)">
        <option value="user">{{ __('Specific User') }}</option>
        <option value="role">{{ __('By Role') }}</option>
        <option value="unit">{{ __('By Unit') }}</option>
        <option value="branch">{{ __('By Branch') }}</option>
        <option value="team">{{ __('By Team') }}</option>
        <option value="auto">{{ __('Auto-Assign') }}</option>
      </select>
    </div>
    <div>
      <label class="config-label">{{ __('Assign To') }}</label>
      <input :value="config.assignTo || ''" type="text" class="config-input" :placeholder="__('User, role, or branch name')" @input="update('assignTo', $event.target.value)" />
    </div>
    <div v-if="config.assignmentType === 'auto'">
      <label class="config-label">{{ __('Auto-Assign Field') }}</label>
      <input :value="config.autoAssignField || ''" type="text" class="config-input" :placeholder="__('Field name for auto-assignment')" @input="update('autoAssignField', $event.target.value)" />
      <p class="mt-1 text-[11px] text-gray-400">{{ __('Application field whose value determines the assignee.') }}</p>
    </div>
    <!-- Assignment Rules -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label class="config-label mb-0">{{ __('Assignment Rules') }}</label>
        <button class="text-xs brand-link font-medium" @click="addRule">+ {{ __('Add Rule') }}</button>
      </div>
      <div class="space-y-2">
        <div v-for="(rule, idx) in rules" :key="idx" class="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50/60 p-2.5">
          <input :value="rule.condition" type="text" class="config-input-sm flex-1" :placeholder="__('IF condition')" @input="updateRule(idx, 'condition', $event.target.value)" />
          <span class="text-xs text-gray-400">→</span>
          <input :value="rule.assignTo" type="text" class="config-input-sm flex-1" :placeholder="__('Assign to')" @input="updateRule(idx, 'assignTo', $event.target.value)" />
          <button class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500" @click="removeRule(idx)">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:config'])
const rules = computed(() => props.config.assignmentRules || [])
function update(key, value) { emit('update:config', { ...props.config, [key]: value }) }
function addRule() { emit('update:config', { ...props.config, assignmentRules: [...rules.value, { condition: '', assignTo: '' }] }) }
function updateRule(idx, key, value) { const arr = [...rules.value]; arr[idx] = { ...arr[idx], [key]: value }; emit('update:config', { ...props.config, assignmentRules: arr }) }
function removeRule(idx) { emit('update:config', { ...props.config, assignmentRules: rules.value.filter((_, i) => i !== idx) }) }
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
</style>
