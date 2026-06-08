<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { fetchInvoices } from '@/api/invoices'
import InvoiceDetailModal from '@/components/invoices/InvoiceDetailModal.vue'
import type { InvoiceListItem, InvoiceStatus } from '@/types'
import { formatDate } from '@/utils/cases'
import { formatMoney } from '@/utils/inventory'
import { invoiceStatusLabels } from '@/utils/invoices'

const invoices = ref<InvoiceListItem[]>([])
const loading = ref(true)
const error = ref('')
const statusFilter = ref<InvoiceStatus | 'all'>('all')
const selectedInvoiceId = ref<number | null>(null)

const statusTabs: Array<{ label: string; value: InvoiceStatus | 'all' }> = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'Paid', value: 'paid' },
  { label: 'Cancelled', value: 'cancelled' },
]

async function loadInvoices() {
  loading.value = true
  error.value = ''

  try {
    const response = await fetchInvoices({
      status: statusFilter.value === 'all' ? undefined : statusFilter.value,
    })
    invoices.value = response.items
  } catch (loadError) {
    error.value = loadError instanceof Error ? loadError.message : 'Failed to load invoices'
  } finally {
    loading.value = false
  }
}

watch(statusFilter, () => {
  void loadInvoices()
})

onMounted(() => {
  void loadInvoices()
})
</script>

<template>
  <section class="invoices-page">
    <header class="page-header">
      <div>
        <h1>Invoices</h1>
        <p>Payment records generated from repair cases.</p>
      </div>
      <div class="page-header__meta">{{ invoices.length }} shown</div>
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
    </div>

    <div v-if="error" class="banner banner--error">{{ error }}</div>

    <div class="panel">
      <div v-if="loading" class="state">Loading invoices...</div>

      <div v-else-if="invoices.length === 0" class="state">
        No invoices yet. Generate payment from a case when work is done.
      </div>

      <table v-else class="table">
        <thead>
          <tr>
            <th>Invoice</th>
            <th>Case</th>
            <th>Customer</th>
            <th>Status</th>
            <th>Total</th>
            <th>Issued</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="invoice in invoices"
            :key="invoice.id"
            class="table__row"
            @click="selectedInvoiceId = invoice.id"
          >
            <td>{{ invoice.invoice_number }}</td>
            <td>{{ invoice.ticket_number }}</td>
            <td>{{ invoice.customer_name }}</td>
            <td>
              <span class="invoice-status" :class="`invoice-status--${invoice.status}`">
                {{ invoiceStatusLabels[invoice.status] }}
              </span>
            </td>
            <td>{{ formatMoney(invoice.total) }}</td>
            <td>{{ invoice.issued_at ? formatDate(invoice.issued_at) : '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <InvoiceDetailModal
      v-if="selectedInvoiceId"
      :invoice-id="selectedInvoiceId"
      @close="selectedInvoiceId = null"
    />
  </section>
</template>

<style scoped>
.invoices-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.page-header h1 {
  font-size: 1.5rem;
  color: var(--color-heading);
}

.page-header p {
  color: var(--color-text-muted);
}

.page-header__meta {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.tab {
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 0.45rem 0.85rem;
  background: var(--color-surface);
  color: var(--color-text-muted);
  cursor: pointer;
}

.tab--active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: white;
}

.panel {
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  background: var(--color-surface);
  overflow: hidden;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 0.85rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.table th {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  background: var(--color-surface-muted);
}

.table__row {
  cursor: pointer;
}

.table__row:hover {
  background: var(--color-surface-muted);
}

.invoice-status {
  padding: 0.15rem 0.55rem;
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

.banner--error {
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
}

.state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-muted);
}
</style>
