<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <ViewBreadcrumbs v-model="viewControls" routeName="Committee Approval" />
      </template>
      <template #right-header>
        <div
          v-if="ctx.data?.user_full_name"
          class="ml-6 flex items-center gap-1.5 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-2.5 py-1.5"
        >
          <FeatherIcon name="user" class="h-3.5 w-3.5 text-ink-gray-5" />
          <span class="text-sm font-medium text-ink-gray-8">{{ ctx.data.user_full_name }}</span>
        </div>
      </template>
    </LayoutHeader>

    <!-- Tab strip -->
    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-5">
      <div class="flex items-center justify-between gap-4">
        <div class="flex gap-5">
          <button
            v-for="tab in TABS"
            :key="tab.view"
            class="border-b-2 py-2.5 text-base transition-colors whitespace-nowrap"
            :class="activeView === tab.view
              ? 'border-ink-gray-8 font-medium text-ink-gray-9'
              : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
            @click="navigate(tab.view)"
          >
            {{ tab.label }}
          </button>
        </div>
        <div class="flex shrink-0 items-center gap-2 py-1.5">
          <Button
            v-if="activeView === 'decisions'"
            variant="outline"
            size="sm"
            label="Export CSV"
            @click="exportDecisions"
          >
            <template #prefix><FeatherIcon name="download" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'setup'"
            variant="solid"
            size="sm"
            label="New Committee"
            @click="openNewCommittee"
          >
            <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
          </Button>
          <Button
            v-if="activeView === 'calendar'"
            variant="solid"
            size="sm"
            label="Refresh"
            @click="meetings.reload()"
          >
            <template #prefix><FeatherIcon name="refresh-cw" class="h-4 w-4" /></template>
          </Button>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto bg-surface-gray-1">
      <div class="w-full px-10 py-6">

        <!-- ── QUEUE ─────────────────────────────────────────────────────── -->
        <template v-if="activeView === 'queue'">
          <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 class="text-xl font-semibold text-ink-gray-9">{{ __('Pending Decisions') }}</h2>
              <p class="mt-1 text-sm text-ink-gray-5">
                {{ __('Applications awaiting committee vote, sorted by SLA.') }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <select
                v-model="queueFilters.committee"
                class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8"
                @change="queue.reload()"
              >
                <option value="">{{ __('All committees') }}</option>
                <option v-for="c in ctx.data?.committees || []" :key="c.name" :value="c.name">
                  {{ c.committee_name }}
                </option>
              </select>
              <select
                v-model="queueFilters.sort_by"
                class="rounded-md border border-outline-gray-2 bg-white px-3 py-1.5 text-sm text-ink-gray-8"
                @change="queue.reload()"
              >
                <option value="sla">{{ __('Sort: SLA') }}</option>
                <option value="amount">{{ __('Sort: Amount') }}</option>
                <option value="submitted">{{ __('Sort: Submitted') }}</option>
              </select>
              <label class="flex items-center gap-1.5 text-sm text-ink-gray-7">
                <input
                  v-model="queueFilters.my_pending_only"
                  type="checkbox"
                  class="rounded border-outline-gray-3"
                  @change="queue.reload()"
                />
                {{ __('My pending only') }}
              </label>
              <Button variant="solid" size="sm" label="New Item" @click="openNewItemDialog">
                <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
              </Button>
            </div>
          </div>

          <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm">
            <div v-if="queue.loading" class="flex h-40 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else-if="!queueRows.length" class="flex flex-col items-center justify-center px-6 py-16 text-center">
              <FeatherIcon name="inbox" class="mb-3 h-8 w-8 text-ink-gray-3" />
              <p class="text-base font-medium text-ink-gray-8">{{ __('No pending decisions') }}</p>
              <p class="mt-1 text-sm text-ink-gray-5">
                {{ __('Items routed to your committee will appear here.') }}
              </p>
            </div>
            <table v-else class="w-full text-sm">
              <thead class="border-b border-outline-gray-2 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-4 py-2.5 font-medium">{{ __('Applicant') }}</th>
                  <th class="px-4 py-2.5 font-medium">{{ __('Facility') }}</th>
                  <th class="px-4 py-2.5 font-medium text-right">{{ __('Amount') }}</th>
                  <th class="px-4 py-2.5 font-medium">{{ __('Committee') }}</th>
                  <th class="px-4 py-2.5 font-medium">{{ __('Quorum') }}</th>
                  <th class="px-4 py-2.5 font-medium">{{ __('SLA') }}</th>
                  <th class="px-4 py-2.5 font-medium text-right">{{ __('') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in queueRows"
                  :key="row.name"
                  class="border-b border-outline-gray-1 last:border-b-0 hover:bg-surface-gray-1"
                >
                  <td class="px-4 py-3">
                    <div class="font-medium text-ink-gray-9">{{ row.applicant_name }}</div>
                    <div class="text-xs text-ink-gray-5">{{ row.application }}</div>
                  </td>
                  <td class="px-4 py-3 text-ink-gray-7">{{ row.facility_type || '—' }}</td>
                  <td class="px-4 py-3 text-right font-medium text-ink-gray-8">
                    {{ formatRp(row.requested_amount) }}
                  </td>
                  <td class="px-4 py-3 text-ink-gray-7">{{ row.committee }}</td>
                  <td class="px-4 py-3">
                    <QuorumBar :tally="row.tally" />
                  </td>
                  <td class="px-4 py-3">
                    <Badge :label="slaLabel(row)" :theme="slaTheme(row.sla_state)" variant="subtle" />
                  </td>
                  <td class="px-4 py-3 text-right">
                    <Button size="sm" variant="solid" label="Review" @click="openReview(row.name)">
                      <template #suffix><FeatherIcon name="arrow-right" class="h-3.5 w-3.5" /></template>
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- ── REVIEW ────────────────────────────────────────────────────── -->
        <template v-else-if="activeView === 'review'">
          <button
            class="mb-3 flex items-center gap-1 text-sm text-ink-gray-5 hover:text-ink-gray-9"
            @click="navigate('queue')"
          >
            <FeatherIcon name="arrow-left" class="h-3.5 w-3.5" /> {{ __('Back to queue') }}
          </button>

          <div v-if="review.loading" class="flex h-48 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>

          <div v-else-if="review.data" class="grid gap-5 lg:grid-cols-[2fr_1fr]">
            <!-- LEFT: review material -->
            <div class="space-y-5">
              <!-- summary -->
              <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
                <div class="flex items-start justify-between gap-4">
                  <div>
                    <h2 class="text-lg font-semibold text-ink-gray-9">
                      {{ review.data.item.applicant_name }}
                    </h2>
                    <p class="mt-1 text-sm text-ink-gray-5">
                      {{ review.data.item.application }} ·
                      {{ review.data.item.facility_type }}
                    </p>
                  </div>
                  <Badge
                    :label="review.data.item.status"
                    :theme="statusTheme(review.data.item.status)"
                    variant="subtle"
                  />
                </div>
                <div class="mt-4 grid gap-4 sm:grid-cols-4">
                  <SummaryStat label="Requested" :value="formatRp(review.data.item.requested_amount)" />
                  <SummaryStat label="Risk Grade" :value="review.data.item.risk_grade || '—'" />
                  <SummaryStat label="Committee" :value="review.data.committee.committee_name" />
                  <SummaryStat label="SLA Due" :value="formatDate(review.data.item.sla_due) || '—'" />
                </div>
              </div>

              <!-- review tabs -->
              <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm">
                <div class="flex border-b border-outline-gray-1 px-5">
                  <button
                    v-for="t in REVIEW_TABS"
                    :key="t"
                    class="border-b-2 px-3 py-2.5 text-sm transition-colors"
                    :class="reviewTab === t
                      ? 'border-ink-gray-8 font-medium text-ink-gray-9'
                      : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
                    @click="reviewTab = t"
                  >
                    {{ t }}
                  </button>
                </div>
                <div class="p-5">
                  <template v-if="reviewTab === 'Memo'">
                    <div v-if="review.data.item.memo" class="prose prose-sm max-w-none text-ink-gray-8" v-html="review.data.item.memo" />
                    <p v-else class="text-sm text-ink-gray-5">{{ __('No credit memo attached.') }}</p>
                  </template>
                  <template v-else-if="reviewTab === 'Application'">
                    <div v-if="review.data.application" class="grid gap-3 sm:grid-cols-2 text-sm">
                      <div><span class="text-ink-gray-5">{{ __('Borrower') }}:</span> {{ review.data.application.borrower_name }}</div>
                      <div><span class="text-ink-gray-5">{{ __('Type') }}:</span> {{ review.data.application.borrower_type }}</div>
                      <div><span class="text-ink-gray-5">{{ __('Industry') }}:</span> {{ review.data.application.industry || '—' }}</div>
                      <div><span class="text-ink-gray-5">{{ __('Risk') }}:</span> {{ review.data.application.risk_grade || '—' }}</div>
                      <div class="sm:col-span-2">
                        <span class="text-ink-gray-5">{{ __('Purpose') }}:</span> {{ review.data.application.purpose || '—' }}
                      </div>
                    </div>
                    <p v-else class="text-sm text-ink-gray-5">{{ __('Application linkage not available.') }}</p>
                  </template>
                  <template v-else-if="reviewTab === 'Documents'">
                    <div v-if="review.data.documents.length" class="space-y-2">
                      <div
                        v-for="d in review.data.documents"
                        :key="d.name"
                        class="flex items-center justify-between rounded border border-outline-gray-1 px-3 py-2 text-sm"
                      >
                        <div>
                          <div class="font-medium text-ink-gray-8">{{ d.document_title }}</div>
                          <div class="text-xs text-ink-gray-5">{{ d.document_type }}</div>
                        </div>
                        <Badge :label="d.status" :theme="docTheme(d.status)" variant="subtle" />
                      </div>
                    </div>
                    <p v-else class="text-sm text-ink-gray-5">{{ __('No documents attached.') }}</p>
                  </template>
                  <template v-else-if="reviewTab === 'AI Insights'">
                    <div class="flex items-start gap-3 rounded-md p-3" style="background: #f0fafa">
                      <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-white" style="background: #008C95">
                        <FeatherIcon name="cpu" class="h-4 w-4" />
                      </div>
                      <div class="text-sm text-ink-gray-8">
                        {{ review.data.item.ai_insights || __('No AI insight generated for this item.') }}
                      </div>
                    </div>
                  </template>
                  <template v-else-if="reviewTab === 'Comments'">
                    <div v-if="review.data.tally.votes.length" class="space-y-3">
                      <div
                        v-for="v in review.data.tally.votes"
                        :key="v.name"
                        class="rounded border border-outline-gray-1 p-3 text-sm"
                      >
                        <div class="flex items-center justify-between">
                          <span class="font-medium text-ink-gray-8">{{ v.member_name || v.member }}</span>
                          <Badge :label="v.decision" :theme="voteTheme(v.decision)" variant="subtle" />
                        </div>
                        <p v-if="v.comment" class="mt-1 text-ink-gray-7">{{ v.comment }}</p>
                        <ul v-if="v.conditions?.length" class="mt-2 list-disc pl-5 text-ink-gray-6">
                          <li v-for="(c, i) in v.conditions" :key="i">{{ c }}</li>
                        </ul>
                        <div class="mt-1 text-xs text-ink-gray-4">{{ formatDate(v.signed_at) }}</div>
                      </div>
                    </div>
                    <p v-else class="text-sm text-ink-gray-5">{{ __('No votes yet.') }}</p>
                  </template>
                </div>
              </div>
            </div>

            <!-- RIGHT: voting panel -->
            <div class="space-y-5">
              <div class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
                <h3 class="text-sm font-semibold uppercase tracking-wide text-ink-gray-5">{{ __('Live Tally') }}</h3>
                <div class="mt-3">
                  <QuorumBar :tally="review.data.tally" :large="true" />
                </div>
                <div class="mt-4 grid grid-cols-3 gap-2 text-center text-sm">
                  <div class="rounded bg-surface-gray-1 px-2 py-2">
                    <div class="text-base font-semibold text-green-700">{{ review.data.tally.approve }}</div>
                    <div class="text-xs text-ink-gray-5">{{ __('Approve') }}</div>
                  </div>
                  <div class="rounded bg-surface-gray-1 px-2 py-2">
                    <div class="text-base font-semibold text-red-700">{{ review.data.tally.reject }}</div>
                    <div class="text-xs text-ink-gray-5">{{ __('Reject') }}</div>
                  </div>
                  <div class="rounded bg-surface-gray-1 px-2 py-2">
                    <div class="text-base font-semibold text-ink-gray-7">{{ review.data.tally.abstain }}</div>
                    <div class="text-xs text-ink-gray-5">{{ __('Abstain') }}</div>
                  </div>
                </div>
                <div class="mt-3 text-xs text-ink-gray-5">
                  {{ __('Majority rule') }}: <span class="font-medium text-ink-gray-7">{{ review.data.committee.majority_rule }}</span>
                </div>
              </div>

              <div v-if="review.data.decision" class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
                <div class="flex items-center gap-2">
                  <FeatherIcon name="check-circle" class="h-5 w-5 text-green-600" />
                  <h3 class="text-base font-semibold text-ink-gray-9">{{ __('Decision Finalized') }}</h3>
                </div>
                <p class="mt-2 text-sm text-ink-gray-7">
                  {{ __('Outcome') }}:
                  <Badge :label="review.data.decision.outcome" :theme="outcomeTheme(review.data.decision.outcome)" variant="subtle" />
                </p>
                <p class="mt-1 text-xs text-ink-gray-5">
                  {{ formatDate(review.data.decision.decided_at) }} · {{ review.data.decision.decided_by }}
                </p>
              </div>

              <div
                v-else-if="review.data.my_vote"
                class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm"
              >
                <p class="text-sm text-ink-gray-7">
                  {{ __('You voted') }}
                  <Badge :label="review.data.my_vote.decision" :theme="voteTheme(review.data.my_vote.decision)" variant="subtle" />
                </p>
                <p v-if="review.data.my_vote.comment" class="mt-2 text-sm text-ink-gray-6">{{ review.data.my_vote.comment }}</p>
              </div>

              <div v-else class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm">
                <h3 class="text-base font-semibold text-ink-gray-9">{{ __('Cast Your Vote') }}</h3>
                <div class="mt-3 grid grid-cols-2 gap-2">
                  <Button
                    v-for="d in DECISIONS"
                    :key="d.value"
                    :variant="voteForm.decision === d.value ? 'solid' : 'outline'"
                    :label="d.label"
                    @click="voteForm.decision = d.value"
                  />
                </div>
                <textarea
                  v-model="voteForm.comment"
                  :placeholder="commentPlaceholder"
                  rows="3"
                  class="mt-3 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm focus:border-ink-gray-7 focus:outline-none"
                />
                <div v-if="voteForm.decision === 'Approve'" class="mt-3">
                  <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                    {{ __('Conditions (one per line)') }}
                  </label>
                  <textarea
                    v-model="voteForm.conditions_text"
                    rows="3"
                    placeholder="CP: Quarterly financial submission&#10;CS: Insurance assignment within 30 days"
                    class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm focus:border-ink-gray-7 focus:outline-none"
                  />
                </div>
                <label class="mt-3 flex items-start gap-2 text-xs text-ink-gray-6">
                  <input v-model="voteForm.signature_ack" type="checkbox" class="mt-0.5 rounded border-outline-gray-3" />
                  <span>{{ __('By submitting I am e-signing this decision (UU ITE compliant acknowledgement).') }}</span>
                </label>
                <Button
                  class="mt-3 w-full"
                  variant="solid"
                  :label="voteSubmitting ? __('Submitting…') : __('Submit Vote')"
                  :disabled="!canSubmitVote"
                  @click="confirmSubmitVote"
                />
              </div>
            </div>
          </div>
        </template>

        <!-- ── DECISIONS ─────────────────────────────────────────────────── -->
        <template v-else-if="activeView === 'decisions'">
          <div class="mb-4">
            <h2 class="text-xl font-semibold text-ink-gray-9">{{ __('Decision Log') }}</h2>
            <p class="mt-1 text-sm text-ink-gray-5">{{ __('Immutable record of every finalized committee decision.') }}</p>
          </div>
          <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm">
            <div v-if="decisions.loading" class="flex h-40 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else-if="!decisions.data?.length" class="flex flex-col items-center justify-center px-6 py-16 text-center">
              <FeatherIcon name="archive" class="mb-3 h-8 w-8 text-ink-gray-3" />
              <p class="text-base font-medium text-ink-gray-8">{{ __('No finalized decisions yet') }}</p>
            </div>
            <table v-else class="w-full text-sm">
              <thead class="border-b border-outline-gray-2 bg-surface-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-4 py-2.5 font-medium">{{ __('Decision') }}</th>
                  <th class="px-4 py-2.5 font-medium">{{ __('Applicant') }}</th>
                  <th class="px-4 py-2.5 font-medium">{{ __('Committee') }}</th>
                  <th class="px-4 py-2.5 font-medium">{{ __('Outcome') }}</th>
                  <th class="px-4 py-2.5 font-medium text-center">{{ __('A / R / Ab') }}</th>
                  <th class="px-4 py-2.5 font-medium text-right">{{ __('Amount') }}</th>
                  <th class="px-4 py-2.5 font-medium">{{ __('Decided') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="d in decisions.data"
                  :key="d.name"
                  class="cursor-pointer border-b border-outline-gray-1 last:border-b-0 hover:bg-surface-gray-1"
                  @click="openDecisionDrawer(d)"
                >
                  <td class="px-4 py-3 font-medium text-ink-gray-8">{{ d.name }}</td>
                  <td class="px-4 py-3 text-ink-gray-7">{{ d.item_detail?.applicant_name }}</td>
                  <td class="px-4 py-3 text-ink-gray-7">{{ d.item_detail?.committee }}</td>
                  <td class="px-4 py-3">
                    <Badge :label="d.outcome" :theme="outcomeTheme(d.outcome)" variant="subtle" />
                  </td>
                  <td class="px-4 py-3 text-center text-ink-gray-7">
                    {{ d.approve_count }} / {{ d.reject_count }} / {{ d.abstain_count }}
                  </td>
                  <td class="px-4 py-3 text-right text-ink-gray-7">{{ formatRp(d.item_detail?.requested_amount) }}</td>
                  <td class="px-4 py-3 text-ink-gray-5">{{ formatDate(d.decided_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <!-- ── CALENDAR ──────────────────────────────────────────────────── -->
        <template v-else-if="activeView === 'calendar'">
          <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <h2 class="text-xl font-semibold text-ink-gray-9">{{ __('Committee Calendar') }}</h2>
              <p class="mt-1 text-sm text-ink-gray-5">{{ __('Upcoming and past committee meetings.') }}</p>
            </div>
            <Button variant="solid" size="sm" label="New Meeting" @click="openNewMeetingDialog">
              <template #prefix><FeatherIcon name="plus" class="h-4 w-4" /></template>
            </Button>
          </div>
          <div v-if="meetings.loading" class="flex h-40 items-center justify-center">
            <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
          </div>
          <div v-else-if="!meetings.data?.length" class="rounded-[14px] border border-outline-gray-2 bg-white p-10 text-center shadow-sm">
            <FeatherIcon name="calendar" class="mx-auto mb-3 h-8 w-8 text-ink-gray-3" />
            <p class="text-base font-medium text-ink-gray-8">{{ __('No meetings scheduled') }}</p>
          </div>
          <div v-else class="grid gap-4 md:grid-cols-2">
            <div
              v-for="m in meetings.data"
              :key="m.name"
              class="rounded-[14px] border border-outline-gray-2 bg-white p-5 shadow-sm"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <h3 class="text-base font-semibold text-ink-gray-9">{{ m.title }}</h3>
                  <p class="mt-0.5 text-sm text-ink-gray-5">{{ m.committee }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <Badge :label="m.status" :theme="meetingTheme(m.status)" variant="subtle" />
                  <button class="text-ink-gray-4 hover:text-red-500" @click="deleteMeeting(m)">
                    <FeatherIcon name="trash-2" class="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div class="mt-3 flex items-center gap-2 text-sm text-ink-gray-7">
                <FeatherIcon name="clock" class="h-4 w-4" />
                {{ formatDateTime(m.scheduled_at) }} · {{ m.duration_minutes }}min
              </div>
              <div v-if="m.location" class="mt-1 flex items-center gap-2 text-sm text-ink-gray-7">
                <FeatherIcon name="map-pin" class="h-4 w-4" />
                {{ m.location }}
              </div>
              <div v-if="m.agenda?.length" class="mt-3">
                <p class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Agenda') }}</p>
                <ul class="mt-1 space-y-1 text-sm text-ink-gray-7">
                  <li v-for="(a, i) in m.agenda" :key="i" class="flex items-center justify-between">
                    <span>{{ a.item }}</span>
                    <span class="text-xs text-ink-gray-4">{{ a.minutes }}min</span>
                  </li>
                </ul>
              </div>
              <div v-if="m.status === 'Scheduled'" class="mt-3 flex gap-2">
                <Button size="sm" variant="solid" label="Attending" @click="rsvp(m, 'yes')" />
                <Button size="sm" variant="outline" label="Maybe" @click="rsvp(m, 'maybe')" />
                <Button size="sm" variant="ghost" label="Decline" @click="rsvp(m, 'no')" />
              </div>
            </div>
          </div>
        </template>

        <!-- ── SETUP ─────────────────────────────────────────────────────── -->
        <template v-else-if="activeView === 'setup'">
          <div class="mb-4">
            <h2 class="text-xl font-semibold text-ink-gray-9">{{ __('Committee Setup') }}</h2>
            <p class="mt-1 text-sm text-ink-gray-5">{{ __('Manage committees, members, and routing rules.') }}</p>
          </div>

          <div class="mb-5 rounded-[14px] border border-outline-gray-2 bg-white shadow-sm">
            <div class="border-b border-outline-gray-1 px-5 py-3">
              <h3 class="text-base font-semibold text-ink-gray-9">{{ __('Committees') }}</h3>
            </div>
            <div v-if="committeesRes.loading" class="flex h-32 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <div v-else>
              <div
                v-for="c in committeesRes.data || []"
                :key="c.name"
                class="border-b border-outline-gray-1 px-5 py-4 last:border-b-0"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <div class="flex items-center gap-2">
                      <h4 class="text-base font-medium text-ink-gray-9">{{ c.committee_name }}</h4>
                      <Badge v-if="c.active" label="Active" theme="green" variant="subtle" />
                      <Badge v-else label="Inactive" theme="gray" variant="subtle" />
                    </div>
                    <p class="mt-1 text-sm text-ink-gray-5">
                      {{ __('Quorum') }}: {{ c.quorum_pct }}% ·
                      {{ __('Majority') }}: {{ c.majority_rule }}
                      <span v-if="c.chairman_tie_break"> · {{ __('Chairman tie-break') }}</span>
                    </p>
                  </div>
                  <div class="flex items-center gap-1">
                    <Button size="sm" variant="outline" label="Edit" @click="openEditCommittee(c)" />
                    <Button size="sm" variant="ghost" @click="deleteCommittee(c)">
                      <FeatherIcon name="trash-2" class="h-4 w-4 text-ink-gray-4 hover:text-red-500" />
                    </Button>
                  </div>
                </div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <div
                    v-for="m in c.members"
                    :key="m.member"
                    class="flex items-center gap-1.5 rounded-md border border-outline-gray-2 bg-surface-gray-1 px-2 py-1 text-xs"
                  >
                    <FeatherIcon
                      :name="m.role === 'Chairman' ? 'star' : m.role === 'Observer' ? 'eye' : 'user'"
                      class="h-3 w-3 text-ink-gray-5"
                    />
                    <span class="text-ink-gray-7">{{ m.member_name || m.member }}</span>
                    <span class="text-ink-gray-4">· {{ m.role }} ({{ m.weight }})</span>
                  </div>
                </div>
              </div>
              <div v-if="!committeesRes.data?.length" class="px-5 py-10 text-center text-sm text-ink-gray-5">
                {{ __('No committees configured.') }}
              </div>
            </div>
          </div>

          <div class="rounded-[14px] border border-outline-gray-2 bg-white shadow-sm">
            <div class="flex items-center justify-between border-b border-outline-gray-1 px-5 py-3">
              <h3 class="text-base font-semibold text-ink-gray-9">{{ __('Auto-Routing Rules') }}</h3>
              <Button size="sm" variant="outline" label="New Rule" @click="openNewRoutingRule">
                <template #prefix><FeatherIcon name="plus" class="h-3.5 w-3.5" /></template>
              </Button>
            </div>
            <div v-if="rulesRes.loading" class="flex h-24 items-center justify-center">
              <LoadingIndicator class="h-5 w-5 text-ink-gray-4" />
            </div>
            <table v-else-if="rulesRes.data?.length" class="w-full text-sm">
              <thead class="border-b border-outline-gray-1 text-left text-xs uppercase tracking-wide text-ink-gray-5">
                <tr>
                  <th class="px-5 py-2 font-medium">{{ __('Rule') }}</th>
                  <th class="px-5 py-2 font-medium">{{ __('Amount Range') }}</th>
                  <th class="px-5 py-2 font-medium">{{ __('Product Type') }}</th>
                  <th class="px-5 py-2 font-medium">{{ __('Risk Grade') }}</th>
                  <th class="px-5 py-2 font-medium">{{ __('Routes To') }}</th>
                  <th class="px-5 py-2 font-medium text-center">{{ __('Priority') }}</th>
                  <th class="px-5 py-2 font-medium">{{ __('Active') }}</th>
                  <th class="px-5 py-2 font-medium text-right">{{ __('Actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in rulesRes.data" :key="r.name" class="border-b border-outline-gray-1 last:border-b-0">
                  <td class="px-5 py-2.5 text-ink-gray-8">{{ r.rule_name }}</td>
                  <td class="px-5 py-2.5 text-ink-gray-7">
                    {{ formatRp(r.min_amount) }} – {{ r.max_amount ? formatRp(r.max_amount) : '∞' }}
                  </td>
                  <td class="px-5 py-2.5 text-ink-gray-7">{{ r.product_type || '—' }}</td>
                  <td class="px-5 py-2.5 text-ink-gray-7">{{ r.risk_grade || '—' }}</td>
                  <td class="px-5 py-2.5 text-ink-gray-7">{{ r.committee }}</td>
                  <td class="px-5 py-2.5 text-center text-ink-gray-7">{{ r.priority }}</td>
                  <td class="px-5 py-2.5">
                    <Badge :label="r.active ? 'Yes' : 'No'" :theme="r.active ? 'green' : 'gray'" variant="subtle" />
                  </td>
                  <td class="px-5 py-2.5 text-right">
                    <Button size="sm" variant="ghost" @click="deleteRoutingRule(r)">
                      <FeatherIcon name="trash-2" class="h-4 w-4 text-ink-gray-4 hover:text-red-500" />
                    </Button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="px-5 py-10 text-center text-sm text-ink-gray-5">{{ __('No routing rules.') }}</div>
          </div>
        </template>
      </div>
    </div>

    <!-- ── Confirm vote dialog ────────────────────────────────────────── -->
    <Dialog v-model="confirmDialog" :options="{ title: __('Confirm your vote') }">
      <template #body-content>
        <p class="text-sm text-ink-gray-7">
          {{ __('You are submitting a') }}
          <span class="font-medium text-ink-gray-9">{{ voteForm.decision }}</span>
          {{ __('vote. This action is final and will be recorded with your e-signature.') }}
        </p>
        <p class="mt-2 text-xs text-ink-gray-5">
          {{ __('Comment') }}: {{ voteForm.comment || __('(none)') }}
        </p>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button
            variant="solid"
            :label="voteSubmitting ? __('Submitting…') : __('Confirm & Sign')"
            :disabled="voteSubmitting"
            @click="submitVote().then(close)"
          />
        </div>
      </template>
    </Dialog>

    <!-- ── Decision drawer ────────────────────────────────────────────── -->
    <Dialog v-model="decisionDrawer.open" :options="{ title: decisionDrawer.data?.name || 'Decision' }">
      <template #body-content>
        <div v-if="decisionDrawer.data" class="space-y-3 text-sm">
          <div class="flex items-center gap-2">
            <Badge :label="decisionDrawer.data.outcome" :theme="outcomeTheme(decisionDrawer.data.outcome)" variant="subtle" />
            <span class="text-ink-gray-5">·</span>
            <span class="text-ink-gray-7">{{ formatDate(decisionDrawer.data.decided_at) }}</span>
          </div>
          <div class="rounded border border-outline-gray-1 p-3">
            <div class="text-xs uppercase text-ink-gray-5">{{ __('Tally') }}</div>
            <div class="mt-1 text-ink-gray-8">
              {{ __('Approve') }}: {{ decisionDrawer.data.approve_count }} ·
              {{ __('Reject') }}: {{ decisionDrawer.data.reject_count }} ·
              {{ __('Abstain') }}: {{ decisionDrawer.data.abstain_count }}
            </div>
          </div>
          <div v-if="decisionDrawer.data.item_detail" class="rounded border border-outline-gray-1 p-3">
            <div class="text-xs uppercase text-ink-gray-5">{{ __('Item') }}</div>
            <div class="mt-1 text-ink-gray-8">
              {{ decisionDrawer.data.item_detail.applicant_name }} ·
              {{ decisionDrawer.data.item_detail.facility_type }} ·
              {{ formatRp(decisionDrawer.data.item_detail.requested_amount) }}
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- ── Committee edit dialog ──────────────────────────────────────── -->
    <Dialog v-model="committeeDialog.open" :options="{ title: committeeDialog.data?.committee_name ? __('Edit Committee') : __('New Committee') }">
      <template #body-content>
        <div class="space-y-3 text-sm">
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Committee Name') }}</label>
            <input
              v-model="committeeDialog.data.committee_name"
              :disabled="!!committeeDialog.editing"
              class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
            />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Quorum %') }}</label>
              <input
                v-model.number="committeeDialog.data.quorum_pct"
                type="number"
                min="1"
                max="100"
                class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
              />
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Majority Rule') }}</label>
              <select
                v-model="committeeDialog.data.majority_rule"
                class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
              >
                <option>Simple</option>
                <option>Qualified</option>
                <option>Unanimous</option>
                <option>Weighted</option>
              </select>
            </div>
          </div>
          <label class="flex items-center gap-2 text-sm">
            <input v-model="committeeDialog.data.chairman_tie_break" type="checkbox" class="rounded border-outline-gray-3" />
            {{ __('Chairman tie-break') }}
          </label>
          <label class="flex items-center gap-2 text-sm">
            <input v-model="committeeDialog.data.active" type="checkbox" class="rounded border-outline-gray-3" />
            {{ __('Active') }}
          </label>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Description') }}</label>
            <textarea v-model="committeeDialog.data.description" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm focus:border-ink-gray-7 focus:outline-none" />
          </div>
          <div class="mt-2">
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Members') }}</label>
            <div v-if="committeeDialog.data.members?.length" class="mt-1 space-y-1">
              <div
                v-for="(m, i) in committeeDialog.data.members"
                :key="i"
                class="flex items-center gap-2 rounded border border-outline-gray-1 px-2 py-1 text-xs"
              >
                <span class="flex-1 text-ink-gray-8">{{ m.member_name || m.member }}</span>
                <span class="text-ink-gray-5">{{ m.role }} ({{ m.weight }})</span>
                <button class="text-ink-gray-4 hover:text-red-500" @click="committeeDialog.data.members.splice(i, 1)">
                  <FeatherIcon name="trash-2" class="h-3 w-3" />
                </button>
              </div>
            </div>
            <div v-else class="mt-1 text-xs text-ink-gray-4">{{ __('No members') }}</div>
            <div class="mt-2 flex gap-2">
              <input
                v-model="newMember.member"
                placeholder="user@example.com"
                class="flex-1 rounded-md border border-outline-gray-2 px-2 py-1 text-xs"
              />
              <select v-model="newMember.role" class="rounded-md border border-outline-gray-2 px-1 py-1 text-xs">
                <option>Member</option>
                <option>Chairman</option>
                <option>Observer</option>
              </select>
              <input
                v-model.number="newMember.weight"
                type="number"
                min="1"
                class="w-14 rounded-md border border-outline-gray-2 px-1 py-1 text-xs"
              />
              <Button size="sm" variant="outline" label="Add" @click="addMember" />
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Save')" @click="saveCommittee().then(close)" />
        </div>
      </template>
    </Dialog>

    <!-- ── Routing rule dialog ────────────────────────────────────────── -->
    <Dialog v-model="ruleDialog.open" :options="{ title: __('New Routing Rule') }">
      <template #body-content>
        <div class="space-y-3 text-sm">
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Rule Name') }}</label>
            <input
              v-model="ruleDialog.data.rule_name"
              class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
            />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Min Amount') }}</label>
              <input
                v-model.number="ruleDialog.data.min_amount"
                type="number"
                class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
              />
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Max Amount (0 = no limit)') }}</label>
              <input
                v-model.number="ruleDialog.data.max_amount"
                type="number"
                class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
              />
            </div>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Route To Committee') }}</label>
            <select
              v-model="ruleDialog.data.committee"
              class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
            >
              <option v-for="c in committeesRes.data || []" :key="c.name" :value="c.name">{{ c.committee_name }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Product Type (optional)') }}</label>
            <input
              v-model="ruleDialog.data.product_type"
              class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
              placeholder="e.g. Working Capital, Invoice Financing"
            />
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Risk Grade (optional)') }}</label>
            <input
              v-model="ruleDialog.data.risk_grade"
              class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none"
            />
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Save')" @click="saveRoutingRule().then(close)" />
        </div>
      </template>
    </Dialog>

    <!-- ── New Committee Item dialog ─────────────────────────────────── -->
    <Dialog v-model="itemDialog.open" :options="{ title: __('New Committee Item') }">
      <template #body-content>
        <div class="space-y-3 text-sm">
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Committee') }}</label>
            <select v-model="itemDialog.data.committee" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none">
              <option v-for="c in committeesRes.data || []" :key="c.name" :value="c.name">{{ c.committee_name }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Applicant Name') }}</label>
            <input v-model="itemDialog.data.applicant_name" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Facility Type') }}</label>
              <input v-model="itemDialog.data.facility_type" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" placeholder="e.g. Working Capital" />
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Amount (IDR)') }}</label>
              <input v-model.number="itemDialog.data.requested_amount" type="number" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Risk Grade') }}</label>
            <input v-model="itemDialog.data.risk_grade" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" placeholder="e.g. A, B, C" />
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Description') }}</label>
            <textarea v-model="itemDialog.data.description" rows="2" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" />
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Create')" @click="saveItem().then(close)" />
        </div>
      </template>
    </Dialog>

    <!-- ── New Meeting dialog ──────────────────────────────────────────── -->
    <Dialog v-model="meetingDialog.open" :options="{ title: __('New Meeting') }">
      <template #body-content>
        <div class="space-y-3 text-sm">
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Committee') }}</label>
            <select v-model="meetingDialog.data.committee" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none">
              <option v-for="c in committeesRes.data || []" :key="c.name" :value="c.name">{{ c.committee_name }}</option>
            </select>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Title') }}</label>
            <input v-model="meetingDialog.data.title" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Scheduled At') }}</label>
              <input v-model="meetingDialog.data.scheduled_at" type="datetime-local" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" />
            </div>
            <div>
              <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Duration (min)') }}</label>
              <input v-model.number="meetingDialog.data.duration_minutes" type="number" min="15" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="text-xs font-medium uppercase tracking-wide text-ink-gray-5">{{ __('Location') }}</label>
            <input v-model="meetingDialog.data.location" class="mt-1 w-full rounded-md border border-outline-gray-2 px-3 py-2 focus:border-ink-gray-7 focus:outline-none" placeholder="e.g. Conference Room A" />
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button variant="solid" :label="__('Create')" @click="saveMeeting().then(close)" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, defineComponent, h, onMounted } from 'vue'
import { Badge, Button, Dialog, FeatherIcon, LoadingIndicator, createResource, toast } from 'frappe-ui'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'

const viewControls = ref(null)

const QuorumBar = defineComponent({
  name: 'QuorumBar',
  props: ['tally', 'large'],
  setup(props) {
    return () => {
      const t = props.tally || {}
      const pct = t.total ? Math.min(100, Math.round((t.voted / t.total) * 100)) : 0
      return h('div', { class: 'w-full' }, [
        h('div', { class: 'flex items-center justify-between text-xs text-ink-gray-6' }, [
          h('span', `${t.voted || 0}/${t.total || 0} voted`),
          h(
            'span',
            { class: t.quorum_met ? 'font-medium text-green-700' : '' },
            t.quorum_met ? 'Quorum reached' : `Need ${t.need_to_quorum || 0} more`,
          ),
        ]),
        h(
          'div',
          { class: `mt-1 w-full rounded-full bg-surface-gray-2 ${props.large ? 'h-2' : 'h-1.5'}` },
          [h('div', { class: 'h-full rounded-full transition-all', style: `width: ${pct}%; background: #008C95` })],
        ),
      ])
    }
  },
})

const SummaryStat = defineComponent({
  name: 'SummaryStat',
  props: ['label', 'value'],
  setup(props) {
    return () =>
      h('div', { class: 'rounded-md bg-surface-gray-1 px-3 py-2' }, [
        h('div', { class: 'text-xs uppercase tracking-wide text-ink-gray-5' }, props.label),
        h('div', { class: 'mt-0.5 text-sm font-medium text-ink-gray-9' }, props.value),
      ])
  },
})

const TABS = [
  { label: 'Queue', view: 'queue' },
  { label: 'Decisions', view: 'decisions' },
  { label: 'Calendar', view: 'calendar' },
  { label: 'Setup', view: 'setup' },
]

const REVIEW_TABS = ['Memo', 'Application', 'Documents', 'AI Insights', 'Comments']

const DECISIONS = [
  { value: 'Approve', label: 'Approve' },
  { value: 'Reject', label: 'Reject' },
  { value: 'Abstain', label: 'Abstain' },
  { value: 'Refer Back', label: 'Refer Back' },
]

const activeView = ref('queue')
const reviewTab = ref('Memo')
const reviewItemName = ref(null)

const queueFilters = reactive({ committee: '', sort_by: 'sla', my_pending_only: false })

const voteForm = reactive({ decision: '', comment: '', conditions_text: '', signature_ack: false })
const voteSubmitting = ref(false)
const confirmDialog = ref(false)

const decisionDrawer = reactive({ open: false, data: null })
const committeeDialog = reactive({ open: false, editing: false, data: {} })
const ruleDialog = reactive({ open: false, data: {} })
const itemDialog = reactive({ open: false, data: {} })
const meetingDialog = reactive({ open: false, data: {} })
const newMember = reactive({ member: '', role: 'Member', weight: 1 })

// ── Resources ───────────────────────────────────────────────────────

const ctx = createResource({
  url: 'crm.api.committee.get_context',
  auto: true,
})

const queue = createResource({
  url: 'crm.api.committee.get_queue',
  params: () => ({
    committee: queueFilters.committee || null,
    my_pending_only: queueFilters.my_pending_only ? 1 : 0,
    sort_by: queueFilters.sort_by,
  }),
  auto: true,
})

const review = createResource({
  url: 'crm.api.committee.get_review',
  makeParams: () => ({ item: reviewItemName.value }),
})

const decisions = createResource({
  url: 'crm.api.committee.get_decisions',
  auto: true,
})

const meetings = createResource({
  url: 'crm.api.committee.list_meetings',
  auto: true,
})

const committeesRes = createResource({
  url: 'crm.api.committee.list_committees',
  auto: true,
})

const rulesRes = createResource({
  url: 'crm.api.committee.list_routing_rules',
  auto: true,
})

// ── Computed ────────────────────────────────────────────────────────

const queueRows = computed(() => queue.data || [])

const commentPlaceholder = computed(() =>
  voteForm.decision === 'Reject' || voteForm.decision === 'Refer Back'
    ? __('Comment is required when rejecting or referring back…')
    : __('Optional comment'),
)

const canSubmitVote = computed(() => {
  if (!voteForm.decision || !voteForm.signature_ack) return false
  if ((voteForm.decision === 'Reject' || voteForm.decision === 'Refer Back') && !voteForm.comment.trim()) return false
  return !voteSubmitting.value
})

// ── Helpers ─────────────────────────────────────────────────────────

function formatRp(n) {
  if (n == null || n === '') return '—'
  return 'Rp ' + Number(n).toLocaleString('id-ID')
}

function formatDate(s) {
  if (!s) return ''
  return new Date(s).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatDateTime(s) {
  if (!s) return ''
  return new Date(s).toLocaleString('id-ID', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function slaLabel(row) {
  if (!row.sla_due) return __('No SLA')
  if (row.sla_state === 'breached') return __('Breached')
  if (row.sla_state === 'amber') return __('Due soon')
  return formatDate(row.sla_due)
}

function slaTheme(state) {
  return state === 'breached' ? 'red' : state === 'amber' ? 'orange' : 'green'
}

function statusTheme(s) {
  return s === 'Decided' ? 'green' : s === 'Referred Back' ? 'orange' : s === 'Quorum Reached' ? 'blue' : 'gray'
}

function outcomeTheme(o) {
  return o === 'Approved' ? 'green' : o === 'Rejected' ? 'red' : 'orange'
}

function voteTheme(d) {
  return d === 'Approve' ? 'green' : d === 'Reject' ? 'red' : d === 'Refer Back' ? 'orange' : 'gray'
}

function docTheme(s) {
  if (s === 'Approved') return 'green'
  if (s === 'Rejected' || s === 'Expired') return 'red'
  return 'gray'
}

function meetingTheme(s) {
  return s === 'Completed' ? 'gray' : s === 'In Progress' ? 'blue' : s === 'Cancelled' ? 'red' : 'green'
}

// ── Navigation ──────────────────────────────────────────────────────

function navigate(view) {
  activeView.value = view
}

function openReview(itemName) {
  reviewItemName.value = itemName
  reviewTab.value = 'Memo'
  voteForm.decision = ''
  voteForm.comment = ''
  voteForm.conditions_text = ''
  voteForm.signature_ack = false
  review.fetch()
  activeView.value = 'review'
}

// ── Vote submission ─────────────────────────────────────────────────

function confirmSubmitVote() {
  confirmDialog.value = true
}

async function submitVote() {
  voteSubmitting.value = true
  try {
    const conditions = voteForm.conditions_text
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean)
    await createResource({
      url: 'crm.api.committee.submit_vote',
      makeParams: () => ({
        item: reviewItemName.value,
        decision: voteForm.decision,
        comment: voteForm.comment,
        conditions: JSON.stringify(conditions),
        signature_ack: 1,
      }),
    }).submit()
    toast.success(__('Vote recorded'))
    review.fetch()
    queue.reload()
    decisions.reload()
  } catch (e) {
    toast.error(e?.exc?.split('\n').slice(-2)[0] || e?.message || __('Failed to submit'))
  } finally {
    voteSubmitting.value = false
  }
}

// ── Decisions ───────────────────────────────────────────────────────

function openDecisionDrawer(d) {
  decisionDrawer.data = d
  decisionDrawer.open = true
}

async function exportDecisions() {
  try {
    const r = createResource({ url: 'crm.api.committee.export_decisions_csv' })
    const csv = await r.submit()
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `committee-decisions-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    toast.error(__('Export failed'))
  }
}

// ── Calendar RSVP ───────────────────────────────────────────────────

async function rsvp(meeting, response) {
  try {
    await createResource({
      url: 'crm.api.committee.rsvp_meeting',
      makeParams: () => ({ meeting: meeting.name, response }),
    }).submit()
    toast.success(__('RSVP saved'))
    meetings.reload()
  } catch (e) {
    toast.error(__('Failed to RSVP'))
  }
}

// ── Setup ───────────────────────────────────────────────────────────

function openNewCommittee() {
  committeeDialog.editing = false
  committeeDialog.data = {
    committee_name: '',
    quorum_pct: 60,
    majority_rule: 'Simple',
    chairman_tie_break: false,
    active: true,
    description: '',
    members: [],
  }
  newMember.member = ''
  newMember.role = 'Member'
  newMember.weight = 1
  committeeDialog.open = true
}

function openEditCommittee(c) {
  committeeDialog.editing = true
  committeeDialog.data = {
    committee_name: c.committee_name,
    quorum_pct: c.quorum_pct,
    majority_rule: c.majority_rule,
    chairman_tie_break: !!c.chairman_tie_break,
    active: !!c.active,
    description: c.description || '',
    members: (c.members || []).map((m) => ({ ...m })),
  }
  newMember.member = ''
  newMember.role = 'Member'
  newMember.weight = 1
  committeeDialog.open = true
}

async function saveCommittee() {
  try {
    await createResource({
      url: 'crm.api.committee.upsert_committee',
      makeParams: () => ({
        committee_name: committeeDialog.data.committee_name,
        quorum_pct: committeeDialog.data.quorum_pct,
        majority_rule: committeeDialog.data.majority_rule,
        chairman_tie_break: committeeDialog.data.chairman_tie_break ? 1 : 0,
        active: committeeDialog.data.active ? 1 : 0,
        description: committeeDialog.data.description,
        members: JSON.stringify(committeeDialog.data.members || []),
      }),
    }).submit()
    toast.success(__('Committee saved'))
    committeesRes.reload()
    ctx.reload()
  } catch (e) {
    toast.error(__('Save failed: ') + (e?.message || ''))
  }
}

function openNewItemDialog() {
  itemDialog.data = {
    committee: committeesRes.data?.[0]?.name || '',
    applicant_name: '',
    facility_type: '',
    requested_amount: 0,
    risk_grade: '',
    description: '',
  }
  itemDialog.open = true
}

async function saveItem() {
  try {
    await createResource({
      url: 'crm.api.committee.create_committee_item',
      makeParams: () => ({
        committee: itemDialog.data.committee,
        applicant_name: itemDialog.data.applicant_name,
        facility_type: itemDialog.data.facility_type,
        requested_amount: itemDialog.data.requested_amount,
        risk_grade: itemDialog.data.risk_grade,
        description: itemDialog.data.description,
      }),
    }).submit()
    toast.success(__('Committee item created'))
    queue.reload()
  } catch (e) {
    toast.error(__('Create failed'))
  }
}

function openNewMeetingDialog() {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  meetingDialog.data = {
    committee: committeesRes.data?.[0]?.name || '',
    title: '',
    scheduled_at: now.toISOString().slice(0, 16),
    duration_minutes: 60,
    location: '',
  }
  meetingDialog.open = true
}

async function saveMeeting() {
  try {
    await createResource({
      url: 'crm.api.committee.create_meeting',
      makeParams: () => ({
        title: meetingDialog.data.title,
        committee: meetingDialog.data.committee,
        scheduled_at: meetingDialog.data.scheduled_at,
        duration_minutes: meetingDialog.data.duration_minutes,
        location: meetingDialog.data.location,
      }),
    }).submit()
    toast.success(__('Meeting scheduled'))
    meetings.reload()
  } catch (e) {
    toast.error(__('Schedule failed: ') + (e?.message || ''))
  }
}

function openNewRoutingRule() {
  ruleDialog.data = {
    rule_name: '',
    min_amount: 0,
    max_amount: 0,
    committee: committeesRes.data?.[0]?.name || '',
    product_type: '',
    risk_grade: '',
  }
  ruleDialog.open = true
}

async function saveRoutingRule() {
  try {
    await createResource({
      url: 'crm.api.committee.upsert_routing_rule',
      makeParams: () => ({
        rule_name: ruleDialog.data.rule_name,
        committee: ruleDialog.data.committee,
        min_amount: ruleDialog.data.min_amount,
        max_amount: ruleDialog.data.max_amount,
        product_type: ruleDialog.data.product_type || undefined,
        risk_grade: ruleDialog.data.risk_grade,
        priority: 10,
        active: 1,
      }),
    }).submit()
    toast.success(__('Rule saved'))
    rulesRes.reload()
  } catch (e) {
    toast.error(__('Save failed'))
  }
}

function addMember() {
  if (!newMember.member.trim()) return
  committeeDialog.data.members = committeeDialog.data.members || []
  committeeDialog.data.members.push({
    member: newMember.member.trim(),
    member_name: newMember.member.trim(),
    role: newMember.role,
    weight: newMember.weight || 1,
  })
  newMember.member = ''
  newMember.role = 'Member'
  newMember.weight = 1
}

async function deleteCommittee(c) {
  if (!confirm(__('Delete committee "%1"?', [c.committee_name]))) return
  try {
    await createResource({
      url: 'crm.api.committee.delete_committee',
      makeParams: () => ({ name: c.name }),
    }).submit()
    toast.success(__('Committee deactivated'))
    committeesRes.reload()
    ctx.reload()
  } catch (e) {
    toast.error(__('Failed'))
  }
}

async function deleteRoutingRule(r) {
  if (!confirm(__('Delete rule "%1"?', [r.rule_name]))) return
  try {
    await createResource({
      url: 'crm.api.committee.delete_routing_rule',
      makeParams: () => ({ name: r.name }),
    }).submit()
    toast.success(__('Rule deleted'))
    rulesRes.reload()
  } catch (e) {
    toast.error(__('Failed'))
  }
}

async function deleteMeeting(m) {
  if (!confirm(__('Delete meeting "%1"?', [m.title]))) return
  try {
    await createResource({
      url: 'crm.api.committee.delete_meeting',
      makeParams: () => ({ name: m.name }),
    }).submit()
    toast.success(__('Meeting deleted'))
    meetings.reload()
  } catch (e) {
    toast.error(__('Failed'))
  }
}

async function maybeSeedCommittee() {
  try {
    const r = await createResource({
      url: 'crm.api.committee.seed_committee_sample_data',
    }).submit()
    if (r.created) {
      toast.success(__('Sample committees created'))
      committeesRes.reload()
      meetings.reload()
      rulesRes.reload()
      ctx.reload()
    }
  } catch (e) {
    // silently ignore if module not ready
  }
}

onMounted(() => {
  maybeSeedCommittee()
})
</script>
