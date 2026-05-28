<template>
  <FrappeUIProvider>
    <NotPermitted v-if="$route.name === 'Not Permitted'" />
    <div v-else-if="$route.meta.standalone && session.isLoggedIn" class="h-screen isolate">
      <router-view :key="$route.fullPath" />
    </div>
    <component :is="Layout" v-else-if="session.isLoggedIn" :key="route.path.startsWith('/mobile') ? 'mobile' : 'desktop'" class="isolate">
      <router-view :key="$route.fullPath" />
    </component>
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
import { Dialogs } from '@/utils/dialogs'
import { sessionStore } from '@/stores/session'
import { FrappeUIProvider, setConfig, useTheme } from 'frappe-ui'
import { computed, defineAsyncComponent, provide, watch } from 'vue'
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
const MobileLayout = defineAsyncComponent(
  () => import('./components/Layouts/MobileLayout.vue'),
)
const DesktopLayout = defineAsyncComponent(
  () => import('./components/Layouts/DesktopLayout.vue'),
)
const Layout = computed(() => {
  if (window.innerWidth < 640 || route.path.startsWith('/mobile')) {
    return MobileLayout
  } else {
    return DesktopLayout
  }
})

setConfig('systemTimezone', window.timezone?.system || null)
setConfig('localTimezone', window.timezone?.user || null)
setConfig('translatedMessages', window.translated_messages || {})
</script>
