<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Lead Scoring Rules" />
      </template>
      <template #right-header>
        <Button variant="outline" size="sm" label="Reload" @click="reloadAll" />
        <Button variant="solid" size="sm" label="New Model" @click="createModel">
          <template #prefix><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 px-6 py-4">
      <div v-if="!models.data?.models?.length" class="rounded-[10px] border border-dashed border-outline-gray-2 bg-white px-6 py-12 text-center">
        <div class="text-sm text-ink-gray-6">No scoring models yet.</div>
        <Button class="mt-3" variant="solid" label="Create first model" @click="createModel" />
      </div>

      <template v-else>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-2">
            <select v-model="selectedModel" class="h-8 rounded-md border border-outline-gray-2 bg-white px-2 text-sm text-ink-gray-9 focus:border-ink-gray-5 focus:outline-none">
              <option v-for="m in models.data.models" :key="m.name" :value="m.name">
                {{ m.model_name }} (v{{ m.version }})
              </option>
            </select>
            <Badge v-if="activeModel?.is_active" label="Active" theme="green" variant="subtle" size="sm" />
            <Badge v-else label="Draft" theme="gray" variant="subtle" size="sm" />
          </div>
          <div class="flex gap-2">
            <Button variant="outline" size="sm" label="Clone version" :loading="cloning" @click="cloneModel" />
            <Button
              variant="solid"
              size="sm"
              label="Activate this version"
              :loading="activating"
              :disabled="activeModel?.is_active || !modelDetail.data?.rules?.length"
              @click="activateModel"
            />
          </div>
        </div>

        <div v-if="activeModel" class="mt-2 text-xs text-ink-gray-5">
          {{ activeModel.rule_count }} rules
          <span v-if="activeModel.trained_on">· Last trained {{ formatDate(activeModel.trained_on) }}</span>
          <span v-if="activeModel.description">· {{ activeModel.description }}</span>
        </div>

        <div class="mt-4 rounded-[10px] border border-outline-gray-2 bg-white shadow-sm">
          <div class="flex items-center justify-between border-b border-outline-gray-1 px-3 py-2">
            <div class="text-xs font-semibold uppercase tracking-wide text-ink-gray-5">Rules</div>
            <Button variant="solid" size="sm" label="Add Rule" @click="openEditor()">
              <template #prefix><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
            </Button>
          </div>
          <table class="w-full text-sm">
            <thead class="bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
              <tr>
                <th class="px-3 py-2">Rule</th>
                <th class="px-3 py-2">Criteria</th>
                <th class="px-3 py-2 text-right">Weight</th>
                <th class="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in modelDetail.data?.rules || []" :key="r.name" class="border-t border-outline-gray-1">
                <td class="px-3 py-1.5">
                  <div class="font-medium text-ink-gray-9">{{ r.description || r.fieldname }}</div>
                  <div class="text-[11px] text-ink-gray-5">{{ r.name }}</div>
                </td>
                <td class="px-3 py-1.5 text-ink-gray-7">
                  {{ r.fieldname }} {{ r.operator }} <span v-if="r.value" class="font-mono text-xs">{{ r.value }}</span>
                </td>
                <td class="px-3 py-1.5 text-right font-mono">{{ r.weight }}</td>
                <td class="px-3 py-1.5 text-right">
                  <div class="flex items-center justify-end gap-1">
                    <Button variant="ghost" size="sm" @click="testRule(r)">Test</Button>
                    <Button variant="ghost" size="sm" @click="openEditor(r)">Edit</Button>
                    <Button variant="ghost" size="sm" theme="red" @click="deleteRule(r)">Delete</Button>
                  </div>
                </td>
              </tr>
              <tr v-if="!modelDetail.data?.rules?.length">
                <td colspan="4" class="px-3 py-8 text-center text-ink-gray-5">No rules yet. Add one to start scoring.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-4 rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between">
            <div class="text-xs font-semibold uppercase tracking-wide text-ink-gray-5">Test Model Against Sample Lead</div>
            <Button variant="outline" size="sm" label="Run Test" :loading="modelTest.loading" @click="testModel" />
          </div>
          <div v-if="modelTest.data" class="mt-3 space-y-2">
            <div class="flex items-center gap-3">
              <div class="text-2xl font-bold text-ink-gray-9">{{ modelTest.data.total }}</div>
              <Badge :label="modelTest.data.band" :theme="bandTheme(modelTest.data.band)" variant="subtle" size="lg" />
            </div>
            <div class="text-xs text-ink-gray-5">Sample lead: {{ modelTest.data.sample }}</div>
            <div class="space-y-1">
              <div v-for="b in modelTest.data.breakdown" :key="b.rule" class="flex items-center justify-between rounded border border-outline-gray-1 px-2 py-1 text-xs">
                <span class="text-ink-gray-7">{{ b.fieldname }}</span>
                <div class="flex items-center gap-2">
                  <span class="font-mono text-ink-gray-9">{{ b.contribution }}</span>
                  <FeatherIcon v-if="b.matched" name="check" class="h-3.5 w-3.5 text-green-600" />
                  <FeatherIcon v-else name="minus" class="h-3.5 w-3.5 text-ink-gray-3" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <LeadScoringRuleEditor
      v-model:visible="editorVisible"
      :model="selectedModel"
      :rule="editingRule"
      :fields="models.data?.fields || []"
      :operators="models.data?.operators || []"
      @saved="onRuleSaved"
    />
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LeadScoringRuleEditor from '@/components/LeadScoringRuleEditor.vue'
import { Badge, Button, FeatherIcon, call, createResource, toast } from 'frappe-ui'
import { computed, ref, watch } from 'vue'

const viewControls = ref(null)
const selectedModel = ref('')
const editorVisible = ref(false)
const editingRule = ref(null)
const cloning = ref(false)
const activating = ref(false)

const models = createResource({
  url: 'crm.api.lead_management.list_scoring_models',
  auto: true,
  onSuccess(data) {
    if (data.models?.length && !selectedModel.value) {
      const active = data.models.find((m) => m.is_active)
      selectedModel.value = active?.name || data.models[0].name
    }
  },
})

const modelDetail = createResource({
  url: 'crm.api.lead_management.get_scoring_model',
  makeParams: () => ({ name: selectedModel.value }),
})

watch(selectedModel, () => modelDetail.fetch())

const activeModel = computed(() => models.data?.models?.find((m) => m.name === selectedModel.value))

function reloadAll() {
  models.reload()
  modelDetail.fetch()
}

async function createModel() {
  try {
    const name = `Scoring Model ${new Date().toLocaleDateString()}`
    await call('frappe.client.insert', {
      doc: {
        doctype: 'CRM Lead Scoring Model',
        model_name: name,
        version: 1,
        is_active: 0,
        description: '',
      },
    })
    toast.success('Model created')
    models.reload()
  } catch (e) {
    toast.error(e?.message || 'Failed to create model')
  }
}

async function cloneModel() {
  if (!selectedModel.value) return
  cloning.value = true
  try {
    await call('crm.api.lead_management.clone_scoring_model_version', { model: selectedModel.value })
    toast.success('Cloned to new version')
    await models.reload()
    const latest = models.data?.models?.[0]
    if (latest) selectedModel.value = latest.name
  } catch (e) {
    toast.error(e?.message || 'Clone failed')
  } finally {
    cloning.value = false
  }
}

async function activateModel() {
  if (!selectedModel.value) return
  activating.value = true
  try {
    await call('crm.api.lead_management.activate_scoring_model', { model: selectedModel.value })
    toast.success('Activated')
    await models.reload()
    modelDetail.fetch()
  } catch (e) {
    toast.error(e?.message || 'Activation failed')
  } finally {
    activating.value = false
  }
}

function openEditor(rule = null) {
  editingRule.value = rule
  editorVisible.value = true
}

function onRuleSaved() {
  editorVisible.value = false
  modelDetail.fetch()
  models.reload()
}

async function deleteRule(r) {
  if (!confirm(`Delete rule "${r.description || r.fieldname}"?`)) return
  try {
    await call('crm.api.lead_management.delete_scoring_rule', { model: selectedModel.value, rule: r.name })
    toast.success('Rule deleted')
    modelDetail.fetch()
    models.reload()
  } catch (e) {
    toast.error(e?.message || 'Delete failed')
  }
}

const modelTest = createResource({
  url: 'crm.api.lead_management.test_scoring_model',
  makeParams: () => ({ model: selectedModel.value }),
})

function testModel() {
  modelTest.fetch()
}

async function testRule(r) {
  try {
    const res = await call('crm.api.lead_management.test_scoring_rule', { model: selectedModel.value, rule: r.name })
    toast.info(`${r.description || r.fieldname}: ${res.matched ? 'Matched' : 'No match'} · ${res.contribution} pts`)
  } catch (e) {
    toast.error(e?.message || 'Test failed')
  }
}

function bandTheme(band) {
  if (band === 'Hot') return 'green'
  if (band === 'Warm') return 'orange'
  return 'gray'
}

function formatDate(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
