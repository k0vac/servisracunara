<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import { fetchInvoice } from '@/api/invoices'
import type { InvoiceDetail } from '@/types'
import { formatDate } from '@/utils/cases'
import { formatMoney } from '@/utils/inventory'
import { invoiceLineSourceLabels, invoiceStatusLabels } from '@/utils/invoices'

const props = defineProps<{
  invoiceId: number
}>()

const emit = defineEmits<{
  close: []
}>()

const invoice = ref<InvoiceDetail | null>(null)
const loading = ref(true)
const error = ref('')

async function loadInvoice() {
  loading.value = true
  error.value = ''

  try {
    invoice.value = await fetchInvoice(props.invoiceId)
  } catch (loadError) {
    invoice.value = null
    error.value = loadError instanceof Error ? loadError.message : 'Failed to load invoice'
  } finally {
    loading.value = false
  }
}

watch(
  () => props.invoiceId,
  () => {
    void loadInvoice()
  },
)

onMounted(() => {
  void loadInvoice()
})
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal" role="dialog">
      <header class="modal__header">
        <div v-if="invoice">
          <h2>{{ invoice.invoice_number }}</h2>
          <p>{{ invoice.ticket_number }} · {{ invoice.customer_name }}</p>
        </div>
        <h2 v-else>Invoice</h2>
        <button type="button" class="modal__close" aria-label="Close" @click="emit('close')">×</button>
      </header>

      <div class="modal__body">
        <div v-if="loading" class="state">Loading invoice...</div>
        <div v-else-if="error" class="state state--error">{{ error }}</div>

        <template v-else-if="invoice">
          <div class="meta-row">
            <span
              class="invoice-status"
              :class="`invoice-status--${invoice.status}`"
            >
              {{ invoiceStatusLabels[invoice.status] }}
            </span>
            <span v-if="invoice.created_by_username">By {{ invoice.created_by_username }}</span>
            <span>{{ formatDate(invoice.created_at) }}</span>
          </div>

          <div v-if="invoice.retraction_reason" class="retraction-box">
            <strong>Retracted</strong>
            <p>{{ invoice.retraction_reason }}</p>
            <span v-if="invoice.retracted_at">{{ formatDate(invoice.retracted_at) }}</span>
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
              <tr v-for="line in invoice.line_items" :key="line.id">
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
                <td>{{ formatMoney(invoice.subtotal) }}</td>
              </tr>
              <tr>
                <td colspan="3">Tax ({{ invoice.tax_rate }}%)</td>
                <td>{{ formatMoney(invoice.tax_amount) }}</td>
              </tr>
              <tr>
                <td colspan="3"><strong>Total</strong></td>
                <td><strong>{{ formatMoney(invoice.total) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.45);
}

.modal {
  width: min(100%, 640px);
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
}

.modal__header p {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.modal__close {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--color-text-muted);
}

.modal__body {
  padding: 1.25rem 1.5rem 1.5rem;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.85rem;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.88rem;
  color: var(--color-text-muted);
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

.retraction-box {
  margin-bottom: 1rem;
  padding: 0.75rem 0.9rem;
  border-radius: 0.75rem;
  background: #f8fafc;
  border: 1px solid var(--color-border);
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.retraction-box strong {
  display: block;
  color: var(--color-heading);
}

.invoice-lines {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

.invoice-lines th,
.invoice-lines td {
  padding: 0.55rem 0.5rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.invoice-lines th {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.invoice-lines__type {
  display: inline-block;
  margin-right: 0.35rem;
  font-size: 0.72rem;
  color: var(--color-text-muted);
}

.state {
  text-align: center;
  color: var(--color-text-muted);
}

.state--error {
  color: #b91c1c;
}
</style>
