<template>
  <button
    class="flex h-7.5 cursor-pointer items-center rounded-[14px] duration-300 ease-in-out focus:outline-none focus:transition-none focus-visible:rounded-[14px] focus-visible:ring-2 focus-visible:ring-crm-orange/40"
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
  href: { type: String, default: '' },
  isCollapsed: { type: Boolean, default: false },
  theme: { type: String, default: 'crm' },
})

const buttonClasses = computed(() => {
  if (props.theme === 'light') {
    return isActive.value
      ? 'bg-surface-selected text-ink-gray-9 shadow-sm'
      : 'text-ink-gray-7 hover:bg-surface-gray-3 hover:text-ink-gray-9'
  }
  // CRM theme (DESIGN.md)
  return isActive.value
    ? 'crm-sidebar-active text-[#e8872f] font-semibold'
    : 'text-[#222] hover:bg-crm-peach hover:text-[#111]'
})

const iconClasses = computed(() => {
  if (props.theme === 'light') {
    return isActive.value ? 'text-ink-gray-9' : 'text-ink-gray-5'
  }
  return isActive.value ? 'text-[#e8872f]' : 'text-[#777]'
})

function handleClick() {
  if (props.href) {
    window.location.href = props.href
  } else if (typeof props.to === 'object') {
    router.push(props.to)
  } else if (props.to) {
    router.push({ name: props.to })
  } else {
    return
  }

  if (isMobileView.value) {
    mobileSidebarOpened.value = false
  }
}

let isActive = computed(() => {
  if (props.href) {
    let targetPath = new URL(props.href, window.location.origin).pathname
    let currentPath = window.location.pathname

    return (
      currentPath === targetPath ||
      currentPath.startsWith(`${targetPath}/`) ||
      route.fullPath === targetPath.replace(/^\/crm/, '')
    )
  }

  if (route.query.view) {
    return route.query.view == props.to?.query?.view
  }

  if (typeof props.to === 'object') {
    return route.name === props.to?.name
  }

  return route.name === props.to
})
</script>

<style scoped>
.crm-sidebar-active {
  background: linear-gradient(90deg, rgba(255, 160, 64, 0.18), rgba(180, 120, 255, 0.22));
}
</style>
