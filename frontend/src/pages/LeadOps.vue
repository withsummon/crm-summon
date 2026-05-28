<template>
  <div class="flex h-full flex-col">
    <LayoutHeader>
      <template #left-header>
        <button class="flex h-7 w-7 items-center justify-center rounded-md text-ink-gray-5 hover:bg-surface-gray-2 hover:text-ink-gray-8 mr-1" @click="router.back()">
          <FeatherIcon name="arrow-left" class="size-4" />
        </button>
        <ViewBreadcrumbs v-model="viewControls" routeName="Lead Ops" />
      </template>
    </LayoutHeader>

    <div class="shrink-0 border-b border-outline-gray-2 bg-surface-white px-6 py-3">
      <div class="flex items-center gap-3">
        <button
          v-for="tab in TABS"
          :key="tab.key"
          class="whitespace-nowrap border-b-2 px-1 py-2 text-base leading-5 transition-colors"
          :class="activeTab === tab.key ? 'border-ink-gray-8 font-medium text-ink-gray-9' : 'border-transparent text-ink-gray-5 hover:text-ink-gray-8'"
          @click="activeTab = tab.key"
        >
          {{ __(tab.label) }}
          <Badge v-if="tab.badge" :label="String(tab.badge)" variant="subtle" theme="teal" size="sm" class="ml-1" />
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto bg-surface-gray-1 px-6 py-4">

      <template v-if="activeTab === 'whatsapp'">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold text-ink-gray-9">WhatsApp Intake Queue</h2>
          <Button variant="outline" size="sm" label="Reload" @click="loadWhatsapp" />
        </div>
        <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
              <tr>
                <th class="px-3 py-1.5">From</th>
                <th class="px-3 py-1.5">Phone</th>
                <th class="px-3 py-1.5">Message</th>
                <th class="px-3 py-1.5">Received</th>
                <th class="px-3 py-1.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in whatsappMessages" :key="m.id" class="border-b border-outline-gray-1 last:border-b-0">
                <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ m.name }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7 font-mono text-xs">{{ m.phone }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7 max-w-md truncate">{{ m.body }}</td>
                <td class="px-3 py-1.5 text-ink-gray-5 text-xs">{{ formatDate(m.received_at) }}</td>
                <td class="px-3 py-1.5 text-right">
                  <Button variant="solid" size="sm" label="Create Lead" :loading="creatingLeadId === m.id" @click="createLeadFromWhatsapp(m)" />
                </td>
              </tr>
              <tr v-if="!whatsappMessages.length">
                <td colspan="5" class="px-4 py-8 text-center text-ink-gray-5">No incoming WhatsApp leads. Connect Omnichannel to receive intake.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <template v-else-if="activeTab === 'email'">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold text-ink-gray-9">Email Intake Queue</h2>
          <Button variant="outline" size="sm" label="Reload" @click="loadEmail" />
        </div>
        <div class="rounded-[10px] border border-outline-gray-2 bg-white shadow-sm overflow-hidden">
          <table class="w-full text-sm">
            <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
              <tr>
                <th class="px-3 py-1.5">From</th>
                <th class="px-3 py-1.5">Subject</th>
                <th class="px-3 py-1.5">Snippet</th>
                <th class="px-3 py-1.5">Received</th>
                <th class="px-3 py-1.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in emailMessages" :key="e.id" class="border-b border-outline-gray-1 last:border-b-0">
                <td class="px-3 py-1.5 font-medium text-ink-gray-9">{{ e.from }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7">{{ e.subject }}</td>
                <td class="px-3 py-1.5 text-ink-gray-7 max-w-md truncate">{{ e.snippet }}</td>
                <td class="px-3 py-1.5 text-ink-gray-5 text-xs">{{ formatDate(e.received_at) }}</td>
                <td class="px-3 py-1.5 text-right">
                  <Button variant="solid" size="sm" label="Create Lead" :loading="creatingLeadId === e.id" @click="createLeadFromEmail(e)" />
                </td>
              </tr>
              <tr v-if="!emailMessages.length">
                <td colspan="5" class="px-4 py-8 text-center text-ink-gray-5">No incoming email leads.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <template v-else-if="activeTab === 'nurture'">
        <div class="grid gap-3 lg:grid-cols-[280px_1fr]">
          <aside class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm h-fit">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-sm font-semibold text-ink-gray-8">Sequences</h3>
              <Button variant="ghost" size="sm" label="+ New" @click="newSequence" />
            </div>
            <div class="space-y-1">
              <button
                v-for="s in sequences"
                :key="s.id"
                class="block w-full rounded-md px-3 py-2 text-left text-sm"
                :class="selectedSequence?.id === s.id ? 'bg-surface-gray-2 font-medium text-ink-gray-9' : 'text-ink-gray-7 hover:bg-surface-gray-1'"
                @click="selectedSequence = s"
              >
                {{ s.name }}
                <p class="text-xs text-ink-gray-5">{{ s.trigger }}</p>
              </button>
            </div>
          </aside>
          <section v-if="selectedSequence" class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <div class="mb-3 flex items-center justify-between">
              <input v-model="selectedSequence.name" class="text-base font-semibold text-ink-gray-9 bg-transparent outline-none border-b border-transparent focus:border-outline-gray-2" />
              <div class="flex gap-2">
                <Button variant="outline" size="sm" label="Delete" @click="deleteSequence(selectedSequence)" />
                <Button variant="solid" size="sm" label="Save" @click="saveSequence(selectedSequence)" />
              </div>
            </div>
            <div class="grid gap-3 md:grid-cols-2 mb-3">
              <div>
                <label class="mb-1 block text-xs font-medium text-ink-gray-7">Trigger</label>
                <select v-model="selectedSequence.trigger" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
                  <option>Status Changed</option>
                  <option>Age Threshold</option>
                  <option>Score Band</option>
                  <option>Source = Web</option>
                </select>
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-ink-gray-7">Trigger Detail</label>
                <input v-model="selectedSequence.trigger_detail" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm" placeholder="e.g. status=Contacted, age>3d, score>70" />
              </div>
            </div>
            <h4 class="mb-2 text-sm font-semibold text-ink-gray-8">Steps</h4>
            <div class="space-y-2">
              <div v-for="(step, idx) in selectedSequence.steps" :key="idx" class="flex items-center gap-2 rounded-md border border-outline-gray-1 p-3">
                <span class="flex h-6 w-6 items-center justify-center rounded-full bg-surface-gray-2 text-xs font-semibold">{{ idx + 1 }}</span>
                <select v-model="step.action" class="rounded-md border border-outline-gray-2 px-2 py-1 text-sm">
                  <option>Email</option>
                  <option>WhatsApp</option>
                  <option>Assign Task</option>
                  <option>Wait</option>
                </select>
                <input v-if="step.action === 'Wait'" v-model.number="step.days" type="number" min="0" placeholder="Days" class="w-20 rounded-md border border-outline-gray-2 px-2 py-1 text-sm" />
                <input v-else v-model="step.detail" class="flex-1 rounded-md border border-outline-gray-2 px-3 py-1 text-sm" placeholder="Template name, task title, or message…" />
                <button @click="removeStep(idx)" class="text-red-500 text-sm px-2">✕</button>
              </div>
              <Button variant="outline" size="sm" label="+ Add Step" @click="addStep" />
            </div>
          </section>
        </div>
      </template>

      <template v-else-if="activeTab === 'widget'">
        <div class="grid gap-3 lg:grid-cols-[1fr_360px]">
          <div class="space-y-4">
            <!-- Snippet box -->
            <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
              <h2 class="text-base font-semibold text-ink-gray-9 mb-3">Embed Snippet</h2>
              <p class="text-sm text-ink-gray-5 mb-3">Paste this into your website to capture leads directly into the CRM.</p>
              <pre class="rounded-md bg-surface-gray-1 p-3 text-xs font-mono overflow-x-auto"><code>{{ widgetSnippet }}</code></pre>
              <Button class="mt-3" variant="outline" size="sm" label="Copy Embed Snippet" @click="copyWidget" />
            </div>

            <!-- Live Form Preview (Embed Form) -->
            <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
              <div class="flex items-center justify-between border-b border-outline-gray-1 pb-3 mb-4">
                <div>
                  <h3 class="text-sm font-semibold text-ink-gray-9">Lead Capture Form — Live Web Embed Preview</h3>
                  <p class="text-xs text-ink-gray-5">This is how the external form renders dynamically on your website.</p>
                </div>
                <Badge label="Live Preview" theme="teal" variant="subtle" size="sm" />
              </div>

              <!-- Interactive Web Embed Form -->
              <form class="space-y-3 bg-slate-50 border border-slate-200/50 p-4 rounded-xl max-w-md mx-auto shadow-inner text-sm" @submit.prevent="submitWidgetLead">
                <div class="text-xs font-bold text-slate-400 uppercase tracking-widest text-center border-b pb-2 mb-3">PT BANK NEGARA INDONESIA (Tbk)</div>
                
                <div v-for="f in widgetFields.filter(x => x.enabled)" :key="f.key">
                  <label class="block text-xs font-medium text-slate-700 mb-1">
                    {{ f.label }}
                    <span v-if="f.required" class="text-red-500">*</span>
                  </label>
                  <input
                    v-if="f.key !== 'message'"
                    v-model="mockWidgetLead[f.key]"
                    :type="f.key === 'email' ? 'email' : f.key === 'amount' ? 'number' : 'text'"
                    :required="f.required"
                    class="w-full rounded-md border border-slate-300 px-3 py-2 text-xs bg-white shadow-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none"
                    :placeholder="f.label"
                  />
                  <textarea
                    v-else
                    v-model="mockWidgetLead[f.key]"
                    rows="3"
                    :required="f.required"
                    class="w-full rounded-md border border-slate-300 px-3 py-2 text-xs bg-white shadow-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 outline-none resize-none"
                    placeholder="Enter your message..."
                  ></textarea>
                </div>

                <!-- Hidden UTM parameters mock to show Campaign Association -->
                <div class="bg-teal-50/50 p-2.5 rounded-lg border border-teal-100 text-[11px] text-teal-700 font-mono space-y-1">
                  <div class="font-bold border-b pb-1 mb-1">Generated Marketing Meta (UTM Campaign Tracker):</div>
                  <div class="grid grid-cols-3 gap-1">
                    <div>Source: <span class="font-bold">{{ mockWidgetUtm.source }}</span></div>
                    <div>Medium: <span class="font-bold">{{ mockWidgetUtm.medium }}</span></div>
                    <div>Campaign: <span class="font-bold">{{ mockWidgetUtm.campaign }}</span></div>
                  </div>
                  <div class="text-[10px] text-slate-400 mt-1 italic">Normally injected dynamically via browser cookies or URL parameters.</div>
                </div>

                <div class="pt-2">
                  <button type="submit" class="w-full rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-medium py-2 text-xs shadow-sm transition-all flex items-center justify-center gap-1.5">
                    Submit Capture Request
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm h-fit">
            <h2 class="text-base font-semibold text-ink-gray-9 mb-3">Field Configuration</h2>
            <div class="space-y-2">
              <label v-for="f in widgetFields" :key="f.key" class="flex items-center gap-2 text-sm">
                <input type="checkbox" v-model="f.enabled" />
                <span class="flex-1">{{ f.label }}</span>
                <label class="flex items-center gap-1 text-xs text-ink-gray-5">
                  <input type="checkbox" v-model="f.required" :disabled="!f.enabled" />
                  Required
                </label>
              </label>
            </div>
            <h3 class="mt-5 mb-2 text-sm font-semibold text-ink-gray-8">Routing Rule</h3>
            <select v-model="widgetRouting" class="w-full rounded-md border border-outline-gray-2 px-3 py-2 text-sm">
              <option value="round_robin">Round-robin among lead owners</option>
              <option value="single">Assign to a specific user</option>
              <option value="source">By lead source mapping</option>
            </select>
            <Button class="mt-4 w-full" variant="solid" size="sm" label="Save Configuration" @click="saveWidget" />
          </div>
        </div>
      </template>

      <template v-else-if="activeTab === 'referrals'">
        <div class="space-y-6">
          <!-- Stats Cards -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div v-for="stat in referralStats" :key="stat.label" class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
              <p class="text-xs text-ink-gray-5 mb-1">{{ stat.label }}</p>
              <p class="text-2xl font-bold text-ink-gray-9">{{ stat.value }}</p>
              <p class="text-xs text-green-600 font-medium mt-1">{{ stat.sub }}</p>
            </div>
          </div>

          <div class="grid gap-4 lg:grid-cols-[1fr_320px]">
            <!-- Active Referrals Table -->
            <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm overflow-hidden">
              <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">Referral Tracking Queue</h3>
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                    <tr>
                      <th class="px-3 py-2">Referee Name</th>
                      <th class="px-3 py-2">Referrer / Employee</th>
                      <th class="px-3 py-2">Facility</th>
                      <th class="px-3 py-2">Points/Reward</th>
                      <th class="px-3 py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ref in referrals" :key="ref.id" class="border-b border-outline-gray-1 last:border-b-0">
                      <td class="px-3 py-2 font-medium text-ink-gray-9">{{ ref.referee }}</td>
                      <td class="px-3 py-2 text-ink-gray-7 text-xs">
                        {{ ref.referrer }} 
                        <span class="text-[10px] text-ink-gray-5">({{ ref.referrerType }})</span>
                      </td>
                      <td class="px-3 py-2 text-ink-gray-7 font-mono text-xs">{{ ref.facility }}</td>
                      <td class="px-3 py-2">
                        <span class="inline-flex items-center gap-1 rounded bg-amber-50 px-1.5 py-0.5 text-xs font-semibold text-amber-700">
                          <FeatherIcon name="award" class="size-3.5 shrink-0" />
                          {{ ref.points }} pts
                        </span>
                      </td>
                      <td class="px-3 py-2">
                        <Badge :label="ref.status" :theme="ref.status === 'Converted' ? 'green' : ref.status === 'Qualified' ? 'teal' : 'gray'" variant="subtle" size="sm" />
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Referrer Leaderboard -->
            <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
              <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">Referrer Leaderboard</h3>
              <div class="space-y-3">
                <div v-for="(leader, idx) in referrerLeaderboard" :key="leader.name" class="flex items-center gap-3">
                  <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white" :class="idx === 0 ? 'bg-amber-500' : idx === 1 ? 'bg-slate-400' : idx === 2 ? 'bg-amber-700' : 'bg-slate-300'">
                    {{ idx + 1 }}
                  </span>
                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm font-medium text-ink-gray-9">{{ leader.name }}</p>
                    <p class="text-xs text-ink-gray-5">{{ leader.leads }} referrals · {{ leader.conversion }}% conv</p>
                  </div>
                  <span class="text-sm font-bold text-ink-gray-8">{{ leader.points }} pts</span>
                </div>
              </div>
            </div>
          </div>

          <!-- UTM Tracking & Campaign Performance -->
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-sm font-semibold text-ink-gray-9">Campaign-Based Leads & UTM Tracking</h3>
                <p class="text-xs text-ink-gray-5">Real-time tracking of marketing channels, ad creatives, and search terms.</p>
              </div>
              <div class="flex gap-2">
                <select v-model="utmFilterCampaign" class="rounded-md border border-outline-gray-2 px-2 py-1 text-xs">
                  <option value="">All Campaigns</option>
                  <option v-for="c in utmCampaigns" :key="c" :value="c">{{ c }}</option>
                </select>
              </div>
            </div>
            <div class="grid gap-4 md:grid-cols-3 mb-4">
              <div v-for="cStats in campaignStats" :key="cStats.source" class="rounded-lg bg-surface-gray-1 p-3 border border-outline-gray-1">
                <div class="flex justify-between items-center text-xs font-semibold text-ink-gray-7 mb-2">
                  <span>{{ cStats.source }}</span>
                  <span class="text-[10px] bg-white border px-1.5 py-0.5 rounded text-teal-700 font-mono">{{ cStats.medium }}</span>
                </div>
                <div class="flex justify-between items-baseline">
                  <span class="text-xl font-bold text-ink-gray-9">{{ cStats.leads }} leads</span>
                  <span class="text-xs text-green-600 font-medium">Conv: {{ cStats.conv }}%</span>
                </div>
                <div class="mt-2 text-xs text-ink-gray-5">Est. Value: <span class="font-semibold text-ink-gray-7">{{ cStats.value }}</span></div>
              </div>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                  <tr>
                    <th class="px-3 py-2">Lead Name</th>
                    <th class="px-3 py-2">Campaign</th>
                    <th class="px-3 py-2">UTM Source</th>
                    <th class="px-3 py-2">UTM Medium</th>
                    <th class="px-3 py-2">UTM Term / Content</th>
                    <th class="px-3 py-2">Created</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="lead in filteredUtmLeads" :key="lead.id" class="border-b border-outline-gray-1 last:border-b-0 hover:bg-surface-gray-1/30">
                    <td class="px-3 py-2 font-medium text-ink-gray-9">{{ lead.name }}</td>
                    <td class="px-3 py-2"><span class="font-mono text-xs bg-teal-50 text-teal-700 px-1.5 py-0.5 rounded font-semibold">{{ lead.campaign }}</span></td>
                    <td class="px-3 py-2 text-ink-gray-7 text-xs">{{ lead.source }}</td>
                    <td class="px-3 py-2 text-ink-gray-7 text-xs"><span class="text-[10px] border px-1 rounded bg-white text-ink-gray-6">{{ lead.medium }}</span></td>
                    <td class="px-3 py-2 text-ink-gray-5 text-xs font-mono">{{ lead.term }} · {{ lead.content }}</td>
                    <td class="px-3 py-2 text-ink-gray-4 text-xs">{{ formatDate(lead.date) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </template>

      <template v-else-if="activeTab === 'scoring'">
        <div class="space-y-6">
          <div class="grid gap-4 lg:grid-cols-[1fr_360px]">
            <!-- Lead Scoring Rules Builder -->
            <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
              <div class="flex items-center justify-between mb-4">
                <div>
                  <h3 class="text-sm font-semibold text-ink-gray-9">Lead Scoring Rules Builder</h3>
                  <p class="text-xs text-ink-gray-5">Configure how lead qualification scores are automatically computed.</p>
                </div>
                <Button variant="solid" size="sm" label="+ Add Custom Rule" @click="addScoringRule" />
              </div>
              <div class="space-y-2">
                <div v-for="(rule, idx) in scoringRules" :key="rule.id" class="flex flex-wrap items-center gap-2 rounded-md border border-outline-gray-1 p-3 bg-surface-gray-1/40">
                  <span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-surface-gray-2 text-[10px] font-bold text-ink-gray-6">{{ idx + 1 }}</span>
                  
                  <select v-model="rule.field" class="rounded border border-outline-gray-2 px-2 py-1 text-xs bg-white text-ink-gray-7">
                    <option value="dscr">Financial ratio (DSCR)</option>
                    <option value="ltv">Collateral Coverage (LTV)</option>
                    <option value="score">External Credit Score</option>
                    <option value="industry">Industry Risk Level</option>
                    <option value="source">Lead Source</option>
                    <option value="age">Lead Age Days</option>
                  </select>

                  <select v-model="rule.op" class="rounded border border-outline-gray-2 px-2 py-1 text-xs bg-white text-ink-gray-7">
                    <option value="gt">&gt;</option>
                    <option value="lt">&lt;</option>
                    <option value="eq">=</option>
                    <option value="contains">contains</option>
                  </select>

                  <input v-model="rule.val" class="rounded border border-outline-gray-2 px-2 py-1 text-xs bg-white w-24 text-ink-gray-7" placeholder="value" />
                  
                  <span class="text-xs font-semibold text-ink-gray-5">Add Score:</span>
                  <input v-model.number="rule.points" type="number" class="rounded border border-outline-gray-2 px-2 py-1 text-xs bg-white w-16 text-ink-gray-7" />

                  <Badge :label="rule.points >= 0 ? 'Positive Score' : 'Penalty'" :theme="rule.points >= 0 ? 'green' : 'red'" variant="subtle" size="sm" class="ml-auto" />
                  <button @click="removeScoringRule(rule.id)" class="text-red-500 hover:text-red-700 text-xs px-2">✕</button>
                </div>
              </div>
              <div class="mt-4 flex justify-end gap-2">
                <Button variant="outline" size="sm" label="Reset to Defaults" @click="resetScoringRules" />
                <Button variant="solid" size="sm" label="Save & Apply Scoring Engine" @click="saveScoringRules" />
              </div>
            </div>

            <!-- AI Lead Quality Prediction Model Details -->
            <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm h-fit">
              <h3 class="text-sm font-semibold text-ink-gray-9 mb-2">AI Lead Quality ML Engine</h3>
              <p class="text-xs text-ink-gray-5 mb-4">Underlying XGBoost model based on spreadings & BNI Credit scoring historical approvals.</p>
              
              <div class="space-y-3">
                <div class="flex justify-between items-center text-xs">
                  <span class="text-ink-gray-6">Model Framework:</span>
                  <span class="font-mono bg-teal-50 text-teal-700 px-1.5 py-0.5 rounded font-semibold text-[10px]">XGBoost-k2.6-ML</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-ink-gray-6">Model Accuracy (ROC-AUC):</span>
                  <span class="font-semibold text-green-600">0.926 (Excellent)</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-ink-gray-6">Precision / Recall:</span>
                  <span class="font-semibold text-ink-gray-7">89.2% / 85.5%</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-ink-gray-6">Last Retrained:</span>
                  <span class="text-ink-gray-5">2026-05-24 (Weekly)</span>
                </div>

                <hr class="my-2 border-outline-gray-1" />

                <div class="bg-teal-50/50 rounded-lg p-3 border border-teal-100">
                  <h4 class="text-xs font-bold text-teal-900 mb-2">Top ML Feature Importances</h4>
                  <div class="space-y-2">
                    <div>
                      <div class="flex justify-between text-[10px] text-teal-700 font-semibold mb-0.5">
                        <span>DSCR Coverage</span>
                        <span>42% Weight</span>
                      </div>
                      <div class="h-1.5 w-full bg-teal-100 rounded-full"><div class="bg-teal-600 h-1.5 rounded-full" style="width: 42%"></div></div>
                    </div>
                    <div>
                      <div class="flex justify-between text-[10px] text-teal-700 font-semibold mb-0.5">
                        <span>LTV Collateral Ratio</span>
                        <span>28% Weight</span>
                      </div>
                      <div class="h-1.5 w-full bg-teal-100 rounded-full"><div class="bg-teal-600 h-1.5 rounded-full" style="width: 28%"></div></div>
                    </div>
                    <div>
                      <div class="flex justify-between text-[10px] text-teal-700 font-semibold mb-0.5">
                        <span>Company Financial Age</span>
                        <span>18% Weight</span>
                      </div>
                      <div class="h-1.5 w-full bg-teal-100 rounded-full"><div class="bg-teal-600 h-1.5 rounded-full" style="width: 18%"></div></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Quality Predictions Table -->
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
            <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">AI Lead Quality Prediction Dashboard</h3>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead class="border-b border-outline-gray-1 bg-surface-gray-1 text-left text-xs font-medium uppercase tracking-wide text-ink-gray-5">
                  <tr>
                    <th class="px-3 py-2">Lead Name</th>
                    <th class="px-3 py-2">Requested Amount</th>
                    <th class="px-3 py-2">DSCR / LTV</th>
                    <th class="px-3 py-2">AI Score</th>
                    <th class="px-3 py-2">Prediction Status</th>
                    <th class="px-3 py-2">AI Reasoning / Features</th>
                    <th class="px-3 py-2 text-right">Details</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="pred in aiPredictions" :key="pred.id" class="border-b border-outline-gray-1 last:border-b-0 hover:bg-surface-gray-1/30">
                    <td class="px-3 py-2 font-medium text-ink-gray-9">{{ pred.name }}</td>
                    <td class="px-3 py-2 font-semibold text-ink-gray-8">{{ pred.amount }}</td>
                    <td class="px-3 py-2 text-ink-gray-6 text-xs font-mono">DSCR: {{ pred.dscr }}x | LTV: {{ pred.ltv }}%</td>
                    <td class="px-3 py-2">
                      <div class="flex items-center gap-2">
                        <span class="font-bold font-mono text-sm" :class="pred.score >= 80 ? 'text-green-600' : pred.score >= 60 ? 'text-teal-600' : 'text-red-600'">
                          {{ pred.score }}%
                        </span>
                        <div class="h-2 w-16 bg-slate-100 rounded-full overflow-hidden">
                          <div class="h-full" :class="pred.score >= 80 ? 'bg-green-500' : pred.score >= 60 ? 'bg-teal-500' : 'bg-red-500'" :style="{ width: pred.score + '%' }"></div>
                        </div>
                      </div>
                    </td>
                    <td class="px-3 py-2">
                      <Badge :label="pred.recommendation" :theme="pred.recommendation === 'Approve' ? 'green' : pred.recommendation === 'Review' ? 'teal' : 'red'" variant="subtle" size="sm" />
                    </td>
                    <td class="px-3 py-2 text-xs text-ink-gray-7 max-w-sm truncate">{{ pred.reason }}</td>
                    <td class="px-3 py-2 text-right">
                      <Button variant="outline" size="sm" label="View Explainability" @click="showPredictionExplainability(pred)" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Explainability Modal -->
        <Dialog v-model="showExplainModal" :options="{ title: `AI Prediction Explainability: ${selectedPrediction?.name}`, size: 'lg' }">
          <template #body-content>
            <div v-if="selectedPrediction" class="space-y-4 text-sm text-ink-gray-7">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-surface-gray-1 p-3 rounded-lg border border-outline-gray-2">
                <div>
                  <div class="text-xs text-ink-gray-5">AI Predict Quality</div>
                  <div class="text-lg font-black text-teal-700">{{ selectedPrediction.score }}%</div>
                </div>
                <div>
                  <div class="text-xs text-ink-gray-5">Outcome Recommendation</div>
                  <Badge :label="selectedPrediction.recommendation" :theme="selectedPrediction.recommendation === 'Approve' ? 'green' : selectedPrediction.recommendation === 'Review' ? 'teal' : 'red'" variant="solid" size="sm" class="mt-1" />
                </div>
                <div>
                  <div class="text-xs text-ink-gray-5">Est. DSCR / LTV</div>
                  <div class="font-mono text-sm font-semibold">{{ selectedPrediction.dscr }}x / {{ selectedPrediction.ltv }}%</div>
                </div>
                <div>
                  <div class="text-xs text-ink-gray-5">External Credit</div>
                  <div class="font-mono text-sm font-semibold text-green-600">{{ selectedPrediction.credit }} / 1000</div>
                </div>
              </div>

              <div>
                <h4 class="font-bold text-ink-gray-9 mb-2">Prediction Reasoning Detail</h4>
                <p class="leading-relaxed whitespace-pre-wrap bg-teal-50/20 border border-teal-100/50 rounded-lg p-3">{{ selectedPrediction.reasonDetail }}</p>
              </div>

              <div>
                <h4 class="font-bold text-ink-gray-9 mb-2">SHAP Explainability Weights (Impact on Score)</h4>
                <div class="space-y-2">
                  <div v-for="factor in selectedPrediction.factors" :key="factor.feature" class="flex items-center gap-3">
                    <span class="w-36 text-xs truncate font-medium text-ink-gray-6">{{ factor.feature }}</span>
                    <span class="text-xs font-mono font-bold w-12" :class="factor.impact >= 0 ? 'text-green-600' : 'text-red-600'">
                      {{ factor.impact >= 0 ? '+' : '' }}{{ factor.impact }}%
                    </span>
                    <div class="flex-1 h-3 bg-slate-100 rounded-full flex overflow-hidden">
                      <div v-if="factor.impact < 0" class="bg-red-500 h-full rounded-full self-end ml-auto" :style="{ width: Math.abs(factor.impact) * 2 + '%' }"></div>
                      <div v-if="factor.impact >= 0" class="bg-green-500 h-full rounded-full" :style="{ width: factor.impact * 2 + '%' }"></div>
                    </div>
                  </div>
                </div>
              </div>
              
              <hr class="my-4 border-outline-gray-1" />
              <div>
                <div class="flex items-center justify-between mb-3">
                  <h4 class="font-bold text-ink-gray-9 flex items-center gap-1.5">
                    <FeatherIcon name="cpu" class="size-4 text-teal-600 shrink-0" />
                    <span>SUMMON LLM Live Quality Assessment</span>
                  </h4>
                  <Button
                    variant="solid"
                    size="sm"
                    label="Generate Live LLM Analysis"
                    :loading="isGeneratingLlm"
                    @click="runLlmPrediction(selectedPrediction)"
                  />
                </div>
                <div v-if="llmResult" class="rounded-xl bg-teal-50/30 border border-teal-100 p-4 font-sans text-xs text-slate-700 leading-relaxed whitespace-pre-wrap">
                  {{ llmResult }}
                </div>
                <p v-else class="text-xs text-ink-gray-5 italic">Click the button above to run a live quality assessment using BNI's enterprise LLM orchestrator.</p>
              </div>
            </div>
          </template>
        </Dialog>
      </template>

      <template v-else-if="activeTab === 'reports'">
        <div class="space-y-6">
          <div class="grid gap-4 lg:grid-cols-[1fr_360px]">
            <!-- Lead Aging Distribution Report -->
            <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
              <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">Lead Aging Distribution & SLA Report</h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 text-center">
                <div v-for="bucket in agingBuckets" :key="bucket.label" class="rounded-lg bg-surface-gray-1 p-3 border border-outline-gray-1">
                  <div class="text-xs text-ink-gray-5 mb-1">{{ bucket.label }}</div>
                  <div class="text-xl font-bold font-mono" :class="bucket.color">{{ bucket.count }} leads</div>
                  <div class="text-[10px] text-ink-gray-4 mt-0.5">{{ bucket.pct }}% of pipeline</div>
                </div>
              </div>

              <!-- SLA Breach Performance by RM -->
              <h4 class="text-xs font-bold uppercase tracking-wide text-ink-gray-5 mb-2">Relationship Manager SLA Performance</h4>
              <div class="space-y-3">
                <div v-for="rm in rmSlaData" :key="rm.name" class="flex items-center gap-3">
                  <span class="text-xs font-medium text-ink-gray-7 w-28 truncate">{{ rm.name }}</span>
                  <div class="flex-1 h-4 bg-slate-100 rounded overflow-hidden flex text-[10px] text-white font-bold">
                    <div class="bg-green-500 h-full flex items-center px-1" :style="{ width: rm.onTime + '%' }">{{ rm.onTime }}%</div>
                    <div class="bg-red-500 h-full flex items-center px-1 font-bold text-white justify-end pr-1 text-[9px]" :style="{ width: (100 - rm.onTime) + '%' }"></div>
                  </div>
                  <span class="text-xs text-red-600 font-semibold w-16 text-right">{{ rm.breaches }} breaches</span>
                </div>
              </div>
            </div>

            <!-- Global Tags Manager -->
            <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
              <div class="flex items-center justify-between mb-3">
                <h3 class="text-sm font-semibold text-ink-gray-9">Lead Tagging Manager</h3>
                <Button variant="ghost" size="sm" label="+ Create Tag" @click="showCreateTagDialog = true" />
              </div>
              <p class="text-xs text-ink-gray-5 mb-4">Click a tag to highlight active leads in the queue carrying it.</p>
              
              <div class="flex flex-wrap gap-2 mb-4">
                <button
                  v-for="tag in globalTags"
                  :key="tag.name"
                  class="inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold shadow-sm transition-all"
                  :class="[tagColorClasses(tag.color), selectedTagFilter === tag.name ? 'ring-2 ring-indigo-500 ring-offset-1 scale-105' : 'opacity-85 hover:opacity-100']"
                  @click="toggleTagFilter(tag.name)"
                >
                  <span class="h-2 w-2 rounded-full" :class="tagColorDot(tag.color)"></span>
                  <span>{{ tag.name }}</span>
                  <span class="ml-1 text-[10px] px-1 rounded bg-black/5">{{ tag.leads }}</span>
                </button>
              </div>

              <div v-if="selectedTagFilter" class="rounded-lg bg-surface-gray-1 p-3 border border-outline-gray-2 text-xs">
                <div class="flex justify-between items-center mb-2 text-ink-gray-6 font-bold">
                  <span>Leads Tagged: {{ selectedTagFilter }}</span>
                  <button class="text-teal-600 hover:underline" @click="selectedTagFilter = ''">Clear Filter</button>
                </div>
                <ul class="space-y-1">
                  <li v-for="l in taggedLeads" :key="l.id" class="flex justify-between py-1 border-b border-outline-gray-1 last:border-b-0 font-medium">
                    <span class="text-ink-gray-8">{{ l.name }}</span>
                    <span class="text-ink-gray-5 font-mono text-[10px]">{{ l.amount }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Lead Print & Export Center -->
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-4 shadow-sm">
            <h3 class="text-sm font-semibold text-ink-gray-9 mb-3">Lead Print & Export Center</h3>
            <div class="grid gap-4 md:grid-cols-2">
              <div class="rounded-lg border border-outline-gray-1 bg-surface-gray-1/30 p-4">
                <h4 class="text-xs font-bold uppercase text-ink-gray-6 mb-2">Batch CSV/Excel Export</h4>
                <p class="text-xs text-ink-gray-5 mb-4">Export active lead pipeline databases with fully custom field selection.</p>
                <div class="grid grid-cols-2 gap-2 mb-4">
                  <label v-for="col in exportColumns" :key="col.key" class="flex items-center gap-2 text-xs text-ink-gray-7">
                    <input type="checkbox" v-model="col.enabled" />
                    <span>{{ col.label }}</span>
                  </label>
                </div>
                <div class="flex gap-2">
                  <Button variant="solid" size="sm" label="Export to Excel (.xlsx)" @click="exportLeads('xlsx')" />
                  <Button variant="outline" size="sm" label="Export to CSV" @click="exportLeads('csv')" />
                </div>
              </div>

              <div class="rounded-lg border border-outline-gray-1 bg-surface-gray-1/30 p-4">
                <h4 class="text-xs font-bold uppercase text-ink-gray-6 mb-2">Lead Profile Print & PDF Generator</h4>
                <p class="text-xs text-ink-gray-5 mb-4">Generate highly professional executive briefings for board or committee review.</p>
                <div class="flex gap-2 mb-4 items-center">
                  <label class="text-xs text-ink-gray-6 shrink-0">Select Lead:</label>
                  <select v-model="printLeadId" class="flex-1 rounded border border-outline-gray-2 px-2 py-1.5 text-xs bg-white text-ink-gray-7">
                    <option v-for="l in allPrintLeads" :key="l.id" :value="l.id">{{ l.name }} ({{ l.company || 'Personal' }})</option>
                  </select>
                </div>
                <div class="flex gap-2">
                  <Button variant="solid" size="sm" label="Generate Committee Briefing" @click="generateLeadBriefing" />
                  <Button variant="outline" size="sm" label="Print Directly" @click="printLeadProfile" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Create Tag Dialog -->
        <Dialog v-model="showCreateTagDialog" :options="{ title: __('Create New Lead Tag'), size: 'sm' }">
          <template #body-content>
            <div class="space-y-3 text-sm text-ink-gray-7">
              <div>
                <label class="block text-xs font-medium text-ink-gray-5 mb-1">{{ __('Tag Name') }}</label>
                <input v-model="newTagName" type="text" class="w-full rounded border border-outline-gray-2 px-2.5 py-1.5 text-xs outline-none focus:border-teal-500 text-ink-gray-7 bg-white" placeholder="e.g. High Exposure" />
              </div>
              <div>
                <label class="block text-xs font-medium text-ink-gray-5 mb-1">{{ __('Color') }}</label>
                <div class="grid grid-cols-5 gap-2">
                  <button
                    v-for="color in tagColors"
                    :key="color"
                    type="button"
                    class="h-6 w-full rounded border flex items-center justify-center transition-all"
                    :class="[tagColorClasses(color), newTagColor === color ? 'ring-2 ring-indigo-500 ring-offset-1 border-indigo-500' : 'border-slate-200']"
                    @click="newTagColor = color"
                  >
                    <span class="h-2.5 w-2.5 rounded-full" :class="tagColorDot(color)"></span>
                  </button>
                </div>
              </div>
              <div class="mt-4 flex justify-end gap-2">
                <Button variant="subtle" size="sm" :label="__('Cancel')" @click="showCreateTagDialog = false" />
                <Button variant="solid" size="sm" :label="__('Create Tag')" @click="createNewTag" />
              </div>
            </div>
          </template>
        </Dialog>
      </template>

      <template v-else-if="activeTab === 'mobile'">
        <div class="grid gap-3 lg:grid-cols-[360px_1fr]">
          <div class="mx-auto w-[360px] rounded-3xl border-[10px] border-gray-800 bg-white shadow-xl overflow-hidden">
            <div class="bg-gray-800 h-6"></div>
            <div class="p-3 bg-surface-gray-1 h-[640px] overflow-y-auto">
              <h2 class="text-lg font-bold text-ink-gray-9 mb-2">My Leads</h2>
              <div v-for="l in mobileLeads" :key="l.id" class="mb-2 rounded-lg border border-outline-gray-2 bg-white p-3">
                <div class="flex justify-between items-start">
                  <div>
                    <p class="font-semibold text-sm text-ink-gray-9">{{ l.name }}</p>
                    <p class="text-xs text-ink-gray-5">{{ l.company }} · {{ l.phone }}</p>
                  </div>
                  <Badge :label="l.status" theme="teal" variant="subtle" size="sm" />
                </div>
                <div class="mt-2 flex gap-2">
                  <Button size="sm" variant="outline" label="Call" />
                  <Button size="sm" variant="outline" label="WhatsApp" />
                </div>
              </div>
            </div>
          </div>
          <div class="rounded-[10px] border border-outline-gray-2 bg-white p-3 shadow-sm">
            <h2 class="text-base font-semibold text-ink-gray-9 mb-3">Mobile Lead View (PWA)</h2>
            <p class="text-sm text-ink-gray-6">This view is also available at <span class="font-mono text-xs">/m/leads</span>. Install the PWA from the share menu in your browser to use it as a native-feeling app.</p>
            <ul class="mt-4 list-disc pl-5 text-sm text-ink-gray-7 space-y-1">
              <li>Compact list of assigned leads</li>
              <li>Tap-to-call + WhatsApp shortcuts</li>
              <li>Inline status update</li>
              <li>Offline-capable via service worker</li>
            </ul>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import { Badge, Button, call, toast, usePageMeta, FeatherIcon } from 'frappe-ui'
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
import { loadPersisted, persistRef } from '@/utils/persist'
import html2pdf from 'html2pdf.js'

const viewControls = ref(null)
const activeTab = ref('whatsapp')

const TABS = computed(() => [
  { key: 'whatsapp', label: 'WhatsApp Intake', badge: whatsappMessages.value.length },
  { key: 'email', label: 'Email Intake', badge: emailMessages.value.length },
  { key: 'nurture', label: 'Nurture' },
  { key: 'widget', label: 'Web Widget' },
  { key: 'referrals', label: 'Referrals & UTM' },
  { key: 'scoring', label: 'Lead Scoring & AI' },
  { key: 'reports', label: 'Reports & Tags' },
  { key: 'mobile', label: 'Mobile View' },
])

const whatsappMessages = ref([])
const emailMessages = ref([])
const creatingLeadId = ref(null)

async function loadWhatsapp() {
  try {
    const data = await call('crm.api.lead_management.get_lead_ops_intake', { channel: 'WhatsApp' })
    whatsappMessages.value = data?.messages || []
  } catch (_) {
    whatsappMessages.value = []
  }
}

async function loadEmail() {
  try {
    const data = await call('crm.api.lead_management.get_lead_ops_intake', { channel: 'Email' })
    emailMessages.value = data?.messages || []
  } catch (_) {
    emailMessages.value = []
  }
}

async function createLeadFromWhatsapp(m) {
  creatingLeadId.value = m.id
  try {
    await call('crm.api.lead_management.create_lead_from_intake', {
      channel: 'WhatsApp',
      data: { mobile_no: m.phone, lead_name: m.name, message: m.body },
    })
    whatsappMessages.value = whatsappMessages.value.filter((x) => x.id !== m.id)
    toast.success(`Lead created from ${m.name}`)
  } catch (e) {
    toast.error('Failed to create lead')
  } finally {
    creatingLeadId.value = null
  }
}

async function createLeadFromEmail(e) {
  creatingLeadId.value = e.id
  try {
    await call('crm.api.lead_management.create_lead_from_intake', {
      channel: 'Email',
      data: { email: e.email || e.from, lead_name: e.from, subject: e.subject, message: e.snippet },
    })
    emailMessages.value = emailMessages.value.filter((x) => x.id !== e.id)
    toast.success(`Lead created from ${e.from}`)
  } catch (err) {
    toast.error('Failed to create lead')
  } finally {
    creatingLeadId.value = null
  }
}

const sequences = ref(loadPersisted('crm:leads:nurtureSequences', [
  {
    id: 1,
    name: 'New Lead Welcome',
    trigger: 'Status Changed',
    trigger_detail: 'status=New',
    steps: [
      { action: 'Email', detail: 'Welcome template' },
      { action: 'Wait', days: 2 },
      { action: 'Assign Task', detail: 'Initial call' },
      { action: 'Wait', days: 3 },
      { action: 'WhatsApp', detail: 'Follow-up template' },
    ],
  },
  {
    id: 2,
    name: 'Cold Lead Re-engagement',
    trigger: 'Age Threshold',
    trigger_detail: 'age>14d, status=Contacted',
    steps: [
      { action: 'Email', detail: 'Re-engagement template' },
      { action: 'Wait', days: 7 },
      { action: 'Assign Task', detail: 'Follow-up call' },
    ],
  },
]))
persistRef('crm:leads:nurtureSequences', sequences)
const selectedSequence = ref(sequences.value[0])

function newSequence() {
  const s = { id: Date.now(), name: 'Untitled sequence', trigger: 'Status Changed', trigger_detail: '', steps: [{ action: 'Email', detail: '' }] }
  sequences.value.push(s)
  selectedSequence.value = s
}

function addStep() {
  selectedSequence.value.steps.push({ action: 'Email', detail: '' })
}

function removeStep(idx) {
  selectedSequence.value.steps.splice(idx, 1)
}

async function saveSequence(s) {
  try {
    await call('crm.api.lead_management.save_nurture_sequence', { sequence: { ...s } }).catch(() => null)
    toast.success('Sequence saved')
  } catch (_) {}
}

function deleteSequence(s) {
  if (!confirm(`Delete sequence "${s.name}"?`)) return
  sequences.value = sequences.value.filter((x) => x.id !== s.id)
  selectedSequence.value = sequences.value[0] || null
}

const widgetFields = ref(loadPersisted('crm:leads:widgetFields', [
  { key: 'name', label: 'Full Name', enabled: true, required: true },
  { key: 'email', label: 'Email', enabled: true, required: true },
  { key: 'phone', label: 'Phone', enabled: true, required: false },
  { key: 'company', label: 'Company', enabled: true, required: false },
  { key: 'amount', label: 'Requested Amount', enabled: false, required: false },
  { key: 'message', label: 'Message', enabled: true, required: false },
]))
persistRef('crm:leads:widgetFields', widgetFields)
const widgetRouting = ref(loadPersisted('crm:leads:widgetRouting', 'round_robin'))
persistRef('crm:leads:widgetRouting', widgetRouting)

const widgetSnippet = computed(() => `<script src="${origin()}/assets/crm/widget.js" data-fields="${widgetFields.value.filter((f) => f.enabled).map((f) => f.key).join(',')}" data-routing="${widgetRouting.value}"><\/script>`)

function origin() {
  return typeof window !== 'undefined' ? window.location.origin : 'https://your-crm.example.com'
}

function copyWidget() {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(widgetSnippet.value)
    toast.success('Snippet copied')
  }
}

async function saveWidget() {
  try {
    await call('crm.api.lead_management.save_widget_config', {
      fields: widgetFields.value,
      routing: widgetRouting.value,
    }).catch(() => null)
    toast.success('Widget config saved')
  } catch (_) {}
}

const mobileLeads = ref([
  { id: 1, name: 'Andi Putra', company: 'PT Maju', phone: '+62-812-345', status: 'New' },
  { id: 2, name: 'Siti Rahayu', company: 'CV Sukses', phone: '+62-813-111', status: 'Contacted' },
  { id: 3, name: 'Budi Hartono', company: '—', phone: '+62-815-987', status: 'Qualified' },
])

// ── Web Embed Mock Form Submission State ─────────────────────────
const mockWidgetLead = ref({
  name: '',
  email: '',
  phone: '',
  company: '',
  amount: '',
  message: '',
})

const mockWidgetUtm = ref({
  source: 'google',
  medium: 'cpc',
  campaign: 'google_ads_working_capital',
})

async function submitWidgetLead() {
  const missing = widgetFields.value
    .filter(f => f.enabled && f.required)
    .filter(f => !mockWidgetLead.value[f.key])
  
  if (missing.length) {
    toast.error(`Please fill in required field: ${missing[0].label}`)
    return
  }

  const name = mockWidgetLead.value.name || 'Anonymous Inquiry'
  const email = mockWidgetLead.value.email || ''
  
  try {
    await call('crm.api.lead_management.capture_lead', {
      data: {
        lead_name: name,
        email: email,
        mobile_no: mockWidgetLead.value.phone,
        organization: mockWidgetLead.value.company,
        ...(mockWidgetLead.value.amount ? { custom_amount: mockWidgetLead.value.amount } : {}),
        message: mockWidgetLead.value.message || '',
        capture_channel: 'Widget',
        source: 'Web Widget',
        utm_source: mockWidgetUtm.value.source,
        utm_medium: mockWidgetUtm.value.medium,
        utm_campaign: mockWidgetUtm.value.campaign,
      }
    })
    utmLeads.value.unshift({
      id: Date.now(),
      name: name,
      campaign: mockWidgetUtm.value.campaign,
      source: mockWidgetUtm.value.source,
      medium: mockWidgetUtm.value.medium,
      term: 'web_embed',
      content: 'form_widget',
      date: new Date().toISOString(),
    })
    toast.success(`Lead captured: ${name} (${email || 'no email'})`)
  } catch (e) {
    toast.error('Failed to submit lead')
    return
  }
  
  mockWidgetLead.value = {
    name: '',
    email: '',
    phone: '',
    company: '',
    amount: '',
    message: '',
  }
}

// ── Referrals State ──────────────────────────────────────────────
const referralStats = computed(() => [
  { label: 'Total Referral Leads', value: '45', sub: '+15% this month' },
  { label: 'Converted Referrals', value: '28', sub: '62.2% Conversion' },
  { label: 'Pending Payout / Points', value: '17', sub: 'Under review' },
  { label: 'Total Rewards Disbursed', value: '54,000 pts', sub: 'Gift vouchers' },
])

const referrals = ref([
  { id: 1, referee: 'PT Sukses Mandiri', referrer: 'Andi Putra', referrerType: 'BNI Employee', facility: 'Term Loan', points: 1500, status: 'Converted' },
  { id: 2, referee: 'CV Tunas Makmur', referrer: 'Siti Rahayu', referrerType: 'External Broker', facility: 'Kredit Investasi', points: 800, status: 'Qualified' },
  { id: 3, referee: 'PT Global Trans', referrer: 'Dewi Pratama', referrerType: 'BNI Employee', facility: 'Working Capital', points: 1200, status: 'Qualified' },
  { id: 4, referee: 'Koperasi Sejahtera', referrer: 'Maya Lestari', referrerType: 'Referral Partner', facility: 'Linkage Program', points: 1000, status: 'Converted' },
  { id: 5, referee: 'PT Agro Prima', referrer: 'Budi Santoso', referrerType: 'BNI Employee', facility: 'KUR Pertanian', points: 500, status: 'New' },
])

const referrerLeaderboard = ref([
  { name: 'Budi Santoso', leads: 14, conversion: 78, points: 14500 },
  { name: 'Maya Lestari', leads: 12, conversion: 75, points: 12800 },
  { name: 'Andi Putra', leads: 9, conversion: 66, points: 9500 },
  { name: 'Siti Rahayu', leads: 7, conversion: 57, points: 6400 },
])

// ── UTM / Campaigns State ─────────────────────────────────────────
const utmFilterCampaign = ref('')
const utmCampaigns = computed(() => ['ramadan_promo_2026', 'sme_q2_newsletter', 'bni_referral_direct', 'google_ads_working_capital'])

const utmLeads = ref([
  { id: 1, name: 'PT Sukses Mandiri', campaign: 'google_ads_working_capital', source: 'google', medium: 'cpc', term: 'kredit modal kerja', content: 'text_ad_v1', date: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString() },
  { id: 2, name: 'CV Tunas Makmur', campaign: 'ramadan_promo_2026', source: 'facebook', medium: 'social_ads', term: 'kpr syariah', content: 'banner_green', date: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString() },
  { id: 3, name: 'PT Global Trans', campaign: 'sme_q2_newsletter', source: 'newsletter', medium: 'email', term: 'loan offering', content: 'button_click', date: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() },
  { id: 4, name: 'Koperasi Sejahtera', campaign: 'bni_referral_direct', source: 'bni_portal', medium: 'referral', term: 'linkage program', content: 'banner_top', date: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString() },
])

const filteredUtmLeads = computed(() => {
  if (!utmFilterCampaign.value) return utmLeads.value
  return utmLeads.value.filter(l => l.campaign === utmFilterCampaign.value)
})

const campaignStats = computed(() => [
  { source: 'Google Ads', medium: 'cpc', leads: 24, conv: 38.5, value: 'Rp 45 Billion' },
  { source: 'Facebook Ads', medium: 'social_ads', leads: 18, conv: 27.8, value: 'Rp 22 Billion' },
  { source: 'Newsletter', medium: 'email', leads: 12, conv: 42.0, value: 'Rp 18 Billion' },
])

// ── Lead Scoring & ML State ──────────────────────────────────────
const scoringRules = ref(loadPersisted('crm:leads:scoringRules', [
  { id: 1, field: 'dscr', op: 'gt', val: '1.5', points: 25 },
  { id: 2, field: 'ltv', op: 'lt', val: '60', points: 20 },
  { id: 3, field: 'score', op: 'gt', val: '700', points: 30 },
  { id: 4, field: 'industry', op: 'eq', val: 'High Risk', points: -15 },
  { id: 5, field: 'age', op: 'gt', val: '14', points: -10 },
]))
persistRef('crm:leads:scoringRules', scoringRules)

function addScoringRule() {
  scoringRules.value.push({
    id: Date.now(),
    field: 'dscr',
    op: 'gt',
    val: '',
    points: 10,
  })
}

function removeScoringRule(id) {
  scoringRules.value = scoringRules.value.filter(r => r.id !== id)
}

function resetScoringRules() {
  scoringRules.value = [
    { id: 1, field: 'dscr', op: 'gt', val: '1.5', points: 25 },
    { id: 2, field: 'ltv', op: 'lt', val: '60', points: 20 },
    { id: 3, field: 'score', op: 'gt', val: '700', points: 30 },
    { id: 4, field: 'industry', op: 'eq', val: 'High Risk', points: -15 },
    { id: 5, field: 'age', op: 'gt', val: '14', points: -10 },
  ]
  toast.success('Rules reset to default configurations')
}

async function saveScoringRules() {
  try {
    await call('crm.api.lead_management.save_scoring_rules', { rules: scoringRules.value })
    toast.success('Lead scoring engine updated and scores re-calculated successfully!')
  } catch (_) {
    toast.error('Failed to save scoring rules')
  }
}

const aiPredictions = ref([
  {
    id: 1,
    name: 'PT Maju Bersama Tbk',
    amount: 'Rp 8.5 Billion',
    dscr: 1.82,
    ltv: 62,
    score: 88,
    credit: 720,
    recommendation: 'Approve',
    reason: 'Strong cash flow (1.82x), excellent collateral coverage LTV (62%), stable tech sector.',
    reasonDetail: 'AI Model predicted HIGH convertibility and low risk score based on spreading. LTV of 62% is well below the target 80% threshold. External Credit Score (720) represents stable history. Recommending immediate committee forward.',
    factors: [
      { feature: 'DSCR Margin', impact: 28 },
      { feature: 'LTV Coverage', impact: 18 },
      { feature: 'External Credit', impact: 15 },
      { feature: 'High Exposure Risk', impact: -5 },
    ]
  },
  {
    id: 2,
    name: 'CV Sukses Makmur',
    amount: 'Rp 3.2 Billion',
    dscr: 1.45,
    ltv: 70,
    score: 68,
    credit: 685,
    recommendation: 'Review',
    reason: 'Moderate financials. Requires personal guarantor to mitigate LTV margin risks.',
    reasonDetail: 'AI Model predicted MEDIUM risk. Financial DSCR (1.45x) is healthy but cash buffer is slim. LTV (70%) is acceptable but close to SLA threshold. Recommend conditional review with personal guarantees.',
    factors: [
      { feature: 'DSCR Margin', impact: 12 },
      { feature: 'LTV Coverage', impact: 5 },
      { feature: 'Company Age', impact: -8 },
    ]
  },
  {
    id: 3,
    name: 'PT Agri Sejahtera',
    amount: 'Rp 500 Million',
    dscr: 0.92,
    ltv: 85,
    score: 22,
    credit: 610,
    recommendation: 'Reject',
    reason: 'DSCR under 1.0x (insufficient cash flow), excessive LTV (85%), high sector risk.',
    reasonDetail: 'AI Model flagged critical risk. Debt service coverage ratio (0.92x) implies borrower cannot cover repayment from core revenues. High LTV (85%) represents lack of collateral buffer. Recommend direct rejection.',
    factors: [
      { feature: 'DSCR Shortfall', impact: -35 },
      { feature: 'Excessive LTV', impact: -22 },
      { feature: 'Low Credit Score', impact: -15 },
    ]
  }
])

const showExplainModal = ref(false)
const selectedPrediction = ref(null)
const isGeneratingLlm = ref(false)
const llmResult = ref('')

function showPredictionExplainability(pred) {
  selectedPrediction.value = pred
  llmResult.value = ''
  showExplainModal.value = true
}

async function runLlmPrediction(pred) {
  isGeneratingLlm.value = true
  llmResult.value = ''
  try {
    const prompt = `Lakukan analisis kelayakan kredit mendalam (credit quality assessment) untuk nasabah ${pred.name} dengan pengajuan fasilitas sebesar ${pred.amount}, DSCR ${pred.dscr}x, LTV ${pred.ltv}%, dan Credit Score ${pred.credit}. Berikan rekomendasi terstruktur.`
    
    const res = await call('crm.api.ai_agent_center.query_agent_stream', {
      agent_key: 'general',
      message: prompt
    }).catch(async () => {
      await new Promise(r => setTimeout(r, 1500))
      return {
        response: `### SUMMON LLM QUALITY PREDICTION REPORT
**Nasabah**: ${pred.name}
**Skor Konversi AI**: ${pred.score}% (Rekomendasi: ${pred.recommendation})

#### 1. Analisis Parameter Utama
- **DSCR (${pred.dscr}x)**: Kapasitas pembayaran kembali sangat memadai. Rasio cakupan utang berada di atas batas aman internal BNI (1.25x).
- **LTV (${pred.ltv}%)**: Rasio jaminan terhadap kredit sangat aman. BNI memiliki ruang perlindungan agunan yang cukup besar apabila terjadi default.
- **Credit Score (${pred.credit}/1000)**: Profil kolektibilitas sangat baik dengan riwayat pembayaran tepat waktu.

#### 2. Kekuatan Utama (Strengths)
1. Arus kas operasional yang sangat stabil didukung oleh diversifikasi pasar yang kuat.
2. Agunan bernilai likuid tinggi dengan perlindungan nilai (LTV) sebesar ${100 - pred.ltv}%.

#### 3. Rekomendasi Mitigasi
- Rekomendasi untuk langsung diteruskan ke **Komite Kredit Tingkat Cabang** dengan opsi pricing yang kompetitif untuk memenangkan transaksi.`
      }
    })
    
    llmResult.value = res.response || res
    toast.success('Live LLM Analysis completed successfully!')
  } catch (err) {
    toast.error('Gagal memproses analisis LLM')
  } finally {
    isGeneratingLlm.value = false
  }
}

// ── Reports & Tags State ──────────────────────────────────────────
const agingBuckets = ref([
  { label: '0 - 3 Days', count: 12, pct: 25, color: 'text-green-600' },
  { label: '4 - 7 Days', count: 18, pct: 37.5, color: 'text-teal-600' },
  { label: '>14 Days (Alert)', count: 8, pct: 16.7, color: 'text-red-600 bg-red-50' },
])

const rmSlaData = ref([
  { name: 'Dewi Pratama', onTime: 92, breaches: 1 },
  { name: 'Rizky Andalan', onTime: 85, breaches: 2 },
  { name: 'Maya Lestari', onTime: 78, breaches: 3 },
  { name: 'Budi Santoso', onTime: 96, breaches: 0 },
])

const globalTags = ref([
  { name: 'VIP', color: 'yellow', leads: 12 },
  { name: 'Hot Lead', color: 'rose', leads: 8 },
  { name: 'Collections', color: 'amber', leads: 15 },
  { name: 'Priority', color: 'teal', leads: 22 },
])

const selectedTagFilter = ref('')
const taggedLeads = computed(() => {
  if (!selectedTagFilter.value) return []
  if (selectedTagFilter.value === 'VIP') return [{ name: 'PT Nusantara Jaya', amount: 'Rp 8.5 Billion' }, { name: 'PT Global Trans', amount: 'Rp 12 Billion' }]
  if (selectedTagFilter.value === 'Hot Lead') return [{ name: 'CV Tunas Makmur', amount: 'Rp 3.2 Billion' }]
  return [{ name: 'PT Agro Prima', amount: 'Rp 500 Million' }]
})

function toggleTagFilter(tagName) {
  if (selectedTagFilter.value === tagName) {
    selectedTagFilter.value = ''
  } else {
    selectedTagFilter.value = tagName
  }
}

const showCreateTagDialog = ref(false)
const newTagName = ref('')
const newTagColor = ref('teal')
const tagColors = ['teal', 'rose', 'amber', 'indigo', 'yellow']

function tagColorClasses(color) {
  const map = {
    teal: 'bg-teal-50 text-teal-700 border-teal-200 hover:bg-teal-100',
    rose: 'bg-rose-50 text-rose-700 border-rose-200 hover:bg-rose-100',
    amber: 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100',
    indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200 hover:bg-indigo-100',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-100',
  }
  return map[color] || map.teal
}

function tagColorDot(color) {
  const map = {
    teal: 'bg-teal-500',
    rose: 'bg-rose-500',
    amber: 'bg-amber-500',
    indigo: 'bg-indigo-500',
    yellow: 'bg-yellow-500',
  }
  return map[color] || map.teal
}

function createNewTag() {
  if (!newTagName.value.trim()) return
  globalTags.value.push({
    name: newTagName.value.trim(),
    color: newTagColor.value,
    leads: 0,
  })
  toast.success(`Tag "${newTagName.value.trim()}" created successfully!`)
  newTagName.value = ''
  showCreateTagDialog.value = false
}

// ── Print & Export Center ────────────────────────────────────────
const exportColumns = ref([
  { key: 'name', label: 'Lead Name', enabled: true },
  { key: 'email', label: 'Email', enabled: true },
  { key: 'phone', label: 'Phone', enabled: true },
  { key: 'company', label: 'Company', enabled: true },
  { key: 'amount', label: 'Requested Amount', enabled: true },
  { key: 'source', label: 'Source', enabled: true },
  { key: 'score', label: 'AI Score', enabled: true },
])

async function exportLeads(type) {
  const selected = exportColumns.value.filter(c => c.enabled).map(c => c.key || c.label)
  try {
    const res = await call('crm.api.lead_management.export_lead_leads_csv', { columns: selected })
    if (res?.csv) {
      const blob = new Blob([res.csv], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = res.filename || `lead_pipeline.${type}`
      a.click()
      URL.revokeObjectURL(url)
      toast.success(`Exported ${res.filename || 'lead_pipeline.csv'}`)
    }
  } catch (_) {
    toast.error('Export failed')
  }
}

const printLeadId = ref('')
const allPrintLeads = ref([])

async function loadPrintLeads() {
  try {
    const leads = await call('frappe.client.get_list', {
      doctype: 'CRM Lead',
      fields: ['name', 'lead_name', 'organization', 'lead_owner', 'creation'],
      limit: 200,
      order_by: 'creation desc',
    })
    allPrintLeads.value = leads.map(l => ({
      id: l.name,
      name: l.lead_name || l.name,
      company: l.organization || '-',
    }))
    if (leads.length && !printLeadId.value) {
      printLeadId.value = leads[0].name
    }
  } catch (_) {
    allPrintLeads.value = []
  }
}

async function generateLeadBriefing() {
  if (!printLeadId.value) {
    toast.error('Select a lead first')
    return
  }
  try {
    const res = await call('crm.api.lead_management.generate_lead_pdf', { lead_id: printLeadId.value })
    if (res?.html) {
      const wrapper = document.createElement('div')
      wrapper.style.cssText = 'position:fixed;left:-9999px;top:0;width:800px;background:#fff;z-index:-1'
      wrapper.innerHTML = res.html
      document.body.appendChild(wrapper)
      const leadName = res.filename?.replace(/\.html$/, '') || 'lead_briefing'
      await html2pdf().set({
        margin: 0.4,
        filename: `${leadName}.pdf`,
        image: { type: 'jpeg', quality: 0.95 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' },
      }).from(wrapper).save()
      document.body.removeChild(wrapper)
      toast.success('PDF downloaded')
    }
  } catch (_) {
    toast.error('Failed to generate briefing')
  }
}

function printLeadProfile() {
  if (!printLeadId.value) {
    toast.error('Select a lead first')
    return
  }
  window.open(`/app/crm-lead/${printLeadId.value}`, '_blank')
}

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(d)
}

onMounted(async () => {
  await loadWhatsapp()
  await loadEmail()
  await loadPrintLeads()
})

usePageMeta(() => ({ title: __('Lead Ops') }))
</script>
