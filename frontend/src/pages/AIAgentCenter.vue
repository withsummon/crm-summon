<template>
  <div class="flex h-full bg-slate-50 text-slate-900">
    <aside class="w-72 shrink-0 border-r border-slate-200 bg-white">
      <div class="border-b border-slate-200 p-4">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-600 text-white">
            <AIDeskIcon class="h-5 w-5" />
          </div>
          <div>
            <h1 class="text-base font-bold text-slate-900">{{ __('AI Agent Center') }}</h1>
            <p class="text-xs text-slate-500">{{ __('BNI SUMMON agent workspace') }}</p>
          </div>
        </div>
      </div>

      <div class="h-[calc(100%-73px)] overflow-y-auto p-3">
        <button
          v-for="agent in agents"
          :key="agent.key"
          class="mb-2 w-full rounded-lg border p-3 text-left transition-all"
          :class="selectedAgent?.key === agent.key ? 'border-teal-200 bg-teal-50 shadow-sm' : 'border-slate-200 bg-white hover:border-teal-100 hover:bg-slate-50'"
          @click="selectAgent(agent)"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-teal-700">
              <FeatherIcon :name="agent.icon || 'cpu'" class="h-4 w-4" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="truncate text-sm font-semibold text-slate-900">{{ agent.name }}</div>
              <div class="mt-0.5 flex items-center gap-2 text-[11px] text-slate-500">
                <span>{{ agent.model || 'kimi-k2.6' }}</span>
                <span class="h-1 w-1 rounded-full bg-slate-300" />
                <span>${{ formatCost(agent.cost_today) }}</span>
              </div>
            </div>
          </div>
          <div class="mt-2 line-clamp-2 text-xs leading-5 text-slate-500">
            {{ agent.uat?.slice(0, 2).join(' · ') }}
          </div>
        </button>
      </div>
    </aside>

    <main class="flex min-w-0 flex-1 flex-col">
      <LayoutHeader>
        <template #left-header>
          <div>
            <h2 class="text-base font-semibold text-slate-900">{{ selectedAgent?.name || __('AI Agent Center') }}</h2>
            <p class="text-xs text-slate-500">{{ selectedAgent?.role || __('RAG-grounded banking assistant') }}</p>
          </div>
        </template>
        <template #right-header>
          <div class="flex items-center gap-2">
            <Badge :label="`${messages.length} messages`" theme="teal" variant="subtle" />
            <Badge :label="__('Guardrails Active')" theme="emerald" variant="solid">
              <template #prefix><FeatherIcon name="shield" class="h-3.5 w-3.5 mr-1" /></template>
            </Badge>
            <Button variant="outline" size="sm" :label="__('AI Settings')" @click="openAISettings">
              <template #prefix><FeatherIcon name="settings" class="h-4 w-4" /></template>
            </Button>
            <Button variant="outline" size="sm" :label="__('Reindex RAG')" :loading="isReindexing" @click="reindexRag">
              <template #prefix><FeatherIcon name="refresh-cw" class="h-4 w-4" /></template>
            </Button>
            <Button variant="ghost" size="sm" :label="__('Clear')" @click="clearChat">
              <template #prefix><FeatherIcon name="trash-2" class="h-4 w-4" /></template>
            </Button>
          </div>
        </template>
      </LayoutHeader>

      <div class="flex min-h-0 flex-1">
        <section class="flex min-w-0 flex-1 flex-col">
          <div ref="chatContainer" class="min-h-0 flex-1 overflow-y-auto p-6">
            <div v-if="!messages.length" class="mx-auto max-w-3xl py-10">
              <div class="mb-5 flex items-center gap-4 rounded-lg border border-teal-100 bg-white p-5 shadow-sm">
                <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-teal-600 text-white">
                  <FeatherIcon name="cpu" class="h-5 w-5" />
                </div>
                <div>
                  <h3 class="text-lg font-bold text-slate-900">{{ __('Select an agent and ask a banking workflow question') }}</h3>
                  <p class="mt-1 text-sm text-slate-500">{{ __('Answers use indexed CRM and Customer 360 sources. Unsupported facts are blocked by guardrails.') }}</p>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                <button
                  v-for="suggestion in quickSuggestions"
                  :key="suggestion"
                  class="rounded-lg border border-slate-200 bg-white p-4 text-left text-sm font-medium text-slate-700 shadow-sm hover:border-teal-200 hover:bg-teal-50"
                  @click="sendMessage(suggestion)"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>

            <div class="mx-auto max-w-4xl space-y-4">
              <div
                v-for="message in messages"
                :key="message.id"
                class="flex gap-3"
                :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
              >
                <div v-if="message.role === 'assistant'" class="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-teal-600 text-white">
                  <AIDeskIcon class="h-4 w-4" />
                </div>
                <div
                  class="max-w-[82%] rounded-lg border px-4 py-3 shadow-sm"
                  :class="message.role === 'user' ? 'border-teal-700 bg-teal-700 text-white' : 'border-slate-200 bg-white text-slate-800'"
                >
                  <div v-if="message.loading" class="flex items-center gap-2 text-sm text-slate-500">
                    <FeatherIcon name="loader" class="h-4 w-4 animate-spin text-teal-600" />
                    {{ message.statusMessage || __('Memproses analisis terstruktur dengan Kimi K2.6 dan RAG...') }}
                  </div>
                  <div v-else-if="message.role === 'user'" class="whitespace-pre-wrap text-sm leading-6">
                    {{ message.content }}
                  </div>
                  <StructuredResponseCard v-else :response="message.structuredResponse" :fallback="message.content" />

                  <div v-if="message.sources?.length" class="mt-3 border-t border-slate-200 pt-3">
                    <button class="text-xs font-semibold text-teal-700" @click="selectedSources = message.sources">
                      {{ message.sources.length }} {{ __('sources') }}
                    </button>
                  </div>

                  <div v-if="message.actions?.length" class="mt-3 space-y-2">
                    <div v-for="action in message.actions" :key="action.action_id" class="rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                      <div class="font-semibold">{{ __(action.status) }} · {{ action.result?.doctype || action.action_type || action.action_id }}</div>
                      <div class="mt-2 flex gap-2" v-if="action.status === 'Pending Confirmation'">
                        <Button size="sm" variant="solid" :label="__('Confirm')" @click="confirmAction(action)" />
                        <Button size="sm" variant="outline" :label="__('Reject')" @click="rejectAction(action)" />
                      </div>
                      <div class="mt-2 flex gap-2" v-if="action.status === 'Completed' || action.status === 'Confirmed'">
                        <Button
                          v-if="getRouteForAction(action)"
                          size="sm"
                          variant="solid"
                          theme="teal"
                          :label="getActionDocLabel(action)"
                          @click="openActionRecord(action)"
                        >
                          <template #prefix>
                            <FeatherIcon :name="action.result?.doctype === 'File' ? 'download' : action.action_type === 'fire_workflow' ? 'activity' : 'external-link'" class="h-3.5 w-3.5 mr-1" />
                          </template>
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div v-if="message.role === 'assistant' && !message.loading" class="mt-3 flex items-center gap-2 border-t border-slate-200 pt-2">
                    <button class="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-teal-700" @click="submitFeedback(message, 'up')">
                      <FeatherIcon name="thumbs-up" class="h-4 w-4" />
                    </button>
                    <button class="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-red-600" @click="submitFeedback(message, 'down')">
                      <FeatherIcon name="thumbs-down" class="h-4 w-4" />
                    </button>
                    <span class="ml-auto text-[11px] text-slate-400">{{ message.model }} · {{ message.tokens || 0 }} tokens</span>
                  </div>
                </div>
                <div v-if="message.role === 'user'" class="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-700 text-white">
                  <FeatherIcon name="user" class="h-4 w-4" />
                </div>
              </div>
            </div>
          </div>

          <div class="border-t border-slate-200 bg-white p-4">
            <div v-if="attachments.length" class="mx-auto mb-2 flex max-w-4xl flex-wrap gap-2">
              <span v-for="file in attachments" :key="file.name" class="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                {{ file.name }}
              </span>
            </div>
            <form class="mx-auto flex max-w-4xl items-end gap-3" @submit.prevent="sendMessage()">
              <label class="flex h-11 w-11 cursor-pointer items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 hover:border-teal-200 hover:text-teal-700">
                <FeatherIcon name="paperclip" class="h-4 w-4" />
                <input class="hidden" type="file" multiple @change="onFilesSelected" />
              </label>
              <button
                type="button"
                class="flex h-11 w-11 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 hover:border-teal-200 hover:text-teal-700"
                @click="startVoice"
              >
                <FeatherIcon name="mic" class="h-4 w-4" />
              </button>
              <textarea
                v-model="inputMessage"
                class="max-h-32 min-h-11 flex-1 resize-none rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-100"
                :placeholder="__('Ask the selected agent...')"
                rows="1"
                @keydown.enter.exact.prevent="sendMessage()"
              />
              <Button variant="solid" :disabled="!inputMessage.trim() || isLoading" :loading="isLoading" type="submit" :label="__('Send')">
                <template #prefix><FeatherIcon name="send" class="h-4 w-4" /></template>
              </Button>
            </form>
          </div>
        </section>

        <aside class="hidden w-80 shrink-0 border-l border-slate-200 bg-white xl:flex xl:flex-col">
          <div class="flex border-b border-slate-200 px-3 pt-3">
            <button
              v-for="tab in sideTabs"
              :key="tab"
              class="border-b-2 px-3 pb-2 text-xs font-semibold"
              :class="activeSideTab === tab ? 'border-teal-600 text-teal-700' : 'border-transparent text-slate-500'"
              @click="activeSideTab = tab"
            >
              {{ tab }}
            </button>
          </div>
          <div class="min-h-0 flex-1 overflow-y-auto p-4">
            <div v-if="activeSideTab === 'Context'" class="space-y-4">
              <PanelBlock title="Production Scope">
                <ul class="space-y-2 text-xs text-slate-600">
                  <li v-for="item in selectedAgent?.uat || []" :key="item" class="flex gap-2">
                    <FeatherIcon name="check-circle" class="mt-0.5 h-3.5 w-3.5 shrink-0 text-teal-600" />
                    <span>{{ item }}</span>
                  </li>
                </ul>
              </PanelBlock>
              <PanelBlock title="Agent Tools">
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="tool in selectedAgent?.tools || []" :key="tool" class="rounded-md bg-slate-100 px-2 py-1 text-[11px] font-semibold text-slate-600">
                    {{ tool.replaceAll('_', ' ') }}
                  </span>
                </div>
              </PanelBlock>
              <PanelBlock title="Guardrail Status">
                <div class="flex items-center gap-2 text-xs font-semibold text-emerald-700">
                  <FeatherIcon name="shield" class="h-4 w-4 text-emerald-600 animate-pulse" />
                  <span>Hallucination Guardrails: Active</span>
                </div>
                <p class="mt-1 text-[10px] text-slate-500 leading-relaxed">
                  All AI claims are automatically cross-referenced with BNI SUMMON CRM RAG indexes. Unsupported or speculative statements are systematically blocked.
                </p>
              </PanelBlock>
              <PanelBlock title="Sources">
                <div v-if="selectedSources.length" class="space-y-3">
                  <div v-for="source in selectedSources" :key="source.id" class="rounded-lg border border-slate-200 p-3">
                    <div class="text-xs font-bold text-slate-800">{{ source.title }}</div>
                    <div class="mt-1 text-[11px] text-slate-500">{{ source.doctype }} · {{ source.docname }}</div>
                    <p class="mt-2 line-clamp-5 text-xs leading-5 text-slate-600">{{ source.excerpt }}</p>
                  </div>
                </div>
                <p v-else class="text-xs text-slate-500">{{ __('Sources will appear after an answer.') }}</p>
              </PanelBlock>
            </div>

            <div v-else-if="activeSideTab === 'Automation'" class="space-y-4">
              <div class="flex items-center justify-between">
                <h3 class="text-xs font-bold uppercase tracking-wide text-slate-500">{{ __('AI Triggers') }}</h3>
                <Button
                  size="sm"
                  variant="outline"
                  :label="showAddRuleForm ? __('Cancel') : __('Add Trigger')"
                  @click="showAddRuleForm = !showAddRuleForm"
                >
                  <template #prefix>
                    <FeatherIcon :name="showAddRuleForm ? 'x' : 'plus'" class="h-3.5 w-3.5" />
                  </template>
                </Button>
              </div>

              <!-- Add Rule Form -->
              <div v-if="showAddRuleForm" class="rounded-lg border border-teal-100 bg-teal-50/30 p-3 space-y-3">
                <div>
                  <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">{{ __('Rule Title') }}</label>
                  <input
                    v-model="newRule.title"
                    type="text"
                    placeholder="e.g. Auto-prioritize overdue accounts"
                    class="w-full rounded-md border border-slate-200 bg-white p-2 text-xs outline-none focus:border-teal-500"
                  />
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">
                    {{ __('Confidence Threshold') }}: {{ newRule.threshold }}%
                  </label>
                  <input
                    v-model="newRule.threshold"
                    type="range"
                    min="50"
                    max="99"
                    class="w-full h-1 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-teal-600"
                  />
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">{{ __('Action Event') }}</label>
                  <select
                    v-model="newRule.action_type"
                    class="w-full rounded-md border border-slate-200 bg-white p-2 text-xs outline-none focus:border-teal-500"
                  >
                    <option value="create_task">Create CRM Task</option>
                    <option value="create_note">Create CRM Note</option>
                    <option value="create_lead">Create CRM Lead</option>
                    <option value="create_deal">Create CRM Deal</option>
                    <option value="fire_workflow">Fire Workflow Engine</option>
                    <option value="draft_communication">Draft WA/Email</option>
                    <option value="create_recommendation">Add AI Recommendation</option>
                  </select>
                </div>
                <div class="flex items-center justify-between py-1">
                  <span class="text-xs font-medium text-slate-600">{{ __('Requires Approval Gate') }}</span>
                  <input
                    v-model="newRule.requires_approval"
                    type="checkbox"
                    class="h-4 w-4 rounded border-slate-300 text-teal-600 focus:ring-teal-500"
                  />
                </div>
                <Button
                  class="w-full"
                  size="sm"
                  variant="solid"
                  :label="__('Save Automation Trigger')"
                  :loading="isSavingRule"
                  @click="saveRule"
                />
              </div>

              <!-- Rules List -->
              <div v-if="automationRules.length" class="space-y-3">
                <div
                  v-for="rule in automationRules"
                  :key="rule.name"
                  class="rounded-lg border p-3 transition-all"
                  :class="rule.enabled ? 'border-slate-200 bg-white shadow-sm' : 'border-slate-100 bg-slate-50/50 opacity-70'"
                >
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0 flex-1">
                      <div class="text-xs font-bold text-slate-800">{{ rule.title }}</div>
                      <div class="mt-1 flex flex-wrap gap-1">
                        <span class="rounded bg-slate-100 px-1.5 py-0.5 text-[9px] font-semibold text-slate-600">
                          Threshold: {{ Math.round(rule.threshold * 100) }}%
                        </span>
                        <span class="rounded bg-teal-50 px-1.5 py-0.5 text-[9px] font-semibold text-teal-700">
                          {{ rule.action_type.replaceAll('_', ' ') }}
                        </span>
                        <span
                          v-if="rule.requires_approval"
                          class="rounded bg-amber-50 px-1.5 py-0.5 text-[9px] font-semibold text-amber-700"
                        >
                          Approval Required
                        </span>
                      </div>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        v-model="rule.enabled"
                        @change="toggleRule(rule)"
                        class="sr-only peer"
                      />
                      <div class="w-7 h-4 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-teal-600"></div>
                    </label>
                  </div>
                  <div class="mt-2.5 flex justify-end gap-1.5 border-t border-slate-100 pt-2 text-[10px]">
                    <button
                      class="text-red-600 hover:text-red-700 font-semibold"
                      @click="deleteRule(rule.name)"
                    >
                      {{ __('Delete') }}
                    </button>
                  </div>
                </div>
              </div>
              <p v-else-if="!showAddRuleForm" class="text-xs text-slate-500 text-center py-4">
                {{ __('No automation triggers defined for this agent.') }}
              </p>
            </div>

            <div v-else-if="activeSideTab === 'Admin'" class="space-y-4">
              <PanelBlock title="Cost">
                <div class="text-2xl font-black text-slate-900">${{ formatCost(costDashboard.total_cost) }}</div>
                <div class="mt-2 space-y-1">
                  <div v-for="row in costDashboard.rows?.slice(0, 5)" :key="`${row.agent_key}-${row.user}`" class="flex justify-between text-xs text-slate-600">
                    <span>{{ row.agent_key }}</span>
                    <span>${{ formatCost(row.cost) }}</span>
                  </div>
                </div>
              </PanelBlock>
              <PanelBlock title="Sandbox">
                <textarea v-model="sandboxPrompt" rows="5" class="w-full rounded-lg border border-slate-200 p-2 text-xs outline-none focus:border-teal-500" />
                <Button class="mt-2 w-full" size="sm" variant="solid" :label="__('Run Sandbox')" :loading="isSandboxing" @click="runSandbox" />
                <StructuredResponseCard v-if="sandboxResult" class="mt-3" :response="sandboxResult" :fallback="sandboxFallback" compact />
              </PanelBlock>
              <PanelBlock title="RAG">
                <div class="space-y-2 text-xs text-slate-600">
                  <div class="flex justify-between gap-3">
                    <span>{{ __('Status') }}</span>
                    <span class="font-semibold text-slate-800">{{ ragStatus.status || '-' }}</span>
                  </div>
                  <div class="flex justify-between gap-3">
                    <span>{{ __('Fallback chunks') }}</span>
                    <span class="font-mono text-slate-800">{{ ragStatus.chunk_count || 0 }}</span>
                  </div>
                  <div class="flex justify-between gap-3">
                    <span>{{ __('RAGAnything') }}</span>
                    <span class="font-semibold" :class="ragStatus.native_raganything_ready ? 'text-teal-700' : 'text-orange-700'">
                      {{ ragStatus.native_raganything_ready ? __('Ready') : __('Parser missing') }}
                    </span>
                  </div>
                  <p v-if="ragStatus.message" class="leading-5 text-orange-700">{{ ragStatus.message }}</p>
                </div>
              </PanelBlock>
            </div>

            <div v-else class="space-y-3">
              <div v-for="row in auditLog" :key="row.name" class="rounded-lg border border-slate-200 p-3">
                <div class="flex justify-between gap-2 text-xs font-semibold text-slate-800">
                  <span>{{ row.agent_key }}</span>
                  <span>${{ formatCost(row.cost) }}</span>
                </div>
                <p class="mt-2 line-clamp-3 text-xs leading-5 text-slate-500">{{ row.prompt_preview }}</p>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import LayoutHeader from '@/components/LayoutHeader.vue'
import AIDeskIcon from '@/components/Icons/AIDeskIcon.vue'
import StructuredResponseCard from '@/components/AI/StructuredResponseCard.vue'
import { showSettings, activeSettingsPage } from '@/composables/settings'
import { Badge, Button, FeatherIcon, call, toast } from 'frappe-ui'
import { computed, h, nextTick, onMounted, ref, watch } from 'vue'

const router = useRouter()

const agents = ref([])
const selectedAgent = ref(null)
const LEGACY_STORAGE_KEY = 'ai_agent_center_messages'
const messages = ref([])
const inputMessage = ref('')
const sessionId = ref(null)
const isLoading = ref(false)
const isReindexing = ref(false)
const isSandboxing = ref(false)
const attachments = ref([])
const selectedSources = ref([])
const activeSideTab = ref('Context')
const sideTabs = ['Context', 'Automation', 'Admin', 'Audit']
const costDashboard = ref({ total_cost: 0, rows: [] })
const auditLog = ref([])
const ragStatus = ref({})
const sandboxPrompt = ref('Summarize portfolio risk signals from the indexed CRM data.')
const sandboxResult = ref(null)
const sandboxFallback = ref('')
const chatContainer = ref(null)

watch(messages, (newMessages) => {
  persistAgentConversation(newMessages)
}, { deep: true })

const quickSuggestions = computed(() => [
  'Ringkas risiko kredit utama dari data Customer 360.',
  'Susun next-best action untuk relationship manager hari ini.',
  'Identifikasi isu validasi dokumen dan bukti yang kurang.',
  'Buat watchlist early-warning portofolio.',
])

const automationRules = ref([])
const isSavingRule = ref(false)
const showAddRuleForm = ref(false)
const newRule = ref({
  title: '',
  threshold: 80,
  action_type: 'create_task',
  requires_approval: true,
  enabled: true
})

async function loadAutomationRules() {
  if (!selectedAgent.value) return
  try {
    automationRules.value = await call('crm.api.ai_agent_center.get_automation_rules', {
      agent_key: selectedAgent.value.key
    })
  } catch (error) {
    console.error('Failed to load automation rules', error)
  }
}

async function toggleRule(rule) {
  try {
    await call('crm.api.ai_agent_center.toggle_automation_rule', {
      name: rule.name,
      enabled: rule.enabled ? 1 : 0
    })
    toast.success(rule.enabled ? __('Rule enabled') : __('Rule disabled'))
    await loadAutomationRules()
  } catch (error) {
    toast.error(__('Failed to toggle rule'))
    rule.enabled = !rule.enabled
  }
}

async function saveRule() {
  if (!newRule.value.title.trim()) {
    toast.error(__('Rule title is required'))
    return
  }
  isSavingRule.value = true
  try {
    await call('crm.api.ai_agent_center.save_automation_rule', {
      agent_key: selectedAgent.value.key,
      title: newRule.value.title,
      threshold: Number(newRule.value.threshold) / 100,
      action_type: newRule.value.action_type,
      requires_approval: newRule.value.requires_approval ? 1 : 0,
      enabled: newRule.value.enabled ? 1 : 0
    })
    toast.success(__('Automation rule saved'))
    newRule.value = {
      title: '',
      threshold: 80,
      action_type: 'create_task',
      requires_approval: true,
      enabled: true
    }
    showAddRuleForm.value = false
    await loadAutomationRules()
  } catch (error) {
    toast.error(__('Failed to save automation rule'))
  } finally {
    isSavingRule.value = false
  }
}

async function deleteRule(ruleName) {
  if (!confirm(__('Are you sure you want to delete this rule?'))) return
  try {
    await call('crm.api.ai_agent_center.delete_automation_rule', { name: ruleName })
    toast.success(__('Rule deleted'))
    await loadAutomationRules()
  } catch (error) {
    toast.error(__('Failed to delete rule'))
  }
}

function getRouteForAction(action) {
  const doctype = action.result?.doctype || action.payload?.doctype
  const name = action.result?.name || action.result?.docname || action.payload?.docname
  if (!doctype || !name) {
    if (action.action_type === 'fire_workflow' && action.result?.name) {
      return { path: `/lending-risk/workflow-engine/${action.result.name}/monitor` }
    }
    return null
  }
  if (doctype === 'CRM Lead') {
    return { name: 'Lead', params: { leadId: name } }
  }
  if (doctype === 'CRM Deal') {
    return { name: 'Deal', params: { dealId: name } }
  }
  if (doctype === 'Contact') {
    return { name: 'Contact', params: { contactId: name } }
  }
  if (doctype === 'CRM Organization') {
    return { name: 'Organization', params: { organizationId: name } }
  }
  if (doctype === 'CRM Task') {
    return { path: '/crm-core/tasks/view/list' }
  }
  if (doctype === 'File' && action.result?.file_url) {
    return { external: true, url: action.result.file_url }
  }
  return null
}

function openActionRecord(action) {
  const route = getRouteForAction(action)
  if (!route) return
  if (route.external) {
    window.open(route.url, '_blank')
  } else {
    router.push(route)
  }
}

function getActionDocLabel(action) {
  if (action.result?.doctype === 'File') return __('Download Report')
  if (action.action_type === 'fire_workflow') return __('Buka Workflow Monitor')
  const dt = action.result?.doctype || ''
  if (dt === 'CRM Lead') return __('Buka Lead')
  if (dt === 'CRM Deal') return __('Buka Deal')
  if (dt === 'CRM Task') return __('Buka Task')
  return `Buka ${dt || 'Record'}`
}

function selectAgent(agent) {
  persistAgentConversation(messages.value)
  selectedAgent.value = agent
  localStorage.setItem('ai_agent_center_selected_agent', agent.key)
  loadAgentConversation(agent)
  loadAutomationRules()
}

function agentStorageKey(agentKey) {
  return `ai_agent_center_messages:${agentKey || 'general'}`
}

function agentSessionKey(agentKey) {
  return `ai_agent_center_session:${agentKey || 'general'}`
}

function loadAgentConversation(agent) {
  const key = agent?.key || 'general'
  const storedMessages = localStorage.getItem(agentStorageKey(key))
  const legacyMessages = key === 'general' ? localStorage.getItem(LEGACY_STORAGE_KEY) : null
  messages.value = parseStoredMessages(storedMessages || legacyMessages)
  sessionId.value = localStorage.getItem(agentSessionKey(key)) || null
  selectedSources.value = []
}

function parseStoredMessages(raw) {
  try {
    return JSON.parse(raw || '[]').map((message) => ({ ...message, loading: false }))
  } catch {
    return []
  }
}

function persistAgentConversation(nextMessages = messages.value) {
  const key = selectedAgent.value?.key
  if (!key) return
  const toSave = nextMessages.filter((message) => !message.loading)
  localStorage.setItem(agentStorageKey(key), JSON.stringify(toSave))
  if (sessionId.value) localStorage.setItem(agentSessionKey(key), sessionId.value)
  else localStorage.removeItem(agentSessionKey(key))
}

function formatCost(value) {
  return Number(value || 0).toFixed(4)
}

function openAISettings() {
  activeSettingsPage.value = 'AI Settings'
  showSettings.value = true
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  })
}

async function loadAgents() {
  agents.value = await call('crm.api.ai_agent_center.get_agents')
  const selectedKey = localStorage.getItem('ai_agent_center_selected_agent')
  selectedAgent.value = agents.value.find((agent) => agent.key === selectedKey) || agents.value[0]
  loadAgentConversation(selectedAgent.value)
}

async function loadAdminData() {
  try {
    costDashboard.value = await call('crm.api.ai_agent_center.get_cost_dashboard')
    auditLog.value = await call('crm.api.ai_agent_center.get_audit_log')
    ragStatus.value = await call('crm.api.ai_agent_center.get_rag_status')
  } catch (error) {
    console.error('Could not load AI admin data', error)
  }
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

async function streamAgentResponse({ agent, content, loadingId }) {
  const response = await fetch('/api/method/crm.api.ai_agent_center.query_agent_stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || '',
    },
    body: JSON.stringify({
      agent_key: agent.key,
      message: content,
      session_id: sessionId.value,
      attachments: attachments.value.map((file) => ({ name: file.name, size: file.size, type: file.type })),
    }),
  })
  if (!response.ok || !response.body) {
    throw new Error(await response.text())
  }

  const target = messages.value.find((message) => message.id === loadingId)
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
      if (!event || !target) continue
      const payload = event.payload || {}
      if (event.type === 'meta') {
        sessionId.value = payload.session_id || sessionId.value
        persistAgentConversation()
      } else if (event.type === 'sources') {
        target.sources = payload.sources || []
        selectedSources.value = payload.sources || []
      } else if (event.type === 'status') {
        target.statusMessage = payload.message || target.statusMessage
        scrollToBottom()
      } else if (event.type === 'actions') {
        target.actions = payload.actions || []
      } else if (event.type === 'done') {
        target.loading = false
        target.content = payload.response || target.content
        target.structuredResponse = payload.structured_response || null
        target.sources = payload.sources || target.sources || []
        target.actions = payload.actions || target.actions || []
        target.model = payload.model
        target.tokens = payload.tokens
        target.messageId = payload.message_id
        sessionId.value = payload.session_id || sessionId.value
        selectedSources.value = target.sources || []
        persistAgentConversation()
      } else if (event.type === 'error') {
        target.loading = false
        target.content = payload.message || 'AI Agent Center request failed.'
        target.structuredResponse = null
      }
    }
  }
}

async function sendMessage(text) {
  const content = (text || inputMessage.value).trim()
  if (!content || isLoading.value) return
  const agent = selectedAgent.value || agents.value[0]
  messages.value.push({ id: crypto.randomUUID(), role: 'user', content })
  const loadingId = crypto.randomUUID()
  messages.value.push({ id: loadingId, role: 'assistant', content: '', structuredResponse: null, loading: true, statusMessage: __('Mengambil sumber dan konteks...') })
  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()
  try {
    await streamAgentResponse({ agent, content, loadingId })
    attachments.value = []
    await loadAdminData()
  } catch (error) {
    const target = messages.value.find((message) => message.id === loadingId)
    Object.assign(target, { content: error?.messages?.[0] || error.message || 'AI Agent Center request failed.', structuredResponse: null, loading: false })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

function onFilesSelected(event) {
  attachments.value = Array.from(event.target.files || [])
}

function startVoice() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!Recognition) {
    toast.error(__('Voice input is not supported in this browser'))
    return
  }
  const recognition = new Recognition()
  recognition.lang = 'id-ID'
  recognition.onresult = (event) => {
    inputMessage.value = event.results[0][0].transcript
  }
  recognition.start()
}

async function confirmAction(action) {
  await call('crm.api.ai_agent_center.confirm_action', { action_id: action.action_id })
  action.status = 'Confirmed'
  toast.success(__('Action confirmed'))
  await loadAdminData()
}

async function rejectAction(action) {
  await call('crm.api.ai_agent_center.reject_action', { action_id: action.action_id })
  action.status = 'Rejected'
  toast.success(__('Action rejected'))
  await loadAdminData()
}

async function submitFeedback(message, rating) {
  await call('crm.api.ai_agent_center.submit_feedback', { message_id: message.messageId, rating })
  toast.success(__('Feedback recorded'))
}

async function reindexRag() {
  isReindexing.value = true
  try {
    const result = await call('crm.api.ai_agent_center.reindex_rag', {})
    toast.success(__('RAG indexed {0} records', [result.indexed]))
  } finally {
    isReindexing.value = false
  }
}

async function runSandbox() {
  isSandboxing.value = true
  try {
    const result = await call('crm.api.ai_agent_center.run_sandbox', {
      input_payload: { prompt: sandboxPrompt.value, agent_key: selectedAgent.value?.key || 'general' },
    })
    sandboxResult.value = result.structured_response || null
    sandboxFallback.value = result.response || ''
    await loadAdminData()
  } finally {
    isSandboxing.value = false
  }
}

function clearChat() {
  messages.value = []
  sessionId.value = null
  selectedSources.value = []
  const key = selectedAgent.value?.key || 'general'
  localStorage.removeItem(agentStorageKey(key))
  localStorage.removeItem(agentSessionKey(key))
}

const PanelBlock = {
  props: ['title'],
  setup(props, { slots }) {
    return () =>
      h('section', { class: 'rounded-lg border border-slate-200 bg-white p-3' }, [
        h('h3', { class: 'mb-3 text-xs font-bold uppercase tracking-wide text-slate-500' }, props.title),
        slots.default?.(),
      ])
  },
}

onMounted(async () => {
  await loadAgents()
  await loadAdminData()
  await loadAutomationRules()
})
</script>
