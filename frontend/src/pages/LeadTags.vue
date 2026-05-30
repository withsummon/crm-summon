<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Lead Tags" />
      </template>
      <template #right-header>
        <Button variant="solid" label="New Tag" @click="openCreate()">
          <template #prefix>
            <FeatherIcon name="plus" class="h-3.5 w-3.5" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 px-6 py-4">
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-base font-semibold text-ink-gray-9">Tag Library</h2>
        <div class="flex items-center gap-2">
          <input
            v-model="search"
            type="text"
            placeholder="Search tags…"
            class="h-8 w-56 rounded-md border border-outline-gray-2 bg-white px-2 text-sm text-ink-gray-8 placeholder:text-ink-gray-4 focus:border-ink-gray-5 focus:outline-none"
          />
          <Button variant="outline" size="sm" label="Reload" @click="tagsResource.reload()" />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div
          v-for="t in filtered"
          :key="t.name"
          class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex min-w-0 items-center gap-2">
              <span
                class="inline-block size-4 shrink-0 rounded-full"
                :style="{ backgroundColor: t.color || '#0f766e' }"
              />
              <div class="min-w-0">
                <div class="truncate text-sm font-semibold text-ink-gray-9">{{ t.tag }}</div>
                <div class="truncate text-xs text-ink-gray-5">
                  {{ t.description || '—' }}
                </div>
              </div>
            </div>
            <Badge
              :label="t.is_active ? 'Active' : 'Hidden'"
              variant="subtle"
              :theme="t.is_active ? 'teal' : 'gray'"
              size="sm"
            />
          </div>
          <div class="mt-3 flex items-center justify-between text-xs text-ink-gray-6">
            <div>
              <span class="font-medium text-ink-gray-8">{{ t.usage }}</span>
              {{ t.usage === 1 ? 'lead' : 'leads' }}
            </div>
            <div>
              {{ t.last_used ? `Last used ${formatDate(t.last_used)}` : 'Never used' }}
            </div>
          </div>
          <div class="mt-3 flex gap-1.5">
            <Button size="sm" variant="outline" label="Edit" @click="openEdit(t)" />
            <Button
              size="sm"
              variant="outline"
              theme="red"
              label="Delete"
              :loading="deletingTag === t.tag"
              @click="confirmDelete(t)"
            />
          </div>
        </div>

        <div
          v-if="!filtered.length"
          class="col-span-full rounded-[10px] border border-dashed border-outline-gray-2 bg-white px-6 py-12 text-center"
        >
          <div class="text-sm text-ink-gray-6">No tags yet.</div>
          <div class="mt-1 text-xs text-ink-gray-5">
            Tags let you slice leads beyond status — e.g. <em>VIP</em>, <em>UMKM</em>, <em>Returning Customer</em>.
          </div>
          <Button class="mt-3" variant="solid" label="Create your first tag" @click="openCreate()" />
        </div>
      </div>
    </div>

    <Dialog
      v-model="showDialog"
      :options="{
        title: editing.name ? 'Edit Tag' : 'New Tag',
        size: 'sm',
        actions: [
          { label: 'Cancel', onClick: closeDialog },
          { label: 'Save', variant: 'solid', loading: saving, onClick: saveTag },
        ],
      }"
    >
      <template #body-content>
        <div class="space-y-3">
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Name</label>
            <input
              v-model="editing.tag"
              type="text"
              :disabled="!!editing.name"
              class="h-8 w-full rounded-md border border-outline-gray-2 bg-white px-2 text-sm text-ink-gray-9 focus:border-ink-gray-5 focus:outline-none disabled:bg-surface-gray-1"
              placeholder="e.g. VIP"
            />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Color</label>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="c in palette"
                :key="c"
                type="button"
                class="size-7 rounded-full border-2 transition"
                :class="editing.color === c ? 'border-ink-gray-9' : 'border-transparent'"
                :style="{ backgroundColor: c }"
                @click="editing.color = c"
              />
            </div>
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-ink-gray-6">Description</label>
            <textarea
              v-model="editing.description"
              rows="2"
              class="w-full rounded-md border border-outline-gray-2 bg-white px-2 py-1.5 text-sm text-ink-gray-9 focus:border-ink-gray-5 focus:outline-none"
              placeholder="Optional"
            />
          </div>
          <label class="flex items-center gap-2 text-sm text-ink-gray-7">
            <input v-model="editing.is_active" type="checkbox" class="size-4 accent-[#FF6600]" />
            Active
          </label>
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
const search = ref('')
const showDialog = ref(false)
const saving = ref(false)
const deletingTag = ref(null)

const editing = reactive({
  name: '',
  tag: '',
  color: '#0f766e',
  description: '',
  is_active: true,
})

const tagsResource = createResource({
  url: 'crm.api.lead_management.list_tags',
  auto: true,
  cache: 'leadTags',
})

const tags = computed(() => tagsResource.data?.tags || [])
const palette = computed(() => tagsResource.data?.palette || [
  '#0f766e', '#FF6600', '#2563eb', '#9333ea',
  '#dc2626', '#65a30d', '#0891b2', '#a16207',
])

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return tags.value
  return tags.value.filter((t) =>
    [t.tag, t.description].some((v) => (v || '').toLowerCase().includes(q)),
  )
})

function resetEditing() {
  editing.name = ''
  editing.tag = ''
  editing.color = palette.value[0]
  editing.description = ''
  editing.is_active = true
}

function openCreate() {
  resetEditing()
  showDialog.value = true
}

function openEdit(t) {
  editing.name = t.name
  editing.tag = t.tag
  editing.color = t.color || palette.value[0]
  editing.description = t.description || ''
  editing.is_active = !!t.is_active
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
}

async function saveTag() {
  const tag = editing.tag.trim()
  if (!tag) {
    toast.error('Tag name is required')
    return
  }
  saving.value = true
  try {
    await call('crm.api.lead_management.upsert_tag', {
      payload: {
        tag,
        color: editing.color,
        description: editing.description,
        is_active: editing.is_active ? 1 : 0,
      },
    })
    showDialog.value = false
    toast.success(editing.name ? 'Tag updated' : 'Tag created')
    tagsResource.reload()
  } catch (e) {
    toast.error(e?.message || 'Failed to save tag')
  } finally {
    saving.value = false
  }
}

async function confirmDelete(t) {
  if (!window.confirm(`Delete tag "${t.tag}"? ${t.usage ? `It is used on ${t.usage} leads and will be removed from all.` : ''}`)) return
  deletingTag.value = t.tag
  try {
    await call('crm.api.lead_management.delete_tag', { tag: t.tag, force: t.usage ? 1 : 0 })
    toast.success('Tag deleted')
    tagsResource.reload()
  } catch (e) {
    toast.error(e?.message || 'Failed to delete')
  } finally {
    deletingTag.value = null
  }
}

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
</script>
