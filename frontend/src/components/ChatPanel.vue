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

      <div class="flex-1 overflow-y-auto px-4 py-3" ref="messagesContainer" @scroll="onScroll">
        <div v-if="messagesLoading" class="flex items-center justify-center py-8">
          <div class="h-6 w-6 animate-spin rounded-full border-3 border-crm-teal border-t-transparent" />
        </div>

        <div v-for="msg in messages" :key="msg.name" class="mb-3 flex flex-col" :class="isMine(msg) ? 'items-end' : 'items-start'">
          <div class="max-w-[80%] rounded-xl px-3 py-2 text-sm" :class="isMine(msg) ? 'bg-crm-teal text-white rounded-br-sm' : 'bg-gray-100 text-crm-text rounded-bl-sm'">
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
import { computed, ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Button, FeatherIcon, call } from 'frappe-ui'

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
const conversation = ref(null)
const messages = ref([])
const newMessage = ref('')
const attachedFile = ref(null)
const messagesContainer = ref(null)
const fileInput = ref(null)
let conversationId = null
let pollTimer = null

const loadedConversation = computed(() => !!conversation.value?.conversation)

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
  if (!conversationId) return
  sending.value = true
  try {
    await call('crm.api.omnichannel.send_message', {
      conversation_id: conversationId,
      content: content,
      attachments: attachedFile.value ? [attachedFile.value.file_url] : undefined,
    })
    newMessage.value = ''
    attachedFile.value = null
    await loadConversation()
  } catch (err) {
    console.error('[ChatPanel] send error:', err)
  } finally {
    sending.value = false
  }
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
  const el = messagesContainer.value
  if (el && el.scrollTop + el.clientHeight >= el.scrollHeight - 100) {
    // Could mark as read here
  }
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
