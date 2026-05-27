import './index.css'

if (typeof window !== 'undefined' && typeof window.frappe === 'undefined') {
  window.frappe = {
    session: { user: 'Guest' },
    boot: {},
    _: (msg) => msg,
    realtime: { on: () => {}, off: () => {}, publish: () => {} },
  }
}

window['__'] =
  window['__'] ||
  function (message, replace) {
    if (!replace) return message
    return String(message).replace(/{(\d+)}/g, function (match, number) {
      return typeof replace[number] !== 'undefined' ? replace[number] : match
    })
  }

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createDialog } from './utils/dialogs'
import { initSocket } from './socket'
import router from './router'
import translationPlugin from './translation'
import App from './App.vue'

import {
  FrappeUI,
  Button,
  Input,
  TextInput,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  setConfig,
  frappeRequest,
  FeatherIcon,
} from 'frappe-ui'

import { telemetryPlugin } from 'frappe-ui/frappe'

let globalComponents = {
  Button,
  TextInput,
  Input,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  FeatherIcon,
}

// create a pinia instance
let pinia = createPinia()

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)
app.use(FrappeUI)
app.use(pinia)
app.use(translationPlugin)
for (let key in globalComponents) {
  app.component(key, globalComponents[key])
}

app.config.globalProperties.$dialog = createDialog

let socket
if (import.meta.env.DEV) {
  frappeRequest({
    url: '/api/method/crm.www.crm.get_context_for_dev',
    method: 'GET',
  }).then((values) => {
      const data = values?.message || values
      for (let key in data) {
        window[key] = data[key]
      }
      app.use(router)
      app.use(telemetryPlugin, { app_name: 'crm' })
      socket = initSocket()
      app.config.globalProperties.$socket = socket
      app.provide('socket', socket)
      app.mount('#app')
    },
  )
} else {
  app.use(router)
  app.use(telemetryPlugin, { app_name: 'crm' })
  socket = initSocket()
  app.config.globalProperties.$socket = socket
  app.provide('socket', socket)
  app.mount('#app')
}

if (import.meta.env.DEV) {
  window.$dialog = createDialog
}
