import { createRouter, createWebHistory } from 'vue-router'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import { viewsStore } from '@/stores/views'
import { mobileFeatures } from '@/data/mobileFeatures'

const handleMobileView = (componentName) => {
  return window.innerWidth < 768 ? `Mobile${componentName}` : componentName
}

const requiresCrmRole = (route) => {
  if (route.path.startsWith('/crm-core')) return true
  
  const flatCrmRoutes = [
    'Leads', 'Lead', 'Deals', 'Deal', 'Contacts', 'Contact',
    'Organizations', 'Organization', 'Notes', 'Tasks', 'Calendar', 'Call Logs', 'AI Agent Center',
    'Lead Tags', 'Lead Aging Report', 'Lead Referrals', 'Lead Campaigns', 'Lead Scoring Rules', 'Lead Web Forms'
  ]
  if (flatCrmRoutes.includes(route.name)) return true
  
  return false
}

const routes = [
  {
    path: '/',
    name: 'CRM Dispatcher',
  },
  {
    path: '/notifications',
    name: 'Notifications',
    redirect: { name: 'Notification Center' },
  },
  // ─── CRM Core ────────────────────────────────────────────
  {
    path: '/crm-core',
    children: [
      {
        path: '',
        redirect: { name: 'CRM Core Dashboard' },
      },
      {
        path: 'dashboard',
        name: 'CRM Core Dashboard',
        component: () => import('@/pages/ExecutiveDashboard.vue'),
      },
      {
        path: 'executive-dashboard',
        redirect: { name: 'CRM Core Dashboard' },
      },
      {
        path: 'insights-dashboard',
        name: 'SUMMON Insights Dashboard',
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'Dashboard',
          subtitle: 'Insights',
          icon: 'bar-chart-2',
          sourcePath: '/insights/dashboards',
        },
      },
      {
        path: 'customer-360',
        name: 'Customer 360',
        component: () => import('@/pages/Customer360List.vue'),
      },
      {
        path: 'customer-360/:customer',
        name: 'Customer 360 Detail',
        component: () => import('@/pages/Customer360.vue'),
        props: true,
      },
      {
        path: 'credit-analysis',
        name: 'Credit Analysis',
        component: () => import('@/pages/CreditAnalysisList.vue'),
      },
      {
        path: 'credit-analysis/:applicationId',
        name: 'Credit Analysis Detail',
        component: () => import('@/pages/CreditAnalysis.vue'),
        props: true,
      },
      {
        alias: 'leads',
        path: 'leads/view/:viewType?',
        name: 'Leads',
        component: () => import('@/pages/Leads.vue'),
      },
      {
        path: 'lead-ops',
        name: 'Lead Ops',
        redirect: '/crm-core/leads/view/lead-ops',
      },
      {
        path: 'leads/tags',
        name: 'Lead Tags',
        component: () => import('@/pages/LeadTags.vue'),
      },
      {
        path: 'leads/aging',
        name: 'Lead Aging Report',
        component: () => import('@/pages/LeadAgingReport.vue'),
      },
      {
        path: 'leads/referrals',
        name: 'Lead Referrals',
        component: () => import('@/pages/LeadReferralLeaderboard.vue'),
      },
      {
        path: 'leads/campaigns',
        name: 'Lead Campaigns',
        component: () => import('@/pages/LeadCampaigns.vue'),
      },
      {
        path: 'leads/scoring',
        name: 'Lead Scoring Rules',
        component: () => import('@/pages/LeadScoringRules.vue'),
      },
      {
        path: 'leads/webforms',
        name: 'Lead Web Forms',
        component: () => import('@/pages/LeadWebForms.vue'),
      },
      {
        path: 'leads/:leadId',
        name: 'Lead',
        component: () => import(`@/pages/${handleMobileView('Lead')}.vue`),
        props: true,
      },
      {
        alias: 'deals',
        path: 'deals/view/:viewType?',
        name: 'Deals',
        component: () => import('@/pages/Deals.vue'),
      },
      {
        path: 'deals/:dealId',
        name: 'Deal',
        component: () => import(`@/pages/${handleMobileView('Deal')}.vue`),
        props: true,
      },
      {
        alias: 'contacts',
        path: 'contacts/view/:viewType?',
        name: 'Contacts',
        component: () => import('@/pages/Contacts.vue'),
      },
      {
        path: 'contacts/:contactId',
        name: 'Contact',
        component: () => import(`@/pages/${handleMobileView('Contact')}.vue`),
        props: true,
      },
      {
        alias: 'organizations',
        path: 'organizations/view/:viewType?',
        name: 'Organizations',
        component: () => import('@/pages/Organizations.vue'),
      },
      {
        path: 'organizations/:organizationId',
        name: 'Organization',
        component: () =>
          import(`@/pages/${handleMobileView('Organization')}.vue`),
        props: true,
      },
      {
        alias: 'notes',
        path: 'notes/view/:viewType?',
        name: 'Notes',
        component: () => import('@/pages/Notes.vue'),
      },
      {
        alias: 'tasks',
        path: 'tasks/view/:viewType?',
        name: 'Tasks',
        component: () => import('@/pages/Tasks.vue'),
      },
      {
        path: 'calendar',
        name: 'Calendar',
        component: () => import('@/pages/Calendar.vue'),
      },
      {
        alias: 'call-logs',
        path: 'call-logs/view/:viewType?',
        name: 'Call Logs',
        component: () => import('@/pages/CallLogs.vue'),
      },
      {
        path: 'ai-desk',
        redirect: { name: 'AI Agent Center' },
      },
      {
        path: 'ai-agent-center',
        name: 'AI Agent Center',
        alias: 'ai-agent',
        component: () => import('@/pages/AIAgentCenter.vue'),
      },
    ],
  },
  // ─── Lending & Risk ──────────────────────────────────────
  {
    path: '/lending-risk',
    children: [
      {
        path: '',
        redirect: { name: 'Loan Origination System' },
      },
      {
        path: 'loan-origination-system',
        name: 'Loan Origination System',
        component: () => import('@/pages/LoanOrigination.vue'),
      },
      {
        path: 'loan-origination-system/:id',
        name: 'Loan Application',
        component: () => import('@/pages/LoanOrigination.vue'),
      },
      {
        path: 'portfolio-monitoring',
        name: 'Portfolio Monitoring',
        component: () => import('@/pages/PortfolioMonitoring.vue'),
      },
      {
        path: 'product-configuration',
        name: 'Product Configuration',
        component: () => import('@/pages/ProductConfiguration.vue'),
      },
      {
        path: 'covenant-monitoring',
        name: 'Covenant Monitoring',
        component: () => import('@/pages/CovenantMonitoring.vue'),
      },
      {
        path: 'collections',
        name: 'Collections',
        component: () => import('@/pages/Collections.vue'),
      },
      {
        path: 'committee-approval',
        name: 'Committee Approval',
        component: () => import('@/pages/CommitteeApproval.vue'),
      },
      {
        path: 'covenant-monitoring',
        name: 'Covenant Monitoring',
        component: () => import('@/pages/CovenantMonitoring.vue'),
      },
      // ─── Workflow Engine ───────────────────────────────────
      {
        path: 'workflow-engine',
        name: 'Workflow List',
        component: () =>
          import('@/modules/workflow-engine/pages/WorkflowList.vue'),
      },
      {
        path: 'workflow-engine/marketplace',
        name: 'Workflow Marketplace',
        component: () =>
          import('@/modules/workflow-engine/pages/WorkflowMarketplace.vue'),
      },
      {
        path: 'workflow-engine/new',
        name: 'Workflow New',
        component: () =>
          import('@/modules/workflow-engine/pages/WorkflowDesigner.vue'),
      },
      {
        path: 'workflow-engine/:flowId',
        name: 'Workflow Detail',
        component: () =>
          import('@/modules/workflow-engine/pages/WorkflowDesigner.vue'),
        props: true,
      },
      {
        path: 'workflow-engine/:flowId/monitor',
        name: 'Workflow Monitor',
        component: () =>
          import('@/modules/workflow-engine/pages/WorkflowMonitor.vue'),
        props: true,
      },
      // Legacy redirect
      {
        path: 'credit-flow-designer/:pathMatch(.*)*',
        redirect: to => {
          const sub = to.params.pathMatch ? '/' + (Array.isArray(to.params.pathMatch) ? to.params.pathMatch.join('/') : to.params.pathMatch) : ''
          return `/lending-risk/workflow-engine${sub}`
        },
      },
    ],
  },
  // ─── Operations ──────────────────────────────────────────
  {
    path: '/operations',
    children: [
      {
        path: '',
        redirect: { name: 'Document Management' },
      },
      {
        path: 'document-management',
        name: 'Document Management',
        component: () => import('@/pages/DocumentManagement.vue'),
      },
      {
        path: 'partner-vendor-management',
        name: 'Partner & Vendor Management',
        component: () => import('@/pages/PartnerVendorManagement.vue'),
      },
      {
        path: 'notification-center',
        name: 'Notification Center',
        component: () => import('@/pages/NotificationCenter.vue'),
      },
      {
        path: 'drive/:pathMatch(.*)*',
        redirect: { name: 'Document Management' },
      },
    ],
  },
  // ─── Admin & Platform ────────────────────────────────────
  {
    path: '/admin-platform',
    children: [
      {
        path: '',
        redirect: { name: 'Reporting & BI' },
      },
      {
        path: 'workflow-engine',
        redirect: { name: 'Workflow List' },
      },
      {
        path: 'workflow',
        redirect: { name: 'Workflow List' },
      },
      {
        path: 'reporting-bi',
        name: 'Reporting & BI',
        component: () => import('@/pages/ReportingBI.vue'),
      },
      {
        path: 'api-integration-center',
        name: 'API & Integration Center',
        component: () => import('@/pages/APIIntegrationCenter.vue'),
      },
      {
        path: 'rules-engine',
        name: 'Rules Engine',
        component: () => import('@/modules/admin/pages/RulesEngine.vue'),
      },
      {
        path: 'rules-engine/:ruleId',
        name: 'Rule Detail',
        component: () => import('@/modules/admin/pages/RulesEngine.vue'),
        props: true,
      },
      // RBAC Routes
      {
        path: 'rbac',
        name: 'RBAC Admin',
        component: () => import('@/modules/rbac/pages/RBACAdmin.vue'),
      },
      {
        path: 'users',
        name: 'User List',
        component: () => import('@/modules/rbac/pages/UserList.vue'),
      },
      {
        path: 'users/:userId',
        name: 'User Detail',
        component: () => import('@/modules/rbac/pages/UserDetail.vue'),
        props: true,
      },
      {
        path: 'roles',
        name: 'Role List',
        component: () => import('@/modules/rbac/pages/RoleList.vue'),
      },
      {
        path: 'role-permissions',
        name: 'Role Permissions',
        component: () => import('@/modules/rbac/pages/RolePermissionManager.vue'),
      },
      {
        path: 'user-permissions',
        name: 'User Permissions',
        component: () => import('@/modules/rbac/pages/UserPermissions.vue'),
      },
      {
        path: 'branches',
        name: 'RBAC Branches',
        component: () => import('@/modules/rbac/pages/BranchManagement.vue'),
      },
      {
        path: 'approval-matrix',
        name: 'RBAC Approval Matrix',
        component: () => import('@/modules/rbac/pages/ApprovalMatrix.vue'),
      },
      {
        path: 'field-permissions',
        name: 'RBAC Field Permissions',
        component: () => import('@/modules/rbac/pages/FieldPermissions.vue'),
      },
      {
        path: 'delegations',
        name: 'RBAC Delegations',
        component: () => import('@/modules/rbac/pages/Delegations.vue'),
      },
      {
        path: 'sod-rules',
        name: 'RBAC SoD',
        component: () => import('@/modules/rbac/pages/SoDRules.vue'),
      },
      {
        path: 'jit-requests',
        name: 'RBAC JIT',
        component: () => import('@/modules/rbac/pages/JITRequests.vue'),
      },
      {
        path: 'audit-trail',
        name: 'Audit Trail',
        component: () => import('@/modules/admin/pages/AuditTrail.vue'),
      },
    ],
  },
  // ─── Channels & Portal ───────────────────────────────────
  {
    path: '/channels-portal',
    children: [
      {
        path: '',
        redirect: { name: 'Omnichannel Workspace' },
      },
      {
        path: 'omnichannel-workspace',
        name: 'Omnichannel Workspace',
        component: () => import('@/pages/OmnichannelWorkspace.vue'),
      },
      {
        path: 'customer-portal',
        name: 'Customer Portal',
        component: () => import('@/pages/CustomerPortalFrame.vue'),
      },
    ],
  },
  // ─── Mobile PWA Routes ──────────────────────────────────
  {
    path: '/mobile',
    children: [
      {
        path: '',
        redirect: { name: 'Mobile Home Dashboard' },
      },
      ...mobileFeatures.map((f) => {
        if (f.routeName === 'Mobile Home Dashboard') {
          return {
            path: 'dashboard',
            name: f.routeName,
            component: () => import('@/pages/MobileHomeDashboard.vue'),
          }
        }
        if (f.routeName === 'My Customers Mobile') {
          return {
            path: 'my-customers',
            name: f.routeName,
            component: () => import('@/pages/MyCustomersMobile.vue'),
          }
        }
        if (f.routeName === 'Customer 360 Mobile') {
          return {
            path: 'customer-360/:customer?',
            name: f.routeName,
            component: () => import('@/pages/Customer360.vue'),
            props: true,
          }
        }
        if (f.routeName === 'Mobile Login & Biometric') {
          return {
            path: 'security',
            name: f.routeName,
            component: () => import('@/pages/MobileLoginBiometric.vue'),
          }
        }
        if (f.routeName === 'Mobile Lead Capture') {
          return {
            path: 'lead-capture',
            name: f.routeName,
            component: () => import('@/pages/MobileLeadCapture.vue'),
          }
        }
        if (f.routeName === 'Document Scanner') {
          return {
            path: 'document-scanner',
            name: f.routeName,
            component: () => import('@/pages/DocumentScanner.vue'),
          }
        }
        if (f.routeName === 'Visit Planner & Route') {
          return {
            path: 'visit-planner',
            name: f.routeName,
            component: () => import('@/pages/VisitPlannerRoute.vue'),
          }
        }
        if (f.routeName === 'Visit Check-In/Out GPS') {
          return {
            path: 'visit-checkin',
            name: f.routeName,
            component: () => import('@/pages/VisitCheckInGPS.vue'),
          }
        }
        if (f.routeName === 'Visit Report Capture') {
          return {
            path: 'visit-report',
            name: f.routeName,
            component: () => import('@/pages/VisitReportCapture.vue'),
          }
        }
        if (f.routeName === 'Mobile Application Submit') {
          return {
            path: 'application-submit',
            name: f.routeName,
            component: () => import('@/pages/MobileApplicationSubmit.vue'),
          }
        }
        if (f.routeName === 'Mobile Approval') {
          return {
            path: 'approval',
            name: f.routeName,
            component: () => import('@/pages/MobileApproval.vue'),
          }
        }
        if (f.routeName === 'Mobile Push Notifications') {
          return {
            path: 'notifications',
            name: f.routeName,
            component: () => import('@/pages/MobilePushNotifications.vue'),
          }
        }
        if (f.routeName === 'Mobile Omnichannel Chat') {
          return {
            path: 'omnichannel',
            name: f.routeName,
            component: () => import('@/pages/MobileOmnichannelChat.vue'),
          }
        }
        if (f.routeName === 'Mobile Calculator Pricing') {
          return {
            path: 'calculator-pricing',
            name: f.routeName,
            component: () => import('@/pages/MobileCalculatorPricing.vue'),
          }
        }
        if (f.routeName === 'Offline Mode & Sync') {
          return {
            path: 'offline-sync',
            name: f.routeName,
            component: () => import('@/pages/OfflineModeSync.vue'),
          }
        }
        if (f.routeName === 'Quick Actions FAB') {
          return {
            path: 'quick-actions',
            name: f.routeName,
            component: () => import('@/pages/QuickActionsFAB.vue'),
          }
        }
        if (f.routeName === 'Voice Commands') {
          return {
            path: 'voice-commands',
            name: f.routeName,
            component: () => import('@/pages/VoiceCommands.vue'),
          }
        }
        if (f.routeName === 'Camera Business Card Scan') {
          return {
            path: 'business-card-scan',
            name: f.routeName,
            component: () => import('@/pages/CameraBusinessCardScan.vue'),
          }
        }
        if (f.routeName === 'AI Assistant Mobile') {
          return {
            path: 'ai-assistant',
            name: f.routeName,
            component: () => import('@/pages/AIAssistantMobile.vue'),
          }
        }
        if (f.routeName === 'Geo-Fence Reminders') {
          return {
            path: 'geo-fence',
            name: f.routeName,
            component: () => import('@/pages/GeoFenceReminders.vue'),
          }
        }
        if (f.routeName === 'Mobile Expense & Mileage') {
          return {
            path: 'expense-mileage',
            name: f.routeName,
            component: () => import('@/pages/MobileExpenseMileage.vue'),
          }
        }
        return {
          path: f.routeName
            .replace(/([a-z])([A-Z])/g, '$1-$2')
            .replace(/\s+/g, '-')
            .toLowerCase(),
          name: f.routeName,
          component: () => import('@/pages/MobilePlaceholderPage.vue'),
          meta: {
            featureTitle: f.label,
            featureIcon: f.icon,
            featureDescription: f.description,
          },
        }
      }),
    ],
  },

  // ─── Shared / Utility Routes ─────────────────────────────
  {
    path: '/customer-portal/auth',
    name: 'Customer Portal Auth',
    component: () => import('@/pages/CustomerPortalAuth.vue'),
    meta: { standalone: true },
  },
  {
    path: '/customer-portal',
    name: 'Customer Portal Web',
    component: () => import('@/pages/CustomerPortal.vue'),
    meta: { standalone: true },
    beforeEnter: (to, from, next) => {
      if (!localStorage.getItem('crm:portal:session')) {
        next({ name: 'Customer Portal Auth' })
      } else {
        next()
      }
    },
  },
  {
    path: '/data-import',
    name: 'DataImportList',
    component: () => import('@/pages/DataImport.vue'),
  },
  {
    path: '/data-import/doctype/:doctype',
    name: 'NewDataImport',
    component: () => import('@/pages/DataImport.vue'),
    props: true,
  },
  {
    path: '/data-import/:importName',
    name: 'DataImport',
    component: () => import('@/pages/DataImport.vue'),
    props: true,
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: () => import('@/pages/Welcome.vue'),
  },
  {
    path: '/modules/committee-approval',
    name: 'Committee Approval',
    component: () => import('@/pages/CommitteeApproval.vue'),
  },
  {
    path: '/modules/:moduleSlug',
    name: 'Summon Module',
    component: () => import('@/pages/SummonModulePlaceholder.vue'),
    props: true,
  },
  // Legacy redirect: /dashboard → /crm-core/dashboard
  {
    path: '/dashboard',
    redirect: { name: 'CRM Core Dashboard' },
  },
  // Legacy redirects for old flat routes
  { path: '/leads', redirect: '/crm-core/leads' },
  { path: '/leads/view/:viewType?', redirect: (to) => ({ path: `/crm-core/leads/view/${to.params.viewType || ''}`, query: to.query }) },
  { path: '/deals', redirect: '/crm-core/deals' },
  { path: '/deals/view/:viewType?', redirect: (to) => ({ path: `/crm-core/deals/view/${to.params.viewType || ''}`, query: to.query }) },
  { path: '/contacts', redirect: '/crm-core/contacts' },
  { path: '/organizations', redirect: '/crm-core/organizations' },
  { path: '/notes', redirect: '/crm-core/notes' },
  { path: '/tasks', redirect: '/crm-core/tasks' },
  { path: '/calendar', redirect: '/crm-core/calendar' },
  { path: '/call-logs', redirect: '/crm-core/call-logs' },
  { path: '/ai-desk', redirect: '/crm-core/ai-agent-center' },
  { path: '/ai-agent-center', redirect: '/crm-core/ai-agent-center' },
  // Drive legacy CRM redirects now land on the iframe-based Document Management page.
  { path: '/drive', redirect: '/operations/document-management' },
  { path: '/drive/:pathMatch(.*)*', redirect: '/operations/document-management' },
  {
    path: '/not-permitted',
    name: 'Not Permitted',
    component: () => import('@/pages/NotPermitted.vue'),
  },
  {
    path: '/:invalidpath(.*)',
    name: 'Invalid Page',
    component: () => import('@/pages/InvalidPage.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/crm'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  router.previousRoute = from

  const session = sessionStore()
  const loggedIn = session.isLoggedIn
  const { users, isCrmUser } = usersStore()

  if (loggedIn && !users.fetched) {
    try {
      await users.promise
    } catch (error) {
      console.error('Error loading users', error)
      // If user API failed (e.g., bench not running), don't block navigation
      // Just proceed to the requested page
      next()
      return
    }
  }

  if (to.name === 'Not Permitted') {
    next()
  } else if (loggedIn && users.fetched && !isCrmUser() && requiresCrmRole(to)) {
    next({ name: 'Not Permitted' })
  } else if (to.name === 'CRM Dispatcher' && loggedIn) {
    if (window.matchMedia('(display-mode: standalone)').matches) {
      next({ name: 'Mobile Home Dashboard' })
      return
    }
    const { views, getDefaultView } = viewsStore()
    await views.promise

    let defaultView = getDefaultView()
    if (!defaultView) {
      if (!isCrmUser()) {
        next({ name: 'Not Permitted' })
      } else {
        next({ name: 'CRM Core Dashboard' })
      }
      return
    }

    let { route_name, type, name, is_standard } = defaultView
    route_name = route_name || 'CRM Core Dashboard'

    if (name && !is_standard) {
      next({
        name: route_name,
        params: { viewType: type },
        query: { view: name },
      })
    } else {
      next({ name: route_name, params: { viewType: type } })
    }
  } else if (!loggedIn) {
    window.location.href = `/login?redirect-to=${encodeURIComponent(`/crm${to.fullPath}`)}`
    next(false)
  } else if (to.matched.length === 0) {
    next({ name: 'Invalid Page' })
  } else if (['Deal', 'Lead'].includes(to.name) && !to.hash) {
    let storageKey = to.name === 'Deal' ? 'lastDealTab' : 'lastLeadTab'
    const activeTab = localStorage.getItem(storageKey) || 'activity'
    const hash = '#' + activeTab
    next({ ...to, hash })
  } else if (
    [
      'Leads',
      'Deals',
      'Contacts',
      'Organizations',
      'Notes',
      'Tasks',
      'Call Logs',
    ].includes(to.name) &&
    !to.query?.view
  ) {
    const viewsStoreInstance = viewsStore()
    const { views, getDefaultView } = viewsStoreInstance
    await views.promise

    const viewType = to.params?.viewType ?? ''
    const standardViewTypes = ['list', 'kanban', 'group_by', 'calendar', 'timeline', 'lead-ops']

    if (!viewType) {
      const doctypeMap = {
        Leads: 'CRM Lead',
        Deals: 'CRM Deal',
        Contacts: 'Contact',
        Organizations: 'CRM Organization',
        Notes: 'FCRM Note',
        Tasks: 'CRM Task',
        'Call Logs': 'CRM Call Log',
      }

      const doctype = doctypeMap[to.name]
      let defaultViewType = 'list'

      let globalDefault = getDefaultView()
      if (globalDefault && globalDefault.route_name === to.name) {
        defaultViewType = globalDefault.type || 'list'
        if (globalDefault.name && !globalDefault.is_standard) {
          next({
            name: to.name,
            params: { viewType: defaultViewType },
            query: { ...to.query, view: globalDefault.name },
          })
          return
        }
      }

      for (const viewType of standardViewTypes) {
        const standardViews = viewsStoreInstance.standardViews
        const standardView = (standardViews?.[doctype + ' ' + viewType]) || (standardViews?.value?.[doctype + ' ' + viewType])
        if (standardView?.is_default) {
          defaultViewType = viewType
          break
        }
      }

      next({
        name: to.name,
        params: { viewType: defaultViewType },
        query: to.query,
      })
    } else if (!standardViewTypes.includes(viewType)) {
      const viewNameOrLabel = viewType

      let view = views.data?.find(
        (v) => v.name == viewNameOrLabel || v.label === viewNameOrLabel,
      )

      if (view) {
        next({
          name: to.name,
          params: { viewType: view.type || 'list' },
          query: { ...to.query, view: view.name },
        })
      } else {
        next({
          name: to.name,
          params: { viewType: 'list' },
          query: to.query,
        })
      }
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
