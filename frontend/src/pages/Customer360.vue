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
          @click="selectCustomer(cust)"
          class="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all hover:bg-slate-50"
          :class="selectedCustomerName === cust.name ? 'bg-teal-50 border border-teal-100' : ''"
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
              @click="activeTab = tab.key"
              class="pb-3 text-sm font-semibold border-b-2 transition-all whitespace-nowrap"
              :class="activeTab === tab.key ? 'border-teal-600 text-teal-600' : 'border-transparent text-slate-500 hover:text-slate-800'"
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
                <textarea
                  v-model="summaryText"
                  rows="6"
                  class="w-full p-4 bg-teal-50/30 border border-teal-100 rounded-lg text-sm text-slate-700 focus:outline-none focus:border-teal-400"
                />
                <div class="mt-3 flex flex-wrap justify-between items-center gap-2 text-xs text-slate-400">
                  <span>{{ __('5-bullet summary generated from persisted Customer 360 records') }}</span>
                  <div class="flex gap-2">
                    <Button variant="subtle" size="sm" :label="__('Refresh')" @click="reloadCustomer360" />
                    <Button variant="solid" size="sm" :label="__('Save Summary')" @click="saveCustomerSummary" />
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
                  <Button size="sm" variant="solid" :label="__('Task')" @click="openForm('task')" />
                  <Button size="sm" variant="outline" :label="__('Note')" @click="openForm('note')" />
                  <Button size="sm" variant="outline" :label="__('Event')" @click="openForm('event')" />
                </div>
                <ActivityList :tasks="tasks" :notes="notes" :events="events" @toggle-task="toggleTask" />
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
                <Button size="sm" variant="solid" :label="__('Edit Profile')" @click="showProfileEdit = true" />
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
            <Panel :title="__('Shareholders')" icon="pie-chart">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Shareholder')" @click="openForm('relationship', { relationship_type: 'Shareholder' })" />
              </template>
              <div class="mb-4 flex flex-wrap items-center gap-3">
                <Badge :label="`${summary.shareholder_total || 0}% ownership captured`" :theme="summary.shareholder_balanced ? 'green' : 'orange'" />
                <span class="text-xs text-slate-500">{{ __('UAT requires total shareholders to equal 100%.') }}</span>
              </div>
              <OwnershipChart :shareholders="shareholders" />
              <SimpleTable :headers="['Shareholder', 'Ownership %', 'UBO', 'Linked Profile']" :rows="shareholders" :columns="['related_party', 'ownership_percent', 'is_ubo', 'related_customer']" :edit="(row) => openForm('relationship', row)" />
            </Panel>

            <Panel :title="__('Directors')" icon="briefcase">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Director')" @click="openForm('relationship', { relationship_type: 'Director' })" />
              </template>
              <SimpleTable :headers="['Name', 'Role', 'ID', 'LinkedIn', 'Tenure', 'AML/PEP', 'Background']" :rows="directors" :columns="['related_party', 'position', 'director_id', 'linkedin_url', 'tenure_start', 'aml_pep_status', 'background_check_status']" :edit="(row) => openForm('relationship', row)" :action="runAmlCheck" action-label="AML/PEP" />
            </Panel>

            <Panel :title="__('Related Entities')" icon="git-branch">
              <template #actions>
                <Button size="sm" variant="solid" :label="__('Add Related Entity')" @click="openForm('relationship', { relationship_type: 'Group Company' })" />
              </template>
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
          <FormInput v-model="profileForm.customer_name" label="Customer Name" />
          <FormSelect v-model="profileForm.customer_type" label="Customer Type" :options="['Company', 'Individual']" />
          <FormInput v-model="profileForm.tax_id" label="Tax ID / NPWP" />
          <FormInput v-model="profileForm.website" label="Website" />
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2 justify-end">
          <Button variant="outline" :label="__('Cancel')" @click="showProfileEdit = false" />
          <Button variant="solid" :label="__('Save')" @click="saveProfile" />
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showExportDialog" :options="{ title: __('Export Customer Profile') }">
      <template #body-content>
        <div class="space-y-4 pt-3">
          <FormSelect v-model="exportForm.scope" label="Scope" :options="['Full Profile', 'Current Tab', 'Profile & KYC', 'Financing', 'Risk', 'Documents']" />
          <FormInput v-model="exportForm.watermark" label="Watermark" />
          <FormInput v-model="exportForm.password" label="PDF Password" type="password" />
          <div class="rounded-lg border border-amber-100 bg-amber-50 p-3 text-xs text-amber-700">
            {{ __('Email/PDF renderer is captured as an export request record until the production adapter is configured.') }}
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2 justify-end">
          <Button variant="outline" :label="__('Cancel')" @click="showExportDialog = false" />
          <Button variant="solid" :label="__('Create Export Request')" @click="exportProfile" />
        </div>
      </template>
    </Dialog>

    <Dialog v-model="showDynamicForm" :options="{ title: dynamicForm.title }">
      <template #body-content>
        <div class="space-y-4 pt-3">
          <template v-for="field in dynamicForm.fields" :key="field.fieldname">
            <FormSelect v-if="field.type === 'select'" v-model="dynamicForm.doc[field.fieldname]" :label="field.label" :options="field.options" />
            <FormTextarea v-else-if="field.type === 'textarea'" v-model="dynamicForm.doc[field.fieldname]" :label="field.label" />
            <FormCheckbox v-else-if="field.type === 'checkbox'" v-model="dynamicForm.doc[field.fieldname]" :label="field.label" />
            <FormInput v-else v-model="dynamicForm.doc[field.fieldname]" :label="field.label" :type="field.type || 'text'" />
          </template>
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2 justify-end">
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
const globalResults = ref([])
const recentSearches = ref(JSON.parse(localStorage.getItem('customer360RecentSearches') || '[]'))
const graphFilter = ref('All')
const graphZoom = ref(1)
const timelineFilter = ref('All')
const productFilter = ref('')
const documentSearch = ref('')
const communicationFilter = ref('All')
const transactionFrom = ref('')
const transactionTo = ref('')
let searchTimer = null
const routeCustomer = computed(() => String(route.params.customer || ''))

const newCustomer = reactive({ customer_name: '', customer_type: 'Company' })
const profileForm = reactive({ customer_name: '', customer_type: 'Company', tax_id: '', website: '' })
const exportForm = reactive({ scope: 'Full Profile', watermark: 'SUMMON BNI Confidential', password: '' })
const mergeForm = reactive({ target: '', field_map_json: '{}' })
const dynamicForm = reactive({ key: '', title: '', doctype: '', doc: {}, fields: [] })

const tabs = [
  { key: 'overview', label: 'Overview' },
  { key: 'profile', label: 'Personal / KYC' },
  { key: 'ownership', label: 'Ownership' },
  { key: 'financing', label: 'Financing' },
  { key: 'documents', label: 'Documents & Comms' },
  { key: 'risk', label: 'Risk & Transactions' },
  { key: 'statements', label: 'Statements & Visits' },
  { key: 'engagement', label: 'Engagement & Merge' },
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
    defaults: { borrower: selectedCustomerName.value, borrower_type: 'Individual', status: 'Draft' },
    fields: [field('facility_type', 'Facility Type'), field('requested_amount', 'Requested Amount', 'number'), field('employer_name', 'Employer / Affiliation'), field('public_company_ticker', 'PT Tbk Ticker'), field('purpose', 'Purpose', 'textarea')],
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
      field('related_customer', 'Linked Customer Profile'),
      field('relationship_type', 'Relationship Type', 'select', ['Shareholder', 'UBO', 'Director', 'Commissioner', 'Group Company', 'RM', 'Other']),
      field('ownership_percent', 'Ownership %', 'number'),
      field('position', 'Position / Role'),
      field('director_id', 'Director ID / KTP'),
      field('linkedin_url', 'LinkedIn URL'),
      field('tenure_start', 'Tenure Start', 'date'),
      field('aml_pep_status', 'AML / PEP Status', 'select', ['Manual', 'Pending Vendor', 'Clear', 'Potential Match', 'Unavailable']),
      field('background_check_status', 'Background Check', 'select', ['Manual', 'Pending Vendor', 'Clear', 'Flagged', 'Unavailable']),
      field('exposure', 'Exposure', 'number'),
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
      field('outstanding', 'Outstanding', 'number'),
      field('limit_amount', 'Limit Amount', 'number'),
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
    fields: [field('asset', 'Asset'), field('collateral_type', 'Type'), field('collateral_value', 'Value', 'number'), field('linked_facility', 'Linked Facility ID'), field('ltv_percent', 'LTV %', 'number'), field('expiry_date', 'Expiry Date', 'date'), field('insurance_expiry', 'Insurance Expiry', 'date'), field('document_link', 'Document Link'), field('reappraisal_status', 'Re-appraisal', 'select', ['Not Required', 'Due', 'In Progress', 'Completed']), field('status', 'Status', 'select', ['Active', 'Expired', 'Released', 'Under Review'])],
  },
  bureau: {
    title: __('Bureau Report'),
    doctype: 'CRM Bureau Report',
    defaults: { customer: selectedCustomerName.value, source: 'SLIK/OJK Manual Upload' },
    fields: [field('source', 'Source', 'select', ['SLIK/OJK Manual Upload', 'PEFINDO', 'Internal', 'Other']), field('report_date', 'Report Date', 'date'), field('kol_status', 'KOL Status'), field('score', 'Score', 'number'), field('external_exposure', 'External Exposure', 'number'), field('notes', 'Notes', 'textarea')],
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
    fields: [field('statement_type', 'Statement Type', 'select', ['P&L', 'Balance Sheet', 'Cash Flow', 'Other']), field('metric', 'Metric'), field('year', 'Year', 'number'), field('amount', 'Amount', 'number'), field('auditor', 'Auditor'), field('audit_year', 'Audit Year', 'number'), field('source', 'Source'), field('extraction_status', 'AI Extraction Status', 'select', ['Manual', 'Pending Vendor', 'Extracted', 'Failed', 'Unavailable']), field('audited', 'Audited', 'checkbox'), field('forecast', 'Forecast', 'checkbox'), field('notes', 'Notes', 'textarea')],
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
    fields: [field('facility', 'Facility ID'), field('transaction_date', 'Transaction Date', 'date'), field('transaction_type', 'Type', 'select', ['Repayment', 'Missed Payment', 'Disbursement', 'Fee', 'Adjustment']), field('amount', 'Amount', 'number'), field('running_balance', 'Running Balance', 'number'), field('status', 'Status', 'select', ['Posted', 'Pending', 'Failed']), field('notes', 'Notes', 'textarea')],
  },
  task: {
    title: __('Customer Task'),
    doctype: 'CRM Task',
    defaults: { reference_doctype: 'Customer', reference_docname: selectedCustomerName.value, status: 'Todo', priority: 'Medium' },
    fields: [field('title', 'Title'), field('assigned_to', 'Assigned To'), field('priority', 'Priority', 'select', ['Low', 'Medium', 'High']), field('status', 'Status', 'select', ['Backlog', 'Todo', 'In Progress', 'Done', 'Canceled']), field('due_date', 'Due Date', 'datetime-local'), field('recurring', 'Recurring', 'checkbox'), field('recurrence_rule', 'Recurrence Rule'), field('description', 'Description', 'textarea')],
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

function field(fieldname, label, type = 'text', options = []) {
  return { fieldname, label, type, options }
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
  dynamicForm.key = key
  dynamicForm.title = config.title
  dynamicForm.doctype = config.doctype
  dynamicForm.fields = config.fields
  dynamicForm.doc = { ...config.defaults, ...existing }
  showDynamicForm.value = true
}

function submitDynamicForm() {
  insertResource.submit({ doctype: dynamicForm.doctype, doc: normalizeDoc(dynamicForm.doc) })
}

async function toggleTask(task) {
  const nextStatus = task.status === 'Done' ? 'Todo' : 'Done'
  await call('frappe.client.set_value', { doctype: 'CRM Task', name: task.name, fieldname: 'status', value: nextStatus })
  toast.success(__('Task updated'))
  reloadCustomer360()
}

async function saveProfile() {
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

async function exportProfile() {
  await call('crm.api.credit.export_customer_profile', { customer: selectedCustomerName.value, ...exportForm })
  toast.success(__('Export request created'))
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

function formatCurrency(value) {
  const amount = Number(value || 0)
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(amount)
}

function normalizeDoc(doc) {
  return Object.fromEntries(Object.entries(doc).map(([key, value]) => [key, typeof value === 'string' && value.includes('T') ? value.replace('T', ' ') : value]))
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
  props: ['tasks', 'notes', 'events'],
  emits: ['toggleTask'],
  setup(props, { emit }) {
    return () => h('div', { class: 'space-y-3' }, [
      ...props.tasks.slice(0, 4).map((task) => h('div', { class: 'flex items-start gap-2 rounded-lg border border-slate-100 bg-slate-50 p-3' }, [
        h('input', { type: 'checkbox', checked: task.status === 'Done', class: 'mt-1 accent-teal-600', onChange: () => emit('toggleTask', task) }),
        h('div', { class: 'min-w-0' }, [h('div', { class: 'text-sm font-semibold text-slate-800 truncate' }, task.title), h('div', { class: 'text-xs text-slate-500' }, `${task.priority || 'Medium'} - ${task.due_date || 'No due date'}`)]),
      ])),
      ...props.notes.slice(0, 2).map((note) => h('div', { class: 'rounded-lg border border-slate-100 p-3' }, [h('div', { class: 'text-sm font-semibold text-slate-800' }, note.title), h('div', { class: 'text-xs text-slate-500 truncate' }, note.content || '')])),
      ...props.events.slice(0, 2).map((event) => h('div', { class: 'rounded-lg border border-slate-100 p-3' }, [h('div', { class: 'text-sm font-semibold text-slate-800' }, event.subject), h('div', { class: 'text-xs text-slate-500' }, event.starts_on || '')])),
      !props.tasks.length && !props.notes.length && !props.events.length ? h('div', { class: 'text-sm text-slate-400' }, __('No activities yet')) : null,
    ])
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
  props: ['label', 'type', 'modelValue'],
  emits: ['update:modelValue'],
  setup(props, { attrs, emit }) {
    return () => h('label', { class: 'block' }, [
      h('span', { class: 'block text-xs font-bold text-slate-500 uppercase mb-1' }, props.label),
      h('input', { ...attrs, type: props.type || 'text', value: props.modelValue, class: 'w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-500', onInput: (event) => emit('update:modelValue', event.target.value) }),
    ])
  },
}

const FormTextarea = {
  props: ['label', 'modelValue'],
  emits: ['update:modelValue'],
  setup(props, { attrs, emit }) {
    return () => h('label', { class: 'block' }, [
      h('span', { class: 'block text-xs font-bold text-slate-500 uppercase mb-1' }, props.label),
      h('textarea', { ...attrs, rows: 3, value: props.modelValue, class: 'w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-500', onInput: (event) => emit('update:modelValue', event.target.value) }),
    ])
  },
}

const FormSelect = {
  props: ['label', 'options', 'modelValue', 'compact'],
  emits: ['update:modelValue'],
  setup(props, { attrs, emit }) {
    return () => h('label', { class: props.compact ? 'block min-w-32' : 'block' }, [
      h('span', { class: 'block text-xs font-bold text-slate-500 uppercase mb-1' }, props.label),
      h('select', { ...attrs, value: props.modelValue, class: 'w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-teal-500 bg-white', onChange: (event) => emit('update:modelValue', event.target.value) }, (props.options || []).map((option) => h('option', { value: option }, option))),
    ])
  },
}

const FormCheckbox = {
  props: ['label', 'modelValue'],
  emits: ['update:modelValue'],
  setup(props, { attrs, emit }) {
    return () => h('label', { ...attrs, class: 'flex items-center justify-between gap-3 rounded-lg border border-slate-200 px-3 py-2' }, [
      h('span', { class: 'text-sm font-semibold text-slate-700' }, props.label),
      h('input', { type: 'checkbox', checked: Boolean(props.modelValue), class: 'accent-teal-600', onChange: (event) => emit('update:modelValue', event.target.checked ? 1 : 0) }),
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
</style>
