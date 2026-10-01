<template>
  <div class="flex h-[72px] border-b border-crm-border bg-white pr-5">
    <div id="app-header" class="flex-1">
      <span class="header-fallback flex h-full items-center pl-5 text-lg font-medium text-ink-gray-7">{{ $route.meta.title || $route.name }}</span>
    </div>
    <div class="flex items-center justify-center">
      <CallUI />
    </div>
  </div>
</template>

<script setup>
import CallUI from '@/components/Telephony/CallUI.vue'
</script>

<style>
#app-header:has(> :nth-child(2)) > .header-fallback { display: none; }
</style>
