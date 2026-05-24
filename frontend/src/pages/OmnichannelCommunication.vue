<template>
  <div class="flex h-full flex-col bg-white">
    <LayoutHeader>
      <template #left-header>
        <div class="flex min-w-0 items-center gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-[10px]"
            style="background: linear-gradient(135deg, #22c55e, #14b8a6)"
          >
            <FeatherIcon name="message-square" class="h-4 w-4 text-white" />
          </div>
          <div class="min-w-0">
            <h1 class="truncate text-lg font-semibold text-crm-text">
              {{ __('Omnichannel Communication') }}
            </h1>
            <p class="truncate text-xs text-crm-muted">
              {{ __('Unified Inbox (POC)') }}
            </p>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            :label="__('New Conversation')"
            variant="solid"
            @click="showConversationForm = true"
          />
          <Button
            :label="__('New Campaign')"
            variant="outline"
            @click="showCampaignInfo = true"
          />
        </div>
      </template>
    </LayoutHeader>

    <div class="flex min-h-0 flex-1 gap-4 bg-surface-gray-1 p-4">
      <div class="flex w-[360px] flex-col gap-4">
        <div
          class="rounded-[14px] border border-crm-border bg-white px-4 py-3 shadow-sm"
        >
          <div class="flex items-center gap-2">
            <input
              v-model="search"
              class="h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm"
              :placeholder="__('Search conversations')"
              type="search"
            />
          </div>
          <div class="mt-3 flex flex-wrap gap-2">
            <button
              v-for="tab in tabs"
              :key="tab"
              class="rounded-full border px-3 py-1 text-xs"
              :class="
                activeTab === tab
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-outline-gray-2 text-ink-gray-6'
              "
              @click="activeTab = tab"
            >
              <span>{{ __(tab) }}</span>
              <span
                v-if="tabCounts[tab] > 0"
                class="ml-1 rounded-full bg-primary-500 px-1.5 text-[10px] text-white font-semibold"
              >
                {{ tabCounts[tab] }}
              </span>
            </button>
          </div>
          <div class="mt-3 flex items-center justify-between gap-2">
            <div class="flex items-center gap-2 text-xs text-ink-gray-5">
              <input
                class="h-4 w-4 rounded border-outline-gray-2"
                type="checkbox"
                :checked="allSelected"
                @change="toggleSelectAll"
              />
              <span>
                {{
                  selectedIds.length
                    ? `${selectedIds.length} ${__('selected')}`
                    : __('Select all')
                }}
              </span>
              <button
                v-if="selectedIds.length"
                class="text-[11px] text-ink-gray-4 underline"
                @click="clearSelection"
              >
                {{ __('Clear') }}
              </button>
            </div>
            <select
              v-model="sortOption"
              class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs"
            >
              <option value="recent">{{ __('Sort: Recent') }}</option>
              <option value="unread">{{ __('Sort: Unread') }}</option>
              <option value="priority">{{ __('Sort: Priority') }}</option>
            </select>
          </div>
        </div>

        <div
          class="flex flex-1 flex-col overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm"
        >
          <div class="flex items-center justify-between border-b border-crm-border px-4 py-2.5">
            <div class="text-xs font-semibold text-ink-gray-6">
              {{ __('Conversations') }}
            </div>
            <div class="text-xs text-ink-gray-4">
              {{ filteredConversations.length }} {{ __('items') }}
            </div>
          </div>
          <div class="flex-1 overflow-y-auto">
            <button
              v-for="conversation in filteredConversations"
              :key="conversation.id"
              class="flex w-full flex-col gap-1 border-b border-outline-gray-1 px-4 py-3 text-left"
              :class="
                selectedId === conversation.id
                  ? 'bg-primary-50'
                  : 'hover:bg-surface-gray-1'
              "
              @click="selectConversation(conversation.id)"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex min-w-0 flex-1 items-start gap-2">
                  <input
                    class="mt-1 h-4 w-4 rounded border-outline-gray-2"
                    type="checkbox"
                    :checked="isSelected(conversation.id)"
                    @click.stop
                    @change="toggleSelection(conversation.id, $event)"
                  />
                  <div class="min-w-0">
                    <div class="flex items-center gap-2">
                      <span class="truncate text-sm font-medium text-ink-gray-9">
                        {{ conversation.customer }}
                      </span>
                      <Badge
                        :label="conversation.channel"
                        variant="subtle"
                        theme="gray"
                      />
                      <Badge
                        v-if="conversation.priority === 'High'"
                        :label="__('High')"
                        variant="subtle"
                        theme="red"
                      />
                    </div>
                    <div class="mt-1 truncate text-xs text-ink-gray-5">
                      {{ conversation.lastMessage }}
                    </div>
                  </div>
                </div>
                <div class="flex flex-col items-end gap-1">
                  <span class="text-xs text-ink-gray-4">
                    {{ conversation.lastTime }}
                  </span>
                  <span
                    v-if="conversation.unread"
                    class="rounded-full bg-primary-500 px-2 text-[10px] text-white"
                  >
                    {{ conversation.unread }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-2 text-[11px] text-ink-gray-5">
                <span>{{ conversation.assignedTo }}</span>
                <span>•</span>
                <span>{{ conversation.status }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div class="flex min-w-0 flex-1 flex-col gap-4">
        <div
          class="flex min-h-0 flex-1 overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm"
        >
          <div class="flex min-w-0 flex-1 flex-col">
            <div class="border-b border-crm-border px-4 py-3">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <div class="text-base font-semibold text-ink-gray-9">
                    {{ activeConversation.customer }}
                  </div>
                  <div class="text-xs text-ink-gray-5">
                    {{ activeConversation.subject }}
                  </div>
                  <div
                    v-if="activeConversation.slaTargetMin"
                    class="mt-2 flex items-center gap-2 text-[11px] text-ink-gray-5"
                  >
                    <span class="rounded-full bg-surface-gray-2 px-2 py-0.5">
                      {{ __('SLA') }}
                      {{ activeConversation.slaRemainingMin }}{{ __('m') }}
                      {{ __('left') }}
                    </span>
                    <span class="rounded-full bg-surface-gray-2 px-2 py-0.5">
                      {{ __('Routing') }}: {{ activeConversation.routingRule }}
                    </span>
                    <span
                      v-if="whatsappReplyWindow"
                      :class="
                        whatsappReplyWindow.isExpiring
                          ? 'bg-ink-red-1 text-ink-red-6'
                          : 'bg-surface-gray-2'
                      "
                      class="rounded-full px-2 py-0.5"
                    >
                      {{ __('24h window') }}:
                      {{ whatsappReplyWindow.remainingHours }}{{
                        __('h')
                      }}
                      {{ whatsappReplyWindow.remainingMinutes % 60 }}{{
                        __('m')
                      }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <Badge :label="activeConversation.status" variant="subtle" />
                  <Badge
                    :label="activeConversation.channel"
                    variant="subtle"
                    theme="gray"
                  />
                  <Badge
                    v-if="activeConversation.slaStatus"
                    :label="activeConversation.slaStatus"
                    variant="subtle"
                    :theme="activeConversation.slaStatus === 'Breached' ? 'red' : 'orange'"
                  />
                </div>
              </div>
            </div>

            <div class="flex-1 overflow-y-auto px-4 py-4">
              <div
                v-for="message in activeConversation.messages"
                :key="message.id"
                class="mb-3 flex"
                :class="message.direction === 'out' ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-[70%] rounded-2xl px-3 py-2 text-sm"
                  :class="
                    message.direction === 'out'
                      ? 'bg-primary-500 text-white'
                      : 'bg-surface-gray-2 text-ink-gray-8'
                  "
                >
                  <div class="whitespace-pre-line">{{ message.body }}</div>
                  <div v-if="message.media && message.media.length" class="mt-2 space-y-1">
                    <div
                      v-for="(file, idx) in message.media"
                      :key="idx"
                      class="flex items-center gap-1 rounded bg-black/10 px-2 py-1 text-[11px]"
                    >
                      <span v-if="file.type === 'document'">📎</span>
                      <span v-else>🖼</span>
                      <span class="truncate">{{ file.name }}</span>
                      <span class="ml-auto text-[10px] opacity-70">{{ file.size }}</span>
                    </div>
                  </div>
                  <div class="mt-1 flex items-center justify-between gap-2 text-[10px] opacity-70">
                    <span>{{ message.time }}</span>
                    <div v-if="message.direction === 'out'" class="flex gap-0.5">
                      <span v-if="message.status === 'read'" title="Read">✓✓</span>
                      <span v-else-if="message.status === 'delivered'" title="Delivered">✓✓</span>
                      <span v-else title="Sent">✓</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="border-t border-crm-border px-4 py-3">
              <div class="mb-2 flex items-center gap-2">
                <select
                  v-model="selectedTemplate"
                  class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs"
                >
                  <option value="">{{ __('Insert template') }}</option>
                  <option
                    v-for="template in templates.filter((t) => t.channel === activeConversation.channel)"
                    :key="template.id"
                    :value="template.id"
                  >
                    {{ template.name }}
                    {{ template.isApproved ? '✓ approved' : '' }}
                  </option>
                </select>
                <Button
                  :label="__('Apply')"
                  variant="subtle"
                  @click="applyTemplate"
                />
                <div class="ml-auto flex items-center gap-1 text-[10px] text-ink-gray-4">
                  <span v-if="whatsappReplyWindow && !whatsappReplyWindow.isActive">
                    ⏰ {{ __('24h window expired') }}
                  </span>
                </div>
              </div>
              <div class="flex items-end gap-2">
                <div class="flex gap-1">
                  <Button
                    icon="image"
                    variant="ghost"
                    title="Attach media"
                    @click="() => {}"
                  />
                  <Button
                    icon="paperclip"
                    variant="ghost"
                    title="Attach document"
                    @click="() => {}"
                  />
                </div>
                <textarea
                  v-model="composer"
                  rows="2"
                  class="min-h-10 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm"
                  :placeholder="__('Type a message...')"
                  :disabled="whatsappReplyWindow && !whatsappReplyWindow.isActive"
                />
                <div v-if="activeConversation.channel === 'WhatsApp'" class="flex items-end gap-1">
                  <select
                    v-model="messageTone"
                    class="h-9 rounded-md border border-outline-gray-2 px-2 text-xs"
                    title="Message tone (for AI suggestions)"
                  >
                    <option value="Formal">{{ __('Formal') }}</option>
                    <option value="Friendly">{{ __('Friendly') }}</option>
                  </select>
                </div>
                <Button
                  :label="__('Send')"
                  variant="solid"
                  :disabled="whatsappReplyWindow && !whatsappReplyWindow.isActive"
                  @click="sendMessage"
                />
              </div>
            </div>
          </div>

          <div class="w-72 border-l border-crm-border bg-surface-gray-1 p-4">
            <div class="text-sm font-semibold text-ink-gray-8">
              {{ __('Customer Context') }}
            </div>
            <div class="mt-3 space-y-3 text-xs text-ink-gray-6">
              <div>
                <div class="text-ink-gray-4">{{ __('Segment') }}</div>
                <div class="text-sm text-ink-gray-8">
                  {{ activeConversation.context.segment }}
                </div>
              </div>
              <div>
                <div class="text-ink-gray-4">{{ __('Active Facility') }}</div>
                <div class="text-sm text-ink-gray-8">
                  {{ activeConversation.context.facility }}
                </div>
              </div>
              <div>
                <div class="text-ink-gray-4">{{ __('RM Owner') }}</div>
                <div class="text-sm text-ink-gray-8">
                  {{ activeConversation.assignedTo }}
                </div>
              </div>
              <div>
                <div class="text-ink-gray-4">{{ __('Tags') }}</div>
                <div class="mt-1 flex flex-wrap gap-1">
                  <Badge
                    v-for="tag in activeConversation.tags"
                    :key="tag"
                    :label="tag"
                    variant="subtle"
                    theme="gray"
                  />
                </div>
              </div>
              <div>
                <div class="text-ink-gray-4">{{ __('Next Action') }}</div>
                <div class="text-sm text-ink-gray-8">
                  {{ activeConversation.context.nextAction }}
                </div>
              </div>
              <div>
                <div class="text-ink-gray-4">{{ __('Routing') }}</div>
                <div class="text-sm text-ink-gray-8">
                  {{ activeConversation.routingRule }}
                </div>
                <div class="mt-1 text-[11px] text-ink-gray-5">
                  {{ __('Queue') }}: {{ activeConversation.queueName }}
                </div>
              </div>
              <div v-if="activeConversation.slaTargetMin">
                <div class="text-ink-gray-4">{{ __('SLA Timer') }}</div>
                <div class="mt-1 text-sm text-ink-gray-8">
                  {{ activeConversation.slaRemainingMin }}{{ __('m') }} /
                  {{ activeConversation.slaTargetMin }}{{ __('m') }}
                </div>
                <div class="mt-2 h-2 w-full rounded-full bg-surface-gray-2">
                  <div
                    class="h-2 rounded-full"
                    :class="
                      activeConversation.slaStatus === 'Breached'
                        ? 'bg-ink-red-3'
                        : activeConversation.slaStatus === 'At Risk'
                          ? 'bg-ink-orange-3'
                          : 'bg-ink-green-3'
                    "
                    :style="{ width: activeConversation.slaPercent + '%' }"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-4 gap-3">
          <div class="rounded-[12px] border border-outline-gray-1 bg-white p-3">
            <div class="text-xs text-ink-gray-4">{{ __('Total Conversations') }}</div>
            <div class="mt-1 text-lg font-semibold text-ink-gray-9">
              {{ metrics.total }}
            </div>
          </div>
          <div class="rounded-[12px] border border-outline-gray-1 bg-white p-3">
            <div class="text-xs text-ink-gray-4">{{ __('Avg Response') }}</div>
            <div class="mt-1 text-lg font-semibold text-ink-gray-9">
              {{ metrics.avgResponse }}
            </div>
          </div>
          <div class="rounded-[12px] border border-outline-gray-1 bg-white p-3">
            <div class="text-xs text-ink-gray-4">{{ __('Routing Queue') }}</div>
            <div class="mt-1 text-lg font-semibold text-ink-gray-9">
              {{ metrics.queueBacklog }}
            </div>
          </div>
          <div class="rounded-[12px] border border-outline-gray-1 bg-white p-3">
            <div class="text-xs text-ink-gray-4">{{ __('SLA Breaches') }}</div>
            <div class="mt-1 text-lg font-semibold text-ink-gray-9">
              {{ metrics.slaBreaches }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div
    v-if="showConversationForm"
    class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4"
  >
    <div class="w-full max-w-lg rounded-[16px] bg-white p-6 shadow-xl">
      <div class="flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">
          {{ __('New Conversation') }}
        </div>
        <button class="text-ink-gray-4" @click="showConversationForm = false">
          ✕
        </button>
      </div>
      <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Customer') }}</label>
          <input
            v-model="form.customer"
            class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3"
            type="text"
          />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Channel') }}</label>
          <select
            v-model="form.channel"
            class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2"
          >
            <option v-for="tab in tabs.slice(1)" :key="tab" :value="tab">
              {{ tab }}
            </option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Priority') }}</label>
          <select
            v-model="form.priority"
            class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2"
          >
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
          </select>
        </div>
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Subject') }}</label>
          <input
            v-model="form.subject"
            class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3"
            type="text"
          />
        </div>
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Initial Message') }}</label>
          <textarea
            v-model="form.message"
            rows="3"
            class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2"
          />
        </div>
      </div>
      <div class="mt-5 flex items-center justify-end gap-2">
        <Button
          :label="__('Cancel')"
          variant="subtle"
          @click="showConversationForm = false"
        />
        <Button :label="__('Create')" variant="solid" @click="addConversation" />
      </div>
    </div>
  </div>

  <div
    v-if="showCampaignInfo"
    class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4"
  >
    <div class="w-full max-w-md rounded-[16px] bg-white p-6 shadow-xl">
      <div class="flex items-center justify-between">
        <div class="text-lg font-semibold text-ink-gray-9">
          {{ __('New Campaign') }}
        </div>
        <button class="text-ink-gray-4" @click="showCampaignInfo = false">
          ✕
        </button>
      </div>
      <p class="mt-3 text-sm text-ink-gray-6">
        {{
          __(
            'Campaigns are for broadcasting templates to a segmented audience (e.g., payment reminders or promo updates). This POC shows the entry point only.',
          )
        }}
      </p>
      <div class="mt-4 flex justify-end">
        <Button
          :label="__('Close')"
          variant="solid"
          @click="showCampaignInfo = false"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Badge, Button, FeatherIcon, usePageMeta } from 'frappe-ui'
import { computed, ref } from 'vue'

const tabs = ['All', 'WhatsApp', 'Email', 'SMS', 'In-app']
const search = ref('')
const activeTab = ref('All')
const sortOption = ref('recent')
const showConversationForm = ref(false)
const showCampaignInfo = ref(false)
const selectedIds = ref([])
const messageTone = ref('Formal')
const form = ref({
  customer: '',
  channel: 'WhatsApp',
  priority: 'Medium',
  subject: '',
  message: '',
})

const templates = [
  {
    id: 'wa_followup',
    channel: 'WhatsApp',
    name: 'Follow-up Reminder',
    body: 'Hi {{name}}, just checking in on your application status.',
    isApproved: true,
  },
  {
    id: 'wa_docs',
    channel: 'WhatsApp',
    name: 'Document Request',
    body: 'Hi {{name}}, please share the required documents for verification.',
    isApproved: true,
  },
  {
    id: 'email_summary',
    channel: 'Email',
    name: 'Summary Email',
    body: 'Dear {{name}}, here is the summary of our last discussion...',
    isApproved: false,
  },
]

const conversations = ref([
  {
    id: 'conv-001',
    channel: 'WhatsApp',
    customer: 'PT Nusantara Jaya',
    subject: 'Loan application follow-up',
    lastMessage: 'We have sent the missing documents.',
    lastTime: '10:24',
    lastTimestamp: Date.now() - 12 * 60 * 1000,
    unread: 2,
    status: 'Open',
    priority: 'High',
    assignedTo: 'Dewi Pratama',
    slaStatus: 'Breached',
    slaTargetMin: 30,
    slaRemainingMin: -5,
    slaPercent: 100,
    routingRule: 'Keyword: Dokumen',
    queueName: 'Priority RM Queue',
    tags: ['Credit', 'Urgent'],
    context: {
      segment: 'Enterprise Banking',
      facility: 'Working Capital Loan',
      nextAction: 'Call customer by 15:00',
    },
    messages: [
      {
        id: 'm-001',
        direction: 'in',
        body: 'Selamat pagi, dokumen sudah kami kirimkan.',
        time: '09:45',
        status: 'read',
        media: [
          { type: 'document', name: 'Document1.pdf', size: '245 KB' },
          { type: 'document', name: 'Invoice.pdf', size: '128 KB' },
        ],
      },
      {
        id: 'm-002',
        direction: 'out',
        body: 'Terima kasih, kami cek dahulu dan update hari ini.',
        time: '09:50',
        status: 'read',
      },
    ],
  },
  {
    id: 'conv-002',
    channel: 'Email',
    customer: 'Sari Logistics',
    subject: 'Proposal update',
    lastMessage: 'We need a revised term sheet.',
    lastTime: '09:10',
    lastTimestamp: Date.now() - 80 * 60 * 1000,
    unread: 0,
    status: 'Pending',
    priority: 'Medium',
    assignedTo: 'Rizky Andalan',
    slaStatus: 'At Risk',
    slaTargetMin: 60,
    slaRemainingMin: 12,
    slaPercent: 80,
    routingRule: 'Product: Revolving Credit',
    queueName: 'Commercial Queue',
    tags: ['Renewal'],
    context: {
      segment: 'Commercial',
      facility: 'Revolving Credit',
      nextAction: 'Prepare revised proposal',
    },
    messages: [
      {
        id: 'm-003',
        direction: 'in',
        body: 'Can you share an updated term sheet by tomorrow?',
        time: '08:30',
        status: 'read',
      },
      {
        id: 'm-004',
        direction: 'out',
        body: 'Sure, we will send it by end of day.',
        time: '08:45',
        status: 'delivered',
      },
    ],
  },
  {
    id: 'conv-003',
    channel: 'SMS',
    customer: 'CV Arjuna',
    subject: 'Payment reminder',
    lastMessage: 'Thanks, we will pay today.',
    lastTime: 'Yesterday',
    lastTimestamp: Date.now() - 26 * 60 * 60 * 1000,
    unread: 1,
    status: 'Open',
    priority: 'Low',
    assignedTo: 'Maya Lestari',
    slaStatus: '',
    slaTargetMin: 120,
    slaRemainingMin: 60,
    slaPercent: 50,
    routingRule: 'Fallback: Round-robin',
    queueName: 'Collections Queue',
    tags: ['Collections'],
    context: {
      segment: 'SME',
      facility: 'Invoice Financing',
      nextAction: 'Monitor payment confirmation',
    },
    messages: [
      {
        id: 'm-005',
        direction: 'out',
        body: 'Reminder: payment due today. Please confirm once completed.',
        time: 'Yesterday',
        status: 'read',
      },
      {
        id: 'm-006',
        direction: 'in',
        body: 'Thanks, we will pay today.',
        time: 'Yesterday',
        status: 'read',
      },
    ],
  },
])

const selectedId = ref(conversations.value[0]?.id || '')
const composer = ref('')
const selectedTemplate = ref('')

const allSelected = computed(() => {
  if (!filteredConversations.value.length) return false
  return filteredConversations.value.every((conversation) =>
    selectedIds.value.includes(conversation.id),
  )
})

const filteredConversations = computed(() => {
  const query = search.value.trim().toLowerCase()
  const results = conversations.value.filter((conversation) => {
    const matchesTab =
      activeTab.value === 'All' || conversation.channel === activeTab.value
    const matchesQuery =
      !query ||
      conversation.customer.toLowerCase().includes(query) ||
      conversation.lastMessage.toLowerCase().includes(query)
    return matchesTab && matchesQuery
  })
  const priorityRank = {
    High: 3,
    Medium: 2,
    Low: 1,
  }
  return [...results].sort((a, b) => {
    if (sortOption.value === 'unread') {
      return (
        (b.unread || 0) - (a.unread || 0) ||
        (b.lastTimestamp || 0) - (a.lastTimestamp || 0)
      )
    }
    if (sortOption.value === 'priority') {
      return (
        (priorityRank[b.priority] || 0) - (priorityRank[a.priority] || 0) ||
        (b.lastTimestamp || 0) - (a.lastTimestamp || 0)
      )
    }
    return (b.lastTimestamp || 0) - (a.lastTimestamp || 0)
  })
})

const activeConversation = computed(() => {
  return (
    conversations.value.find((conv) => conv.id === selectedId.value) ||
    conversations.value[0]
  )
})

const tabCounts = computed(() => {
  const counts = { All: 0, WhatsApp: 0, Email: 0, SMS: 0, 'In-app': 0 }
  conversations.value.forEach((conversation) => {
    counts.All += conversation.unread || 0
    if (counts[conversation.channel] !== undefined) {
      counts[conversation.channel] += conversation.unread || 0
    }
  })
  return counts
})

const metrics = computed(() => {
  const total = conversations.value.length
  const slaBreaches = conversations.value.filter(
    (conversation) => conversation.slaStatus === 'Breached',
  ).length
  return {
    total,
    avgResponse: '18m',
    queueBacklog: '14',
    slaBreaches,
  }
})

const whatsappReplyWindow = computed(() => {
  if (!activeConversation.value || activeConversation.value.channel !== 'WhatsApp') {
    return null
  }
  
  const lastInbound = activeConversation.value.messages
    .filter((m) => m.direction === 'in')
    .pop()
  
  if (!lastInbound) return null
  
  // Mock: assume last inbound was within last few hours
  const lastInboundTime = new Date(Date.now() - 3 * 60 * 60 * 1000)
  const windowEnd = new Date(lastInboundTime.getTime() + 24 * 60 * 60 * 1000)
  const now = new Date()
  const remaining = Math.max(0, Math.floor((windowEnd - now) / (60 * 1000)))
  
  return {
    isActive: remaining > 0,
    remainingMinutes: remaining,
    remainingHours: Math.floor(remaining / 60),
    isExpiring: remaining < 60,
  }
})

function selectConversation(id) {
  selectedId.value = id
  const conversation = conversations.value.find((conv) => conv.id === id)
  if (conversation) {
    conversation.unread = 0
  }
}

function toggleSelection(id, event) {
  if (event?.target?.checked) {
    if (!selectedIds.value.includes(id)) {
      selectedIds.value = [...selectedIds.value, id]
    }
    return
  }
  selectedIds.value = selectedIds.value.filter((selectedId) => selectedId !== id)
}

function toggleSelectAll(event) {
  const visibleIds = filteredConversations.value.map((conversation) => conversation.id)
  if (event?.target?.checked) {
    const merged = new Set([...selectedIds.value, ...visibleIds])
    selectedIds.value = Array.from(merged)
    return
  }
  selectedIds.value = selectedIds.value.filter(
    (selectedId) => !visibleIds.includes(selectedId),
  )
}

function clearSelection() {
  selectedIds.value = []
}

function isSelected(id) {
  return selectedIds.value.includes(id)
}

function applyTemplate() {
  if (!selectedTemplate.value) return
  const template = templates.find((t) => t.id === selectedTemplate.value)
  if (!template) return
  composer.value = template.body
}

function sendMessage() {
  if (!composer.value.trim()) return
  const conversation = activeConversation.value
  if (!conversation) return
  conversation.messages.push({
    id: `m-${Date.now()}`,
    direction: 'out',
    body: composer.value.trim(),
    time: 'Now',
  })
  conversation.lastMessage = composer.value.trim()
  conversation.lastTime = 'Now'
  conversation.lastTimestamp = Date.now()
  conversation.unread = 0
  composer.value = ''
}

function addConversation() {
  if (!form.value.customer || !form.value.subject) return
  const newConversation = {
    id: `conv-${Date.now()}`,
    channel: form.value.channel,
    customer: form.value.customer,
    subject: form.value.subject,
    lastMessage: form.value.message || __('New conversation created'),
    lastTime: 'Now',
    lastTimestamp: Date.now(),
    unread: 0,
    status: 'Open',
    priority: form.value.priority,
    assignedTo: 'Auto-Routed',
    slaStatus: 'At Risk',
    slaTargetMin: 60,
    slaRemainingMin: 60,
    slaPercent: 10,
    routingRule: 'Manual creation',
    queueName: 'Omnichannel Queue',
    tags: [],
    context: {
      segment: 'Prospect',
      facility: '-',
      nextAction: 'Assign RM',
    },
    messages: [
      {
        id: `m-${Date.now()}-init`,
        direction: 'out',
        body: form.value.message || __('Conversation started.'),
        time: 'Now',
      },
    ],
  }
  conversations.value.unshift(newConversation)
  selectedId.value = newConversation.id
  form.value = {
    customer: '',
    channel: 'WhatsApp',
    priority: 'Medium',
    subject: '',
    message: '',
  }
  showConversationForm.value = false
}

usePageMeta(() => ({ title: __('Omnichannel Communication') }))
</script>
