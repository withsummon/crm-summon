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
              {{ __('Unified Conversation Workspace') }}
            </p>
          </div>
        </div>
      </template>
      <template #right-header>
        <div class="flex items-center gap-2">
          <Button
            :label="__('Connect WA')"
            variant="subtle"
            @click="openWhatsAppConnect"
          >
            <template #prefix>
              <FeatherIcon name="message-circle" class="h-4 w-4 text-emerald-600" />
            </template>
          </Button>
          <Button
            :label="__('New Conversation')"
            variant="solid"
            @click="showConversationForm = true"
          />
          <Button
            :label="__('Broadcast')"
            variant="outline"
            @click="activePage = 'campaigns'; showCampaignForm = true"
          />
        </div>
      </template>
    </LayoutHeader>

    <!-- Page-level tabs -->
    <div class="flex items-center gap-1 border-b border-crm-border bg-white px-4">
      <button
        v-for="page in pages"
        :key="page.key"
        class="px-4 py-2.5 text-sm font-medium transition-colors"
        :class="
          activePage === page.key
            ? 'border-b-2 border-primary-500 text-primary-600'
            : 'text-ink-gray-5 hover:text-ink-gray-8'
        "
        @click="activePage = page.key"
      >
        {{ __(page.label) }}
        <span
          v-if="page.key === 'inbox' && totalUnread > 0"
          class="ml-1.5 rounded-full bg-primary-500 px-1.5 text-[10px] text-white"
        >
          {{ totalUnread }}
        </span>
      </button>
    </div>

    <!-- ── INBOX TAB ── -->
    <div v-if="activePage === 'inbox'" class="flex min-h-0 flex-1 gap-4 bg-surface-gray-1 p-4">
      <!-- Left: Conversation List -->
      <div class="flex w-[340px] flex-col gap-3">
        <div class="rounded-[14px] border border-crm-border bg-white px-4 py-3 shadow-sm">
          <div class="flex items-center gap-2">
            <input
              v-model="search"
              class="h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm"
              :placeholder="__('Search conversations...')"
              type="search"
            />
          </div>
          <div class="mt-3 flex flex-wrap gap-1.5">
            <button
              v-for="tab in channelTabs"
              :key="tab"
              class="rounded-full border px-3 py-1 text-xs"
              :class="
                activeTab === tab
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : 'border-outline-gray-2 text-ink-gray-6 hover:border-ink-gray-4'
              "
              @click="activeTab = tab"
            >
              {{ channelIcon(tab) }} {{ __(tab) }}
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
              <option value="recent">{{ __('Recent') }}</option>
              <option value="unread">{{ __('Unread') }}</option>
              <option value="priority">{{ __('Priority') }}</option>
            </select>
          </div>
        </div>

        <div class="flex flex-1 flex-col overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-crm-border px-4 py-2.5">
            <div class="text-xs font-semibold text-ink-gray-6">{{ __('Conversations') }}</div>
            <div class="text-xs text-ink-gray-4">{{ filteredConversations.length }} {{ __('items') }}</div>
          </div>
          <div class="flex-1 overflow-y-auto">
            <button
              v-for="conv in filteredConversations"
              :key="conv.id"
              class="flex w-full flex-col gap-1 border-b border-outline-gray-1 px-4 py-3 text-left transition-colors"
              :class="selectedId === conv.id ? 'bg-primary-50' : 'hover:bg-surface-gray-1'"
              @click="selectConversation(conv.id)"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="flex min-w-0 flex-1 items-start gap-2">
                  <input
                    class="mt-1 h-4 w-4 shrink-0 rounded border-outline-gray-2"
                    type="checkbox"
                    :checked="isSelected(conv.id)"
                    @click.stop
                    @change="toggleSelection(conv.id, $event)"
                  />
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center gap-1.5 flex-wrap">
                      <span class="truncate text-sm font-medium text-ink-gray-9">{{ conv.customer }}</span>
                      <span class="text-xs">{{ channelIcon(conv.channel) }}</span>
                      <Badge v-if="conv.priority === 'High'" label="High" variant="subtle" theme="red" />
                      <span :title="sentimentLabel(conv.sentiment)" class="text-xs">{{ sentimentEmoji(conv.sentiment) }}</span>
                    </div>
                    <div class="mt-0.5 truncate text-xs text-ink-gray-5">{{ conv.lastMessage }}</div>
                  </div>
                </div>
                <div class="flex flex-col items-end gap-1 shrink-0">
                  <span class="text-[10px] text-ink-gray-4">{{ conv.lastTime }}</span>
                  <span
                    v-if="conv.unread"
                    class="rounded-full bg-primary-500 px-1.5 text-[10px] text-white"
                  >
                    {{ conv.unread }}
                  </span>
                  <span
                    v-if="conv.slaStatus === 'Breached'"
                    class="rounded-full bg-red-100 px-1.5 text-[10px] text-red-600"
                  >
                    SLA!
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-2 text-[11px] text-ink-gray-4">
                <span>{{ conv.assignedTo }}</span>
                <span>·</span>
                <span>{{ conv.status }}</span>
                <span v-if="conv.tags.length" class="ml-auto flex gap-1">
                  <span
                    v-for="tag in conv.tags.slice(0, 2)"
                    :key="tag"
                    class="rounded-full bg-surface-gray-2 px-1.5 py-0.5 text-[10px]"
                  >
                    {{ tag }}
                  </span>
                </span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Center: Chat Window -->
      <div class="flex min-w-0 flex-1 flex-col gap-3">
        <div class="flex min-h-0 flex-1 flex-col overflow-hidden rounded-[14px] border border-crm-border bg-white shadow-sm">
          <!-- Conversation Header -->
          <div class="border-b border-crm-border px-4 py-3">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-base font-semibold text-ink-gray-9">{{ activeConv.customer }}</span>
                  <span class="text-base">{{ channelIcon(activeConv.channel) }}</span>
                  <Badge :label="activeConv.status" variant="subtle" />
                  <span
                    v-if="activeConv.isRecording"
                    class="flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-[10px] text-red-600"
                  >
                    <span class="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-red-500" />
                    {{ __('Recording') }}
                  </span>
                </div>
                <div class="text-xs text-ink-gray-5">{{ activeConv.subject }}</div>
                <div class="mt-1.5 flex flex-wrap items-center gap-2 text-[11px]">
                  <span
                    v-if="activeConv.slaTargetMin"
                    class="rounded-full bg-surface-gray-2 px-2 py-0.5"
                    :class="activeConv.slaStatus === 'Breached' ? '!bg-red-50 text-red-600' : activeConv.slaStatus === 'At Risk' ? '!bg-amber-50 text-amber-700' : 'text-ink-gray-5'"
                  >
                    SLA: {{ activeConv.slaRemainingMin >= 0 ? activeConv.slaRemainingMin + 'm left' : Math.abs(activeConv.slaRemainingMin) + 'm breached' }}
                  </span>
                  <span class="rounded-full bg-surface-gray-2 px-2 py-0.5 text-ink-gray-5">
                    {{ __('Route') }}: {{ activeConv.routingRule }}
                  </span>
                  <span
                    v-if="whatsappWindow"
                    class="rounded-full px-2 py-0.5"
                    :class="whatsappWindow.isExpiring ? 'bg-red-50 text-red-600' : 'bg-surface-gray-2 text-ink-gray-5'"
                  >
                    ⏱ 24h: {{ whatsappWindow.remainingHours }}h {{ whatsappWindow.remainingMinutes % 60 }}m
                  </span>
                </div>
              </div>
              <div class="flex shrink-0 items-center gap-1.5">
                <Button
                  icon="phone"
                  variant="ghost"
                  size="sm"
                  :title="__('Voice Call')"
                  @click="openVoiceCall"
                />
                <Button
                  icon="arrow-right"
                  variant="ghost"
                  size="sm"
                  :title="__('Transfer')"
                  @click="showTransferDialog = true"
                />
                <Button
                  icon="tag"
                  variant="ghost"
                  size="sm"
                  :title="__('Add Tag')"
                  @click="showTagDialog = true"
                />
                <Button
                  icon="archive"
                  variant="ghost"
                  size="sm"
                  :title="__('Archive')"
                  @click="archiveConversation"
                />
              </div>
            </div>
          </div>

          <!-- Messages -->
          <div ref="messageArea" class="flex-1 overflow-y-auto px-4 py-4 space-y-3">
            <div
              v-for="msg in activeConv.messages"
              :key="msg.id"
              class="flex"
              :class="msg.direction === 'out' ? 'justify-end' : 'justify-start'"
            >
              <!-- Internal note -->
              <div v-if="msg.internal" class="w-full rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
                <div class="flex items-center gap-1 font-medium mb-1">
                  <FeatherIcon name="lock" class="h-3 w-3" /> {{ __('Internal Note') }}
                  <span class="ml-auto text-amber-600 font-normal">{{ msg.time }}</span>
                </div>
                <div>{{ msg.body }}</div>
              </div>
              <!-- Regular message -->
              <div
                v-else
                class="max-w-[72%]"
              >
                <div
                  class="rounded-2xl px-3 py-2 text-sm"
                  :class="
                    msg.direction === 'out'
                      ? 'bg-primary-500 text-white rounded-br-sm'
                      : 'bg-surface-gray-2 text-ink-gray-8 rounded-bl-sm'
                  "
                >
                  <div class="whitespace-pre-line">{{ msg.body }}</div>
                  <div v-if="msg.media?.length" class="mt-2 space-y-1">
                    <div
                      v-for="(file, idx) in msg.media"
                      :key="idx"
                      class="flex items-center gap-1.5 rounded bg-black/10 px-2 py-1 text-[11px]"
                    >
                      <span>{{ file.type === 'document' ? '📎' : '🖼' }}</span>
                      <span class="truncate">{{ file.name }}</span>
                      <span class="ml-auto opacity-70">{{ file.size }}</span>
                    </div>
                  </div>
                  <div class="mt-1 flex items-center justify-between gap-2 text-[10px] opacity-70">
                    <span>{{ msg.time }}</span>
                    <span v-if="msg.direction === 'out'">
                      {{ msg.status === 'read' ? '✓✓' : msg.status === 'delivered' ? '✓✓' : '✓' }}
                    </span>
                  </div>
                </div>
                <!-- Sentiment badge on inbound -->
                <div v-if="msg.direction === 'in' && msg.sentiment" class="mt-0.5 text-[10px] text-ink-gray-4 px-1">
                  {{ sentimentEmoji(msg.sentiment) }} {{ sentimentLabel(msg.sentiment) }}
                </div>
              </div>
            </div>
            <!-- Typing indicator -->
            <div v-if="isTyping" class="flex justify-start">
              <div class="rounded-2xl bg-surface-gray-2 px-3 py-2 text-xs text-ink-gray-5 italic">
                {{ activeConv.customer }} {{ __('is typing') }}...
              </div>
            </div>
          </div>

          <!-- AI Suggestion Banner -->
          <div
            v-if="aiSuggestion"
            class="mx-4 mb-1 flex items-start gap-3 rounded-lg border border-primary-100 bg-primary-50 px-3 py-2"
          >
            <div class="flex-1">
              <div class="flex items-center gap-1 text-[11px] font-semibold text-primary-700">
                <FeatherIcon name="zap" class="h-3 w-3" />
                {{ __('AI Reply Suggestion') }}
              </div>
              <div class="mt-0.5 text-xs text-ink-gray-7">{{ aiSuggestion }}</div>
            </div>
            <div class="flex shrink-0 gap-1">
              <Button label="Use" variant="subtle" size="sm" @click="useAiSuggestion" />
              <Button icon="x" variant="ghost" size="sm" @click="aiSuggestion = ''" />
            </div>
          </div>

          <!-- Composer -->
          <div class="border-t border-crm-border px-4 py-3">
            <!-- Toolbar row -->
            <div class="mb-2 flex flex-wrap items-center gap-2">
              <!-- Internal/External toggle -->
              <div class="flex rounded-md border border-outline-gray-2 overflow-hidden text-xs">
                <button
                  class="px-2.5 py-1 transition-colors"
                  :class="!isInternal ? 'bg-primary-500 text-white' : 'text-ink-gray-5 hover:bg-surface-gray-1'"
                  @click="isInternal = false"
                >
                  {{ __('Reply') }}
                </button>
                <button
                  class="px-2.5 py-1 transition-colors"
                  :class="isInternal ? 'bg-amber-500 text-white' : 'text-ink-gray-5 hover:bg-surface-gray-1'"
                  @click="isInternal = true"
                >
                  🔒 {{ __('Internal') }}
                </button>
              </div>
              <select
                v-model="selectedTemplate"
                class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs"
                @change="applyTemplate"
              >
                <option value="">{{ __('Insert template') }}</option>
                <option
                  v-for="t in templates.filter((t) => t.channel === activeConv.channel || t.channel === 'All')"
                  :key="t.id"
                  :value="t.id"
                >
                  {{ t.name }}{{ t.isApproved ? ' ✓' : '' }}
                </option>
              </select>
              <div class="flex items-center gap-1">
                <select
                  v-model="messageTone"
                  class="h-8 rounded-md border border-outline-gray-2 px-2 text-xs"
                >
                  <option value="Formal">{{ __('Formal') }}</option>
                  <option value="Friendly">{{ __('Friendly') }}</option>
                  <option value="Concise">{{ __('Concise') }}</option>
                </select>
                <Button
                  :label="__('AI Suggest')"
                  icon="zap"
                  variant="subtle"
                  size="sm"
                  @click="generateAiSuggestion"
                />
              </div>
              <div v-if="autoResponderActive" class="ml-auto flex items-center gap-1 text-[10px] text-ink-gray-4 rounded-full bg-surface-gray-2 px-2 py-1">
                <span class="inline-block h-1.5 w-1.5 rounded-full bg-green-500" />
                {{ __('Auto-responder active') }}
              </div>
            </div>
            <!-- Attachment + Text + Send -->
            <div class="flex items-end gap-2">
              <div class="flex gap-1">
                <Button icon="image" variant="ghost" size="sm" title="Attach image" @click="() => {}" />
                <Button icon="paperclip" variant="ghost" size="sm" title="Attach document" @click="() => {}" />
                <Button icon="phone-call" variant="ghost" size="sm" title="Voice note" @click="() => {}" />
              </div>
              <textarea
                v-model="composer"
                rows="2"
                class="min-h-[60px] w-full rounded-md border px-3 py-2 text-sm transition-colors"
                :class="
                  isInternal
                    ? 'border-amber-300 bg-amber-50 placeholder-amber-400'
                    : whatsappWindow && !whatsappWindow.isActive
                      ? 'border-red-300 bg-red-50 text-ink-gray-4'
                      : 'border-outline-gray-2'
                "
                :placeholder="
                  isInternal
                    ? __('Write internal note (not visible to customer)...')
                    : whatsappWindow && !whatsappWindow.isActive
                      ? __('24h window expired. Use a template to restart.')
                      : __('Type a message...')
                "
                :disabled="!isInternal && whatsappWindow && !whatsappWindow.isActive"
              />
              <Button
                :label="isInternal ? __('Add Note') : __('Send')"
                variant="solid"
                :class="isInternal ? '!bg-amber-500' : ''"
                :disabled="!isInternal && whatsappWindow && !whatsappWindow.isActive"
                @click="sendMessage"
              />
            </div>
          </div>
        </div>

        <!-- Bottom Analytics Strip -->
        <div class="grid grid-cols-4 gap-3">
          <div v-for="m in bottomMetrics" :key="m.label" class="rounded-[12px] border border-outline-gray-1 bg-white p-3">
            <div class="text-xs text-ink-gray-4">{{ __(m.label) }}</div>
            <div class="mt-1 text-lg font-semibold text-ink-gray-9">{{ m.value }}</div>
            <div v-if="m.sub" class="text-[10px]" :class="m.subColor || 'text-ink-gray-4'">{{ __(m.sub) }}</div>
          </div>
        </div>
      </div>

      <!-- Right: Context Panel -->
      <div class="flex w-64 flex-col gap-3 overflow-y-auto">
        <!-- Customer Context -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between mb-3">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Customer Context') }}</div>
            <button class="text-xs text-primary-500 hover:underline" @click="() => {}">360 →</button>
          </div>
          <div class="space-y-3 text-xs">
            <div>
              <div class="text-ink-gray-4">{{ __('Segment') }}</div>
              <div class="font-medium text-ink-gray-8">{{ activeConv.context.segment }}</div>
            </div>
            <div>
              <div class="text-ink-gray-4">{{ __('Active Facility') }}</div>
              <div class="font-medium text-ink-gray-8">{{ activeConv.context.facility }}</div>
            </div>
            <div>
              <div class="text-ink-gray-4">{{ __('RM Owner') }}</div>
              <div class="font-medium text-ink-gray-8">{{ activeConv.assignedTo }}</div>
            </div>
            <div>
              <div class="text-ink-gray-4">{{ __('Sentiment') }}</div>
              <div class="mt-1 flex items-center gap-1.5">
                <span class="text-base">{{ sentimentEmoji(activeConv.sentiment) }}</span>
                <span
                  class="font-medium"
                  :class="{
                    'text-green-600': activeConv.sentiment === 'positive',
                    'text-amber-600': activeConv.sentiment === 'neutral',
                    'text-red-600': activeConv.sentiment === 'negative',
                  }"
                >
                  {{ sentimentLabel(activeConv.sentiment) }}
                </span>
              </div>
            </div>
            <div>
              <div class="text-ink-gray-4 mb-1">{{ __('Tags') }}</div>
              <div class="flex flex-wrap gap-1">
                <Badge
                  v-for="tag in activeConv.tags"
                  :key="tag"
                  :label="tag"
                  variant="subtle"
                  theme="gray"
                />
              </div>
            </div>
            <div>
              <div class="text-ink-gray-4">{{ __('Next Action') }}</div>
              <div class="font-medium text-ink-gray-8">{{ activeConv.context.nextAction }}</div>
            </div>
          </div>
        </div>

        <!-- SLA -->
        <div v-if="activeConv.slaTargetMin" class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-sm font-semibold text-ink-gray-8 mb-2">{{ __('SLA Monitor') }}</div>
          <div class="flex items-center justify-between text-xs mb-1">
            <span class="text-ink-gray-5">{{ __('Response SLA') }}</span>
            <Badge
              v-if="activeConv.slaStatus"
              :label="activeConv.slaStatus"
              variant="subtle"
              :theme="activeConv.slaStatus === 'Breached' ? 'red' : 'orange'"
            />
          </div>
          <div class="h-2 w-full rounded-full bg-surface-gray-2 overflow-hidden">
            <div
              class="h-2 rounded-full transition-all"
              :class="
                activeConv.slaStatus === 'Breached' ? 'bg-red-500' :
                activeConv.slaStatus === 'At Risk' ? 'bg-amber-500' : 'bg-green-500'
              "
              :style="{ width: Math.min(100, activeConv.slaPercent) + '%' }"
            />
          </div>
          <div class="mt-1 text-[10px] text-ink-gray-4">
            {{ activeConv.slaRemainingMin >= 0 ? activeConv.slaRemainingMin + 'm remaining' : Math.abs(activeConv.slaRemainingMin) + 'm past SLA' }}
            / target {{ activeConv.slaTargetMin }}m
          </div>
        </div>

        <!-- Auto-Responder -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Auto-Responder') }}</div>
            <button
              class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
              :class="autoResponderActive ? 'bg-green-500' : 'bg-surface-gray-3'"
              @click="autoResponderActive = !autoResponderActive"
            >
              <span
                class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                :class="autoResponderActive ? 'translate-x-4' : 'translate-x-0.5'"
              />
            </button>
          </div>
          <div v-if="autoResponderActive" class="text-[11px] text-green-700 bg-green-50 rounded px-2 py-1">
            {{ __('Active: "Thank you for your message. An RM will respond within 1 business hour."') }}
          </div>
          <div v-else class="text-[11px] text-ink-gray-4">{{ __('Set an automatic acknowledgment when away.') }}</div>
        </div>

        <!-- Compliance -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <div class="text-sm font-semibold text-ink-gray-8">{{ __('Compliance') }}</div>
            <button
              class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
              :class="activeConv.isRecording ? 'bg-red-500' : 'bg-surface-gray-3'"
              @click="toggleRecording"
            >
              <span
                class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform"
                :class="activeConv.isRecording ? 'translate-x-4' : 'translate-x-0.5'"
              />
            </button>
          </div>
          <div class="text-[11px] text-ink-gray-4">
            {{ activeConv.isRecording ? '🔴 ' + __('Recording for archive') : __('Archive conversation for audit compliance') }}
          </div>
        </div>
      </div>
    </div>

    <!-- ── CAMPAIGNS TAB ── -->
    <div v-if="activePage === 'campaigns'" class="flex min-h-0 flex-1 flex-col gap-4 bg-surface-gray-1 p-4">
      <div class="flex items-center justify-between">
        <div class="text-sm font-semibold text-ink-gray-7">{{ __('Broadcast Campaigns') }}</div>
        <Button :label="__('New Campaign')" variant="solid" @click="showCampaignForm = true" />
      </div>
      <div class="grid grid-cols-3 gap-4">
        <div
          v-for="camp in campaigns"
          :key="camp.id"
          class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between gap-2">
            <div>
              <div class="text-sm font-semibold text-ink-gray-9">{{ camp.name }}</div>
              <div class="text-xs text-ink-gray-5 mt-0.5">{{ camp.channel }} · {{ camp.audience }}</div>
            </div>
            <Badge :label="camp.status" variant="subtle" :theme="camp.status === 'Sent' ? 'green' : camp.status === 'Scheduled' ? 'blue' : 'gray'" />
          </div>
          <div class="mt-3 text-xs text-ink-gray-5">{{ camp.message.slice(0, 80) }}...</div>
          <div class="mt-3 grid grid-cols-3 gap-2 text-xs">
            <div class="text-center">
              <div class="font-semibold text-ink-gray-8">{{ camp.sent }}</div>
              <div class="text-ink-gray-4">{{ __('Sent') }}</div>
            </div>
            <div class="text-center">
              <div class="font-semibold text-green-600">{{ camp.delivered }}</div>
              <div class="text-ink-gray-4">{{ __('Delivered') }}</div>
            </div>
            <div class="text-center">
              <div class="font-semibold text-primary-600">{{ camp.opened }}</div>
              <div class="text-ink-gray-4">{{ __('Opened') }}</div>
            </div>
          </div>
          <div class="mt-3 text-[10px] text-ink-gray-4">{{ __('Scheduled') }}: {{ camp.scheduled }}</div>
        </div>
      </div>
    </div>

    <!-- ── TEMPLATES TAB ── -->
    <div v-if="activePage === 'templates'" class="flex min-h-0 flex-1 flex-col gap-4 bg-surface-gray-1 p-4">
      <div class="flex items-center justify-between">
        <div class="text-sm font-semibold text-ink-gray-7">{{ __('Message Templates') }}</div>
        <Button :label="__('New Template')" variant="solid" @click="showTemplateForm = true" />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div
          v-for="t in allTemplates"
          :key="t.id"
          class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between gap-2 mb-2">
            <div>
              <div class="text-sm font-semibold text-ink-gray-9">{{ t.name }}</div>
              <div class="text-xs text-ink-gray-5">{{ t.channel }} · {{ t.language }}</div>
            </div>
            <div class="flex items-center gap-1.5">
              <Badge v-if="t.isApproved" label="Approved" variant="subtle" theme="green" />
              <Badge v-else label="Draft" variant="subtle" theme="gray" />
            </div>
          </div>
          <div class="rounded-md bg-surface-gray-1 p-2 text-xs text-ink-gray-7 leading-relaxed">{{ t.body }}</div>
          <div class="mt-2 flex flex-wrap gap-1">
            <span
              v-for="field in t.mergeFields"
              :key="field"
              class="rounded bg-primary-50 px-1.5 py-0.5 text-[10px] text-primary-700"
            >
              {{ mergeFieldDisplay(field) }}
            </span>
          </div>
          <div class="mt-3 flex gap-2">
            <Button label="Edit" variant="ghost" size="sm" @click="() => {}" />
            <Button label="Preview" variant="ghost" size="sm" @click="() => {}" />
          </div>
        </div>
      </div>
    </div>

    <!-- ── ANALYTICS TAB ── -->
    <div v-if="activePage === 'analytics'" class="flex min-h-0 flex-1 flex-col gap-4 bg-surface-gray-1 p-4">
      <!-- KPI row -->
      <div class="grid grid-cols-5 gap-3">
        <div v-for="kpi in analyticsKpis" :key="kpi.label" class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-xs text-ink-gray-4">{{ __(kpi.label) }}</div>
          <div class="mt-1 text-2xl font-bold text-ink-gray-9">{{ kpi.value }}</div>
          <div class="mt-0.5 text-[11px]" :class="kpi.delta?.startsWith('+') ? 'text-green-600' : 'text-red-500'">
            {{ kpi.delta }} {{ __('vs last week') }}
          </div>
        </div>
      </div>
      <!-- Charts row -->
      <div class="grid grid-cols-3 gap-4">
        <!-- Volume by channel -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-sm font-semibold text-ink-gray-8 mb-3">{{ __('Volume by Channel') }}</div>
          <div class="space-y-2">
            <div v-for="ch in channelVolume" :key="ch.name" class="flex items-center gap-2 text-xs">
              <span class="w-16 text-ink-gray-6">{{ ch.name }}</span>
              <div class="flex-1 h-4 rounded-full bg-surface-gray-2 overflow-hidden">
                <div class="h-4 rounded-full" :style="{ width: ch.pct + '%', background: ch.color }" />
              </div>
              <span class="w-8 text-right text-ink-gray-5">{{ ch.count }}</span>
            </div>
          </div>
        </div>
        <!-- Response time by RM -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-sm font-semibold text-ink-gray-8 mb-3">{{ __('Avg Response Time by RM') }}</div>
          <div class="space-y-2">
            <div v-for="rm in rmResponse" :key="rm.name" class="flex items-center gap-2 text-xs">
              <span class="w-20 truncate text-ink-gray-6">{{ rm.name }}</span>
              <div class="flex-1 h-4 rounded-full bg-surface-gray-2 overflow-hidden">
                <div class="h-4 rounded-full bg-primary-400" :style="{ width: rm.pct + '%' }" />
              </div>
              <span class="w-10 text-right text-ink-gray-5">{{ rm.time }}</span>
            </div>
          </div>
        </div>
        <!-- Sentiment breakdown -->
        <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
          <div class="text-sm font-semibold text-ink-gray-8 mb-3">{{ __('Sentiment Analysis') }}</div>
          <div class="space-y-3">
            <div v-for="s in sentimentBreakdown" :key="s.label" class="flex items-center gap-2 text-xs">
              <span class="text-base">{{ s.emoji }}</span>
              <span class="w-16 text-ink-gray-6">{{ __(s.label) }}</span>
              <div class="flex-1 h-3 rounded-full bg-surface-gray-2 overflow-hidden">
                <div class="h-3 rounded-full" :style="{ width: s.pct + '%', background: s.color }" />
              </div>
              <span class="w-8 text-right text-ink-gray-5">{{ s.pct }}%</span>
            </div>
          </div>
          <div class="mt-4 text-[11px] text-ink-gray-4">
            {{ __('AI-detected from') }} {{ analytics.totalAnalyzed }} {{ __('conversations this week') }}
          </div>
        </div>
      </div>
      <!-- SLA Compliance table -->
      <div class="rounded-[14px] border border-crm-border bg-white p-4 shadow-sm">
        <div class="text-sm font-semibold text-ink-gray-8 mb-3">{{ __('SLA Compliance by Queue') }}</div>
        <table class="w-full text-xs">
          <thead>
            <tr class="border-b border-outline-gray-1 text-ink-gray-4">
              <th class="pb-2 text-left font-medium">{{ __('Queue') }}</th>
              <th class="pb-2 text-right font-medium">{{ __('Total') }}</th>
              <th class="pb-2 text-right font-medium">{{ __('Within SLA') }}</th>
              <th class="pb-2 text-right font-medium">{{ __('Breached') }}</th>
              <th class="pb-2 text-right font-medium">{{ __('Compliance') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in slaTable" :key="q.queue" class="border-b border-outline-gray-1 last:border-0">
              <td class="py-2 text-ink-gray-7">{{ q.queue }}</td>
              <td class="py-2 text-right text-ink-gray-6">{{ q.total }}</td>
              <td class="py-2 text-right text-green-600">{{ q.within }}</td>
              <td class="py-2 text-right text-red-500">{{ q.breached }}</td>
              <td class="py-2 text-right">
                <span
                  class="rounded-full px-2 py-0.5 font-medium"
                  :class="q.pct >= 90 ? 'bg-green-50 text-green-700' : q.pct >= 70 ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-700'"
                >
                  {{ q.pct }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ── MODALS ── -->

  <!-- New Conversation -->
  <div v-if="showConversationForm" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-lg rounded-[16px] bg-white p-6 shadow-xl">
      <div class="flex items-center justify-between mb-4">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('New Conversation') }}</div>
        <button class="text-ink-gray-4 hover:text-ink-gray-7" @click="showConversationForm = false">✕</button>
      </div>
      <div class="grid grid-cols-2 gap-3 text-sm">
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Customer / Company') }}</label>
          <input v-model="form.customer" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" type="text" placeholder="e.g. PT Nusantara Jaya" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Channel') }}</label>
          <select v-model="form.channel" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="ch in ['WhatsApp','Email','SMS','In-App','Voice']" :key="ch" :value="ch">{{ ch }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Priority') }}</label>
          <select v-model="form.priority" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option>Low</option><option>Medium</option><option>High</option>
          </select>
        </div>
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Subject') }}</label>
          <input v-model="form.subject" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" type="text" />
        </div>
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Initial Message') }}</label>
          <textarea v-model="form.message" rows="3" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
        </div>
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Assign To') }}</label>
          <select v-model="form.assignTo" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option value="">{{ __('Auto-route') }}</option>
            <option v-for="rm in rmList" :key="rm" :value="rm">{{ rm }}</option>
          </select>
        </div>
      </div>
      <div class="mt-5 flex items-center justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showConversationForm = false" />
        <Button :label="__('Create')" variant="solid" @click="addConversation" />
      </div>
    </div>
  </div>

  <!-- Transfer Conversation -->
  <div v-if="showTransferDialog" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-sm rounded-[16px] bg-white p-6 shadow-xl">
      <div class="flex items-center justify-between mb-4">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Transfer Conversation') }}</div>
        <button class="text-ink-gray-4" @click="showTransferDialog = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Transfer To') }}</label>
          <select v-model="transferTarget" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2">
            <option v-for="rm in rmList" :key="rm" :value="rm">{{ rm }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Reason') }}</label>
          <textarea v-model="transferNote" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" placeholder="Optional handover note..." />
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showTransferDialog = false" />
        <Button :label="__('Transfer')" variant="solid" @click="doTransfer" />
      </div>
    </div>
  </div>

  <!-- Tag Dialog -->
  <div v-if="showTagDialog" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-sm rounded-[16px] bg-white p-6 shadow-xl">
      <div class="flex items-center justify-between mb-4">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('Manage Tags') }}</div>
        <button class="text-ink-gray-4" @click="showTagDialog = false">✕</button>
      </div>
      <div class="flex flex-wrap gap-2 mb-4">
        <button
          v-for="tag in availableTags"
          :key="tag"
          class="rounded-full border px-3 py-1 text-xs transition-colors"
          :class="activeConv.tags.includes(tag) ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-outline-gray-2 text-ink-gray-5'"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
      <div class="flex gap-2">
        <input v-model="newTag" class="h-8 flex-1 rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="New tag..." @keyup.enter="addCustomTag" />
        <Button :label="__('Add')" variant="subtle" @click="addCustomTag" />
      </div>
      <div class="mt-4 flex justify-end">
        <Button :label="__('Done')" variant="solid" @click="showTagDialog = false" />
      </div>
    </div>
  </div>

  <!-- Voice Call Simulation -->
  <div v-if="showVoiceCall" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-sm rounded-[24px] bg-gray-900 p-8 shadow-2xl text-center text-white">
      <div class="text-lg font-semibold mb-1">{{ activeConv.customer }}</div>
      <div class="text-sm text-gray-400 mb-6">
        {{ voiceCallState === 'calling' ? __('Calling...') : voiceCallState === 'connected' ? callDurationDisplay : __('Call Ended') }}
      </div>
      <div class="mx-auto mb-8 flex h-20 w-20 items-center justify-center rounded-full bg-gray-700 text-3xl">
        📞
      </div>
      <div class="flex items-center justify-center gap-6">
        <button class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-700 text-sm" @click="() => {}">🔇</button>
        <button
          class="flex h-16 w-16 items-center justify-center rounded-full text-xl font-bold transition-colors"
          :class="voiceCallState === 'connected' ? 'bg-red-500' : 'bg-green-500'"
          @click="toggleCall"
        >
          {{ voiceCallState === 'connected' ? '📵' : '📞' }}
        </button>
        <button class="flex h-12 w-12 items-center justify-center rounded-full bg-gray-700 text-sm" @click="() => {}">🔊</button>
      </div>
      <button v-if="voiceCallState === 'ended'" class="mt-6 text-sm text-gray-400 underline" @click="showVoiceCall = false">{{ __('Close') }}</button>
    </div>
  </div>

  <!-- Campaign Form -->
  <div v-if="showCampaignForm" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-xl rounded-[16px] bg-white p-6 shadow-xl">
      <div class="flex items-center justify-between mb-4">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('New Broadcast Campaign') }}</div>
        <button class="text-ink-gray-4" @click="showCampaignForm = false">✕</button>
      </div>
      <div class="grid grid-cols-2 gap-3 text-sm">
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Campaign Name') }}</label>
          <input v-model="campaignForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Channel') }}</label>
          <select v-model="campaignForm.channel" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option>WhatsApp</option><option>SMS</option><option>Email</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Audience Segment') }}</label>
          <select v-model="campaignForm.audience" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option>All Active Customers</option>
            <option>SME Segment</option>
            <option>Enterprise Segment</option>
            <option>Overdue > 30 Days</option>
            <option>Loan Maturity Next 30 Days</option>
          </select>
        </div>
        <div class="col-span-2">
          <label class="text-xs text-ink-gray-5">{{ __('Template') }}</label>
          <select v-model="campaignForm.template" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option v-for="t in allTemplates" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Schedule') }}</label>
          <input v-model="campaignForm.schedule" type="datetime-local" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Send Limit / Day') }}</label>
          <input v-model="campaignForm.limit" type="number" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" placeholder="e.g. 500" />
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showCampaignForm = false" />
        <Button :label="__('Schedule Campaign')" variant="solid" @click="createCampaign" />
      </div>
    </div>
  </div>

  <!-- Template Form -->
  <div v-if="showTemplateForm" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-lg rounded-[16px] bg-white p-6 shadow-xl">
      <div class="flex items-center justify-between mb-4">
        <div class="text-lg font-semibold text-ink-gray-9">{{ __('New Template') }}</div>
        <button class="text-ink-gray-4" @click="showTemplateForm = false">✕</button>
      </div>
      <div class="space-y-3 text-sm">
        <div class="grid grid-cols-3 gap-3">
          <div class="col-span-2">
            <label class="text-xs text-ink-gray-5">{{ __('Template Name') }}</label>
            <input v-model="templateForm.name" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-3 text-sm" />
          </div>
          <div>
            <label class="text-xs text-ink-gray-5">{{ __('Channel') }}</label>
            <select v-model="templateForm.channel" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
              <option>WhatsApp</option><option>Email</option><option>SMS</option><option>All</option>
            </select>
          </div>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Language') }}</label>
          <select v-model="templateForm.language" class="mt-1 h-9 w-full rounded-md border border-outline-gray-2 px-2 text-sm">
            <option>Bahasa Indonesia</option><option>English</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-ink-gray-5">{{ __('Message Body') }} <span class="text-ink-gray-4">(use {{name}}, {{amount}}, etc.)</span></label>
          <textarea v-model="templateForm.body" rows="4" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
        </div>
      </div>
      <div class="mt-5 flex justify-end gap-2">
        <Button :label="__('Cancel')" variant="subtle" @click="showTemplateForm = false" />
        <Button :label="__('Save Template')" variant="solid" @click="saveTemplate" />
      </div>
    </div>
  </div>
  <!-- WhatsApp Connect Dialog -->
  <Dialog v-model="showWhatsAppConnectDialog" :options="{ title: __('Connect WhatsApp Device'), size: 'md' }">
    <template #body-content>
      <div class="flex flex-col items-center justify-center p-6 text-center">
        <template v-if="connecting">
          <div class="h-10 w-10 animate-spin rounded-full border-4 border-emerald-500 border-t-transparent mb-4" />
          <p class="text-sm font-medium text-slate-700">{{ __('Generating dynamic connection pairing QR Code...') }}</p>
        </template>
        <template v-else-if="qrCodeUrl">
          <div class="mb-4 rounded-2xl bg-slate-50 p-4 shadow-inner border border-slate-100 flex items-center justify-center">
            <img :src="qrCodeUrl" class="h-48 w-48 object-contain transition-all hover:scale-105 duration-300" alt="WhatsApp Connection QR Code" />
          </div>
          <h3 class="text-base font-semibold text-slate-800 mb-2">{{ __('Scan QR Code with WhatsApp') }}</h3>
          <p class="text-xs text-slate-500 max-w-sm mb-4 leading-relaxed">
            {{ __('Open WhatsApp on your mobile phone, go to Linked Devices, and scan this QR code to connect and automatically activate the channel.') }}
          </p>
          <div class="flex gap-2">
            <Button variant="solid" :label="__('I have scanned the code')" @click="confirmConnection" />
            <Button variant="outline" :label="__('Cancel')" @click="showWhatsAppConnectDialog = false" />
          </div>
        </template>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Badge, Button, FeatherIcon, usePageMeta, Dialog, call, toast } from 'frappe-ui'
import { computed, ref } from 'vue'

// ── Page navigation ──────────────────────────────────────────
const pages = [
  { key: 'inbox', label: 'Inbox' },
  { key: 'campaigns', label: 'Campaigns' },
  { key: 'templates', label: 'Templates' },
  { key: 'analytics', label: 'Analytics' },
]
const activePage = ref('inbox')

// ── Conversation list state ──────────────────────────────────
const channelTabs = ['All', 'WhatsApp', 'Email', 'SMS', 'In-App', 'Voice']
const search = ref('')
const activeTab = ref('All')
const sortOption = ref('recent')
const selectedIds = ref([])
const selectedId = ref('conv-001')
const composer = ref('')
const selectedTemplate = ref('')
const messageTone = ref('Formal')
const isInternal = ref(false)
const aiSuggestion = ref('')
const autoResponderActive = ref(false)
const isTyping = ref(false)

// ── Modal state ──────────────────────────────────────────────
const showConversationForm = ref(false)
const showTransferDialog = ref(false)
const showTagDialog = ref(false)
const showVoiceCall = ref(false)
const showCampaignForm = ref(false)
const showTemplateForm = ref(false)
const transferTarget = ref('')
const transferNote = ref('')
const newTag = ref('')
const voiceCallState = ref('calling')
const callSeconds = ref(0)
let callTimer = null

const form = ref({ customer: '', channel: 'WhatsApp', priority: 'Medium', subject: '', message: '', assignTo: '' })
const campaignForm = ref({ name: '', channel: 'WhatsApp', audience: 'All Active Customers', template: '', schedule: '', limit: '' })
const templateForm = ref({ name: '', channel: 'WhatsApp', language: 'Bahasa Indonesia', body: '' })

const rmList = ['Dewi Pratama', 'Rizky Andalan', 'Maya Lestari', 'Budi Santoso', 'Siti Rahayu']
const availableTags = ['Credit', 'Urgent', 'Collections', 'Renewal', 'KYC', 'Complaint', 'Disbursement', 'Follow-up']

// ── Conversations data ───────────────────────────────────────
const conversations = ref([
  {
    id: 'conv-001',
    channel: 'WhatsApp',
    customer: 'PT Nusantara Jaya',
    subject: 'Loan application follow-up',
    lastMessage: 'Dokumen sudah kami kirimkan.',
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
    sentiment: 'neutral',
    isRecording: true,
    tags: ['Credit', 'Urgent'],
    context: { segment: 'Enterprise Banking', facility: 'Working Capital Loan', nextAction: 'Call customer by 15:00' },
    messages: [
      { id: 'm-001', direction: 'in', body: 'Selamat pagi, dokumen sudah kami kirimkan.', time: '09:45', status: 'read', sentiment: 'neutral', media: [{ type: 'document', name: 'Laporan_Keuangan.pdf', size: '245 KB' }, { type: 'document', name: 'Invoice_2026.pdf', size: '128 KB' }] },
      { id: 'm-002', direction: 'out', body: 'Terima kasih Bapak/Ibu, kami akan verifikasi dan memberikan update hari ini.', time: '09:50', status: 'read' },
      { id: 'm-003', direction: 'in', body: 'Baik, kami tunggu kabarnya. Apakah ada dokumen tambahan yang diperlukan?', time: '10:00', status: 'read', sentiment: 'neutral' },
      { id: 'm-004', direction: 'out', body: 'Untuk saat ini dokumen sudah cukup. Tim kami sedang memproses.', time: '10:05', status: 'read' },
      { id: 'm-internal', internal: true, direction: 'in', body: 'Noted: Customer sudah follow-up 3x. Prioritaskan review kredit hari ini.', time: '10:10' },
    ],
  },
  {
    id: 'conv-002',
    channel: 'Email',
    customer: 'Sari Logistics',
    subject: 'Revised term sheet request',
    lastMessage: 'We need a revised term sheet by EOD.',
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
    sentiment: 'negative',
    isRecording: false,
    tags: ['Renewal'],
    context: { segment: 'Commercial', facility: 'Revolving Credit — IDR 5B', nextAction: 'Prepare revised proposal' },
    messages: [
      { id: 'm-003a', direction: 'in', body: 'Dear RM,\n\nWe reviewed the term sheet and have some concerns on the interest rate floor. Could you send a revised version by end of day?\n\nRegards,\nAndi - Sari Logistics', time: '08:30', status: 'read', sentiment: 'negative' },
      { id: 'm-004a', direction: 'out', body: 'Dear Pak Andi,\n\nThank you for your feedback. We will prepare a revised term sheet and revert by 17:00 today.\n\nBest regards,\nRizky — BNI CRM Team', time: '08:45', status: 'delivered' },
    ],
  },
  {
    id: 'conv-003',
    channel: 'SMS',
    customer: 'CV Arjuna',
    subject: 'Payment reminder',
    lastMessage: 'Baik, kami bayar hari ini.',
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
    sentiment: 'positive',
    isRecording: false,
    tags: ['Collections'],
    context: { segment: 'SME', facility: 'Invoice Financing — IDR 800M', nextAction: 'Monitor payment confirmation' },
    messages: [
      { id: 'm-005', direction: 'out', body: 'Reminder: Tagihan Anda jatuh tempo hari ini senilai IDR 25.000.000. Mohon segera konfirmasi pembayaran.', time: 'Yesterday 08:00', status: 'read' },
      { id: 'm-006', direction: 'in', body: 'Baik, kami bayar hari ini sebelum jam 15.00.', time: 'Yesterday 08:15', status: 'read', sentiment: 'positive' },
    ],
  },
  {
    id: 'conv-004',
    channel: 'In-App',
    customer: 'Mega Teknik Group',
    subject: 'Inquiry: KPR Fasilitas Baru',
    lastMessage: 'Bisa jadwalkan video call besok?',
    lastTime: '11:30',
    lastTimestamp: Date.now() - 2 * 60 * 1000,
    unread: 3,
    status: 'Open',
    priority: 'High',
    assignedTo: 'Budi Santoso',
    slaStatus: 'At Risk',
    slaTargetMin: 15,
    slaRemainingMin: 4,
    slaPercent: 75,
    routingRule: 'Segment: Enterprise',
    queueName: 'Enterprise Queue',
    sentiment: 'positive',
    isRecording: false,
    tags: ['Credit', 'Follow-up'],
    context: { segment: 'Enterprise Banking', facility: 'New Application — KPR Korporat', nextAction: 'Schedule video call' },
    messages: [
      { id: 'm-007', direction: 'in', body: 'Selamat siang, kami tertarik dengan produk KPR Korporat BNI untuk pembangunan gedung kantor.', time: '11:10', status: 'read', sentiment: 'positive' },
      { id: 'm-008', direction: 'out', body: 'Selamat siang Bapak! Terima kasih atas minatnya. Saya Budi, RM yang akan mendampingi Anda. Boleh saya pelajari kebutuhannya?', time: '11:15', status: 'read' },
      { id: 'm-009', direction: 'in', body: 'Tentu. Kami butuh fasilitas sekitar IDR 30 miliar untuk konstruksi. Bisa jadwalkan video call besok?', time: '11:30', status: 'delivered', sentiment: 'positive' },
    ],
  },
  {
    id: 'conv-005',
    channel: 'Voice',
    customer: 'PT Cahaya Abadi',
    subject: 'Rekaman panggilan — konfirmasi pencairan',
    lastMessage: 'Panggilan selesai (durasi: 08:32)',
    lastTime: 'Yesterday',
    lastTimestamp: Date.now() - 28 * 60 * 60 * 1000,
    unread: 0,
    status: 'Closed',
    priority: 'Medium',
    assignedTo: 'Siti Rahayu',
    slaStatus: '',
    slaTargetMin: 0,
    slaRemainingMin: 0,
    slaPercent: 100,
    routingRule: 'Direct RM',
    queueName: '-',
    sentiment: 'positive',
    isRecording: false,
    tags: ['Disbursement'],
    context: { segment: 'Commercial', facility: 'Term Loan IDR 15B', nextAction: 'Proses pencairan tahap 1' },
    messages: [
      { id: 'm-010', direction: 'in', body: '📞 Inbound call — durasi 08:32\nTopik: Konfirmasi jadwal pencairan tahap 1\nHasil: Customer konfirmasi akan hadir tandatangan akad tanggal 27 Mei 2026', time: 'Yesterday 14:00', status: 'read', sentiment: 'positive' },
      { id: 'm-011', internal: true, direction: 'in', body: 'Action item: Siapkan dokumen akad dan koordinasi dengan tim legal untuk notaris.', time: 'Yesterday 14:10' },
    ],
  },
])

// ── Templates ────────────────────────────────────────────────
const templates = [
  { id: 'wa_followup', channel: 'WhatsApp', name: 'Follow-up Reminder', body: 'Hi {{name}}, kami ingin menindaklanjuti aplikasi Anda. Ada yang bisa kami bantu?', isApproved: true, language: 'Bahasa Indonesia', mergeFields: ['name'] },
  { id: 'wa_docs', channel: 'WhatsApp', name: 'Document Request', body: 'Yth. {{name}}, mohon kirimkan dokumen berikut: {{document_list}}. Terima kasih.', isApproved: true, language: 'Bahasa Indonesia', mergeFields: ['name', 'document_list'] },
  { id: 'wa_payment', channel: 'WhatsApp', name: 'Payment Reminder', body: 'Kepada {{name}}, angsuran sebesar {{amount}} jatuh tempo pada {{due_date}}. Mohon segera lakukan pembayaran.', isApproved: true, language: 'Bahasa Indonesia', mergeFields: ['name', 'amount', 'due_date'] },
  { id: 'email_summary', channel: 'Email', name: 'Meeting Summary', body: 'Dear {{name}},\n\nBerikut ringkasan pertemuan kita:\n{{summary}}\n\nAction items:\n{{action_items}}\n\nSalam,\n{{rm_name}}', isApproved: false, language: 'Bahasa Indonesia', mergeFields: ['name', 'summary', 'action_items', 'rm_name'] },
  { id: 'sms_otp', channel: 'SMS', name: 'OTP Verification', body: 'Kode OTP Anda: {{otp}}. Berlaku 5 menit. Jangan bagikan ke siapapun.', isApproved: true, language: 'Bahasa Indonesia', mergeFields: ['otp'] },
  { id: 'all_welcome', channel: 'All', name: 'Welcome Message', body: 'Selamat datang di layanan BNI CRM, {{name}}. Kami siap membantu kebutuhan perbankan Anda.', isApproved: true, language: 'Bahasa Indonesia', mergeFields: ['name'] },
]
const allTemplates = ref([...templates])

// ── Campaigns data ───────────────────────────────────────────
const campaigns = ref([
  { id: 'camp-001', name: 'Payment Reminder — May 2026', channel: 'WhatsApp', audience: 'Overdue > 30 Days', message: 'Kepada nasabah terhormat, angsuran Anda telah melewati jatuh tempo lebih dari 30 hari...', status: 'Sent', sent: 245, delivered: 238, opened: 201, scheduled: '2026-05-20 08:00' },
  { id: 'camp-002', name: 'Loan Maturity Alert — June', channel: 'SMS', audience: 'Loan Maturity Next 30 Days', message: 'Fasilitas kredit Anda akan jatuh tempo pada bulan Juni 2026. Silakan hubungi RM Anda...', status: 'Scheduled', sent: 0, delivered: 0, opened: 0, scheduled: '2026-06-01 09:00' },
  { id: 'camp-003', name: 'New Product — KPR Korporat', channel: 'Email', audience: 'Enterprise Segment', message: 'Kami dengan bangga memperkenalkan produk KPR Korporat BNI dengan suku bunga kompetitif...', status: 'Draft', sent: 0, delivered: 0, opened: 0, scheduled: '-' },
])

// ── Analytics data ───────────────────────────────────────────
const analytics = { totalAnalyzed: 142 }
const analyticsKpis = [
  { label: 'Total Conversations', value: '847', delta: '+12%' },
  { label: 'Avg First Response', value: '18m', delta: '-3m' },
  { label: 'SLA Compliance', value: '87%', delta: '+5%' },
  { label: 'CSAT Score', value: '4.3', delta: '+0.2' },
  { label: 'Open Tickets', value: '34', delta: '-8' },
]
const channelVolume = [
  { name: 'WhatsApp', count: 412, pct: 49, color: '#22c55e' },
  { name: 'Email', count: 198, pct: 23, color: '#3b82f6' },
  { name: 'SMS', count: 142, pct: 17, color: '#f59e0b' },
  { name: 'In-App', count: 71, pct: 8, color: '#8b5cf6' },
  { name: 'Voice', count: 24, pct: 3, color: '#ec4899' },
]
const rmResponse = [
  { name: 'Dewi Pratama', time: '12m', pct: 60 },
  { name: 'Rizky Andalan', time: '22m', pct: 78 },
  { name: 'Budi Santoso', time: '8m', pct: 32 },
  { name: 'Maya Lestari', time: '35m', pct: 90 },
  { name: 'Siti Rahayu', time: '15m', pct: 55 },
]
const sentimentBreakdown = [
  { emoji: '😊', label: 'Positive', pct: 54, color: '#22c55e' },
  { emoji: '😐', label: 'Neutral', pct: 31, color: '#f59e0b' },
  { emoji: '😟', label: 'Negative', pct: 15, color: '#ef4444' },
]
const slaTable = [
  { queue: 'Priority RM Queue', total: 84, within: 61, breached: 23, pct: 73 },
  { queue: 'Commercial Queue', total: 156, within: 142, breached: 14, pct: 91 },
  { queue: 'Collections Queue', total: 203, within: 198, breached: 5, pct: 98 },
  { queue: 'Enterprise Queue', total: 48, within: 45, breached: 3, pct: 94 },
]

// ── Computed ─────────────────────────────────────────────────
const totalUnread = computed(() =>
  conversations.value.reduce((sum, c) => sum + (c.unread || 0), 0)
)

const allSelected = computed(() => {
  if (!filteredConversations.value.length) return false
  return filteredConversations.value.every((c) => selectedIds.value.includes(c.id))
})

const filteredConversations = computed(() => {
  const q = search.value.trim().toLowerCase()
  const results = conversations.value.filter((c) => {
    const matchTab = activeTab.value === 'All' || c.channel === activeTab.value
    const matchQuery = !q || c.customer.toLowerCase().includes(q) || c.lastMessage.toLowerCase().includes(q)
    return matchTab && matchQuery
  })
  const rank = { High: 3, Medium: 2, Low: 1 }
  return [...results].sort((a, b) => {
    if (sortOption.value === 'unread') return (b.unread || 0) - (a.unread || 0) || b.lastTimestamp - a.lastTimestamp
    if (sortOption.value === 'priority') return (rank[b.priority] || 0) - (rank[a.priority] || 0) || b.lastTimestamp - a.lastTimestamp
    return b.lastTimestamp - a.lastTimestamp
  })
})

const activeConv = computed(() =>
  conversations.value.find((c) => c.id === selectedId.value) || conversations.value[0]
)

const tabCounts = computed(() => {
  const counts = { All: 0, WhatsApp: 0, Email: 0, SMS: 0, 'In-App': 0, Voice: 0 }
  conversations.value.forEach((c) => {
    counts.All += c.unread || 0
    if (counts[c.channel] !== undefined) counts[c.channel] += c.unread || 0
  })
  return counts
})

const bottomMetrics = computed(() => [
  { label: 'Total Conversations', value: conversations.value.length, sub: '+3 today', subColor: 'text-green-600' },
  { label: 'Avg Response', value: '18m', sub: 'SLA: 30m' },
  { label: 'Queue Backlog', value: filteredConversations.value.filter((c) => c.status === 'Open').length },
  { label: 'SLA Breaches', value: conversations.value.filter((c) => c.slaStatus === 'Breached').length, sub: 'needs attention', subColor: 'text-red-500' },
])

const whatsappWindow = computed(() => {
  if (activeConv.value?.channel !== 'WhatsApp') return null
  const lastIn = [...(activeConv.value.messages || [])].filter((m) => m.direction === 'in' && !m.internal).pop()
  if (!lastIn) return null
  const windowMs = 24 * 60 * 60 * 1000
  const elapsed = 3 * 60 * 60 * 1000 // mock: 3h ago
  const remaining = Math.max(0, Math.floor((windowMs - elapsed) / 60000))
  return { isActive: remaining > 0, remainingMinutes: remaining, remainingHours: Math.floor(remaining / 60), isExpiring: remaining < 120 }
})

const callDurationDisplay = computed(() => {
  const m = Math.floor(callSeconds.value / 60).toString().padStart(2, '0')
  const s = (callSeconds.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

// ── Helpers ──────────────────────────────────────────────────
function mergeFieldDisplay(field) { return '{' + '{' + field + '}' + '}' }

function channelIcon(ch) {
  return { WhatsApp: '💬', Email: '📧', SMS: '📱', 'In-App': '💻', Voice: '📞' }[ch] || '📩'
}
function sentimentEmoji(s) {
  return { positive: '😊', neutral: '😐', negative: '😟' }[s] || ''
}
function sentimentLabel(s) {
  return { positive: 'Positive', neutral: 'Neutral', negative: 'Negative' }[s] || ''
}

// ── Actions ──────────────────────────────────────────────────
function selectConversation(id) {
  selectedId.value = id
  aiSuggestion.value = ''
  isInternal.value = false
  const c = conversations.value.find((c) => c.id === id)
  if (c) c.unread = 0
  // Simulate typing for In-App
  if (c?.channel === 'In-App') {
    isTyping.value = true
    setTimeout(() => { isTyping.value = false }, 3000)
  }
}

function toggleSelection(id, event) {
  if (event?.target?.checked) {
    if (!selectedIds.value.includes(id)) selectedIds.value = [...selectedIds.value, id]
  } else {
    selectedIds.value = selectedIds.value.filter((s) => s !== id)
  }
}
function toggleSelectAll(event) {
  const ids = filteredConversations.value.map((c) => c.id)
  if (event?.target?.checked) {
    selectedIds.value = [...new Set([...selectedIds.value, ...ids])]
  } else {
    selectedIds.value = selectedIds.value.filter((id) => !ids.includes(id))
  }
}
function clearSelection() { selectedIds.value = [] }
function isSelected(id) { return selectedIds.value.includes(id) }

function applyTemplate() {
  if (!selectedTemplate.value) return
  const t = allTemplates.value.find((t) => t.id === selectedTemplate.value)
  if (t) composer.value = t.body
  selectedTemplate.value = ''
}

function generateAiSuggestion() {
  const last = [...(activeConv.value.messages || [])].filter((m) => m.direction === 'in' && !m.internal).pop()
  if (!last) return
  const suggestions = {
    WhatsApp: `Terima kasih atas informasinya. Kami akan segera menindaklanjuti dan menghubungi Bapak/Ibu dalam waktu 1 jam kerja. Apakah ada hal lain yang perlu kami bantu?`,
    Email: `Dear Bapak/Ibu,\n\nTerima kasih atas email Anda. Kami telah menerima permintaan Anda dan akan segera memproses. Mohon tunggu konfirmasi dari kami dalam 1x24 jam kerja.\n\nSalam hormat,\nBNI CRM Team`,
    SMS: `Terima kasih. Tim kami akan menghubungi Anda segera.`,
    'In-App': `Terima kasih atas pertanyaannya! Saya akan segera jadwalkan pertemuan. Kapan waktu yang paling nyaman untuk Bapak/Ibu?`,
    Voice: `Catatan panggilan telah dicatat. Tindak lanjut akan dilakukan sesuai hasil diskusi.`,
  }
  aiSuggestion.value = suggestions[activeConv.value.channel] || suggestions.WhatsApp
}

function useAiSuggestion() {
  composer.value = aiSuggestion.value
  aiSuggestion.value = ''
}

function sendMessage() {
  if (!composer.value.trim()) return
  const conv = activeConv.value
  conv.messages.push({
    id: `m-${Date.now()}`,
    direction: isInternal.value ? 'in' : 'out',
    internal: isInternal.value,
    body: composer.value.trim(),
    time: 'Now',
    status: 'sent',
  })
  if (!isInternal.value) {
    conv.lastMessage = composer.value.trim()
    conv.lastTime = 'Now'
    conv.lastTimestamp = Date.now()
  }
  composer.value = ''
  aiSuggestion.value = ''
}

function addConversation() {
  if (!form.value.customer || !form.value.subject) return
  const newConv = {
    id: `conv-${Date.now()}`,
    channel: form.value.channel,
    customer: form.value.customer,
    subject: form.value.subject,
    lastMessage: form.value.message || 'New conversation created',
    lastTime: 'Now',
    lastTimestamp: Date.now(),
    unread: 0,
    status: 'Open',
    priority: form.value.priority,
    assignedTo: form.value.assignTo || 'Auto-Routed',
    slaStatus: 'At Risk',
    slaTargetMin: 60,
    slaRemainingMin: 60,
    slaPercent: 10,
    routingRule: form.value.assignTo ? 'Manual assignment' : 'Auto-route',
    queueName: 'Omnichannel Queue',
    sentiment: 'neutral',
    isRecording: false,
    tags: [],
    context: { segment: 'Prospect', facility: '-', nextAction: 'Assign RM' },
    messages: [{ id: `m-${Date.now()}-init`, direction: 'out', body: form.value.message || 'Conversation started.', time: 'Now', status: 'sent' }],
  }
  conversations.value.unshift(newConv)
  selectedId.value = newConv.id
  form.value = { customer: '', channel: 'WhatsApp', priority: 'Medium', subject: '', message: '', assignTo: '' }
  showConversationForm.value = false
}

function doTransfer() {
  if (!transferTarget.value) return
  const conv = activeConv.value
  const prevRM = conv.assignedTo
  conv.assignedTo = transferTarget.value
  if (transferNote.value) {
    conv.messages.push({ id: `m-${Date.now()}`, internal: true, direction: 'in', body: `Transferred from ${prevRM} to ${transferTarget.value}. Note: ${transferNote.value}`, time: 'Now' })
  }
  transferTarget.value = ''
  transferNote.value = ''
  showTransferDialog.value = false
}

function toggleTag(tag) {
  const conv = activeConv.value
  if (conv.tags.includes(tag)) {
    conv.tags = conv.tags.filter((t) => t !== tag)
  } else {
    conv.tags = [...conv.tags, tag]
  }
}
function addCustomTag() {
  if (!newTag.value.trim()) return
  const conv = activeConv.value
  if (!conv.tags.includes(newTag.value.trim())) conv.tags.push(newTag.value.trim())
  if (!availableTags.includes(newTag.value.trim())) availableTags.push(newTag.value.trim())
  newTag.value = ''
}

function archiveConversation() {
  const conv = activeConv.value
  conv.status = 'Closed'
}

function toggleRecording() {
  const conv = activeConv.value
  conv.isRecording = !conv.isRecording
}

function openVoiceCall() {
  voiceCallState.value = 'calling'
  callSeconds.value = 0
  showVoiceCall.value = true
  setTimeout(() => {
    voiceCallState.value = 'connected'
    callTimer = setInterval(() => { callSeconds.value++ }, 1000)
  }, 2000)
}

function toggleCall() {
  if (voiceCallState.value === 'connected') {
    clearInterval(callTimer)
    voiceCallState.value = 'ended'
    const conv = activeConv.value
    conv.messages.push({ id: `m-${Date.now()}`, direction: 'in', body: `📞 Outbound call ended — duration ${callDurationDisplay.value}`, time: 'Now', status: 'read', sentiment: 'neutral' })
    conv.lastMessage = `Voice call (${callDurationDisplay.value})`
    conv.lastTime = 'Now'
    conv.lastTimestamp = Date.now()
  }
}

function createCampaign() {
  if (!campaignForm.value.name) return
  campaigns.value.unshift({
    id: `camp-${Date.now()}`,
    name: campaignForm.value.name,
    channel: campaignForm.value.channel,
    audience: campaignForm.value.audience,
    message: allTemplates.value.find((t) => t.id === campaignForm.value.template)?.body || '-',
    status: 'Scheduled',
    sent: 0, delivered: 0, opened: 0,
    scheduled: campaignForm.value.schedule || '-',
  })
  campaignForm.value = { name: '', channel: 'WhatsApp', audience: 'All Active Customers', template: '', schedule: '', limit: '' }
  showCampaignForm.value = false
}

function saveTemplate() {
  if (!templateForm.value.name || !templateForm.value.body) return
  allTemplates.value.push({
    id: `tpl-${Date.now()}`,
    ...templateForm.value,
    isApproved: false,
    mergeFields: (templateForm.value.body.match(/\{\{(\w+)\}\}/g) || []).map((m) => m.replace(/[{}]/g, '')),
  })
  templateForm.value = { name: '', channel: 'WhatsApp', language: 'Bahasa Indonesia', body: '' }
  showTemplateForm.value = false
}
const showWhatsAppConnectDialog = ref(false)
const connecting = ref(false)
const qrCodeUrl = ref('')

async function openWhatsAppConnect() {
  showWhatsAppConnectDialog.value = true
  connecting.value = true
  qrCodeUrl.value = ''
  try {
    const uniqueSession = `fcrm_wa_session_${Math.random().toString(36).substring(2, 15)}`
    qrCodeUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&color=059669&data=${encodeURIComponent(uniqueSession)}`
  } catch (err) {
    console.error(err)
    toast.error(__('Failed to generate WhatsApp QR code'))
  } finally {
    connecting.value = false
  }
}

async function confirmConnection() {
  connecting.value = true
  try {
    await call('crm.api.whatsapp.connect_whatsapp_channel')
    toast.success(__('WhatsApp Channel connected and activated successfully!'))
    showWhatsAppConnectDialog.value = false
  } catch (err) {
    toast.error(err?.messages?.[0] || err.message || __('Connection failed'))
  } finally {
    connecting.value = false
  }
}

usePageMeta(() => ({ title: __('Omnichannel Communication') }))
</script>
