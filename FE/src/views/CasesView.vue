<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { fetchCases } from '@/api/cases'
import CaseDetailModal from '@/components/cases/CaseDetailModal.vue'
import CaseStatusBadge from '@/components/cases/CaseStatusBadge.vue'
import NewCaseModal from '@/components/cases/NewCaseModal.vue'
import type { CaseListItem, CaseStatus } from '@/types'
import { casePriorityLabels, formatDate } from '@/utils/cases'

const cases = ref<CaseListItem[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const statusFilter = ref<CaseStatus | 'all'>('all')
const showNewCaseModal = ref(false)
const selectedCaseId = ref<number | null>(null)

const statusTabs: Array<{ label: string; value: CaseStatus | 'all' }> = [
  { label: 'All', value: 'all' },
  { label: 'Open', value: 'open' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Awaiting Payment', value: 'awaiting_payment' },
  { label: 'Closed', value: 'closed' },
]

const filteredCount = computed(() => cases.value.length)

let searchTimer: number | undefined

async function loadCases() {
  loading.value = true
  error.value = ''

  try {
    const response = await fetchCases({
      status: statusFilter.value === 'all' ? undefined : statusFilter.value,
      search: search.value.trim() || undefined,
    })
    cases.value = response.items
  } catch (loadError) {
    error.value = loadError instanceof Error ? loadError.message : 'Failed to load cases'
  } finally {
    loading.value = false
  }
}

watch(statusFilter, () => {
  void loadCases()
})

watch(search, () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    void loadCases()
  }, 300)
})

onMounted(() => {
  void loadCases()
})

function handleCaseCreated() {
  statusFilter.value = 'all'
  void loadCases()
}

function openCase(caseId: number) {
  selectedCaseId.value = caseId
}

function closeCaseDetail() {
  selectedCaseId.value = null
}
</script>

<template>
  <section class="cases-page">
    <header class="page-header">
      <div>
        <h1>Cases</h1>
        <p>Track open repairs, assignments, and payment status.</p>
      </div>
      <div class="page-header__actions">
        <div class="page-header__meta">{{ filteredCount }} shown</div>
        <button type="button" class="new-case-button" @click="showNewCaseModal = true">
          New case
        </button>
      </div>
    </header>

    <div class="toolbar">
      <div class="tabs">
        <button
          v-for="tab in statusTabs"
          :key="tab.value"
          type="button"
          class="tab"
          :class="{ 'tab--active': statusFilter === tab.value }"
          @click="statusFilter = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>

      <input
        v-model="search"
        class="search"
        type="search"
        placeholder="Search ticket, customer, device..."
      />
    </div>

    <div v-if="error" class="banner banner--error">{{ error }}</div>

    <div class="panel">
      <div v-if="loading" class="state">Loading cases...</div>

      <div v-else-if="cases.length === 0" class="state">
        No cases found. New repair cases will appear here.
      </div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Ticket</th>
              <th>Customer</th>
              <th>Device</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Assigned</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in cases"
              :key="item.id"
              class="case-row"
              @click="openCase(item.id)"
            >
              <td class="mono">{{ item.ticket_number }}</td>
              <td>
                <div class="stack">
                  <strong>{{ item.customer_name }}</strong>
                  <span class="muted">{{ item.customer_phone }}</span>
                </div>
              </td>
              <td>
                <div class="stack">
                  <strong>{{ item.device_brand }} {{ item.device_model }}</strong>
                  <span class="muted">{{ item.device_type }}</span>
                </div>
              </td>
              <td>
                <CaseStatusBadge :status="item.status" />
              </td>
              <td>{{ casePriorityLabels[item.priority] }}</td>
              <td>{{ item.assigned_to_username ?? 'Unassigned' }}</td>
              <td>{{ formatDate(item.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <NewCaseModal
      v-if="showNewCaseModal"
      @close="showNewCaseModal = false"
      @created="handleCaseCreated"
    />

    <CaseDetailModal
      v-if="selectedCaseId !== null"
      :case-id="selectedCaseId"
      @close="closeCaseDetail"
      @updated="loadCases"
    />
  </section>
</template>

<style scoped>
.cases-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.page-header h1 {
  font-size: 1.75rem;
  color: var(--color-heading);
}

.page-header p {
  color: var(--color-text-muted);
  margin-top: 0.25rem;
}

.page-header__meta {
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.new-case-button {
  border: none;
  border-radius: 0.75rem;
  padding: 0.65rem 1rem;
  background: var(--color-accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.new-case-button:hover {
  filter: brightness(1.05);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: space-between;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tab {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  border-radius: 999px;
  padding: 0.45rem 0.9rem;
  cursor: pointer;
}

.tab--active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: white;
}

.search {
  min-width: min(100%, 320px);
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.65rem 0.85rem;
  background: var(--color-surface);
  color: var(--color-text);
}

.panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  overflow: hidden;
}

.state {
  padding: 2.5rem 1.5rem;
  text-align: center;
  color: var(--color-text-muted);
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.95rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

th {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  background: var(--color-surface-muted);
}

tbody tr:hover {
  background: rgba(37, 99, 235, 0.04);
}

.case-row {
  cursor: pointer;
}

.stack {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.muted {
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.92rem;
}

.banner {
  padding: 0.85rem 1rem;
  border-radius: 0.75rem;
}

.banner--error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}
</style>
