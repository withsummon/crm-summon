<template>
  <div class="flex min-h-screen items-center justify-center bg-gradient-to-br from-[#FFF5EF] to-[#FFE8D6] p-4">
    <div class="w-full max-w-md rounded-[14px] border border-outline-gray-2 bg-white p-6 shadow-xl">
      <div class="mb-6 text-center">
        <h1 class="text-xl font-bold text-ink-gray-9">{{ __('Customer Portal') }}</h1>
        <p class="mt-1 text-sm text-ink-gray-5">{{ __('Manage your facilities and payments') }}</p>
      </div>

      <div class="mb-4 flex border-b border-outline-gray-2">
        <button
          class="flex-1 pb-2 text-sm font-medium"
          :class="authTab === 'login' ? 'border-b-2 border-[#FF6600] text-[#FF6600]' : 'text-ink-gray-5'"
          @click="authTab = 'login'"
        >{{ __('Login') }}</button>
        <button
          class="flex-1 pb-2 text-sm font-medium"
          :class="authTab === 'register' ? 'border-b-2 border-[#FF6600] text-[#FF6600]' : 'text-ink-gray-5'"
          @click="authTab = 'register'"
        >{{ __('Register') }}</button>
      </div>

      <div v-if="authTab === 'login'" class="space-y-3">
        <div>
          <label class="mb-1 block text-xs font-medium text-ink-gray-6">{{ __('Email or Phone') }}</label>
          <input v-model="loginForm.identifier" type="text" class="h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm focus:border-[#FF6600] focus:outline-none" />
        </div>
        <div>
          <label class="mb-1 block text-xs font-medium text-ink-gray-6">{{ __('Password') }}</label>
          <input v-model="loginForm.password" type="password" class="h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm focus:border-[#FF6600] focus:outline-none" />
        </div>
        <div class="flex items-center justify-between text-xs">
          <label class="flex items-center gap-2 text-ink-gray-7"><input v-model="loginForm.remember" type="checkbox" class="size-4 accent-[#FF6600]" /> {{ __('Remember me') }}</label>
          <button class="text-[#FF6600] hover:underline" @click="showReset = true">{{ __('Forgot password?') }}</button>
        </div>
        <Button class="w-full" variant="solid" :loading="loggingIn" @click="doLogin">{{ __('Sign In') }}</Button>
      </div>

      <div v-else class="space-y-3">
        <div v-if="registerStep === 1">
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">{{ __('Full Name') }}</label>
            <input v-model="registerForm.name" type="text" class="h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm focus:border-[#FF6600] focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">{{ __('Email') }}</label>
            <input v-model="registerForm.email" type="email" class="h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm focus:border-[#FF6600] focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">{{ __('Phone') }}</label>
            <input v-model="registerForm.phone" type="tel" class="h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm focus:border-[#FF6600] focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">{{ __('Password') }}</label>
            <input v-model="registerForm.password" type="password" class="h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm focus:border-[#FF6600] focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">{{ __('Confirm Password') }}</label>
            <input v-model="registerForm.confirm" type="password" class="h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm focus:border-[#FF6600] focus:outline-none" />
          </div>
          <label class="flex items-center gap-2 text-xs text-ink-gray-7">
            <input v-model="registerForm.accept" type="checkbox" class="size-4 accent-[#FF6600]" />
            {{ __('I accept the Terms & Conditions') }}
          </label>
          <Button class="w-full" variant="solid" :loading="registering" @click="startRegister">{{ __('Continue') }}</Button>
        </div>
        <div v-else class="space-y-3">
          <p class="text-sm text-ink-gray-7">{{ __('Enter the 6-digit OTP sent to your email/phone') }}</p>
          <div class="flex justify-center gap-2">
            <input v-model="otp" type="text" maxlength="6" class="h-10 w-32 rounded-md border border-outline-gray-2 bg-white px-3 text-center text-lg tracking-widest focus:border-[#FF6600] focus:outline-none" />
          </div>
          <Button class="w-full" variant="solid" :loading="verifying" @click="verifyOtp">{{ __('Verify & Create Account') }}</Button>
          <button class="w-full text-xs text-ink-gray-5" @click="registerStep = 1">{{ __('Back') }}</button>
        </div>
      </div>
    </div>

    <Dialog v-model="showReset" :options="{ title: __('Reset Password'), size: 'sm' }">
      <template #body-content>
        <div class="space-y-3">
          <input v-model="resetForm.identifier" type="text" placeholder="Email or phone" class="h-9 w-full rounded-md border border-outline-gray-2 bg-white px-3 text-sm" />
          <Button class="w-full" variant="solid" @click="requestReset">{{ __('Send OTP') }}</Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Button, Dialog, toast } from 'frappe-ui'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const authTab = ref('login')
const loggingIn = ref(false)
const registering = ref(false)
const verifying = ref(false)
const registerStep = ref(1)
const otp = ref('')
const showReset = ref(false)

const loginForm = reactive({ identifier: '', password: '', remember: false })
const registerForm = reactive({ name: '', email: '', phone: '', password: '', confirm: '', accept: false })
const resetForm = reactive({ identifier: '' })

function __(s) { return s }

async function doLogin() {
  if (!loginForm.identifier || !loginForm.password) {
    toast.error('Please fill in all fields')
    return
  }
  loggingIn.value = true
  try {
    const res = await frappe.call('crm.api.portal_auth.portal_login', {
      identifier: loginForm.identifier,
      password: loginForm.password,
    })
    if (res.message) {
      localStorage.setItem('crm:portal:session', JSON.stringify({ ...res.message, loginAt: new Date().toISOString() }))
      router.push('/customer-portal')
    }
  } catch (e) {
    toast.error(e?.message || 'Login failed')
  } finally {
    loggingIn.value = false
  }
}

async function startRegister() {
  if (!registerForm.name || !registerForm.email || !registerForm.password) {
    toast.error('Please fill in all required fields')
    return
  }
  if (registerForm.password !== registerForm.confirm) {
    toast.error('Passwords do not match')
    return
  }
  if (!registerForm.accept) {
    toast.error('Please accept the Terms & Conditions')
    return
  }
  registering.value = true
  try {
    await frappe.call('crm.api.portal_auth.portal_register', {
      email: registerForm.email,
      phone: registerForm.phone,
      password: registerForm.password,
      name: registerForm.name,
    })
    registerStep.value = 2
  } catch (e) {
    toast.error(e?.message || 'Registration failed')
  } finally {
    registering.value = false
  }
}

async function verifyOtp() {
  if (otp.value !== '123456') {
    toast.error('Invalid OTP')
    return
  }
  verifying.value = true
  try {
    await frappe.call('crm.api.portal_auth.portal_verify_otp', { token: 'demo', otp: otp.value })
    toast.success('Account created')
    authTab.value = 'login'
    registerStep.value = 1
  } catch (e) {
    toast.error(e?.message || 'Verification failed')
  } finally {
    verifying.value = false
  }
}

async function requestReset() {
  if (!resetForm.identifier) {
    toast.error('Please enter your email or phone')
    return
  }
  toast.success('OTP sent (use 123456)')
  showReset.value = false
}
</script>
