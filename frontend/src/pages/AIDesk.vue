<template>
  <div class="flex h-full flex-col bg-white">
    <!-- Header -->
    <LayoutHeader>
      <template #left-header>
        <div class="flex items-center gap-3">
          <div>
            <h1 class="text-base font-semibold text-gray-900">{{ __('AI Desk') }}</h1>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Badge v-if="messageCount > 0" :label="messageCount + ' messages'" variant="subtle" theme="blue" />
          <Button
            variant="ghost"
            size="sm"
            :label="__('Clear Chat')"
            @click="clearChat"
          >
            <template #prefix>
              <FeatherIcon name="trash-2" class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <!-- Chat Area -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto px-4 py-6 scroll-smooth relative">
      <!-- Scraping Status Overlay -->
      <Transition name="fade">
        <div v-if="isScraping" class="sticky top-0 z-20 mb-4 -mt-2">
          <div class="mx-auto max-w-2xl overflow-hidden rounded-xl border border-summon-graphite bg-summon-charcoal/90 p-3 shadow-lg backdrop-blur-md">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <div class="flex h-6 w-6 animate-pulse items-center justify-center rounded-full bg-summon-graphite">
                  <FeatherIcon name="loader" class="h-3 w-3 animate-spin text-summon-blue" />
                </div>
                <span class="text-xs font-semibold text-white">
                  {{ __('Scraping Leads...') }}
                </span>
              </div>
              <span class="text-[10px] font-medium text-summon-blue bg-summon-graphite px-2 py-0.5 rounded-full">
                {{ scrapingProcessed }} / {{ scrapingTotal }}
              </span>
            </div>
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-summon-graphite">
              <div 
                class="h-full bg-gradient-to-r from-summon-blue to-summon-navy transition-all duration-500 ease-out"
                :style="{ width: `${scrapingProgress}%` }"
              />
            </div>
            <p v-if="lastScrapedLead" class="mt-2 text-[10px] text-gray-400 truncate">
              {{ __('Found:') }} <span class="font-medium text-white">{{ lastScrapedLead.name || lastScrapedLead.company }}</span>
            </p>
          </div>
        </div>
      </Transition>

      <div class="mx-auto max-w-3xl space-y-6">
        <!-- Welcome message -->
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center py-16">
          <div class="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-summon-black to-summon-charcoal shadow-xl">
            <AIDeskIcon class="h-8 w-8 text-white" />
          </div>
          <h2 class="mb-2 text-2xl font-bold text-gray-900">{{ __('Welcome to AI Desk') }}</h2>
          <p class="mb-8 max-w-md text-center text-gray-500">
            {{ __('Ask me anything about your CRM data, features, or how to get started.') }}
          </p>

          <!-- Quick action suggestions -->
          <div class="grid grid-cols-2 gap-3 w-full max-w-lg">
            <button
              v-for="suggestion in quickSuggestions"
              :key="suggestion.text"
              class="group flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-4 text-left shadow-sm transition-all duration-200 hover:border-summon-charcoal hover:shadow-md hover:-translate-y-0.5"
              @click="sendMessage(suggestion.text)"
            >
              <FeatherIcon :name="suggestion.icon" class="h-5 w-5 text-summon-charcoal" />
              <span class="text-sm font-medium text-gray-700 group-hover:text-gray-900">{{ suggestion.text }}</span>
            </button>
          </div>
        </div>

        <!-- Messages -->
        <TransitionGroup name="message">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="flex gap-3"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <!-- Bot avatar -->
            <div
              v-if="msg.role === 'assistant'"
              class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-summon-black to-summon-charcoal shadow-sm"
            >
              <AIDeskIcon class="h-4 w-4 text-white" />
            </div>

            <!-- Message bubble -->
            <div
              class="max-w-[80%] rounded-2xl px-4 py-3 shadow-sm"
              :class="
                msg.role === 'user'
                  ? 'bg-summon-charcoal text-white rounded-br-md'
                  : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md'
              "
            >
              <div v-if="msg.role === 'assistant' && msg.isTyping" class="flex gap-1 items-center h-5">
                <span class="h-1.5 w-1.5 rounded-full bg-gray-400 animate-pulse"></span>
                <span class="h-1.5 w-1.5 rounded-full bg-gray-400 animate-pulse" style="animation-delay: 150ms"></span>
                <span class="h-1.5 w-1.5 rounded-full bg-gray-400 animate-pulse" style="animation-delay: 300ms"></span>
              </div>
              <div v-else-if="msg.role === 'assistant'" class="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-table:text-sm" v-html="renderMarkdown(msg.content)" />
              <p v-else class="text-sm leading-relaxed whitespace-pre-wrap">{{ msg.content }}</p>

              <!-- Generative UI Details Card -->
              <div v-if="msg.genUI && msg.genUI.type === 'record_detail' && !msg.isTyping" class="mt-4 mb-2 border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm text-left">
                <div class="bg-gray-50 border-b border-gray-200 px-4 py-3 flex justify-between items-center">
                  <span class="font-semibold text-gray-800 text-sm flex gap-2 items-center">
                    <FeatherIcon name="file-text" class="w-4 h-4 text-summon-charcoal" />
                    {{ msg.genUI.doctype }} Details
                  </span>
                  <span v-if="msg.genUI.data.status" class="text-[10px] uppercase tracking-wider font-bold bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded-md">{{ msg.genUI.data.status }}</span>
                </div>
                <div class="p-4 grid grid-cols-2 gap-y-4 gap-x-4 text-sm bg-white">
                  <template v-for="(value, key) in msg.genUI.data" :key="key">
                    <div v-if="value !== null && value !== '' && key !== 'name'" class="flex flex-col">
                      <span class="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-1">{{ String(key).replace(/_/g, ' ') }}</span>
                      <span class="text-gray-900">{{ value }}</span>
                    </div>
                  </template>
                </div>
              </div>

              <!-- SQL query badge -->
              <div v-if="msg.query && !msg.isTyping" class="mt-3 pt-3 border-t" :class="msg.role === 'user' ? 'border-white/20' : 'border-gray-200'">
                <button
                  class="flex items-center gap-1.5 text-xs rounded-md px-2 py-1 transition-colors"
                  :class="msg.role === 'user' ? 'text-white/70 hover:text-white hover:bg-white/10' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'"
                  @click="toggleQuery(index)"
                >
                  <FeatherIcon name="code" class="h-3 w-3" />
                  {{ showQuery[index] ? __('Hide Query') : __('Show Query') }}
                </button>
                <Transition name="fade">
                  <pre v-if="showQuery[index]" class="mt-2 rounded-lg p-3 text-xs font-mono overflow-x-auto" :class="msg.role === 'user' ? 'bg-summon-charcoal text-white/80' : 'bg-gray-50 text-gray-600'">{{ msg.query }}</pre>
                </Transition>
              </div>

              <span
                v-if="!msg.isTyping"
                class="mt-1 block text-[10px]"
                :class="msg.role === 'user' ? 'text-white/50 text-right' : 'text-gray-400'"
              >
                {{ formatTime(msg.timestamp) }}
              </span>
            </div>

            <!-- User avatar -->
            <div
              v-if="msg.role === 'user'"
              class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gray-700 shadow-sm"
            >
              <FeatherIcon name="user" class="h-4 w-4 text-white" />
            </div>
          </div>
        </TransitionGroup>

        <!-- Typing indicator -->
        <div v-if="isLoading" class="flex gap-3 justify-start">
          <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-summon-black to-summon-charcoal shadow-sm">
            <AIDeskIcon class="h-4 w-4 text-white" />
          </div>
          <div class="rounded-2xl rounded-bl-md bg-white border border-gray-200 px-5 py-4 shadow-sm">
            <div class="flex gap-1.5">
              <span class="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 0ms" />
              <span class="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 150ms" />
              <span class="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style="animation-delay: 300ms" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t bg-gray-50/90 backdrop-blur-sm px-4 py-4">
      <div class="mx-auto max-w-3xl">
        <form @submit.prevent="sendMessage()" class="flex items-end gap-3">
          <div class="relative flex-1">
            <textarea
              ref="inputRef"
              v-model="inputMessage"
              :placeholder="__('Ask about your CRM data or features...')"
              class="w-full resize-none rounded-xl border border-gray-200 bg-white px-4 py-3 pr-12 text-sm text-gray-800 placeholder-gray-400 shadow-sm transition-all duration-200 focus:border-summon-charcoal focus:outline-none focus:ring-2 focus:ring-summon-charcoal/20"
              :rows="inputRows"
              @keydown="handleKeydown"
              @input="autoResize"
            />
          </div>
          <button
            type="submit"
            :disabled="!inputMessage.trim() || isLoading"
            class="flex h-11 w-11 items-center justify-center rounded-xl bg-summon-charcoal text-white shadow-sm transition-all duration-200 hover:bg-summon-graphite hover:shadow-md disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-summon-charcoal disabled:hover:shadow-sm"
          >
            <FeatherIcon name="send" class="h-4 w-4" />
          </button>
        </form>
        <p class="mt-2 text-center text-[11px] text-gray-400">
          {{ __('AI Desk answers based on your CRM data. Press Shift+Enter for new line.') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import AIDeskIcon from '@/components/Icons/AIDeskIcon.vue'
import { Badge, Button, FeatherIcon, call } from 'frappe-ui'
import { ref, computed, nextTick, onMounted, toRefs, watch } from 'vue'
import { backgroundStore } from '@/stores/background'
import { useBroadcast } from '@/composables/useBroadcast'

const chatContainer = ref(null)
const inputRef = ref(null)
const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const showQuery = ref({})

const { isScraping, scrapingProgress, scrapingTotal, scrapingProcessed, lastScrapedLead } = toRefs(backgroundStore())
const { startScraping, updateProgress, stopScraping } = backgroundStore()
const { on } = useBroadcast()

// Socket listeners for background tasks
on('lead_gen_start', (data) => {
  startScraping(data.total || 10)
})

on('lead_scraped', (data) => {
  if (data.count !== undefined) {
    updateProgress(data.count, data.lead)
  }
})

on('lead_gen_complete', () => {
  stopScraping()
})

const messageCount = computed(() => messages.value.length)

const inputRows = computed(() => {
  const lines = inputMessage.value.split('\n').length
  return Math.min(Math.max(lines, 1), 4)
})

const quickSuggestions = [
  { icon: 'bar-chart-2', text: 'How many leads do I have?' },
  { icon: 'dollar-sign', text: 'Show me recent deals' },
  { icon: 'file-text', text: 'How do leads work?' },
  { icon: 'rocket', text: 'How to get started?' },
]

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function renderMarkdown(text) {
  if (!text) return ''
  // Simple markdown rendering
  let html = text
    // Headers
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Inline code
    .replace(/`(.*?)`/g, '<code>$1</code>')
    // Unordered lists
    .replace(/^- (.*$)/gm, '<li>$1</li>')
    // Tables
    .replace(/^\|(.*)\|$/gm, (match) => {
      const cells = match.split('|').filter(c => c.trim())
      if (cells.every(c => /^[\s-]+$/.test(c))) return ''
      const tag = match.includes('---') ? 'th' : 'td'
      return '<tr>' + cells.map(c => `<${tag}>${c.trim()}</${tag}>`).join('') + '</tr>'
    })
    // Paragraphs
    .replace(/\n\n/g, '</p><p>')
    // Line breaks
    .replace(/\n/g, '<br>')

  // Wrap lists
  html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
  // Wrap tables
  html = html.replace(/(<tr>.*<\/tr>)/gs, '<table>$1</table>')
  // Wrap in paragraph
  if (!html.startsWith('<')) {
    html = '<p>' + html + '</p>'
  }

  return html
}

function toggleQuery(index) {
  showQuery.value[index] = !showQuery.value[index]
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function autoResize() {
  // Auto-resize is handled by computed inputRows
}

async function simulateTyping(messageIndex, fullText, callback) {
  const msg = messages.value[messageIndex]
  msg.isTyping = false
  msg.content = ''
  
  // Faster typing speed (chunk by 2-4 chars)
  const chunkSize = 3
  let i = 0
  
  const typeChar = () => {
    if (i < fullText.length) {
      msg.content += fullText.substring(i, i + chunkSize)
      i += chunkSize
      scrollToBottom()
      // Very fast timeout 5-15ms
      setTimeout(typeChar, Math.random() * 10 + 5)
    } else {
      msg.content = fullText
      saveHistory()
      if (callback) callback()
    }
  }
  
  typeChar()
}

async function sendMessage(text) {
  const msg = text || inputMessage.value.trim()
  if (!msg) return

  // Add user message
  messages.value.push({
    role: 'user',
    content: msg,
    timestamp: new Date().toISOString(),
  })
  saveHistory()

  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const conversationHistory = messages.value
      .filter(m => !m.isTyping)
      .slice(-10)
      .map(m => ({ role: m.role, content: m.content }))

    const response = await call('crm.api.ai_desk.query_ai_desk', {
      message: msg,
      conversation_history: JSON.stringify(conversationHistory),
    })

    let replyText = response.response || 'I could not process your request. Please try again.'
    let genUI = null
    
    const genUIMatch = replyText.match(/___GENUI_RECORD_DETAIL___\s*(\{[\s\S]*\})/)
    if (genUIMatch) {
      try {
        genUI = JSON.parse(genUIMatch[1])
        replyText = replyText.replace(genUIMatch[0], '').trim()
      } catch (e) {
        console.error('Failed to parse GenUI payload', e)
      }
    }

    const newIndex = messages.value.push({
      role: 'assistant',
      content: '', // Start empty
      data: response.data,
      query: response.query,
      genUI: genUI,
      timestamp: new Date().toISOString(),
      isTyping: true, // Show typing bubbles briefly before text starts
    }) - 1
    
    isLoading.value = false
    
    // Simulate thinking delay, then type
    setTimeout(() => {
      simulateTyping(newIndex, replyText)
    }, 400)
    
  } catch (error) {
    isLoading.value = false
    messages.value.push({
      role: 'assistant',
      content: '❌ Sorry, there was an error processing your request. Please try again.',
      timestamp: new Date().toISOString(),
    })
    saveHistory()
    console.error('AI Desk error:', error)
    scrollToBottom()
  }
}

function clearChat() {
  messages.value = []
  showQuery.value = {}
  localStorage.removeItem('ai_desk_history')
}

function saveHistory() {
  localStorage.setItem('ai_desk_history', JSON.stringify(messages.value))
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

onMounted(() => {
  inputRef.value?.focus()
  try {
    const saved = localStorage.getItem('ai_desk_history')
    if (saved) {
      messages.value = JSON.parse(saved)
      scrollToBottom()
    }
  } catch (e) {
    console.error('Failed to load chat history:', e)
  }
})
</script>

<style scoped>
.message-enter-active {
  transition: all 0.3s ease;
}
.message-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.message-leave-active {
  transition: all 0.2s ease;
}
.message-leave-to {
  opacity: 0;
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  max-height: 0;
}
.fade-enter-to,
.fade-leave-from {
  max-height: 200px;
}

/* Custom scrollbar for chat */
:deep(.prose table) {
  @apply w-full border-collapse text-sm;
}
:deep(.prose th),
:deep(.prose td) {
  @apply border border-gray-200 px-3 py-2 text-left;
}
:deep(.prose th) {
  @apply bg-gray-50 font-medium text-gray-700;
}
:deep(.prose tr:hover td) {
  @apply bg-gray-50;
}
</style>
