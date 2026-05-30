import { ref } from 'vue'
import { defineStore } from 'pinia'

import * as authApi from '@/api/auth'
import { ApiError } from '@/api/client'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const notifications = ref<string[]>([])
  const loading = ref(false)
  const initialized = ref(false)

  async function initialize() {
    loading.value = true

    try {
      user.value = await authApi.fetchCurrentUser()
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 401) {
        throw error
      }
      user.value = null
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  async function login(username: string, password: string) {
    loading.value = true

    try {
      const response = await authApi.login(username, password)
      user.value = response.user
      notifications.value = response.notifications
      return response
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    await authApi.logout()
    user.value = null
    notifications.value = []
  }

  function clearNotifications() {
    notifications.value = []
  }

  return {
    user,
    notifications,
    loading,
    initialized,
    initialize,
    login,
    logout,
    clearNotifications,
  }
})
