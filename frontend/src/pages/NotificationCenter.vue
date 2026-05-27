<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Notification Center" />
      </template>
      <template #right-header>
        <div class="flex shrink-0 items-center gap-3">
          <Button v-if="activeTab === 'inbox'" variant="outline" size="sm" :label="__('Mark All Read')" @click="markAllAsRead">
            <template #prefix><FeatherIcon name="check-circle" class="h-4 w-4" /></template>
          </Button>
          <Button v-if="activeTab === 'inbox'" variant="outline" size="sm" :label="__('Archive All')" @click="archiveAll">
            <template #prefix><FeatherIcon name="archive" class="h-4 w-4" /></template>
          </Button>
          <Button variant="outline" size="sm" :label="__('Preferences')" @click="showPrefs = true">
            <template #prefix><FeatherIcon name="settings" class="h-4 w-4" /></template>
          </Button>
        </div>
      </template>
    </LayoutHeader>

    <div class="shrink-0 overflow-x-auto border-b border-outline-gray-2 bg-surface-white px-10 py-3">
      <div class="flex items-center gap-6">
        <button
          v-for="tab in PAGE_TABS"
          :key="tab.key"
          class="whitespace-nowrap border-b-2 px-1 py-2 text-base leading-5 transition-colors"
          :class="activeTab === tab.key ? 'border-ink-gray-8 font-medium text-ink-gray-9' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          @click="activeTab = tab.key"
        >
          {{ __(tab.label) }}
          <Badge v-if="tab.badge" :label="String(tab.badge)" variant="subtle" theme="teal" size="sm" class="ml-1" />
        </button>
      </div>
    </div>

    <div v-if="activeTab === 'inbox'" class="shrink-0 overflow-x-auto border-b border-outline-gray-2 bg-surface-white px-10 py-3">
      <div class="flex min-w-max items-center justify-start gap-6">
        <button
          v-for="tab in INBOX_TABS"
          :key="tab.key"
          class="whitespace-nowrap border-b-2 px-1 py-2 text-sm leading-5 transition-colors"
          :class="inboxTab === tab.key ? 'border-crm-teal font-medium text-ink-gray-9' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          @click="inboxTab = tab.key"
        >
          {{ __(tab.label) }}
          <Badge v-if="tabBadge(tab) != null" :label="String(tabBadge(tab))" variant="subtle" theme="teal" size="sm" class="ml-1" />
        </button>
        <div class="flex-1"></div>
        <div class="relative">
          <FeatherIcon name="search" class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-gray-4" />
          <input v-model="query" type="text" :placeholder="__('Search notifications…')" class="h-9 w-64 rounded-md border border-outline-gray-2 bg-white pl-9 pr-3 text-sm text-ink-gray-8 outline-none focus:border-crm-teal focus:ring-2 focus:ring-crm-teal/20" />
        </div>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1">
      <div class="w-full px-10 py-6">

        <!-- INBOX -->
        <template v-if="activeTab === 'inbox'">
          <div v-if="loading" class="flex h-48 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>
          <div v-else-if="!filteredNotifications.length" class="flex flex-col items-center justify-center py-16 text-center">
            <FeatherIcon name="inbox" class="mb-3 h-8 w-8 text-ink-gray-3" />
            <p class="text-base font-medium text-ink-gray-8">{{ __('No notifications') }}</p>
            <p class="mt-1 text-sm text-ink-gray-5">{{ __('You have no notifications matching the current filter.') }}</p>
          </div>
          <div v-else class="space-y-2">
            <div
              v-for="n in filteredNotifications"
              :key="n.name"
              class="flex cursor-pointer items-start gap-4 rounded-[14px] border border-outline-gray-2 bg-white p-4 shadow-sm hover:bg-surface-gray-1"
              @click="openNotification(n)"
            >
              <div class="mt-0.5 flex items-center gap-2.5">
                <div class="size-[5px] rounded-full" :class="[n.read ? 'bg-transparent' : 'bg-crm-teal']" />
                <UserAvatar :user="n.from_user.name" size="lg" />
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-medium text-ink-gray-9">{{ n.from_user.full_name }}</span>
                  <Badge :label="labelize(n.type)" theme="teal" variant="subtle" size="sm" />
                  <Badge v-if="n.snoozed_until" :label="`Snoozed · ${formatDate(n.snoozed_until)}`" theme="orange" variant="subtle" size="sm" />
                  <Badge v-if="n.delivery_status" :label="n.delivery_status" :theme="deliveryTheme(n.delivery_status)" variant="subtle" size="sm" />
                  <span v-if="!n.read" class="text-xs text-crm-teal">{{ __('Unread') }}</span>
                </div>
                <p class="mt-1 text-sm text-ink-gray-7" v-html="sanitizeHTML(n.notification_text || n.message || '')" />
                <div class="mt-2 flex items-center gap-3 text-xs text-ink-gray-5">
                  <span>{{ formatDate(n.creation) }}</span>
                  <span v-if="n.reference_doctype && n.reference_name">{{ n.reference_doctype }} · {{ n.reference_name }}</span>
                  <span v-if="n.channel">· {{ n.channel }}</span>
                </div>
              </div>
              <div class="shrink-0 flex items-center gap-1" @click.stop>
                <div class="relative">
                  <Button variant="ghost" size="sm" @click="toggleSnoozeMenu(n)">
                    <template #prefix><FeatherIcon name="clock" class="h-4 w-4 text-ink-gray-5" /></template>
                  </Button>
                  <div v-if="snoozeMenuFor === n.name" class="absolute right-0 z-20 mt-1 w-44 rounded-md border border-outline-gray-2 bg-white py-1 shadow-lg">
                    <button class="block w-full px-3 py-1.5 text-left text-sm hover:bg-surface-gray-1" @click="snoozeNotification(n, 1)">Snooze 1 hour</button>
                    <button class="block w-full px-3 py-1.5 text-left text-sm hover:bg-surface-gray-1" @click="snoozeNotification(n, 4)">Snooze 4 hours</button>
                    <button class="block w-full px-3 py-1.5 text-left text-sm hover:bg-surface-gray-1" @click="snoozeNotification(n, 'tomorrow')">Tomorrow</button>
                    <button v-if="n.snoozed_until" class="block w-full border-t border-outline-gray-1 px-3 py-1.5 text-left text-sm text-red-600 hover:bg-surface-gray-1" @click="unsnoozeNotification(n)">Unsnooze</button>
                  </div>
                </div>
                <Button v-if="!n.read" variant="ghost" size="sm" :label="__('Mark read')" @click="markOneAsRead(n)" />
                <Button variant="ghost" size="sm" @click="deleteNotification(n)">
                  <template #prefix><FeatherIcon name="trash-2" class="h-4 w-4 text-ink-gray-5" /></template>
                </Button>
              </div>
            </div>
          </div>
        </template>

        <!-- RULES -->
        <template v-else-if="activeTab === 'rules'">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h2 class="text-base font-semibold text-ink-gray-9">Notification Rules</h2>
              <p class="text-sm text-ink-gray-5">Trigger an action when an event matches a condition.</p>
            </div>
            <Button variant="solid" size="sm" label="+ New Rule" @click="openRuleEditor(null)" />
          </div>
          <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm overflow-hidden">
            <table class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-4 py-2.5">Name</th>
                  <th class="px-4 py-2.5">Event</th>
                  <th class="px-4 py-2.5">Channels</th>
                  <th class="px-4 py-2.5">Template</th>
                  <th class="px-4 py-2.5">Enabled</th>
                  <th class="px-4 py-2.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in rules" :key="r.id" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-4 py-2.5 font-medium text-ink-gray-9">{{ r.name }}</td>
                  <td class="px-4 py-2.5 text-ink-gray-7">{{ r.event }}</td>
                  <td class="px-4 py-2.5"><Badge v-for="c in r.channels" :key="c" :label="c" theme="teal" variant="subtle" size="sm" class="mr-1" /></td>
                  <td class="px-4 py-2.5 text-ink-gray-7">{{ r.template || '—' }}</td>
                  <td class="px-4 py-2.5"><input type="checkbox" v-model="r.enabled" class="rounded" /></td>
                  <td class="px-4 py-2.5 text-right">
                    <Button variant="ghost" size="sm" label="Edit" @click="openRuleEditor(r)" />
                    <Button variant="ghost" size="sm" label="Delete" @click="deleteRule(r)" />
                  </td>
                </tr>
                <tr v-if="!rules.length">
                  <td colspan="6" class="px-4 py-8 text-center text-ink-gray-5">No rules yet. Click + New Rule to create one.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- TEMPLATES -->
        <template v-else-if="activeTab === 'templates'">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h2 class="text-base font-semibold text-ink-gray-9">Notification Templates</h2>
              <p class="text-sm text-ink-gray-5">Reusable message templates with variables like <code>&#123;&#123;customer&#125;&#125;</code>.</p>
            </div>
            <Button variant="solid" size="sm" label="+ New Template" @click="openTemplateEditor(null)" />
          </div>
          <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm overflow-hidden">
            <table class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-4 py-2.5">Name</th>
                  <th class="px-4 py-2.5">Channel</th>
                  <th class="px-4 py-2.5">Subject</th>
                  <th class="px-4 py-2.5">Variables</th>
                  <th class="px-4 py-2.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in templates" :key="t.id" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-4 py-2.5 font-medium text-ink-gray-9">{{ t.name }}</td>
                  <td class="px-4 py-2.5"><Badge :label="t.channel" theme="teal" variant="subtle" size="sm" /></td>
                  <td class="px-4 py-2.5 text-ink-gray-7">{{ t.subject || '—' }}</td>
                  <td class="px-4 py-2.5 text-ink-gray-5 font-mono text-xs">{{ (t.variables || []).join(', ') || '—' }}</td>
                  <td class="px-4 py-2.5 text-right">
                    <Button variant="ghost" size="sm" label="Edit" @click="openTemplateEditor(t)" />
                    <Button variant="ghost" size="sm" label="Delete" @click="deleteTemplate(t)" />
                  </td>
                </tr>
                <tr v-if="!templates.length">
                  <td colspan="5" class="px-4 py-8 text-center text-ink-gray-5">No templates yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- ANALYTICS -->
        <template v-else-if="activeTab === 'analytics'">
          <div class="grid gap-3 md:grid-cols-4 mb-4">
            <div v-for="kpi in analyticsKPIs" :key="kpi.label" class="rounded-[14px] border border-outline-gray-2 bg-white p-4 shadow-sm">
              <p class="text-xs text-ink-gray-5">{{ kpi.label }}</p>
              <p class="mt-1 text-2xl font-semibold text-ink-gray-9">{{ kpi.value }}</p>
              <p class="text-xs text-ink-gray-5 mt-1">{{ kpi.sub }}</p>
            </div>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
              <h3 class="text-sm font-semibold text-ink-gray-8 mb-3">By Channel</h3>
              <div v-for="c in analyticsByChannel" :key="c.channel" class="mb-3">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-ink-gray-7">{{ c.channel }}</span>
                  <span class="text-ink-gray-5">{{ c.delivered }}/{{ c.sent }} ({{ c.deliveryRate }}%)</span>
                </div>
                <div class="h-2 rounded-full bg-surface-gray-2 overflow-hidden">
                  <div class="h-full rounded-full bg-crm-teal" :style="{ width: c.deliveryRate + '%' }" />
                </div>
              </div>
            </div>
            <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
              <h3 class="text-sm font-semibold text-ink-gray-8 mb-3">By Type</h3>
              <div v-for="t in analyticsByType" :key="t.type" class="mb-3">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-ink-gray-7">{{ t.type }}</span>
                  <span class="text-ink-gray-5">{{ t.opened }}/{{ t.sent }} ({{ t.openRate }}%)</span>
                </div>
                <div class="h-2 rounded-full bg-surface-gray-2 overflow-hidden">
                  <div class="h-full rounded-full bg-blue-500" :style="{ width: t.openRate + '%' }" />
                </div>
              </div>
            </div>
            <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm md:col-span-2">
              <h3 class="text-sm font-semibold text-ink-gray-8 mb-3">Volume (last 14 days)</h3>
              <div class="flex items-end gap-2 h-32">
                <div v-for="(d, i) in analyticsTimeseries" :key="i" class="flex-1 flex flex-col items-center gap-1">
                  <span class="text-[10px] text-ink-gray-5">{{ d.count }}</span>
                  <div class="w-full bg-crm-teal rounded-t" :style="{ height: (d.count / 50 * 100) + '%' }" />
                  <span class="text-[10px] text-ink-gray-4">{{ d.day }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- BROADCAST -->
        <template v-else-if="activeTab === 'broadcast'">
          <div class="grid gap-4 lg:grid-cols-[1fr_320px]">
            <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
              <h2 class="text-base font-semibold text-ink-gray-9 mb-4">New Broadcast</h2>
              <div class="space-y-4">
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Audience Segment</label>
                  <select v-model="broadcast.segment" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm">
                    <option value="all">All customers</option>
                    <option value="active">Active facilities only</option>
                    <option value="overdue">Overdue accounts</option>
                    <option value="new">New leads (last 30 days)</option>
                  </select>
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Channel</label>
                  <div class="flex gap-3">
                    <label v-for="ch in ['Email', 'SMS', 'WhatsApp', 'Push']" :key="ch" class="flex items-center gap-2 text-sm">
                      <input type="checkbox" :checked="broadcast.channels.includes(ch)" @change="toggleBroadcastChannel(ch)" class="rounded" />
                      {{ ch }}
                    </label>
                  </div>
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Template</label>
                  <select v-model="broadcast.template" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm">
                    <option value="">— Custom message —</option>
                    <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Message</label>
                  <textarea v-model="broadcast.message" rows="4" :placeholder="placeholderBroadcast" class="w-full rounded-md border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm" />
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-medium text-ink-gray-7">Schedule</label>
                  <div class="flex items-center gap-2">
                    <label class="flex items-center gap-1 text-sm"><input type="radio" v-model="broadcast.when" value="now" /> Send now</label>
                    <label class="flex items-center gap-1 text-sm"><input type="radio" v-model="broadcast.when" value="later" /> Schedule</label>
                    <input v-if="broadcast.when === 'later'" v-model="broadcast.schedule" type="datetime-local" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm" />
                  </div>
                </div>
                <div class="flex gap-2">
                  <Button variant="solid" :loading="broadcastSending" label="Send Broadcast" @click="sendBroadcast" />
                  <Button variant="outline" label="Save Draft" @click="saveBroadcastDraft" />
                </div>
              </div>
            </div>
            <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
              <h3 class="text-sm font-semibold text-ink-gray-8 mb-3">Recent Broadcasts</h3>
              <div v-for="b in broadcastHistory" :key="b.id" class="mb-3 rounded-md border border-outline-gray-1 p-3">
                <p class="text-sm font-medium text-ink-gray-9">{{ b.subject || b.message.slice(0, 32) + '…' }}</p>
                <p class="text-xs text-ink-gray-5 mt-1">{{ b.segment }} · {{ b.channels.join(', ') }}</p>
                <p class="text-xs text-ink-gray-4">{{ formatDate(b.sent_at) }} · {{ b.delivered }}/{{ b.sent }} delivered</p>
              </div>
              <p v-if="!broadcastHistory.length" class="text-xs text-ink-gray-5">No broadcasts yet.</p>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Preferences Dialog -->
    <Dialog v-model="showPrefs" :options="{ title: __('Notification Preferences') }">
      <template #body-content>
        <div class="space-y-4 text-sm">
          <div class="rounded-md border border-outline-gray-1 p-3 bg-surface-gray-1">
            <p class="font-medium text-ink-gray-8 text-xs uppercase tracking-wider">Digest schedule</p>
            <div class="mt-2 flex items-center gap-3 text-sm">
              <label class="flex items-center gap-2"><input type="checkbox" v-model="digestEnabled" /> Send daily digest at</label>
              <input v-model="digestTime" type="time" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm" :disabled="!digestEnabled" />
            </div>
          </div>
          <div v-for="pref in preferences" :key="pref.type" class="rounded-md border border-outline-gray-1 px-3 py-2">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-ink-gray-8">{{ pref.label }}</p>
                <p class="text-xs text-ink-gray-5">{{ pref.description }}</p>
              </div>
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-3">
              <label class="flex items-center gap-1 text-xs"><input v-model="pref.in_app" type="checkbox" class="rounded" /> {{ __('In-app') }}</label>
              <label class="flex items-center gap-1 text-xs"><input v-model="pref.email" type="checkbox" class="rounded" /> {{ __('Email') }}</label>
              <label class="flex items-center gap-1 text-xs"><input v-model="pref.sms" type="checkbox" class="rounded" /> {{ __('SMS') }}</label>
              <label class="flex items-center gap-1 text-xs"><input v-model="pref.push" type="checkbox" class="rounded" /> {{ __('Push') }}</label>
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="ghost" label="Cancel" @click="close" />
        <Button variant="solid" label="Save" @click="savePreferences().then(close)" />
      </template>
    </Dialog>

    <!-- Rule Editor -->
    <Dialog v-model="showRuleEditor" :options="{ title: editingRule?.id ? 'Edit Rule' : 'New Rule', size: 'xl' }">
      <template #body-content>
        <div class="space-y-3 text-sm">
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-7">Rule Name</label>
            <input v-model="ruleDraft.name" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" placeholder="e.g. SLA Breach Alert" />
          </div>
          <div class="grid gap-3 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-xs font-medium text-ink-gray-7">Event Trigger</label>
              <select v-model="ruleDraft.event" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option v-for="e in EVENTS" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
            <div>
              <label class="mb-1 block text-xs font-medium text-ink-gray-7">Template</label>
              <select v-model="ruleDraft.template" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option value="">— None —</option>
                <option v-for="t in templates" :key="t.id" :value="t.name">{{ t.name }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-7">Condition (JS-like expression)</label>
            <input v-model="ruleDraft.condition" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm font-mono" placeholder="e.g. doc.priority === 'High'" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-7">Channels</label>
            <div class="flex gap-3">
              <label v-for="ch in ['Email', 'In-app', 'SMS', 'WhatsApp', 'Push']" :key="ch" class="flex items-center gap-1 text-sm">
                <input type="checkbox" :checked="ruleDraft.channels.includes(ch)" @change="toggleRuleChannel(ch)" />
                {{ ch }}
              </label>
            </div>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-7">Recipients</label>
            <input v-model="ruleDraft.recipients" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" placeholder="user@example.com, role:Manager, owner" />
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="ghost" label="Cancel" @click="close" />
        <Button variant="solid" label="Save Rule" @click="saveRule().then(close)" />
      </template>
    </Dialog>

    <!-- Template Editor -->
    <Dialog v-model="showTemplateEditor" :options="{ title: editingTemplate?.id ? 'Edit Template' : 'New Template', size: 'xl' }">
      <template #body-content>
        <div class="space-y-3 text-sm">
          <div class="grid gap-3 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-xs font-medium text-ink-gray-7">Name</label>
              <input v-model="templateDraft.name" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="mb-1 block text-xs font-medium text-ink-gray-7">Channel</label>
              <select v-model="templateDraft.channel" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                <option>Email</option>
                <option>SMS</option>
                <option>WhatsApp</option>
                <option>Push</option>
                <option>In-app</option>
              </select>
            </div>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-7">Subject</label>
            <input v-model="templateDraft.subject" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-7">Body (use <code>&#123;&#123;var&#125;&#125;</code> for variables)</label>
            <textarea v-model="templateDraft.body" rows="6" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm font-mono" />
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="ghost" label="Cancel" @click="close" />
        <Button variant="solid" label="Save Template" @click="saveTemplate().then(close)" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import {
  Badge,
  Button,
  Dialog,
  FeatherIcon,
  LoadingIndicator,
  call,
  toast,
  usePageMeta,
} from 'frappe-ui'
import { computed, onMounted, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const viewControls = ref(null)
const activeTab = ref('inbox')
const inboxTab = ref('all')
const query = ref('')
const loading = ref(false)
const notifications = ref([])
const showPrefs = ref(false)
const snoozeMenuFor = ref(null)

const placeholderBroadcast = 'Hello {{customer}}, ...'

const PAGE_TABS = [
  { key: 'inbox', label: 'Inbox' },
  { key: 'rules', label: 'Rules' },
  { key: 'templates', label: 'Templates' },
  { key: 'analytics', label: 'Analytics' },
  { key: 'broadcast', label: 'Broadcast' },
]

const INBOX_TABS = [
  { key: 'all', label: 'All', badge: computed(() => visibleNotifications.value.length) },
  { key: 'unread', label: 'Unread', badge: computed(() => visibleNotifications.value.filter((n) => !n.read).length) },
  { key: 'mentions', label: 'Mentions' },
  { key: 'tasks', label: 'Tasks' },
  { key: 'assignments', label: 'Assignments' },
  { key: 'snoozed', label: 'Snoozed', badge: computed(() => notifications.value.filter((n) => n.snoozed_until && new Date(n.snoozed_until) > new Date()).length) },
]

const EVENTS = [
  'Lead Created',
  'Lead Status Changed',
  'Deal Stage Changed',
  'Task Assigned',
  'Task Overdue',
  'SLA Approaching Breach',
  'SLA Breached',
  'Application Submitted',
  'Approval Required',
  'Document Uploaded',
  'Payment Due',
  'Payment Overdue',
]

function tabBadge(tab) {
  const b = tab.badge
  if (b == null) return null
  return typeof b === 'object' && 'value' in b ? b.value : b
}

const preferences = ref([
  { type: 'Mention', label: 'Mentions', description: 'When someone mentions you', email: true, in_app: true, sms: false, push: false },
  { type: 'Task', label: 'Tasks', description: 'Task assignments and updates', email: true, in_app: true, sms: false, push: true },
  { type: 'Assignment', label: 'Assignments', description: 'Lead/deal assignments', email: true, in_app: true, sms: false, push: false },
  { type: 'WhatsApp', label: 'WhatsApp', description: 'WhatsApp message notifications', email: false, in_app: true, sms: false, push: true },
  { type: 'SLA', label: 'SLA Alerts', description: 'SLA breach warnings', email: true, in_app: true, sms: true, push: true },
])

const digestEnabled = ref(false)
const digestTime = ref('09:00')

const visibleNotifications = computed(() => {
  const now = new Date()
  return notifications.value.filter((n) => !n.snoozed_until || new Date(n.snoozed_until) <= now || inboxTab.value === 'snoozed')
})

const filteredNotifications = computed(() => {
  let rows = visibleNotifications.value
  if (inboxTab.value === 'unread') rows = rows.filter((n) => !n.read)
  if (inboxTab.value === 'mentions') rows = rows.filter((n) => n.type === 'Mention')
  if (inboxTab.value === 'tasks') rows = rows.filter((n) => n.type === 'Task')
  if (inboxTab.value === 'assignments') rows = rows.filter((n) => n.type === 'Assignment')
  if (inboxTab.value === 'snoozed') rows = notifications.value.filter((n) => n.snoozed_until && new Date(n.snoozed_until) > new Date())
  if (query.value) {
    const q = query.value.toLowerCase()
    rows = rows.filter((n) =>
      [n.notification_text, n.message, n.from_user?.full_name, n.reference_name]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q)),
    )
  }
  return rows
})

async function fetchNotifications() {
  loading.value = true
  try {
    const data = await call('crm.api.notifications.get_notifications')
    notifications.value = (data || []).map((n) => ({
      ...n,
      snoozed_until: n.snoozed_until || null,
      delivery_status: n.delivery_status || null,
      channel: n.channel || null,
    }))
  } catch (e) {
    toast.error(__('Failed to load notifications'))
  }
  loading.value = false
}

async function markAllAsRead() {
  try {
    await call('crm.api.notifications.mark_as_read')
    toast.success(__('All marked as read'))
    fetchNotifications()
  } catch (e) {
    toast.error(__('Failed to mark as read'))
  }
}

async function markOneAsRead(n) {
  try {
    await call('crm.api.notifications.mark_as_read', { doc: n.name })
    n.read = true
  } catch (e) {
    toast.error(__('Failed to mark as read'))
  }
}

async function openNotification(n) {
  if (!n.read) await markOneAsRead(n)
  const route = notificationRoute(n)
  if (!route) {
    toast.info(__('This notification is not linked to a CRM record.'))
    return
  }
  router.push(route)
}

async function deleteNotification(n) {
  try {
    await call('crm.api.notifications.delete_notification', { name: n.name })
    notifications.value = notifications.value.filter((item) => item.name !== n.name)
    toast.success(__('Notification deleted'))
  } catch (e) {
    toast.error(__('Failed to delete notification'))
  }
}

function notificationRoute(n) {
  const doctype = n.reference_doctype || n.notification_type_doctype
  const name = n.reference_name || n.notification_type_doc
  if (doctype === 'CRM Deal' && name) return { name: 'Deal', params: { dealId: name }, hash: n.hash || '' }
  if (doctype === 'CRM Lead' && name) return { name: 'Lead', params: { leadId: name }, hash: n.hash || '' }
  if (doctype === 'CRM Task') return { name: 'Tasks', hash: n.hash || '#tasks' }
  return null
}

async function archiveAll() {
  try {
    await call('crm.api.notifications.archive_all_notifications')
    toast.success(__('All notifications archived'))
    fetchNotifications()
  } catch (e) {
    toast.error(__('Failed to archive notifications'))
  }
}

function toggleSnoozeMenu(n) {
  snoozeMenuFor.value = snoozeMenuFor.value === n.name ? null : n.name
}

async function snoozeNotification(n, value) {
  let until = new Date()
  if (value === 'tomorrow') {
    until.setDate(until.getDate() + 1)
    until.setHours(9, 0, 0, 0)
  } else {
    until.setHours(until.getHours() + Number(value))
  }
  n.snoozed_until = until.toISOString()
  snoozeMenuFor.value = null
  try {
    await call('crm.api.notifications.snooze_notification', { name: n.name, until: n.snoozed_until })
  } catch (_) {}
  toast.success('Notification snoozed')
}

async function unsnoozeNotification(n) {
  n.snoozed_until = null
  snoozeMenuFor.value = null
  try {
    await call('crm.api.notifications.unsnooze_notification', { name: n.name })
  } catch (_) {}
}

async function fetchPreferences() {
  try {
    const data = await call('crm.api.notifications.get_preferences')
    if (data) {
      preferences.value.forEach((pref) => {
        const row = data[pref.type]
        if (row) {
          pref.email = Boolean(row.email)
          pref.in_app = Boolean(row.in_app)
          pref.sms = Boolean(row.sms)
          pref.push = Boolean(row.push)
        }
      })
      if (data.digest) {
        digestEnabled.value = !!data.digest.enabled
        digestTime.value = data.digest.time || '09:00'
      }
    }
  } catch (e) {}
}

async function savePreferences() {
  try {
    await call('crm.api.notifications.save_preferences', {
      preferences: preferences.value,
      digest: { enabled: digestEnabled.value, time: digestTime.value },
    })
    toast.success(__('Preferences saved'))
  } catch (e) {
    toast.error(__('Failed to save preferences'))
  }
}

const rules = ref([
  { id: 1, name: 'SLA Breach Alert', event: 'SLA Breached', condition: '', channels: ['Email', 'In-app', 'SMS'], recipients: 'owner, role:Manager', template: 'SLA Breach', enabled: true },
  { id: 2, name: 'New Lead Assignment', event: 'Lead Created', condition: '', channels: ['Email', 'In-app'], recipients: 'owner', template: 'Lead Welcome', enabled: true },
  { id: 3, name: 'Approval Required', event: 'Approval Required', condition: 'doc.amount > 1000000000', channels: ['Email', 'WhatsApp'], recipients: 'role:Approver', template: '', enabled: true },
])

const showRuleEditor = ref(false)
const editingRule = ref(null)
const ruleDraft = reactive({ id: null, name: '', event: 'Lead Created', condition: '', channels: ['Email'], recipients: '', template: '', enabled: true })

function openRuleEditor(r) {
  editingRule.value = r
  if (r) {
    Object.assign(ruleDraft, r)
    ruleDraft.channels = [...r.channels]
  } else {
    Object.assign(ruleDraft, { id: null, name: '', event: 'Lead Created', condition: '', channels: ['Email'], recipients: '', template: '', enabled: true })
  }
  showRuleEditor.value = true
}

function toggleRuleChannel(ch) {
  const idx = ruleDraft.channels.indexOf(ch)
  if (idx >= 0) ruleDraft.channels.splice(idx, 1)
  else ruleDraft.channels.push(ch)
}

async function saveRule() {
  if (!ruleDraft.name) {
    toast.error('Name is required')
    return
  }
  try {
    await call('crm.api.notifications.save_rule', { rule: { ...ruleDraft } }).catch(() => null)
  } catch (_) {}
  if (ruleDraft.id) {
    const idx = rules.value.findIndex((r) => r.id === ruleDraft.id)
    if (idx >= 0) rules.value.splice(idx, 1, { ...ruleDraft, channels: [...ruleDraft.channels] })
  } else {
    rules.value.push({ ...ruleDraft, id: Date.now(), channels: [...ruleDraft.channels] })
  }
  toast.success('Rule saved')
}

async function deleteRule(r) {
  if (!confirm(`Delete rule "${r.name}"?`)) return
  rules.value = rules.value.filter((x) => x.id !== r.id)
  try { await call('crm.api.notifications.delete_rule', { id: r.id }) } catch (_) {}
}

const templates = ref([
  { id: 1, name: 'SLA Breach', channel: 'Email', subject: 'SLA Breached on {{ref}}', body: 'The SLA on {{ref}} has been breached.', variables: ['ref', 'owner'] },
  { id: 2, name: 'Lead Welcome', channel: 'Email', subject: 'Welcome to BNI', body: 'Hi {{name}}, welcome.', variables: ['name'] },
  { id: 3, name: 'Payment Reminder', channel: 'SMS', subject: '', body: 'Hi {{name}}, your payment of {{amount}} is due {{due_date}}.', variables: ['name', 'amount', 'due_date'] },
])

const showTemplateEditor = ref(false)
const editingTemplate = ref(null)
const templateDraft = reactive({ id: null, name: '', channel: 'Email', subject: '', body: '', variables: [] })

function openTemplateEditor(t) {
  editingTemplate.value = t
  if (t) {
    Object.assign(templateDraft, t)
    templateDraft.variables = [...(t.variables || [])]
  } else {
    Object.assign(templateDraft, { id: null, name: '', channel: 'Email', subject: '', body: '', variables: [] })
  }
  showTemplateEditor.value = true
}

async function saveTemplate() {
  if (!templateDraft.name) {
    toast.error('Name is required')
    return
  }
  const vars = [...new Set([...(String(templateDraft.body).match(/\{\{([^}]+)\}\}/g) || []).map((m) => m.slice(2, -2).trim())])]
  templateDraft.variables = vars
  try {
    await call('crm.api.notifications.save_template', { template: { ...templateDraft } }).catch(() => null)
  } catch (_) {}
  if (templateDraft.id) {
    const idx = templates.value.findIndex((t) => t.id === templateDraft.id)
    if (idx >= 0) templates.value.splice(idx, 1, { ...templateDraft })
  } else {
    templates.value.push({ ...templateDraft, id: Date.now() })
  }
  toast.success('Template saved')
}

async function deleteTemplate(t) {
  if (!confirm(`Delete template "${t.name}"?`)) return
  templates.value = templates.value.filter((x) => x.id !== t.id)
  try { await call('crm.api.notifications.delete_template', { id: t.id }) } catch (_) {}
}

const analyticsKPIs = computed(() => [
  { label: 'Sent (7d)', value: 1284, sub: '+12% vs prev' },
  { label: 'Delivered', value: '94.5%', sub: '1213 / 1284' },
  { label: 'Opened', value: '38.2%', sub: '463 / 1213' },
  { label: 'Failed', value: 71, sub: '5.5%' },
])

const analyticsByChannel = computed(() => [
  { channel: 'Email', sent: 720, delivered: 695, deliveryRate: 96 },
  { channel: 'In-app', sent: 380, delivered: 380, deliveryRate: 100 },
  { channel: 'SMS', sent: 124, delivered: 108, deliveryRate: 87 },
  { channel: 'WhatsApp', sent: 40, delivered: 30, deliveryRate: 75 },
  { channel: 'Push', sent: 20, delivered: 18, deliveryRate: 90 },
])

const analyticsByType = computed(() => [
  { type: 'Mention', sent: 220, opened: 165, openRate: 75 },
  { type: 'Task', sent: 480, opened: 192, openRate: 40 },
  { type: 'Assignment', sent: 200, opened: 80, openRate: 40 },
  { type: 'SLA Alert', sent: 80, opened: 64, openRate: 80 },
  { type: 'Broadcast', sent: 304, opened: 60, openRate: 20 },
])

const analyticsTimeseries = computed(() =>
  Array.from({ length: 14 }, (_, i) => ({
    day: `D-${13 - i}`,
    count: 20 + Math.round(Math.sin(i / 2) * 8 + Math.random() * 15),
  })),
)

const broadcast = reactive({ segment: 'all', channels: ['Email'], template: '', message: '', when: 'now', schedule: '' })
const broadcastSending = ref(false)
const broadcastHistory = ref([
  { id: 1, subject: 'New year campaign 2026', message: 'Happy new year ...', segment: 'all', channels: ['Email'], sent: 1240, delivered: 1180, sent_at: '2026-01-01T08:00:00' },
])

function toggleBroadcastChannel(ch) {
  const idx = broadcast.channels.indexOf(ch)
  if (idx >= 0) broadcast.channels.splice(idx, 1)
  else broadcast.channels.push(ch)
}

async function sendBroadcast() {
  if (!broadcast.message || !broadcast.channels.length) {
    toast.error('Pick at least one channel and write a message')
    return
  }
  broadcastSending.value = true
  try {
    const res = await call('crm.api.notifications.send_broadcast', { broadcast: { ...broadcast } }).catch(() => null)
    broadcastHistory.value.unshift({
      id: Date.now(),
      subject: broadcast.message.slice(0, 60),
      message: broadcast.message,
      segment: broadcast.segment,
      channels: [...broadcast.channels],
      sent: res?.sent || 100,
      delivered: res?.delivered || 95,
      sent_at: new Date().toISOString(),
    })
    toast.success('Broadcast sent')
    broadcast.message = ''
  } catch (e) {
    toast.error('Broadcast failed')
  } finally {
    broadcastSending.value = false
  }
}

function saveBroadcastDraft() {
  toast.success('Draft saved')
}

function deliveryTheme(status) {
  return { delivered: 'green', sent: 'blue', queued: 'gray', failed: 'red', bounced: 'red' }[String(status).toLowerCase()] || 'gray'
}

function sanitizeHTML(html) {
  if (!html) return ''
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

function labelize(value) {
  if (!value) return '—'
  return String(value).replace(/[_-]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

onMounted(async () => {
  await fetchNotifications()
  await fetchPreferences()
  if (!notifications.value.length) {
    try {
      await call('crm.api.notifications.seed_notification_sample_data')
      await fetchNotifications()
    } catch (e) {}
  }
})
usePageMeta(() => ({ title: __('Notification Center') }))
</script>
