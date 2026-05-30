<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Lead Web Forms" />
      </template>
      <template #right-header>
        <Button variant="outline" size="sm" label="Reload" @click="forms.reload()" />
        <Button variant="solid" size="sm" label="New Form" @click="openCreate">
          <template #prefix><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 px-6 py-4">
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="f in forms.data?.forms || []"
          :key="f.name"
          class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <div class="truncate text-sm font-semibold text-ink-gray-9">{{ f.form_name }}</div>
              <div class="text-xs text-ink-gray-5">/{{ f.slug }}</div>
            </div>
            <Badge
              :label="f.active ? 'Active' : 'Inactive'"
              :theme="f.active ? 'green' : 'gray'"
              variant="subtle"
              size="sm"
            />
          </div>

          <div class="mt-3 space-y-1 text-xs text-ink-gray-6">
            <div>Captcha: {{ f.captcha_enabled ? 'On' : 'Off' }}</div>
            <div class="truncate">Redirect: {{ f.redirect_url || '—' }}</div>
          </div>

          <div class="mt-3 rounded border border-outline-gray-1 bg-surface-gray-1 p-2">
            <div class="text-[10px] uppercase tracking-wide text-ink-gray-5">Embed</div>
            <code class="mt-1 block break-all text-[11px] text-ink-gray-7">
              &lt;script src="{{ baseUrl }}/webform.js?slug={{ f.slug }}"&gt;&lt;/script&gt;<br/>
              &lt;div id="summon-lead-form-{{ f.slug }}"&gt;&lt;/div&gt;
            </code>
            <div class="mt-2 flex gap-2">
              <Button variant="outline" size="sm" label="Copy" @click="copyEmbed(f)" />
              <Button variant="outline" size="sm" label="Preview" @click="previewForm(f)" />
            </div>
          </div>

          <div class="mt-3 flex gap-2">
            <Button variant="ghost" size="sm" @click="openEdit(f)">Edit</Button>
            <Button variant="ghost" size="sm" theme="red" @click="deleteForm(f)">Delete</Button>
          </div>
        </div>

        <div v-if="!forms.data?.forms?.length" class="col-span-full rounded-[10px] border border-dashed border-outline-gray-2 bg-white px-6 py-12 text-center">
          <div class="text-sm text-ink-gray-6">No web forms yet.</div>
          <Button class="mt-3" variant="solid" label="Create first form" @click="openCreate" />
        </div>
      </div>
    </div>

    <Dialog
      v-model="showDialog"
      :options="{
        title: editing.name ? 'Edit Web Form' : 'New Web Form',
        size: 'lg',
        actions: [
          { label: 'Cancel', onClick: () => (showDialog = false) },
          { label: 'Save', variant: 'solid', loading: saving, onClick: saveForm },
        ],
      }"
    >
      <template #body-content>
        <div class="grid gap-3 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Form Name</label>
            <input v-model="editing.form_name" type="text" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Slug</label>
            <input v-model="editing.slug" :disabled="!!editing.name" type="text" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none disabled:bg-surface-gray-1" />
          </div>
          <div class="sm:col-span-2">
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Redirect URL</label>
            <input v-model="editing.redirect_url" type="text" placeholder="https://…" class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm focus:border-ink-gray-5 focus:outline-none" />
          </div>
          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2 text-sm text-ink-gray-7">
              <input v-model="editing.active" type="checkbox" class="size-4 accent-[#FF6600]" />
              Active
            </label>
            <label class="flex items-center gap-2 text-sm text-ink-gray-7">
              <input v-model="editing.captcha_enabled" type="checkbox" class="size-4 accent-[#FF6600]" />
              Captcha
            </label>
          </div>
        </div>
        <div class="mt-4">
          <label class="mb-1 block text-xs font-medium text-ink-gray-6">Fields JSON</label>
          <textarea v-model="editing.fields_json" rows="6" class="w-full rounded-md border border-outline-gray-2 bg-white px-2 py-1.5 font-mono text-xs text-ink-gray-9 focus:border-ink-gray-5 focus:outline-none" placeholder='[{ "fieldname": "first_name", "label": "First Name", "required": 1 }, ...]'></textarea>
          <div class="mt-1 text-[11px] text-ink-gray-5">Leave blank to use the default field set.</div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import { Badge, Button, Dialog, FeatherIcon, call, createResource, toast } from 'frappe-ui'
import { computed, reactive, ref } from 'vue'

const viewControls = ref(null)
const showDialog = ref(false)
const saving = ref(false)

const editing = reactive({
  name: '',
  form_name: '',
  slug: '',
  active: true,
  captcha_enabled: false,
  redirect_url: '',
  fields_json: '',
})

const forms = createResource({
  url: 'crm.api.lead_management.list_webforms',
  auto: true,
})

const baseUrl = computed(() => {
  try {
    return window.location.origin + '/crm'
  } catch (e) {
    return ''
  }
})

function resetEditing() {
  editing.name = ''
  editing.form_name = ''
  editing.slug = ''
  editing.active = true
  editing.captcha_enabled = false
  editing.redirect_url = ''
  editing.fields_json = ''
}

function openCreate() {
  resetEditing()
  showDialog.value = true
}

function openEdit(f) {
  editing.name = f.name
  editing.form_name = f.form_name
  editing.slug = f.slug
  editing.active = !!f.active
  editing.captcha_enabled = !!f.captcha_enabled
  editing.redirect_url = f.redirect_url || ''
  editing.fields_json = ''
  showDialog.value = true
}

async function saveForm() {
  if (!editing.form_name.trim() || !editing.slug.trim()) {
    toast.error('Name and slug are required')
    return
  }
  let fieldsJson = editing.fields_json.trim()
  if (fieldsJson) {
    try {
      JSON.parse(fieldsJson)
    } catch (e) {
      toast.error('Fields JSON is invalid')
      return
    }
  }
  saving.value = true
  try {
    await call('crm.api.lead_management.upsert_webform', {
      payload: {
        name: editing.name,
        form_name: editing.form_name.trim(),
        slug: editing.slug.trim(),
        active: editing.active ? 1 : 0,
        captcha_enabled: editing.captcha_enabled ? 1 : 0,
        redirect_url: editing.redirect_url.trim(),
        fields_json: fieldsJson || undefined,
      },
    })
    showDialog.value = false
    toast.success(editing.name ? 'Form updated' : 'Form created')
    forms.reload()
  } catch (e) {
    toast.error(e?.message || 'Save failed')
  } finally {
    saving.value = false
  }
}

async function deleteForm(f) {
  if (!confirm(`Delete form "${f.form_name}"?`)) return
  try {
    await call('frappe.client.delete', { doctype: 'CRM Lead Web Form', name: f.name })
    toast.success('Form deleted')
    forms.reload()
  } catch (e) {
    toast.error(e?.message || 'Delete failed')
  }
}

function copyEmbed(f) {
  const snippet = `<script src="${baseUrl.value}/webform.js?slug=${f.slug}"><\/script>\n<div id="summon-lead-form-${f.slug}"></div>`
  navigator.clipboard.writeText(snippet).then(() => toast.success('Copied to clipboard'))
}

function previewForm(f) {
  const url = `${baseUrl.value}/webform-preview?slug=${f.slug}`
  window.open(url, '_blank')
}
</script>
