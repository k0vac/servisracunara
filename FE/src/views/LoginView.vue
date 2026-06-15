<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { ApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref('')

async function handleSubmit() {
  error.value = ''

  try {
    await auth.login(username.value.trim(), password.value)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/cases'
    await router.push(redirect)
  } catch (submitError) {
    if (submitError instanceof ApiError) {
      error.value = submitError.message
      return
    }

    error.value = 'Unable to sign in right now.'
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-card__header">
        <span class="login-card__logo">SR</span>
        <div>
          <h1>Servis Racunara</h1>
          <p>Sign in to manage repair cases.</p>
        </div>
      </div>

      <form class="login-form" @submit.prevent="handleSubmit">
        <label>
          <span>Username</span>
          <input v-model="username" type="text" autocomplete="username" required />
        </label>

        <label>
          <span>Password</span>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>

        <p v-if="error" class="login-form__error">{{ error }}</p>

        <button type="submit" :disabled="auth.loading">
          {{ auth.loading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      <p class="login-card__hint">Default admin: admin / password</p>

      <p class="login-card__public">
        <RouterLink to="/lookup">Track your repair</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background:
    radial-gradient(circle at top, rgba(37, 99, 235, 0.12), transparent 35%),
    var(--color-background);
}

.login-card {
  width: min(100%, 420px);
  padding: 2rem;
  border-radius: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
}

.login-card__header {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.5rem;
}

.login-card__logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 1rem;
  background: #2563eb;
  color: white;
  font-weight: 700;
}

.login-card__header h1 {
  font-size: 1.5rem;
  color: var(--color-heading);
}

.login-card__header p {
  color: var(--color-text-muted);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.login-form label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.login-form label span {
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.login-form input {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.75rem 0.85rem;
  background: var(--color-background);
  color: var(--color-text);
}

.login-form button {
  margin-top: 0.5rem;
  border: none;
  border-radius: 0.75rem;
  padding: 0.8rem 1rem;
  background: #2563eb;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.login-form button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.login-form__error {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  padding: 0.75rem 0.85rem;
}

.login-card__hint {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.login-card__public {
  margin-top: 0.75rem;
  font-size: 0.9rem;
  text-align: center;
}

.login-card__public a {
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
}
</style>
