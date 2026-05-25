<template>
  <div class="flex h-full bg-slate-50 font-sans">
    <div v-if="!routeCustomer" class="w-80 border-r border-slate-200 bg-white flex flex-col shrink-0">
      <div class="p-4 border-b border-slate-200 space-y-3">
        <div>
          <h2 class="text-lg font-bold text-slate-800">{{ __('Customer Directory') }}</h2>
          <p class="text-xs text-slate-500">{{ __('Global search: name, NPWP, KTP, phone, email') }}</p>
        </div>
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="__('Search Customer (Global)')"
            class="w-full pl-9 pr-3 py-2 bg-slate-100 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-600 focus:bg-white transition-all"
          />
          <span class="absolute left-3 top-2.5 text-slate-400">
            <FeatherIcon name="search" class="h-4 w-4" />
          </span>
        </div>
        <div v-if="recentSearches.length" class="flex flex-wrap gap-1.5">
          <button
            v-for="item in recentSearches"
            :key="item"
            class="px-2 py-1 rounded-md bg-slate-100 text-[11px] font-semibold text-slate-500 hover:bg-teal-50 hover:text-teal-700"
            @click="searchQuery = item"
          >
            {{ item }}
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div
          v-for="cust in directoryCustomers"
          :key="cust.name"
          :class="selectedCustomerName === cust.name ? 'bg-teal-50 border border-teal-100' : ''"
          class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all hover:bg-slate-50"
          @click="selectCustomer(cust)"
        >
          <div class="w-10 h-10 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center font-bold text-sm shrink-0">
            {{ initials(cust.customer_name || cust.name) }}
          </div>
          <div class="min-w-0 flex-1">
            <div class="font-semibold text-sm text-slate-800 truncate">{{ cust.customer_name || cust.name }}</div>
            <div class="text-xs text-slate-500 truncate mt-0.5">{{ cust.preview || `${cust.customer_type || 'Customer'} - ${cust.territory || 'Default'}` }}</div>
          </div>
          <Badge v-if="cust.score" :label="String(cust.score)" theme="gray" variant="subtle" />
        </div>
        <div v-if="directoryCustomers.length === 0" class="text-center p-6 text-slate-400 text-sm">
          {{ __('No customers found') }}
        </div>
      </div>

      <div class="p-3 border-t border-slate-200">
        <Button class="w-full" variant="solid" :label="__('Add Customer')" @click="showAddCustomer = true">
          <template #prefix>
            <FeatherIcon name="plus" class="h-4 w-4" />
          </template>
        </Button>
      </div>
    </div>

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <div v-if="!selectedCustomer" class="flex-1 flex flex-col items-center justify-center text-slate-400 p-8">
        <div class="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center mb-4">
          <FeatherIcon name="user" class="h-10 w-10 text-slate-300" />
        </div>
        <h3 class="text-lg font-semibold text-slate-700">{{ __('No Customer Selected') }}</h3>
        <p class="text-sm text-slate-500 mt-1 max-w-sm text-center">
          {{ __('Select a customer to manage the complete Customer 360 UAT workspace.') }}
        </p>
      </div>

      <div v-else class="flex-1 flex flex-col overflow-hidden">
        <div class="bg-white border-b border-slate-200 p-6 flex flex-col xl:flex-row xl:items-center justify-between gap-6 shrink-0 shadow-sm">
          <div class="flex items-center gap-4 min-w-0">
            <div class="w-16 h-16 rounded-xl bg-teal-600 text-white flex items-center justify-center font-black text-2xl shadow-md shadow-teal-600/10 shrink-0">
              {{ initials(selectedCustomer.customer_name || selectedCustomer.name) }}
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-3 flex-wrap">
                <h1 class="text-2xl font-bold text-slate-800 truncate">{{ selectedCustomer.customer_name || selectedCustomer.name }}</h1>
                <Badge :label="selectedCustomer.customer_type || 'Customer'" theme="teal" variant="subtle" />
                <Badge v-if="summary.watchlist" label="Watchlist" theme="red" variant="subtle" />
                <Badge v-for="tag in tags.slice(0, 3)" :key="tag.name" :label="tag.tag" theme="gray" variant="subtle" />
              </div>
              <div class="text-sm text-slate-500 flex flex-wrap items-center gap-4 mt-1.5">
                <span class="flex items-center gap-1"><FeatherIcon name="hash" class="h-3.5 w-3.5 text-slate-400" />ID: {{ selectedCustomer.name }}</span>
                <span class="flex items-center gap-1"><FeatherIcon name="map-pin" class="h-3.5 w-3.5 text-slate-400" />{{ selectedCustomer.territory || __('National') }}</span>
                <span class="flex items-center gap-1"><FeatherIcon name="users" class="h-3.5 w-3.5 text-slate-400" />{{ selectedCustomer.customer_group || __('Default Group') }}</span>
              </div>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <Button v-if="routeCustomer" variant="outline" :label="__('Back to List')" @click="goToCustomerList">
              <template #prefix><FeatherIcon name="arrow-left" class="h-4 w-4" /></template>
            </Button>
            <Button variant="solid" :label="__('New Application')" @click="openForm('creditApplication')">
              <template #prefix><FeatherIcon name="file-plus" class="h-4 w-4" /></template>
            </Button>
            <Button variant="outline" :label="__('Communicate')" @click="openForm('communication')" />
            <Button variant="outline" :label="__('Export Profile')" @click="showExportDialog = true" />
            <Button variant="outline" :label="__('Edit')" @click="showProfileEdit = true" />
          </div>
        </div>

        <div class="grid grid-cols-2 xl:grid-cols-6 gap-4 px-6 pt-6 shrink-0">
          <StatCard :label="__('Total Outstanding')" :value="formatCurrency(summary.total_outstanding)" :detail="`${summary.active_facilities || 0} active facilities`" icon="dollar-sign" tone="orange" />
          <StatCard :label="__('Risk Grade')" :value="summary.risk_grade || 'Unrated'" :detail="`Score: ${summary.score || 0}`" icon="activity" tone="teal" />
          <StatCard :label="__('Group Exposure')" :value="formatCurrency(summary.group_exposure)" :detail="`${summary.related_entities || 0} relation records`" icon="globe" tone="blue" />
          <StatCard :label="__('KYC Status')" :value="summary.kyc_status || 'Pending'" :detail="summary.next_review_date ? `Next: ${summary.next_review_date}` : 'No review date'" icon="shield" tone="purple" />
          <StatCard :label="__('Documents')" :value="String(summary.documents || 0)" :detail="`${summary.expired_documents || 0} expired`" icon="folder" tone="slate" />
          <StatCard :label="__('Missed Payments')" :value="String(summary.missed_payments || 0)" :detail="`${summary.transactions || 0} transactions`" icon="repeat" tone="red" />
        </div>

        <div class="px-6 pt-4 shrink-0">
          <div class="flex border-b border-slate-200 gap-6 overflow-x-auto">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="pb-3 text-sm font-semibold border-b-2 transition-all whitespace-nowrap"
              :class="activeTab === tab.key ? 'border-teal-600 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6 min-h-0">
          <div v-if="customer360.loading" class="text-sm text-slate-500">{{ __('Loading customer profile...') }}</div>

          <div v-else-if="activeTab === 'overview'" class="space-y-6">
            <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <Panel class="xl:col-span-2" :title="__('AI Customer Summary')" icon="cpu">
                <div class="relative">
                  <div v-if="!editingSummary"
                    class="min-h-[150px] w-full p-4 bg-teal-50/30 border border-teal-100 rounded-lg text-sm text-slate-700 cursor-pointer hover:border-teal-300 prose prose-sm prose-teal max-w-none overflow-auto"
                    style="min-height: 144px"
                    @click="editingSummary = true"
                    v-html="renderMarkdown(summaryText)"
                  />
                  <textarea
                    v-else
                    v-model="summaryText"
                    rows="9"
                    class="w-full p-4 bg-white border border-teal-400 rounded-lg text-sm text-slate-700 focus:outline-none focus:border-teal-500 font-mono"
                    @blur="editingSummary = false"
                    ref="summaryTextareaRef"
                  />
                  <button
                    class="absolute top-2 right-2 rounded-md bg-white border border-slate-200 px-2 py-1 text-xs text-slate-500 hover:border-teal-400 hover:text-teal-700"
                    @click="editingSummary = !editingSummary"
                  >
                    {{ editingSummary ? __('Preview') : __('Edit') }}
                  </button>
                </div>
                <div class="mt-3 flex flex-wrap justify-between items-center gap-2 text-xs text-slate-400">
                  <span>{{ __('RAG summary generated from indexed Customer 360 records and documents') }}</span>
                  <div class="flex gap-2">
                    <select v-model="summaryLength" class="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-600 focus:outline-none focus:border-teal-500">
                      <option>TL;DR</option>
                      <option>Standard</option>
                      <option>Detailed</option>
                    </select>
                    <Button variant="subtle" size="sm" :label="__('Refresh')" @click="reloadCustomer360" />
                    <Button variant="outline" size="sm" :label="__('Generate with RAG')" :loading="isGeneratingSummary" @click="generateCustomerSummary" />
                    <Button variant="solid" size="sm" :label="__('Save Summary')" @click="saveCustomerSummary" />
                  </div>
                </div>
                <div v-if="summarySources.length" class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div v-for="source in summarySources" :key="source.id" class="rounded-lg border border-teal-100 bg-white p-3">
                    <div class="text-xs font-bold text-slate-800 truncate">{{ source.title }}</div>
                    <div class="mt-1 text-[11px] text-slate-500">{{ source.doctype }} · {{ source.docname }}</div>
                    <p class="mt-2 line-clamp-3 text-xs leading-5 text-slate-600">{{ source.excerpt }}</p>
                  </div>
                </div>
              </Panel>

              <Panel :title="__('Credit Score Display')" icon="shield">
                <div class="flex items-center gap-4 mb-4">
                  <div class="w-16 h-16 rounded-full border-4 border-teal-500 flex flex-col items-center justify-center bg-teal-50/50">
                    <span class="text-lg font-extrabold text-teal-700">{{ summary.score || '-' }}</span>
                    <span class="text-[9px] uppercase font-bold text-slate-400">{{ latestBureau?.source || 'Score' }}</span>
                  </div>
                  <div>
                    <div class="text-sm font-semibold text-slate-700">{{ summary.risk_grade || __('Unrated') }}</div>
                    <div class="text-xs text-slate-500">{{ __('Last update') }}: {{ latestBureau?.report_date || latestRisk?.grade_date || '-' }}</div>
                  </div>
                </div>
                <ScoreTrend :reports="bureauReports" :risks="riskProfiles" />
                <div class="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" :label="__('Add Bureau')" @click="openForm('bureau')" />
                  <Button variant="outline" size="sm" :label="__('Refresh Score')" @click="reloadCustomer360" />
                </div>
              </Panel>
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <Panel :title="__('Activities')" icon="calendar">
                <div class="flex flex-wrap gap-2 mb-4">
                  <Button size="sm" :variant="activityFilter === 'task' ? 'solid' : 'outline'" :label="__('Task')" @click="activityFilter = activityFilter === 'task' ? 'all' : 'task'" />
                  <Button size="sm" :variant="activityFilter === 'note' ? 'solid' : 'outline'" :label="__('Note')" @click="activityFilter = activityFilter === 'note' ? 'all' : 'note'" />
                  <Button size="sm" :variant="activityFilter === 'event' ? 'solid' : 'outline'" :label="__('Event')" @click="activityFilter = activityFilter === 'event' ? 'all' : 'event'" />
                  <Button size="sm" variant="outline" :label="__('+')" @click="openForm('task')" />
                  <Button size="sm" variant="outline" :label="__('+ Note')" @click="openForm('note')" />
                  <Button size="sm" variant="outline" :label="__('+ Event')" @click="openForm('event')" />
                </div>
                <ActivityList :tasks="tasks" :notes="notes" :events="events" :filter="activityFilter" @toggle-task="toggleTask" />
              </Panel>

              <Panel :title="__('Relationship Graph')" icon="share-2">
                <div class="mb-3 flex justify-between gap-2">
                  <FormSelect v-model="graphFilter" label="Filter" :options="['All', 'Shareholder', 'Director', 'Group Company', 'RM', 'UBO']" compact />
                  <div class="flex items-end gap-1">
                    <Button size="sm" variant="outline" label="+" @click="graphZoom += 0.1" />
                    <Button size="sm" variant="outline" label="-" @click="graphZoom = Math.max(0.8, graphZoom - 0.1)" />
                  </div>
                </div>
                <RelationshipGraph :customer="selectedCustomer" :relationships="filteredGraphRelationships" :zoom="graphZoom" @open-node="openRelatedCustomer" />
              </Panel>

              <Panel :title="__('Customer History Timeline')" icon="clock">
                <div class="mb-3">
                  <FormSelect v-model="timelineFilter" label="Filter" :options="timelineKinds" compact />
                </div>
                <TimelineList :items="filteredTimeline" />
              </Panel>
            </div>
          </div>

          <div v-else-if="activeTab === 'profile'" class="space-y-6">
            <Panel :title="__('Personal / Company Data')" icon="user-check">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Edit Profile')" @click="openForm('kyc', kyc || {})" />
              </template>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FieldDisplay label="Name" :value="selectedCustomer.customer_name" />
                <FieldDisplay label="Customer Type" :value="selectedCustomer.customer_type" />
                <FieldDisplay label="NPWP" :value="kyc?.npwp || selectedCustomer.tax_id" />
                <FieldDisplay label="KTP / NIK" :value="kyc?.nik" />
                <FieldDisplay label="DOB" :value="kyc?.date_of_birth" />
                <FieldDisplay label="Founded" :value="kyc?.founded_date" />
                <FieldDisplay label="Employees" :value="kyc?.employee_count" />
                <FieldDisplay label="e-KYC Result" :value="kyc?.ekyc_result || 'Manual'" />
                <FieldDisplay label="Audit" :value="selectedCustomer.modified ? `Last updated ${selectedCustomer.modified}` : 'Tracked by Frappe changes'" />
                <FieldDisplay class="md:col-span-3" label="Address" :value="kyc?.registered_address" />
              </div>
            </Panel>

            <Panel :title="__('KYC Status')" icon="shield">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add / Update KYC')" @click="openForm('kyc', kyc || {})" />
              </template>
              <SimpleTable
                :headers="['Status', 'Last KYC', 'Next Review', 'Renewal', 'e-KYC', 'Watchlist']"
                :rows="kyc ? [kyc] : []"
                :columns="['status', 'review_date', 'next_review_date', 'renewal_workflow_status', 'ekyc_result', 'watchlist_reason']"
                :edit="(row) => openForm('kyc', row)"
              />
            </Panel>
          </div>

          <div v-else-if="activeTab === 'ownership'" class="space-y-6">
            <div class="flex justify-end">
              <Button size="sm" variant="solid" :label="__('Add Relationship')" @click="openForm('relationship')" />
            </div>
            <Panel :title="__('Shareholders')" icon="pie-chart">
              <div class="mb-4 flex flex-wrap items-center gap-3">
                <Badge :label="`${summary.shareholder_total || 0}% ownership captured`" :theme="summary.shareholder_balanced ? 'green' : 'orange'" />
                <span class="text-xs text-slate-500">{{ __('UAT requires total shareholders to equal 100%.') }}</span>
              </div>
              <OwnershipChart :shareholders="shareholders" />
              <SimpleTable :headers="['Shareholder', 'Ownership %', 'UBO', 'Linked Profile']" :rows="shareholders" :columns="['related_party', 'ownership_percent', 'is_ubo', 'related_customer']" :edit="(row) => openForm('relationship', row)" />
            </Panel>

            <Panel :title="__('Directors')" icon="briefcase">
              <SimpleTable :headers="['Name', 'Role', 'ID', 'LinkedIn', 'Tenure', 'AML/PEP', 'Background']" :rows="directors" :columns="['related_party', 'position', 'director_id', 'linkedin_url', 'tenure_start', 'aml_pep_status', 'background_check_status']" :edit="(row) => openForm('relationship', row)" :action="runAmlCheck" action-label="AML/PEP" />
            </Panel>

            <Panel :title="__('Related Entities')" icon="git-branch">
              <SimpleTable :headers="['Entity', 'Type', 'Group Exposure', 'Linked Customer']" :rows="relatedEntities" :columns="['related_party', 'relationship_type', 'exposure', 'related_customer']" currency-column="exposure" :edit="(row) => openForm('relationship', row)" :action="openRelatedCustomer" action-label="Open" />
            </Panel>
          </div>

          <div v-else-if="activeTab === 'financing'" class="space-y-6">
            <Panel :title="__('Financing History')" icon="archive">
              <template #actions>
                <Button size="sm" variant="outline" :label="__('Export PDF')" @click="showExportDialog = true" />
              </template>
              <div class="mb-3 max-w-xs">
                <FormInput v-model="productFilter" label="Filter Product Type" />
              </div>
              <SimpleTable :headers="['Facility', 'Product', 'Status', 'Repayment', 'Default']" :rows="filteredFacilities" :columns="['facility_type', 'product_type', 'status', 'repayment_behavior', 'default_flag']" :edit="(row) => openForm('facility', row)" />
            </Panel>

            <Panel :title="__('Active Facilities')" icon="credit-card">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Facility')" @click="openForm('facility')" />
              </template>
              <SimpleTable :headers="['Facility', 'OS', 'Limit', 'Due Date', 'Health', 'Action']" :rows="activeFacilities" :columns="['facility_type', 'outstanding', 'limit_amount', 'due_date', 'health', 'action_status']" currency-column="outstanding,limit_amount" :edit="(row) => openForm('facility', row)" :action="requestRestructure" action-label="Restructure" />
            </Panel>

            <Panel :title="__('Bank Accounts')" icon="database">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Bank Account')" @click="openForm('bankAccount')" />
              </template>
              <SimpleTable :headers="['Bank', 'Number', 'Name', 'Primary', 'Verification', 'OTP']" :rows="bankAccounts" :columns="['bank', 'account_number', 'account_name', 'is_primary', 'verification_status', 'otp_status']" :edit="(row) => openForm('bankAccount', row)" />
            </Panel>

            <Panel :title="__('Collateral')" icon="home">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Collateral')" @click="openForm('collateral')" />
              </template>
              <SimpleTable :headers="['Asset', 'Type', 'Value', 'LTV', 'Insurance Expiry', 'Document', 'Re-appraisal']" :rows="collaterals" :columns="['asset', 'collateral_type', 'collateral_value', 'ltv_percent', 'insurance_expiry', 'document_link', 'reappraisal_status']" currency-column="collateral_value" :edit="(row) => openForm('collateral', row)" />
            </Panel>
          </div>

          <div v-else-if="activeTab === 'documents'" class="space-y-6">
            <Panel :title="__('Documents')" icon="folder">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Document')" @click="openForm('document')" />
              </template>
              <div class="mb-3">
                <FormInput v-model="documentSearch" label="Search / Tag" />
              </div>
              <SimpleTable :headers="['Folder', 'Type', 'Title', 'Version', 'Expiry', 'Tags', 'Preview']" :rows="filteredDocuments" :columns="['folder', 'document_type', 'title', 'version', 'expiry_status', 'tags', 'preview_status']" :edit="(row) => openForm('document', row)" :action="previewDocument" action-label="Preview" />
            </Panel>

            <Panel :title="__('Communications')" icon="message-square">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Compose')" @click="openForm('communication')" />
              </template>
              <div class="mb-3 max-w-xs">
                <FormSelect v-model="communicationFilter" label="Channel" :options="['All', 'Email', 'WA', 'SMS', 'Call']" />
              </div>
              <SimpleTable :headers="['Channel', 'Direction', 'Subject', 'Time', 'Status', 'Compose']" :rows="filteredCommunications" :columns="['channel', 'direction', 'subject', 'communication_time', 'status', 'compose_status']" :edit="(row) => openForm('communication', row)" :action="openConversation" action-label="Open" />
            </Panel>
          </div>

          <div v-else-if="activeTab === 'risk'" class="space-y-6">
            <Panel :title="__('Risk Profile')" icon="alert-triangle">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Risk Profile')" @click="openForm('risk')" />
              </template>
              <SimpleTable :headers="['Grade', 'Score', 'Watchlist', 'NPL', 'Factors', 'Early Warning']" :rows="riskProfiles" :columns="['risk_grade', 'internal_score', 'watchlist_status', 'npl_flag', 'risk_factors', 'early_warning_triggers']" :edit="(row) => openForm('risk', row)" />
            </Panel>

            <Panel :title="__('Watchlist Flag')" icon="flag">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FieldDisplay label="Status" :value="summary.watchlist ? 'Watchlist' : 'Normal'" />
                <FieldDisplay label="Reason" :value="kyc?.watchlist_reason" />
                <FieldDisplay label="Removal Approval" :value="kyc?.watchlist_remove_approval || 'Not Required'" />
              </div>
              <Button class="mt-4" variant="solid" :label="__('Update Watchlist')" @click="openForm('kyc', kyc || { watchlist: 1 })" />
            </Panel>

            <Panel :title="__('Transaction History')" icon="repeat">
              <template #actions>
                <Button size="sm" variant="outline" :label="__('Export Excel')" @click="exportRows('transactions')" />
                <Button size="sm" variant="solid" :label="__('Add Transaction')" @click="openForm('transaction')" />
              </template>
              <div class="mb-3 grid grid-cols-1 md:grid-cols-2 gap-3 max-w-xl">
                <FormInput v-model="transactionFrom" label="From Date" type="date" />
                <FormInput v-model="transactionTo" label="To Date" type="date" />
              </div>
              <SimpleTable :headers="['Date', 'Type', 'Amount', 'Running Balance', 'Status']" :rows="filteredTransactions" :columns="['transaction_date', 'transaction_type', 'amount', 'running_balance', 'status']" currency-column="amount,running_balance" :edit="(row) => openForm('transaction', row)" />
            </Panel>
          </div>

          <div v-else-if="activeTab === 'statements'" class="space-y-6">
            <Panel :title="__('Financial Statements')" icon="bar-chart-2">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Upload / Add Row')" @click="openForm('financial')" />
              </template>
              <SimpleTable :headers="['Type', 'Metric', 'Year', 'Amount', 'Auditor', 'Audit Year', 'AI Extraction']" :rows="financials" :columns="['statement_type', 'metric', 'year', 'amount', 'auditor', 'audit_year', 'extraction_status']" currency-column="amount" :edit="(row) => openForm('financial', row)" />
            </Panel>

            <Panel :title="__('Site Visit History')" icon="camera">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Site Visit')" @click="openForm('siteVisit')" />
              </template>
              <SimpleTable :headers="['Visit Date', 'RM', 'GPS', 'Photo', 'Report PDF', 'Next Visit']" :rows="siteVisits" :columns="['visit_date', 'rm', 'gps_coordinates', 'photo_attachment', 'report_pdf', 'next_visit_date']" :edit="(row) => openForm('siteVisit', row)" />
            </Panel>
          </div>

          <div v-else-if="activeTab === 'engagement'" class="space-y-6">
            <Panel :title="__('Tasks')" icon="check-circle">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Task')" @click="openForm('task')" />
              </template>
              <SimpleTable :headers="['Title', 'Assigned', 'Due', 'Priority', 'Status', 'Recurring']" :rows="tasks" :columns="['title', 'assigned_to', 'due_date', 'priority', 'status', 'recurrence_rule']" :edit="(row) => openForm('task', row)" :action="toggleTask" action-label="Done" />
            </Panel>

            <Panel :title="__('AI Insights')" icon="zap">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Insight')" @click="openForm('aiInsight')" />
              </template>
              <SimpleTable :headers="['Type', 'Title', 'Confidence', 'Status', 'Suggested Action', 'Outcome']" :rows="aiInsights" :columns="['insight_type', 'title', 'confidence_score', 'status', 'suggested_action', 'outcome']" :edit="(row) => openForm('aiInsight', row)" :action="acceptInsight" action-label="Accept" />
            </Panel>

            <Panel :title="__('Customer Tagging')" icon="tag">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Tag')" @click="openForm('tag')" />
              </template>
              <div class="mb-4 flex flex-wrap gap-2">
                <button
                  v-for="tag in tags"
                  :key="tag.name"
                  class="px-3 py-1 rounded-full text-xs font-bold text-white"
                  :style="{ backgroundColor: tag.color || '#0f766e' }"
                  @click="searchQuery = tag.tag"
                >
                  {{ tag.tag }}
                </button>
              </div>
              <SimpleTable :headers="['Tag', 'Color', 'Bulk Batch']" :rows="tags" :columns="['tag', 'color', 'bulk_batch_id']" :edit="(row) => openForm('tag', row)" />
            </Panel>

            <Panel :title="__('Customer Merge')" icon="copy">
              <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
                <div class="rounded-lg border border-slate-100 bg-slate-50 p-4">
                  <div class="text-xs font-bold uppercase text-slate-500 mb-2">{{ __('Current Customer') }}</div>
                  <div class="text-sm font-semibold text-slate-800">{{ selectedCustomer.customer_name || selectedCustomer.name }}</div>
                  <div class="text-xs text-slate-500">{{ selectedCustomer.name }}</div>
                </div>
                <div class="space-y-3">
                  <FormInput v-model="mergeForm.target" label="Target Customer ID" />
                  <FormTextarea v-model="mergeForm.field_map_json" label="Field Map JSON" />
                  <div class="flex gap-2">
                    <Button variant="outline" :label="__('Preview Merge')" @click="mergeCustomer(0)" />
                    <Button variant="solid" :label="__('Run Merge')" @click="mergeCustomer(1)" />
                  </div>
                </div>
              </div>
              <SimpleTable class="mt-4" :headers="['Source', 'Target', 'Status', 'Old IDs']" :rows="mergeAudits" :columns="['source_customer', 'target_customer', 'status', 'old_ids']" />
            </Panel>
          </div>

          <!-- Chat Tab -->
          <div v-else-if="activeTab === 'chat'" class="h-full flex flex-col" style="min-height: 500px;">
            <ChatPanel doctype="Customer" :docname="selectedCustomerName" class="flex h-full flex-col rounded-lg border border-slate-200 bg-white overflow-hidden" />
          </div>
        </div>
      </div>
    </div>

    <Dialog v-model="showAddCustomer" :options="{ title: __('Add New Customer') }">
      <template #body-content>
        <div class="space-y-4 pt-3">
          <FormInput v-model="newCustomer.customer_name" label="Customer Name" />
          <FormSelect v-model="newCustomer.customer_type" label="Segment" :options="['Company', 'Individual']" />
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2 justify-end">
          <Button variant="outline" :label="__('Cancel')" @click="showAddCustomer = false" />
          <Button variant="solid" :label="__('Save')" @click="addCustomer" />
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showProfileEdit" :options="{ title: __('Edit Basic Profile') }">
      <template #body-content>
        <div class="space-y-4 pt-3">
          <FormInput v-model="profileForm.customer_name" label="Customer Name" :error="profileErrors.customer_name" />
          <FormSelect v-model="profileForm.customer_type" label="Customer Type" :options="['Company', 'Individual']" />
          <FormInput v-model="profileForm.tax_id" label="Tax ID / NPWP" :error="profileErrors.tax_id" />
          <FormInput v-model="profileForm.website" label="Website" :error="profileErrors.website" />
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2 justify-end">
          <Button variant="outline" :label="__('Cancel')" @click="showProfileEdit = false" />
          <Button variant="solid" :label="__('Save')" @click="saveProfile" />
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showExportDialog" :options="{ title: __('Export Customer Profile'), size: 'md' }">
      <template #body-content>
        <div class="space-y-4 pt-3">
          <FormSelect v-model="exportForm.format" label="Export Format" :options="['PDF Report', 'Excel Spreadsheet']" />
          <FormSelect v-model="exportForm.scope" label="Scope / Content" :options="['Full Profile', 'Current Tab', 'Profile & KYC', 'Financing', 'Risk', 'Documents']" />
          <FormInput v-model="exportForm.watermark" label="Watermark Text" />
          <FormInput v-model="exportForm.password" label="PDF Password (Optional)" type="password" />
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2 justify-end">
          <Button variant="outline" :label="__('Cancel')" @click="showExportDialog = false" />
          <Button variant="solid" :label="exportForm.format === 'PDF Report' ? __('Download PDF') : __('Download Excel')" @click="exportProfile" />
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showDynamicForm" :options="dynamicForm.options">
      <template #body-content>
        <div :class="dynamicForm.fields.length > 5 ? 'grid grid-cols-1 md:grid-cols-2 gap-4 pt-3' : 'space-y-4 pt-3'">
          <template v-for="field in dynamicForm.fields" :key="field.fieldname">
            <input v-if="field.type === 'hidden'" v-model="dynamicForm.doc[field.fieldname]" type="hidden" />
            <FormSelect v-else-if="field.type === 'select'" v-model="dynamicForm.doc[field.fieldname]" :label="field.label" :options="field.options" :error="dynamicFormErrors[field.fieldname]" />
            <Link v-else-if="field.type === 'link'" v-model="dynamicForm.doc[field.fieldname]" :doctype="field.options" :filters="field.filters || []" :label="field.label" :placeholder="field.placeholder || __('Search {0}', [field.label])" />
            <label v-else-if="field.type === 'currency'" class="flex flex-col gap-1">
              <span class="text-xs text-ink-gray-5">{{ field.label }}</span>
              <RupiahInput v-model="dynamicForm.doc[field.fieldname]" />
              <span v-if="dynamicFormErrors[field.fieldname]" class="text-xs text-red-600">{{ dynamicFormErrors[field.fieldname] }}</span>
            </label>
            <FormTextarea v-else-if="field.type === 'textarea'" v-model="dynamicForm.doc[field.fieldname]" :label="field.label" :class="dynamicForm.fields.length > 5 ? 'md:col-span-2' : ''" :error="dynamicFormErrors[field.fieldname]" />
            <FormCheckbox v-else-if="field.type === 'checkbox'" v-model="dynamicForm.doc[field.fieldname]" :label="field.label" />
            <FormInput v-else v-model="dynamicForm.doc[field.fieldname]" :label="field.label" :type="field.type || 'text'" :error="dynamicFormErrors[field.fieldname]" />
          </template>
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2 justify-end border-t border-slate-100 pt-4 mt-2">
          <Button variant="outline" :label="__('Cancel')" @click="showDynamicForm = false" />
          <Button variant="solid" :label="dynamicForm.doc.name ? __('Update') : __('Save')" :loading="insertResource.loading" @click="submitDynamicForm" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { Button, FeatherIcon, Badge, Dialog, usePageMeta, createListResource, createResource, toast, call } from 'frappe-ui'
import { computed, h, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DOMPurify from 'dompurify'
import ChatPanel from '@/components/ChatPanel.vue'
import Link from '@/components/Controls/Link.vue'
import RupiahInput from '@/components/Controls/RupiahInput.vue'
import html2pdf from 'html2pdf.js'

const route = useRoute()
const router = useRouter()
const searchQuery = ref('')
const selectedCustomerName = ref('')
const selectedCustomer = ref(null)
const activeTab = ref('overview')
const showAddCustomer = ref(false)
const showProfileEdit = ref(false)
const showDynamicForm = ref(false)
const showExportDialog = ref(false)
const summaryText = ref('')
const summaryLength = ref('Standard')
const summarySources = ref([])
const isGeneratingSummary = ref(false)
const globalResults = ref([])
const recentSearches = ref(JSON.parse(localStorage.getItem('customer360RecentSearches') || '[]'))
const activityFilter = ref('all')
const graphFilter = ref('All')
const graphZoom = ref(1)
const timelineFilter = ref('All')
const productFilter = ref('')
const documentSearch = ref('')
const communicationFilter = ref('All')
const transactionFrom = ref('')
const transactionTo = ref('')
const editingSummary = ref(false)
const summaryTextareaRef = ref(null)
let searchTimer = null
const routeCustomer = computed(() => String(route.params.customer || ''))

const newCustomer = reactive({ customer_name: '', customer_type: 'Company' })
const profileForm = reactive({ customer_name: '', customer_type: 'Company', tax_id: '', website: '' })
const exportForm = reactive({ scope: 'Full Profile', watermark: 'BNI CRM Confidential', password: '', format: 'PDF Report' })
const mergeForm = reactive({ target: '', field_map_json: '{}' })
const dynamicForm = reactive({ key: '', title: '', doctype: '', doc: {}, fields: [], options: {} })

// Validation State for basic profile edit and dynamic forms (KYC)
const profileErrors = reactive({ customer_name: '', tax_id: '', website: '' })
const dynamicFormErrors = reactive({})

function formatNPWP(value) {
  if (!value) return ''
  const digits = value.replace(/\D/g, '')
  if (digits.length <= 15) {
    let formatted = ''
    for (let i = 0; i < digits.length; i++) {
      if (i === 2 || i === 5 || i === 8) formatted += '.'
      else if (i === 9) formatted += '-'
      else if (i === 12) formatted += '.'
      formatted += digits[i]
    }
    return formatted
  } else {
    return digits.slice(0, 16)
  }
}

function isValidWebsite(url) {
  if (!url) return true
  const pattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$/i
  return pattern.test(url)
}

function validateProfile() {
  let isValid = true
  profileErrors.customer_name = ''
  profileErrors.tax_id = ''
  profileErrors.website = ''
  
  if (!profileForm.customer_name || !profileForm.customer_name.trim()) {
    profileErrors.customer_name = __('Customer Name is required')
    isValid = false
  }
  
  if (profileForm.tax_id) {
    const digits = profileForm.tax_id.replace(/\D/g, '')
    if (digits.length !== 15 && digits.length !== 16) {
      profileErrors.tax_id = __('NPWP must be exactly 15 or 16 digits')
      isValid = false
    }
  }
  
  if (profileForm.website) {
    if (!isValidWebsite(profileForm.website)) {
      profileErrors.website = __('Please enter a valid website URL')
      isValid = false
    }
  }
  
  return isValid
}

function validateKYC() {
  let isValid = true
  // Reset all existing KYC errors
  for (const fieldname in dynamicFormErrors) {
    dynamicFormErrors[fieldname] = ''
  }
  
  const doc = dynamicForm.doc
  
  if (doc.npwp) {
    const digits = doc.npwp.replace(/\D/g, '')
    if (digits.length !== 15 && digits.length !== 16) {
      dynamicFormErrors.npwp = __('NPWP must be exactly 15 or 16 digits')
      isValid = false
    }
  }
  
  if (doc.nik) {
    const digits = doc.nik.replace(/\D/g, '')
    if (digits.length !== 16) {
      dynamicFormErrors.nik = __('NIK / KTP must be exactly 16 digits')
      isValid = false
    }
  }
  
  if (doc.employee_count !== undefined && doc.employee_count !== null && doc.employee_count !== '') {
    const count = Number(doc.employee_count)
    if (isNaN(count) || count < 0) {
      dynamicFormErrors.employee_count = __('Employee count cannot be negative')
      isValid = false
    }
  }
  
  if (doc.date_of_birth) {
    const dob = new Date(doc.date_of_birth)
    const today = new Date()
    today.setHours(23, 59, 59, 999)
    if (dob > today) {
      dynamicFormErrors.date_of_birth = __('Date of Birth cannot be in the future')
      isValid = false
    }
  }
  
  if (doc.founded_date) {
    const fd = new Date(doc.founded_date)
    const today = new Date()
    today.setHours(23, 59, 59, 999)
    if (fd > today) {
      dynamicFormErrors.founded_date = __('Company Founded Date cannot be in the future')
      isValid = false
    }
  }
  
  if (!doc.registered_address || !doc.registered_address.trim()) {
    dynamicFormErrors.registered_address = __('Registered Address is required')
    isValid = false
  }

  if (doc.watchlist && (!doc.watchlist_reason || !doc.watchlist_reason.trim())) {
    dynamicFormErrors.watchlist_reason = __('Watchlist Reason is required when watchlist is enabled')
    isValid = false
  }
  
  return isValid
}

// Watchers for Profile Edit validation
watch(() => profileForm.tax_id, (newVal) => {
  const formatted = formatNPWP(newVal)
  if (formatted !== newVal) {
    profileForm.tax_id = formatted
  }
  if (profileErrors.tax_id) validateProfile()
})

watch(() => profileForm.customer_name, () => {
  if (profileErrors.customer_name) validateProfile()
})

watch(() => profileForm.website, () => {
  if (profileErrors.website) validateProfile()
})

watch(showProfileEdit, (newVal) => {
  if (!newVal) {
    profileErrors.customer_name = ''
    profileErrors.tax_id = ''
    profileErrors.website = ''
  }
})

// Watchers for dynamic KYC form real-time formatting & validation
watch(() => dynamicForm.doc.npwp, (newVal) => {
  if (dynamicForm.key === 'kyc' && newVal) {
    const formatted = formatNPWP(newVal)
    if (formatted !== newVal) {
      dynamicForm.doc.npwp = formatted
    }
    if (dynamicFormErrors.npwp) validateKYC()
  }
})

watch(() => dynamicForm.doc.nik, (newVal) => {
  if (dynamicForm.key === 'kyc' && newVal) {
    const clean = newVal.replace(/\D/g, '').slice(0, 16)
    if (clean !== newVal) {
      dynamicForm.doc.nik = clean
    }
    if (dynamicFormErrors.nik) validateKYC()
  }
})

watch(() => dynamicForm.doc.employee_count, () => {
  if (dynamicForm.key === 'kyc' && dynamicFormErrors.employee_count) validateKYC()
})

watch(() => dynamicForm.doc.date_of_birth, () => {
  if (dynamicForm.key === 'kyc' && dynamicFormErrors.date_of_birth) validateKYC()
})

watch(() => dynamicForm.doc.founded_date, () => {
  if (dynamicForm.key === 'kyc' && dynamicFormErrors.founded_date) validateKYC()
})

watch(() => dynamicForm.doc.registered_address, () => {
  if (dynamicForm.key === 'kyc' && dynamicFormErrors.registered_address) validateKYC()
})

watch(() => dynamicForm.doc.watchlist, () => {
  if (dynamicForm.key === 'kyc' && dynamicFormErrors.watchlist_reason) validateKYC()
})

watch(() => dynamicForm.doc.watchlist_reason, () => {
  if (dynamicForm.key === 'kyc' && dynamicFormErrors.watchlist_reason) validateKYC()
})

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'profile', label: 'Personal / KYC' },
  { key: 'ownership', label: 'Ownership' },
  { key: 'financing', label: 'Financing' },
  { key: 'documents', label: 'Documents & Comms' },
  { key: 'risk', label: 'Risk' },
  { key: 'statements', label: 'Statements & Visit' },
  { key: 'engagement', label: 'Engagement' },
  { key: 'chat', label: 'Chat' },
]

const customersResource = createListResource({
  type: 'list',
  doctype: 'Customer',
  fields: ['name', 'customer_name', 'customer_type', 'customer_group', 'territory', 'website', 'tax_id', 'modified'],
  limit: 100,
  auto: true,
})

const customer360 = createResource({
  url: 'crm.api.credit.get_customer_360',
  makeParams() {
    return { customer: selectedCustomerName.value }
  },
  onSuccess(data) {
    summaryText.value = data?.summary?.summary_text || ''
    if (data?.customer) {
      selectedCustomer.value = data.customer
      Object.assign(profileForm, {
        customer_name: data.customer.customer_name || data.customer.name,
        customer_type: data.customer.customer_type || 'Company',
        tax_id: data.customer.tax_id || '',
        website: data.customer.website || '',
      })
    }
  },
})

const insertResource = createResource({
  url: 'crm.api.credit.create_or_update_customer360_record',
  onSuccess() {
    toast.success(__('Record saved'))
    showDynamicForm.value = false
    reloadCustomer360()
  },
  onError(error) {
    toast.error(error?.messages?.[0] || __('Could not save record'))
  },
})

const localCustomers = computed(() => {
  const rows = customersResource.data || []
  const query = searchQuery.value.toLowerCase()
  if (!query) return rows
  return rows.filter((customer) =>
    [customer.customer_name, customer.name, customer.customer_type, customer.territory, customer.tax_id]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query)),
  )
})
const directoryCustomers = computed(() => (searchQuery.value.length > 1 && globalResults.value.length ? globalResults.value : localCustomers.value))
const data = computed(() => customer360.data || {})
const summary = computed(() => data.value.summary || {})
const kyc = computed(() => data.value.kyc || null)
const facilities = computed(() => data.value.facilities || [])
const activeFacilities = computed(() => facilities.value.filter((row) => row.status === 'Active'))
const filteredFacilities = computed(() => {
  const query = productFilter.value.toLowerCase()
  if (!query) return facilities.value
  return facilities.value.filter((row) => String(row.product_type || row.facility_type || '').toLowerCase().includes(query))
})
const collaterals = computed(() => data.value.collaterals || [])
const bureauReports = computed(() => data.value.bureau_reports || [])
const latestBureau = computed(() => bureauReports.value[0] || null)
const relationships = computed(() => data.value.relationships || [])
const shareholders = computed(() => data.value.shareholders || [])
const directors = computed(() => data.value.directors || [])
const relatedEntities = computed(() => data.value.related_entities || [])
const financials = computed(() => data.value.financials || [])
const siteVisits = computed(() => data.value.site_visits || [])
const bankAccounts = computed(() => data.value.bank_accounts || [])
const documents = computed(() => data.value.documents || [])
const communications = computed(() => data.value.communications || [])
const transactions = computed(() => data.value.transactions || [])
const riskProfiles = computed(() => data.value.risk_profiles || [])
const latestRisk = computed(() => data.value.latest_risk || null)
const aiInsights = computed(() => data.value.ai_insights || [])
const tags = computed(() => data.value.tags || [])
const mergeAudits = computed(() => data.value.merge_audits || [])
const tasks = computed(() => data.value.tasks || [])
const notes = computed(() => data.value.notes || [])
const events = computed(() => data.value.events || [])
const timeline = computed(() => data.value.timeline || [])
const timelineKinds = computed(() => ['All', ...new Set(timeline.value.map((row) => row.kind).filter(Boolean))])
const filteredTimeline = computed(() => timelineFilter.value === 'All' ? timeline.value : timeline.value.filter((row) => row.kind === timelineFilter.value))
const filteredGraphRelationships = computed(() => graphFilter.value === 'All' ? relationships.value : relationships.value.filter((row) => row.relationship_type === graphFilter.value))
const filteredDocuments = computed(() => {
  const query = documentSearch.value.toLowerCase()
  if (!query) return documents.value
  return documents.value.filter((row) => [row.title, row.document_type, row.folder, row.tags].filter(Boolean).some((value) => String(value).toLowerCase().includes(query)))
})
const filteredCommunications = computed(() => communicationFilter.value === 'All' ? communications.value : communications.value.filter((row) => row.channel === communicationFilter.value))
const filteredTransactions = computed(() => transactions.value.filter((row) => {
  if (transactionFrom.value && row.transaction_date < transactionFrom.value) return false
  if (transactionTo.value && row.transaction_date > transactionTo.value) return false
  return true
}))

const formConfigs = computed(() => ({
  creditApplication: {
    title: __('New Credit Application'),
    doctype: 'CRM Credit Application',
    defaults: { borrower: selectedCustomerName.value, borrower_type: selectedCustomer.value?.customer_type || 'Company', status: 'Draft' },
    fields: [
      field('borrower', 'Borrower', 'hidden'),
      field('borrower_type', 'Borrower Type', 'select', ['Individual', 'Company']),
      field('status', 'Status', 'select', ['Draft', 'Application Received', 'Document Review', 'Credit Analysis', 'Collateral Appraisal', 'Committee Approval', 'Legal Documentation', 'Disbursement', 'Active', 'Rejected', 'Closed']),
      field('facility_type', 'Facility Type'),
      field('requested_amount', 'Requested Amount', 'currency'),
      field('employer_name', 'Employer / Affiliation'),
      field('public_company_ticker', 'PT Tbk Ticker'),
      field('purpose', 'Purpose', 'textarea'),
    ],
  },
  kyc: {
    title: __('KYC Review'),
    doctype: 'CRM KYC Review',
    defaults: { customer: selectedCustomerName.value, status: 'Pending', ekyc_result: 'Manual', renewal_workflow_status: 'Not Started' },
    fields: [
      field('status', 'Status', 'select', ['Pending', 'Verified', 'Expired', 'Rejected']),
      field('review_date', 'Last KYC Date', 'date'),
      field('next_review_date', 'Next Review Date', 'date'),
      field('renewal_workflow_status', 'Renewal Workflow', 'select', ['Not Started', 'Triggered', 'In Progress', 'Completed']),
      field('npwp', 'NPWP'),
      field('nik', 'NIK / KTP'),
      field('date_of_birth', 'Date of Birth', 'date'),
      field('founded_date', 'Company Founded Date', 'date'),
      field('employee_count', 'Employees', 'number'),
      field('registered_address', 'Registered Address', 'textarea'),
      field('ekyc_result', 'e-KYC Result', 'select', ['Manual', 'Pending Vendor', 'Verified', 'Failed', 'Unavailable']),
      field('watchlist', 'Watchlist', 'checkbox'),
      field('watchlist_reason', 'Watchlist Reason', 'textarea'),
      field('watchlist_remove_approval', 'Removal Approval', 'select', ['Not Required', 'Pending Approval', 'Approved', 'Rejected']),
    ],
  },
  relationship: {
    title: __('Relationship'),
    doctype: 'CRM Relationship',
    defaults: { customer: selectedCustomerName.value, aml_pep_status: 'Manual', background_check_status: 'Manual' },
    fields: [
      field('related_party', 'Related Party'),
      field('related_customer', 'Linked Customer Profile', 'link', 'Customer'),
      field('relationship_type', 'Relationship Type', 'select', ['Shareholder', 'UBO', 'Director', 'Commissioner', 'Group Company', 'RM', 'Other']),
      field('ownership_percent', 'Ownership %', 'number'),
      field('position', 'Position / Role'),
      field('director_id', 'Director ID / KTP'),
      field('linkedin_url', 'LinkedIn URL'),
      field('tenure_start', 'Tenure Start', 'date'),
      field('aml_pep_status', 'AML / PEP Status', 'select', ['Manual', 'Pending Vendor', 'Clear', 'Potential Match', 'Unavailable']),
      field('background_check_status', 'Background Check', 'select', ['Manual', 'Pending Vendor', 'Clear', 'Flagged', 'Unavailable']),
      field('exposure', 'Exposure', 'currency'),
      field('is_ubo', 'Is UBO', 'checkbox'),
    ],
  },
  facility: {
    title: __('Credit Facility'),
    doctype: 'CRM Credit Facility',
    defaults: { customer: selectedCustomerName.value, status: 'Active' },
    fields: [
      field('facility_type', 'Facility Type'),
      field('product_type', 'Product Type'),
      field('status', 'Status', 'select', ['Active', 'Closed', 'Restructured', 'Watchlist']),
      field('due_date', 'Due Date', 'date'),
      field('outstanding', 'Outstanding', 'currency'),
      field('limit_amount', 'Limit Amount', 'currency'),
      field('health', 'Health / KOL'),
      field('repayment_behavior', 'Repayment Behavior', 'textarea'),
      field('default_flag', 'Default History Flag', 'checkbox'),
      field('action_status', 'Quick Action Status', 'select', ['', 'Top-up Requested', 'Restructure Requested', 'Under Review', 'Completed']),
    ],
  },
  bankAccount: {
    title: __('Bank Account'),
    doctype: 'CRM Bank Account',
    defaults: { customer: selectedCustomerName.value, verification_status: 'Pending', otp_status: 'Pending Vendor' },
    fields: [field('bank', 'Bank'), field('account_number', 'Account Number'), field('account_name', 'Account Name'), field('is_primary', 'Primary', 'checkbox'), field('verification_status', 'Verification', 'select', ['Verified', 'Pending', 'Failed', 'Unavailable']), field('otp_status', 'OTP Status', 'select', ['Pending Vendor', 'Sent', 'Verified', 'Failed', 'Unavailable'])],
  },
  collateral: {
    title: __('Collateral'),
    doctype: 'CRM Collateral',
    defaults: { customer: selectedCustomerName.value, status: 'Active', reappraisal_status: 'Not Required' },
    fields: [field('asset', 'Asset'), field('collateral_type', 'Type'), field('collateral_value', 'Value', 'currency'), field('linked_facility', 'Linked Facility', 'link', 'CRM Credit Facility', { customer: selectedCustomerName.value }), field('ltv_percent', 'LTV %', 'number'), field('expiry_date', 'Expiry Date', 'date'), field('insurance_expiry', 'Insurance Expiry', 'date'), field('document_link', 'Document Link'), field('reappraisal_status', 'Re-appraisal', 'select', ['Not Required', 'Due', 'In Progress', 'Completed']), field('status', 'Status', 'select', ['Active', 'Expired', 'Released', 'Under Review'])],
  },
  bureau: {
    title: __('Bureau Report'),
    doctype: 'CRM Bureau Report',
    defaults: { customer: selectedCustomerName.value, source: 'SLIK/OJK Manual Upload' },
    fields: [field('source', 'Source', 'select', ['SLIK/OJK Manual Upload', 'PEFINDO', 'Internal', 'Other']), field('report_date', 'Report Date', 'date'), field('kol_status', 'KOL Status'), field('score', 'Score', 'number'), field('external_exposure', 'External Exposure', 'currency'), field('notes', 'Notes', 'textarea')],
  },
  document: {
    title: __('Customer Document'),
    doctype: 'CRM Customer Document',
    defaults: { customer: selectedCustomerName.value, document_type: 'KYC', expiry_status: 'Valid', preview_status: 'Needs Upload' },
    fields: [field('document_type', 'Document Type', 'select', ['KYC', 'Financial', 'Collateral', 'Legal', 'Visit', 'Other']), field('title', 'Title'), field('folder', 'Folder'), field('version', 'Version'), field('expiry_date', 'Expiry Date', 'date'), field('expiry_status', 'Expiry Status', 'select', ['Valid', 'Expiring Soon', 'Expired', 'Not Applicable']), field('tags', 'Tags'), field('preview_status', 'Preview Status', 'select', ['Preview Available', 'Needs Upload', 'Unavailable']), field('notes', 'Notes', 'textarea')],
  },
  communication: {
    title: __('Communication'),
    doctype: 'CRM Customer Communication',
    defaults: { customer: selectedCustomerName.value, channel: 'Email', direction: 'Outbound', compose_status: 'Manual', status: 'Open' },
    fields: [field('channel', 'Channel', 'select', ['Email', 'WA', 'SMS', 'Call']), field('direction', 'Direction', 'select', ['Inbound', 'Outbound']), field('subject', 'Subject'), field('communication_time', 'Time', 'datetime-local'), field('conversation_link', 'Conversation Link'), field('compose_status', 'Compose Status', 'select', ['Manual', 'Pending Vendor', 'Sent', 'Failed', 'Unavailable']), field('status', 'Status', 'select', ['Open', 'Closed', 'Failed']), field('message', 'Message', 'textarea')],
  },
  financial: {
    title: __('Financial Statement'),
    doctype: 'CRM Financial Statement',
    defaults: { customer: selectedCustomerName.value, statement_type: 'P&L', extraction_status: 'Manual' },
    fields: [field('statement_type', 'Statement Type', 'select', ['P&L', 'Balance Sheet', 'Cash Flow', 'Other']), field('metric', 'Metric'), field('year', 'Year', 'number'), field('amount', 'Amount', 'currency'), field('auditor', 'Auditor'), field('audit_year', 'Audit Year', 'number'), field('source', 'Source'), field('extraction_status', 'AI Extraction Status', 'select', ['Manual', 'Pending Vendor', 'Extracted', 'Failed', 'Unavailable']), field('audited', 'Audited', 'checkbox'), field('forecast', 'Forecast', 'checkbox'), field('notes', 'Notes', 'textarea')],
  },
  siteVisit: {
    title: __('Site Visit'),
    doctype: 'CRM Site Visit',
    defaults: { customer: selectedCustomerName.value },
    fields: [field('visit_date', 'Visit Date', 'datetime-local'), field('next_visit_date', 'Next Visit Reminder', 'datetime-local'), field('gps_coordinates', 'GPS Coordinates'), field('photo_attachment', 'Photo Attachment Path'), field('report_pdf', 'Visit Report PDF Path'), field('notes', 'Notes', 'textarea')],
  },
  risk: {
    title: __('Risk Profile'),
    doctype: 'CRM Risk Profile',
    defaults: { customer: selectedCustomerName.value, watchlist_status: 'No' },
    fields: [field('risk_grade', 'Risk Grade'), field('internal_score', 'Internal Score', 'number'), field('grade_date', 'Grade Date', 'date'), field('watchlist_status', 'Watchlist Status', 'select', ['No', 'Yes', 'Pending Removal']), field('npl_flag', 'NPL Flag', 'checkbox'), field('risk_factors', 'Risk Factors', 'textarea'), field('early_warning_triggers', 'Early Warning Triggers', 'textarea'), field('change_reason', 'Change Reason', 'textarea')],
  },
  transaction: {
    title: __('Transaction'),
    doctype: 'CRM Transaction History',
    defaults: { customer: selectedCustomerName.value, transaction_type: 'Repayment', status: 'Posted' },
    fields: [field('facility', 'Facility', 'link', 'CRM Credit Facility', { customer: selectedCustomerName.value }), field('transaction_date', 'Transaction Date', 'date'), field('transaction_type', 'Type', 'select', ['Repayment', 'Missed Payment', 'Disbursement', 'Fee', 'Adjustment']), field('amount', 'Amount', 'currency'), field('running_balance', 'Running Balance', 'currency'), field('status', 'Status', 'select', ['Posted', 'Pending', 'Failed']), field('notes', 'Notes', 'textarea')],
  },
  task: {
    title: __('Customer Task'),
    doctype: 'CRM Task',
    defaults: { reference_doctype: 'Customer', reference_docname: selectedCustomerName.value, status: 'Todo', priority: 'Medium' },
    fields: [field('title', 'Title'), field('assigned_to', 'Assigned To', 'link', 'User'), field('priority', 'Priority', 'select', ['Low', 'Medium', 'High']), field('status', 'Status', 'select', ['Backlog', 'Todo', 'In Progress', 'Done', 'Canceled']), field('due_date', 'Due Date', 'datetime-local'), field('recurring', 'Recurring', 'checkbox'), field('recurrence_rule', 'Recurrence Rule'), field('description', 'Description', 'textarea')],
  },
  note: { title: __('Customer Note'), doctype: 'FCRM Note', defaults: { reference_doctype: 'Customer', reference_docname: selectedCustomerName.value }, fields: [field('title', 'Title'), field('content', 'Content', 'textarea')] },
  event: { title: __('Customer Event'), doctype: 'Event', defaults: { reference_doctype: 'Customer', reference_docname: selectedCustomerName.value, status: 'Open', event_type: 'Private' }, fields: [field('subject', 'Subject'), field('starts_on', 'Starts On', 'datetime-local'), field('ends_on', 'Ends On', 'datetime-local'), field('description', 'Description', 'textarea')] },
  aiInsight: {
    title: __('AI Insight'),
    doctype: 'CRM AI Insight',
    defaults: { customer: selectedCustomerName.value, insight_type: 'Cross-sell', status: 'Open' },
    fields: [field('insight_type', 'Insight Type', 'select', ['Cross-sell', 'Retention Risk', 'Upsell', 'Risk']), field('title', 'Title'), field('confidence_score', 'Confidence %', 'number'), field('status', 'Status', 'select', ['Open', 'Accepted', 'Dismissed', 'Completed']), field('suggested_action', 'Suggested Action', 'textarea'), field('outcome', 'Outcome', 'textarea'), field('notes', 'Notes', 'textarea')],
  },
  tag: { title: __('Customer Tag'), doctype: 'CRM Customer Tag', defaults: { customer: selectedCustomerName.value, color: '#0f766e' }, fields: [field('tag', 'Tag'), field('color', 'Color', 'color'), field('bulk_batch_id', 'Bulk Batch ID'), field('notes', 'Notes', 'textarea')] },
}))

function field(fieldname, label, type = 'text', options = [], filters = []) {
  return { fieldname, label, type, options, filters }
}

function selectCustomer(cust) {
  selectedCustomer.value = cust
  selectedCustomerName.value = cust.name
  pushRecentSearch(searchQuery.value || cust.customer_name || cust.name)
  Object.assign(profileForm, {
    customer_name: cust.customer_name || cust.name,
    customer_type: cust.customer_type || 'Company',
    tax_id: cust.tax_id || '',
    website: cust.website || '',
  })
  reloadCustomer360()
}

function loadRouteCustomer() {
  if (!routeCustomer.value) return
  const row = (customersResource.data || []).find((customer) => customer.name === routeCustomer.value)
  selectCustomer(row || { name: routeCustomer.value, customer_name: routeCustomer.value, customer_type: 'Customer' })
}

function goToCustomerList() {
  router.push({ name: 'Customer 360' })
}

function reloadCustomer360() {
  if (selectedCustomerName.value) customer360.fetch()
}

function openForm(key, existing = {}) {
  const config = formConfigs.value[key]
  if (!config) return
  
  // Clear any existing errors when opening form
  for (const k in dynamicFormErrors) {
    dynamicFormErrors[k] = ''
  }
  
  dynamicForm.key = key
  dynamicForm.title = config.title
  dynamicForm.doctype = config.doctype
  dynamicForm.fields = config.fields
  dynamicForm.doc = { ...config.defaults, ...existing }
  dynamicForm.options = {
    title: config.title,
    size: config.fields.length > 5 ? '3xl' : 'md',
  }
  showDynamicForm.value = true
}

function submitDynamicForm() {
  if (dynamicForm.key === 'kyc') {
    if (!validateKYC()) {
      toast.error(__('Please correct the errors in the KYC form'))
      return
    }
  }
  insertResource.submit({ doctype: dynamicForm.doctype, doc: normalizeDoc(dynamicForm.doc) })
}

async function toggleTask(task) {
  const nextStatus = task.status === 'Done' ? 'Todo' : 'Done'
  await call('frappe.client.set_value', { doctype: 'CRM Task', name: task.name, fieldname: 'status', value: nextStatus })
  toast.success(__('Task updated'))
  reloadCustomer360()
}

async function saveProfile() {
  if (!validateProfile()) {
    toast.error(__('Please correct the errors in the profile form'))
    return
  }
  await call('crm.api.credit.update_customer_profile', {
    customer: selectedCustomerName.value,
    payload: normalizeDoc(profileForm),
  })
  showProfileEdit.value = false
  toast.success(__('Customer profile updated'))
  customersResource.reload()
  reloadCustomer360()
}

async function saveCustomerSummary() {
  await call('crm.api.credit.save_customer_summary', { customer: selectedCustomerName.value, summary: summaryText.value })
  toast.success(__('Summary saved'))
  reloadCustomer360()
}

async function generateCustomerSummary() {
  if (!selectedCustomerName.value) return
  isGeneratingSummary.value = true
  try {
    const response = await call('crm.api.ai_agent_center.generate_summary', {
      scope: 'Customer',
      docname: selectedCustomerName.value,
      length: summaryLength.value,
    })
    summaryText.value = response.response || ''
    summarySources.value = response.sources || []
    toast.success(__('RAG summary generated'))
    reloadCustomer360()
  } catch (error) {
    toast.error(error?.messages?.[0] || __('Could not generate RAG summary'))
  } finally {
    isGeneratingSummary.value = false
  }
}

async function addCustomer() {
  if (!newCustomer.customer_name.trim()) {
    toast.error(__('Customer name is required'))
    return
  }
  try {
    await call('crm.api.credit.create_customer_360_customer', { customer_name: newCustomer.customer_name, customer_type: newCustomer.customer_type })
    toast.success(__('Customer added successfully'))
    showAddCustomer.value = false
    newCustomer.customer_name = ''
    customersResource.reload()
  } catch {
    toast.error(__('Failed to create customer record'))
  }
}

async function runAmlCheck(row) {
  await call('frappe.client.set_value', { doctype: 'CRM Relationship', name: row.name, fieldname: 'aml_pep_status', value: 'Pending Vendor' })
  toast.success(__('AML/PEP check marked as pending vendor'))
  reloadCustomer360()
}

async function requestRestructure(row) {
  await call('frappe.client.set_value', { doctype: 'CRM Credit Facility', name: row.name, fieldname: 'action_status', value: 'Restructure Requested' })
  toast.success(__('Restructure request captured'))
  reloadCustomer360()
}

async function acceptInsight(row) {
  await call('frappe.client.set_value', { doctype: 'CRM AI Insight', name: row.name, fieldname: 'status', value: 'Accepted' })
  toast.success(__('Insight accepted'))
  reloadCustomer360()
}

function buildProfileHTML(cust, scope, watermark) {
  const fmt = (v) => formatCurrency(v)
  const fmtDate = (d) => d ? new Date(d).toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' }) : '-'
  
  const incAll = scope === 'Full Profile'
  const incKYC = incAll || scope === 'Profile & KYC'
  const incFinancing = incAll || scope === 'Financing'
  const incRisk = incAll || scope === 'Risk'
  const incDocs = incAll || scope === 'Documents'
  const incCurrent = scope === 'Current Tab'
  
  let html = `
    <div style="font-family: 'Inter', sans-serif; color: #1e293b; line-height: 1.5; padding: 20px; max-width: 800px; margin: 0 auto; background: #fff; position: relative;">
  `
  
  html += `
    <!-- COVER PAGE -->
    <div class="page-section" style="page-break-after: always; height: 950px; display: flex; flex-direction: column; justify-content: space-between; border: 2px solid #e2e8f0; border-radius: 12px; padding: 40px; box-sizing: border-box; position: relative; background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);">
      ${watermark ? `<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 5rem; color: rgba(226, 232, 240, 0.25); font-weight: 800; pointer-events: none; z-index: 0; white-space: nowrap; text-transform: uppercase;">${watermark}</div>` : ''}
      
      <div style="z-index: 1;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #005e6a; padding-bottom: 15px;">
          <div>
            <span style="font-size: 24px; font-weight: 900; color: #005e6a;">BNI</span>
            <span style="font-size: 14px; font-weight: 600; color: #f79009; margin-left: 5px;">CRM PORTAL</span>
          </div>
          <span style="font-size: 10px; font-weight: 700; color: #64748b; background: #e2e8f0; padding: 4px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 1px;">CONFIDENTIAL</span>
        </div>
        
        <div style="margin-top: 180px;">
          <h1 style="font-size: 38px; font-weight: 800; color: #0f172a; line-height: 1.2; margin: 0 0 10px 0;">CUSTOMER 360 PROFILE REPORT</h1>
          <p style="font-size: 18px; font-weight: 500; color: #005e6a; margin: 0 0 40px 0; letter-spacing: 0.5px;">Comprehensive Portfolio & Risk Exposure Review</p>
          
          <div style="width: 80px; height: 6px; background-color: #f79009; border-radius: 3px; margin-bottom: 50px;"></div>
          
          <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
              <td style="padding: 10px 0; color: #64748b; font-weight: 600; width: 160px;">Customer Name</td>
              <td style="padding: 10px 0; color: #0f172a; font-weight: 700; font-size: 16px;">${cust.customer_name || cust.name}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Customer Type</td>
              <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">${cust.customer_type || 'Company'}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Tax ID / NPWP</td>
              <td style="padding: 10px 0; color: #0f172a; font-family: monospace; font-weight: 600;">${cust.tax_id || kyc.value?.npwp || '-'}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; color: #64748b; font-weight: 600;">Risk Grade / Score</td>
              <td style="padding: 10px 0; color: #0f172a; font-weight: 600;">
                <span style="background: #fff8e6; color: #b78103; padding: 3px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #ffe8cc;">
                  ${summary.value?.risk_grade || 'Unrated'} (${summary.value?.score || 0} pts)
                </span>
              </td>
            </tr>
          </table>
        </div>
      </div>
      
      <div style="z-index: 1; border-top: 1px solid #e2e8f0; padding-top: 20px; display: flex; justify-content: space-between; align-items: flex-end;">
        <div>
          <p style="font-size: 11px; color: #94a3b8; margin: 0 0 4px 0;">REPORT GENERATED BY</p>
          <p style="font-size: 13px; font-weight: 700; color: #334155; margin: 0;">BNI RM Workspace</p>
        </div>
        <div>
          <p style="font-size: 11px; color: #94a3b8; margin: 0 0 4px 0; text-align: right;">DATE OF GENERATION</p>
          <p style="font-size: 13px; font-weight: 700; color: #334155; margin: 0; text-align: right;">${fmtDate(new Date())}</p>
        </div>
      </div>
    </div>
  `
  
  if (incKYC || (incCurrent && activeTab.value === 'overview') || (incCurrent && activeTab.value === 'profile')) {
    html += `
      <div class="page-section" style="page-break-after: always; padding-top: 20px; position: relative; min-height: 900px;">
        ${watermark ? `<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 5rem; color: rgba(226, 232, 240, 0.2); font-weight: 800; pointer-events: none; z-index: 0; white-space: nowrap; text-transform: uppercase;">${watermark}</div>` : ''}
        
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 25px;">
          <span style="font-size: 12px; font-weight: 700; color: #005e6a; letter-spacing: 0.5px;">SECTION 1: PROFILE & KYC REVIEW</span>
          <span style="font-size: 11px; color: #94a3b8;">${cust.customer_name || cust.name}</span>
        </div>
        
        <div style="background: #f0fdfa; border-left: 4px solid #0d9488; border-radius: 8px; padding: 20px; margin-bottom: 30px; box-shadow: inset 0 0 8px rgba(13,148,136,0.02);">
          <h3 style="font-size: 14px; font-weight: 800; color: #0f766e; margin: 0 0 10px 0; letter-spacing: 0.5px; text-transform: uppercase;">AI Customer Executive Summary</h3>
          <div style="font-size: 13px; color: #334155; line-height: 1.6; font-style: italic;">
            ${summaryText.value ? summaryText.value.replace(/\n/g, '<br>') : 'No executive summary generated.'}
          </div>
        </div>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Know Your Customer (KYC) Registry</h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 40px;">
          <div style="background: #f8fafc; border: 1px solid #edf2f7; border-radius: 6px; padding: 12px;">
            <div style="font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;">KYC Status</div>
            <div style="font-size: 14px; font-weight: 700; color: ${kyc.value?.status === 'Verified' ? '#16a34a' : '#ea580c'}">${kyc.value?.status || 'Pending'}</div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #edf2f7; border-radius: 6px; padding: 12px;">
            <div style="font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;">e-KYC Result</div>
            <div style="font-size: 14px; font-weight: 700; color: #005e6a;">${kyc.value?.ekyc_result || 'Manual'}</div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #edf2f7; border-radius: 6px; padding: 12px;">
            <div style="font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;">Last Review Date</div>
            <div style="font-size: 13px; font-weight: 600; color: #334155;">${fmtDate(kyc.value?.review_date)}</div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #edf2f7; border-radius: 6px; padding: 12px;">
            <div style="font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;">Next Scheduled Review</div>
            <div style="font-size: 13px; font-weight: 600; color: #334155;">${fmtDate(kyc.value?.next_review_date)}</div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #edf2f7; border-radius: 6px; padding: 12px; grid-column: span 2;">
            <div style="font-size: 10px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px;">Registered Address</div>
            <div style="font-size: 13px; font-weight: 500; color: #334155; line-height: 1.4;">${kyc.value?.registered_address || '-'}</div>
          </div>
        </div>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Corporate Demographics</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 20px;">
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px; color: #64748b; font-weight: 600;">Customer Group</td>
            <td style="padding: 10px; color: #1e293b; font-weight: 600; text-align: right;">${cust.customer_group || '-'}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px; color: #64748b; font-weight: 600;">Territory / Region</td>
            <td style="padding: 10px; color: #1e293b; font-weight: 600; text-align: right;">${cust.territory || '-'}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f1f5f9;">
            <td style="padding: 10px; color: #64748b; font-weight: 600;">Corporate Website</td>
            <td style="padding: 10px; color: #1e293b; font-weight: 600; text-align: right;">${cust.website || '-'}</td>
          </tr>
        </table>
      </div>
    `
  }
  
  if (incAll || (incCurrent && activeTab.value === 'ownership')) {
    html += `
      <div class="page-section" style="page-break-after: always; padding-top: 20px; position: relative; min-height: 900px;">
        ${watermark ? `<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 5rem; color: rgba(226, 232, 240, 0.2); font-weight: 800; pointer-events: none; z-index: 0; white-space: nowrap; text-transform: uppercase;">${watermark}</div>` : ''}
        
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 25px;">
          <span style="font-size: 12px; font-weight: 700; color: #005e6a; letter-spacing: 0.5px;">SECTION 2: CORPORATE STRUCTURE & OWNERSHIP</span>
          <span style="font-size: 11px; color: #94a3b8;">${cust.customer_name || cust.name}</span>
        </div>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Corporate Shareholders (Cap Table)</h3>
        <div style="margin-bottom: 10px; font-size: 12px; font-weight: 700; color: #005e6a;">
          Ownership Captured: ${summary.value?.shareholder_total || 0}%
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Shareholder Name</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">Ownership %</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: center;">Is UBO</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Linked Customer Profile</th>
            </tr>
          </thead>
          <tbody>
            ${shareholders.value.map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${row.related_party || '-'}</td>
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 700; text-align: right;">${row.ownership_percent || 0}%</td>
                <td style="padding: 10px 12px; text-align: center;">
                  <span style="background: ${row.is_ubo ? '#f0fdf4' : '#f1f5f9'}; color: ${row.is_ubo ? '#16a34a' : '#64748b'}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; border: 1px solid ${row.is_ubo ? '#bbf7d0' : '#e2e8f0'}">
                    ${row.is_ubo ? 'YES' : 'NO'}
                  </span>
                </td>
                <td style="padding: 10px 12px; color: #64748b;">${row.related_customer || '-'}</td>
              </tr>
            `).join('')}
            ${!shareholders.value.length ? `<tr><td colspan="4" style="padding: 20px; text-align: center; color: #94a3b8;">No shareholder records found</td></tr>` : ''}
          </tbody>
        </table>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Board of Directors & Commissioners</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Name</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Role / Position</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">ID Card / NIK</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">AML/PEP Check</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Background Check</th>
            </tr>
          </thead>
          <tbody>
            ${directors.value.map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${row.related_party || '-'}</td>
                <td style="padding: 10px 12px; color: #334155;">${row.position || '-'}</td>
                <td style="padding: 10px 12px; color: #64748b; font-family: monospace;">${row.director_id || '-'}</td>
                <td style="padding: 10px 12px;">
                  <span style="background: ${row.aml_pep_status === 'Clear' ? '#f0fdf4' : row.aml_pep_status === 'Pending Vendor' ? '#fffbeb' : '#fef2f2'}; color: ${row.aml_pep_status === 'Clear' ? '#16a34a' : row.aml_pep_status === 'Pending Vendor' ? '#b45309' : '#dc2626'}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">
                    ${row.aml_pep_status || 'Manual'}
                  </span>
                </td>
                <td style="padding: 10px 12px;">
                  <span style="background: ${row.background_check_status === 'Clear' ? '#f0fdf4' : '#f1f5f9'}; color: ${row.background_check_status === 'Clear' ? '#16a34a' : '#64748b'}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">
                    ${row.background_check_status || 'Manual'}
                  </span>
                </td>
              </tr>
            `).join('')}
            ${!directors.value.length ? `<tr><td colspan="5" style="padding: 20px; text-align: center; color: #94a3b8;">No director records found</td></tr>` : ''}
          </tbody>
        </table>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Affiliated & Group Companies</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Entity Name</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Relationship Type</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">Group Exposure</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Linked Customer</th>
            </tr>
          </thead>
          <tbody>
            ${relatedEntities.value.map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${row.related_party || '-'}</td>
                <td style="padding: 10px 12px; color: #334155;">${row.relationship_type || '-'}</td>
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 700; text-align: right;">${fmt(row.exposure)}</td>
                <td style="padding: 10px 12px; color: #64748b;">${row.related_customer || '-'}</td>
              </tr>
            `).join('')}
            ${!relatedEntities.value.length ? `<tr><td colspan="4" style="padding: 20px; text-align: center; color: #94a3b8;">No affiliated entities found</td></tr>` : ''}
          </tbody>
        </table>
      </div>
    `
  }
  
  if (incFinancing || (incCurrent && activeTab.value === 'financing')) {
    const totalLimit = facilities.value.reduce((s, row) => s + flt(row.limit_amount), 0)
    const totalOS = facilities.value.reduce((s, row) => s + flt(row.outstanding), 0)
    html += `
      <div class="page-section" style="page-break-after: always; padding-top: 20px; position: relative; min-height: 900px;">
        ${watermark ? `<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 5rem; color: rgba(226, 232, 240, 0.2); font-weight: 800; pointer-events: none; z-index: 0; white-space: nowrap; text-transform: uppercase;">${watermark}</div>` : ''}
        
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 25px;">
          <span style="font-size: 12px; font-weight: 700; color: #005e6a; letter-spacing: 0.5px;">SECTION 3: CREDIT FACILITIES & EXPOSURE</span>
          <span style="font-size: 11px; color: #94a3b8;">${cust.customer_name || cust.name}</span>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px;">
          <div style="background: linear-gradient(135deg, #005e6a 0%, #008c95 100%); border-radius: 8px; padding: 15px; color: #fff; box-shadow: 0 4px 6px rgba(0,94,106,0.15);">
            <div style="font-size: 9px; font-weight: 800; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Total Approved Limit</div>
            <div style="font-size: 16px; font-weight: 800; white-space: nowrap;">${fmt(totalLimit)}</div>
          </div>
          <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; color: #1e293b; box-shadow: 0 4px 6px rgba(0,0,0,0.01);">
            <div style="font-size: 9px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Total Outstanding Exposure</div>
            <div style="font-size: 16px; font-weight: 800; color: #005e6a; white-space: nowrap;">${fmt(totalOS)}</div>
          </div>
          <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; color: #1e293b; box-shadow: 0 4px 6px rgba(0,0,0,0.01);">
            <div style="font-size: 9px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Active Facilities</div>
            <div style="font-size: 16px; font-weight: 800; color: #f79009;">${facilities.value.filter(r=>r.status==='Active').length} Facility(s)</div>
          </div>
        </div>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Active Credit Facilities</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Facility Type</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">Outstanding</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">Limit Amount</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Due Date</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: center;">KOL Health</th>
            </tr>
          </thead>
          <tbody>
            ${facilities.value.map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${row.facility_type || row.product_type || '-'}</td>
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 700; text-align: right;">${fmt(row.outstanding)}</td>
                <td style="padding: 10px 12px; color: #475569; text-align: right;">${fmt(row.limit_amount)}</td>
                <td style="padding: 10px 12px; color: #64748b;">${fmtDate(row.due_date)}</td>
                <td style="padding: 10px 12px; text-align: center;">
                  <span style="background: ${row.health === 'KOL-1' || row.health === 'KOL 1' ? '#f0fdf4' : '#fff1f2'}; color: ${row.health === 'KOL-1' || row.health === 'KOL 1' ? '#16a34a' : '#e11d48'}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">
                    ${row.health || 'KOL-1'}
                  </span>
                </td>
              </tr>
            `).join('')}
            ${!facilities.value.length ? `<tr><td colspan="5" style="padding: 20px; text-align: center; color: #94a3b8;">No facilities records found</td></tr>` : ''}
          </tbody>
        </table>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Pledged Collateral Assets</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; margin-bottom: 40px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Collateral Asset / Details</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Asset Type</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">Appraised Value</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">LTV %</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: center;">Status</th>
            </tr>
          </thead>
          <tbody>
            ${collaterals.value.map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${row.asset || '-'}</td>
                <td style="padding: 10px 12px; color: #475569;">${row.collateral_type || '-'}</td>
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 700; text-align: right;">${fmt(row.collateral_value)}</td>
                <td style="padding: 10px 12px; color: #475569; text-align: right;">${row.ltv_percent || 0}%</td>
                <td style="padding: 10px 12px; text-align: center;">
                  <span style="background: #f0fdf4; color: #16a34a; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">
                    ${row.status || 'Active'}
                  </span>
                </td>
              </tr>
            `).join('')}
            ${!collaterals.value.length ? `<tr><td colspan="5" style="padding: 20px; text-align: center; color: #94a3b8;">No collateral records found</td></tr>` : ''}
          </tbody>
        </table>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Registered Settlement Accounts</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Bank</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Account Number</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Account Name</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: center;">Primary</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: center;">Verification</th>
            </tr>
          </thead>
          <tbody>
            ${bankAccounts.value.map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${row.bank || '-'}</td>
                <td style="padding: 10px 12px; color: #1e293b; font-family: monospace;">${row.account_number || '-'}</td>
                <td style="padding: 10px 12px; color: #475569;">${row.account_name || '-'}</td>
                <td style="padding: 10px 12px; text-align: center;">
                  <span style="font-size: 10px; font-weight: 800; color: ${row.is_primary ? '#005e6a' : '#94a3b8'};">
                    ${row.is_primary ? 'YES' : 'NO'}
                  </span>
                </td>
                <td style="padding: 10px 12px; text-align: center;">
                  <span style="background: ${row.verification_status === 'Verified' ? '#f0fdf4' : '#fff1f2'}; color: ${row.verification_status === 'Verified' ? '#16a34a' : '#e11d48'}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">
                    ${row.verification_status || 'Pending'}
                  </span>
                </td>
              </tr>
            `).join('')}
            ${!bankAccounts.value.length ? `<tr><td colspan="5" style="padding: 20px; text-align: center; color: #94a3b8;">No bank accounts found</td></tr>` : ''}
          </tbody>
        </table>
      </div>
    `
  }
  
  if (incRisk || (incCurrent && activeTab.value === 'risk')) {
    html += `
      <div class="page-section" style="page-break-after: always; padding-top: 20px; position: relative; min-height: 900px;">
        ${watermark ? `<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 5rem; color: rgba(226, 232, 240, 0.2); font-weight: 800; pointer-events: none; z-index: 0; white-space: nowrap; text-transform: uppercase;">${watermark}</div>` : ''}
        
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 25px;">
          <span style="font-size: 12px; font-weight: 700; color: #005e6a; letter-spacing: 0.5px;">SECTION 4: RISK EVALUATION & METRICS</span>
          <span style="font-size: 11px; color: #94a3b8;">${cust.customer_name || cust.name}</span>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-bottom: 40px;">
          <div style="background: #fff8e6; border: 1px solid #ffe8cc; border-radius: 8px; padding: 20px; text-align: center;">
            <div style="font-size: 11px; font-weight: 800; color: #b78103; text-transform: uppercase; margin-bottom: 6px;">UAT Risk Rating</div>
            <div style="font-size: 42px; font-weight: 900; color: #b78103; margin-bottom: 5px;">${latestRisk.value?.risk_grade || 'B'}</div>
            <div style="font-size: 12px; font-weight: 700; color: #667085;">Internal Score: ${latestRisk.value?.internal_score || 720} / 1000</div>
          </div>
          <div style="background: #f8fafc; border: 1px solid #edf2f7; border-radius: 8px; padding: 20px;">
            <h4 style="font-size: 12px; font-weight: 800; color: #334155; margin: 0 0 8px 0; text-transform: uppercase;">Adverse Risk Factors & Triggers</h4>
            <p style="font-size: 12px; color: #475569; margin: 0 0 10px 0; line-height: 1.5;">
              <strong>Factors:</strong> ${latestRisk.value?.risk_factors || 'No severe qualitative adverse risks reported in UAT.'}
            </p>
            <p style="font-size: 12px; color: #475569; margin: 0; line-height: 1.5;">
              <strong>Early Warning triggers:</strong> ${latestRisk.value?.early_warning_triggers || 'No triggers tripped.'}
            </p>
          </div>
        </div>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Recent Financial Transactions</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Date</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Transaction Type</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">Amount</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">Running Balance</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: center;">Status</th>
            </tr>
          </thead>
          <tbody>
            ${transactions.value.slice(0, 10).map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #64748b;">${fmtDate(row.transaction_date)}</td>
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${row.transaction_type || '-'}</td>
                <td style="padding: 10px 12px; color: ${row.transaction_type === 'Missed Payment' ? '#dc2626' : '#1e293b'}; font-weight: 700; text-align: right;">${fmt(row.amount)}</td>
                <td style="padding: 10px 12px; color: #475569; text-align: right;">${fmt(row.running_balance)}</td>
                <td style="padding: 10px 12px; text-align: center;">
                  <span style="background: ${row.status === 'Posted' ? '#f0fdf4' : '#fffbeb'}; color: ${row.status === 'Posted' ? '#16a34a' : '#b45309'}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">
                    ${row.status || 'Posted'}
                  </span>
                </td>
              </tr>
            `).join('')}
            ${!transactions.value.length ? `<tr><td colspan="5" style="padding: 20px; text-align: center; color: #94a3b8;">No transactions records found</td></tr>` : ''}
          </tbody>
        </table>
      </div>
    `
  }
  
  if (incAll || (incCurrent && activeTab.value === 'statements')) {
    html += `
      <div class="page-section" style="padding-top: 20px; position: relative; min-height: 900px;">
        ${watermark ? `<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 5rem; color: rgba(226, 232, 240, 0.2); font-weight: 800; pointer-events: none; z-index: 0; white-space: nowrap; text-transform: uppercase;">${watermark}</div>` : ''}
        
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 25px;">
          <span style="font-size: 12px; font-weight: 700; color: #005e6a; letter-spacing: 0.5px;">SECTION 5: FINANCIAL STATEMENT SPREADING</span>
          <span style="font-size: 11px; color: #94a3b8;">${cust.customer_name || cust.name}</span>
        </div>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Financial Statement Spreading</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden; margin-bottom: 40px;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Statement Type</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Metric Key / Description</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: center;">FY Year</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569; text-align: right;">Amount</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Audited / Status</th>
            </tr>
          </thead>
          <tbody>
            ${financials.value.slice(0, 20).map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #475569;">${row.statement_type || 'P&L'}</td>
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${row.metric || '-'}</td>
                <td style="padding: 10px 12px; text-align: center; color: #0f172a; font-weight: 600;">${row.year || '-'}</td>
                <td style="padding: 10px 12px; color: #005e6a; font-weight: 700; text-align: right;">${fmt(row.amount)}</td>
                <td style="padding: 10px 12px;">
                  <span style="background: ${row.audited ? '#f0fdf4' : '#f1f5f9'}; color: ${row.audited ? '#16a34a' : '#64748b'}; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold;">
                    ${row.audited ? 'AUDITED' : 'UNAUDITED'}
                  </span>
                </td>
              </tr>
            `).join('')}
            ${!financials.value.length ? `<tr><td colspan="5" style="padding: 20px; text-align: center; color: #94a3b8;">No financial records found</td></tr>` : ''}
          </tbody>
        </table>
        
        <h3 style="font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 0.5px;">Relationship Manager Site Visit History</h3>
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; border: 1px solid #edf2f7; border-radius: 6px; overflow: hidden;">
          <thead>
            <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: left;">
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Visit Date</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">RM Auditor</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">GPS Coordinates</th>
              <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Next Reminder</th>
            </tr>
          </thead>
          <tbody>
            ${siteVisits.value.map(row => `
              <tr style="border-bottom: 1px solid #f1f5f9;">
                <td style="padding: 10px 12px; color: #1e293b; font-weight: 600;">${fmtDate(row.visit_date)}</td>
                <td style="padding: 10px 12px; color: #334155;">${row.rm || 'RM'}</td>
                <td style="padding: 10px 12px; color: #64748b; font-family: monospace;">${row.gps_coordinates || '-'}</td>
                <td style="padding: 10px 12px; color: #64748b;">${fmtDate(row.next_visit_date)}</td>
              </tr>
            `).join('')}
            ${!siteVisits.value.length ? `<tr><td colspan="4" style="padding: 20px; text-align: center; color: #94a3b8;">No site visit logs found</td></tr>` : ''}
          </tbody>
        </table>
      </div>
    `
  }
  
  html += `</div>`
  return html
}

function buildProfileCSV(cust, scope) {
  let csv = ''
  
  const addHeader = (title) => {
    csv += `\n=========================================\n`
    csv += `${title.toUpperCase()}\n`
    csv += `=========================================\n`
  }
  const addSubHeader = (title) => {
    csv += `\n-----------------------------------------\n`
    csv += `${title.toUpperCase()}\n`
    csv += `-----------------------------------------\n`
  }
  const addRow = (arr) => {
    csv += arr.map(val => {
      const s = val == null ? '' : String(val)
      return s.includes(',') || s.includes('"') || s.includes('\n') ? `"${s.replace(/"/g, '""')}"` : s
    }).join(',') + '\n'
  }
  
  addHeader('bni crm - customer portfolio report')
  addRow(['Customer Name', cust.customer_name || cust.name])
  addRow(['Customer Type', cust.customer_type || 'Company'])
  addRow(['Tax ID / NPWP', cust.tax_id || kyc.value?.npwp || '-'])
  addRow(['Risk Rating', summary.value?.risk_grade || 'Unrated'])
  addRow(['Risk Score', `${summary.value?.score || 0} pts`])
  addRow(['Export Date', new Date().toISOString().slice(0, 19).replace('T', ' ')])
  
  addSubHeader('executive ai summary')
  csv += `${summaryText.value || 'No summary text available.'}\n`
  
  if (scope === 'Full Profile' || scope === 'Profile & KYC') {
    addSubHeader('kyc review registry')
    addRow(['KYC Status', kyc.value?.status || 'Pending'])
    addRow(['e-KYC Result', kyc.value?.ekyc_result || 'Manual'])
    addRow(['Last Review Date', kyc.value?.review_date || '-'])
    addRow(['Next Review Date', kyc.value?.next_review_date || '-'])
    addRow(['Registered Address', kyc.value?.registered_address || '-'])
  }
  
  if (scope === 'Full Profile' || scope === 'Profile & KYC') {
    addSubHeader('corporate cap table (shareholders)')
    addRow(['Shareholder Name', 'Ownership %', 'Is UBO', 'Linked Customer'])
    shareholders.value.forEach(row => {
      addRow([row.related_party, `${row.ownership_percent || 0}%`, row.is_ubo ? 'Yes' : 'No', row.related_customer])
    })
    
    addSubHeader('board of directors & commissioners')
    addRow(['Name', 'Position', 'ID / NIK', 'AML/PEP Check', 'Background Check'])
    directors.value.forEach(row => {
      addRow([row.related_party, row.position, row.director_id, row.aml_pep_status, row.background_check_status])
    })
  }
  
  if (scope === 'Full Profile' || scope === 'Financing') {
    addSubHeader('credit facilities & outstanding exposure')
    addRow(['Facility Type', 'Outstanding Balance', 'Limit Approved Amount', 'Due Date', 'KOL Rating'])
    facilities.value.forEach(row => {
      addRow([row.facility_type || row.product_type, row.outstanding, row.limit_amount, row.due_date, row.health])
    })
    
    addSubHeader('pledged collateral portfolio')
    addRow(['Asset Details', 'Collateral Type', 'Appraised Value', 'LTV %', 'Status'])
    collaterals.value.forEach(row => {
      addRow([row.asset, row.collateral_type, row.collateral_value, `${row.ltv_percent || 0}%`, row.status])
    })
  }
  
  if (scope === 'Full Profile' || scope === 'Risk') {
    addSubHeader('recent financial transaction log')
    addRow(['Transaction Date', 'Type', 'Amount', 'Running Balance', 'Status', 'Notes'])
    transactions.value.forEach(row => {
      addRow([row.transaction_date, row.transaction_type, row.amount, row.running_balance, row.status, row.notes])
    })
  }
  
  if (scope === 'Full Profile') {
    addSubHeader('financial statements spreading')
    addRow(['Statement Type', 'Metric Description', 'Fiscal Year', 'Amount', 'Audited Status'])
    financials.value.forEach(row => {
      addRow([row.statement_type || 'P&L', row.metric, row.year, row.amount, row.audited ? 'Audited' : 'Unaudited'])
    })
  }
  
  return csv
}

async function exportProfile() {
  try {
    await call('crm.api.credit.export_customer_profile', { customer: selectedCustomerName.value, ...exportForm })
  } catch (err) {
    console.error("Backend request fail (non-blocking):", err)
  }

  if (exportForm.format === 'PDF Report') {
    const htmlContent = buildProfileHTML(selectedCustomer.value || { name: selectedCustomerName.value }, exportForm.scope, exportForm.watermark)
    const printEl = document.createElement('div')
    printEl.innerHTML = htmlContent
    document.body.appendChild(printEl)
    
    try {
      await html2pdf().set({
        margin: [10, 10, 10, 10],
        filename: `${selectedCustomerName.value}-profile-${exportForm.scope.toLowerCase().replace(/ & /g, '_').replace(/ /g, '_')}-${new Date().toISOString().slice(0, 10)}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      }).from(printEl).save()
      
      toast.success(__('PDF report downloaded successfully'))
    } catch (e) {
      toast.error(__('PDF export failed'))
      console.error(e)
    } finally {
      document.body.removeChild(printEl)
    }
  } else {
    const csvContent = buildProfileCSV(selectedCustomer.value || { name: selectedCustomerName.value }, exportForm.scope)
    const bom = '\uFEFF'
    const blob = new Blob([bom + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${selectedCustomerName.value}-profile-${exportForm.scope.toLowerCase().replace(/ & /g, '_').replace(/ /g, '_')}-${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(link.href)
    toast.success(__('Excel spreadsheet downloaded successfully'))
  }
  
  showExportDialog.value = false
  reloadCustomer360()
}

async function mergeCustomer(confirm) {
  if (!mergeForm.target) {
    toast.error(__('Target customer is required'))
    return
  }
  await call('crm.api.credit.merge_customers', {
    source: selectedCustomerName.value,
    target: mergeForm.target,
    field_map: mergeForm.field_map_json,
    confirm,
  })
  toast.success(confirm ? __('Merge completed') : __('Merge preview captured'))
  reloadCustomer360()
}

function previewDocument(row) {
  if (row.file) window.open(row.file, '_blank')
  else toast.success(__('Preview state captured. Upload adapter can attach the file.'))
}

function openConversation(row) {
  if (row.conversation_link) window.open(row.conversation_link, '_blank')
  else openForm('communication', row)
}

function openRelatedCustomer(row) {
  const target = row?.related_customer || row?.name
  if (!target) return
  if (routeCustomer.value) {
    router.push({ name: 'Customer 360 Detail', params: { customer: target } })
    return
  }
  const customer = [...(customersResource.data || []), ...globalResults.value].find((item) => item.name === target)
  if (customer) selectCustomer(customer)
  else {
    selectedCustomerName.value = target
    selectedCustomer.value = { name: target, customer_name: target }
    reloadCustomer360()
  }
}

function exportRows(kind) {
  const rows = kind === 'transactions' ? filteredTransactions.value : []
  const csv = rows.map((row) => Object.values(row).map((value) => `"${String(value ?? '').replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${selectedCustomerName.value}-${kind}.csv`
  link.click()
  URL.revokeObjectURL(link.href)
}

async function runGlobalSearch() {
  if (searchQuery.value.length < 2) {
    globalResults.value = []
    return
  }
  try {
    globalResults.value = await call('crm.api.credit.global_customer_search', { query: searchQuery.value, limit: 30 })
  } catch {
    globalResults.value = []
  }
}

function pushRecentSearch(value) {
  value = String(value || '').trim()
  if (!value) return
  recentSearches.value = [value, ...recentSearches.value.filter((item) => item !== value)].slice(0, 5)
  localStorage.setItem('customer360RecentSearches', JSON.stringify(recentSearches.value))
}

function initials(value) {
  return (value || 'CU').slice(0, 2).toUpperCase()
}

function renderMarkdown(text) {
  if (!text) return '<p class="text-slate-400 text-sm">Click to edit or generate a summary...</p>'
  let html = String(text)
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^---$/gm, '<hr>')
    .replace(/^\|(.*)\|$/gm, (match) => {
      const cells = match.split('|').filter((cell) => cell.trim())
      if (cells.every((cell) => /^[\s:-]+$/.test(cell))) return ''
      return '<tr>' + cells.map((cell) => `<td>${cell.trim()}</td>`).join('') + '</tr>'
    })
    .replace(/^- (.*$)/gm, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
  html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
  html = html.replace(/(<tr>.*<\/tr>)/gs, '<table class="w-full border-collapse text-xs">$1</table>')
  if (!html.startsWith('<')) html = `<p>${html}</p>`
  return DOMPurify.sanitize(html)
}

function formatCurrency(value) {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(amount)
}

function normalizeDoc(doc) {
  return Object.fromEntries(Object.entries(doc).map(([key, value]) => [key, typeof value === 'string' ? value.replace(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})/, '$1 $2') : value]))
}

watch(searchQuery, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(runGlobalSearch, 250)
})

watch(
  () => customersResource.data,
  (rows) => {
    if (routeCustomer.value) loadRouteCustomer()
    else if (!selectedCustomer.value && rows?.length) selectCustomer(rows[0])
  },
)

watch(routeCustomer, () => {
  loadRouteCustomer()
})

onMounted(async () => {
  await customersResource.promise
  if (routeCustomer.value) loadRouteCustomer()
  else if (directoryCustomers.value.length > 0) selectCustomer(directoryCustomers.value[0])
})

usePageMeta(() => ({ title: 'Customer 360' }))

const StatCard = {
  props: ['label', 'value', 'detail', 'icon', 'tone'],
  setup(props) {
    const toneClass = {
      orange: 'bg-orange-50 text-orange-600',
      teal: 'bg-teal-50 text-teal-600',
      blue: 'bg-blue-50 text-blue-600',
      purple: 'bg-purple-50 text-purple-600',
      slate: 'bg-slate-100 text-slate-600',
      red: 'bg-red-50 text-red-600',
    }
    return () => h('div', { class: 'bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex items-center gap-4 min-w-0' }, [
      h('div', { class: `w-10 h-10 rounded-lg ${toneClass[props.tone] || toneClass.teal} flex items-center justify-center shrink-0` }, [h(FeatherIcon, { name: props.icon, class: 'h-5 w-5' })]),
      h('div', { class: 'min-w-0' }, [
        h('div', { class: 'text-xs font-semibold text-slate-400 uppercase tracking-wide truncate' }, props.label),
        h('div', { class: 'text-lg font-bold text-slate-800 mt-0.5 truncate' }, props.value),
        h('div', { class: 'text-xs text-slate-500 mt-0.5 truncate' }, props.detail),
      ]),
    ])
  },
}

const Panel = {
  props: ['title', 'icon'],
  setup(props, { slots, attrs }) {
    return () => h('div', { ...attrs, class: ['bg-white border border-slate-200 rounded-lg p-5 shadow-sm', attrs.class] }, [
      h('div', { class: 'flex items-center justify-between gap-3 mb-4' }, [
        h('div', { class: 'flex items-center gap-2 min-w-0' }, [
          props.icon ? h(FeatherIcon, { name: props.icon, class: 'h-5 w-5 text-teal-600 shrink-0' }) : null,
          h('h3', { class: 'font-bold text-slate-800 truncate' }, props.title),
        ]),
        slots.actions?.(),
      ]),
      slots.default?.(),
    ])
  },
}

const FieldDisplay = {
  props: ['label', 'value'],
  setup(props, { attrs }) {
    return () => h('div', { ...attrs, class: ['rounded-lg border border-slate-100 bg-slate-50 p-4', attrs.class] }, [
      h('div', { class: 'text-xs font-bold text-slate-500 uppercase mb-1' }, props.label),
      h('div', { class: 'text-sm font-semibold text-slate-800 whitespace-pre-wrap' }, props.value || '-'),
    ])
  },
}

const SimpleTable = {
  props: ['headers', 'rows', 'columns', 'currencyColumn', 'edit', 'action', 'actionLabel'],
  setup(props, { attrs }) {
    const currencyColumns = computed(() => String(props.currencyColumn || '').split(',').filter(Boolean))
    return () => h('div', { ...attrs, class: ['overflow-x-auto', attrs.class] }, [
      h('table', { class: 'w-full text-sm min-w-[720px]' }, [
        h('thead', [h('tr', { class: 'bg-slate-50 text-slate-500 border-b border-slate-200' }, [
          ...props.headers.map((head) => h('th', { class: 'py-3 px-4 text-left font-bold' }, head)),
          props.edit || props.action ? h('th', { class: 'py-3 px-4 text-right font-bold' }, __('Actions')) : null,
        ])]),
        h('tbody', [
          ...(props.rows || []).map((row) => h('tr', { class: 'border-b border-slate-100 hover:bg-slate-50' }, [
            ...props.columns.map((column) => h('td', { class: 'py-3 px-4 text-slate-700 align-top' }, formatCell(row[column], currencyColumns.value.includes(column)))),
            props.edit || props.action ? h('td', { class: 'py-2 px-4 text-right whitespace-nowrap' }, [
              props.action ? h(Button, { size: 'sm', variant: 'outline', label: props.actionLabel || __('Open'), onClick: () => props.action(row) }) : null,
              props.edit ? h(Button, { class: 'ml-2', size: 'sm', variant: 'subtle', label: __('Edit'), onClick: () => props.edit(row) }) : null,
            ]) : null,
          ])),
          !(props.rows || []).length ? h('tr', [h('td', { colspan: props.headers.length + 1, class: 'py-8 text-center text-slate-400' }, __('No records yet'))]) : null,
        ]),
      ]),
    ])
  },
}

function formatCell(value, isCurrency) {
  if (isCurrency) return formatCurrency(value)
  if (value === 1) return 'Yes'
  if (value === 0) return 'No'
  return String(value ?? '-')
}

const ActivityList = {
  props: ['tasks', 'notes', 'events', 'filter'],
  emits: ['toggleTask'],
  setup(props, { emit }) {
    return () => {
      const showTasks = props.filter === 'all' || props.filter === 'task'
      const showNotes = props.filter === 'all' || props.filter === 'note'
      const showEvents = props.filter === 'all' || props.filter === 'event'
      const children = []
      if (showTasks) {
        children.push(...props.tasks.slice(0, 4).map((task) => h('div', { class: 'flex items-start gap-2 rounded-lg border border-slate-100 bg-slate-50 p-3' }, [
          h('input', { type: 'checkbox', checked: task.status === 'Done', class: 'mt-1 accent-teal-600', onChange: () => emit('toggleTask', task) }),
          h('div', { class: 'min-w-0' }, [h('div', { class: 'text-sm font-semibold text-slate-800 truncate' }, task.title), h('div', { class: 'text-xs text-slate-500' }, `${task.priority || 'Medium'} - ${task.due_date || 'No due date'}`)]),
        ])))
      }
      if (showNotes) {
        children.push(...props.notes.slice(0, 2).map((note) => h('div', { class: 'rounded-lg border border-slate-100 p-3' }, [h('div', { class: 'text-sm font-semibold text-slate-800' }, note.title), h('div', { class: 'text-xs text-slate-500 truncate' }, note.content || '')])))
      }
      if (showEvents) {
        children.push(...props.events.slice(0, 2).map((event) => h('div', { class: 'rounded-lg border border-slate-100 p-3' }, [h('div', { class: 'text-sm font-semibold text-slate-800' }, event.subject), h('div', { class: 'text-xs text-slate-500' }, event.starts_on || '')])))
      }
      if (!children.length) {
        children.push(h('div', { class: 'text-sm text-slate-400' }, __('No activities yet')))
      }
      return h('div', { class: 'space-y-3' }, children)
    }
  },
}

const TimelineList = {
  props: ['items'],
  setup(props) {
    const colorClass = { blue: 'text-blue-600 bg-blue-50', teal: 'text-teal-600 bg-teal-50', emerald: 'text-emerald-600 bg-emerald-50', amber: 'text-amber-600 bg-amber-50', purple: 'text-purple-600 bg-purple-50', cyan: 'text-cyan-600 bg-cyan-50', orange: 'text-orange-600 bg-orange-50', red: 'text-red-600 bg-red-50', slate: 'text-slate-600 bg-slate-100' }
    return () => h('div', { class: 'space-y-3' }, [
      ...props.items.map((item) => h('div', { class: 'flex gap-3' }, [
        h('div', { class: `w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${colorClass[item.color] || colorClass.slate}` }, [h(FeatherIcon, { name: item.icon || 'file', class: 'h-4 w-4' })]),
        h('div', { class: 'min-w-0' }, [h('div', { class: 'text-xs font-semibold text-slate-700 truncate' }, item.title || item.kind), h('div', { class: 'text-xs text-slate-500 truncate' }, `${item.kind} - ${item.modified || 'No date'}`), item.description ? h('div', { class: 'text-xs text-slate-400 truncate' }, item.description) : null]),
      ])),
      !props.items.length ? h('div', { class: 'text-sm text-slate-400' }, __('No timeline records yet')) : null,
    ])
  },
}

const RelationshipGraph = {
  props: ['customer', 'relationships', 'zoom'],
  emits: ['openNode'],
  setup(props, { emit }) {
    return () => h('div', { class: 'relative h-72 rounded-lg border border-slate-100 bg-slate-50 overflow-hidden' }, [
      h('div', { class: 'absolute inset-0 flex items-center justify-center', style: { transform: `scale(${props.zoom || 1})` } }, [
        h('div', { class: 'relative w-64 h-64' }, [
          h('div', { class: 'absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 rounded-full bg-teal-600 text-white flex items-center justify-center text-xs font-black text-center p-2 shadow-lg' }, props.customer?.customer_name || props.customer?.name || 'Customer'),
          ...props.relationships.slice(0, 8).map((rel, index) => {
            const angle = (index / Math.max(props.relationships.length, 1)) * Math.PI * 2
            const x = 112 + Math.cos(angle) * 100
            const y = 112 + Math.sin(angle) * 100
            return h('button', { class: 'absolute w-16 h-16 rounded-full bg-white border border-slate-200 text-[10px] font-bold text-slate-600 shadow-sm p-1 hover:border-teal-400', style: { left: `${x}px`, top: `${y}px` }, onClick: () => emit('openNode', rel) }, [h('span', { class: 'line-clamp-2' }, rel.related_party || rel.relationship_type)])
          }),
        ]),
      ]),
    ])
  },
}

const OwnershipChart = {
  props: ['shareholders'],
  setup(props) {
    return () => h('div', { class: 'mb-4 flex h-10 overflow-hidden rounded-lg border border-slate-100 bg-slate-50' }, [
      ...(props.shareholders || []).map((row, index) => h('div', { class: 'flex items-center justify-center px-2 text-[11px] font-bold text-white', style: { width: `${Math.max(Number(row.ownership_percent || 0), 5)}%`, backgroundColor: ['#0f766e', '#2563eb', '#c2410c', '#7c3aed', '#be123c'][index % 5] } }, `${row.related_party || 'Owner'} ${row.ownership_percent || 0}%`)),
      !(props.shareholders || []).length ? h('div', { class: 'flex-1 flex items-center justify-center text-xs text-slate-400' }, __('No ownership records')) : null,
    ])
  },
}

const ScoreTrend = {
  props: ['reports', 'risks'],
  setup(props) {
    return () => {
      const points = [...(props.reports || []).map((row) => Number(row.score || 0)), ...(props.risks || []).map((row) => Number(row.internal_score || 0))].slice(0, 6).reverse()
      return h('div', { class: 'flex items-end gap-1 h-16 border-b border-slate-100' }, [
        ...points.map((score) => h('div', { class: 'flex-1 rounded-t bg-teal-500 min-w-4', style: { height: `${Math.max(8, Math.min(100, score / 10))}%` }, title: String(score) })),
        !points.length ? h('div', { class: 'text-xs text-slate-400' }, __('No score trend yet')) : null,
      ])
    }
  },
}

const FormInput = {
  props: ['label', 'type', 'modelValue', 'error'],
  emits: ['update:modelValue'],
  setup(props, { attrs, emit }) {
    return () => h('label', { class: 'block' }, [
      h('span', { class: 'block text-[11px] font-bold text-slate-500 uppercase mb-1 tracking-wider' }, props.label),
      h('input', { 
        ...attrs, 
        type: props.type || 'text', 
        value: props.modelValue, 
        class: [
          'w-full px-3.5 py-2 border rounded-lg text-sm bg-slate-50/20 focus:outline-none focus:ring-4 transition-all duration-200',
          props.error 
            ? 'border-red-500 hover:border-red-600 focus:border-red-500 focus:ring-red-500/10' 
            : 'border-slate-200 hover:border-slate-300 focus:border-teal-500 focus:ring-teal-500/10'
        ],
        onInput: (event) => emit('update:modelValue', event.target.value) 
      }),
      props.error ? h('span', { class: 'block mt-1 text-xs text-red-500 font-semibold' }, props.error) : null
    ])
  },
}

const FormTextarea = {
  props: ['label', 'modelValue', 'error'],
  emits: ['update:modelValue'],
  setup(props, { attrs, emit }) {
    return () => h('label', { class: 'block' }, [
      h('span', { class: 'block text-[11px] font-bold text-slate-500 uppercase mb-1 tracking-wider' }, props.label),
      h('textarea', { 
        ...attrs, 
        rows: 3, 
        value: props.modelValue, 
        class: [
          'w-full px-3.5 py-2 border rounded-lg text-sm bg-slate-50/20 focus:outline-none focus:ring-4 transition-all duration-200',
          props.error 
            ? 'border-red-500 hover:border-red-600 focus:border-red-500 focus:ring-red-500/10' 
            : 'border-slate-200 hover:border-slate-300 focus:border-teal-500 focus:ring-teal-500/10'
        ],
        onInput: (event) => emit('update:modelValue', event.target.value) 
      }),
      props.error ? h('span', { class: 'block mt-1 text-xs text-red-500 font-semibold' }, props.error) : null
    ])
  },
}

const FormSelect = {
  props: ['label', 'options', 'modelValue', 'compact', 'error'],
  emits: ['update:modelValue'],
  setup(props, { attrs, emit }) {
    return () => h('label', { class: props.compact ? 'block min-w-32' : 'block' }, [
      h('span', { class: 'block text-[11px] font-bold text-slate-500 uppercase mb-1 tracking-wider' }, props.label),
      h('select', { 
        ...attrs, 
        value: props.modelValue, 
        class: [
          'w-full px-3.5 py-2 border rounded-lg text-sm focus:outline-none focus:ring-4 transition-all duration-200 bg-white',
          props.error 
            ? 'border-red-500 hover:border-red-600 focus:border-red-500 focus:ring-red-500/10' 
            : 'border-slate-200 hover:border-slate-300 focus:border-teal-500 focus:ring-teal-500/10'
        ],
        onChange: (event) => emit('update:modelValue', event.target.value) 
      }, (props.options || []).map((option) => h('option', { value: option }, option))),
      props.error ? h('span', { class: 'block mt-1 text-xs text-red-500 font-semibold' }, props.error) : null
    ])
  },
}

const FormCheckbox = {
  props: ['label', 'modelValue'],
  emits: ['update:modelValue'],
  setup(props, { attrs, emit }) {
    return () => h('label', { ...attrs, class: 'flex items-center gap-3 py-2 cursor-pointer select-none group' }, [
      h('input', { 
        type: 'checkbox', 
        checked: Boolean(props.modelValue), 
        class: 'w-4 h-4 rounded border-slate-300 text-teal-600 focus:ring-teal-500 accent-teal-600 transition duration-150', 
        onChange: (event) => emit('update:modelValue', event.target.checked ? 1 : 0) 
      }),
      h('span', { class: 'text-sm font-medium text-slate-700 group-hover:text-slate-900 transition-colors duration-150' }, props.label),
    ])
  },
}
</script>

<style scoped>
::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
:deep(.prose table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
  margin: 0.5rem 0;
}
:deep(.prose td), :deep(.prose th) {
  border: 1px solid #e2e8f0;
  padding: 0.3rem 0.5rem;
  vertical-align: top;
}
:deep(.prose tr:nth-child(even)) {
  background: #f8fafc;
}
:deep(.prose h2) {
  font-size: 1rem;
  font-weight: 700;
  margin: 0.75rem 0 0.25rem;
  color: #1e293b;
}
:deep(.prose h3) {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0.5rem 0 0.25rem;
  color: #334155;
}
:deep(.prose ul) {
  list-style: disc;
  padding-left: 1.25rem;
  margin: 0.25rem 0;
}
:deep(.prose hr) {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 0.75rem 0;
}
</style>
