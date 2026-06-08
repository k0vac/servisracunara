<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { createCaseEvent, fetchCase } from '@/api/cases'
import { fetchParts } from '@/api/inventory'
import {
  generateCasePayment,
  markCaseInvoicePaid,
  retractCaseInvoice,
} from '@/api/invoices'
import { fetchLaborTypes } from '@/api/labor'
import CaseStatusBadge from '@/components/cases/CaseStatusBadge.vue'
import type { CaseDetail, CaseEventType, LaborType, PartListItem } from '@/types'
import { caseEventTypeLabels, casePriorityLabels, formatDate } from '@/utils/cases'
import { formatMoney } from '@/utils/inventory'
import { invoiceLineSourceLabels, invoiceStatusLabels } from '@/utils/invoices'

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
const showRetractForm = ref(false)
const retractReason = ref('')
const invoiceActionLoading = ref(false)

const updateForm = reactive({
  event_type: 'note' as CaseEventType,
  description: '',
  is_public: false,
})

const repairParts = ref<RepairPartRow[]>([])
const repairLabor = ref<RepairLaborRow[]>([])

const manualEventTypes: CaseEventType[] = ['note', 'diagnosis', 'repair']

const isRepairUpdate = computed(() => updateForm.event_type === 'repair')

const activeInvoice = computed(() => {
  const invoice = caseDetail.value?.invoice
  if (!invoice) {
    return null
  }

  return invoice.status === 'pending' || invoice.status === 'paid' ? invoice : null
})

const cancelledInvoice = computed(() =>
  caseDetail.value?.invoice?.status === 'cancelled' ? caseDetail.value.invoice : null,
)

const isCaseLocked = computed(() => caseDetail.value?.is_locked ?? false)

const canGeneratePayment = computed(() => {
  if (!caseDetail.value || isCaseLocked.value) {
    return false
  }

  return !activeInvoice.value
})

const canMarkPaid = computed(() => activeInvoice.value?.status === 'pending')

const canRetract = computed(() => activeInvoice.value?.status === 'pending')

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

function resetRetractForm() {
  retractReason.value = ''
  showRetractForm.value = false
}

async function handleGeneratePayment() {
  if (!caseDetail.value) {
    return
  }

  invoiceActionLoading.value = true
  error.value = ''

  try {
    await generateCasePayment(caseDetail.value.id)
    resetRetractForm()
    await loadCase()
    emit('updated')
  } catch (actionError) {
    error.value =
      actionError instanceof Error ? actionError.message : 'Failed to generate payment'
  } finally {
    invoiceActionLoading.value = false
  }
}

async function handleMarkPaid() {
  if (!caseDetail.value) {
    return
  }

  invoiceActionLoading.value = true
  error.value = ''

  try {
    await markCaseInvoicePaid(caseDetail.value.id)
    await loadCase()
    emit('updated')
  } catch (actionError) {
    error.value = actionError instanceof Error ? actionError.message : 'Failed to mark as paid'
  } finally {
    invoiceActionLoading.value = false
  }
}

async function handleRetractInvoice() {
  if (!caseDetail.value || !retractReason.value.trim()) {
    return
  }

  invoiceActionLoading.value = true
  error.value = ''

  try {
    await retractCaseInvoice(caseDetail.value.id, retractReason.value.trim())
    resetRetractForm()
    await loadCase()
    emit('updated')
  } catch (actionError) {
    error.value = actionError instanceof Error ? actionError.message : 'Failed to retract invoice'
  } finally {
    invoiceActionLoading.value = false
  }
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
    resetRetractForm()
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

          <section class="section payment-section">
            <div class="section__header">
              <h3>Payment</h3>
            </div>

            <p v-if="isCaseLocked && activeInvoice" class="lock-banner">
              This case is locked while invoice
              <strong>{{ activeInvoice.invoice_number }}</strong>
              is {{ invoiceStatusLabels[activeInvoice.status].toLowerCase() }}.
              Retract the invoice to make changes again.
            </p>

            <p v-else-if="isCaseLocked && caseDetail.status === 'closed'" class="lock-banner">
              This case is closed and paid.
            </p>

            <div v-if="cancelledInvoice" class="cancelled-banner">
              <strong>Previous invoice retracted</strong>
              <p>{{ cancelledInvoice.retraction_reason }}</p>
              <span v-if="cancelledInvoice.retracted_at">
                {{ formatDate(cancelledInvoice.retracted_at) }}
              </span>
            </div>

            <div v-if="activeInvoice || cancelledInvoice" class="invoice-card">
              <div class="invoice-card__header">
                <div>
                  <strong>{{
                    (activeInvoice ?? cancelledInvoice)?.invoice_number
                  }}</strong>
                  <span
                    class="invoice-status"
                    :class="`invoice-status--${(activeInvoice ?? cancelledInvoice)?.status}`"
                  >
                    {{
                      invoiceStatusLabels[
                        (activeInvoice ?? cancelledInvoice)!.status
                      ]
                    }}
                  </span>
                </div>
                <span class="invoice-card__total">
                  {{ formatMoney((activeInvoice ?? cancelledInvoice)!.total) }}
                </span>
              </div>

              <table class="invoice-lines">
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Qty</th>
                    <th>Unit</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="line in (activeInvoice ?? cancelledInvoice)!.line_items"
                    :key="line.id"
                  >
                    <td>
                      <span class="invoice-lines__type">
                        {{ invoiceLineSourceLabels[line.source] }}
                      </span>
                      {{ line.description }}
                    </td>
                    <td>{{ line.quantity }}</td>
                    <td>{{ formatMoney(line.unit_price) }}</td>
                    <td>{{ formatMoney(line.line_total) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr>
                    <td colspan="3">Subtotal</td>
                    <td>{{ formatMoney((activeInvoice ?? cancelledInvoice)!.subtotal) }}</td>
                  </tr>
                  <tr>
                    <td colspan="3">
                      Tax ({{ (activeInvoice ?? cancelledInvoice)!.tax_rate }}%)
                    </td>
                    <td>{{ formatMoney((activeInvoice ?? cancelledInvoice)!.tax_amount) }}</td>
                  </tr>
                  <tr>
                    <td colspan="3"><strong>Total</strong></td>
                    <td>
                      <strong>{{ formatMoney((activeInvoice ?? cancelledInvoice)!.total) }}</strong>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <div v-else class="payment-empty">
              No invoice yet. Generate payment when repair work is complete.
            </div>

            <div class="payment-actions">
              <button
                v-if="canGeneratePayment"
                type="button"
                class="payment-button"
                :disabled="invoiceActionLoading"
                @click="handleGeneratePayment"
              >
                {{ invoiceActionLoading ? 'Working...' : 'Generate payment' }}
              </button>

              <button
                v-if="canMarkPaid"
                type="button"
                class="payment-button payment-button--success"
                :disabled="invoiceActionLoading"
                @click="handleMarkPaid"
              >
                Mark as paid
              </button>

              <button
                v-if="canRetract && !showRetractForm"
                type="button"
                class="payment-button payment-button--ghost"
                :disabled="invoiceActionLoading"
                @click="showRetractForm = true"
              >
                Retract invoice
              </button>
            </div>

            <form
              v-if="showRetractForm"
              class="retract-form"
              @submit.prevent="handleRetractInvoice"
            >
              <label>
                <span>Why are you retracting this invoice?</span>
                <textarea
                  v-model="retractReason"
                  rows="3"
                  required
                  placeholder="e.g. Wrong parts listed, customer changed mind..."
                />
              </label>
              <div class="retract-form__actions">
                <button
                  type="button"
                  class="inline-button inline-button--ghost"
                  @click="resetRetractForm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  class="payment-button payment-button--danger"
                  :disabled="invoiceActionLoading || !retractReason.trim()"
                >
                  {{ invoiceActionLoading ? 'Retracting...' : 'Confirm retract' }}
                </button>
              </div>
            </form>

            <p v-if="error" class="payment-error">{{ error }}</p>
          </section>

          <section class="section">
            <div class="section__header">
              <h3>Update log</h3>
              <div class="section__actions">
                <span>{{ caseDetail.events.length }} entries</span>
                <button
                  v-if="!isCaseLocked"
                  type="button"
                  class="add-update-button"
                  @click="showUpdateForm = !showUpdateForm"
                >
                  {{ showUpdateForm ? 'Cancel' : 'Add update' }}
                </button>
              </div>
            </div>

            <p v-if="isCaseLocked" class="update-locked-note">
              Updates are disabled while this case has an active invoice or is closed.
            </p>

            <form
              v-if="showUpdateForm && !isCaseLocked"
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
.update-form textarea {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.65rem 0.75rem;
  background: var(--color-background);
  color: var(--color-text);
}

.update-form select {
  min-width: 0;
  width: 100%;
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

.repair-row input {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.55rem 0.65rem;
  background: var(--color-background);
  color: var(--color-text);
}

.repair-row select {
  min-width: 0;
  padding: 0.55rem 2.1rem 0.55rem 0.65rem;
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

.lock-banner,
.update-locked-note {
  padding: 0.75rem 0.9rem;
  border-radius: 0.75rem;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  color: #9a3412;
  font-size: 0.9rem;
  margin-bottom: 0.85rem;
}

.cancelled-banner {
  padding: 0.75rem 0.9rem;
  border-radius: 0.75rem;
  background: #f8fafc;
  border: 1px solid var(--color-border);
  margin-bottom: 0.85rem;
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.cancelled-banner strong {
  display: block;
  color: var(--color-heading);
  margin-bottom: 0.25rem;
}

.payment-empty {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin-bottom: 0.85rem;
}

.invoice-card {
  border: 1px solid var(--color-border);
  border-radius: 0.85rem;
  overflow: hidden;
  margin-bottom: 0.85rem;
}

.invoice-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  background: var(--color-surface-muted);
  border-bottom: 1px solid var(--color-border);
}

.invoice-card__total {
  font-weight: 700;
  color: var(--color-heading);
}

.invoice-status {
  margin-left: 0.5rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
}

.invoice-status--pending {
  background: #fef3c7;
  color: #92400e;
}

.invoice-status--paid {
  background: #dcfce7;
  color: #166534;
}

.invoice-status--cancelled {
  background: #f1f5f9;
  color: #475569;
}

.invoice-lines {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.invoice-lines th,
.invoice-lines td {
  padding: 0.55rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.invoice-lines th {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
}

.invoice-lines tfoot td {
  border-bottom: none;
}

.invoice-lines__type {
  display: inline-block;
  margin-right: 0.35rem;
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.payment-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.payment-button {
  border: none;
  border-radius: 0.75rem;
  padding: 0.65rem 1rem;
  background: var(--color-accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.payment-button--success {
  background: #15803d;
}

.payment-button--danger {
  background: #b91c1c;
}

.payment-button--ghost {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.payment-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.retract-form {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.85rem;
  background: var(--color-surface-muted);
}

.retract-form label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.retract-form label span {
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.retract-form textarea {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.65rem 0.75rem;
  background: var(--color-background);
  color: var(--color-text);
  resize: vertical;
}

.retract-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.payment-error {
  color: #b91c1c;
  font-size: 0.88rem;
}

@media (max-width: 640px) {
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style>
