<template>
  <div :class="$route.meta.ownHeader ? 'relative z-40 h-0' : 'flex h-[72px] border-b border-crm-border bg-white pr-5'">
    <div v-if="!$route.meta.ownHeader" id="app-header" class="flex-1">
      <span class="header-fallback flex h-full items-center pl-5 text-lg font-medium text-ink-gray-7">{{ $route.meta.title || $route.name }}</span>
    </div>
    <div :class="$route.meta.ownHeader ? 'absolute right-5 top-2' : 'flex items-center justify-center'">
      <CallUI />
    </div>
  </div>
</template>

<script setup>
import CallUI from '@/components/Telephony/CallUI.vue'
</script>

<style>
#app-header:has(> :not(.header-fallback)) > .header-fallback { display: none; }
</style>
