<template>
  <div class="flex items-center justify-between gap-4 crm-animate-in">
    <!-- Left: Time filters -->
    <div class="crm-filter-group">
      <button
        v-for="filter in timeFilters"
        :key="filter.value"
        class="crm-filter-item"
        :class="{ active: activeFilter === filter.value }"
        @click="selectFilter(filter.value)"
      >
        <div class="flex items-center gap-1.5">
          <component
            :is="filter.icon"
            v-if="filter.icon"
            class="w-3.5 h-3.5"
          />
          <span>{{ __(filter.label) }}</span>
        </div>
      </button>
    </div>

    <!-- Right: All + User selector -->
    <div class="flex items-center gap-2">
      <!-- All filter -->
      <div class="crm-filter-group">
        <button
          class="crm-filter-item"
          :class="{ active: showAll }"
          @click="toggleAll"
        >
          <div class="flex items-center gap-1.5">
            <LucideLayers class="w-3.5 h-3.5" />
            <span>{{ __('All') }}</span>
          </div>
        </button>
      </div>

      <!-- User selector -->
      <div class="crm-filter-group">
        <button
          class="crm-filter-item active"
          @click="$emit('select-user')"
        >
          <div class="flex items-center gap-1.5">
            <LucideUser class="w-3.5 h-3.5" />
            <span class="max-w-[120px] truncate">
              {{ activeUser || __('Select User') }}
            </span>
            <LucideChevronDown class="w-3 h-3 text-crm-muted" />
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, markRaw } from 'vue'
import LucideSun from '~icons/lucide/sun'
import LucideHistory from '~icons/lucide/history'
import LucideCalendarDays from '~icons/lucide/calendar-days'
import LucideCalendarRange from '~icons/lucide/calendar-range'
import LucideCalendarSearch from '~icons/lucide/calendar-search'
import LucideLayers from '~icons/lucide/layers'
import LucideUser from '~icons/lucide/user'
import LucideChevronDown from '~icons/lucide/chevron-down'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'today',
  },
  user: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'update:user', 'select-user'])

const showAll = ref(false)

const timeFilters = [
  { label: 'Today', value: 'today', icon: markRaw(LucideSun) },
  { label: 'Yesterday', value: 'yesterday', icon: markRaw(LucideHistory) },
  { label: 'Weekly', value: 'weekly', icon: markRaw(LucideCalendarDays) },
  { label: 'Monthly', value: 'monthly', icon: markRaw(LucideCalendarRange) },
  { label: 'Select Date', value: 'select_date', icon: markRaw(LucideCalendarSearch) },
]

const activeFilter = computed(() => props.modelValue)
const activeUser = computed(() => props.user)

function selectFilter(value) {
  emit('update:modelValue', value)
}

function toggleAll() {
  showAll.value = !showAll.value
}
</script>
