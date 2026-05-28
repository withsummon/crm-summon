/**
 * Workflow Node Type Definitions
 *
 * Single source of truth for all 13 node types in the Workflow Designer.
 * Used by WorkflowNodePalette, WorkflowCanvas, WorkflowNodeRenderer, and NodePropertyPanel.
 */

// ─── Color Palette ──────────────────────────────────────────
export const NODE_COLORS = {
  emerald: {
    bg: 'bg-emerald-100',
    text: 'text-emerald-600',
    border: 'border-emerald-300',
    accent: '#059669',
  },
  red: {
    bg: 'bg-red-100',
    text: 'text-red-600',
    border: 'border-red-300',
    accent: '#dc2626',
  },
  amber: {
    bg: 'bg-amber-100',
    text: 'text-amber-600',
    border: 'border-amber-300',
    accent: '#d97706',
  },
  slate: {
    bg: 'bg-slate-100',
    text: 'text-slate-600',
    border: 'border-slate-300',
    accent: '#475569',
  },
  blue: {
    bg: 'bg-blue-100',
    text: 'text-blue-600',
    border: 'border-blue-300',
    accent: '#2563eb',
  },
  violet: {
    bg: 'bg-violet-100',
    text: 'text-violet-600',
    border: 'border-violet-300',
    accent: '#7c3aed',
  },
  cyan: {
    bg: 'bg-cyan-100',
    text: 'text-cyan-600',
    border: 'border-cyan-300',
    accent: '#0891b2',
  },
  green: {
    bg: 'bg-green-100',
    text: 'text-green-600',
    border: 'border-green-300',
    accent: '#16a34a',
  },
  indigo: {
    bg: 'bg-indigo-100',
    text: 'text-indigo-600',
    border: 'border-indigo-300',
    accent: '#4f46e5',
  },
  orange: {
    bg: 'bg-orange-100',
    text: 'text-orange-600',
    border: 'border-orange-300',
    accent: '#ea580c',
  },
  pink: {
    bg: 'bg-pink-100',
    text: 'text-pink-600',
    border: 'border-pink-300',
    accent: '#db2777',
  },
  yellow: {
    bg: 'bg-yellow-100',
    text: 'text-yellow-600',
    border: 'border-yellow-300',
    accent: '#ca8a04',
  },
  rose: {
    bg: 'bg-rose-100',
    text: 'text-rose-600',
    border: 'border-rose-300',
    accent: '#e11d48',
  },
}

// ─── Node Type Definitions ──────────────────────────────────
export const NODE_TYPES = {
  StartNode: {
    type: 'StartNode',
    label: 'Start',
    icon: 'play-circle',
    color: 'emerald',
    category: 'Flow Control',
    description: 'Entry point of Workflow Engine',
    maxInstances: 1,
    handles: {
      inputs: [],
      outputs: [{ id: 'default', label: 'Next', position: '50%' }],
    },
    defaultConfig: {
      triggerType: 'manual', // manual | auto | api
      applicableProducts: [],
      applicablePersonas: [],
    },
  },

  EndNode: {
    type: 'EndNode',
    label: 'End',
    icon: 'stop-circle',
    color: 'red',
    category: 'Flow Control',
    description: 'Terminal node — Approved, Rejected, Cancelled, or Withdrawn',
    maxInstances: null, // multiple end nodes allowed
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [],
    },
    defaultConfig: {
      outcome: 'approved', // approved | rejected | cancelled | withdrawn
      finalActions: [],
      notifications: [],
    },
  },

  DecisionNode: {
    type: 'DecisionNode',
    label: 'Decision',
    icon: 'git-branch',
    color: 'amber',
    category: 'Flow Control',
    description: 'Branch based on business conditions',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [
        { id: 'true', label: 'Yes', position: '30%' },
        { id: 'false', label: 'No', position: '70%' },
      ],
    },
    defaultConfig: {
      conditions: [],
      dataSource: 'application', // application | applicant | product | risk | scoring | external
      expression: '',
    },
  },

  SkipNode: {
    type: 'SkipNode',
    label: 'Skip Gate',
    icon: 'skip-forward',
    color: 'slate',
    category: 'Flow Control',
    description: 'Skip stage based on conditions (pre-approved, etc.)',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [
        { id: 'continue', label: 'Continue', position: '30%' },
        { id: 'skip', label: 'Skip', position: '70%' },
      ],
    },
    defaultConfig: {
      skipConditions: [],
      skipReason: '',
    },
  },

  FormNode: {
    type: 'FormNode',
    label: 'Form Stage',
    icon: 'file-text',
    color: 'blue',
    category: 'Application',
    description: 'Dynamic form with configurable sections, fields, and validation',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [{ id: 'default', label: 'Next', position: '50%' }],
    },
    defaultConfig: {
      formTemplate: '',
      sections: [],
      fields: [],
      validationRules: [],
      defaultValues: {},
      computedValues: {},
      availableActions: ['save_draft', 'submit'],
    },
  },

  DocumentNode: {
    type: 'DocumentNode',
    label: 'Document',
    icon: 'folder-open',
    color: 'violet',
    category: 'Application',
    description: 'Document generation, upload, review, or validation',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [{ id: 'default', label: 'Next', position: '50%' }],
    },
    defaultConfig: {
      documentAction: 'upload', // upload | generate | review | validate
      requiredDocuments: [],
      templates: [],
      validationRules: [],
    },
  },

  AssignmentNode: {
    type: 'AssignmentNode',
    label: 'Assignment',
    icon: 'user-plus',
    color: 'cyan',
    category: 'Approval & Assignment',
    description: 'Assign task to user, role, unit, branch, or team',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [{ id: 'default', label: 'Next', position: '50%' }],
    },
    defaultConfig: {
      assignmentType: 'role', // user | role | unit | branch | team | auto
      assignTo: '',
      assignmentRules: [],
      autoAssignField: '',
    },
  },

  ApprovalNode: {
    type: 'ApprovalNode',
    label: 'Approval',
    icon: 'shield-check',
    color: 'green',
    category: 'Approval & Assignment',
    description: 'Single or multi-level approval with matrix rules',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [
        { id: 'approved', label: 'Approved', position: '25%' },
        { id: 'rejected', label: 'Rejected', position: '50%' },
        { id: 'returned', label: 'Returned', position: '75%' },
      ],
    },
    defaultConfig: {
      approvalType: 'single', // single | sequential | parallel | and | or | n_of_m | quorum | majority | weighted
      approvers: [],
      nRequired: null, // for n_of_m
      mTotal: null, // for n_of_m
      amountRules: [],
      riskRules: [],
      timeoutHours: 48,
      escalationTarget: '',
      availableActions: ['approve', 'reject', 'return'],
    },
  },

  CommitteeNode: {
    type: 'CommitteeNode',
    label: 'Committee',
    icon: 'users',
    color: 'indigo',
    category: 'Approval & Assignment',
    description: 'Committee-based approval with quorum and voting',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [
        { id: 'approved', label: 'Approved', position: '25%' },
        { id: 'rejected', label: 'Rejected', position: '50%' },
        { id: 'deferred', label: 'Deferred', position: '75%' },
      ],
    },
    defaultConfig: {
      committee: '', // link to CRM Committee
      quorumType: 'majority', // majority | unanimous | n_of_m | weighted
      quorumN: null,
      votingMethod: 'majority', // majority | unanimous | weighted
      meetingRequired: false,
      timeoutDays: 7,
    },
  },

  DelegationNode: {
    type: 'DelegationNode',
    label: 'Delegation',
    icon: 'user-check',
    color: 'orange',
    category: 'Approval & Assignment',
    description: 'Check approver availability, delegate or escalate',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [
        { id: 'delegated', label: 'Delegated', position: '25%' },
        { id: 'escalated', label: 'Escalated', position: '50%' },
        { id: 'fallback', label: 'Fallback', position: '75%' },
      ],
    },
    defaultConfig: {
      checkStatuses: ['on_leave', 'resigned', 'inactive', 'suspended'],
      delegationMatrix: [],
      fallbackType: 'role', // role | hierarchy | committee | manual
      fallbackTarget: '',
      maxDelegationDepth: 3,
    },
  },

  IntegrationNode: {
    type: 'IntegrationNode',
    label: 'Integration',
    icon: 'plug',
    color: 'pink',
    category: 'System',
    description: 'Call internal or external APIs/services',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [
        { id: 'success', label: 'Success', position: '35%' },
        { id: 'failure', label: 'Failure', position: '65%' },
      ],
    },
    defaultConfig: {
      integrationType: 'internal', // internal | external | webhook
      endpoint: '',
      method: 'GET',
      headers: {},
      payload: {},
      responseMapping: {},
      retryCount: 3,
      timeoutSeconds: 30,
    },
  },

  NotificationNode: {
    type: 'NotificationNode',
    label: 'Notification',
    icon: 'bell',
    color: 'yellow',
    category: 'System',
    description: 'Send notifications to users, roles, teams, or channels',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [{ id: 'default', label: 'Next', position: '50%' }],
    },
    defaultConfig: {
      channels: ['in_app'], // in_app | email | sms | whatsapp | push
      recipients: [],
      recipientType: 'role', // user | role | team | applicant | assignee
      template: '',
      subject: '',
      message: '',
    },
  },

  SLANode: {
    type: 'SLANode',
    label: 'SLA Timer',
    icon: 'clock',
    color: 'rose',
    category: 'System',
    description: 'Define deadlines, reminders, and escalation rules',
    maxInstances: null,
    handles: {
      inputs: [{ id: 'default', label: 'Input', position: '50%' }],
      outputs: [
        { id: 'on-time', label: 'On Time', position: '25%' },
        { id: 'warning', label: 'Warning', position: '50%' },
        { id: 'breached', label: 'Breached', position: '75%' },
      ],
    },
    defaultConfig: {
      deadlineHours: 24,
      warningHours: 4,
      reminderIntervalHours: 2,
      escalationTarget: '',
      escalationAction: 'notify', // notify | reassign | escalate
      businessHoursOnly: true,
    },
  },
}

// ─── Node Categories (for palette display) ──────────────────
export const NODE_CATEGORIES = [
  {
    name: 'Flow Control',
    icon: 'route',
    nodes: ['StartNode', 'EndNode', 'DecisionNode', 'SkipNode'],
  },
  {
    name: 'Application',
    icon: 'file-text',
    nodes: ['FormNode', 'DocumentNode'],
  },
  {
    name: 'Approval & Assignment',
    icon: 'shield-check',
    nodes: ['AssignmentNode', 'ApprovalNode', 'CommitteeNode', 'DelegationNode'],
  },
  {
    name: 'System',
    icon: 'cpu',
    nodes: ['IntegrationNode', 'NotificationNode', 'SLANode'],
  },
]

// ─── Helper Functions ───────────────────────────────────────

/**
 * Get node type definition by type key
 */
export function getNodeType(type) {
  return NODE_TYPES[type] || null
}

/**
 * Get color classes for a node type
 */
export function getNodeColors(type) {
  const nodeDef = NODE_TYPES[type]
  if (!nodeDef) return NODE_COLORS.slate
  return NODE_COLORS[nodeDef.color] || NODE_COLORS.slate
}

/**
 * Get output handles for a node type
 */
export function getNodeOutputHandles(type) {
  const nodeDef = NODE_TYPES[type]
  if (!nodeDef) return [{ id: 'default', label: 'Next', position: '50%' }]
  return nodeDef.handles.outputs
}

/**
 * Get input handles for a node type
 */
export function getNodeInputHandles(type) {
  const nodeDef = NODE_TYPES[type]
  if (!nodeDef) return [{ id: 'default', label: 'Input', position: '50%' }]
  return nodeDef.handles.inputs
}

/**
 * Get default config for a node type
 */
export function getDefaultNodeConfig(type) {
  const nodeDef = NODE_TYPES[type]
  if (!nodeDef) return {}
  return JSON.parse(JSON.stringify(nodeDef.defaultConfig))
}

/**
 * Get all node types in a category
 */
export function getNodesByCategory(categoryName) {
  const category = NODE_CATEGORIES.find((c) => c.name === categoryName)
  if (!category) return []
  return category.nodes.map((type) => NODE_TYPES[type]).filter(Boolean)
}

/**
 * Available actions that can be configured per node
 */
export const AVAILABLE_ACTIONS = [
  { id: 'save_draft', label: 'Save Draft', icon: 'save', group: 'general' },
  { id: 'submit', label: 'Submit', icon: 'send', group: 'general' },
  { id: 'continue', label: 'Continue', icon: 'arrow-right', group: 'general' },
  { id: 'approve', label: 'Approve', icon: 'check-circle', group: 'approval' },
  { id: 'reject', label: 'Reject', icon: 'x-circle', group: 'approval' },
  { id: 'return', label: 'Return', icon: 'corner-up-left', group: 'approval' },
  { id: 'return_to_rm', label: 'Return to RM', icon: 'corner-down-left', group: 'approval' },
  { id: 'request_document', label: 'Request Additional Document', icon: 'file-plus', group: 'document' },
  { id: 'send_to_analyst', label: 'Send to Analyst', icon: 'user-plus', group: 'assignment' },
  { id: 'assign_reviewer', label: 'Assign to Reviewer', icon: 'user-check', group: 'assignment' },
  { id: 'generate_document', label: 'Generate Document', icon: 'file-output', group: 'document' },
  { id: 'upload_document', label: 'Upload Document', icon: 'upload', group: 'document' },
  { id: 'validate_data', label: 'Validate Data', icon: 'check-square', group: 'general' },
  { id: 'cancel', label: 'Cancel Application', icon: 'x-square', group: 'terminal' },
  { id: 'withdraw', label: 'Withdraw Application', icon: 'log-out', group: 'terminal' },
  { id: 'escalate', label: 'Escalate', icon: 'trending-up', group: 'assignment' },
  { id: 'delegate', label: 'Delegate', icon: 'share-2', group: 'assignment' },
  { id: 'reassign', label: 'Reassign', icon: 'shuffle', group: 'assignment' },
]

/**
 * Condition data sources that can be used in Decision/Skip nodes
 */
export const CONDITION_DATA_SOURCES = [
  {
    id: 'applicant',
    label: 'Applicant Profile',
    fields: [
      { name: 'applicant_persona', label: 'Applicant Persona', type: 'select', options: ['New Customer', 'Existing Customer'] },
      { name: 'customer_segment', label: 'Customer Segment', type: 'select', options: ['Retail', 'SME', 'Commercial', 'Corporate'] },
      { name: 'customer_status', label: 'Customer Status', type: 'select', options: ['Active', 'Inactive', 'Blacklisted'] },
    ],
  },
  {
    id: 'application',
    label: 'Application Data',
    fields: [
      { name: 'amount', label: 'Credit Amount', type: 'currency' },
      { name: 'product_type', label: 'Product Type', type: 'link', options: 'CRM Product' },
      { name: 'is_pre_approved', label: 'Pre-Approved', type: 'check' },
      { name: 'application_status', label: 'Application Status', type: 'select', options: ['Draft', 'Submitted', 'Under Review', 'Approved', 'Rejected'] },
      { name: 'collateral_required', label: 'Collateral Required', type: 'check' },
    ],
  },
  {
    id: 'risk',
    label: 'Risk Assessment',
    fields: [
      { name: 'risk_grade', label: 'Risk Grade', type: 'select', options: ['Low', 'Medium', 'High', 'Very High'] },
      { name: 'credit_score', label: 'Credit Score', type: 'int' },
      { name: 'dti_ratio', label: 'Debt-to-Income Ratio', type: 'float' },
    ],
  },
  {
    id: 'organization',
    label: 'Organization',
    fields: [
      { name: 'branch', label: 'Branch', type: 'link', options: 'FCRM Branch' },
      { name: 'region', label: 'Region', type: 'data' },
      { name: 'program', label: 'Program', type: 'data' },
    ],
  },
]

/**
 * Condition operators by field type
 */
export const CONDITION_OPERATORS = {
  select: [
    { value: '==', label: 'equals' },
    { value: '!=', label: 'not equals' },
    { value: 'in', label: 'in' },
    { value: 'not_in', label: 'not in' },
  ],
  data: [
    { value: '==', label: 'equals' },
    { value: '!=', label: 'not equals' },
    { value: 'contains', label: 'contains' },
    { value: 'is_empty', label: 'is empty' },
    { value: 'is_not_empty', label: 'is not empty' },
  ],
  currency: [
    { value: '==', label: 'equals' },
    { value: '!=', label: 'not equals' },
    { value: '>', label: 'greater than' },
    { value: '>=', label: 'greater than or equal' },
    { value: '<', label: 'less than' },
    { value: '<=', label: 'less than or equal' },
    { value: 'between', label: 'between' },
  ],
  int: [
    { value: '==', label: 'equals' },
    { value: '!=', label: 'not equals' },
    { value: '>', label: 'greater than' },
    { value: '>=', label: 'greater than or equal' },
    { value: '<', label: 'less than' },
    { value: '<=', label: 'less than or equal' },
  ],
  float: [
    { value: '>', label: 'greater than' },
    { value: '>=', label: 'greater than or equal' },
    { value: '<', label: 'less than' },
    { value: '<=', label: 'less than or equal' },
  ],
  check: [
    { value: '==', label: 'is' },
  ],
  link: [
    { value: '==', label: 'equals' },
    { value: '!=', label: 'not equals' },
    { value: 'in', label: 'in' },
  ],
}
