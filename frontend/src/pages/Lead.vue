<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template v-if="!errorTitle" #right-header>
      <CustomActions
        v-if="document._actions?.length"
        :actions="document._actions"
      />
      <CustomActions
        v-if="document.actions?.length"
        :actions="document.actions"
      />
      <Button :label="__('Print')" variant="outline" :loading="printing" @click="printLead">
        <template #prefix><FeatherIcon name="printer" class="h-3.5 w-3.5" /></template>
      </Button>
      <AssignTo v-model="assignees.data" doctype="CRM Lead" :docname="leadId" />
      <Dropdown
        v-if="doc && document.statuses"
        :options="statuses"
        placement="right"
      >
        <template #default="{ open }">
          <Button
            v-if="doc.status"
            :label="statusLabel(doc.status)"
            :iconRight="open ? 'chevron-up' : 'chevron-down'"
          >
            <template #prefix>
              <IndicatorIcon :class="getLeadStatus(doc.status).color" />
            </template>
          </Button>
        </template>
      </Dropdown>
      <Button
        :label="__('Convert to Deal')"
        variant="solid"
        @click="showConvertToDealModal = true"
      />
    </template>
  </LayoutHeader>
  <div v-if="doc.name" class="flex h-full overflow-hidden">
    <Tabs
      v-model="tabIndex"
      :tabs="tabs"
      class="flex flex-1 overflow-hidden flex-col [&_[role='tab']]:px-0 [&_[role='tab']]:shrink-0 [&_[role='tablist']]:px-5 [&_[role='tablist']::-webkit-scrollbar]:h-0 [&_[role='tablist']]:min-h-[45px] [&_[role='tablist']]:gap-7.5 [&_[role='tabpanel']:not([hidden])]:flex [&_[role='tabpanel']:not([hidden])]:grow"
    >
      <template #tab-panel>
        <Activities
          ref="activities"
          v-model:reload="reload"
          v-model:tabIndex="tabIndex"
          doctype="CRM Lead"
          :docname="leadId"
          :tabs="tabs"
          @beforeSave="beforeStatusChange"
          @afterSave="reloadResources"
        />
      </template>
    </Tabs>
    <Resizer class="flex flex-col justify-between border-l" side="right">
      <div
        class="flex h-[45px] cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
        @click="copyToClipboard(leadId)"
      >
        {{ __(leadId) }}
      </div>
      <FileUploader
        :validateFile="validateIsImageFile"
        @success="(file) => updateField('image', file.file_url)"
      >
        <template #default="{ openFileSelector }">
          <div class="flex items-center justify-start gap-5 border-b p-5">
            <div class="group relative size-12">
              <Avatar
                size="3xl"
                class="size-12"
                :label="title"
                :image="doc.image"
              />
              <component
                :is="doc.image ? Dropdown : 'div'"
                v-bind="
                  doc.image
                    ? {
                        options: [
                          {
                            icon: 'upload',
                            label: doc.image
                              ? __('Change Image')
                              : __('Upload Image'),
                            onClick: openFileSelector,
                          },
                          {
                            icon: 'trash-2',
                            label: __('Remove Image'),
                            onClick: () => updateField('image', ''),
                          },
                        ],
                      }
                    : { onClick: openFileSelector }
                "
                class="!absolute bottom-0 left-0 right-0"
              >
                <div
                  class="z-1 absolute bottom-0.5 left-0 right-0.5 flex h-9 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-3 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
                  style="
                    -webkit-clip-path: inset(12px 0 0 0);
                    clip-path: inset(12px 0 0 0);
                  "
                >
                  <CameraIcon class="size-4 cursor-pointer text-white" />
                </div>
              </component>
            </div>
            <div class="flex flex-col gap-2.5 truncate">
              <Tooltip :text="doc.lead_name || __('Set First Name')">
                <div class="truncate text-2xl font-medium text-ink-gray-9">
                  {{ title }}
                </div>
              </Tooltip>
              <div class="flex gap-1.5">
                <Button
                  v-if="callEnabled"
                  :tooltip="__('Make a Call')"
                  :icon="PhoneIcon"
                  @click="
                    () =>
                      doc.mobile_no
                        ? makeCall(doc.mobile_no)
                        : toast.error(
                            __('Please set a mobile number to make calls'),
                          )
                  "
                />

                <Button
                  :tooltip="__('Send an Email')"
                  :icon="Email2Icon"
                  @click="
                    doc.email
                      ? openEmailBox()
                      : toast.error(
                          __('Please set an email address to send emails'),
                        )
                  "
                />
                <Button
                  :tooltip="__('Go to Website')"
                  :icon="LinkIcon"
                  @click="
                    doc.website
                      ? openWebsite(doc.website)
                      : toast.error(__('Please set a website to visit'))
                  "
                />

                <Button
                  :tooltip="__('Attach a File')"
                  :icon="AttachmentIcon"
                  @click="showFilesUploader = true"
                />

                <Button
                  v-if="canDelete"
                  :tooltip="__('Delete')"
                  variant="subtle"
                  theme="red"
                  icon="trash-2"
                  @click="deleteLead"
                />
              </div>
              <ErrorMessage :message="__(error)" />
            </div>
          </div>
        </template>
      </FileUploader>
      <SLASection
        v-if="doc.sla_status"
        v-model="doc"
        @updateField="updateField"
      />
      <div class="border-b p-5">
        <div class="mb-3 flex items-center justify-between gap-3">
          <div>
            <div class="text-sm font-semibold text-ink-gray-9">
              {{ __('Lead Intelligence') }}
            </div>
            <div class="text-xs text-ink-gray-5">
              {{ __('Score, duplicate, attribution, and assignment context') }}
            </div>
          </div>
          <Button variant="subtle" size="sm" icon="refresh-cw" @click="refreshLeadSummary" />
        </div>
        <div v-if="leadSummary.loading" class="text-sm text-ink-gray-5">
          {{ __('Loading...') }}
        </div>
        <div v-else class="flex flex-col gap-4">
          <div class="grid grid-cols-3 gap-2">
            <div class="rounded border bg-surface-gray-1 p-3">
              <div class="text-xs text-ink-gray-5">{{ __('Score') }}</div>
              <div class="text-xl font-semibold text-ink-gray-9">
                {{ leadSummary.data?.score?.value || 0 }}
              </div>
            </div>
            <div class="rounded border bg-surface-gray-1 p-3">
              <div class="text-xs text-ink-gray-5">{{ __('Band') }}</div>
              <Badge
                :label="leadSummary.data?.score?.band || __('Cold')"
                variant="subtle"
                theme="blue"
              />
            </div>
            <div class="rounded border bg-surface-gray-1 p-3">
              <div class="text-xs text-ink-gray-5">{{ __('Quality') }}</div>
              <div class="text-sm font-medium text-ink-gray-9">
                {{ leadSummary.data?.score?.probability || 0 }}%
              </div>
            </div>
          </div>
          <div>
            <div class="mb-2 text-xs font-semibold uppercase text-ink-gray-5">
              {{ __('Attribution') }}
            </div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>{{ __('Channel') }}: {{ leadSummary.data?.attribution?.channel || '-' }}</div>
              <div>{{ __('Source') }}: {{ leadSummary.data?.attribution?.source || '-' }}</div>
              <div>{{ __('Campaign') }}: {{ leadSummary.data?.attribution?.campaign || '-' }}</div>
              <div>{{ __('Referrer') }}: {{ leadSummary.data?.attribution?.referrer || '-' }}</div>
            </div>
          </div>
          <div>
            <div class="mb-2 flex items-center justify-between">
              <div class="text-xs font-semibold uppercase text-ink-gray-5">{{ __('Referral') }}</div>
              <button
                v-if="!referralEditing"
                class="text-xs text-ink-gray-5 hover:text-ink-gray-8"
                @click="beginReferralEdit"
              >
                {{ __('Edit') }}
              </button>
              <div v-else class="flex items-center gap-1">
                <button class="text-xs text-ink-gray-5 hover:text-ink-gray-8" @click="referralEditing = false">{{ __('Cancel') }}</button>
                <button class="text-xs font-medium text-[#FF6600]" :disabled="savingReferral" @click="saveReferral">{{ savingReferral ? __('Saving…') : __('Save') }}</button>
              </div>
            </div>
            <div v-if="!referralEditing" class="grid grid-cols-3 gap-2 text-sm">
              <div>
                <div class="text-[10px] uppercase text-ink-gray-5">{{ __('Type') }}</div>
                <div class="text-ink-gray-9">{{ uatSummary.data?.attribution?.referrer_type || '—' }}</div>
              </div>
              <div>
                <div class="text-[10px] uppercase text-ink-gray-5">{{ __('Referrer') }}</div>
                <div class="truncate text-ink-gray-9">{{ uatSummary.data?.attribution?.referrer || '—' }}</div>
              </div>
              <div>
                <div class="text-[10px] uppercase text-ink-gray-5">{{ __('Fee') }}</div>
                <div class="font-mono text-ink-gray-9">{{ formatRupiah(document?.doc?.referral_fee) }}</div>
              </div>
            </div>
            <div v-else class="grid grid-cols-3 gap-2 text-sm">
              <select
                v-model="referralDraft.referrer_type"
                class="h-8 rounded-md border border-outline-gray-2 bg-white px-2 text-xs focus:border-ink-gray-5 focus:outline-none"
              >
                <option value="">—</option>
                <option>Customer</option>
                <option>RM</option>
                <option>Partner</option>
                <option>Other</option>
              </select>
              <input
                v-model="referralDraft.referrer"
                type="text"
                placeholder="Name or user@…"
                class="col-span-2 h-8 rounded-md border border-outline-gray-2 bg-white px-2 text-xs focus:border-ink-gray-5 focus:outline-none"
              />
              <div class="col-span-3 text-[11px] text-ink-gray-5">
                {{ __('Fee is recomputed on save based on type + expected value.') }}
              </div>
            </div>
          </div>
          <div>
            <div class="mb-2 flex items-center justify-between">
              <div class="text-xs font-semibold uppercase text-ink-gray-5">
                {{ __('Duplicate Candidates') }}
              </div>
              <Button
                variant="ghost"
                size="sm"
                :label="__('Refresh')"
                @click="refreshDuplicates"
              />
            </div>
            <div v-if="leadSummary.data?.duplicates?.length" class="flex flex-col gap-2">
              <div
                v-for="candidate in leadSummary.data.duplicates"
                :key="candidate.name"
                class="rounded border p-2 text-sm"
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="truncate font-medium">{{ candidate.lead_name || candidate.name }}</span>
                  <Badge :label="`${candidate.score}%`" variant="subtle" theme="orange" />
                </div>
                <div class="truncate text-xs text-ink-gray-5">
                  {{ candidate.match_basis || candidate.email || candidate.mobile_no }}
                </div>
              </div>
            </div>
            <div v-else class="text-sm text-ink-gray-5">{{ __('No duplicate candidates') }}</div>
          </div>
          <div>
            <div class="mb-2 flex items-center justify-between">
              <div class="text-xs font-semibold uppercase text-ink-gray-5">{{ __('Tags') }}</div>
              <button
                class="text-xs text-ink-gray-5 hover:text-ink-gray-8"
                @click="$router.push({ name: 'Lead Tags' })"
              >
                {{ __('Manage') }}
              </button>
            </div>
            <div class="flex flex-wrap items-center gap-1.5">
              <span
                v-for="tag in uatSummary.data?.tags || []"
                :key="tag.tag"
                class="inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs"
                :style="{ borderColor: (tag.color || '#0f766e') + '40', backgroundColor: (tag.color || '#0f766e') + '14', color: tag.color || '#0f766e' }"
              >
                {{ tag.tag }}
                <button class="text-ink-gray-5 hover:text-ink-gray-8" @click="removeTag(tag.tag)">×</button>
              </span>
              <div class="relative">
                <button
                  class="inline-flex items-center gap-1 rounded-full border border-dashed border-outline-gray-2 px-2 py-0.5 text-xs text-ink-gray-6 hover:text-ink-gray-8"
                  @click="tagPickerOpen = !tagPickerOpen"
                >
                  + {{ __('Add tag') }}
                </button>
                <div
                  v-if="tagPickerOpen"
                  class="absolute left-0 top-full z-20 mt-1 w-56 rounded-md border border-outline-gray-2 bg-white p-2 shadow-lg"
                >
                  <input
                    v-model="tagSearch"
                    type="text"
                    placeholder="Search or create…"
                    class="mb-1 h-7 w-full rounded border border-outline-gray-2 px-2 text-xs focus:outline-none"
                    @keydown.enter="addNewTag()"
                  />
                  <div class="max-h-40 overflow-y-auto">
                    <button
                      v-for="t in tagSuggestions"
                      :key="t.name"
                      class="flex w-full items-center gap-2 rounded px-2 py-1 text-left text-xs hover:bg-surface-gray-1"
                      @click="addTag(t.tag)"
                    >
                      <span class="inline-block size-2.5 rounded-full" :style="{ backgroundColor: t.color || '#0f766e' }" />
                      {{ t.tag }}
                    </button>
                    <div v-if="!tagSuggestions.length && !tagSearch" class="px-2 py-1 text-xs text-ink-gray-5">{{ __('No tags yet') }}</div>
                    <button
                      v-if="tagSearch && !tagSuggestions.some((s) => s.tag.toLowerCase() === tagSearch.toLowerCase())"
                      class="w-full rounded px-2 py-1 text-left text-xs text-[#FF6600] hover:bg-surface-gray-1"
                      @click="addNewTag()"
                    >
                      + Create "{{ tagSearch }}"
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <SidePanelLayout
          :sections="sections.data"
          doctype="CRM Lead"
          :docname="leadId"
          @reload="sections.reload"
          @beforeFieldChange="beforeStatusChange"
          @afterFieldChange="reloadResources"
        />
      </div>
    </Resizer>
  </div>
  <ErrorPage
    v-else-if="errorTitle"
    :errorTitle="errorTitle"
    :errorMessage="errorMessage"
  />
  <ConvertToDealModal
    v-if="showConvertToDealModal"
    v-model="showConvertToDealModal"
    :lead="doc"
  />
  <FilesUploader
    v-model="showFilesUploader"
    doctype="CRM Lead"
    :docname="leadId"
    @after="
      () => {
        activities?.all_activities?.reload()
        changeTabTo('attachments')
      }
    "
  />
  <DeleteLinkedDocModal
    v-if="showDeleteLinkedDocModal"
    v-model="showDeleteLinkedDocModal"
    :doctype="'CRM Lead'"
    :docname="leadId"
    name="Leads"
  />
  <LostReasonModal
    v-if="showLostReasonModal"
    v-model="showLostReasonModal"
    doctype="CRM Lead"
    :document="document"
  />
</template>
<script setup>
import DeleteLinkedDocModal from '@/components/DeleteLinkedDocModal.vue'
import ErrorPage from '@/components/ErrorPage.vue'
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import EventIcon from '@/components/Icons/EventIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import ChatIcon from '@/components/Icons/ChatIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import CameraIcon from '@/components/Icons/CameraIcon.vue'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import LostReasonModal from '@/components/Modals/LostReasonModal.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import AssignTo from '@/components/AssignTo.vue'
import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
import SidePanelLayout from '@/components/SidePanelLayout.vue'
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import ConvertToDealModal from '@/components/Modals/ConvertToDealModal.vue'
import {
  openWebsite,
  setupCustomizations,
  copyToClipboard,
  validateIsImageFile,
  isTranslatable,
} from '@/utils'
import { getView } from '@/utils/view'
import { getSettings } from '@/stores/settings'
import { globalStore } from '@/stores/global'
import { statusesStore } from '@/stores/statuses'
import { getMeta } from '@/stores/meta'
import { useDocument } from '@/data/document'
import { whatsappEnabled } from '@/composables/whatsapp'
import { callEnabled } from '@/composables/telephony'
import {
  createResource,
  FileUploader,
  Dropdown,
  FeatherIcon,
  Badge,
  Tooltip,
  Avatar,
  Tabs,
  Breadcrumbs,
  call,
  usePageMeta,
  toast,
} from 'frappe-ui'
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useActiveTabManager } from '@/composables/useActiveTabManager'

const { brand } = getSettings()
const { $dialog, $socket, makeCall } = globalStore()
const { statusOptions, getLeadStatus } = statusesStore()
const { doctypeMeta } = getMeta('CRM Lead')

const route = useRoute()
const router = useRouter()

const props = defineProps({
  leadId: { type: String, required: true },
})

const reload = ref(false)
const activities = ref(null)
const errorTitle = ref('')
const errorMessage = ref('')
const showDeleteLinkedDocModal = ref(false)
const showConvertToDealModal = ref(false)
const showFilesUploader = ref(false)

const {
  triggerOnChange,
  triggerOnRender,
  assignees,
  permissions,
  document,
  scripts,
  error,
} = useDocument('CRM Lead', props.leadId)

const canDelete = computed(() => permissions.data?.permissions?.delete || false)

const doc = computed(() => document.doc || {})

onMounted(async () => {
  if (document.doc) await triggerOnRender()
})

watch(error, (err) => {
  if (err) {
    errorTitle.value = __(
      err.exc_type == 'DoesNotExistError'
        ? 'Document not found'
        : 'Error occurred',
    )
    errorMessage.value = __(err.messages?.[0] || 'An error occurred')
  } else {
    errorTitle.value = ''
    errorMessage.value = ''
  }
})

watch(
  () => document.doc,
  async (_doc) => {
    if (scripts.data?.length) {
      let s = await setupCustomizations(scripts.data, {
        doc: _doc,
        $dialog,
        $socket,
        router,
        toast,
        updateField,
        createToast: toast.create,
        deleteDoc: deleteLead,
        call,
      })
      document._actions = s.actions || []
      document._statuses = s.statuses || []
    }
  },
  { once: true },
)

const breadcrumbs = computed(() => {
  let items = [{ label: __('Leads'), route: { name: 'Leads' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Lead')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Leads',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: title.value,
    route: { name: 'Lead', params: { leadId: props.leadId } },
  })
  return items
})

const title = computed(() => {
  let t = doctypeMeta.value?.title_field || 'name'
  return doc.value?.[t] || props.leadId
})

const statuses = computed(() => {
  let customStatuses = document.statuses?.length
    ? document.statuses
    : document._statuses || []
  return statusOptions('lead', customStatuses, triggerStatusChange)
})

usePageMeta(() => {
  return { title: title.value, icon: brand.favicon }
})

const tabs = computed(() => {
  let tabOptions = [
    {
      name: 'Activity',
      label: __('Activity'),
      icon: ActivityIcon,
    },
    {
      name: 'Emails',
      label: __('Emails'),
      icon: EmailIcon,
    },
    {
      name: 'Comments',
      label: __('Comments'),
      icon: CommentIcon,
    },
    {
      name: 'Data',
      label: __('Data'),
      icon: DetailsIcon,
    },
    {
      name: 'Events',
      label: __('Events'),
      icon: EventIcon,
    },
    {
      name: 'Calls',
      label: __('Calls'),
      icon: PhoneIcon,
    },
    {
      name: 'Tasks',
      label: __('Tasks'),
      icon: TaskIcon,
    },
    {
      name: 'Notes',
      label: __('Notes'),
      icon: NoteIcon,
    },
    {
      name: 'Attachments',
      label: __('Attachments'),
      icon: AttachmentIcon,
    },
    {
      name: 'WhatsApp',
      label: __('WhatsApp'),
      icon: WhatsAppIcon,
      condition: () => whatsappEnabled.value,
    },
    {
      name: 'Chat',
      label: __('Chat'),
      icon: ChatIcon,
    },
  ]
  return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true))
})

const { tabIndex, changeTabTo } = useActiveTabManager(tabs, 'lastLeadTab')

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Lead'],
  params: { doctype: 'CRM Lead' },
  auto: true,
})

const leadSummary = createResource({
  url: 'crm.api.lead_management.get_lead_summary',
  cache: ['leadSummary', props.leadId],
  params: { lead: props.leadId },
  auto: true,
})

async function refreshLeadSummary() {
  await call('crm.api.lead_management.score_lead', { lead: props.leadId })
  leadSummary.reload()
}

const printing = ref(false)
async function printLead() {
  printing.value = true
  try {
    const res = await call('crm.api.lead_management.print_lead', { lead: props.leadId })
    if (res?.file_url) {
      window.open(res.file_url, '_blank')
    } else {
      toast.error('Print failed')
    }
  } catch (e) {
    toast.error(e?.message || 'Print failed')
  } finally {
    printing.value = false
  }
}

const referralEditing = ref(false)
const savingReferral = ref(false)
const referralDraft = ref({ referrer_type: '', referrer: '' })
function beginReferralEdit() {
  referralDraft.value = {
    referrer_type: uatSummary.data?.attribution?.referrer_type || '',
    referrer: uatSummary.data?.attribution?.referrer || '',
  }
  referralEditing.value = true
}
async function saveReferral() {
  savingReferral.value = true
  try {
    await call('frappe.client.set_value', {
      doctype: 'CRM Lead',
      name: props.leadId,
      fieldname: {
        referrer_type: referralDraft.value.referrer_type || '',
        referrer: referralDraft.value.referrer || '',
        referral_fee: 0,
      },
    })
    referralEditing.value = false
    uatSummary.reload()
    if (document?.reload) document.reload()
    toast.success('Referral updated')
  } catch (e) {
    toast.error(e?.message || 'Failed to save')
  } finally {
    savingReferral.value = false
  }
}
function formatRupiah(n) {
  const v = Number(n || 0)
  if (!v) return 'Rp 0'
  return 'Rp ' + v.toLocaleString('id-ID')
}

const tagPickerOpen = ref(false)
const tagSearch = ref('')
const allTags = createResource({
  url: 'crm.api.lead_management.list_tags',
  auto: true,
  cache: 'leadTags',
})
const tagSuggestions = computed(() => {
  const used = new Set((uatSummary.data?.tags || []).map((t) => t.tag.toLowerCase()))
  const q = tagSearch.value.trim().toLowerCase()
  return (allTags.data?.tags || [])
    .filter((t) => !used.has(t.tag.toLowerCase()))
    .filter((t) => !q || t.tag.toLowerCase().includes(q))
    .slice(0, 8)
})
async function applyTags(next) {
  try {
    await call('crm.api.lead_management.set_tags_for_lead', {
      lead: props.leadId,
      tags: next,
    })
    uatSummary.reload()
    allTags.reload()
  } catch (e) {
    toast.error(e?.message || 'Failed to update tags')
  }
}
async function addTag(name) {
  const current = (uatSummary.data?.tags || []).map((t) => t.tag)
  if (current.includes(name)) return
  tagPickerOpen.value = false
  tagSearch.value = ''
  await applyTags([...current, name])
}
async function addNewTag() {
  const name = tagSearch.value.trim()
  if (!name) return
  await addTag(name)
}
async function removeTag(name) {
  const next = (uatSummary.data?.tags || []).map((t) => t.tag).filter((t) => t !== name)
  await applyTags(next)
}

async function refreshDuplicates() {
  await call('crm.api.lead_management.preview_duplicates', { lead: props.leadId })
  leadSummary.reload()
}

async function triggerStatusChange(value) {
  await triggerOnChange('status', value)
  setLostReason()
}

function updateField(name, value) {
  value = Array.isArray(name) ? '' : value
  let oldValues = Array.isArray(name) ? {} : doc.value[name]

  if (Array.isArray(name)) {
    name.forEach((field) => (doc.value[field] = value))
  } else {
    doc.value[name] = value
  }

  document.save.submit(null, {
    onSuccess: () => (reload.value = true),
    onError: (err) => {
      if (Array.isArray(name)) {
        name.forEach((field) => (doc.value[field] = oldValues[field]))
      } else {
        doc.value[name] = oldValues
      }
      toast.error(err.messages?.[0] || __('Error updating field'))
    },
  })
}

function deleteLead() {
  showDeleteLinkedDocModal.value = true
}

function openEmailBox() {
  let currentTab = tabs.value[tabIndex.value]
  if (!['Emails', 'Comments', 'Activities'].includes(currentTab.name)) {
    activities.value.changeTabTo('emails')
  }
  nextTick(() => (activities.value.emailBox.show = true))
}

function statusLabel(status) {
  if (isTranslatable('CRM Lead Status')) return __(status)
  return status
}

const showLostReasonModal = ref(false)

function setLostReason() {
  if (
    getLeadStatus(document.doc.status).type !== 'Lost' ||
    (document.doc.lost_reason && document.doc.lost_reason !== 'Other') ||
    (document.doc.lost_reason === 'Other' && document.doc.lost_notes)
  ) {
    document.save.submit(null, {
      onSuccess: () => sections.reload(),
    })
    return
  }

  showLostReasonModal.value = true
}

function beforeStatusChange(data) {
  if (
    Object.hasOwn(data ?? {}, 'status') &&
    getLeadStatus(data.status).type == 'Lost'
  ) {
    setLostReason()
  } else {
    document.save.submit(null, {
      onSuccess: () => reloadResources(data),
    })
  }
}

function reloadResources(data) {
  leadSummary.reload()
  if (Object.hasOwn(data ?? {}, 'lead_owner')) {
    assignees.reload()
  }
  if (
    Object.hasOwn(data ?? {}, 'status') &&
    getLeadStatus(data.status).type != 'Lost'
  ) {
    sections.reload()
  }
}
</script>
