<template>
  <div class="space-y-4">
    <div>
      <label class="config-label">{{ __('Committee') }}</label>
      <input :value="config.committee || ''" type="text" class="config-input" :placeholder="__('Committee name or ID')" @input="update('committee', $event.target.value)" />
    </div>
    <div>
      <label class="config-label">{{ __('Quorum Type') }}</label>
      <select :value="config.quorumType || 'majority'" class="config-select" @change="update('quorumType', $event.target.value)">
        <option value="majority">{{ __('Majority') }}</option>
        <option value="unanimous">{{ __('Unanimous') }}</option>
        <option value="n_of_m">{{ __('N-of-M') }}</option>
        <option value="weighted">{{ __('Weighted') }}</option>
      </select>
    </div>
    <div v-if="config.quorumType === 'n_of_m'">
      <label class="config-label">{{ __('Quorum N (Minimum Members)') }}</label>
      <input :value="config.quorumN || 2" type="number" min="1" class="config-input" @input="update('quorumN', parseInt($event.target.value))" />
    </div>
    <div>
      <label class="config-label">{{ __('Voting Method') }}</label>
      <select :value="config.votingMethod || 'majority'" class="config-select" @change="update('votingMethod', $event.target.value)">
        <option value="majority">{{ __('Majority Vote') }}</option>
        <option value="unanimous">{{ __('Unanimous') }}</option>
        <option value="weighted">{{ __('Weighted Vote') }}</option>
      </select>
    </div>
    <label class="flex items-center gap-2 cursor-pointer">
      <input type="checkbox" :checked="config.meetingRequired" class="h-4 w-4 rounded border-gray-300 text-secondary-600" @change="update('meetingRequired', $event.target.checked)" />
      <span class="text-sm text-gray-700">{{ __('Meeting Required') }}</span>
    </label>
    <div>
      <label class="config-label">{{ __('Timeout (days)') }}</label>
      <input :value="config.timeoutDays || 7" type="number" min="1" class="config-input" @input="update('timeoutDays', parseInt($event.target.value))" />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ config: { type: Object, default: () => ({}) } })
const emit = defineEmits(['update:config'])
function update(key, value) { emit('update:config', { ...props.config, [key]: value }) }
</script>

<style scoped>
.config-label { @apply mb-1 block text-xs font-medium text-gray-600; }
.config-select { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
.config-input { @apply w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm outline-none focus:border-secondary-500; }
</style>
