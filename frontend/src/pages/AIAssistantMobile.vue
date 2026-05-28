<template>
  <div class="flex flex-1 flex-col bg-crm-surface">
    <div class="bg-white px-4 pb-3 pt-2">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-crm-text">
          {{ __('Asisten AI') }}
        </h1>
        <button
          v-if="messages.length > 0"
          class="flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-crm-text-secondary hover:bg-crm-surface"
          @click="clearChat"
        >
          <FeatherIcon name="trash-2" class="size-3.5" />
          {{ __('Hapus') }}
        </button>
      </div>
    </div>

    <div v-if="ragStatus === 'indexing'" class="mx-4 mt-3 rounded-xl bg-amber-50 border border-amber-200 p-3">
      <div class="flex items-center gap-2">
        <FeatherIcon name="loader" class="size-4 animate-spin text-amber-600 shrink-0" />
        <p class="text-xs text-amber-700">{{ ragMessage }}</p>
      </div>
    </div>

    <div v-if="ragStatus === 'error'" class="mx-4 mt-3 rounded-xl bg-red-50 border border-red-200 p-3">
      <p class="text-xs text-red-700">{{ ragMessage }}</p>
    </div>

    <div class="chat-messages flex-1 overflow-y-auto px-4 pb-6 space-y-4">
      <template v-if="messages.length === 0">
        <div class="flex flex-col items-center justify-center py-16 text-center">
          <FeatherIcon name="message-circle" class="size-12 text-crm-muted mb-4" />
          <p class="text-sm text-crm-text-secondary max-w-xs">
            {{ __('Halo! Saya asisten AI Anda. Tanyakan apa saja tentang portofolio atau nasabah Anda') }}
          </p>
        </div>

        <div class="flex flex-wrap gap-2 justify-center">
          <button
            v-for="suggestion in suggestions"
            :key="suggestion.text"
            class="rounded-xl border border-crm-border bg-white px-4 py-2.5 text-sm text-crm-text shadow-sm hover:border-crm-teal hover:text-crm-teal transition-colors"
            @click="sendSuggestion(suggestion.text)"
          >
            <FeatherIcon :name="suggestion.icon" class="size-3.5 inline mr-1.5" />
            {{ suggestion.text }}
          </button>
        </div>
      </template>

      <template v-else>
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="flex flex-col space-y-1.5"
          :class="msg.role === 'user' ? 'items-end' : 'items-start'"
        >
          <div
            class="max-w-[85%] rounded-2xl px-4 py-2.5 shadow-sm"
            :class="msg.role === 'user'
              ? 'bg-crm-teal text-white rounded-tr-sm'
              : 'bg-white border border-crm-border text-crm-text rounded-tl-sm'"
          >
            <!-- Collapsible Thinking Process -->
            <div v-if="msg.role === 'assistant' && (msg.thinking || (msg.thinkingActive && msg.statusMessage))" class="mb-2 rounded-xl bg-crm-surface border border-crm-border p-3 text-xs text-crm-text-secondary">
              <details :open="msg.thinkingActive || !msg.text" class="group">
                <summary class="flex items-center gap-2 font-semibold cursor-pointer select-none outline-none">
                  <FeatherIcon
                    name="cpu"
                    class="size-3.5 text-crm-teal shrink-0"
                    :class="msg.thinkingActive ? 'animate-pulse' : ''"
                  />
                  <span>{{ msg.thinkingActive ? (msg.statusMessage || __('Berpikir...')) : __('Proses Berpikir AI') }}</span>
                  <FeatherIcon
                    name="chevron-down"
                    class="size-3.5 ml-auto text-crm-muted transition-transform group-open:rotate-180"
                  />
                </summary>
                <div class="mt-2 pl-3 font-mono text-[10px] leading-5 whitespace-pre-wrap border-l border-crm-teal/30 text-crm-muted max-h-40 overflow-y-auto">
                  {{ msg.thinking || __('Menganalisis...') }}
                </div>
              </details>
            </div>

            <!-- Main Response Text / Structured Card -->
            <template v-if="msg.text && !(msg.thinkingActive && msg.text.trim().startsWith('{'))">
              <StructuredResponseCard v-if="msg.structuredResponse" :response="msg.structuredResponse" :fallback="msg.text" compact />
              <p v-else class="text-sm whitespace-pre-wrap leading-6">{{ msg.text }}</p>
            </template>
            <div v-else-if="msg.thinkingActive" class="flex items-center gap-2 py-1.5 text-xs text-crm-muted animate-pulse">
              <FeatherIcon name="loader" class="size-3.5 animate-spin text-crm-teal shrink-0" />
              <span>{{ msg.statusMessage || __('Menyusun analisis terstruktur...') }}</span>
            </div>

            <!-- Metadata / Timestamp -->
            <p
              class="text-[9px] mt-1.5 opacity-60"
              :class="msg.role === 'user' ? 'text-white/70' : 'text-crm-muted'"
            >
              {{ timeAgo(msg.time) }}
            </p>
          </div>
        </div>
      </template>
    </div>

    <div class="sticky bottom-0 bg-white border-t border-crm-border px-4 py-3">
      <div class="flex items-center gap-2">
        <input
          v-model="inputText"
          type="text"
          :placeholder="__('Ketik pesan...')"
          class="flex-1 rounded-xl border border-crm-border px-3 py-2.5 text-sm text-crm-text outline-none focus:border-crm-teal placeholder:text-crm-muted"
          :disabled="aiThinking"
          @keydown.enter="sendMessage()"
        />
        <button
          class="flex size-10 items-center justify-center rounded-xl bg-crm-teal text-white disabled:opacity-50"
          :disabled="!inputText.trim() || aiThinking || !ragReady"
          @click="sendMessage()"
        >
          <FeatherIcon name="send" class="size-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { FeatherIcon, call, toast } from 'frappe-ui'
import { timeAgo } from '@/utils'

const inputText = ref('')
const messages = ref([])
const aiThinking = ref(false)
const error = ref('')
const ragReady = ref(false)
const ragStatus = ref('checking')
const ragMessage = ref('')
const sessionId = ref(null)

const suggestions = [
  { text: __('Analisis portofolio saya'), icon: 'bar-chart-2' },
  { text: __('Rekomendasi nasabah potensial'), icon: 'users' },
  { text: __('Ringkasan aktivitas hari ini'), icon: 'activity' },
  { text: __('Target pencapaian bulan ini'), icon: 'crosshair' },
]

onMounted(async () => {
  try {
    const status = await call('crm.api.ai_agent_center.get_rag_status')
    if (status.fallback_retrieval_ready || status.chunk_count > 0) {
      ragReady.value = true
      ragStatus.value = 'ready'
      ragMessage.value = ''
    } else {
      ragStatus.value = 'indexing'
      ragMessage.value = __('AI Assistant sedang mengindeks data CRM... ini hanya sekali ~2 menit')
      toast.info(ragMessage.value)
      await call('crm.api.ai_agent_center.initialize_rag', { scope: 'crm' })
      pollRagStatus()
    }
  } catch {
    ragStatus.value = 'error'
    ragMessage.value = __('Gagal mengecek status AI')
  }
})

async function pollRagStatus() {
  const interval = setInterval(async () => {
    try {
      const status = await call('crm.api.ai_agent_center.get_rag_status')
      if (status.fallback_retrieval_ready || status.chunk_count > 0) {
        ragReady.value = true
        ragStatus.value = 'ready'
        ragMessage.value = ''
        clearInterval(interval)
        toast.success(__('AI Assistant siap digunakan'))
      } else {
        ragMessage.value = __('Mengindeks data CRM... ({0} dokumen diproses)', [status.document_count || 0])
      }
    } catch {
      clearInterval(interval)
    }
  }, 5000)
}

function parseSSEBlock(block) {
  const event = { type: 'message', data: '' }
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event.type = line.slice(6).trim()
    if (line.startsWith('data:')) event.data += line.slice(5).trim()
  }
  if (!event.data) return null
  try {
    event.payload = JSON.parse(event.data)
  } catch {
    event.payload = { message: event.data }
  }
  return event
}

async function streamAgentResponse({ content, targetMsg }) {
  const response = await fetch('/api/method/crm.api.ai_agent_center.query_agent_stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || '',
    },
    body: JSON.stringify({
      agent_key: 'general',
      message: content,
      session_id: sessionId.value,
    }),
  })
  if (!response.ok || !response.body) {
    throw new Error(await response.text())
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() || ''
    for (const block of blocks) {
      const event = parseSSEBlock(block)
      if (!event) continue
      const payload = event.payload || {}
      if (event.type === 'meta') {
        sessionId.value = payload.session_id || sessionId.value
      } else if (event.type === 'status') {
        targetMsg.statusMessage = payload.message || targetMsg.statusMessage
        scrollToBottom()
      } else if (event.type === 'thinking') {
        targetMsg.thinking = (targetMsg.thinking || '') + (payload.thinking || '')
        targetMsg.statusMessage = __('AI sedang berpikir...')
        scrollToBottom()
      } else if (event.type === 'delta') {
        targetMsg.text = (targetMsg.text || '') + (payload.delta || '')
        scrollToBottom()
      } else if (event.type === 'done') {
        targetMsg.thinkingActive = false
        targetMsg.text = payload.response || targetMsg.text
        targetMsg.structuredResponse = payload.structured_response || null
        sessionId.value = payload.session_id || sessionId.value
        scrollToBottom()
      } else if (event.type === 'error') {
        targetMsg.thinkingActive = false
        targetMsg.text = payload.message || __('Maaf, terjadi kesalahan.')
      }
    }
  }
}

async function sendMessage(text) {
  if (!text) text = inputText.value
  if (!text?.trim() || aiThinking.value) return
  const content = text.trim()
  messages.value.push({ role: 'user', text: content, time: new Date() })
  inputText.value = ''
  aiThinking.value = true
  error.value = ''

  const targetMsg = ref({
    role: 'assistant',
    text: '',
    thinking: '',
    thinkingActive: true,
    statusMessage: __('Menyiapkan analisis...'),
    structuredResponse: null,
    time: new Date(),
  })
  messages.value.push(targetMsg.value)
  scrollToBottom()

  try {
    await streamAgentResponse({ content, targetMsg: targetMsg.value })
  } catch (err) {
    error.value = err.messages?.[0] || err.message || __('Maaf, terjadi kesalahan. Silakan coba lagi.')
    targetMsg.value.text = error.value
    targetMsg.value.thinkingActive = false
  } finally {
    aiThinking.value = false
    targetMsg.value.thinkingActive = false
    nextTick(() => scrollToBottom())
  }
}

function sendSuggestion(text) {
  sendMessage(text)
}

function clearChat() {
  messages.value = []
  error.value = ''
}

function scrollToBottom() {
  nextTick(() => {
    const el = document.querySelector('.chat-messages')
    if (el) el.scrollTop = el.scrollHeight
  })
}
</script>
