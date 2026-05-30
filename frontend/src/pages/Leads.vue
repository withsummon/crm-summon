<template>
  <div v-if="route.params.viewType === 'lead-ops'" class="h-full">
    <LeadOps />
  </div>
  <div v-else class="flex h-full flex-col">
    <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Leads" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="leadsListView?.customListActions && !isMobile"
        :actions="leadsListView.customListActions"
      />
      <Button
        v-if="hasSelection && !isMobile"
        variant="outline"
        :label="__('Reassign')"
        @click="openReassignDialog"
      >
        <template #prefix><FeatherIcon name="user-check" class="h-4 w-4" /></template>
      </Button>
      <Button
        v-if="hasSelection && !isMobile"
        variant="outline"
        :label="__('Close')"
        @click="openCloseDialog"
      >
        <template #prefix><FeatherIcon name="x-circle" class="h-4 w-4" /></template>
      </Button>
      <Button
        v-if="hasSelection && !isMobile"
        variant="outline"
        theme="red"
        :label="__('Delete')"
        @click="deleteSelectedLeads"
      >
        <template #prefix><FeatherIcon name="trash-2" class="h-4 w-4" /></template>
      </Button>
      <Button
        v-if="hasSelection && !isMobile"
        variant="outline"
        :label="__('Tag')"
        @click="openTagDialog"
      >
        <template #prefix><FeatherIcon name="tag" class="h-4 w-4" /></template>
      </Button>
      <Button
        v-if="selections.length === 2 && !isMobile"
        variant="outline"
        :label="__('Merge')"
        @click="openMergeDialog"
      >
        <template #prefix><FeatherIcon name="git-merge" class="h-4 w-4" /></template>
      </Button>
      <Dropdown
        :options="[
          { label: __('Export as CSV'), onClick: () => exportFilteredLeads('CSV') },
          { label: __('Export as Excel'), onClick: () => exportFilteredLeads('XLSX') },
          { label: __('Export as PDF'), onClick: () => exportFilteredLeads('PDF') },
        ]"
      >
        <template #default="{ open }">
          <Button variant="outline" :label="__('Export')" :iconRight="open ? 'chevron-up' : 'chevron-down'">
            <template #prefix>
              <FeatherIcon name="download" class="h-4 w-4" />
            </template>
          </Button>
        </template>
      </Dropdown>
      <Button
        v-if="!isMobile"
        variant="solid"
        :loading="isScraping"
        :label="__('Run Lead Gen')"
        @click="showPromptDialog = true"
      >
        <template #prefix>
          <FeatherIcon name="cpu" class="h-4 w-4" />
        </template>
      </Button>
      <Button
        v-if="!isMobile"
        variant="outline"
        :label="__('Import Excel')"
        @click="showImportDialog = true"
      >
        <template #prefix>
          <FeatherIcon name="upload" class="h-4 w-4" />
        </template>
      </Button>
      <Button
        v-if="!isMobile"
        variant="outline"
        :label="__('Lead Intake')"
        @click="showLeadIntakeDialog = true"
      >
        <template #prefix>
          <FeatherIcon name="inbox" class="h-4 w-4" />
        </template>
      </Button>
      <Button
        v-if="!isMobile"
        variant="outline"
        :label="__('Lead Ops')"
        @click="router.push('/crm-core/leads/view/lead-ops')"
      >
        <template #prefix>
          <FeatherIcon name="cpu" class="h-4 w-4" />
        </template>
      </Button>
      
      <!-- Mobile dropdown for actions -->
      <Dropdown
        v-if="isMobile"
        :options="mobileActions"
      >
        <Button variant="outline" icon="more-horizontal" />
      </Dropdown>

      <Button
        variant="solid"
        :label="isMobile ? '' : __('Create')"
        iconLeft="plus"
        @click="showLeadModal = true"
      />
      <Dropdown :options="viewModeActions">
        <Button variant="subtle" icon="layout" />
      </Dropdown>
    </template>
  </LayoutHeader>
  <LeadKpiRibbon @filter="onKpiFilter" />
  <ViewControls
    ref="viewControls"
    v-model="leads"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Lead"
    :filters="{ converted: 0 }"
    :options="{
      allowedViews: ['list', 'group_by', 'kanban', 'calendar', 'timeline'],
    }"
  />
  <KanbanView
    v-if="route.params.viewType == 'kanban'"
    v-model="leads"
    :options="{
      getRoute: (row) => ({
        name: 'Lead',
        params: { leadId: row.name },
        query: { view: route.query.view, viewType: route.params.viewType },
      }),
      onNewClick: (column) => onNewClick(column),
    }"
    @update="(data) => viewControls.updateKanbanSettings(data)"
    @loadMore="(columnName) => viewControls.loadMoreKanban(columnName)"
  >
    <template #title="{ titleField, itemName }">
      <div class="flex items-center gap-2">
        <div v-if="titleField === 'status'">
          <IndicatorIcon :class="getRow(itemName, titleField).color" />
        </div>
        <div
          v-else-if="
            titleField === 'organization' && getRow(itemName, titleField).label
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).logo"
            :label="getRow(itemName, titleField).label"
            size="sm"
          />
        </div>
        <div
          v-else-if="
            titleField === 'lead_name' && getRow(itemName, titleField).label
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).image"
            :label="getRow(itemName, titleField).image_label"
            size="sm"
          />
        </div>
        <div
          v-else-if="
            titleField === 'lead_owner' &&
            getRow(itemName, titleField).full_name
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).user_image"
            :label="getRow(itemName, titleField).full_name"
            size="sm"
          />
        </div>
        <div v-else-if="titleField === 'mobile_no'">
          <PhoneIcon class="h-4 w-4" />
        </div>
        <div
          v-if="
            [
              'modified',
              'creation',
              'first_response_time',
              'first_responded_on',
              'response_by',
            ].includes(titleField)
          "
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, titleField).label">
            <div>{{ getRow(itemName, titleField).timeAgo }}</div>
          </Tooltip>
        </div>
        <div v-else-if="titleField === 'sla_status'" class="truncate text-base">
          <Badge
            v-if="getRow(itemName, titleField).value"
            :variant="'subtle'"
            :theme="getRow(itemName, titleField).color"
            size="md"
            :label="getRow(itemName, titleField).value"
          />
        </div>
        <div
          v-else-if="getRow(itemName, titleField).label"
          class="truncate text-base"
        >
          {{ getRow(itemName, titleField).label }}
        </div>
        <div v-else class="text-ink-gray-4">{{ __('No Title') }}</div>
      </div>
    </template>
    <template #fields="{ fieldName, itemName }">
      <div
        v-if="getRow(itemName, fieldName).label"
        class="truncate flex items-center gap-2"
      >
        <div v-if="fieldName === 'status'">
          <IndicatorIcon :class="getRow(itemName, fieldName).color" />
        </div>
        <div
          v-else-if="
            fieldName === 'organization' && getRow(itemName, fieldName).label
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, fieldName).logo"
            :label="getRow(itemName, fieldName).label"
            size="xs"
          />
        </div>
        <div v-else-if="fieldName === 'lead_name'">
          <Avatar
            v-if="getRow(itemName, fieldName).label"
            class="flex items-center"
            :image="getRow(itemName, fieldName).image"
            :label="getRow(itemName, fieldName).image_label"
            size="xs"
          />
        </div>
        <div v-else-if="fieldName === 'lead_owner'">
          <Avatar
            v-if="getRow(itemName, fieldName).full_name"
            class="flex items-center"
            :image="getRow(itemName, fieldName).user_image"
            :label="getRow(itemName, fieldName).full_name"
            size="xs"
          />
        </div>
        <div
          v-if="
            [
              'modified',
              'creation',
              'first_response_time',
              'first_responded_on',
              'response_by',
            ].includes(fieldName)
          "
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, fieldName).label">
            <div>{{ getRow(itemName, fieldName).timeAgo }}</div>
          </Tooltip>
        </div>
        <div v-else-if="fieldName === 'sla_status'" class="truncate text-base">
          <Badge
            v-if="getRow(itemName, fieldName).value"
            :variant="'subtle'"
            :theme="getRow(itemName, fieldName).color"
            size="md"
            :label="getRow(itemName, fieldName).value"
          />
        </div>
        <div
          v-else-if="fieldName === '_assign'"
          class="flex items-center truncate"
        >
          <MultipleAvatar
            :avatars="getRow(itemName, fieldName).label"
            size="xs"
          />
        </div>
        <div v-else class="truncate text-base">
          {{ getRow(itemName, fieldName).label }}
        </div>
      </div>
    </template>
    <template #actions="{ itemName }">
      <div class="flex gap-2 items-center justify-between">
        <div class="text-ink-gray-5 flex items-center gap-1.5">
          <EmailAtIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_email_count').label">
            {{ getRow(itemName, '_email_count').label }}
          </span>
          <span class="text-3xl leading-[0]"> &middot; </span>
          <NoteIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_note_count').label">
            {{ getRow(itemName, '_note_count').label }}
          </span>
          <span class="text-3xl leading-[0]"> &middot; </span>
          <TaskIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_task_count').label">
            {{ getRow(itemName, '_task_count').label }}
          </span>
          <span class="text-3xl leading-[0]"> &middot; </span>
          <CommentIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_comment_count').label">
            {{ getRow(itemName, '_comment_count').label }}
          </span>
        </div>
        <Dropdown
          class="flex items-center gap-2"
          :options="actions(itemName)"
          variant="ghost"
          @click.stop.prevent
        >
          <Button icon="plus" variant="ghost" />
        </Dropdown>
      </div>
    </template>
  </KanbanView>
  <div
    v-else-if="route.params.viewType == 'calendar' && rows.length"
    class="flex h-full flex-col overflow-auto bg-surface-gray-1 p-5"
  >
    <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      <div
        v-for="row in rows"
        :key="row.name"
        class="rounded-lg border bg-white p-4 shadow-sm"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <div class="truncate text-base font-semibold text-ink-gray-9">
              {{ rowLabel(row, 'lead_name') || row.name }}
            </div>
            <div class="mt-1 truncate text-sm text-ink-gray-5">
              {{ rowLabel(row, 'organization') || rowLabel(row, 'email') || '-' }}
            </div>
          </div>
          <Badge
            v-if="rowLabel(row, 'lead_score_band')"
            :label="rowLabel(row, 'lead_score_band')"
            variant="subtle"
            theme="blue"
          />
        </div>
        <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
          <div>
            <div class="text-xs text-ink-gray-5">{{ __('Created') }}</div>
            <div class="text-ink-gray-8">{{ rowLabel(row, 'creation') }}</div>
          </div>
          <div>
            <div class="text-xs text-ink-gray-5">{{ __('SLA') }}</div>
            <div class="text-ink-gray-8">{{ rowLabel(row, 'sla_status') || '-' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div
    v-else-if="route.params.viewType == 'timeline' && rows.length"
    class="h-full overflow-auto bg-surface-gray-1 p-5"
  >
    <div class="mx-auto flex max-w-4xl flex-col gap-3">
      <div
        v-for="row in rows"
        :key="row.name"
        class="grid grid-cols-[140px_minmax(0,1fr)] gap-4 rounded-lg border bg-white p-4 shadow-sm"
      >
        <div class="text-sm text-ink-gray-5">
          {{ rowLabel(row, 'modified') || rowLabel(row, 'creation') }}
        </div>
        <div class="min-w-0">
          <div class="truncate font-semibold text-ink-gray-9">
            {{ rowLabel(row, 'lead_name') || row.name }}
          </div>
          <div class="mt-1 flex flex-wrap gap-2">
            <Badge
              v-if="rowLabel(row, 'status')"
              :label="rowLabel(row, 'status')"
              variant="subtle"
              theme="gray"
            />
            <Badge
              v-if="rowLabel(row, 'capture_channel')"
              :label="rowLabel(row, 'capture_channel')"
              variant="subtle"
              theme="teal"
            />
            <Badge
              v-if="rowLabel(row, 'lead_score_band')"
              :label="rowLabel(row, 'lead_score_band')"
              variant="subtle"
              theme="blue"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
  <LeadsListView
    v-else-if="leads.data && rows.length"
    ref="leadsListView"
    v-model="leads.data.page_length_count"
    v-model:list="leads"
    :rows="rows"
    :columns="columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      selectable: true,
      rowCount: leads.data.row_count,
      totalCount: leads.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="updateSelections"
    @previewLead="onPreviewLead"
    @openScoring="onOpenScoring"
  />
  <EmptyState
    v-else-if="leads.data && !rows.length"
    name="Leads"
    :icon="LeadsIcon"
  />
  <LeadModal
    v-if="showLeadModal"
    v-model="showLeadModal"
    :defaults="defaults"
    @created="onLeadsImported"
  />
  <LeadGenDialog
    v-model="showImportDialog"
    @imported="onLeadsImported"
  />
  <ScrapingAnimation
    v-model="isScraping"
    :progress="scrapingProgress"
    :totalCount="scrapingTotal"
    :processedCount="scrapingProcessed"
  />
  <Dialog
    v-model="showLeadIntakeDialog"
    :options="{
      title: __('Lead Intake'),
      size: 'md',
      actions: [
        {
          label: __('Create Lead'),
          variant: 'solid',
          loading: intakeLoading,
          onClick: captureLeadFromIntake,
        },
      ],
    }"
  >
    <template #body-content>
      <div class="space-y-4 py-3">
        <div>
          <label class="mb-1 block text-xs font-medium uppercase tracking-wide text-ink-gray-5">
            {{ __('Intake Channel') }}
          </label>
          <select
            v-model="intakeDraft.channel"
            class="w-full rounded border border-outline-gray-2 px-3 py-2 text-sm"
            @change="syncIntakeSource"
          >
            <option v-for="channel in intakeChannels" :key="channel.value" :value="channel.value">
              {{ channel.label }}
            </option>
          </select>
        </div>
        <div class="grid gap-3 sm:grid-cols-2">
          <FormControl v-model="intakeDraft.lead_name" :label="__('Full Name')" />
          <FormControl v-model="intakeDraft.organization" :label="__('Organization')" />
          <FormControl v-model="intakeDraft.email" :label="__('Email')" />
          <FormControl v-model="intakeDraft.mobile_no" :label="__('Mobile No.')" />
          <FormControl v-model="intakeDraft.source" :label="__('Lead Source')" />
          <FormControl v-model="intakeDraft.campaign" :label="__('Campaign')" />
          <FormControl v-model="intakeDraft.referrer_type" :label="__('Referrer Type')" />
          <FormControl v-model="intakeDraft.referrer" :label="__('Referrer')" />
          <FormControl v-model="intakeDraft.referral_fee" :label="__('Referral Fee')" type="number" />
          <FormControl v-model="intakeDraft.npwp" :label="__('NPWP / Tax ID')" />
          <FormControl v-model="intakeDraft.utm_source" :label="__('UTM Source')" />
          <FormControl v-model="intakeDraft.utm_medium" :label="__('UTM Medium')" />
          <FormControl v-model="intakeDraft.utm_campaign" :label="__('UTM Campaign')" />
          <FormControl v-model="intakeDraft.utm_content" :label="__('UTM Content')" />
        </div>
      </div>
    </template>
  </Dialog>
  <Dialog
    v-model="showPromptDialog"
    :options="{
      title: __('Run Lead Gen'),
      size: 'sm',
      actions: [
        {
          label: __('Run Engine'),
          variant: 'solid',
          onClick: () => {
            showPromptDialog = false
            runMockScraping()
          }
        }
      ]
    }"
  >
    <template #body-content>
      <div class="py-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">{{ __('Scraping Prompt') }}</label>
        <textarea
          v-model="promptText"
          rows="3"
          :placeholder="__('E.g. Carikan saya 10 software engineer di jakarta...')"
          class="w-full resize-none rounded-md border border-gray-300 p-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        ></textarea>
        <p class="mt-2 text-xs text-gray-500">
          {{ __('AI will use this prompt to find matching leads in the global database.') }}
        </p>
      </div>
    </template>
  </Dialog>

  <!-- Reassign Dialog -->
  <Dialog v-model="reassignDialog.open" :options="{ title: __('Reassign Leads') }">
    <template #body-content>
      <div class="space-y-3">
        <p class="text-sm text-ink-gray-7">{{ __('{0} leads selected').replace('{0}', selections.length) }}</p>
        <div>
          <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Assignee') }}</label>
          <select v-model="reassignDialog.toUser" class="mt-1 w-full rounded border border-outline-gray-2 px-3 py-2 text-sm">
            <option v-for="u in users" :key="u.name" :value="u.name">{{ u.full_name || u.name }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Reason') }}</label>
          <textarea v-model="reassignDialog.reason" rows="2" class="mt-1 w-full rounded border border-outline-gray-2 px-3 py-2 text-sm" :placeholder="__('Mandatory reason…')"></textarea>
        </div>
      </div>
    </template>
    <template #actions>
      <Button variant="ghost" label="Cancel" @click="reassignDialog.open = false" />
      <Button variant="solid" :disabled="!canReassign" @click="submitReassign().then(() => (reassignDialog.open = false))">{{ __('Reassign') }}</Button>
    </template>
  </Dialog>

  <!-- Tag Dialog -->
  <Dialog v-model="tagDialog.open" :options="{ title: __('Tag Leads') }">
    <template #body-content>
      <div class="space-y-3">
        <p class="text-sm text-ink-gray-7">{{ __('{0} leads selected').replace('{0}', selections.length) }}</p>
        <div>
          <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Tag') }}</label>
          <input v-model="tagDialog.tag" class="mt-1 w-full rounded border border-outline-gray-2 px-3 py-2 text-sm" placeholder="e.g. Hot, Cross-sell" />
        </div>
        <div>
          <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Color') }}</label>
          <input v-model="tagDialog.color" type="color" class="mt-1 h-8 w-full rounded border border-outline-gray-2" />
        </div>
      </div>
    </template>
    <template #actions>
      <Button variant="ghost" label="Cancel" @click="tagDialog.open = false" />
      <Button variant="solid" :disabled="!canTag" @click="submitTag().then(() => (tagDialog.open = false))">{{ __('Tag') }}</Button>
    </template>
  </Dialog>

  <!-- Async Export Dialog -->
  <Dialog v-model="exportDialog.open" :options="{ title: __('Export Leads') }">
    <template #body-content>
      <div class="space-y-3">
        <p class="text-sm text-ink-gray-7">{{ __('This export contains {0} leads.').replace('{0}', exportDialog.rowCount) }}</p>
        <div v-if="exportDialog.rowCount > 1000">
          <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Email when ready') }}</label>
          <input v-model="exportDialog.email" type="email" class="mt-1 w-full rounded border border-outline-gray-2 px-3 py-2 text-sm" />
        </div>
        <div v-else>
          <p class="text-sm text-ink-gray-5">{{ __('A direct download will start after confirmation.') }}</p>
        </div>
      </div>
    </template>
    <template #actions>
      <Button variant="ghost" label="Cancel" @click="exportDialog.open = false" />
      <Button variant="solid" @click="confirmExport().then(() => (exportDialog.open = false))">{{ __('Export') }}</Button>
    </template>
  </Dialog>

  <!-- Quick View Popover -->
  <LeadQuickView
    :visible="quickView.visible"
    :lead-name="quickView.leadName"
    :position-style="quickView.style"
    @close="quickView.visible = false"
  />

  <!-- Scoring Drawer -->
  <LeadScoringDrawer
    v-model:visible="scoringDrawer.open"
    :lead-name="scoringDrawer.leadName"
    @changed="onLeadsImported"
  />

  <!-- Close Dialog -->
  <Dialog v-model="closeDialog.open" :options="{ title: __('Close Leads') }">
    <template #body-content>
      <div class="space-y-3">
        <p class="text-sm text-ink-gray-7">{{ __(`${selections.length} leads selected`) }}</p>
        <div>
          <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Close Reason') }}</label>
          <textarea v-model="closeDialog.reason" rows="2" class="mt-1 w-full rounded border border-outline-gray-2 px-3 py-2 text-sm" :placeholder="__('Mandatory reason…')"></textarea>
        </div>
      </div>
    </template>
    <template #actions>
      <Button variant="ghost" label="Cancel" @click="closeDialog.open = false" />
      <Button variant="solid" :disabled="!closeDialog.reason.trim()" @click="submitClose().then(() => (closeDialog.open = false))">{{ __('Close Leads') }}</Button>
    </template>
  </Dialog>

  <!-- Merge Dialog -->
  <Dialog v-model="mergeDialog.open" :options="{ title: __('Merge Leads') }">
    <template #body-content>
      <div class="space-y-3">
        <p class="text-sm text-ink-gray-7">{{ __('Select which lead to keep as the primary record.') }}</p>
        <div class="space-y-2">
          <label
            v-for="name in mergeDialog.candidates"
            :key="name"
            class="flex cursor-pointer items-center gap-3 rounded-md border border-outline-gray-2 px-3 py-2"
            :class="mergeDialog.primary === name ? 'border-crm-teal bg-crm-teal/5' : ''"
          >
            <input v-model="mergeDialog.primary" type="radio" :value="name" />
            <span class="text-sm font-medium text-ink-gray-9">{{ name }}</span>
          </label>
        </div>
      </div>
    </template>
    <template #actions>
      <Button variant="ghost" label="Cancel" @click="mergeDialog.open = false" />
      <Button variant="solid" :disabled="!mergeDialog.primary" @click="submitMerge().then(() => (mergeDialog.open = false))">{{ __('Merge') }}</Button>
    </template>
  </Dialog>
  </div>
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import CustomActions from '@/components/CustomActions.vue'
import EmailAtIcon from '@/components/Icons/EmailAtIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import LeadsListView from '@/components/ListViews/LeadsListView.vue'
import EmptyState from '@/components/ListViews/EmptyState.vue'
import LeadKpiRibbon from '@/components/LeadKpiRibbon.vue'
import LeadQuickView from '@/components/LeadQuickView.vue'
import LeadScoringDrawer from '@/components/LeadScoringDrawer.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import LeadModal from '@/components/Modals/LeadModal.vue'
import LeadGenDialog from '@/components/LeadGenDialog.vue'
import ScrapingAnimation from '@/components/ScrapingAnimation.vue'
import ViewControls from '@/components/ViewControls.vue'
import LeadOps from '@/pages/LeadOps.vue'
import { backgroundStore } from '@/stores/background'
import { useDoctypeModal } from '@/composables/doctypeModal'
import { getMeta } from '@/stores/meta'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { callEnabled } from '@/composables/telephony'
import { useBroadcast } from '@/composables/useBroadcast'
import { formatDate, timeAgo, website, formatTime, formatCurrency } from '@/utils'
import { useOnboarding, useTelemetry } from 'frappe-ui/frappe'
import {
  Avatar,
  Badge,
  Dialog,
  FormControl,
  Tooltip,
  Dropdown,
  FeatherIcon,
  toast,
  call,
} from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import { ref, computed, reactive, h, onMounted, onUnmounted, watch, toRefs, onActivated } from 'vue'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Lead')
const { makeCall } = globalStore()
const { getUser } = usersStore()
const { getLeadStatus } = statusesStore()
const { on } = useBroadcast()
const { updateOnboardingStep } = useOnboarding('frappecrm')
const { capture } = useTelemetry()
const { showModal } = useDoctypeModal()

const { isScraping, scrapingProgress, scrapingTotal, scrapingProcessed } = toRefs(backgroundStore())
const { startScraping, updateProgress, stopScraping } = backgroundStore()

const route = useRoute()
const router = useRouter()

const leadsListView = ref(null)
const showLeadModal = ref(false)
const showImportDialog = ref(false)
const showPromptDialog = ref(false)
const showLeadIntakeDialog = ref(false)
const intakeLoading = ref(false)
const promptText = ref('')
const intakeChannels = [
  { value: 'Web Form', label: __('Web Form') },
  { value: 'WhatsApp', label: 'WhatsApp' },
  { value: 'Email', label: 'Email' },
  { value: 'Walk-in', label: __('Walk-in') },
  { value: 'Referral', label: __('Referral') },
  { value: 'Campaign', label: __('Campaign') },
  { value: 'Widget', label: __('Web Widget') },
  { value: 'Mobile', label: __('Mobile App') },
  { value: 'OCR', label: __('ID OCR') },
]
const intakeDraft = reactive({
  channel: 'Web Form',
  lead_name: '',
  organization: '',
  email: '',
  mobile_no: '',
  source: 'Web Form',
  campaign: '',
  referrer_type: '',
  referrer: '',
  referral_fee: '',
  npwp: '',
  utm_source: '',
  utm_medium: '',
  utm_campaign: '',
  utm_content: '',
})

const selections = ref([])
const hasSelection = computed(() => selections.value.length > 0)

const quickView = reactive({ visible: false, leadName: '', style: {} })
const scoringDrawer = reactive({ open: false, leadName: '' })
const reassignDialog = reactive({ open: false, toUser: '', reason: '' })
const tagDialog = reactive({ open: false, tag: '', color: '#0f766e' })
  const exportDialog = reactive({ open: false, rowCount: 0, email: '', format: 'CSV' })
  const mergeDialog = reactive({ open: false, candidates: [], primary: '' })
  const closeDialog = reactive({ open: false, reason: '' })

  const users = ref([])

const viewModeActions = computed(() => [
  {
    label: __('List'),
    onClick: () => router.push({ name: 'Leads', params: { viewType: 'list' } }),
  },
  {
    label: __('Kanban'),
    onClick: () => router.push({ name: 'Leads', params: { viewType: 'kanban' } }),
  },
  {
    label: __('Calendar'),
    onClick: () => router.push({ name: 'Leads', params: { viewType: 'calendar' } }),
  },
  {
    label: __('Timeline'),
    onClick: () => router.push({ name: 'Leads', params: { viewType: 'timeline' } }),
  },
  {
    label: __('Lead Ops'),
    onClick: () => router.push('/crm-core/leads/view/lead-ops'),
  },
])


async function runMockScraping() {
  let count = 15;
  const matchCount = promptText.value.match(/\b(\d+)\b/);
  if (matchCount) {
    count = Math.min(parseInt(matchCount[1], 10), 50);
  }
  startScraping(count)

  // Simulate progress
  const progressInterval = setInterval(() => {
    if (scrapingProgress.value < 90) {
      updateProgress(scrapingProcessed.value + 1)
    }
  }, 800)

  try {
    const res = await call('crm.api.lead_gen.mock_lead_scraping', {
      prompt: promptText.value
    })
    
    // Clear prompt text after successful execution
    promptText.value = ''
    clearInterval(progressInterval)
    updateProgress(scrapingTotal.value)

    // Small delay to show 100% before closing
    setTimeout(() => {
      stopScraping()
      if (typeof toast === 'function') {
        toast({
          title: __('Lead Gen Complete'),
          text: res.message,
          icon: 'check-circle',
          iconClasses: 'text-green-600',
        })
      } else {
        toast.success(res.message)
      }
      onLeadsImported()
    }, 1000)

  } catch (e) {
    clearInterval(progressInterval)
    stopScraping()
    toast.error(__('Lead Gen Failed: {0}', [e.message || 'Unknown error']))
  }
}

on('trigger_lead_create', (data) => {
  showLeadModal.value = Boolean(data)
})

// Real-time listener for scraping and list updates
on('lead_gen_start', (data) => {
  startScraping(data.total || 10)
})

on('lead_scraped', (data) => {
  onLeadsImported()
  if (data.count !== undefined) {
    updateProgress(data.count, data.lead)
  }
})

on('lead_gen_complete', () => {
  stopScraping()
  onLeadsImported()
})

on('list_update', () => {
  onLeadsImported()
})

// Polling fallback when socket is broken
let refreshInterval = null
watch(isScraping, (value) => {
  if (value) {
    refreshInterval = setInterval(() => {
      onLeadsImported()
    }, 5000) // Poll every 5 seconds during scraping
  } else {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
    // Final refresh when done
    onLeadsImported()
  }
})

// Tab focus refresh (safety net)
const handleFocus = () => {
  onLeadsImported()
}

const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

const mobileActions = computed(() => {
  const actions = []
  
  actions.push({
    label: __('Lead Intake'),
    onClick: () => { showLeadIntakeDialog.value = true }
  })
  actions.push({
    label: __('Import Excel'),
    onClick: () => { showImportDialog.value = true }
  })
  actions.push({
    label: __('Run Lead Gen'),
    onClick: () => { showPromptDialog.value = true }
  })
  actions.push({
    label: __('Export'),
    onClick: () => { exportFilteredLeads() }
  })
  
  return actions
})


onMounted(async () => {
  window.addEventListener('focus', handleFocus)
  checkMobile()
  window.addEventListener('resize', checkMobile)
  try {
    users.value = await call('frappe.client.get_list', {
      doctype: 'User',
      fields: ['name', 'full_name'],
      filters: { enabled: 1, user_type: 'System User' },
      limit_page_length: 50,
    })
  } catch (e) {
    users.value = []
  }
})

onUnmounted(() => {
  window.removeEventListener('focus', handleFocus)
  window.removeEventListener('resize', checkMobile)
})

onActivated(() => {
  if (leads.value && typeof leads.value.reload === 'function') {
    leads.value.reload()
  }
})

const defaults = reactive({})

const leads = ref({})
const loadMore = ref(false)
const triggerResize = ref(false)
const updatedPageCount = ref(20)
const viewControls = ref(null)

function updateSelections(selectedRows = []) {
  viewControls.value?.updateSelections?.(selectedRows)
  selections.value = (selectedRows || []).map((row) => row.name).filter(Boolean)
}



function onLeadsImported() {
  // Reload the resource directly - this is the most efficient way
  if (leads.value && typeof leads.value.reload === 'function') {
    leads.value.reload()
  }
}

function resetIntakeDraft() {
  Object.assign(intakeDraft, {
    channel: 'Web Form',
    lead_name: '',
    organization: '',
    email: '',
    mobile_no: '',
    source: 'Web Form',
    campaign: '',
    referrer_type: '',
    referrer: '',
    referral_fee: '',
    npwp: '',
    utm_source: '',
    utm_medium: '',
    utm_campaign: '',
    utm_content: '',
  })
}

function syncIntakeSource() {
  intakeDraft.source = intakeDraft.channel
  if (intakeDraft.channel === 'Referral' && !intakeDraft.referrer_type) {
    intakeDraft.referrer_type = 'Customer'
  }
  if (intakeDraft.channel === 'Campaign' && !intakeDraft.campaign) {
    intakeDraft.campaign = intakeDraft.utm_campaign || 'Campaign Intake'
  }
}

async function captureLeadFromIntake(close) {
  intakeLoading.value = true
  try {
    const result = await call('crm.api.lead_management.capture_lead', {
      data: intakeDraft,
      channel: intakeDraft.channel || intakeDraft.source || 'Web Form',
    })
    if (result.created) {
      toast.success(__('Lead created'))
      resetIntakeDraft()
      showLeadIntakeDialog.value = false
      close?.()
      onLeadsImported()
      router.push({ name: 'Lead', params: { leadId: result.lead } })
    } else {
      toast.error(__('Duplicate lead found. Review duplicate candidates before creating.'))
    }
  } finally {
    intakeLoading.value = false
  }
}

async function exportFilteredLeads(format = 'CSV') {
  const filters = {
    converted: 0,
    ...(leads.value?.params?.filters || {}),
  }
  exportDialog.format = format
  const result = await call('crm.api.lead_management.export_leads', {
    filters,
    format,
  })
  if (result.async && result.row_count > 1000) {
    exportDialog.rowCount = result.row_count
    exportDialog.open = true
    return
  }
  if (result.file_url) {
    window.open(result.file_url, '_blank')
  }
  toast.success(__('Lead export prepared'))
}

async function confirmExport() {
  const filters = { converted: 0, ...(leads.value?.params?.filters || {}) }
  const result = await call('crm.api.lead_management.export_leads', {
    filters,
    format: exportDialog.format || 'CSV',
    email_to: exportDialog.email || undefined,
  })
  if (result.file_url) {
    window.open(result.file_url, '_blank')
  }
  toast.success(result.async ? __('Export queued. You will be emailed when ready.') : __('Lead export prepared'))
}

function openReassignDialog() {
  reassignDialog.toUser = ''
  reassignDialog.reason = ''
  reassignDialog.open = true
}

const canReassign = computed(() => reassignDialog.toUser && reassignDialog.reason.trim())

async function submitReassign() {
  try {
    await call('crm.api.lead_management.reassign_leads', {
      leads: selections.value,
      to_user: reassignDialog.toUser,
      reason: reassignDialog.reason,
    })
    toast.success(__('Leads reassigned'))
    onLeadsImported()
    updateSelections([])
  } catch (e) {
    toast.error(e?.message || __('Reassign failed'))
  }
}

function openTagDialog() {
  tagDialog.tag = ''
  tagDialog.color = '#0f766e'
  tagDialog.open = true
}

const canTag = computed(() => tagDialog.tag.trim())

async function submitTag() {
  try {
    await call('crm.api.lead_management.bulk_tag_leads', {
      leads: selections.value,
      tag: tagDialog.tag,
      color: tagDialog.color,
    })
    toast.success(__('Tags applied'))
    onLeadsImported()
    updateSelections([])
  } catch (e) {
    toast.error(e?.message || __('Tagging failed'))
  }
}

function onKpiFilter(key) {
  if (!viewControls.value) return
  const list = viewControls.value.list
  if (!list) return
  let filters = { ...list.value.params.filters }
  if (key === 'new_today') {
    filters.creation = new Date().toISOString().slice(0, 10)
  } else if (key === 'aging_stale') {
    filters.last_activity_on = ['<=', addDays(new Date(), -14).toISOString().slice(0, 10)]
  } else if (key === 'sla_breaching') {
    filters.sla_status = ['in', ['At Risk', 'Breached', 'Failed']]
  } else if (key === 'dedupe_pending') {
    router.push({ name: 'Leads', params: { viewType: 'list' }, query: { ...route.query, dedupe: '1' } })
    return
  }
  list.value.params.filters = filters
  list.value.reload()
}

function addDays(date, days) {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

function onPreviewLead({ name, event }) {
  const rect = event.target.closest('tr')?.getBoundingClientRect?.() || event.target.getBoundingClientRect()
  quickView.leadName = name
  quickView.style = {
    top: `${rect.top + window.scrollY + 24}px`,
    left: `${Math.min(rect.left + window.scrollX, window.innerWidth - 380)}px`,
  }
  quickView.visible = true
}

function onOpenScoring(name) {
  scoringDrawer.leadName = name
  scoringDrawer.open = true
}

function openCloseDialog() {
  closeDialog.reason = ''
  closeDialog.open = true
}

async function submitClose() {
  try {
    for (const name of selections.value) {
      await call('crm.api.lead_management.close_lead', { name, reason: closeDialog.reason })
    }
    toast.success(__('Leads closed'))
    onLeadsImported()
    updateSelections([])
  } catch (e) {
    toast.error(e?.message || __('Close failed'))
  }
}

async function deleteSelectedLeads() {
  if (!selections.value.length) return
  if (!confirm(__('Are you sure you want to delete the selected leads?'))) return
  try {
    for (const name of selections.value) {
      await call('crm.api.lead_management.delete_lead', { name })
    }
    toast.success(__('Leads deleted'))
    onLeadsImported()
    updateSelections([])
  } catch (e) {
    toast.error(e?.message || __('Delete failed'))
  }
}

function openMergeDialog() {
  if (selections.value.length !== 2) return
  mergeDialog.candidates = [...selections.value]
  mergeDialog.primary = selections.value[0]
  mergeDialog.open = true
}

async function submitMerge() {
  try {
    const primary = mergeDialog.primary
    const duplicate = mergeDialog.candidates.find((n) => n !== primary)
    await call('crm.api.lead_management.merge_leads', { primary, duplicate })
    toast.success(__('Leads merged'))
    onLeadsImported()
    updateSelections([])
  } catch (e) {
    toast.error(e?.message || __('Merge failed'))
  }
}

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

function rowLabel(row, field) {
  const value = row?.[field]
  if (value && typeof value === 'object') {
    return value.value || value.label || value.full_name || ''
  }
  return value || ''
}

// Rows
const rows = computed(() => {
  if (!leads.value?.data?.data) return []
  if (leads.value.data.view_type === 'group_by') {
    if (!leads.value?.data.group_by_field?.fieldname) return []
    return getGroupedByRows(
      leads.value?.data.data,
      leads.value?.data.group_by_field,
      leads.value.data.columns,
    )
  } else if (leads.value.data.view_type === 'kanban') {
    return getKanbanRows(leads.value.data.data, leads.value.data.fields)
  } else {
    return parseRows(leads.value?.data.data, leads.value.data.columns)
  }
})

const columns = computed(() => {
  let _columns = leads.value?.data?.columns || []

  // Set align right for last column
  if (_columns.length) {
    _columns = _columns.map((col, index) => {
      if (index === _columns.length - 1) {
        return { ...col, align: 'right' }
      }
      return col
    })
  }

  return _columns
})

function getGroupedByRows(listRows, groupByField, columns) {
  let groupedRows = []

  groupByField.options?.forEach((option) => {
    let filteredRows

    if (!option) {
      filteredRows = listRows.filter((row) => !row[groupByField.fieldname])
    } else {
      filteredRows = listRows.filter(
        (row) => row[groupByField.fieldname] == option,
      )
    }

    let groupDetail = {
      label: groupByField.label,
      group: option || __(' '),
      collapsed: false,
      rows: parseRows(filteredRows, columns),
    }
    if (groupByField.fieldname == 'status') {
      groupDetail.icon = () =>
        h(IndicatorIcon, {
          class: getLeadStatus(option)?.color,
        })
    }
    groupedRows.push(groupDetail)
  })

  return groupedRows || listRows
}

function getKanbanRows(data, columns) {
  let _rows = []
  data.forEach((column) => {
    column.data?.forEach((row) => {
      _rows.push(row)
    })
  })
  return parseRows(_rows, columns)
}

function parseRows(rows, columns = []) {
  let view_type = leads.value.data.view_type
  let key = view_type === 'kanban' ? 'fieldname' : 'key'
  let type = view_type === 'kanban' ? 'fieldtype' : 'type'

  return rows.map((lead) => {
    let _rows = {}
    leads.value?.data.rows.forEach((row) => {
      _rows[row] = lead[row]

      let fieldType = columns?.find((col) => (col[key] || col.value) == row)?.[
        type
      ]

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(lead[row], '', true, fieldType == 'Datetime')
      }

      if (fieldType && fieldType == 'Currency') {
        _rows[row] = formatCurrency(lead[row], '', 'IDR', 0)
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, lead)
      }

      if (fieldType && fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, lead)
      }

      if (row == 'lead_name') {
        _rows[row] = {
          label: lead.lead_name,
          image: lead.image,
          image_label: lead.first_name,
        }
      } else if (row == 'organization') {
        _rows[row] = lead.organization
      } else if (row === 'website') {
        _rows[row] = website(lead.website)
      } else if (row == 'status') {
        _rows[row] = {
          label: lead.status,
          color: getLeadStatus(lead.status)?.color,
        }
      } else if (row == 'sla_status') {
        let value = lead.sla_status
        let tooltipText = value
        let color =
          lead.sla_status == 'Failed'
            ? 'red'
            : lead.sla_status == 'Fulfilled'
              ? 'green'
              : 'orange'
        if (value == 'First Response Due' || value == 'Rolling Response Due') {
          value = __(timeAgo(lead.response_by))
          tooltipText = formatDate(lead.response_by)
          if (new Date(lead.response_by) < new Date()) {
            color = 'red'
          }
        }
        _rows[row] = {
          label: tooltipText,
          value: value,
          color: color,
        }
      } else if (row == 'lead_owner') {
        _rows[row] = {
          label: lead.lead_owner && getUser(lead.lead_owner).full_name,
          ...(lead.lead_owner && getUser(lead.lead_owner)),
        }
      } else if (row == '_assign') {
        let assignees = JSON.parse(lead._assign || '[]')
        _rows[row] = assignees.map((user) => ({
          name: user,
          image: getUser(user).user_image,
          label: getUser(user).full_name,
        }))
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(lead[row]),
          timeAgo: __(timeAgo(lead[row])),
        }
      } else if (
        ['first_response_time', 'first_responded_on', 'response_by'].includes(
          row,
        )
      ) {
        let field = row == 'response_by' ? 'response_by' : 'first_responded_on'
        _rows[row] = {
          label: lead[field] ? formatDate(lead[field]) : '',
          timeAgo: lead[row]
            ? row == 'first_response_time'
              ? formatTime(lead[row])
              : __(timeAgo(lead[row]))
            : '',
        }
      }
    })
    _rows['_email_count'] = lead._email_count
    _rows['_note_count'] = lead._note_count
    _rows['_task_count'] = lead._task_count
    _rows['_comment_count'] = lead._comment_count
    return _rows
  })
}

function onNewClick(column) {
  let column_field = leads.value.params.column_field

  if (column_field) {
    defaults[column_field] = column.column.name
  }

  showLeadModal.value = true
}

function actions(itemName) {
  let mobile_no = getRow(itemName, 'mobile_no')?.label || ''
  let actions = [
    {
      icon: h(PhoneIcon, { class: 'h-4 w-4' }),
      label: __('Make a Call'),
      onClick: () => makeCall(mobile_no),
      condition: () => mobile_no && callEnabled.value,
    },
    {
      icon: h(NoteIcon, { class: 'h-4 w-4' }),
      label: __('New Note'),
      onClick: () => showNote(itemName),
    },
    {
      icon: h(TaskIcon, { class: 'h-4 w-4' }),
      label: __('New Task'),
      onClick: () => showTask(itemName),
    },
  ]
  return actions.filter((action) =>
    action.condition ? action.condition() : true,
  )
}

function showNote(name) {
  showModal({
    doctype: 'FCRM Note',
    title: 'Note',
    defaults: {
      reference_doctype: 'CRM Lead',
      reference_docname: name,
    },
    callbacks: {
      afterInsert: (d) => after(d, true),
      afterUpdate: after,
    },
  })
}

function showTask(name) {
  showModal({
    doctype: 'CRM Task',
    title: 'Task',
    defaults: {
      reference_doctype: 'CRM Lead',
      reference_docname: name,
    },
    callbacks: {
      afterInsert: (d) => after(d, true),
      afterUpdate: after,
    },
  })
}

function after(d, isNew = false) {
  let a = d.doctype == 'FCRM Note' ? 'note' : 'task'
  if (isNew) {
    updateOnboardingStep('create_first_' + a)
    capture(a + '_created')
  } else {
    capture(a + '_updated')
  }
}
</script>
