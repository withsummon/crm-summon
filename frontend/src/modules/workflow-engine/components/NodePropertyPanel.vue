<template>
  <div class="flex h-full w-80 flex-col border-l border-crm-border bg-white shadow-sm z-10">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-crm-border">
      <div class="flex items-center gap-2">
        <div :class="['p-1 rounded', colorClasses.bg]">
          <component :is="getIcon(node.data?.nodeType)" :class="['w-4.5 h-4.5', colorClasses.text]" />
        </div>
        <div>
          <h2 class="text-sm font-semibold text-gray-800">{{ __('Node Properties') }}</h2>
          <p class="text-[10px] text-crm-muted font-mono mt-0.5">{{ node.id }}</p>
        </div>
      </div>
      <button
        class="text-crm-muted hover:text-crm-text text-xs p-1 hover:bg-surface-gray-1 rounded"
        @click="closePanel"
      >
        ✕
      </button>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-crm-border bg-surface-gray-1/40">
      <button
        v-for="tab in ['General', 'Settings']"
        :key="tab"
        class="flex-1 py-2 text-xs font-semibold text-center transition-colors border-b-2"
        :class="[
          activeTab === tab
            ? 'border-purple-600 text-purple-600 bg-white'
            : 'border-transparent text-crm-muted hover:text-crm-text hover:bg-surface-gray-1/80'
        ]"
        @click="activeTab = tab"
      >
        {{ __(tab) }}
      </button>
    </div>

    <!-- Scrollable Content -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <!-- GENERAL TAB -->
      <div v-if="activeTab === 'General'" class="space-y-4">
        <!-- Node Type -->
        <div>
          <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
            {{ __('Node Type') }}
          </label>
          <input
            type="text"
            readonly
            :value="node.data?.nodeType"
            class="w-full px-3 py-2 text-xs bg-surface-gray-1 rounded-lg border border-crm-border text-crm-muted cursor-not-allowed focus:outline-none"
          />
        </div>

        <!-- Node Label -->
        <div>
          <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
            {{ __('Node Label') }}
          </label>
          <input
            v-model="localLabel"
            type="text"
            class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
            @input="updateNode"
          />
        </div>

        <!-- Node Description -->
        <div>
          <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
            {{ __('Description') }}
          </label>
          <textarea
            v-model="localDescription"
            rows="3"
            class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text leading-normal resize-none"
            @input="updateNode"
          ></textarea>
        </div>
      </div>

      <!-- SETTINGS TAB -->
      <div v-else class="space-y-4">
        <!-- Start Node Settings -->
        <div v-if="node.data?.nodeType === 'StartNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Trigger Type') }}
            </label>
            <select
              v-model="localConfig.triggerType"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="manual">{{ __('Manual Submission') }}</option>
              <option value="auto">{{ __('Auto Triggered') }}</option>
              <option value="api">{{ __('API Triggered') }}</option>
            </select>
          </div>
        </div>

        <!-- End Node Settings -->
        <div v-else-if="node.data?.nodeType === 'EndNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Final Outcome') }}
            </label>
            <select
              v-model="localConfig.outcome"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="approved">{{ __('Approved') }}</option>
              <option value="rejected">{{ __('Rejected') }}</option>
              <option value="cancelled">{{ __('Cancelled') }}</option>
              <option value="withdrawn">{{ __('Withdrawn') }}</option>
            </select>
          </div>
        </div>

        <!-- Decision Node Settings -->
        <div v-else-if="node.data?.nodeType === 'DecisionNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Data Source') }}
            </label>
            <select
              v-model="localConfig.dataSource"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="application">{{ __('Application Data') }}</option>
              <option value="applicant">{{ __('Applicant Profile') }}</option>
              <option value="product">{{ __('Product Type') }}</option>
              <option value="risk">{{ __('Risk Assessment') }}</option>
              <option value="scoring">{{ __('Scoring Metrics') }}</option>
              <option value="external">{{ __('External APIs') }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Expression / Formula') }}
            </label>
            <input
              v-model="localConfig.expression"
              type="text"
              placeholder="e.g. amount > 5000000000"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text mb-3"
              @input="updateConfig"
            />
          </div>
          
          <!-- Visual Condition Builder -->
          <div>
            <ConditionBuilder
              v-model="localConfig.conditions"
              :label="__('Branch Rules')"
              @changed="updateConfig"
            />
          </div>
        </div>

        <!-- Skip Node Settings -->
        <div v-else-if="node.data?.nodeType === 'SkipNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Skip Reason') }}
            </label>
            <input
              v-model="localConfig.skipReason"
              type="text"
              placeholder="e.g. Pre-Approved Customer"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text mb-3"
              @input="updateConfig"
            />
          </div>
          
          <!-- Visual Skip Condition Builder -->
          <div>
            <ConditionBuilder
              v-model="localConfig.skipConditions"
              :label="__('Skip Conditions')"
              @changed="updateConfig"
            />
          </div>
        </div>

        <!-- Form Node Settings -->
        <div v-else-if="node.data?.nodeType === 'FormNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Form Layout Designer') }}
            </label>
            <Button
              :label="__('Configure Form Layout')"
              variant="solid"
              class="w-full justify-center"
              @click="showFormDesigner = true"
            >
              <template #prefix>
                <LucideFileText class="w-4 h-4" />
              </template>
            </Button>
          </div>
          
          <div class="bg-surface-gray-1 p-2.5 rounded-lg text-[10px] text-crm-muted space-y-1.5 border border-crm-border">
            <div class="flex justify-between">
              <span>{{ __('Sections Configured:') }}</span>
              <span class="font-bold text-gray-700">{{ localConfig.sections?.length || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span>{{ __('Fields Configured:') }}</span>
              <span class="font-bold text-gray-700">{{ localConfig.fields?.length || 0 }}</span>
            </div>
            <div class="flex justify-between">
              <span>{{ __('Available Actions:') }}</span>
              <span class="font-bold text-gray-700">{{ localConfig.availableActions?.length || 0 }}</span>
            </div>
          </div>

          <!-- Slide-over Designer sheet -->
          <FormNodeConfig
            v-if="showFormDesigner"
            v-model="localConfig"
            @update:modelValue="onFormDesignerApply"
            @close="showFormDesigner = false"
          />
        </div>

        <!-- Document Node Settings -->
        <div v-else-if="node.data?.nodeType === 'DocumentNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Document Action') }}
            </label>
            <select
              v-model="localConfig.documentAction"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="upload">{{ __('Upload Document') }}</option>
              <option value="generate">{{ __('Generate from Template') }}</option>
              <option value="review">{{ __('Review and Verification') }}</option>
              <option value="validate">{{ __('Third Party Validation') }}</option>
            </select>
          </div>
        </div>

        <!-- Assignment Node Settings -->
        <div v-else-if="node.data?.nodeType === 'AssignmentNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Assignment Method') }}
            </label>
            <select
              v-model="localConfig.assignmentType"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="role">{{ __('By Role') }}</option>
              <option value="user">{{ __('By Specific User') }}</option>
              <option value="unit">{{ __('By Business Unit') }}</option>
              <option value="branch">{{ __('By Branch Location') }}</option>
              <option value="team">{{ __('By Committee / Team') }}</option>
              <option value="auto">{{ __('Auto Routing Engine') }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Assign To') }}
            </label>
            <input
              v-model="localConfig.assignTo"
              type="text"
              placeholder="e.g. Credit Analyst"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              @input="updateConfig"
            />
          </div>
        </div>

        <!-- Approval Node Settings -->
        <div v-else-if="node.data?.nodeType === 'ApprovalNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Approval Type') }}
            </label>
            <select
              v-model="localConfig.approvalType"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="single">{{ __('Single Approver') }}</option>
              <option value="sequential">{{ __('Sequential Chain') }}</option>
              <option value="parallel">{{ __('Parallel Review') }}</option>
              <option value="and">{{ __('AND Gate (All must)') }}</option>
              <option value="or">{{ __('OR Gate (Any one)') }}</option>
              <option value="n_of_m">{{ __('N of M voting') }}</option>
              <option value="majority">{{ __('Majority Decision') }}</option>
              <option value="weighted">{{ __('Weighted Authority') }}</option>
              <option value="amount_based">{{ __('Amount-based Tiers') }}</option>
            </select>
          </div>

          <!-- Quorum N of M input -->
          <div v-if="localConfig.approvalType === 'n_of_m'" class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('N (Required)') }}
              </label>
              <input
                v-model.number="localConfig.nRequired"
                type="number"
                min="1"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border text-crm-text"
                @input="updateConfig"
              />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('M (Total)') }}
              </label>
              <input
                v-model.number="localConfig.mTotal"
                type="number"
                min="1"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border text-crm-text"
                @input="updateConfig"
              />
            </div>
          </div>

          <!-- Approver List Selector (Users & Roles) -->
          <div v-if="['sequential', 'parallel', 'and', 'or', 'n_of_m', 'majority', 'weighted', 'single'].includes(localConfig.approvalType)" class="space-y-2">
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-0.5">
              {{ __('Configured Approvers') }}
            </label>
            
            <!-- List of current approvers -->
            <div class="flex flex-wrap gap-1.5 p-2 bg-surface-gray-1 border border-crm-border rounded-lg min-h-[40px]">
              <span v-if="!localConfig.approvers?.length" class="text-[10px] text-crm-muted italic m-auto">
                {{ __('No approvers added yet') }}
              </span>
              <div
                v-for="(approver, index) in localConfig.approvers"
                :key="index"
                class="flex items-center gap-1 bg-purple-50 text-purple-700 px-2 py-0.5 rounded text-[10px] font-medium border border-purple-100 animate-fade-in"
              >
                <span>{{ approver.type === 'user' ? '👤' : '🛡️' }}</span>
                <span>{{ approver.value }}</span>
                <button
                  type="button"
                  class="text-purple-400 hover:text-purple-600 font-bold ml-1 transition-colors"
                  @click="removeApprover(index)"
                >
                  ×
                </button>
              </div>
            </div>

            <!-- Add Approver controls -->
            <div class="grid grid-cols-3 gap-1.5">
              <select
                v-model="newApproverType"
                class="col-span-1 px-2 py-1.5 text-xs rounded-lg border border-crm-border text-crm-text bg-white"
              >
                <option value="role">{{ __('Role') }}</option>
                <option value="user">{{ __('User') }}</option>
              </select>
              <select
                v-model="newApproverValue"
                class="col-span-2 px-2 py-1.5 text-xs rounded-lg border border-crm-border text-crm-text bg-white"
              >
                <option value="" disabled>{{ __('Select value...') }}</option>
                <template v-if="newApproverType === 'user'">
                  <option
                    v-for="u in userList.data"
                    :key="u.name"
                    :value="u.name"
                  >
                    {{ u.full_name || u.name }}
                  </option>
                </template>
                <template v-else>
                  <option
                    v-for="r in roleList.data"
                    :key="r.name"
                    :value="r.name"
                  >
                    {{ r.name }}
                  </option>
                </template>
              </select>
            </div>
            <Button
              :label="__('Add Approver')"
              variant="subtle"
              size="sm"
              class="w-full justify-center"
              :disabled="!newApproverValue"
              @click="addApprover"
            />
          </div>

          <!-- Amount-based Tiers Builder -->
          <div v-if="localConfig.approvalType === 'amount_based'" class="space-y-3">
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Amount Tiers (IDR)') }}
            </label>
            <div v-for="(rule, idx) in localConfig.amountRules" :key="idx" class="p-3 bg-surface-gray-1 border border-crm-border rounded-xl space-y-2 relative">
              <button
                type="button"
                class="absolute top-2 right-2 text-red-500 hover:text-red-700 font-semibold text-xs"
                @click="removeAmountRule(idx)"
              >
                ✕
              </button>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span class="text-[10px] text-crm-muted uppercase font-bold">{{ __('Min Amount') }}</span>
                  <input
                    v-model.number="rule.min"
                    type="number"
                    class="w-full px-2 py-1 text-xs rounded border border-crm-border mt-0.5 text-crm-text"
                    @input="updateConfig"
                  />
                </div>
                <div>
                  <span class="text-[10px] text-crm-muted uppercase font-bold">{{ __('Max Amount') }}</span>
                  <input
                    v-model.number="rule.max"
                    type="number"
                    class="w-full px-2 py-1 text-xs rounded border border-crm-border mt-0.5 text-crm-text"
                    @input="updateConfig"
                  />
                </div>
              </div>
              <div>
                <span class="text-[10px] text-crm-muted uppercase font-bold block mb-0.5">{{ __('Approver Role') }}</span>
                <select
                  v-model="rule.approverRole"
                  class="w-full px-2 py-1 text-xs rounded border border-crm-border bg-white text-crm-text"
                  @change="updateConfig"
                >
                  <option
                    v-for="r in roleList.data"
                    :key="r.name"
                    :value="r.name"
                  >
                    {{ r.name }}
                  </option>
                </select>
              </div>
            </div>
            <Button
              :label="__('+ Add Tier')"
              variant="subtle"
              size="sm"
              class="w-full justify-center"
              @click="addAmountRule"
            />
          </div>

          <!-- SLA Timeout Hours -->
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('SLA Timeout (Hours)') }}
            </label>
            <input
              v-model.number="localConfig.timeoutHours"
              type="number"
              min="1"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              @input="updateConfig"
            />
          </div>
        </div>

        <!-- Committee Node Settings -->
        <div v-else-if="node.data?.nodeType === 'CommitteeNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Target Committee') }}
            </label>
            <select
              v-model="localConfig.committee"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="" disabled>{{ __('Select Committee...') }}</option>
              <option value="Credit Committee">{{ __('Credit Committee') }}</option>
              <option value="Risk Committee">{{ __('Risk Committee') }}</option>
              <option value="Executive Board">{{ __('Executive Board') }}</option>
              <option value="ALCO">{{ __('ALCO (Asset-Liability Committee)') }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Quorum Attendance (Min Votes)') }}
            </label>
            <input
              v-model.number="localConfig.quorum"
              type="number"
              min="1"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border text-crm-text"
              @input="updateConfig"
            />
          </div>
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Voting Quorum Majority Rule') }}
            </label>
            <select
              v-model="localConfig.quorumType"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="majority">{{ __('Simple Majority (>50%)') }}</option>
              <option value="unanimous">{{ __('Unanimous Consensus (100%)') }}</option>
              <option value="two_thirds">{{ __('Two-Thirds Majority (66.7%)') }}</option>
              <option value="weighted">{{ __('Weighted Committee Representation') }}</option>
            </select>
          </div>
        </div>

        <!-- Delegation Node Settings -->
        <div v-else-if="node.data?.nodeType === 'DelegationNode'" class="space-y-3">
          <!-- Availability rules -->
          <div class="space-y-2 pb-2 border-b border-gray-100">
            <span class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Availability Validation') }}
            </span>
            <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer">
              <input
                v-model="localConfig.checkAvailability"
                type="checkbox"
                class="rounded text-purple-600 focus:ring-purple-500"
                @change="updateConfig"
              />
              <span>{{ __('Validate User Availability') }}</span>
            </label>
            <label class="flex items-center gap-2 text-xs text-gray-700 cursor-pointer">
              <input
                v-model="localConfig.checkLeave"
                type="checkbox"
                class="rounded text-purple-600 focus:ring-purple-500"
                @change="updateConfig"
              />
              <span>{{ __('Check HR Leave Status') }}</span>
            </label>
          </div>

          <!-- Cascade Max Depth -->
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Max Delegation Depth (1-5)') }}
            </label>
            <input
              v-model.number="localConfig.maxDepth"
              type="number"
              min="1"
              max="5"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border text-crm-text"
              @input="updateConfig"
            />
          </div>

          <!-- Fallback routing -->
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Fallback Routing Type') }}
            </label>
            <select
              v-model="localConfig.fallbackType"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="role">{{ __('Substitute Role') }}</option>
              <option value="hierarchy">{{ __('Direct Supervisor') }}</option>
              <option value="committee">{{ __('Committee Delegation') }}</option>
              <option value="manual">{{ __('Manual Operations Override') }}</option>
            </select>
          </div>
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Fallback Target Role') }}
            </label>
            <select
              v-model="localConfig.fallbackTarget"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="" disabled>{{ __('Select Role...') }}</option>
              <option
                v-for="r in roleList.data"
                :key="r.name"
                :value="r.name"
              >
                {{ r.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- SLA Node Settings -->
        <div v-else-if="node.data?.nodeType === 'SLANode'" class="space-y-3">
          <!-- SLA Visual Summary -->
          <div class="bg-rose-50/60 border border-rose-200/60 rounded-xl p-3 space-y-1.5">
            <div class="flex items-center gap-2 text-rose-700">
              <LucideClock class="h-4 w-4" />
              <span class="text-[10px] font-bold uppercase tracking-wider">{{ __('SLA Timer Configuration') }}</span>
            </div>
            <p class="text-[10px] text-rose-600/80 leading-relaxed">
              {{ __('Configure deadline, warning thresholds, reminder intervals, and escalation rules for this SLA timer node.') }}
            </p>
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('Deadline (Hours)') }}
              </label>
              <input
                v-model.number="localConfig.deadlineHours"
                type="number"
                min="1"
                placeholder="24"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
                @input="updateConfig"
              />
            </div>
            <div>
              <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
                {{ __('Warning (Hours)') }}
              </label>
              <input
                v-model.number="localConfig.warningHours"
                type="number"
                min="1"
                placeholder="4"
                class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
                @input="updateConfig"
              />
            </div>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Reminder Interval (Hours)') }}
            </label>
            <input
              v-model.number="localConfig.reminderIntervalHours"
              type="number"
              min="1"
              placeholder="2"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              @input="updateConfig"
            />
            <p class="text-[10px] text-crm-muted mt-1">{{ __('Sends periodic reminders at this interval before deadline') }}</p>
          </div>

          <div class="border-t border-crm-border pt-3">
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Escalation Action') }}
            </label>
            <select
              v-model="localConfig.escalationAction"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="notify">{{ __('Notify Only') }}</option>
              <option value="reassign">{{ __('Reassign to Target') }}</option>
              <option value="escalate">{{ __('Escalate to Supervisor') }}</option>
            </select>
          </div>

          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Escalation Target') }}
            </label>
            <select
              v-model="localConfig.escalationTarget"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="">{{ __('Select Target Role...') }}</option>
              <option
                v-for="r in roleList.data"
                :key="r.name"
                :value="r.name"
              >
                {{ r.name }}
              </option>
            </select>
          </div>

          <div class="flex items-center gap-2 pt-2 border-t border-crm-border">
            <input
              id="sla-business-hours"
              v-model="localConfig.businessHoursOnly"
              type="checkbox"
              class="rounded border-crm-border text-purple-600 focus:ring-purple-500 h-4 w-4"
              @change="updateConfig"
            />
            <label for="sla-business-hours" class="text-xs font-semibold text-gray-700 select-none cursor-pointer">
              {{ __('Count Business Hours Only') }}
            </label>
          </div>
          <p v-if="localConfig.businessHoursOnly" class="text-[10px] text-crm-muted -mt-1 pl-6">
            {{ __('Weekends and holidays will be excluded from the SLA timer calculation.') }}
          </p>
        </div>

        <!-- Notification Node Settings -->
        <div v-else-if="node.data?.nodeType === 'NotificationNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Notification Subject') }}
            </label>
            <input
              v-model="localConfig.subject"
              type="text"
              placeholder="e.g. Credit Application Submitted"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              @input="updateConfig"
            />
          </div>
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Message Body') }}
            </label>
            <textarea
              v-model="localConfig.message"
              rows="3"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text leading-normal"
              @input="updateConfig"
            ></textarea>
          </div>
        </div>

        <!-- Integration Node Settings -->
        <div v-else-if="node.data?.nodeType === 'IntegrationNode'" class="space-y-3">
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('Endpoint / URL') }}
            </label>
            <input
              v-model="localConfig.endpoint"
              type="text"
              placeholder="e.g. https://api.riskbureau.com/v1"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text"
              @input="updateConfig"
            />
          </div>
          <div>
            <label class="block text-[10px] font-bold text-crm-muted uppercase tracking-wider mb-1">
              {{ __('HTTP Method') }}
            </label>
            <select
              v-model="localConfig.method"
              class="w-full px-3 py-2 text-xs rounded-lg border border-crm-border focus:ring-1 focus:ring-purple-500 focus:border-purple-500 text-crm-text bg-white"
              @change="updateConfig"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions Footer -->
    <div class="p-4 border-t border-crm-border bg-surface-gray-1/20 flex gap-2">
      <button
        class="flex-1 bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-700 py-2 rounded-lg text-xs font-semibold border border-red-200 transition-colors"
        @click="deleteNode"
      >
        {{ __('Delete Node') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button, createListResource } from 'frappe-ui'
import { useNodeDefinitions } from '../composables/useNodeDefinitions'
import ConditionBuilder from './ConditionBuilder.vue'
import FormNodeConfig from './FormNodeConfig.vue'

// Lucide Icons
import LucidePlayCircle from '~icons/lucide/play-circle'
import LucideStopCircle from '~icons/lucide/stop-circle'
import LucideGitBranch from '~icons/lucide/git-branch'
import LucideSkipForward from '~icons/lucide/skip-forward'
import LucideFileText from '~icons/lucide/file-text'
import LucideFolderOpen from '~icons/lucide/folder-open'
import LucideUserPlus from '~icons/lucide/user-plus'
import LucideShieldCheck from '~icons/lucide/shield-check'
import LucideUsers from '~icons/lucide/users'
import LucideUserCheck from '~icons/lucide/user-check'
import LucidePlug from '~icons/lucide/plug'
import LucideBell from '~icons/lucide/bell'
import LucideClock from '~icons/lucide/clock'

const props = defineProps({
  node: { type: Object, required: true },
})

const emit = defineEmits(['update-node', 'delete-node', 'close'])

const { NODE_TYPES, NODE_COLORS } = useNodeDefinitions()

const activeTab = ref('General')

// Approver selectors & list resources
const newApproverType = ref('role')
const newApproverValue = ref('')

const userList = createListResource({
  doctype: 'User',
  fields: ['name', 'full_name'],
  orderBy: 'full_name asc',
  pageLength: 500,
  auto: true
})

const roleList = createListResource({
  doctype: 'Role',
  fields: ['name'],
  orderBy: 'name asc',
  pageLength: 500,
  auto: true
})

function addApprover() {
  if (!newApproverValue.value) return
  if (!localConfig.value.approvers) {
    localConfig.value.approvers = []
  }
  
  // Prevent duplicate additions
  const exists = localConfig.value.approvers.some(
    a => a.type === newApproverType.value && a.value === newApproverValue.value
  )
  if (!exists) {
    localConfig.value.approvers.push({
      type: newApproverType.value,
      value: newApproverValue.value
    })
    updateConfig()
  }
  newApproverValue.value = ''
}

function removeApprover(index) {
  if (localConfig.value.approvers) {
    localConfig.value.approvers.splice(index, 1)
    updateConfig()
  }
}

function addAmountRule() {
  if (!localConfig.value.amountRules) {
    localConfig.value.amountRules = []
  }
  localConfig.value.amountRules.push({
    min: 0,
    max: 1000000000,
    approverRole: 'Sales Manager'
  })
  updateConfig()
}

function removeAmountRule(index) {
  if (localConfig.value.amountRules) {
    localConfig.value.amountRules.splice(index, 1)
    updateConfig()
  }
}

const localLabel = ref('')
const localDescription = ref('')
const localConfig = ref({})

const nodeDef = computed(() => NODE_TYPES[props.node.data?.nodeType])
const colorClasses = computed(() => {
  const colorName = nodeDef.value?.color || 'slate'
  return NODE_COLORS[colorName] || NODE_COLORS.slate
})

const iconMap = {
  StartNode: LucidePlayCircle,
  EndNode: LucideStopCircle,
  DecisionNode: LucideGitBranch,
  SkipNode: LucideSkipForward,
  FormNode: LucideFileText,
  DocumentNode: LucideFolderOpen,
  AssignmentNode: LucideUserPlus,
  ApprovalNode: LucideShieldCheck,
  CommitteeNode: LucideUsers,
  DelegationNode: LucideUserCheck,
  IntegrationNode: LucidePlug,
  NotificationNode: LucideBell,
  SLANode: LucideClock,
}

function getIcon(type) {
  return iconMap[type] || LucidePlayCircle
}

// Watch incoming node and map to local references
watch(
  () => props.node,
  (newNode) => {
    if (newNode) {
      localLabel.value = newNode.data?.label || ''
      localDescription.value = newNode.data?.description || ''
      localConfig.value = newNode.value?.data?.config
        ? JSON.parse(JSON.stringify(newNode.data.config))
        : newNode.data?.config
        ? { ...newNode.data.config }
        : {}
    }
  },
  { immediate: true, deep: true }
)

function updateNode() {
  const updatedNode = {
    ...props.node,
    data: {
      ...props.node.data,
      label: localLabel.value,
      description: localDescription.value,
    },
  }
  emit('update-node', updatedNode)
}

function updateConfig() {
  const updatedNode = {
    ...props.node,
    data: {
      ...props.node.data,
      config: {
        ...props.node.data.config,
        ...localConfig.value,
      },
    },
  }
  emit('update-node', updatedNode)
}

const showFormDesigner = ref(false)

function onFormDesignerApply(newVal) {
  localConfig.value = newVal
  updateConfig()
}

function deleteNode() {
  emit('delete-node', props.node.id)
}

function closePanel() {
  emit('close')
}
</script>
