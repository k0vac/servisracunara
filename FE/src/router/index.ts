import { createRouter, createWebHistory } from 'vue-router'

import DashboardLayout from '@/layouts/DashboardLayout.vue'
import { useAuthStore } from '@/stores/auth'
import CasesView from '@/views/CasesView.vue'
import InventoryView from '@/views/InventoryView.vue'
import InvoicesView from '@/views/InvoicesView.vue'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guestOnly: true },
    },
    {
      path: '/',
      component: DashboardLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/cases',
        },
        {
          path: 'cases',
          name: 'cases',
          component: CasesView,
        },
        {
          path: 'inventory',
          name: 'inventory',
          component: InventoryView,
        },
        {
          path: 'invoices',
          name: 'invoices',
          component: InvoicesView,
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!auth.initialized) {
    await auth.initialize()
  }

  if (to.meta.requiresAuth && !auth.user) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  if (to.meta.guestOnly && auth.user) {
    return { name: 'cases' }
  }

  return true
})

export default router
