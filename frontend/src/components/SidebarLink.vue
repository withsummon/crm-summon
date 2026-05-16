<template>
  <button
    class="flex h-7.5 cursor-pointer items-center rounded duration-300 ease-in-out focus:outline-none focus:transition-none focus-visible:rounded focus-visible:ring-2 focus-visible:ring-primary-300"
    :class="buttonClasses"
    @click="handleClick"
  >
    <div
      class="flex w-full items-center justify-between duration-300 ease-in-out"
      :class="isCollapsed ? 'ml-[3px] p-1' : 'px-2 py-[7px]'"
    >
      <div class="flex items-center truncate">
        <Tooltip :text="label" placement="right" :disabled="!isCollapsed">
          <slot name="icon">
            <Icon
              :icon="icon"
              class="flex items-center size-4"
              :class="iconClasses"
            />
          </slot>
        </Tooltip>
        <Tooltip
          :text="label"
          placement="right"
          :disabled="isCollapsed"
          :hoverDelay="1.5"
        >
          <span
            class="flex-1 flex-shrink-0 truncate text-sm duration-300 ease-in-out"
            :class="
              isCollapsed
                ? 'ml-0 w-0 overflow-hidden opacity-0'
                : 'ml-2 w-auto opacity-100'
            "
          >
            {{ label }}
          </span>
        </Tooltip>
      </div>
      <slot name="right" />
    </div>
  </button>
</template>

<script setup>
import Icon from '@/components/Icon.vue'
import { Tooltip } from 'frappe-ui'
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { isMobileView, mobileSidebarOpened } from '@/composables/settings'

const router = useRouter()
const route = useRoute()

const props = defineProps({
  icon: { type: [Object, String, Function], default: null },
  label: { type: String, default: '' },
  to: { type: [Object, String], default: null },
  isCollapsed: { type: Boolean, default: false },
  theme: { type: String, default: 'dark' },
})

const buttonClasses = computed(() => {
  if (props.theme === 'light') {
    return isActive.value
      ? 'bg-surface-selected text-ink-gray-9 shadow-sm'
      : 'text-ink-gray-7 hover:bg-surface-gray-3 hover:text-ink-gray-9'
  }
  return isActive.value
    ? 'bg-primary-500 text-white shadow-sm'
    : 'text-white/75 hover:bg-summon-charcoal hover:text-white'
})

const iconClasses = computed(() => {
  if (props.theme === 'light') {
    return isActive.value ? 'text-ink-gray-9' : 'text-ink-gray-5'
  }
  return isActive.value ? 'text-white' : 'text-white/75'
})

function handleClick() {
  if (!props.to) return
  if (typeof props.to === 'object') {
    router.push(props.to)
  } else {
    router.push({ name: props.to })
  }
  if (isMobileView.value) {
    mobileSidebarOpened.value = false
  }
}

let isActive = computed(() => {
  if (route.query.view) {
    return route.query.view == props.to?.query?.view
  }
  return route.name === props.to
})
</script>

