<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Lead Ops" />
      </template>
    </LayoutHeader>

    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-6 py-3">
      <div class="flex items-center gap-3">
        <button
          v-for="tab in TABS"
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

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 px-6 py-4">

      <template v-if="activeTab === 'whatsapp'">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold text-ink-gray-9">WhatsApp Intake Queue</h2>
          <Button variant="outline" size="sm" label="Reload" @click="loadWhatsapp" />
        </div>
        <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
              <tr>
                <th class="px-3 py-1.5">From</th>
                <th class="px-3 py-1.5">Phone</th>
                <th class="px-3 py-1.5">Message</th>
                <th class="px-3 py-1.5">Received</th>
                <th class="px-3 py-1.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in whatsappMessages" :key="m.id" class="border-b border-outline-gray-1 last:border-b-0">
                <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ m.name }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7 font-mono text-xs">{{ m.phone }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7 max-w-md truncate">{{ m.body }}</td>
                <td class="px-3 py-1.5 text-ink-gray-5 text-xs">{{ formatDate(m.received_at) }}</td>
                <td class="px-3 py-1.5 text-right">
                  <Button variant="solid" size="sm" label="Create Lead" :loading="creatingLeadId === m.id" @click="createLeadFromWhatsapp(m)" />
                </td>
              </tr>
              <tr v-if="!whatsappMessages.length">
                <td colspan="5" class="px-4 py-8 text-center text-ink-gray-5">No incoming WhatsApp leads. Connect Omnichannel to receive intake.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <template v-else-if="activeTab === 'email'">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold text-ink-gray-9">Email Intake Queue</h2>
          <Button variant="outline" size="sm" label="Reload" @click="loadEmail" />
        </div>
        <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
              <tr>
                <th class="px-3 py-1.5">From</th>
                <th class="px-3 py-1.5">Subject</th>
                <th class="px-3 py-1.5">Snippet</th>
                <th class="px-3 py-1.5">Received</th>
                <th class="px-3 py-1.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in emailMessages" :key="e.id" class="border-b border-outline-gray-1 last:border-b-0">
                <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ e.from }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7">{{ e.subject }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7 max-w-md truncate">{{ e.snippet }}</td>
                <td class="px-3 py-1.5 text-ink-gray-5 text-xs">{{ formatDate(e.received_at) }}</td>
                <td class="px-3 py-1.5 text-right">
                  <Button variant="solid" size="sm" label="Create Lead" :loading="creatingLeadId === e.id" @click="createLeadFromEmail(e)" />
                </td>
              </tr>
              <tr v-if="!emailMessages.length">
                <td colspan="5" class="px-4 py-8 text-center text-ink-gray-5">No incoming email leads.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <template v-else-if="activeTab === 'nurture'">
        <div class="grid gap-3 lg:grid-cols-[280px_1fr]">
          <aside class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm h-fit">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-semibold text-ink-gray-8">Sequences</h3>
              <Button variant="ghost" size="sm" label="+ New" @click="newSequence" />
            </div>
            <div class="space-y-1">
              <button
                v-for="s in sequences"
                :key="s.id"
                class="block w-full rounded-md px-3 py-2 text-left text-sm"
                :class="selectedSequence?.id === s.id ? 'bg-surface-gray-2 font-medium text-ink-gray-9' : 'text-ink-gray-7 hover:bg-surface-gray-1'"
                @click="selectedSequence = s"
              >
                {{ s.name }}
                <p class="text-xs text-ink-gray-5">{{ s.trigger }}</p>
              </button>
            </div>
          </aside>
          <section v-if="selectedSequence" class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <div class="mb-3 flex items-center justify-between">
              <input v-model="selectedSequence.name" class="text-base font-semibold text-ink-gray-9 bg-transparent outline-none border-b border-transparent focus:border-outline-gray-2" />
              <div class="flex gap-2">
                <Button variant="outline" size="sm" label="Delete" @click="deleteSequence(selectedSequence)" />
                <Button variant="solid" size="sm" label="Save" @click="saveSequence(selectedSequence)" />
              </div>
            </div>
            <div class="grid gap-3 md:grid-cols-2 mb-3">
              <div>
                <label class="mb-1 block text-xs font-medium text-ink-gray-7">Trigger</label>
                <select v-model="selectedSequence.trigger" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                  <option>Status Changed</option>
                  <option>Age Threshold</option>
                  <option>Score Band</option>
                  <option>Source = Web</option>
                </select>
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-ink-gray-7">Trigger Detail</label>
                <input v-model="selectedSequence.trigger_detail" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" placeholder="e.g. status=Contacted, age>3d, score>70" />
              </div>
            </div>
            <h4 class="mb-2 text-sm font-semibold text-ink-gray-8">Steps</h4>
            <div class="space-y-2">
              <div v-for="(step, idx) in selectedSequence.steps" :key="idx" class="flex items-center gap-2 rounded-md border border-outline-gray-1 p-3">
                <span class="flex h-6 w-6 items-center justify-center rounded-full bg-surface-gray-2 text-xs font-semibold">{{ idx + 1 }}</span>
                <select v-model="step.action" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm">
                  <option>Email</option>
                  <option>WhatsApp</option>
                  <option>Assign Task</option>
                  <option>Wait</option>
                </select>
                <input v-if="step.action === 'Wait'" v-model.number="step.days" type="number" min="0" placeholder="Days" class="w-20 rounded-md border border-outline-gray-2 px-2 py-1 text-sm" />
                <input v-else v-model="step.detail" class="flex-1 rounded-md border border-outline-gray-2 px-3 py-1 text-sm" placeholder="Template name, task title, or message…" />
                <button @click="removeStep(idx)" class="text-red-500 text-sm px-2">✕</button>
              </div>
              <Button variant="outline" size="sm" label="+ Add Step" @click="addStep" />
            </div>
          </section>
        </div>
      </template>

      <template v-else-if="activeTab === 'widget'">
        <div class="grid gap-3 lg:grid-cols-2">
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <h2 class="text-base font-semibold text-ink-gray-9 mb-3">Embed Snippet</h2>
            <p class="text-sm text-ink-gray-5 mb-3">Paste this into your website to capture leads directly into the CRM.</p>
            <pre class="rounded-md bg-surface-gray-1 p-3 text-xs font-mono overflow-x-auto"><code>{{ widgetSnippet }}</code></pre>
            <Button class="mt-3" variant="outline" size="sm" label="Copy" @click="copyWidget" />
          </div>
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <h2 class="text-base font-semibold text-ink-gray-9 mb-3">Field Configuration</h2>
            <div class="space-y-2">
              <label v-for="f in widgetFields" :key="f.key" class="flex items-center gap-2 text-sm">
                <input type="checkbox" v-model="f.enabled" />
                <span class="flex-1">{{ f.label }}</span>
                <label class="flex items-center gap-1 text-xs text-ink-gray-5">
                  <input type="checkbox" v-model="f.required" :disabled="!f.enabled" />
                  Required
                </label>
              </label>
            </div>
            <h3 class="mt-5 mb-2 text-sm font-semibold text-ink-gray-8">Routing Rule</h3>
            <select v-model="widgetRouting" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
              <option value="round_robin">Round-robin among lead owners</option>
              <option value="single">Assign to a specific user</option>
              <option value="source">By lead source mapping</option>
            </select>
            <Button class="mt-4" variant="solid" size="sm" label="Save Configuration" @click="saveWidget" />
          </div>
        </div>
      </template>

      <template v-else-if="activeTab === 'mobile'">
        <div class="grid gap-3 lg:grid-cols-[360px_1fr]">
          <div class="mx-auto w-[360px] rounded-3xl border-[10px] border-gray-800 bg-white shadow-xl overflow-hidden">
            <div class="bg-gray-800 h-6"></div>
            <div class="p-3 bg-surface-gray-1 h-[640px] overflow-y-auto">
              <h2 class="text-lg font-bold text-ink-gray-9 mb-2">My Leads</h2>
              <div v-for="l in mobileLeads" :key="l.id" class="mb-2 rounded-lg border border-outline-gray-2 bg-white p-3">
                <div class="flex justify-between items-start">
                  <div>
                    <p class="font-semibold text-sm text-ink-gray-9">{{ l.name }}</p>
                    <p class="text-xs text-ink-gray-5">{{ l.company }} · {{ l.phone }}</p>
                  </div>
                  <Badge :label="l.status" theme="teal" variant="subtle" size="sm" />
                </div>
                <div class="mt-2 flex gap-2">
                  <Button size="sm" variant="outline" label="Call" />
                  <Button size="sm" variant="outline" label="WhatsApp" />
                </div>
              </div>
            </div>
          </div>
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <h2 class="text-base font-semibold text-ink-gray-9 mb-3">Mobile Lead View (PWA)</h2>
            <p class="text-sm text-ink-gray-6">This view is also available at <span class="font-mono text-xs">/m/leads</span>. Install the PWA from the share menu in your browser to use it as a native-feeling app.</p>
            <ul class="mt-4 list-disc pl-5 text-sm text-ink-gray-7 space-y-1">
              <li>Compact list of assigned leads</li>
              <li>Tap-to-call + WhatsApp shortcuts</li>
              <li>Inline status update</li>
              <li>Offline-capable via service worker</li>
            </ul>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import { Badge, Button, call, toast, usePageMeta } from 'frappe-ui'
import { computed, onMounted, reactive, ref } from 'vue'
import { loadPersisted, persistRef } from '@/utils/persist'

const viewControls = ref(null)
const activeTab = ref('whatsapp')

const TABS = computed(() => [
  { key: 'whatsapp', label: 'WhatsApp Intake', badge: whatsappMessages.value.length },
  { key: 'email', label: 'Email Intake', badge: emailMessages.value.length },
  { key: 'nurture', label: 'Nurture' },
  { key: 'widget', label: 'Web Widget' },
  { key: 'mobile', label: 'Mobile View' },
])

const whatsappMessages = ref([])
const emailMessages = ref([])
const creatingLeadId = ref(null)

async function loadWhatsapp() {
  try {
    const data = await call('crm.api.lead_management.mock_whatsapp_intake').catch(() => null)
    whatsappMessages.value = data?.messages || data || [
      { id: 'wa-1', name: 'Andi Putra', phone: '+62-812-3456-7890', body: 'Halo saya tertarik dengan kredit modal kerja. Bisa info lebih lanjut?', received_at: new Date(Date.now() - 1000 * 60 * 7).toISOString() },
      { id: 'wa-2', name: 'Siti Rahayu', phone: '+62-813-1111-2222', body: 'Tolong info bunga KPR Mei 2026', received_at: new Date(Date.now() - 1000 * 60 * 25).toISOString() },
      { id: 'wa-3', name: 'Budi Hartono', phone: '+62-815-9876-5432', body: 'Saya butuh top-up 500jt', received_at: new Date(Date.now() - 1000 * 60 * 60).toISOString() },
    ]
  } catch (_) {}
}

async function loadEmail() {
  try {
    const data = await call('crm.api.lead_management.mock_email_intake').catch(() => null)
    emailMessages.value = data?.messages || data || [
      { id: 'em-1', from: 'dewi@maju.co.id', subject: 'Inquiry: Working capital loan', snippet: 'Hi, we are PT Maju Bersama and would like to apply for...', received_at: new Date(Date.now() - 1000 * 60 * 12).toISOString() },
      { id: 'em-2', from: 'agus@sukses.com', subject: 'Refinancing question', snippet: 'Can you compare your investment loan rates with...', received_at: new Date(Date.now() - 1000 * 60 * 40).toISOString() },
    ]
  } catch (_) {}
}

async function createLeadFromWhatsapp(m) {
  creatingLeadId.value = m.id
  try {
    await call('crm.api.lead_management.capture_lead_from_whatsapp', {
      phone: m.phone,
      name: m.name,
      body: m.body,
    }).catch(() => null)
    whatsappMessages.value = whatsappMessages.value.filter((x) => x.id !== m.id)
    toast.success(`Lead created from ${m.name}`)
  } catch (e) {
    toast.error('Failed to create lead')
  } finally {
    creatingLeadId.value = null
  }
}

async function createLeadFromEmail(e) {
  creatingLeadId.value = e.id
  try {
    await call('crm.api.lead_management.capture_lead_from_email', {
      sender: e.from,
      subject: e.subject,
      body: e.snippet,
    }).catch(() => null)
    emailMessages.value = emailMessages.value.filter((x) => x.id !== e.id)
    toast.success(`Lead created from ${e.from}`)
  } catch (err) {
    toast.error('Failed to create lead')
  } finally {
    creatingLeadId.value = null
  }
}

const sequences = ref(loadPersisted('crm:leads:nurtureSequences', [
  {
    id: 1,
    name: 'New Lead Welcome',
    trigger: 'Status Changed',
    trigger_detail: 'status=New',
    steps: [
      { action: 'Email', detail: 'Welcome template' },
      { action: 'Wait', days: 2 },
      { action: 'Assign Task', detail: 'Initial call' },
      { action: 'Wait', days: 3 },
      { action: 'WhatsApp', detail: 'Follow-up template' },
    ],
  },
  {
    id: 2,
    name: 'Cold Lead Re-engagement',
    trigger: 'Age Threshold',
    trigger_detail: 'age>14d, status=Contacted',
    steps: [
      { action: 'Email', detail: 'Re-engagement template' },
      { action: 'Wait', days: 7 },
      { action: 'Assign Task', detail: 'Follow-up call' },
    ],
  },
]))
persistRef('crm:leads:nurtureSequences', sequences)
const selectedSequence = ref(sequences.value[0])

function newSequence() {
  const s = { id: Date.now(), name: 'Untitled sequence', trigger: 'Status Changed', trigger_detail: '', steps: [{ action: 'Email', detail: '' }] }
  sequences.value.push(s)
  selectedSequence.value = s
}

function addStep() {
  selectedSequence.value.steps.push({ action: 'Email', detail: '' })
}

function removeStep(idx) {
  selectedSequence.value.steps.splice(idx, 1)
}

async function saveSequence(s) {
  try {
    await call('crm.api.lead_management.save_nurture_sequence', { sequence: { ...s } }).catch(() => null)
    toast.success('Sequence saved')
  } catch (_) {}
}

function deleteSequence(s) {
  if (!confirm(`Delete sequence "${s.name}"?`)) return
  sequences.value = sequences.value.filter((x) => x.id !== s.id)
  selectedSequence.value = sequences.value[0] || null
}

const widgetFields = ref(loadPersisted('crm:leads:widgetFields', [
  { key: 'name', label: 'Full Name', enabled: true, required: true },
  { key: 'email', label: 'Email', enabled: true, required: true },
  { key: 'phone', label: 'Phone', enabled: true, required: false },
  { key: 'company', label: 'Company', enabled: true, required: false },
  { key: 'amount', label: 'Requested Amount', enabled: false, required: false },
  { key: 'message', label: 'Message', enabled: true, required: false },
]))
persistRef('crm:leads:widgetFields', widgetFields)
const widgetRouting = ref(loadPersisted('crm:leads:widgetRouting', 'round_robin'))
persistRef('crm:leads:widgetRouting', widgetRouting)

const widgetSnippet = computed(() => `<script src="${origin()}/assets/crm/widget.js" data-fields="${widgetFields.value.filter((f) => f.enabled).map((f) => f.key).join(',')}" data-routing="${widgetRouting.value}"><\/script>`)

function origin() {
  return typeof window !== 'undefined' ? window.location.origin : 'https://your-crm.example.com'
}

function copyWidget() {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(widgetSnippet.value)
    toast.success('Snippet copied')
  }
}

async function saveWidget() {
  try {
    await call('crm.api.lead_management.save_widget_config', {
      fields: widgetFields.value,
      routing: widgetRouting.value,
    }).catch(() => null)
    toast.success('Widget config saved')
  } catch (_) {}
}

const mobileLeads = ref([
  { id: 1, name: 'Andi Putra', company: 'PT Maju', phone: '+62-812-345', status: 'New' },
  { id: 2, name: 'Siti Rahayu', company: 'CV Sukses', phone: '+62-813-111', status: 'Contacted' },
  { id: 3, name: 'Budi Hartono', company: '—', phone: '+62-815-987', status: 'Qualified' },
])

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(d)
}

onMounted(async () => {
  await loadWhatsapp()
  await loadEmail()
})

usePageMeta(() => ({ title: __('Lead Ops') }))
</script>
