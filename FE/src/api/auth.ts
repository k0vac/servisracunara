import { api } from './client'
import type { LoginResponse, User } from '@/types'

export function login(username: string, password: string) {
  return api<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function fetchCurrentUser() {
  return api<User>('/api/auth/me')
}

export function logout() {
  return api<{ message: string }>('/api/auth/logout', {
    method: 'POST',
  })
}
