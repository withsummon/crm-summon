<template>
  <div class="flex h-screen w-screen">
    <MobileSidebar />
    <div class="flex h-full flex-1 flex-col overflow-auto bg-surface-white">
      <MobileAppHeader />
      <slot />
    </div>
    <GlobalModals />
    <MobilePwaInstallToast />
  </div>
</template>
<script setup>
import MobileSidebar from '@/components/Mobile/MobileSidebar.vue'
import MobileAppHeader from '@/components/Mobile/MobileAppHeader.vue'
import MobilePwaInstallToast from '@/components/Mobile/MobilePwaInstallToast.vue'
import GlobalModals from '@/components/Modals/GlobalModals.vue'
</script>
