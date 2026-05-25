import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import router from '@/router'
import { ref, computed } from 'vue'

export const sessionStore = defineStore('crm-session', () => {
  function sessionUser() {
    let cookies = new URLSearchParams(
      document.cookie
        .split(';')
        .map((c) => c.trim())
        .join('&'),
    )
    let _sessionUser = cookies.get('user_id')
    if (_sessionUser) {
      try {
        _sessionUser = decodeURIComponent(_sessionUser)
      } catch (e) {}
      if (_sessionUser.startsWith('"') && _sessionUser.endsWith('"')) {
        _sessionUser = _sessionUser.slice(1, -1)
      }
    }
    if (!_sessionUser || _sessionUser === 'Guest') {
      _sessionUser = window.user
    }
    if (_sessionUser === 'Guest') {
      _sessionUser = null
    }
    return _sessionUser
  }

  let user = ref(sessionUser())
  const isLoggedIn = computed(() => {
    const current = sessionUser()
    if (current && user.value !== current) {
      user.value = current
    }
    return !!current
  })

  const login = createResource({
    url: 'login',
    onError() {
      throw new Error(__('Invalid Email or Password'))
    },
    onSuccess() {
      user.value = sessionUser()
      login.reset()
      router.replace({ path: '/' })
    },
  })

  function redirectToLogin() {
    user.value = null
    window.user = null
    window.location.href = '/login?redirect-to=/crm'
  }

  const logout = createResource({
    url: 'logout',
    onSuccess: redirectToLogin,
    onError: redirectToLogin,
  })

  return {
    user,
    isLoggedIn,
    login,
    logout,
  }
})
