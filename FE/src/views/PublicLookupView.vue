<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

import { ApiError } from '@/api/client'
import { lookupPublicCase } from '@/api/public'
import CaseStatusBadge from '@/components/cases/CaseStatusBadge.vue'
import type { PublicCase } from '@/types'
import {
  formatDate,
  publicCaseStatusDescriptions,
  publicEventTypeLabels,
} from '@/utils/cases'

const phone = ref('')
const referenceCode = ref('')
const loading = ref(false)
const error = ref('')
const caseResult = ref<PublicCase | null>(null)

async function handleSubmit() {
  loading.value = true
  error.value = ''
  caseResult.value = null

  try {
    caseResult.value = await lookupPublicCase({
      phone: phone.value.trim(),
      reference_code: referenceCode.value.trim().toUpperCase(),
    })
  } catch (submitError) {
    if (submitError instanceof ApiError) {
      error.value = submitError.message
      return
    }

    error.value = 'Unable to look up your case right now.'
  } finally {
    loading.value = false
  }
}

function handleNewLookup() {
  caseResult.value = null
  error.value = ''
}
</script>

<template>
  <div class="lookup-page">
    <div class="lookup-shell">
      <header class="lookup-header">
        <span class="lookup-header__logo">VS</span>
        <div>
          <h1>Track your repair</h1>
          <p>Enter the phone number and reference code from your receipt.</p>
        </div>
      </header>

      <form v-if="!caseResult" class="lookup-form" @submit.prevent="handleSubmit">
        <label>
          <span>Phone number</span>
          <input
            v-model="phone"
            type="tel"
            autocomplete="tel"
            placeholder="e.g. 061 2549393"
            required
          />
        </label>

        <label>
          <span>Reference code</span>
          <input
            v-model="referenceCode"
            type="text"
            autocapitalize="characters"
            spellcheck="false"
            placeholder="e.g. REP-0002"
            required
          />
        </label>

        <p v-if="error" class="lookup-form__error">{{ error }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Looking up...' : 'View case status' }}
        </button>
      </form>

      <section v-else class="case-result">
        <div class="case-result__header">
          <div>
            <div class="case-result__title-row">
              <h2>{{ caseResult.ticket_number }}</h2>
              <CaseStatusBadge :status="caseResult.status" />
            </div>
            <p>{{ caseResult.customer_name }}</p>
          </div>
          <button type="button" class="secondary-button" @click="handleNewLookup">
            Look up another
          </button>
        </div>

        <p class="status-summary">{{ publicCaseStatusDescriptions[caseResult.status] }}</p>

        <dl class="details-grid">
          <div>
            <dt>Device</dt>
            <dd>{{ caseResult.device_type }}</dd>
          </div>
          <div>
            <dt>Brand / model</dt>
            <dd>{{ caseResult.device_brand }} {{ caseResult.device_model }}</dd>
          </div>
          <div>
            <dt>Opened</dt>
            <dd>{{ formatDate(caseResult.created_at) }}</dd>
          </div>
          <div v-if="caseResult.estimated_completion">
            <dt>Estimated completion</dt>
            <dd>{{ caseResult.estimated_completion }}</dd>
          </div>
        </dl>

        <div class="updates-section">
          <h3>Updates from the shop</h3>

          <p v-if="caseResult.events.length === 0" class="updates-empty">
            No public updates yet. Check back soon — your repair is in our queue.
          </p>

          <ol v-else class="timeline">
            <li v-for="(event, index) in caseResult.events" :key="index" class="timeline__item">
              <div class="timeline__marker" />
              <div class="timeline__content">
                <div class="timeline__meta">
                  <span class="timeline__type">
                    {{ publicEventTypeLabels[event.event_type] }}
                  </span>
                  <span>{{ formatDate(event.created_at) }}</span>
                </div>
                <p>{{ event.description }}</p>
              </div>
            </li>
          </ol>
        </div>
      </section>

      <footer class="lookup-footer">
        <RouterLink to="/login">Staff login</RouterLink>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.lookup-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background:
    radial-gradient(circle at top, rgba(37, 99, 235, 0.1), transparent 35%),
    var(--color-background);
}

.lookup-shell {
  width: min(100%, 720px);
  padding: 2rem;
  border-radius: 1.25rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
}

.lookup-header {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.5rem;
}

.lookup-header__logo {
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

.lookup-header h1 {
  font-size: 1.5rem;
  color: var(--color-heading);
}

.lookup-header p {
  color: var(--color-text-muted);
}

.lookup-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.lookup-form label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.lookup-form label span {
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.lookup-form input {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.75rem 0.85rem;
  background: var(--color-background);
  color: var(--color-text);
}

.lookup-form button,
.secondary-button {
  border: none;
  border-radius: 0.75rem;
  padding: 0.8rem 1rem;
  background: #2563eb;
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.lookup-form button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.lookup-form__error {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  padding: 0.75rem 0.85rem;
}

.case-result {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.case-result__header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.case-result__title-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.25rem;
}

.case-result__header h2 {
  color: var(--color-heading);
}

.case-result__header p {
  color: var(--color-text-muted);
}

.secondary-button {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
  white-space: nowrap;
}

.status-summary {
  padding: 0.85rem 1rem;
  border-radius: 0.85rem;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem 1rem;
}

dt {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  margin-bottom: 0.15rem;
}

dd {
  color: var(--color-text);
}

.updates-section h3 {
  margin-bottom: 0.75rem;
  color: var(--color-heading);
}

.updates-empty {
  color: var(--color-text-muted);
  font-size: 0.92rem;
}

.timeline {
  list-style: none;
  display: flex;
  flex-direction: column;
}

.timeline__item {
  display: grid;
  grid-template-columns: 1rem 1fr;
  gap: 0.85rem;
  position: relative;
  padding-bottom: 1rem;
}

.timeline__item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 0.45rem;
  top: 1rem;
  bottom: 0;
  width: 2px;
  background: var(--color-border);
}

.timeline__marker {
  width: 0.75rem;
  height: 0.75rem;
  margin-top: 0.35rem;
  border-radius: 999px;
  background: var(--color-accent);
  border: 2px solid var(--color-surface);
  box-shadow: 0 0 0 1px var(--color-border);
}

.timeline__content {
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: 0.85rem;
  padding: 0.85rem 1rem;
}

.timeline__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.5rem;
  margin-bottom: 0.45rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.timeline__type {
  font-weight: 600;
  color: var(--color-heading);
}

.timeline__content p {
  white-space: pre-wrap;
}

.lookup-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.88rem;
}

.lookup-footer a {
  color: var(--color-accent);
  text-decoration: none;
}

@media (max-width: 640px) {
  .details-grid {
    grid-template-columns: 1fr;
  }

  .case-result__header {
    flex-direction: column;
  }
}
</style>
