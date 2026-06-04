<template>
  <div class="space-y-4">
    <!-- Approval Type -->
    <div>
      <label class="config-label">{{ __('Approval Type') }}</label>
      <select
        :value="config.approvalType || 'single'"
        class="config-select"
        @change="update('approvalType', $event.target.value)"
      >
        <option value="single">{{ __('Single Approval') }}</option>
        <option value="sequential">{{ __('Sequential') }}</option>
        <option value="parallel">{{ __('Parallel') }}</option>
        <option value="and">{{ __('AND (All must approve)') }}</option>
        <option value="or">{{ __('OR (Any one can approve)') }}</option>
        <option value="n_of_m">{{ __('N-of-M') }}</option>
        <option value="quorum">{{ __('Quorum') }}</option>
        <option value="majority">{{ __('Majority') }}</option>
        <option value="weighted">{{ __('Weighted') }}</option>
      </select>
    </div>

    <!-- N-of-M Config -->
    <div
      v-if="config.approvalType === 'n_of_m'"
      class="rounded-lg border border-indigo-100 bg-indigo-50/50 p-3"
    >
      <div class="text-xs font-medium text-indigo-600 mb-2">
        {{ __('N-of-M Configuration') }}
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-[11px] text-gray-500">{{ __('Required (N)') }}</label>
          <input
            :value="config.nRequired || 2"
            type="number"
            min="1"
            class="config-input"
            @input="update('nRequired', parseInt($event.target.value))"
          />
        </div>
        <div>
          <label class="text-[11px] text-gray-500">{{ __('Total (M)') }}</label>
          <input
            :value="config.mTotal || approvers.length || 3"
            type="number"
            min="1"
            class="config-input"
            @input="update('mTotal', parseInt($event.target.value))"
          />
        </div>
      </div>
      <p class="mt-2 text-[11px] text-indigo-500">
        {{ __('Require') }} {{ config.nRequired || 2 }} {{ __('out of') }}
        {{ config.mTotal || approvers.length || 3 }} {{ __('approvers') }}
      </p>
    </div>

    <!-- Approvers -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label class="config-label mb-0">{{ __('Approvers') }}</label>
        <button
          class="text-xs brand-link font-medium"
          @click="addApprover"
        >
          + {{ __('Add') }}
        </button>
      </div>
      <div class="space-y-1.5">
        <div
          v-for="(approver, idx) in approvers"
          :key="idx"
          class="flex items-center gap-2"
        >
          <select
            :value="approver.type || 'role'"
            class="config-select-sm w-24 flex-shrink-0"
            @change="updateApprover(idx, 'type', $event.target.value)"
          >
            <option value="role">{{ __('Role') }}</option>
            <option value="user">{{ __('User') }}</option>
            <option value="position">{{ __('Position') }}</option>
            <option value="branch">{{ __('Branch') }}</option>
          </select>
          <input
            :value="approver.value || ''"
            type="text"
            class="config-input-sm flex-1"
            :placeholder="__('Enter name...')"
            @input="updateApprover(idx, 'value', $event.target.value)"
          />
          <button
            class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500"
            @click="removeApprover(idx)"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <!-- Amount-Based Rules -->
    <div>
      <div class="flex items-center justify-between mb-2">
        <label class="config-label mb-0">{{ __('Amount-Based Rules') }}</label>
        <button
          class="text-xs brand-link font-medium"
          @click="addAmountRule"
        >
          + {{ __('Add Rule') }}
        </button>
      </div>
      <div class="space-y-2">
        <div
          v-for="(rule, idx) in amountRules"
          :key="idx"
          class="rounded-lg border border-gray-200 bg-gray-50/60 p-2.5"
        >
          <div class="grid grid-cols-2 gap-2 mb-2">
            <div>
              <label class="text-[10px] text-gray-400">{{ __('Min Amount') }}</label>
              <input
                :value="rule.minAmount"
                type="text"
                class="config-input-sm"
                placeholder="0"
                @input="updateAmountRule(idx, 'minAmount', $event.target.value)"
              />
            </div>
            <div>
              <label class="text-[10px] text-gray-400">{{ __('Max Amount') }}</label>
              <input
                :value="rule.maxAmount"
                type="text"
                class="config-input-sm"
                placeholder="∞"
                @input="updateAmountRule(idx, 'maxAmount', $event.target.value)"
              />
            </div>
          </div>
          <div class="flex items-center gap-2">
            <select
              :value="rule.approvalType || 'single'"
              class="config-select-sm flex-1"
              @change="updateAmountRule(idx, 'approvalType', $event.target.value)"
            >
              <option value="single">{{ __('Single') }}</option>
              <option value="and">{{ __('AND') }}</option>
              <option value="n_of_m">{{ __('N-of-M') }}</option>
            </select>
            <button
              class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-500"
              @click="removeAmountRule(idx)"
            >
              ×
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Timeout & Escalation -->
    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="config-label">{{ __('Timeout (hours)') }}</label>
        <input
          :value="config.timeoutHours || 48"
          type="number"
          min="1"
          class="config-input"
          @input="update('timeoutHours', parseInt($event.target.value))"
        />
      </div>
      <div>
        <label class="config-label">{{ __('Escalation Target') }}</label>
        <input
          :value="config.escalationTarget || ''"
          type="text"
          class="config-input"
          :placeholder="__('Role or user')"
          @input="update('escalationTarget', $event.target.value)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  config: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['update:config'])

const approvers = computed(() => props.config.approvers || [])
const amountRules = computed(() => props.config.amountRules || [])

function update(key, value) {
  emit('update:config', { ...props.config, [key]: value })
}

function addApprover() {
  emit('update:config', {
    ...props.config,
    approvers: [...approvers.value, { type: 'role', value: '' }],
  })
}

function updateApprover(idx, key, value) {
  const arr = [...approvers.value]
  arr[idx] = { ...arr[idx], [key]: value }
  emit('update:config', { ...props.config, approvers: arr })
}

function removeApprover(idx) {
  emit('update:config', {
    ...props.config,
    approvers: approvers.value.filter((_, i) => i !== idx),
  })
}

function addAmountRule() {
  emit('update:config', {
    ...props.config,
    amountRules: [
      ...amountRules.value,
      { minAmount: '', maxAmount: '', approvalType: 'single' },
    ],
  })
}

function updateAmountRule(idx, key, value) {
  const arr = [...amountRules.value]
  arr[idx] = { ...arr[idx], [key]: value }
  emit('update:config', { ...props.config, amountRules: arr })
}

function removeAmountRule(idx) {
  emit('update:config', {
    ...props.config,
    amountRules: amountRules.value.filter((_, i) => i !== idx),
  })
}
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-select-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
.config-input { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input-sm { @apply w-full rounded border border-gray-200 bg-white px-2 py-1.5 text-xs outline-none focus:border-secondary-500; }
</style>
