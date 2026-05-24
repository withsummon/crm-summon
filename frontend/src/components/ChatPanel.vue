<template>
  <div class="flex h-full flex-col">
    <div v-if="loading" class="flex flex-1 items-center justify-center">
      <div class="h-8 w-8 animate-spin rounded-full border-4 border-crm-teal border-t-transparent" />
    </div>

    <template v-else-if="error">
      <div class="flex flex-1 flex-col items-center justify-center gap-3 p-6">
        <FeatherIcon name="message-square" class="h-10 w-10 text-red-300" />
        <p class="text-sm text-red-500">{{ error }}</p>
        <Button label="Retry" variant="outline" size="sm" @click="init" />
      </div>
    </template>

    <template v-else-if="noProfile">
      <div class="flex flex-1 flex-col items-center justify-center gap-3 p-6">
        <FeatherIcon name="message-square" class="h-10 w-10 text-crm-muted/40" />
        <p class="text-sm text-crm-muted">{{ __('No ClefinCode Chat profile linked to this contact') }}</p>
      </div>
    </template>

    <template v-else-if="!channel">
      <div class="flex flex-1 flex-col items-center justify-center gap-4 p-6">
        <FeatherIcon name="message-square" class="h-10 w-10 text-crm-muted/40" />
        <p class="text-sm text-crm-muted">{{ __('No active chat channel') }}</p>
        <Button label="Start Chat" variant="solid" :loading="creating" @click="ensureChannel">
          <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
        </Button>
      </div>
    </template>

    <template v-else>
      <div class="flex-1 overflow-y-auto px-4 py-3" ref="messagesContainer">
        <div v-if="messagesLoading" class="flex items-center justify-center py-8">
          <div class="h-6 w-6 animate-spin rounded-full border-3 border-crm-teal border-t-transparent" />
        </div>

        <div v-for="msg in messages" :key="msg.name" class="mb-3 flex" :class="isMine(msg) ? 'justify-end' : 'justify-start'">
          <div class="max-w-[80%] rounded-xl px-3 py-2 text-sm" :class="isMine(msg) ? 'bg-crm-teal text-white rounded-br-sm' : 'bg-gray-100 text-crm-text rounded-bl-sm'">
            <p class="whitespace-pre-wrap break-words">{{ msg.content || msg.message }}</p>
            <p class="mt-1 text-[10px]" :class="isMine(msg) ? 'text-white/70' : 'text-crm-muted'">{{ formatTime(msg.send_date || msg.creation) }}</p>
          </div>
        </div>

        <div v-if="messages.length === 0 && !messagesLoading" class="flex items-center justify-center py-8">
          <p class="text-xs text-crm-muted">{{ __('No messages yet') }}</p>
        </div>
      </div>

      <div class="border-t border-crm-border px-4 py-3">
        <div class="flex items-center gap-2">
          <input
            v-model="newMessage"
            type="text"
            :placeholder="__('Type a message...')"
            class="min-w-0 flex-1 rounded-lg border border-crm-border bg-white px-3 py-2 text-sm outline-none transition-colors placeholder:text-crm-muted focus:border-crm-teal"
            @keydown.enter="send"
          />
          <Button :label="__('Send')" variant="solid" :loading="sending" :disabled="!newMessage.trim()" @click="send" />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Button, FeatherIcon, call } from 'frappe-ui'

const props = defineProps({
  doctype: { type: String, required: true },
  docname: { type: String, required: true },
})

const loading = ref(true)
const messagesLoading = ref(false)
const sending = ref(false)
const creating = ref(false)
const error = ref('')
const noProfile = ref(false)
const channel = ref(null)
const messages = ref([])
const newMessage = ref('')
const messagesContainer = ref(null)
let pollTimer = null

async function init() {
  loading.value = true
  error.value = ''
  noProfile.value = false
  channel.value = null
  messages.value = []
  newMessage.value = ''

  try {
    const res = await call('crm.api.chat.resolve_record_channels', {
      doctype: props.doctype,
      docname: props.docname,
    })

    if (!res.profile) {
      noProfile.value = true
      return
    }

    if (res.channels && res.channels.length) {
      channel.value = res.channels[0]
      await fetchMessages()
    }
  } catch (err) {
    console.error(err)
    error.value = err.messages?.[0] || err.message || 'Failed to load chat'
  } finally {
    loading.value = false
  }
}

async function ensureChannel() {
  creating.value = true
  try {
    const res = await call('crm.api.chat.ensure_channel', {
      doctype: props.doctype,
      docname: props.docname,
    })
    if (res.channel) {
      channel.value = res.channel
      await fetchMessages()
      startPolling()
    } else {
      error.value = 'Could not create chat channel'
    }
  } catch (err) {
    console.error(err)
    error.value = err.messages?.[0] || err.message || 'Failed to create channel'
  } finally {
    creating.value = false
  }
}

async function fetchMessages() {
  if (!channel.value) return
  messagesLoading.value = true
  try {
    const res = await call('crm.api.chat.get_messages', {
      doctype: props.doctype,
      docname: props.docname,
      limit: 50,
      offset: 0,
    })
    if (res.messages) {
      messages.value = res.messages
      await nextTick()
      scrollToBottom()
    }
  } catch (err) {
    console.error(err)
  } finally {
    messagesLoading.value = false
  }
}

async function send() {
  const content = newMessage.value.trim()
  if (!content || !channel.value) return
  sending.value = true
  try {
    await call('crm.api.chat.send_message', {
      doctype: props.doctype,
      docname: props.docname,
      content,
    })
    newMessage.value = ''
    await fetchMessages()
  } catch (err) {
    console.error(err)
  } finally {
    sending.value = false
  }
}

function isMine(msg) {
  return msg.sender === frappe.session.user || msg.owner === frappe.session.user
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(fetchMessages, 5000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

watch(() => props.docname, () => { init() })

onMounted(() => { init() })
onBeforeUnmount(() => { stopPolling() })
</script>
