<template>
  <FrappeUIProvider>
    <NotPermitted v-if="$route.name === 'Not Permitted'" />
    <div v-else-if="$route.meta.standalone && session.isLoggedIn" class="h-screen isolate">
      <router-view :key="$route.fullPath" />
    </div>
    <DesktopLayout
      v-else-if="session.isLoggedIn && !isMobileView"
      :key="$route.fullPath"
    >
      <router-view :key="$route.fullPath" />
    </DesktopLayout>
    <MobileLayout
      v-else-if="session.isLoggedIn"
      :key="$route.fullPath"
    >
      <router-view :key="$route.fullPath" />
    </MobileLayout>
    <Settings v-if="session.isLoggedIn" />
    <Dialogs />
    <DoctypeModals />
    <EventNotificationPopup />
  </FrappeUIProvider>
</template>

<script setup>
import Settings from '@/components/Settings/Settings.vue'
import NotPermitted from '@/pages/NotPermitted.vue'
import EventNotificationPopup from '@/components/EventNotificationPopup.vue'
import DoctypeModals from '@/components/Modals/DoctypeModals.vue'
import DesktopLayout from '@/components/Layouts/DesktopLayout.vue'
import MobileLayout from '@/components/Layouts/MobileLayout.vue'
import { Dialogs } from '@/utils/dialogs'
import { sessionStore } from '@/stores/session'
import { FrappeUIProvider, setConfig, useTheme } from 'frappe-ui'
import { computed, provide, watch } from 'vue'
import { useRoute } from 'vue-router'

const session = sessionStore()
provide('session', session)

function markOnboardingComplete(user) {
  if (!user) return
  localStorage.setItem(`isOnboardingStepsCompletedfrappecrm${user}`, 'true')
}

markOnboardingComplete(session.user)
watch(() => session.user, markOnboardingComplete)

const { setTheme } = useTheme()
if (!localStorage.getItem('theme')) {
  setTheme('light')
}

const route = useRoute()

const isMobileView = computed(() => {
  return window.innerWidth < 640 || route.path.startsWith('/mobile')
})

setConfig('systemTimezone', window.timezone?.system || null)
setConfig('localTimezone', window.timezone?.user || null)
setConfig('translatedMessages', window.translated_messages || {})
</script>
