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

    <template v-else-if="!loadedConversation">
      <div class="flex flex-1 flex-col items-center justify-center gap-4 p-6">
        <FeatherIcon name="message-square" class="h-10 w-10 text-crm-muted/40" />
        <p class="text-sm text-crm-muted">{{ __('No active chat channel for this record') }}</p>
        <Button label="Start Chat" variant="solid" :loading="creating" @click="startChat">
          <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
        </Button>
      </div>
    </template>

    <template v-else>
      <div class="flex items-center justify-between border-b border-crm-border px-4 py-2">
        <div class="min-w-0 text-xs font-semibold text-crm-muted truncate">
          {{ conversation?.conversation?.subject || conversation?.conversation?.name }}
        </div>
        <Button :label="__('Open Omnichannel')" size="sm" variant="outline" @click="openOmnichannel">
          <template #prefix><FeatherIcon name="external-link" class="h-3.5 w-3.5" /></template>
        </Button>
      </div>

      <div ref="messagesContainer" class="flex-1 overflow-y-auto px-4 py-3" @scroll="onScroll">
        <div v-if="messagesLoading" class="flex items-center justify-center py-8">
          <div class="h-6 w-6 animate-spin rounded-full border-3 border-crm-teal border-t-transparent" />
        </div>

        <div v-for="msg in messages" :key="msg.name" class="mb-3 flex flex-col" :class="isMine(msg) ? 'items-end' : 'items-start'">
          <div class="max-w-[80%] rounded-xl px-3 py-2 text-sm" :class="isMine(msg) ? 'bg-crm-teal text-white rounded-br-sm' : 'bg-gray-100 text-crm-text rounded-bl-sm'">
            <div v-if="msg.channel" class="mb-1 flex items-center gap-1 text-[10px] uppercase tracking-wide" :class="isMine(msg) ? 'text-white/60' : 'text-crm-muted'">
              <component :is="channelIcon(msg.channel)" class="h-3 w-3" />
              <span>{{ msg.channel }}</span>
            </div>
            <template v-if="msg.message_type === 'Image' && msg.attachment">
              <img :src="msg.attachment" class="max-h-48 rounded-lg object-cover cursor-pointer mb-1" @click="previewFile(msg)" />
            </template>
            <template v-else-if="msg.message_type === 'Document' && msg.attachment">
              <div class="flex items-center gap-2 rounded-lg bg-white/20 p-2">
                <FeatherIcon name="file" class="h-5 w-5 shrink-0" />
                <a :href="msg.attachment" target="_blank" class="truncate text-sm underline">{{ msg.attachment?.split('/').pop() || 'Document' }}</a>
              </div>
            </template>
            <p v-if="msg.content" class="whitespace-pre-wrap break-words">{{ msg.content }}</p>
            <div class="mt-1 flex items-center gap-1">
              <span class="text-[10px]" :class="isMine(msg) ? 'text-white/70' : 'text-crm-muted'">{{ formatTime(msg.sent_or_received_on || msg.creation) }}</span>
            </div>
          </div>
        </div>

        <div v-if="!messages.length && !messagesLoading" class="flex items-center justify-center py-8">
          <p class="text-xs text-crm-muted">{{ __('No messages yet') }}</p>
        </div>
      </div>

      <div class="border-t border-crm-border">
        <div class="flex border-b border-crm-border">
          <button
            v-for="ch in channels"
            :key="ch.key"
            class="flex flex-1 items-center justify-center gap-1.5 px-2 py-2 text-xs font-medium transition-colors"
            :class="selectedChannel === ch.key ? 'bg-crm-teal text-white' : 'text-crm-muted hover:bg-gray-50 hover:text-crm-text'"
            @click="selectedChannel = ch.key"
          >
            <component :is="ch.icon" class="h-3.5 w-3.5" />
            <span>{{ ch.label }}</span>
          </button>
        </div>
        <div class="px-4 py-3">
          <div class="flex items-center gap-2">
            <button :title="__('Attach file')" class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-crm-border text-crm-muted hover:bg-gray-50 hover:text-crm-text transition-colors" @click="fileInput.click()">
              <FeatherIcon name="paperclip" class="h-4 w-4" />
            </button>
            <input ref="fileInput" type="file" class="hidden" @change="uploadFile" />
            <input
              v-model="newMessage"
              type="text"
              :placeholder="sendPlaceholder"
              class="min-w-0 flex-1 rounded-lg border border-crm-border bg-white px-3 py-2 text-sm outline-none transition-colors placeholder:text-crm-muted focus:border-crm-teal"
              @keydown.enter="send"
            />
            <Button :label="__('Send')" variant="solid" :loading="sending" :disabled="!canSend" @click="send" />
          </div>
          <div v-if="channelWarning" class="mt-1.5 text-[11px] text-amber-600">
            {{ channelWarning }}
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
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount, watch, nextTick, markRaw, h } from 'vue'
import { useRouter } from 'vue-router'
import { Button, FeatherIcon, call, toast } from 'frappe-ui'

const router = useRouter()

const props = defineProps({
  doctype: { type: String, required: true },
  docname: { type: String, required: true },
  leadEmail: { type: String, default: '' },
  leadMobile: { type: String, default: '' },
  leadName: { type: String, default: '' },
})

const loading = ref(true)
const messagesLoading = ref(false)
const sending = ref(false)
const creating = ref(false)
const uploadingFile = ref(false)
const error = ref('')
const conversation = ref(null)
const messages = ref([])
const newMessage = ref('')
const attachedFile = ref(null)
const messagesContainer = ref(null)
const fileInput = ref(null)
const selectedChannel = ref('In-App')
let conversationId = null
let pollTimer = null

const loadedConversation = computed(() => !!conversation.value?.conversation)

const channels = [
  { key: 'In-App', label: 'In-App', icon: markRaw(h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('path', { d: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z' })])) },
  { key: 'WhatsApp', label: 'WhatsApp', icon: markRaw(h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'currentColor' }, [h('path', { d: 'M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z' })])) },
  { key: 'Email', label: 'Email', icon: markRaw(h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('rect', { x: '2', y: '4', width: '20', height: '16', rx: '2' }), h('path', { d: 'm22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7' })])) },
]

const sendPlaceholder = computed(() => {
  if (selectedChannel.value === 'WhatsApp') return __('Type a WhatsApp message...')
  if (selectedChannel.value === 'Email') return __('Type an email message...')
  return __('Type a message...')
})

const channelWarning = computed(() => {
  if (selectedChannel.value === 'WhatsApp' && !props.leadMobile) {
    return __('Lead has no mobile number for WhatsApp')
  }
  if (selectedChannel.value === 'Email' && !props.leadEmail) {
    return __('Lead has no email address')
  }
  return ''
})

const canSend = computed(() => {
  if (selectedChannel.value === 'WhatsApp' && !props.leadMobile) return false
  if (selectedChannel.value === 'Email' && !props.leadEmail) return false
  return !!(newMessage.value.trim() || attachedFile.value)
})

function channelIcon(channel) {
  const ch = channels.find(c => c.key === channel)
  return ch ? ch.icon : FeatherIcon
}

function openOmnichannel() {
  router.push({ name: 'Omnichannel Workspace' })
}

async function init() {
  loading.value = true
  error.value = ''
  conversation.value = null
  messages.value = []
  newMessage.value = ''
  attachedFile.value = null
  stopPolling()
  conversationId = null

  try {
    const res = await call('crm.api.omnichannel.get_conversations', {
      channel: 'In-App',
      reference_doctype: props.doctype,
      reference_name: props.docname,
      limit: 1,
    })
    if (res?.rows?.length) {
      conversationId = res.rows[0].name
      await loadConversation()
      startPolling()
    }
  } catch (err) {
    error.value = err.messages?.[0] || err.message || 'Failed to load chat'
  } finally {
    loading.value = false
  }
}

async function loadConversation() {
  if (!conversationId) return
  messagesLoading.value = true
  try {
    const res = await call('crm.api.omnichannel.get_conversation', {
      conversation_id: conversationId,
    })
    if (res) {
      conversation.value = res
      messages.value = res.messages || []
      await nextTick()
      scrollToBottom()
    }
  } catch (err) {
    console.error('[ChatPanel] loadConversation error:', err)
  } finally {
    messagesLoading.value = false
  }
}

async function startChat() {
  creating.value = true
  try {
    const res = await call('crm.api.omnichannel.create_or_get_conversation', {
      reference_doctype: props.doctype,
      reference_name: props.docname,
    })
    if (res?.conversation) {
      conversationId = res.conversation.name
      conversation.value = res
      messages.value = res.messages || []
      startPolling()
      await nextTick()
      scrollToBottom()
    } else {
      error.value = 'Could not create chat'
    }
  } catch (err) {
    error.value = err.messages?.[0] || err.message || 'Failed to start chat'
  } finally {
    creating.value = false
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
        name: data.message.name,
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
  if (!content && !attachedFile.value) return

  sending.value = true
  try {
    if (selectedChannel.value === 'WhatsApp') {
      await sendWhatsApp(content)
    } else if (selectedChannel.value === 'Email') {
      await sendEmail(content)
    } else {
      await sendInApp(content)
    }
    newMessage.value = ''
    attachedFile.value = null
    if (conversationId) {
      await loadConversation()
    }
  } catch (err) {
    console.error('[ChatPanel] send error:', err)
  } finally {
    sending.value = false
  }
}

async function sendInApp(content) {
  if (!conversationId) {
    await startChat()
    if (!conversationId) return
  }
  await call('crm.api.omnichannel.send_message', {
    conversation_id: conversationId,
    content: content,
    attachments: attachedFile.value ? [attachedFile.value.file_url] : undefined,
  })
}

async function sendWhatsApp(content) {
  const mobile = props.leadMobile
  if (!mobile) {
    toast.error(__('Lead has no mobile number'))
    return
  }
  const res = await call('crm.api.whatsapp.create_whatsapp_message', {
    reference_doctype: props.doctype,
    reference_name: props.docname,
    message: content,
    to: mobile,
    attach: attachedFile.value?.file_url || '',
    reply_to: '',
    content_type: attachedFile.value ? (attachedFile.value.file_url.match(/\.(jpg|jpeg|png|gif|webp)/i) ? 'image' : 'document') : 'text',
  })
  if (res) {
    toast.success(__('WhatsApp message sent'))
  }
}

async function sendEmail(content) {
  const email = props.leadEmail
  if (!email) {
    toast.error(__('Lead has no email address'))
    return
  }
  const leadSubject = props.leadName ? `${props.leadName} (#${props.docname})` : props.docname
  await call('crm.api.omnichannel.send_lead_email', {
    lead: props.docname,
    recipients: email,
    subject: leadSubject,
    content: content,
    attachments: attachedFile.value ? [attachedFile.value.name] : undefined,
  })
  toast.success(__('Email sent'))
}

function previewFile(msg) {
  if (msg.attachment) window.open(msg.attachment, '_blank')
}

function isMine(msg) {
  return msg.from_party === (window.frappe?.session?.user || '')
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
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(loadConversation, 15000)
}

function stopPolling() {
  if (pollTimer) { clearInterval(pollTimer); pollTimer = null }
}

function cleanup() {
  stopPolling()
}

watch(() => props.docname, () => { cleanup(); init() })
onMounted(() => { init() })
onBeforeUnmount(() => { cleanup() })
</script>
