<template>
  <div
    class="flex flex-col items-center justify-center min-h-screen bg-surface-gray-1"
  >
    <div class="text-center max-w-md">
      <h1 class="text-ink-gray-5 text-3xl font-semibold">
        {{ __('Access Denied') }}
      </h1>
      <div class="border-t w-full my-[15px]" />
      <p class="text-ink-gray-4 text-p-base">
        {{
          __(
            'You do not have enough permissions to access BNI CRM. Please contact your administrator if you believe this is an error.',
          )
        }}
      </p>

      <Button
        class="mt-5 w-full"
        variant="solid"
        :label="__('Login with Different Account')"
        @click="switchAccount"
      />
    </div>
  </div>
</template>
<script setup>
import { sessionStore } from '@/stores/session'
const { logout } = sessionStore()

function switchAccount() {
  logout.submit()
  window.location.href = '/login?redirect-to=/crm'
}
</script>
