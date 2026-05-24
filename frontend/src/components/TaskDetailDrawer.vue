<template>
  <div class="fixed inset-0 z-50 flex">
    <div class="flex-1 bg-black/30" @click="close" />
    <div class="flex h-full w-full max-w-[640px] flex-col border-l border-outline-gray-2 bg-white shadow-xl">
      <!-- Header -->
      <div class="border-b border-outline-gray-2 px-5 py-4">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <input
              v-if="data?.task"
              v-model="titleEdit"
              class="w-full bg-transparent text-lg font-semibold text-ink-gray-9 outline-none focus:border-b focus:border-ink-gray-4"
              @blur="saveTitle"
              @keydown.enter="$event.target.blur()"
            />
            <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-ink-gray-5">
              <span>#{{ data?.task?.name }}</span>
              <span v-if="data?.task?.task_type">· {{ data.task.task_type }}</span>
              <span v-if="data?.task?.reference_doctype">· {{ data.task.reference_label }} {{ data.task.reference_docname }}</span>
            </div>
          </div>
          <button class="rounded p-1 text-ink-gray-5 hover:bg-surface-gray-1" @click="close">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>

        <div v-if="data?.task" class="mt-3 flex flex-wrap items-center gap-2">
          <select
            :value="data.task.status"
            class="rounded-md border border-outline-gray-2 bg-white px-2.5 py-1 text-sm"
            @change="onStatusChange($event.target.value)"
          >
            <option v-for="s in STATUSES" :key="s">{{ s }}</option>
          </select>
          <select
            :value="data.task.priority"
            class="rounded-md border border-outline-gray-2 bg-white px-2.5 py-1 text-sm"
            @change="patchField('priority', $event.target.value)"
          >
            <option v-for="p in PRIORITIES" :key="p">{{ p }}</option>
          </select>
          <Badge v-if="data.task.sla_state" :label="data.task.sla_state" :theme="slaTheme(data.task.sla_state)" variant="subtle" />
          <span v-if="data.task.blocked_reason" class="text-xs text-orange-700">
            <FeatherIcon name="slash" class="inline h-3 w-3" /> {{ data.task.blocked_reason }}
          </span>
        </div>

        <div v-if="data?.task" class="mt-3">
          <div class="flex items-center justify-between text-[11px] text-ink-gray-5">
            <span>{{ data.task.sla_state }}</span>
            <span>{{ formatRemaining(data.task.sla_remaining_seconds) }}</span>
          </div>
          <div class="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-surface-gray-2">
            <div class="h-full rounded-full" :style="`width: ${Math.min(100, data.task.sla_consumed_pct || 0)}%; background: ${slaColor(data.task.sla_state)}`" />
          </div>
        </div>
      </div>

      <!-- Tab strip -->
      <div class="shrink-0 border-b border-outline-gray-1 px-5">
        <div class="flex gap-4 overflow-x-auto">
          <button
            v-for="t in DRAWER_TABS"
            :key="t"
            class="border-b-2 py-2.5 text-sm whitespace-nowrap"
            :class="tab === t ? 'border-ink-gray-8 font-medium text-ink-gray-9' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
            @click="tab = t"
          >
            {{ t }}
          </button>
        </div>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto px-5 py-4">
        <div v-if="taskRes.loading && !data?.task" class="flex h-32 items-center justify-center">
          <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
        </div>

        <template v-else-if="data?.task">
          <!-- Details -->
          <template v-if="tab === 'Details'">
            <div class="space-y-3 text-sm">
              <div class="grid grid-cols-2 gap-3">
                <Field label="Type">
                  <select
                    :value="data.task.task_type || ''"
                    class="w-full rounded-md border border-outline-gray-2 bg-white px-2.5 py-1.5 text-sm"
                    @change="patchField('task_type', $event.target.value || null)"
                  >
                    <option value="">—</option>
                    <option v-for="t in taskTypes" :key="t.name" :value="t.name">{{ t.type_name }}</option>
                  </select>
                </Field>
                <Field label="Due">
                  <input
                    type="datetime-local"
                    :value="toLocalInput(data.task.due_date)"
                    class="w-full rounded-md border border-outline-gray-2 px-2.5 py-1.5 text-sm"
                    @change="patchField('due_date', $event.target.value)"
                  />
                </Field>
              </div>
              <Field label="Assignees">
                <div class="mt-1 flex flex-wrap gap-1.5">
                  <div
                    v-for="a in data.task.assignees || []"
                    :key="a.user"
                    class="flex items-center gap-1.5 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-2 py-1 text-xs"
                  >
                    <Avatar :image="a.user_image" :label="a.full_name" size="xs" />
                    {{ a.full_name }}
                  </div>
                </div>
                <div class="mt-2 max-h-36 overflow-y-auto rounded-md border border-outline-gray-2 bg-white p-1">
                  <label
                    v-for="u in teamUsers"
                    :key="u.name"
                    class="flex cursor-pointer items-center gap-2 rounded px-2 py-1.5 text-sm text-ink-gray-8 hover:bg-surface-gray-1"
                  >
                    <input
                      v-model="assigneePicker"
                      type="checkbox"
                      :value="u.name"
                      class="h-4 w-4 rounded border-outline-gray-3"
                    />
                    <Avatar :image="u.user_image" :label="u.full_name || u.name" size="xs" />
                    <span class="truncate">{{ u.full_name || u.name }}</span>
                  </label>
                </div>
                <Button class="mt-2" size="sm" variant="outline" label="Update assignees" @click="saveAssignees" />
              </Field>
              <Field label="Description">
                <textarea
                  v-model="descEdit"
                  rows="5"
                  class="w-full rounded-md border border-outline-gray-2 px-2.5 py-2 text-sm"
                  @blur="patchField('description', descEdit)"
                />
              </Field>
              <div class="grid grid-cols-2 gap-3 text-xs text-ink-gray-5">
                <div><span class="font-medium">Created:</span> {{ formatDate(data.task.creation) }}</div>
                <div v-if="data.task.started_at"><span class="font-medium">Started:</span> {{ formatDate(data.task.started_at) }}</div>
                <div v-if="data.task.completed_at"><span class="font-medium">Completed:</span> {{ formatDate(data.task.completed_at) }}</div>
                <div v-if="data.task.blocked_at"><span class="font-medium">Blocked:</span> {{ formatDate(data.task.blocked_at) }}</div>
              </div>
            </div>
          </template>

          <!-- Checklist -->
          <template v-else-if="tab === 'Checklist'">
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-ink-gray-5">{{ checklistDone }}/{{ checklistEdit.length }} complete</span>
                <Button size="sm" variant="outline" label="Save" @click="saveChecklist" />
              </div>
              <div class="h-1.5 w-full overflow-hidden rounded-full bg-surface-gray-2">
                <div class="h-full rounded-full" :style="`width: ${checklistPct}%; background: #008C95`" />
              </div>
              <ul class="mt-2 space-y-1">
                <li v-for="(item, i) in checklistEdit" :key="i" class="flex items-center gap-2 rounded border border-outline-gray-1 px-2 py-1.5">
                  <input type="checkbox" v-model="item.done" class="rounded border-outline-gray-3" />
                  <input v-model="item.label" class="flex-1 bg-transparent text-sm outline-none" />
                  <button class="text-ink-gray-4 hover:text-red-500" @click="checklistEdit.splice(i, 1)">
                    <FeatherIcon name="x" class="h-3.5 w-3.5" />
                  </button>
                </li>
              </ul>
              <div class="mt-2 flex gap-2">
                <input v-model="newChecklistLabel" placeholder="Add item…" class="flex-1 rounded-md border border-outline-gray-2 px-2 py-1.5 text-sm" @keydown.enter="addChecklistItem" />
                <Button size="sm" variant="outline" label="Add" @click="addChecklistItem" />
              </div>
            </div>
          </template>

          <!-- Dependencies -->
          <template v-else-if="tab === 'Dependencies'">
            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <h4 class="mb-2 text-xs font-medium uppercase tracking-wide text-ink-gray-5">Blocks</h4>
                <div v-if="!data.dependencies.blocks.length" class="text-sm text-ink-gray-4">None</div>
                <div v-for="d in data.dependencies.blocks" :key="d.name" class="mb-1 flex items-center justify-between rounded border border-outline-gray-1 p-2 text-sm">
                  <span class="truncate">{{ d.task.title }}</span>
                  <Badge :label="d.task.status" theme="gray" variant="subtle" />
                </div>
              </div>
              <div>
                <h4 class="mb-2 text-xs font-medium uppercase tracking-wide text-ink-gray-5">Blocked by</h4>
                <div v-if="!data.dependencies.blocked_by.length" class="text-sm text-ink-gray-4">None</div>
                <div v-for="d in data.dependencies.blocked_by" :key="d.name" class="mb-1 flex items-center justify-between rounded border border-outline-gray-1 p-2 text-sm">
                  <span class="truncate">{{ d.task.title }}</span>
                  <Badge :label="d.task.status" theme="gray" variant="subtle" />
                </div>
              </div>
            </div>
          </template>

          <!-- Time Log -->
          <template v-else-if="tab === 'Time Log'">
            <div class="mb-3 flex items-center justify-between rounded-[10px] border border-outline-gray-2 bg-surface-gray-1 p-3">
              <div class="text-sm">
                <div class="font-medium text-ink-gray-9">{{ formatMinutes(data.task.time_logged_minutes) }} logged</div>
                <div class="text-xs text-ink-gray-5">{{ data.time_logs.filter((t) => t.billable).length }} billable entries</div>
              </div>
              <Button v-if="!runningTimer" size="sm" variant="solid" label="Start timer" @click="startTimer">
                <template #prefix><FeatherIcon name="play" class="h-3.5 w-3.5" /></template>
              </Button>
              <Button v-else size="sm" variant="outline" label="Stop timer" @click="stopTimer">
                <template #prefix><FeatherIcon name="square" class="h-3.5 w-3.5" /></template>
              </Button>
            </div>
            <table class="w-full text-sm">
              <thead class="text-xs uppercase text-ink-gray-5">
                <tr>
                  <th class="py-1 text-left">User</th>
                  <th class="py-1 text-left">Started</th>
                  <th class="py-1 text-right">Min</th>
                  <th class="py-1 text-center">Billable</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="tl in data.time_logs" :key="tl.name" class="border-t border-outline-gray-1">
                  <td class="py-1.5">{{ tl.user_name || tl.user }}</td>
                  <td class="py-1.5">{{ formatDate(tl.started_at) }}</td>
                  <td class="py-1.5 text-right">{{ tl.duration_minutes ? Math.round(tl.duration_minutes) : '—' }}</td>
                  <td class="py-1.5 text-center">{{ tl.billable ? '✓' : '' }}</td>
                </tr>
                <tr v-if="!data.time_logs.length"><td colspan="4" class="py-3 text-center text-ink-gray-4">No time logged.</td></tr>
              </tbody>
            </table>
          </template>

          <!-- Comments -->
          <template v-else-if="tab === 'Comments'">
            <div class="space-y-3">
              <div v-for="c in data.comments" :key="c.name" class="rounded border border-outline-gray-1 p-2 text-sm">
                <div class="flex items-center justify-between text-xs text-ink-gray-5">
                  <span class="font-medium text-ink-gray-7">{{ c.comment_by || c.comment_email }}</span>
                  <span>{{ formatDate(c.creation) }}</span>
                </div>
                <div class="mt-1 text-ink-gray-8" v-html="c.content"></div>
              </div>
              <div v-if="!data.comments.length" class="text-sm text-ink-gray-4">No comments yet.</div>
              <div class="flex gap-2 pt-2">
                <textarea v-model="newComment" rows="2" placeholder="Write a comment… Use @ to mention." class="flex-1 rounded-md border border-outline-gray-2 px-2 py-1.5 text-sm" />
                <Button size="sm" variant="solid" label="Send" :disabled="!newComment.trim()" @click="submitComment" />
              </div>
            </div>
          </template>

          <!-- History -->
          <template v-else-if="tab === 'History'">
            <div v-if="!data.escalations.length" class="text-sm text-ink-gray-4">No history events yet.</div>
            <div v-else class="space-y-2">
              <div v-for="e in data.escalations" :key="e.name" class="rounded border border-outline-gray-1 p-2 text-sm">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <Badge :label="`L${e.level}`" theme="orange" variant="subtle" />
                    <span class="text-ink-gray-8">{{ e.action }}</span>
                    <span v-if="e.recipient_user" class="text-xs text-ink-gray-5">→ {{ e.recipient_user }}</span>
                  </div>
                  <span class="text-xs text-ink-gray-4">{{ formatDate(e.fired_at) }}</span>
                </div>
                <div v-if="e.acknowledged_at" class="mt-1 text-xs text-green-700">
                  Acknowledged by {{ e.acknowledged_by }} · {{ formatDate(e.acknowledged_at) }}
                </div>
                <Button v-else class="mt-1" size="sm" variant="ghost" label="Acknowledge" @click="acknowledge(e.name)" />
              </div>
            </div>
          </template>
        </template>
      </div>
    </div>

    <Dialog v-model="blockedDialog.open" :options="{ title: __('Block this task') }">
      <template #body-content>
        <textarea v-model="blockedDialog.reason" rows="3" placeholder="Why is this blocked?" class="w-full rounded-md border border-outline-gray-2 px-2 py-1.5 text-sm" />
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Block')" :disabled="!blockedDialog.reason.trim()" @click="confirmBlock().then(close)" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, h } from 'vue'
import { Avatar, Badge, Button, Dialog, FeatherIcon, LoadingIndicator, createResource, toast } from 'frappe-ui'

const Field = {
  name: 'Field',
  props: ['label'],
  setup(props, { slots }) {
    return () => h('div', null, [
      h('label', { class: 'text-xs font-medium uppercase tracking-wide text-ink-gray-5' }, props.label),
      h('div', { class: 'mt-1' }, slots.default ? slots.default() : []),
    ])
  },
}

const props = defineProps({
  open: Boolean,
  taskName: { type: [String, Number], default: null },
  teamUsers: { type: Array, default: () => [] },
  taskTypes: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:open', 'changed'])

const DRAWER_TABS = ['Details', 'Checklist', 'Dependencies', 'Time Log', 'Comments', 'History']
const STATUSES = ['Backlog', 'Todo', 'In Progress', 'Blocked', 'Done', 'Canceled']
const PRIORITIES = ['Critical', 'High', 'Medium', 'Low']

const tab = ref('Details')
const titleEdit = ref('')
const descEdit = ref('')
const checklistEdit = ref([])
const newChecklistLabel = ref('')
const assigneePicker = ref([])
const newComment = ref('')
const runningTimer = ref(null)
const blockedDialog = reactive({ open: false, reason: '', targetStatus: 'Blocked' })

const taskRes = createResource({
  url: 'crm.api.tasks.get_task',
  makeParams: () => ({ name: props.taskName }),
})

const data = computed(() => taskRes.data || null)

watch(() => props.taskName, (n) => {
  if (n) {
    taskRes.fetch().then(() => seedEdits())
  }
}, { immediate: true })

function seedEdits() {
  if (!data.value?.task) return
  titleEdit.value = data.value.task.title || ''
  descEdit.value = data.value.task.description || ''
  checklistEdit.value = (data.value.checklist || []).map((c) => ({ ...c }))
  assigneePicker.value = (data.value.task.assignees || []).map((a) => a.user)
  runningTimer.value = (data.value.time_logs || []).find((t) => !t.ended_at) || null
}

function close() { emit('update:open', false) }

async function patchField(field, value) {
  try {
    await createResource({
      url: 'crm.api.tasks.update_task',
      makeParams: () => ({ name: props.taskName, fields: JSON.stringify({ [field]: value }) }),
    }).submit()
    await taskRes.fetch()
    seedEdits()
    emit('changed')
  } catch (e) { toast.error(__('Failed to update ') + field) }
}

async function saveTitle() {
  if (titleEdit.value && titleEdit.value !== data.value.task.title) {
    await patchField('title', titleEdit.value)
  }
}

function onStatusChange(newStatus) {
  if (newStatus === 'Blocked') {
    blockedDialog.reason = ''
    blockedDialog.targetStatus = newStatus
    blockedDialog.open = true
    return
  }
  doTransition(newStatus)
}

async function confirmBlock() {
  await doTransition('Blocked', blockedDialog.reason)
}

async function doTransition(newStatus, blockedReason) {
  try {
    await createResource({
      url: 'crm.api.tasks.transition',
      makeParams: () => ({ task: props.taskName, new_status: newStatus, blocked_reason: blockedReason || null }),
    }).submit()
    await taskRes.fetch(); seedEdits()
    emit('changed')
    toast.success(__('Updated'))
  } catch (e) { toast.error(__('Failed')) }
}

async function saveAssignees() {
  try {
    await createResource({ url: 'crm.api.tasks.set_assignees', makeParams: () => ({ task: props.taskName, users: JSON.stringify(assigneePicker.value) }) }).submit()
    await taskRes.fetch(); seedEdits()
    emit('changed')
    toast.success(__('Assignees updated'))
  } catch (e) { toast.error(__('Failed')) }
}

function addChecklistItem() {
  if (!newChecklistLabel.value.trim()) return
  checklistEdit.value.push({ label: newChecklistLabel.value.trim(), done: 0, position: checklistEdit.value.length })
  newChecklistLabel.value = ''
}

async function saveChecklist() {
  try {
    await createResource({
      url: 'crm.api.tasks.upsert_checklist',
      makeParams: () => ({ task: props.taskName, items: JSON.stringify(checklistEdit.value) }),
    }).submit()
    await taskRes.fetch(); seedEdits()
    toast.success(__('Checklist saved'))
  } catch (e) { toast.error(__('Failed')) }
}

async function startTimer() {
  try {
    await createResource({ url: 'crm.api.tasks.start_timer', makeParams: () => ({ task: props.taskName }) }).submit()
    await taskRes.fetch(); seedEdits()
    toast.success(__('Timer started'))
  } catch (e) { toast.error(__('Failed')) }
}

async function stopTimer() {
  if (!runningTimer.value) return
  try {
    await createResource({ url: 'crm.api.tasks.stop_timer', makeParams: () => ({ time_log: runningTimer.value.name }) }).submit()
    await taskRes.fetch(); seedEdits()
    emit('changed')
    toast.success(__('Timer stopped'))
  } catch (e) { toast.error(__('Failed')) }
}

async function submitComment() {
  try {
    await createResource({ url: 'crm.api.tasks.add_comment', makeParams: () => ({ task: props.taskName, content: newComment.value }) }).submit()
    newComment.value = ''
    await taskRes.fetch(); seedEdits()
  } catch (e) { toast.error(__('Failed')) }
}

async function acknowledge(event) {
  try {
    await createResource({ url: 'crm.api.tasks.acknowledge_escalation', makeParams: () => ({ event }) }).submit()
    await taskRes.fetch()
    toast.success(__('Acknowledged'))
  } catch (e) { toast.error(__('Failed')) }
}

const checklistDone = computed(() => checklistEdit.value.filter((c) => c.done).length)
const checklistPct = computed(() => checklistEdit.value.length ? Math.round((checklistDone.value / checklistEdit.value.length) * 100) : 0)

function formatDate(s) {
  if (!s) return ''
  return new Date(s).toLocaleString('en', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}
function formatMinutes(min) {
  if (!min) return '0m'
  if (min < 60) return `${Math.round(min)}m`
  if (min < 60 * 24) return `${Math.round(min / 60 * 10) / 10}h`
  return `${Math.round(min / (60 * 24))}d`
}
function formatRemaining(s) {
  if (s == null) return ''
  if (s <= 0) return 'Breached'
  if (s < 3600) return `${Math.round(s / 60)}m left`
  if (s < 86400) return `${Math.round(s / 3600)}h left`
  return `${Math.round(s / 86400)}d left`
}
function slaTheme(state) {
  return state === 'Breached' ? 'red' : state === 'Approaching' ? 'orange' : state === 'Paused' ? 'gray' : state === 'Completed' ? 'gray' : 'green'
}
function slaColor(state) {
  return state === 'Breached' ? '#dc2626' : state === 'Approaching' ? '#d97706' : state === 'Paused' ? '#6b7280' : state === 'Completed' ? '#94a3b8' : '#16a34a'
}
function toLocalInput(s) {
  if (!s) return ''
  const d = new Date(s)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>
