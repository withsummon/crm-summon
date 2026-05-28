<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-50 flex justify-end">
      <button
        class="absolute inset-0 bg-black/30"
        :aria-label="__('Close lead scoring')"
        @click="emit('update:visible', false)"
      />
      <aside class="relative flex h-full w-full max-w-[520px] flex-col bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-outline-gray-2 px-5 py-4">
          <div class="text-base font-semibold text-ink-gray-9">{{ __('Lead Scoring') }}</div>
          <Button variant="ghost" icon="x" @click="emit('update:visible', false)" />
        </div>
        <div v-if="loading" class="flex h-40 items-center justify-center">
          <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
        </div>
        <div v-else-if="summary" class="flex-1 space-y-5 overflow-y-auto p-4">
          <div class="rounded-[14px] border border-outline-gray-2 bg-surface-gray-1 p-4">
            <div class="flex items-center justify-between">
              <div>
                <div class="text-xs text-ink-gray-5">{{ __('Score') }}</div>
                <div class="text-3xl font-bold text-ink-gray-9">{{ summary.score?.value || 0 }}</div>
              </div>
              <Badge
                :label="summary.score?.band || 'Cold'"
                variant="subtle"
                :theme="bandTheme(summary.score?.band)"
                size="lg"
              />
            </div>
            <div class="mt-2 text-xs text-ink-gray-5">
              {{ __('Probability') }}: {{ summary.score?.probability || 0 }}% · {{ __('Confidence') }}: {{ summary.score?.confidence || 0 }}%
            </div>
          </div>

          <div v-if="rules.length">
            <div class="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-gray-5">{{ __('Rule Breakdown') }}</div>
            <div class="space-y-2">
              <div
                v-for="rule in rules"
                :key="rule.name"
                class="flex items-center justify-between rounded border border-outline-gray-1 bg-white px-3 py-2 text-sm"
              >
                <span class="text-ink-gray-8">{{ rule.rule_name }}</span>
                <div class="flex items-center gap-2">
                  <span class="text-xs text-ink-gray-5">{{ rule.weight }} pts</span>
                  <FeatherIcon
                    v-if="rule.matched"
                    name="check"
                    class="h-3.5 w-3.5 text-green-600"
                  />
                  <FeatherIcon v-else name="minus" class="h-3.5 w-3.5 text-ink-gray-3" />
                </div>
              </div>
            </div>
          </div>

          <div>
            <div class="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-gray-5">{{ __('AI Quality Prediction') }}</div>
            <div class="rounded border border-outline-gray-1 bg-white p-3 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-ink-gray-7">{{ __('Predicted conversion probability') }}</span>
                <span class="font-semibold text-ink-gray-9">{{ summary.score?.probability || 0 }}%</span>
              </div>
              <div class="mt-1 flex items-center justify-between">
                <span class="text-ink-gray-7">{{ __('Model confidence') }}</span>
                <span class="font-semibold text-ink-gray-9">{{ summary.score?.confidence || 0 }}%</span>
              </div>
            </div>
          </div>

          <div>
            <div class="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-gray-5">{{ __('Manual Override') }}</div>
            <div class="space-y-2">
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('New Band') }}</label>
                  <select v-model="overrideBand" class="mt-1 w-full rounded border border-outline-gray-2 px-2 py-1.5 text-sm">
                    <option value="">{{ __('No override') }}</option>
                    <option value="Cold">Cold</option>
                    <option value="Warm">Warm</option>
                    <option value="Hot">Hot</option>
                  </select>
                </div>
                <div>
                  <label class="text-xs text-ink-gray-5">{{ __('New Score') }}</label>
                  <input v-model.number="overrideScore" type="number" min="0" max="100" class="mt-1 w-full rounded border border-outline-gray-2 px-2 py-1.5 text-sm" />
                </div>
              </div>
              <div>
                <label class="text-xs text-ink-gray-5">{{ __('Reason') }}</label>
                <textarea v-model="overrideReason" rows="2" class="mt-1 w-full rounded border border-outline-gray-2 px-2 py-1.5 text-sm" :placeholder="__('Required when overriding…')"></textarea>
              </div>
              <Button
                size="sm"
                variant="solid"
                :disabled="!canOverride"
                @click="applyOverride"
              >
                {{ __('Apply Override') }}
              </Button>
            </div>
          </div>

          <Button class="w-full" variant="outline" @click="rerunScoring">
            <template #prefix><FeatherIcon name="refresh-cw" class="h-4 w-4" /></template>
            {{ __('Rerun Scoring Engine') }}
          </Button>
        </div>
      </aside>
    </div>
  </Teleport>
</template>

<script setup>
import { Badge, Button, FeatherIcon, LoadingIndicator, createResource, call, toast } from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  leadName: { type: String, default: '' },
})

const emit = defineEmits(['update:visible', 'changed'])

const loading = ref(false)
const rules = ref([])
const overrideBand = ref('')
const overrideScore = ref(0)
const overrideReason = ref('')

const summary = createResource({
  url: 'crm.api.lead_management.get_lead_summary',
  makeParams: () => ({ lead: props.leadName }),
})

watch(() => props.visible, async (val) => {
  if (!val || !props.leadName) return
  loading.value = true
  try {
    await summary.fetch()
    await loadRules()
  } catch (e) {
    toast.error(__('Failed to load scoring data'))
  } finally {
    loading.value = false
  }
})

async function loadRules() {
  if (!frappe.db?.table_exists || !frappe.db.table_exists('CRM Lead Scoring Rule')) {
    rules.value = []
    return
  }
  const activeModel = await call('frappe.client.get_value', {
    doctype: 'CRM Lead Scoring Model',
    filters: { is_active: 1 },
    fieldname: 'name',
  })
  if (!activeModel?.name) {
    rules.value = []
    return
  }
  const model = await call('frappe.client.get_doc', { doctype: 'CRM Lead Scoring Model', name: activeModel.name })
  const lead = await call('frappe.client.get_doc', { doctype: 'CRM Lead', name: props.leadName })
  rules.value = (model.rules || []).map((r) => {
    const val = lead[r.fieldname]
    let matched = false
    const op = r.operator || 'is set'
    if (op === 'is set') matched = !!val
    else if (op === 'equals') matched = String(val || '').toLowerCase() === String(r.value || '').toLowerCase()
    else if (op === 'contains') matched = String(val || '').toLowerCase().includes(String(r.value || '').toLowerCase())
    else if (op === 'greater than') matched = parseFloat(val || 0) > parseFloat(r.value || 0)
    else if (op === 'less than') matched = parseFloat(val || 0) < parseFloat(r.value || 0)
    return { ...r, matched }
  })
}

const canOverride = computed(() => {
  if (!overrideBand.value && !overrideScore.value) return false
  return overrideReason.value.trim().length > 0
})

async function applyOverride() {
  try {
    const updates = {}
    if (overrideBand.value) updates.lead_score_band = overrideBand.value
    if (overrideScore.value) updates.lead_score = overrideScore.value
    updates.lead_quality_probability = overrideScore.value || summary.data?.score?.probability || 0
    await call('frappe.client.set_value', {
      doctype: 'CRM Lead',
      name: props.leadName,
      fieldname: updates,
    })
    await call('crm.api.lead_management.score_lead', { lead: props.leadName })
    toast.success(__('Override applied'))
    emit('changed')
    summary.fetch()
  } catch (e) {
    toast.error(__('Override failed'))
  }
}

async function rerunScoring() {
  try {
    loading.value = true
    await call('crm.api.lead_management.score_lead', { lead: props.leadName })
    toast.success(__('Scoring rerun complete'))
    emit('changed')
    summary.fetch()
    await loadRules()
  } catch (e) {
    toast.error(__('Scoring failed'))
  } finally {
    loading.value = false
  }
}

function bandTheme(band) {
  if (band === 'Hot') return 'green'
  if (band === 'Warm') return 'orange'
  return 'gray'
}
</script>
