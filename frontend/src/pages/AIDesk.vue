<template>
  <div class="flex h-full items-center justify-center bg-slate-50 text-sm text-slate-500">
    {{ __('Redirecting to AI Agent Center...') }}
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  router.replace({ name: 'AI Agent Center' })
})
</script>
