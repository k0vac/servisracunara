<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const navItems = [
  { label: 'Cases', to: '/cases', disabled: false },
  { label: 'Inventory', to: '/inventory', disabled: true },
  { label: 'Invoices', to: '/invoices', disabled: true },
]

const pageTitle = computed(() => {
  if (route.path.startsWith('/cases')) {
    return 'Cases'
  }

  return 'Dashboard'
})

async function handleLogout() {
  await auth.logout()
  await router.push('/login')
}
</script>

<template>
  <div class="dashboard">
    <aside class="sidebar">
      <div class="sidebar__brand">
        <span class="sidebar__logo">VS</span>
        <div>
          <strong>Velja Servis</strong>
        </div>
      </div>

      <nav class="sidebar__nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.disabled ? route.path : item.to"
          class="sidebar__link"
          :class="{
            'sidebar__link--active': route.path.startsWith(item.to),
            'sidebar__link--disabled': item.disabled,
          }"
          @click="item.disabled && $event.preventDefault()"
        >
          {{ item.label }}
          <span v-if="item.disabled" class="sidebar__soon">Soon</span>
        </RouterLink>
      </nav>

      <div class="sidebar__footer">
        <div class="sidebar__user">
          <span class="sidebar__avatar">{{ auth.user?.username.slice(0, 1).toUpperCase() }}</span>
          <div>
            <strong>{{ auth.user?.username }}</strong>
            <span>{{ auth.user?.role }}</span>
          </div>
        </div>
        <button type="button" class="sidebar__logout" @click="handleLogout">Log out</button>
      </div>
    </aside>

    <div class="workspace">
      <header class="workspace__header">
        <div>
          <p class="workspace__eyebrow">Internal portal</p>
          <h2>{{ pageTitle }}</h2>
        </div>
      </header>

      <main class="workspace__content">
        <div v-if="auth.notifications.length" class="notification-banner">
          <p v-for="(message, index) in auth.notifications" :key="index">{{ message }}</p>
          <button type="button" @click="auth.clearNotifications()">Dismiss</button>
        </div>

        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  min-height: 100vh;
  background: var(--color-background);
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.25rem;
  background: #111827;
  color: #e5e7eb;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.sidebar__brand strong {
  display: block;
  color: white;
}

.sidebar__brand span {
  font-size: 0.82rem;
  color: #9ca3af;
}

.sidebar__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  background: #2563eb;
  color: white;
  font-weight: 700;
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.sidebar__link {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0.85rem;
  border-radius: 0.75rem;
  color: #d1d5db;
  text-decoration: none;
}

.sidebar__link:hover {
  background: rgba(255, 255, 255, 0.06);
}

.sidebar__link--active {
  background: rgba(37, 99, 235, 0.18);
  color: white;
}

.sidebar__link--disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.sidebar__soon {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #9ca3af;
}

.sidebar__footer {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-top: auto;
}

.sidebar__user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sidebar__avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: white;
  font-weight: 700;
}

.sidebar__user span {
  display: block;
  font-size: 0.78rem;
  color: #9ca3af;
  text-transform: capitalize;
}

.sidebar__logout {
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: transparent;
  color: #e5e7eb;
  border-radius: 0.75rem;
  padding: 0.65rem 0.85rem;
  cursor: pointer;
}

.sidebar__logout:hover {
  background: rgba(255, 255, 255, 0.06);
}

.workspace {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.workspace__header {
  padding: 1.5rem 1.75rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.workspace__eyebrow {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

.workspace__header h2 {
  font-size: 1.35rem;
  color: var(--color-heading);
}

.workspace__content {
  padding: 1.5rem 1.75rem 2rem;
}

.notification-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.85rem 1rem;
  border-radius: 0.75rem;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: #1d4ed8;
}

.notification-banner button {
  border: none;
  background: white;
  color: #1d4ed8;
  border-radius: 0.5rem;
  padding: 0.45rem 0.75rem;
  cursor: pointer;
}

@media (max-width: 900px) {
  .dashboard {
    grid-template-columns: 1fr;
  }

  .sidebar {
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }
}
</style>
