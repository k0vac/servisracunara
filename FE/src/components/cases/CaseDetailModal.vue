<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { fetchCase } from '@/api/cases'
import CaseStatusBadge from '@/components/cases/CaseStatusBadge.vue'
import type { CaseDetail } from '@/types'
import { caseEventTypeLabels, casePriorityLabels, formatDate } from '@/utils/cases'

const props = defineProps<{
  caseId: number
}>()

const emit = defineEmits<{
  close: []
}>()

const caseDetail = ref<CaseDetail | null>(null)
const loading = ref(true)
const error = ref('')

async function loadCase() {
  loading.value = true
  error.value = ''

  try {
    caseDetail.value = await fetchCase(props.caseId)
  } catch (loadError) {
    caseDetail.value = null
    error.value = loadError instanceof Error ? loadError.message : 'Failed to load case'
  } finally {
    loading.value = false
  }
}

watch(
  () => props.caseId,
  () => {
    void loadCase()
  },
)

onMounted(() => {
  void loadCase()
})
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal" role="dialog" :aria-labelledby="`case-${caseId}-title`">
      <header class="modal__header">
        <div v-if="caseDetail" class="modal__title-block">
          <div class="modal__title-row">
            <h2 :id="`case-${caseId}-title`">{{ caseDetail.ticket_number }}</h2>
            <CaseStatusBadge :status="caseDetail.status" />
          </div>
          <p>{{ caseDetail.customer_name }} · {{ caseDetail.device_brand }} {{ caseDetail.device_model }}</p>
        </div>
        <div v-else>
          <h2 :id="`case-${caseId}-title`">Case overview</h2>
        </div>
        <button type="button" class="modal__close" aria-label="Close" @click="emit('close')">×</button>
      </header>

      <div class="modal__body">
        <div v-if="loading" class="state">Loading case...</div>
        <div v-else-if="error" class="state state--error">{{ error }}</div>

        <template v-else-if="caseDetail">
          <section class="section">
            <h3>Case details</h3>
            <dl class="details-grid">
              <div>
                <dt>Customer</dt>
                <dd>{{ caseDetail.customer_name }}</dd>
              </div>
              <div>
                <dt>Phone</dt>
                <dd>{{ caseDetail.customer_phone }}</dd>
              </div>
              <div>
                <dt>Device</dt>
                <dd>{{ caseDetail.device_type }}</dd>
              </div>
              <div>
                <dt>Brand / model</dt>
                <dd>{{ caseDetail.device_brand }} {{ caseDetail.device_model }}</dd>
              </div>
              <div>
                <dt>Priority</dt>
                <dd>{{ casePriorityLabels[caseDetail.priority] }}</dd>
              </div>
              <div>
                <dt>Assigned to</dt>
                <dd>{{ caseDetail.assigned_to_username ?? 'Unassigned' }}</dd>
              </div>
              <div>
                <dt>Opened</dt>
                <dd>{{ formatDate(caseDetail.created_at) }}</dd>
              </div>
              <div>
                <dt>Closed</dt>
                <dd>{{ caseDetail.closed_at ? formatDate(caseDetail.closed_at) : '—' }}</dd>
              </div>
              <div class="details-grid__wide">
                <dt>Reported issue</dt>
                <dd>{{ caseDetail.reported_issue }}</dd>
              </div>
              <div v-if="caseDetail.estimated_completion" class="details-grid__wide">
                <dt>Estimated completion</dt>
                <dd>{{ caseDetail.estimated_completion }}</dd>
              </div>
            </dl>
          </section>

          <section class="section">
            <div class="section__header">
              <h3>Update log</h3>
              <span>{{ caseDetail.events.length }} entries</span>
            </div>

            <div v-if="caseDetail.events.length === 0" class="state">
              No updates recorded yet.
            </div>

            <ol v-else class="timeline">
              <li v-for="event in caseDetail.events" :key="event.id" class="timeline__item">
                <div class="timeline__marker" />
                <div class="timeline__content">
                  <div class="timeline__meta">
                    <span class="timeline__type">{{ caseEventTypeLabels[event.event_type] }}</span>
                    <span>{{ formatDate(event.created_at) }}</span>
                    <span v-if="event.created_by_username">· {{ event.created_by_username }}</span>
                    <span v-if="event.is_public" class="timeline__public">Public</span>
                  </div>
                  <p>{{ event.description }}</p>
                </div>
              </li>
            </ol>
          </section>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.45);
}

.modal {
  width: min(100%, 760px);
  max-height: calc(100vh - 2rem);
  overflow: auto;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
}

.modal__header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  background: var(--color-surface);
  z-index: 1;
}

.modal__title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal__title-row h2 {
  font-size: 1.35rem;
  color: var(--color-heading);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.modal__title-block p {
  margin-top: 0.35rem;
  color: var(--color-text-muted);
}

.modal__close {
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}

.modal__body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem 1.5rem;
}

.section h3 {
  font-size: 1rem;
  color: var(--color-heading);
  margin-bottom: 0.85rem;
}

.section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.85rem;
}

.section__header h3 {
  margin-bottom: 0;
}

.section__header span {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem 1rem;
}

.details-grid__wide {
  grid-column: 1 / -1;
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

.timeline {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.timeline__item {
  display: grid;
  grid-template-columns: 1rem 1fr;
  gap: 0.85rem;
  position: relative;
  padding-bottom: 1.1rem;
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
  align-items: center;
  margin-bottom: 0.45rem;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.timeline__type {
  font-weight: 600;
  color: var(--color-heading);
}

.timeline__public {
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 0.72rem;
  font-weight: 600;
}

.timeline__content p {
  white-space: pre-wrap;
}

.state {
  padding: 1.5rem;
  text-align: center;
  color: var(--color-text-muted);
}

.state--error {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
}

@media (max-width: 640px) {
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style>
