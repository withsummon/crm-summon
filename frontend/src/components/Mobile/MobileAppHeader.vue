<template>
  <div class="flex pr-3">
    <div class="z-20 ml-2 flex items-center justify-center">
      <Button
        v-if="showBack"
        class="size-7"
        variant="ghosted"
        @click="goBack"
      >
        <FeatherIcon name="arrow-left" class="size-4 text-ink-gray-9" />
      </Button>
      <Button
        v-else
        class="size-7"
        variant="ghosted"
        @click="sidebarOpened = !sidebarOpened"
      >
        <MenuIcon class="h-4 text-ink-gray-9" />
      </Button>
    </div>
    <div id="app-header" class="flex-1" />
  </div>
  <CallUI />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FeatherIcon } from 'frappe-ui'
import MenuIcon from '@/components/Icons/MenuIcon.vue'
import CallUI from '@/components/Telephony/CallUI.vue'
import { mobileSidebarOpened as sidebarOpened } from '@/composables/settings'

const route = useRoute()
const router = useRouter()

const showBack = computed(() => {
  return route.name !== 'Mobile Home Dashboard'
})

function goBack() {
  router.back()
}
</script>
