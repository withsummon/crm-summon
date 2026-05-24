import { createRouter, createWebHistory } from 'vue-router'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'
import { viewsStore } from '@/stores/views'

const handleMobileView = (componentName) => {
  return window.innerWidth < 768 ? `Mobile${componentName}` : componentName
}

const requiresCrmRole = (route) => {
  if (route.path.startsWith('/crm-core')) return true
  
  const flatCrmRoutes = [
    'Leads', 'Lead', 'Deals', 'Deal', 'Contacts', 'Contact',
    'Organizations', 'Organization', 'Notes', 'Tasks', 'Calendar', 'Call Logs', 'AI Desk'
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
        component: () => import('@/pages/CRMCoreDashboard.vue'),
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
        name: 'AI Desk',
        component: () => import('@/pages/AIDesk.vue'),
      },
    ],
  },
  // ─── Lending & Risk ──────────────────────────────────────
  {
    path: '/lending-risk',
    children: [
      {
        path: '',
        redirect: { name: 'Lending Dashboard' },
      },
      {
        path: 'dashboard',
        name: 'Lending Dashboard',
        component: () => import('@/pages/ModuleDashboard.vue'),
        props: { moduleGroup: 'Lending & Risk' },
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
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'Portfolio Monitoring',
          subtitle: 'Insights',
          icon: 'pie-chart',
          sourcePath: '/insights/dashboards',
        },
      },
      {
        path: 'product-configuration',
        name: 'Product Configuration',
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'Product Configuration',
          subtitle: 'Item',
          icon: 'package',
          sourcePath: '/app/item',
        },
      },
      {
        path: 'covenant-monitoring',
        name: 'Covenant Monitoring',
        component: () => import('@/pages/CovenantMonitoring.vue'),
      },
    ],
  },
  // ─── Operations ──────────────────────────────────────────
  {
    path: '/operations',
    children: [
      {
        path: '',
        redirect: { name: 'Operations Dashboard' },
      },
      {
        path: 'dashboard',
        name: 'Operations Dashboard',
        component: () => import('@/pages/ModuleDashboard.vue'),
        props: { moduleGroup: 'Operations' },
      },
      {
        path: 'document-management',
        name: 'Document Management',
        component: () => import('@/pages/DocumentManagement.vue'),
      },
      {
        path: 'partner-vendor-management',
        name: 'Partner & Vendor Management',
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'Partner & Vendor Management',
          subtitle: 'Supplier',
          icon: 'truck',
          sourcePath: '/app/supplier',
        },
      },
      {
        path: 'notification-center',
        name: 'Notification Center',
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'Notification Center',
          subtitle: 'Notification',
          icon: 'bell',
          sourcePath: '/app/notification',
        },
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
        redirect: { name: 'Admin Dashboard' },
      },
      {
        path: 'dashboard',
        name: 'Admin Dashboard',
        component: () => import('@/pages/ModuleDashboard.vue'),
        props: { moduleGroup: 'Admin & Platform' },
      },
      {
        path: 'workflow-engine',
        name: 'Workflow Engine',
        component: () => import('@/modules/admin/pages/WorkflowEngine.vue'),
      },
      {
        path: 'workflow',
        redirect: { name: 'Workflow Engine' },
      },
      {
        path: 'reporting-bi',
        name: 'Reporting & BI',
        component: () => import('@/pages/ReportingBI.vue'),
      },
      {
        path: 'api-integration-center',
        name: 'API & Integration Center',
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'API & Integration Center',
          subtitle: 'Integrations',
          icon: 'link',
          sourcePath: '/app/integrations',
        },
      },
      {
        path: 'rules-engine',
        name: 'Rules Engine',
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'Rules Engine',
          subtitle: 'Assignment Rule',
          icon: 'filter',
          sourcePath: '/app/assignment-rule',
        },
      },
      // RBAC Routes
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
        redirect: { name: 'Channels Dashboard' },
      },
      {
        path: 'dashboard',
        name: 'Channels Dashboard',
        component: () => import('@/pages/ModuleDashboard.vue'),
        props: { moduleGroup: 'Channels & Portal' },
      },
      {
        path: 'omnichannel-communication',
        name: 'Omnichannel Communication',
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'Omnichannel Communication',
          subtitle: 'ClefinCode Chat',
          icon: 'message-square',
          sourcePath: '/app/clefincode-chat-channel',
        },
      },
      {
        path: 'customer-portal',
        name: 'Customer Portal',
        component: () => import('@/pages/EmbeddedAppPage.vue'),
        props: {
          title: 'Customer Portal',
          subtitle: 'Helpdesk',
          icon: 'life-buoy',
          sourcePath: '/helpdesk',
        },
      },
    ],
  },
  // ─── Shared / Utility Routes ─────────────────────────────
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
  { path: '/ai-desk', redirect: '/crm-core/ai-desk' },
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

  const { isLoggedIn } = sessionStore()
  const { users, isCrmUser } = usersStore()

  if (isLoggedIn && !users.fetched) {
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
  } else if (isLoggedIn && users.fetched && !isCrmUser() && requiresCrmRole(to)) {
    next({ name: 'Not Permitted' })
  } else if (to.name === 'CRM Dispatcher' && isLoggedIn) {
    const { views, getDefaultView } = viewsStore()
    await views.promise

    let defaultView = getDefaultView()
    if (!defaultView) {
      if (!isCrmUser()) {
        next({ name: 'Home' })
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
  } else if (!isLoggedIn) {
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
    const { views, standardViews, getDefaultView } = viewsStore()
    await views.promise

    const viewType = to.params?.viewType ?? ''
    const standardViewTypes = ['list', 'kanban', 'group_by']

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
        const standardView = standardViews.value?.[doctype + ' ' + viewType]
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
