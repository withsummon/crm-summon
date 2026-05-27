<template>
  <button
    class="flex h-7.5 cursor-pointer items-center rounded-[10px] duration-300 ease-in-out focus:outline-none focus:transition-none focus-visible:rounded-[10px] focus-visible:ring-2 focus-visible:ring-crm-teal/40"
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
  beforeNavigate: { type: Function, default: null },
})

const buttonClasses = computed(() => {
  if (props.theme === 'light') {
    return isActive.value
      ? 'bg-surface-selected text-ink-gray-9 shadow-sm'
      : 'text-ink-gray-7 hover:bg-surface-gray-3 hover:text-ink-gray-9'
  }
  // CRM theme (DESIGN.md — BNI Teal)
  return isActive.value
    ? 'bg-crm-surface text-crm-text font-semibold'
    : 'text-crm-text-secondary hover:bg-crm-surface hover:text-crm-text'
})

const iconClasses = computed(() => {
  if (props.theme === 'light') {
    return isActive.value ? 'text-ink-gray-9' : 'text-ink-gray-5'
  }
  return isActive.value ? 'text-crm-teal' : 'text-crm-muted'
})

function handleClick() {
  if (props.beforeNavigate) {
    props.beforeNavigate()
    return
  }
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
