<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { createCaseEvent, fetchCase } from '@/api/cases'
import { fetchParts } from '@/api/inventory'
import { fetchLaborTypes } from '@/api/labor'
import CaseStatusBadge from '@/components/cases/CaseStatusBadge.vue'
import type { CaseDetail, CaseEventType, LaborType, PartListItem } from '@/types'
import { caseEventTypeLabels, casePriorityLabels, formatDate } from '@/utils/cases'
import { formatMoney } from '@/utils/inventory'

const props = defineProps<{
  caseId: number
}>()

const emit = defineEmits<{
  close: []
  updated: []
}>()

type RepairPartRow = { part_id: number | ''; quantity: number }
type RepairLaborRow = { labor_type_id: number | ''; hours: number }

const caseDetail = ref<CaseDetail | null>(null)
const inventoryParts = ref<PartListItem[]>([])
const laborTypes = ref<LaborType[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const showUpdateForm = ref(false)

const updateForm = reactive({
  event_type: 'note' as CaseEventType,
  description: '',
  is_public: false,
})

const repairParts = ref<RepairPartRow[]>([])
const repairLabor = ref<RepairLaborRow[]>([])

const manualEventTypes: CaseEventType[] = ['note', 'diagnosis', 'repair']

const isRepairUpdate = computed(() => updateForm.event_type === 'repair')

function laborRate(laborTypeId: number | '') {
  if (laborTypeId === '') {
    return 0
  }
  const match = laborTypes.value.find((item) => item.id === laborTypeId)
  return match ? Number(match.hourly_rate) : 0
}

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

async function loadRepairOptions() {
  const [partsResponse, laborResponse] = await Promise.all([fetchParts(), fetchLaborTypes()])
  inventoryParts.value = partsResponse.items.filter(
    (part) => part.is_active && part.quantity_on_hand > 0,
  )
  laborTypes.value = laborResponse
}

function ensureRepairRows() {
  if (repairParts.value.length === 0) {
    repairParts.value = [{ part_id: '', quantity: 1 }]
  }
  if (repairLabor.value.length === 0) {
    repairLabor.value = [{ labor_type_id: '', hours: 1 }]
  }
}

function resetRepairRows() {
  repairParts.value = []
  repairLabor.value = []
}

function resetUpdateForm() {
  updateForm.event_type = 'note'
  updateForm.description = ''
  updateForm.is_public = false
  resetRepairRows()
  showUpdateForm.value = false
}

function addRepairPartRow() {
  repairParts.value.push({ part_id: '', quantity: 1 })
}

function removeRepairPartRow(index: number) {
  repairParts.value.splice(index, 1)
}

function addRepairLaborRow() {
  repairLabor.value.push({ labor_type_id: '', hours: 1 })
}

function removeRepairLaborRow(index: number) {
  repairLabor.value.splice(index, 1)
}

async function submitUpdate() {
  if (!caseDetail.value) {
    return
  }

  saving.value = true
  error.value = ''

  try {
    const payload = {
      event_type: updateForm.event_type,
      description: updateForm.description.trim(),
      is_public: updateForm.is_public,
      parts_used: [] as Array<{ part_id: number; quantity: number }>,
      labor: [] as Array<{ labor_type_id: number; hours: number }>,
    }

    if (updateForm.event_type === 'repair') {
      payload.parts_used = repairParts.value
        .filter((row) => row.part_id !== '')
        .map((row) => ({ part_id: Number(row.part_id), quantity: row.quantity }))

      payload.labor = repairLabor.value
        .filter((row) => row.labor_type_id !== '' && row.hours > 0)
        .map((row) => ({
          labor_type_id: Number(row.labor_type_id),
          hours: row.hours,
        }))
    }

    await createCaseEvent(caseDetail.value.id, payload)
    resetUpdateForm()
    await loadCase()
    emit('updated')
  } catch (submitError) {
    error.value = submitError instanceof Error ? submitError.message : 'Failed to add update'
  } finally {
    saving.value = false
  }
}

watch(
  () => updateForm.event_type,
  (eventType) => {
    if (eventType === 'repair') {
      ensureRepairRows()
    } else {
      resetRepairRows()
    }
  },
)

watch(showUpdateForm, (visible) => {
  if (visible && inventoryParts.value.length === 0) {
    void loadRepairOptions()
  }
})

watch(
  () => props.caseId,
  () => {
    resetUpdateForm()
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
        <div v-else-if="error && !caseDetail" class="state state--error">{{ error }}</div>

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
              <div class="section__actions">
                <span>{{ caseDetail.events.length }} entries</span>
                <button
                  v-if="caseDetail.status !== 'closed'"
                  type="button"
                  class="add-update-button"
                  @click="showUpdateForm = !showUpdateForm"
                >
                  {{ showUpdateForm ? 'Cancel' : 'Add update' }}
                </button>
              </div>
            </div>

            <form
              v-if="showUpdateForm && caseDetail.status !== 'closed'"
              class="update-form"
              @submit.prevent="submitUpdate"
            >
              <label>
                <span>Update type</span>
                <select v-model="updateForm.event_type">
                  <option v-for="type in manualEventTypes" :key="type" :value="type">
                    {{ caseEventTypeLabels[type] }}
                  </option>
                </select>
              </label>

              <label>
                <span>Description</span>
                <textarea v-model="updateForm.description" rows="4" required />
              </label>

              <label class="checkbox-row">
                <input v-model="updateForm.is_public" type="checkbox" />
                <span>Show on public case lookup</span>
              </label>

              <div v-if="isRepairUpdate" class="repair-section">
                <div class="repair-section__header">
                  <h4>Parts used</h4>
                  <button type="button" class="inline-button" @click="addRepairPartRow">Add part</button>
                </div>

                <div
                  v-for="(row, index) in repairParts"
                  :key="`part-${index}`"
                  class="repair-row"
                >
                  <select v-model="row.part_id">
                    <option value="">Select part</option>
                    <option
                      v-for="part in inventoryParts"
                      :key="part.id"
                      :value="part.id"
                    >
                      {{ part.name }} ({{ part.quantity_on_hand }} on hand)
                    </option>
                  </select>
                  <input v-model.number="row.quantity" type="number" min="1" step="1" />
                  <button
                    type="button"
                    class="inline-button inline-button--ghost"
                    :disabled="repairParts.length === 1"
                    @click="removeRepairPartRow(index)"
                  >
                    Remove
                  </button>
                </div>

                <div class="repair-section__header">
                  <h4>Labor</h4>
                  <button type="button" class="inline-button" @click="addRepairLaborRow">Add labor</button>
                </div>

                <div
                  v-for="(row, index) in repairLabor"
                  :key="`labor-${index}`"
                  class="repair-row repair-row--labor"
                >
                  <select v-model="row.labor_type_id">
                    <option value="">Select labor type</option>
                    <option
                      v-for="laborType in laborTypes"
                      :key="laborType.id"
                      :value="laborType.id"
                    >
                      {{ laborType.name }} ({{ formatMoney(laborType.hourly_rate) }}/h)
                    </option>
                  </select>
                  <input
                    v-model.number="row.hours"
                    type="number"
                    min="0.25"
                    step="0.25"
                    placeholder="Hours"
                  />
                  <span class="repair-row__total">
                    {{
                      row.labor_type_id !== '' && row.hours > 0
                        ? formatMoney(laborRate(row.labor_type_id) * row.hours)
                        : '—'
                    }}
                  </span>
                  <button
                    type="button"
                    class="inline-button inline-button--ghost"
                    :disabled="repairLabor.length === 1"
                    @click="removeRepairLaborRow(index)"
                  >
                    Remove
                  </button>
                </div>
              </div>

              <p v-if="error" class="update-form__error">{{ error }}</p>

              <button type="submit" class="submit-button" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save update' }}
              </button>
            </form>

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

                  <ul v-if="event.parts_used.length" class="event-breakdown">
                    <li v-for="(part, index) in event.parts_used" :key="`part-${event.id}-${index}`">
                      Part: {{ part.part_name }} × {{ part.quantity }} —
                      {{ formatMoney(part.line_total) }}
                    </li>
                  </ul>

                  <ul v-if="event.labor.length" class="event-breakdown">
                    <li v-for="(entry, index) in event.labor" :key="`labor-${event.id}-${index}`">
                      Labor: {{ entry.labor_type_name }} × {{ entry.hours }}h @
                      {{ formatMoney(entry.rate_at_time) }}/h —
                      {{ formatMoney(entry.line_total) }}
                    </li>
                  </ul>
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

.section__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.add-update-button,
.submit-button {
  border: none;
  border-radius: 0.75rem;
  padding: 0.55rem 0.85rem;
  background: var(--color-accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.add-update-button {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.update-form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.85rem;
  background: var(--color-surface-muted);
}

.update-form label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.update-form label span {
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.update-form input,
.update-form select,
.update-form textarea {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.65rem 0.75rem;
  background: var(--color-background);
  color: var(--color-text);
}

.checkbox-row {
  flex-direction: row !important;
  align-items: center;
  gap: 0.55rem !important;
}

.update-form__error {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  padding: 0.75rem;
}

.repair-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 0.25rem;
}

.repair-section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.repair-section__header h4 {
  font-size: 0.92rem;
  color: var(--color-heading);
}

.repair-row {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) 90px auto;
  gap: 0.5rem;
  align-items: center;
}

.repair-row--labor {
  grid-template-columns: minmax(0, 1.4fr) 90px 110px auto;
}

.repair-row select,
.repair-row input {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.55rem 0.65rem;
  background: var(--color-background);
  color: var(--color-text);
}

.repair-row__total {
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.inline-button {
  border: none;
  border-radius: 0.65rem;
  padding: 0.45rem 0.7rem;
  background: var(--color-accent);
  color: white;
  font-size: 0.82rem;
  cursor: pointer;
}

.inline-button--ghost {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.inline-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.event-breakdown {
  list-style: none;
  margin-top: 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.88rem;
  color: var(--color-text-muted);
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
