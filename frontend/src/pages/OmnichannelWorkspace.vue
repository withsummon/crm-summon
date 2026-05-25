<template>
  <div class="omni-shell">
    <aside class="omni-nav">
      <div class="omni-brand">
        <div class="omni-brand-icon">
          <FeatherIcon name="message-square" class="h-5 w-5" />
        </div>
        <div>
          <h1>{{ __('Omnichannel') }}</h1>
          <p>{{ __('Unified inbox') }}</p>
        </div>
      </div>

      <button
        v-for="item in channelTabs"
        :key="item.key"
        :class="['omni-channel', selectedChannel === item.key ? 'active' : '']"
        @click="selectChannel(item.key)"
      >
        <span class="omni-channel-main">
          <FeatherIcon :name="item.icon" class="h-4 w-4" />
          {{ item.label }}
        </span>
        <span class="omni-count">{{ counts[item.countKey] || 0 }}</span>
      </button>

      <div class="omni-side-section">
        <div class="omni-side-title">{{ __('Bulk Actions') }}</div>
        <button class="omni-side-action" :disabled="bulkLoading" @click="bulkAction('tag')">
          <FeatherIcon name="tag" class="h-4 w-4" />
          {{ __('Tag') }}
        </button>
        <button class="omni-side-action" :disabled="bulkLoading" @click="bulkAction('assign')">
          <FeatherIcon name="user-check" class="h-4 w-4" />
          {{ __('Assign to me') }}
        </button>
        <button class="omni-side-action" :disabled="bulkLoading" @click="bulkAction('close')">
          <FeatherIcon name="check-circle" class="h-4 w-4" />
          {{ __('Close') }}
        </button>
        <button class="omni-side-action" :disabled="bulkLoading" @click="bulkAction('archive')">
          <FeatherIcon name="archive" class="h-4 w-4" />
          {{ __('Archive') }}
        </button>
      </div>

      <div class="omni-side-section" style="margin-top: auto; border-top: 1px solid #e6ecef; padding-top: 12px;">
        <div class="omni-side-title">{{ __('Tools') }}</div>
        <button class="omni-side-action" @click="openWhatsAppWeb">
          <FeatherIcon name="message-circle" class="h-4 w-4" />
          {{ __('WhatsApp Web') }}
        </button>
      </div>
    </aside>

    <section class="omni-list-pane">
      <div class="omni-list-header">
        <div>
          <h2>{{ activeTabLabel }}</h2>
          <p>{{ __('Search, triage, and route real customer conversations') }}</p>
        </div>
        <button class="omni-refresh" :aria-label="__('Refresh')" @click="loadConversations">
          <FeatherIcon name="refresh-cw" class="h-4 w-4" />
        </button>
      </div>

      <div class="omni-toolbar">
        <div class="omni-search">
          <FeatherIcon name="search" class="h-4 w-4" />
          <input v-model="search" :placeholder="__('Search conversations')" @keyup.enter="loadConversations" />
        </div>
        <select v-model="sort" @change="loadConversations">
          <option value="recent">{{ __('Recent') }}</option>
          <option value="unread">{{ __('Unread') }}</option>
          <option value="priority">{{ __('Priority') }}</option>
        </select>
        <button v-if="selectedChannel !== 'All'" class="omni-new-chat" @click="showNewChat = true">
          <FeatherIcon name="edit" class="h-4 w-4" />
          {{ __('New Chat') }}
        </button>
      </div>

      <!-- New Chat Dialog -->
      <Dialog v-model="showNewChat" :options="{ title: dialogTitle }">
        <template #body-content>
          <!-- For In-App Chat (Existing Search Users) -->
          <div v-if="selectedChannel === 'In-App'" class="space-y-3 pt-3">
            <div class="relative">
              <FeatherIcon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input v-model="userSearch" :placeholder="__('Search users...')" @keyup="searchUsers" class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm focus:outline-none focus:border-teal-500" />
            </div>
            <div v-if="userSearchLoading" class="flex justify-center py-4">
              <div class="h-5 w-5 animate-spin rounded-full border-2 border-teal-500 border-t-transparent" />
            </div>
            <div v-else-if="!userResults.length && userSearch" class="text-center py-4 text-sm text-slate-400">
              {{ __('No users found') }}
            </div>
            <div v-else class="space-y-1 max-h-60 overflow-y-auto">
              <button v-for="u in userResults" :key="u.name" class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-slate-50 text-left" @click="startChat(u)">
                <div v-if="u.user_image" class="h-8 w-8 rounded-full bg-cover bg-center" :style="{ backgroundImage: `url(${u.user_image})` }" />
                <div v-else class="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-700">
                  {{ (u.full_name || u.name).charAt(0).toUpperCase() }}
                </div>
                <div class="min-w-0 flex-1">
                  <div class="font-medium text-slate-800 truncate">{{ u.full_name || u.name }}</div>
                  <div class="text-xs text-slate-400 truncate">{{ u.email }}</div>
                </div>
              </button>
            </div>
            <div v-if="!userSearch" class="text-center py-4 text-sm text-slate-400">
              {{ __('Type to search users') }}
            </div>
          </div>

          <!-- For External Channels (Email, SMS, WhatsApp, Voice) -->
          <div v-else class="space-y-4 pt-3">
            <!-- Customer Search Input -->
            <div class="relative">
              <FeatherIcon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input v-model="customerSearch" :placeholder="__('Search customers...')" @keyup="searchCustomers" class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm focus:outline-none focus:border-teal-500" />
            </div>
            
            <div v-if="customerSearchLoading" class="flex justify-center py-4">
              <div class="h-5 w-5 animate-spin rounded-full border-2 border-teal-500 border-t-transparent" />
            </div>
            
            <div v-else-if="!customerResults.length && customerSearch" class="text-center py-4 text-sm text-slate-400">
              {{ __('No customers found') }}
            </div>
            
            <div v-else-if="customerResults.length && !selectedNewChatCustomer" class="space-y-1 max-h-40 overflow-y-auto border border-slate-100 rounded-lg p-1 bg-slate-50/50">
              <button v-for="c in customerResults" :key="c.name" class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm hover:bg-white text-left transition-colors border border-transparent hover:border-slate-100" @click="selectNewChatCustomer(c)">
                <div class="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-700 shrink-0">
                  {{ (c.customer_name || c.name).charAt(0).toUpperCase() }}
                </div>
                <div class="min-w-0 flex-1">
                  <div class="font-medium text-slate-800 truncate">{{ c.customer_name || c.name }}</div>
                  <div class="text-xs text-slate-400 truncate">
                    <span v-if="selectedChannel === 'Email'">{{ c.email_id || __('No email') }}</span>
                    <span v-else>{{ c.mobile_no || __('No phone') }}</span>
                  </div>
                </div>
              </button>
            </div>

            <!-- Customer Selected form composition -->
            <div v-if="selectedNewChatCustomer" class="space-y-3 p-3 bg-slate-50/50 border border-slate-100 rounded-xl transition-all duration-200">
              <div class="flex items-center justify-between border-b border-slate-100 pb-2">
                <div class="flex items-center gap-2">
                  <div class="h-2 w-2 rounded-full bg-teal-500" />
                  <span class="text-xs font-semibold text-slate-700">{{ selectedNewChatCustomer.customer_name }}</span>
                </div>
                <button @click="selectedNewChatCustomer = null" class="text-xs text-slate-400 hover:text-teal-600 font-medium">
                  {{ __('Change') }}
                </button>
              </div>

              <!-- Recipient address or phone -->
              <div class="space-y-1">
                <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                  <span v-if="selectedChannel === 'Email'">{{ __('To Email') }}</span>
                  <span v-else>{{ __('To Number') }}</span>
                </label>
                <input v-model="newChatRecipient" class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:border-teal-500" :placeholder="selectedChannel === 'Email' ? 'email@example.com' : '+628...'" />
              </div>

              <!-- Subject for Email -->
              <div v-if="selectedChannel === 'Email'" class="space-y-1">
                <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">{{ __('Subject') }}</label>
                <input v-model="newChatSubject" class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:border-teal-500" :placeholder="__('Email subject...')" />
              </div>

              <!-- First Message -->
              <div class="space-y-1">
                <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">{{ __('First Message') }}</label>
                <textarea v-model="newChatFirstMessage" rows="3" class="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:border-teal-500 resize-none" :placeholder="__('Type your first message...')" />
              </div>

              <!-- Action button inside Dialog body or actions slot -->
              <div class="pt-2 flex justify-end">
                <button
                  class="flex items-center gap-2 rounded-lg bg-teal-600 px-4 py-2 text-sm font-semibold text-white hover:bg-teal-700 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-offset-1"
                  :disabled="newChatLoading || !newChatRecipient || !newChatFirstMessage"
                  @click="startExternalChat"
                >
                  <FeatherIcon v-if="newChatLoading" name="loader" class="h-4 w-4 animate-spin" />
                  <FeatherIcon v-else name="send" class="h-4 w-4" />
                  {{ __('Start Conversation') }}
                </button>
              </div>
            </div>
            
            <div v-if="!customerSearch && !selectedNewChatCustomer" class="text-center py-4 text-sm text-slate-400">
              {{ __('Type to search customers') }}
            </div>
          </div>
        </template>
      </Dialog>

      <!-- Tag Dialog -->
      <Dialog v-model="showTagDialog" :options="{ title: __('Assign / Tag Conversations') }">
        <template #body-content>
          <div class="space-y-4 pt-3">
            <div>
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">{{ __('Assign to User') }}</label>
              <div class="relative mt-1">
                <FeatherIcon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input v-model="tagUserSearch" :placeholder="__('Search users...')" @keyup="searchTagUsers" class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm focus:outline-none focus:border-teal-500" />
              </div>
              <div v-if="tagUserSearchLoading" class="flex justify-center py-3">
                <div class="h-5 w-5 animate-spin rounded-full border-2 border-teal-500 border-t-transparent" />
              </div>
              <div v-else-if="tagUserResults.length" class="mt-2 space-y-1 max-h-48 overflow-y-auto border border-slate-100 rounded-lg">
                <button v-for="u in tagUserResults" :key="u.name" class="flex w-full items-center gap-3 px-3 py-2 text-sm hover:bg-slate-50 text-left border-b border-slate-50 last:border-0" @click="assignToUser(u)">
                  <div v-if="u.user_image" class="h-7 w-7 rounded-full bg-cover bg-center shrink-0" :style="{ backgroundImage: `url(${u.user_image})` }" />
                  <div v-else class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-teal-100 text-xs font-bold text-teal-700">
                    {{ (u.full_name || u.name).charAt(0).toUpperCase() }}
                  </div>
                  <div class="min-w-0 flex-1">
                    <div class="font-medium text-slate-800 truncate text-xs">{{ u.full_name || u.name }}</div>
                    <div class="text-xs text-slate-400 truncate">{{ u.email }}</div>
                  </div>
                  <FeatherIcon name="user-check" class="h-4 w-4 text-teal-500 shrink-0" />
                </button>
              </div>
              <div v-else-if="tagUserSearch && !tagUserSearchLoading" class="text-center py-3 text-sm text-slate-400">
                {{ __('No users found') }}
              </div>
            </div>
            <div class="border-t border-slate-100 pt-3">
              <label class="text-xs font-semibold text-slate-500 uppercase tracking-wide">{{ __('Add Text Tag') }}</label>
              <div class="flex gap-2 mt-1">
                <input v-model="tagName" :placeholder="__('Tag name...')" class="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:border-teal-500" @keydown.enter="confirmTag" />
                <Button variant="solid" :label="__('Add')" :disabled="!tagName.trim()" :loading="bulkLoading" @click="confirmTag" />
              </div>
            </div>
          </div>
        </template>
        <template #actions>
          <Button variant="outline" :label="__('Close')" @click="showTagDialog = false" />
        </template>
      </Dialog>

      <div v-if="loading" class="omni-state">{{ __('Loading conversations...') }}</div>
      <div v-else-if="!conversations.length" class="omni-empty">
        <FeatherIcon name="inbox" class="h-8 w-8" />
        <strong v-if="selectedChannel === 'In-App'">{{ __('Belum ada percakapan.') }}</strong>
        <strong v-else>{{ __('Belum ada percakapan.') }}</strong>
        <span v-if="selectedChannel === 'In-App'">{{ __('Klik "New Chat" untuk memulai percakapan dengan pengguna lain.') }}</span>
        <span v-else>{{ __('Hubungkan channel atau tunggu inbound message.') }}</span>
      </div>
      <div v-else class="omni-list">
        <label v-for="row in conversations" :key="row.name" :class="['omni-row', selectedConversationId === row.name ? 'active' : '']">
          <input v-model="selectedIds" type="checkbox" :value="row.name" @click.stop />
          <button class="omni-row-body" @click.prevent="openConversation(row.name)">
            <span class="omni-row-top">
              <span class="omni-row-title">{{ row.subject }}</span>
              <span :class="['omni-channel-pill', channelTone(row.channel)]">{{ row.channel }}</span>
            </span>
            <span class="omni-row-meta">
              {{ row.customer_name || row.customer || row.reference_name || __('Unknown Customer') }}
            </span>
            <span class="omni-row-preview">{{ row.last_message_preview || __('No message yet') }}</span>
            <span class="omni-row-bottom">
              <span :class="['omni-sla', row.sla_status === 'Breached' ? 'breach' : '']">{{ row.sla_status || 'Not Started' }}</span>
              <span v-if="row.unread_count" class="omni-unread">{{ row.unread_count }}</span>
            </span>
          </button>
        </label>
      </div>
    </section>

    <section class="omni-detail-pane">
      <div v-if="!selectedConversationId" class="omni-detail-empty">
        <FeatherIcon name="message-circle" class="h-10 w-10" />
        <h2>{{ __('Select a conversation') }}</h2>
        <p>{{ __('Open a real WhatsApp, email, SMS, in-app, or voice conversation from the inbox.') }}</p>
      </div>

      <template v-else>
        <div class="omni-detail-header">
          <div>
            <div class="omni-detail-eyebrow">{{ detail?.conversation?.channel }}</div>
            <h2>{{ detail?.conversation?.subject }}</h2>
            <p>{{ detail?.conversation?.customer_name || detail?.conversation?.customer || detail?.conversation?.reference_name }}</p>
          </div>
          <div class="omni-header-actions">
            <span :class="['omni-provider', providerReady ? 'ready' : 'blocked']">
              {{ detail?.provider_status?.status || 'Provider Not Configured' }}
            </span>
            <button class="omni-icon-button" :aria-label="__('Route')" @click="evaluateRouting">
              <FeatherIcon name="shuffle" class="h-4 w-4" />
            </button>
            <button class="omni-icon-button" :aria-label="__('Archive')" @click="archiveSelected">
              <FeatherIcon name="archive" class="h-4 w-4" />
            </button>
          </div>
        </div>

        <div class="omni-detail-grid">
          <main class="omni-thread">
            <div class="omni-sla-bar">
              <span>{{ __('SLA') }}: {{ detail?.sla?.status || '-' }}</span>
              <span>{{ __('Due') }}: {{ formatDate(detail?.sla?.first_response_due_on) }}</span>
              <span v-if="detail?.conversation?.reply_window_ends_on">{{ __('Reply window') }}: {{ formatDate(detail.conversation.reply_window_ends_on) }}</span>
            </div>

            <div class="omni-messages">
              <article
                v-for="message in detail?.messages || []"
                :key="message.name"
                :class="['omni-message', message.direction === 'Outbound' ? 'outbound' : '', message.direction === 'Internal' ? 'internal' : '']"
              >
                <div class="omni-message-meta">
                  <span>{{ message.direction }}</span>
                  <span>{{ message.status }}</span>
                  <span>{{ formatDate(message.sent_or_received_on) }}</span>
                </div>
                <div class="omni-message-body" v-html="message.content || message.attachment || message.message_type" />
                <a v-if="message.attachment" class="omni-attachment" :href="message.attachment" target="_blank" rel="noreferrer">
                  <FeatherIcon name="paperclip" class="h-4 w-4" />
                  {{ __('Attachment') }}
                </a>
              </article>
            </div>

            <div class="omni-composer">
              <div v-if="!providerReady" class="omni-provider-warning">
                {{ __('Provider Not Configured. Sending is disabled for real outbound delivery; API will store the blocked attempt with provider status.') }}
              </div>
              <div class="omni-template-row">
                <select v-model="selectedTemplate">
                  <option value="">{{ __('No template') }}</option>
                  <option v-for="template in templates" :key="template.name" :value="template.name">
                    {{ template.template_name || template.name }}
                  </option>
                </select>
                <button class="omni-secondary" :disabled="suggestionsLoading" @click="generateSuggestions">
                  <FeatherIcon v-if="suggestionsLoading" name="loader" class="h-4 w-4 animate-spin" />
                  <FeatherIcon v-else name="sparkles" class="h-4 w-4" />
                  {{ __('AI Suggestions') }}
                </button>
                <button class="omni-secondary" @click="showInternalNote = !showInternalNote">
                  <FeatherIcon name="lock" class="h-4 w-4" />
                  {{ __('Internal Note') }}
                </button>
              </div>
              <div v-if="suggestions.length && !suggestionsLoading" class="omni-suggestions">
                <button v-for="item in suggestions" :key="item" @click="composer = item">{{ item }}</button>
              </div>
              <div v-if="suggestionsLoading" class="omni-suggestions-loading">{{ __('Generating suggestions...') }}</div>
              <textarea v-model="composer" :placeholder="showInternalNote ? __('Write an internal note') : __('Type a reply')" />
              <div class="omni-composer-actions">
                <FileUploader
                  :upload-args="{ doctype: 'CRM Omnichannel Conversation', docname: selectedConversationId, private: true }"
                  @success="onAttachmentUploaded"
                >
                  <template #default="{ openFileSelector, uploading }">
                    <button class="omni-secondary" :disabled="uploading" @click="openFileSelector">
                      <FeatherIcon name="paperclip" class="h-4 w-4" />
                      {{ uploading ? __('Uploading...') : __('Attach') }}
                    </button>
                  </template>
                </FileUploader>
                <button class="omni-primary" :disabled="sending || (!composer && !selectedTemplate)" @click="sendReply">
                  <FeatherIcon name="send" class="h-4 w-4" />
                  {{ sending ? __('Sending...') : __('Send') }}
                </button>
              </div>
            </div>
          </main>

          <aside class="omni-context">
            <section class="omni-context-section">
              <h3>{{ __('Customer Context') }}</h3>
              <div class="omni-context-name">{{ customerName }}</div>
              <div class="omni-context-grid">
                <span>{{ __('Risk') }}</span>
                <strong>{{ contextSummary.risk_grade || '-' }}</strong>
                <span>{{ __('Facilities') }}</span>
                <strong>{{ contextSummary.active_facilities || 0 }}</strong>
                <span>{{ __('Outstanding') }}</span>
                <strong>{{ formatCurrency(contextSummary.total_outstanding) }}</strong>
                <span>{{ __('KYC') }}</span>
                <strong>{{ contextSummary.kyc_status || '-' }}</strong>
              </div>
              <button v-if="detail?.conversation?.customer" class="omni-secondary full" @click="openCustomer360">
                <FeatherIcon name="external-link" class="h-4 w-4" />
                {{ __('Open Full Profile') }}
              </button>
            </section>

            <section class="omni-context-section">
              <h3>{{ __('Routing') }}</h3>
              <div class="omni-context-grid">
                <span>{{ __('Assigned') }}</span>
                <strong>{{ detail?.routing?.assigned_to || '-' }}</strong>
                <span>{{ __('Team') }}</span>
                <strong>{{ detail?.routing?.owner_team || '-' }}</strong>
              </div>
              <button class="omni-secondary full" @click="assignToMe">{{ __('Assign to me') }}</button>
            </section>

            <section class="omni-context-section">
              <h3>{{ __('Internal Notes') }}</h3>
              <div v-if="!(detail?.notes || []).length" class="omni-muted">{{ __('No internal notes') }}</div>
              <div v-for="note in detail?.notes || []" :key="note.name" class="omni-note" v-html="note.note" />
            </section>
          </aside>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup>
import { call, Dialog, FeatherIcon, FileUploader, toast } from 'frappe-ui'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const channelTabs = [
  { key: 'All', label: __('All'), icon: 'inbox', countKey: 'all' },
  { key: 'WhatsApp', label: 'WhatsApp', icon: 'message-circle', countKey: 'whatsapp' },
  { key: 'Email', label: 'Email', icon: 'mail', countKey: 'email' },
  { key: 'SMS', label: 'SMS', icon: 'smartphone', countKey: 'sms' },
  { key: 'In-App', label: __('In-App'), icon: 'message-square', countKey: 'in_app' },
  { key: 'Voice', label: __('Voice'), icon: 'phone', countKey: 'voice' },
]

const selectedChannel = ref('All')
const search = ref('')
const sort = ref('recent')
const loading = ref(false)
const sending = ref(false)
const conversations = ref([])
const counts = ref({ all: 0, whatsapp: 0, email: 0, sms: 0, in_app: 0, voice: 0 })
const selectedIds = ref([])
const selectedConversationId = ref('')
const bulkLoading = ref(false)
const detail = ref(null)
const templates = ref([])
const selectedTemplate = ref('')
const composer = ref('')
const suggestions = ref([])
const showInternalNote = ref(false)
const suggestionsLoading = ref(false)

// New In-App Chat
const showNewChat = ref(false)
const userSearch = ref('')
const userSearchLoading = ref(false)
const userResults = ref([])
let userSearchTimer = null

// New External Customer Chat
const customerSearch = ref('')
const customerSearchLoading = ref(false)
const customerResults = ref([])
const selectedNewChatCustomer = ref(null)
const newChatRecipient = ref('')
const newChatSubject = ref('')
const newChatFirstMessage = ref('')
const newChatLoading = ref(false)
let customerSearchTimer = null

// Tag dialog
const showTagDialog = ref(false)
const tagName = ref('')
const tagUserSearch = ref('')
const tagUserSearchLoading = ref(false)
const tagUserResults = ref([])
let tagUserSearchTimer = null

const dialogTitle = computed(() => {
  if (selectedChannel.value === 'In-App') {
    return __('Start In-App Chat')
  }
  return __(`Start ${selectedChannel.value} Conversation`)
})

const activeTabLabel = computed(() => channelTabs.find((item) => item.key === selectedChannel.value)?.label || __('All'))
const providerReady = computed(() => detail.value?.provider_status?.status === 'Active')
const contextSummary = computed(() => detail.value?.customer_context?.summary || detail.value?.customer_context || {})
const customerName = computed(() => {
  return (
    detail.value?.customer_context?.customer?.customer_name ||
    detail.value?.conversation?.customer_name ||
    detail.value?.conversation?.customer ||
    __('Unknown Customer')
  )
})

onMounted(loadConversations)

watch(selectedConversationId, async (name) => {
  if (!name) return
  await loadConversation(name)
})

watch(showNewChat, (val) => {
  if (!val) {
    userSearch.value = ''
    userResults.value = []
    customerSearch.value = ''
    customerResults.value = []
    selectedNewChatCustomer.value = null
    newChatRecipient.value = ''
    newChatSubject.value = ''
    newChatFirstMessage.value = ''
  }
})

async function loadConversations() {
  loading.value = true
  try {
    const response = await call('crm.api.omnichannel.get_conversations', {
      channel: selectedChannel.value,
      search: search.value,
      sort: sort.value,
    })
    conversations.value = response?.rows || []
    counts.value = response?.counts || counts.value
    if (!selectedConversationId.value && conversations.value.length) {
      selectedConversationId.value = conversations.value[0].name
    }
  } finally {
    loading.value = false
  }
}

async function loadConversation(name) {
  detail.value = await call('crm.api.omnichannel.get_conversation', { conversation_id: name })
  templates.value = await call('crm.api.omnichannel.get_templates', {
    channel: detail.value?.conversation?.channel,
  })
}

function selectChannel(channel) {
  selectedChannel.value = channel
  selectedConversationId.value = ''
  detail.value = null
  loadConversations()
}

function openConversation(name) {
  selectedConversationId.value = name
}

async function sendReply() {
  if (!selectedConversationId.value) return
  sending.value = true
  try {
    const response = await call('crm.api.omnichannel.send_message', {
      conversation_id: selectedConversationId.value,
      content: composer.value,
      template: selectedTemplate.value || null,
      metadata: { internal_note: showInternalNote.value, note: showInternalNote.value ? composer.value : null },
    })
    if (response?.status === 'Provider Not Configured') {
      toast.error(__('Provider Not Configured'))
    } else if (response?.status === 'Failed') {
      toast.error(response.failed_reason || __('Message failed'))
    } else {
      toast.success(__('Message queued'))
    }
    composer.value = ''
    selectedTemplate.value = ''
    await loadConversation(selectedConversationId.value)
    await loadConversations()
  } finally {
    sending.value = false
  }
}

async function onAttachmentUploaded(file) {
  const fileUrl = file?.file_url || file?.url
  if (!fileUrl) return
  await call('crm.api.omnichannel.upload_message_attachment', {
    conversation_id: selectedConversationId.value,
    file_url: fileUrl,
    file_name: file?.file_name || file?.name,
  })
  await loadConversation(selectedConversationId.value)
}

async function bulkAction(action) {
  let ids = selectedIds.value
  if (!ids.length && selectedConversationId.value) ids = [selectedConversationId.value]
  if (!ids.length) { toast.error(__('Select conversations first')); return }
  if (action === 'tag') { tagName.value = ''; showTagDialog.value = true; return }
  bulkLoading.value = true
  try {
    let value = null
    if (action === 'assign') value = window.frappe?.session?.user
    const result = await call('crm.api.omnichannel.bulk_update_conversations', {
      conversation_ids: ids,
      action,
      value,
    })
    toast.success(result?.updated?.length ? `${result.updated.length} ${__('updated')}` : __('Action completed'))
    selectedIds.value = []
    await loadConversations()
    if (selectedConversationId.value) await loadConversation(selectedConversationId.value)
  } catch (err) {
    toast.error(err?.messages?.[0] || err.message || __('Bulk action failed'))
  } finally {
    bulkLoading.value = false
  }
}

async function confirmTag() {
  if (!tagName.value.trim()) return
  showTagDialog.value = false
  let ids = selectedIds.value
  if (!ids.length && selectedConversationId.value) ids = [selectedConversationId.value]
  bulkLoading.value = true
  try {
    const result = await call('crm.api.omnichannel.bulk_update_conversations', {
      conversation_ids: ids,
      action: 'tag',
      value: tagName.value.trim(),
    })
    toast.success(result?.updated?.length ? `${result.updated.length} ${__('updated')}` : __('Action completed'))
    selectedIds.value = []
    tagName.value = ''
    await loadConversations()
    if (selectedConversationId.value) await loadConversation(selectedConversationId.value)
  } catch (err) {
    toast.error(err?.messages?.[0] || err.message || __('Tag action failed'))
  } finally {
    bulkLoading.value = false
  }
}

async function assignToMe() {
  selectedIds.value = [selectedConversationId.value]
  await bulkAction('assign')
}

async function archiveSelected() {
  selectedIds.value = [selectedConversationId.value]
  await bulkAction('archive')
  selectedConversationId.value = ''
  detail.value = null
}

function openWhatsAppWeb() {
  window.open('https://web.whatsapp.com', '_blank', 'noopener,noreferrer')
}

async function searchUsers() {
  clearTimeout(userSearchTimer)
  if (!userSearch.value.trim()) { userResults.value = []; return }
  userSearchTimer = setTimeout(async () => {
    userSearchLoading.value = true
    try {
      userResults.value = await call('crm.api.omnichannel.search_users', { query: userSearch.value })
    } catch { userResults.value = []
    } finally { userSearchLoading.value = false }
  }, 300)
}

async function startChat(user) {
  showNewChat.value = false
  userSearch.value = ''
  userResults.value = []
  try {
    const res = await call('crm.api.omnichannel.start_inapp_chat', {
      user_email: user.name,
      subject: `Chat with ${user.full_name || user.name}`,
    })
    if (res.conversation_id) {
      selectedChannel.value = 'In-App'
      await loadConversations()
      selectedConversationId.value = res.conversation_id
      await loadConversation(res.conversation_id)
      toast.success(__('Chat started'))
    }
  } catch (err) {
    toast.error(err?.messages?.[0] || err.message || __('Failed to start chat'))
  }
}

async function searchTagUsers() {
  clearTimeout(tagUserSearchTimer)
  if (!tagUserSearch.value.trim()) { tagUserResults.value = []; return }
  tagUserSearchTimer = setTimeout(async () => {
    tagUserSearchLoading.value = true
    try {
      tagUserResults.value = await call('crm.api.omnichannel.search_users', { query: tagUserSearch.value })
    } catch { tagUserResults.value = []
    } finally { tagUserSearchLoading.value = false }
  }, 300)
}

async function assignToUser(user) {
  let ids = selectedIds.value
  if (!ids.length && selectedConversationId.value) ids = [selectedConversationId.value]
  bulkLoading.value = true
  try {
    const result = await call('crm.api.omnichannel.bulk_update_conversations', {
      conversation_ids: ids,
      action: 'assign',
      value: user.name,
    })
    toast.success(result?.updated?.length ? `${result.updated.length} ${__('assigned to')} ${user.full_name || user.name}` : __('Action completed'))
    selectedIds.value = []
    tagUserSearch.value = ''
    tagUserResults.value = []
    showTagDialog.value = false
    await loadConversations()
    if (selectedConversationId.value) await loadConversation(selectedConversationId.value)
  } catch (err) {
    toast.error(err?.messages?.[0] || err.message || __('Assign failed'))
  } finally {
    bulkLoading.value = false
  }
}

async function evaluateRouting() {
  const response = await call('crm.api.omnichannel.evaluate_routing', {
    conversation_id: selectedConversationId.value,
  })
  toast.success(response?.status || __('Routing evaluated'))
  await loadConversation(selectedConversationId.value)
}

async function generateSuggestions() {
  if (suggestionsLoading.value) return
  suggestionsLoading.value = true
  suggestions.value = []
  try {
    const response = await call('crm.api.omnichannel.generate_reply_suggestions', {
      conversation_id: selectedConversationId.value,
      tone: 'Formal',
    })
    suggestions.value = response?.suggestions || []
    if (response?.status === 'Provider Not Configured') {
      toast.error(__('AI Provider Not Configured'))
    } else if (response?.status === 'Fallback') {
      toast.success(__('Template suggestions ready'))
    }
  } catch (err) {
    toast.error(err?.messages?.[0] || err.message || __('Failed to generate suggestions'))
  } finally {
    suggestionsLoading.value = false
  }
}

function openCustomer360() {
  router.push({
    name: 'Customer 360 Detail',
    params: { customer: detail.value.conversation.customer },
  })
}

function channelTone(channel) {
  return {
    WhatsApp: 'green',
    Email: 'blue',
    SMS: 'orange',
    'In-App': 'teal',
    Voice: 'slate',
  }[channel] || 'slate'
}

function formatDate(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

function formatCurrency(value) {
  const number = Number(value || 0)
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(number)
}

async function searchCustomers() {
  clearTimeout(customerSearchTimer)
  if (!customerSearch.value.trim()) { customerResults.value = []; return }
  customerSearchTimer = setTimeout(async () => {
    customerSearchLoading.value = true
    try {
      customerResults.value = await call('crm.api.omnichannel.search_customers', { query: customerSearch.value })
    } catch { 
      customerResults.value = []
    } finally { 
      customerSearchLoading.value = false 
    }
  }, 300)
}

function selectNewChatCustomer(customer) {
  selectedNewChatCustomer.value = customer
  if (selectedChannel.value === 'Email') {
    newChatRecipient.value = customer.email_id || ''
  } else {
    newChatRecipient.value = customer.mobile_no || ''
  }
  newChatSubject.value = ''
  newChatFirstMessage.value = ''
}

async function startExternalChat() {
  if (!selectedNewChatCustomer.value || !newChatRecipient.value || !newChatFirstMessage.value) return
  newChatLoading.value = true
  try {
    const res = await call('crm.api.omnichannel.start_external_conversation', {
      channel: selectedChannel.value,
      customer: selectedNewChatCustomer.value.name,
      recipient: newChatRecipient.value,
      subject: newChatSubject.value || `${selectedChannel.value} Conversation with ${selectedNewChatCustomer.value.customer_name}`,
      content: newChatFirstMessage.value,
    })
    
    if (res.conversation_id) {
      showNewChat.value = false
      await loadConversations()
      selectedConversationId.value = res.conversation_id
      await loadConversation(res.conversation_id)
      toast.success(__('Conversation started successfully'))
    }
  } catch (err) {
    toast.error(err?.messages?.[0] || err.message || __('Failed to start conversation'))
  } finally {
    newChatLoading.value = false
  }
}
</script>

<style scoped>
.omni-shell {
  display: grid;
  grid-template-columns: 252px minmax(320px, 420px) minmax(0, 1fr);
  height: 100%;
  min-height: calc(100vh - 48px);
  background: #f7fafc;
  color: #1e293b;
}

.omni-nav,
.omni-list-pane,
.omni-detail-pane {
  min-height: 0;
  border-right: 1px solid #dbe3ea;
  background: #ffffff;
}

.omni-nav {
  padding: 16px;
}

.omni-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.omni-brand-icon {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 8px;
  background: #0f766e;
  color: #ffffff;
}

.omni-brand h1,
.omni-list-header h2,
.omni-detail-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
}

.omni-brand p,
.omni-list-header p,
.omni-detail-header p {
  margin: 2px 0 0;
  color: #64748b;
  font-size: 12px;
}

.omni-channel,
.omni-side-action,
.omni-refresh,
.omni-icon-button,
.omni-secondary,
.omni-primary {
  border: 1px solid transparent;
  border-radius: 8px;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.omni-channel {
  display: flex;
  justify-content: space-between;
  width: 100%;
  padding: 10px;
  color: #475569;
}

.omni-channel.active {
  border-color: #99f6e4;
  background: #f0fdfa;
  color: #0f766e;
}

.omni-channel-main,
.omni-side-action,
.omni-template-row,
.omni-composer-actions,
.omni-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.omni-count,
.omni-unread {
  min-width: 22px;
  border-radius: 999px;
  background: #e2e8f0;
  padding: 1px 7px;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
}

.omni-side-section {
  margin-top: 24px;
  border-top: 1px solid #e2e8f0;
  padding-top: 16px;
}

.omni-side-title {
  margin-bottom: 8px;
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.omni-side-action {
  width: 100%;
  margin-bottom: 6px;
  padding: 9px 10px;
  color: #475569;
}

.omni-side-action:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.omni-list-pane {
  display: flex;
  flex-direction: column;
}

.omni-list-header,
.omni-detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid #e2e8f0;
  padding: 16px;
}

.omni-refresh,
.omni-icon-button {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  background: #f8fafc;
  color: #475569;
}

.omni-toolbar {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.omni-search {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 8px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0 10px;
  background: #ffffff;
}

.omni-search input,
.omni-toolbar select,
.omni-template-row select,
.omni-composer textarea {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  font-size: 13px;
}

.omni-toolbar select,
.omni-template-row select {
  width: auto;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px;
  background: #ffffff;
}

.omni-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.omni-row {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px;
  background: #ffffff;
}

.omni-row.active {
  border-color: #14b8a6;
  background: #f0fdfa;
}

.omni-row input {
  margin-top: 4px;
}

.omni-row-body {
  min-width: 0;
  flex: 1;
  text-align: left;
}

.omni-row-top,
.omni-row-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.omni-row-title,
.omni-row-meta,
.omni-row-preview {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.omni-row-title {
  font-weight: 800;
}

.omni-row-meta,
.omni-row-preview {
  color: #64748b;
  font-size: 12px;
}

.omni-channel-pill,
.omni-sla,
.omni-provider {
  border-radius: 999px;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 800;
}

.omni-channel-pill.green,
.omni-provider.ready {
  background: #dcfce7;
  color: #15803d;
}

.omni-channel-pill.blue {
  background: #dbeafe;
  color: #1d4ed8;
}

.omni-channel-pill.orange {
  background: #ffedd5;
  color: #c2410c;
}

.omni-channel-pill.teal {
  background: #ccfbf1;
  color: #0f766e;
}

.omni-channel-pill.slate,
.omni-sla {
  background: #e2e8f0;
  color: #475569;
}

.omni-sla.breach,
.omni-provider.blocked {
  background: #fee2e2;
  color: #b91c1c;
}

.omni-empty,
.omni-state,
.omni-detail-empty {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 8px;
  height: 100%;
  padding: 32px;
  color: #64748b;
  text-align: center;
}

.omni-detail-pane {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.omni-detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  min-height: 0;
  flex: 1;
}

.omni-thread {
  display: flex;
  min-width: 0;
  flex-direction: column;
  border-right: 1px solid #e2e8f0;
}

.omni-sla-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  border-bottom: 1px solid #e2e8f0;
  padding: 10px 16px;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.omni-messages {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
}

.omni-message {
  max-width: 74%;
  margin-bottom: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px;
  background: #ffffff;
}

.omni-message.outbound {
  margin-left: auto;
  border-color: #99f6e4;
  background: #f0fdfa;
}

.omni-message.internal {
  margin-inline: auto;
  border-color: #fde68a;
  background: #fffbeb;
}

.omni-message-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 6px;
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
}

.omni-message-body {
  color: #1e293b;
  font-size: 13px;
  line-height: 1.5;
}

.omni-attachment {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
}

.omni-composer {
  border-top: 1px solid #e2e8f0;
  padding: 14px;
  background: #ffffff;
}

.omni-provider-warning {
  margin-bottom: 10px;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 8px 10px;
  background: #fef2f2;
  color: #991b1b;
  font-size: 12px;
}

.omni-template-row {
  margin-bottom: 10px;
}

.omni-suggestions {
  display: grid;
  gap: 6px;
  margin-bottom: 10px;
}

.omni-suggestions button {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px;
  background: #f8fafc;
  text-align: left;
  font-size: 12px;
}

.omni-composer textarea {
  min-height: 90px;
  resize: vertical;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 10px;
}

.omni-composer-actions {
  justify-content: space-between;
  margin-top: 10px;
}

.omni-secondary,
.omni-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 800;
}

.omni-secondary {
  border-color: #cbd5e1;
  background: #ffffff;
  color: #334155;
}

.omni-secondary.full {
  width: 100%;
  margin-top: 12px;
}

.omni-primary {
  border-color: #0f766e;
  background: #0f766e;
  color: #ffffff;
}

.omni-primary:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.omni-context {
  overflow-y: auto;
  padding: 16px;
  background: #f8fafc;
}

.omni-context-section {
  margin-bottom: 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px;
  background: #ffffff;
}

.omni-context-section h3 {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 800;
}

.omni-context-name {
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 800;
}

.omni-context-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  font-size: 12px;
}

.omni-context-grid span,
.omni-muted {
  color: #64748b;
}

.omni-note {
  border-left: 3px solid #0f766e;
  padding-left: 10px;
  color: #334155;
  font-size: 12px;
}

@media (max-width: 1180px) {
  .omni-shell {
    grid-template-columns: 220px minmax(280px, 360px) minmax(0, 1fr);
  }

  .omni-detail-grid {
    grid-template-columns: 1fr;
  }

  .omni-context {
    border-top: 1px solid #e2e8f0;
  }
}

@media (max-width: 820px) {
  .omni-shell {
    grid-template-columns: 1fr;
    height: auto;
  }

  .omni-nav,
  .omni-list-pane,
  .omni-detail-pane {
    min-height: auto;
    border-right: 0;
    border-bottom: 1px solid #dbe3ea;
  }
}
</style>
