<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed inset-0 z-50 flex justify-end">
      <button class="absolute inset-0 bg-black/30" aria-label="Close" @click="emit('update:visible', false)" />
      <aside class="relative flex h-full w-full max-w-[520px] flex-col bg-white shadow-xl">
        <div class="flex items-center justify-between border-b border-outline-gray-2 px-5 py-4">
          <div class="text-base font-semibold text-ink-gray-9">{{ editing.name ? 'Edit Rule' : 'New Rule' }}</div>
          <Button variant="ghost" icon="x" @click="emit('update:visible', false)" />
        </div>

        <div class="flex-1 space-y-4 overflow-y-auto p-5">
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Field</label>
            <select v-model="editing.fieldname" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none">
              <option v-for="f in fields" :key="f" :value="f">{{ f }}</option>
            </select>
          </div>

          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Operator</label>
            <select v-model="editing.operator" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none">
              <option v-for="o in operators" :key="o" :value="o">{{ o }}</option>
            </select>
          </div>

          <div v-if="editing.operator !== 'is set'">
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Value</label>
            <input v-model="editing.value" type="text" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>

          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Weight: {{ editing.weight }}</label>
            <input v-model.number="editing.weight" type="range" min="0" max="100" class="w-full accent-[#FF6600]" />
          </div>

          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Description</label>
            <textarea v-model="editing.description" rows="2" class="w-full rounded-md border border-outline-gray-2 bg-white px-2 py-1.5 text-sm focus:border-ink-gray-5 focus:outline-none" placeholder="Optional"></textarea>
          </div>

          <div v-if="testResult" class="rounded border border-outline-gray-1 bg-surface-gray-1 p-3 text-sm">
            <div class="flex items-center justify-between">
              <span class="text-ink-gray-7">Sample lead</span>
              <span class="font-mono text-xs text-ink-gray-9">{{ testResult.sample }}</span>
            </div>
            <div class="mt-1 flex items-center justify-between">
              <span class="text-ink-gray-7">Matched</span>
              <FeatherIcon v-if="testResult.matched" name="check" class="h-4 w-4 text-green-600" />
              <FeatherIcon v-else name="x" class="h-4 w-4 text-red-500" />
            </div>
            <div class="mt-1 flex items-center justify-between">
              <span class="text-ink-gray-7">Contribution</span>
              <span class="font-semibold text-ink-gray-9">{{ testResult.contribution }} pts</span>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 border-t border-outline-gray-2 px-5 py-4">
          <Button variant="outline" label="Cancel" @click="emit('update:visible', false)" />
          <Button variant="outline" label="Test" :loading="testing" @click="runTest" />
          <Button variant="solid" label="Save" :loading="saving" @click="save" />
        </div>
      </aside>
    </div>
  </Teleport>
</template>

<script setup>
import { Button, FeatherIcon, call, toast } from 'frappe-ui'
import { reactive, ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  model: { type: String, default: '' },
  rule: { type: Object, default: null },
  fields: { type: Array, default: () => [] },
  operators: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:visible', 'saved'])

const saving = ref(false)
const testing = ref(false)
const testResult = ref(null)

const editing = reactive({
  name: '',
  fieldname: '',
  operator: 'is set',
  value: '',
  weight: 10,
  description: '',
})

watch(() => props.visible, (val) => {
  if (val) {
    testResult.value = null
    if (props.rule) {
      editing.name = props.rule.name
      editing.fieldname = props.rule.fieldname
      editing.operator = props.rule.operator || 'is set'
      editing.value = props.rule.value || ''
      editing.weight = props.rule.weight || 10
      editing.description = props.rule.description || ''
    } else {
      editing.name = ''
      editing.fieldname = props.fields[0] || ''
      editing.operator = 'is set'
      editing.value = ''
      editing.weight = 10
      editing.description = ''
    }
  }
})

async function save() {
  if (!editing.fieldname) {
    toast.error('Field is required')
    return
  }
  saving.value = true
  try {
    await call('crm.api.lead_management.upsert_scoring_rule', {
      model: props.model,
      payload: {
        name: editing.name,
        fieldname: editing.fieldname,
        operator: editing.operator,
        value: editing.value,
        weight: editing.weight,
        description: editing.description,
      },
    })
    toast.success(editing.name ? 'Rule updated' : 'Rule created')
    emit('saved')
  } catch (e) {
    toast.error(e?.message || 'Save failed')
  } finally {
    saving.value = false
  }
}

async function runTest() {
  testing.value = true
  try {
    let ruleName = editing.name
    if (!ruleName) {
      const res = await call('crm.api.lead_management.upsert_scoring_rule', {
        model: props.model,
        payload: {
          fieldname: editing.fieldname,
          operator: editing.operator,
          value: editing.value,
          weight: editing.weight,
          description: editing.description,
        },
      })
      ruleName = res.rule
      editing.name = ruleName
    }
    const result = await call('crm.api.lead_management.test_scoring_rule', {
      model: props.model,
      rule: ruleName,
    })
    testResult.value = result
  } catch (e) {
    toast.error(e?.message || 'Test failed')
  } finally {
    testing.value = false
  }
}
</script>
