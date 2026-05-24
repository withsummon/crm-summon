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
      <div class="flex items-center justify-between border-b border-crm-border px-4 py-2">
        <div class="min-w-0 text-xs font-semibold text-crm-muted truncate">
          {{ channel.channel_name || channel.name }}
        </div>
        <Button :label="__('Open Omnichannel')" size="sm" variant="outline" @click="openOmnichannel">
          <template #prefix><FeatherIcon name="external-link" class="h-3.5 w-3.5" /></template>
        </Button>
      </div>
      <div class="flex-1 overflow-y-auto px-4 py-3" ref="messagesContainer" @scroll="onScroll">
        <div v-if="messagesLoading" class="flex items-center justify-center py-8">
          <div class="h-6 w-6 animate-spin rounded-full border-3 border-crm-teal border-t-transparent" />
        </div>

        <div v-if="typingUsers.length" class="mb-2 text-xs text-crm-muted italic px-1">
          {{ typingUsers.join(', ') }} {{ __('typing...') }}
        </div>

        <div v-for="msg in messages" :key="msg.name" class="mb-3 flex flex-col" :class="isMine(msg) ? 'items-end' : 'items-start'">
          <div class="max-w-[80%] rounded-xl px-3 py-2 text-sm" :class="isMine(msg) ? 'bg-crm-teal text-white rounded-br-sm' : 'bg-gray-100 text-crm-text rounded-bl-sm'">
            <template v-if="msg.is_media || msg.is_document || msg.is_voice_clip">
              <div v-if="msg.is_media" class="mb-1">
                <img :src="msg.attachment || msg.content" class="max-h-48 rounded-lg object-cover cursor-pointer" @click="previewFile(msg)" />
              </div>
              <div v-else-if="msg.is_document" class="flex items-center gap-2 rounded-lg bg-white/20 p-2">
                <FeatherIcon name="file" class="h-5 w-5 shrink-0" />
                <a :href="msg.attachment" target="_blank" class="truncate text-sm underline">{{ msg.file_name || msg.attachment?.split('/').pop() || 'Document' }}</a>
              </div>
              <div v-else-if="msg.is_voice_clip" class="flex items-center gap-2">
                <FeatherIcon name="headphones" class="h-5 w-5 shrink-0" />
                <audio :src="msg.attachment" controls class="h-8 max-w-[200px]" />
              </div>
            </template>
            <p v-if="msg.content && !msg.is_media" class="whitespace-pre-wrap break-words">{{ msg.content }}</p>
            <div class="mt-1 flex items-center gap-1">
              <span class="text-[10px]" :class="isMine(msg) ? 'text-white/70' : 'text-crm-muted'">{{ formatTime(msg.send_date || msg.creation) }}</span>
              <span v-if="isMine(msg)" class="inline-flex">
                <FeatherIcon v-if="msg.read_by_recipient" name="check-circle" class="h-3 w-3 text-blue-300" />
                <FeatherIcon v-else name="check" class="h-3 w-3 text-white/60" />
              </span>
            </div>
          </div>
        </div>

        <div v-if="messages.length === 0 && !messagesLoading" class="flex items-center justify-center py-8">
          <p class="text-xs text-crm-muted">{{ __('No messages yet') }}</p>
        </div>
      </div>

      <div class="border-t border-crm-border px-4 py-3">
        <div class="flex items-center gap-2">
          <button class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-crm-border text-crm-muted hover:bg-gray-50 hover:text-crm-text transition-colors" @click="fileInput.click()" :title="__('Attach file')">
            <FeatherIcon name="paperclip" class="h-4 w-4" />
          </button>
          <input ref="fileInput" type="file" class="hidden" @change="uploadFile" />
          <input
            v-model="newMessage"
            type="text"
            :placeholder="__('Type a message...')"
            class="min-w-0 flex-1 rounded-lg border border-crm-border bg-white px-3 py-2 text-sm outline-none transition-colors placeholder:text-crm-muted focus:border-crm-teal"
            @keydown.enter="send"
            @input="onTyping"
          />
          <Button :label="__('Send')" variant="solid" :loading="sending" :disabled="!newMessage.trim() && !uploadingFile" @click="send" />
        </div>
        <div v-if="uploadingFile" class="mt-2 flex items-center gap-2 text-xs text-crm-muted">
          <div class="h-4 w-4 animate-spin rounded-full border-2 border-crm-teal border-t-transparent" />
          <span>{{ __('Uploading...') }}</span>
        </div>
        <div v-if="attachedFile" class="mt-2 flex items-center gap-2 rounded-lg bg-gray-50 px-3 py-2 text-xs text-crm-text">
          <FeatherIcon name="paperclip" class="h-3 w-3 shrink-0" />
          <span class="truncate flex-1">{{ attachedFile.file_name }}</span>
          <button class="text-crm-muted hover:text-red-500" @click="attachedFile = null">&times;</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Button, FeatherIcon, call } from 'frappe-ui'
import { globalStore } from '@/stores/global'

const props = defineProps({
  doctype: { type: String, required: true },
  docname: { type: String, required: true },
})

const loading = ref(true)
const messagesLoading = ref(false)
const sending = ref(false)
const creating = ref(false)
const uploadingFile = ref(false)
const error = ref('')
const noProfile = ref(false)
const channel = ref(null)
const messages = ref([])
const newMessage = ref('')
const attachedFile = ref(null)
const typingUsers = ref([])
const messagesContainer = ref(null)
const fileInput = ref(null)
let pollTimer = null
let timeoutTimer = null
let typingTimer = null
let typingTimeout = null
const { $socket } = globalStore()
const router = useRouter()

function openOmnichannel() {
  router.push({ name: 'Omnichannel Communication' })
}

async function init() {
  clearTimeout(timeoutTimer)
  loading.value = true
  error.value = ''
  noProfile.value = false
  channel.value = null
  messages.value = []
  newMessage.value = ''
  attachedFile.value = null
  typingUsers.value = []
  stopPolling()
  teardownSocket()

  timeoutTimer = setTimeout(() => {
    loading.value = false
    error.value = 'Chat service timed out'
  }, 15000)

  try {
    const res = await call('crm.api.chat.resolve_record_channels', {
      doctype: props.doctype,
      docname: props.docname,
    })
    clearTimeout(timeoutTimer)

    if (!res || !res.profile) {
      if (res && res.contact && !res.profile) {
        noProfile.value = true
      } else {
        error.value = 'No profile found'
      }
      return
    }

    if (res.channels && res.channels.length) {
      channel.value = res.channels[0]
      setupSocket()
      await fetchMessages()
      markAsRead()
    }
  } catch (err) {
    clearTimeout(timeoutTimer)
    console.error('[ChatPanel] init error:', err)
    error.value = err.messages?.[0] || err.message || 'Failed to load chat'
  } finally {
    clearTimeout(timeoutTimer)
    loading.value = false
  }
}

function setupSocket() {
  if (!$socket || !channel.value) return
  const ch = channel.value.name
  $socket.on(ch, handleSocketEvent)
  $socket.on('new_chat_notification', handleNotification)
}

function teardownSocket() {
  if (!$socket) return
  if (channel.value) {
    $socket.off(channel.value.name, handleSocketEvent)
  }
  $socket.off('new_chat_notification', handleNotification)
}

function handleSocketEvent(data) {
  if (!data) return
  if (data.realtime_type === 'send_message') {
    fetchMessages()
    markAsRead()
  } else if (data.realtime_type === 'typing') {
    handleTypingEvent(data)
  }
}

function handleNotification(data) {
  if (data && data.channel === channel.value?.name) {
    fetchMessages()
  }
}

function handleTypingEvent(data) {
  const currentUser = window.frappe?.session?.user || ''
  if (!data.user || data.user === currentUser) return

  if (data.is_typing === 'true') {
    if (!typingUsers.value.includes(data.first_name || data.user)) {
      typingUsers.value.push(data.first_name || data.user)
    }
  } else {
    const name = data.first_name || data.user
    typingUsers.value = typingUsers.value.filter(u => u !== name)
  }
}

function onTyping() {
  if (!channel.value) return
  const api = 'clefincode_chat.api.api_1_3_4.api.set_typing'
  call(api, {
    user: window.frappe?.session?.user || '',
    room: channel.value.name,
    is_typing: 'true',
  }).catch(() => {})

  clearTimeout(typingTimeout)
  typingTimeout = setTimeout(() => {
    call(api, {
      user: window.frappe?.session?.user || '',
      room: channel.value.name,
      is_typing: 'false',
    }).catch(() => {})
  }, 3000)
}

function markAsRead() {
  if (!channel.value) return
  call('clefincode_chat.api.api_1_3_4.api.mark_messsages_as_read', {
    user: window.frappe?.session?.user || '',
    channel: channel.value.name,
  }).catch(() => {})
}

async function ensureChannel() {
  creating.value = true
  try {
    const res = await call('crm.api.chat.ensure_channel', {
      doctype: props.doctype,
      docname: props.docname,
    })
    if (res && res.channel) {
      channel.value = res.channel
      setupSocket()
      await fetchMessages()
      markAsRead()
    } else {
      error.value = 'Could not create chat channel'
    }
  } catch (err) {
    console.error('[ChatPanel] ensureChannel error:', err)
    error.value = err.messages?.[0] || err.message || 'Failed to create channel'
  } finally {
    creating.value = false
  }
}

async function fetchMessages() {
  if (!channel.value) return
  const prevLen = messages.value.length
  messagesLoading.value = true
  try {
    const res = await call('crm.api.chat.get_messages', {
      doctype: props.doctype,
      docname: props.docname,
      limit: 50,
      offset: 0,
    })
    if (res && res.messages) {
      messages.value = res.messages
      if (prevLen === 0 || res.messages.length > prevLen) {
        await nextTick()
        scrollToBottom()
      }
    }
  } catch (err) {
    console.error('[ChatPanel] fetchMessages error:', err)
  } finally {
    messagesLoading.value = false
  }
}

async function uploadFile(e) {
  const file = e.target?.files?.[0]
  if (!file) return
  uploadingFile.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_private', '0')
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token || '' },
      body: formData,
    })
    const data = await res.json()
    if (data.message) {
      attachedFile.value = {
        file_url: data.message.file_url,
        file_name: data.message.file_name,
        file_id: data.message.name,
      }
    }
  } catch (err) {
    console.error('[ChatPanel] upload error:', err)
  } finally {
    uploadingFile.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function send() {
  const content = newMessage.value.trim()
  const file = attachedFile.value
  if (!content && !file) return
  sending.value = true

  try {
    const args = {
      content: content || (file ? file.file_name : ''),
      user: window.frappe?.session?.user || '',
      room: channel.value.name,
      email: window.frappe?.session?.user || '',
      message_type: '',
    }
    if (file) {
      args.attachment = file.file_url
      args.file_id = file.file_id
      const ext = file.file_name?.split('.').pop()?.toLowerCase()
      const imgExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']
      args.is_media = imgExts.includes(ext) ? 1 : 0
      const docExts = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
      if (!args.is_media && docExts.includes(ext)) {
        args.is_document = 1
      }
    }

    await call('clefincode_chat.api.api_1_3_4.api.send', args)
    newMessage.value = ''
    attachedFile.value = null
    await fetchMessages()
    markAsRead()
  } catch (err) {
    console.error('[ChatPanel] send error:', err)
  } finally {
    sending.value = false
  }
}

function previewFile(msg) {
  if (msg.attachment) {
    window.open(msg.attachment, '_blank')
  }
}

function isMine(msg) {
  if (!msg) return false
  const user = window.frappe?.session?.user || ''
  return msg.sender === user || msg.owner === user
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function onScroll() {
  if (!channel.value) return
  const el = messagesContainer.value
  if (el && el.scrollTop + el.clientHeight >= el.scrollHeight - 100) {
    markAsRead()
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(fetchMessages, 15000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function cleanup() {
  stopPolling()
  clearTimeout(timeoutTimer)
  clearTimeout(typingTimeout)
  teardownSocket()
}

watch(() => props.docname, () => { cleanup(); init() })

onMounted(() => { init() })
onBeforeUnmount(() => { cleanup() })
</script>
