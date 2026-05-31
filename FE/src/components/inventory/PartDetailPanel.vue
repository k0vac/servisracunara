<script setup lang="ts">
import { reactive, ref, watch } from 'vue'

import { adjustPartStock, fetchPart, updatePart } from '@/api/inventory'
import type { PartDetail } from '@/types'
import { formatMoney } from '@/utils/inventory'

const props = defineProps<{
  partId: number
}>()

const emit = defineEmits<{
  updated: []
}>()

const part = ref<PartDetail | null>(null)
const loading = ref(true)
const saving = ref(false)
const adjusting = ref(false)
const error = ref('')
const stockDelta = ref(0)

const form = reactive({
  name: '',
  category_name: '',
  unit_price: 0,
  low_stock_threshold: '' as number | '',
  notes: '',
  is_active: true,
})

async function loadPart() {
  loading.value = true
  error.value = ''

  try {
    part.value = await fetchPart(props.partId)
    form.name = part.value.name
    form.category_name = part.value.category_name ?? ''
    form.unit_price = Number(part.value.unit_price)
    form.low_stock_threshold = part.value.low_stock_threshold ?? ''
    form.notes = part.value.notes ?? ''
    form.is_active = part.value.is_active
    stockDelta.value = 0
  } catch (loadError) {
    part.value = null
    error.value = loadError instanceof Error ? loadError.message : 'Failed to load part'
  } finally {
    loading.value = false
  }
}

async function saveDetails() {
  if (!part.value) {
    return
  }

  saving.value = true
  error.value = ''

  try {
    part.value = await updatePart(part.value.id, {
      name: form.name.trim(),
      category_name: form.category_name.trim() || null,
      unit_price: Number(form.unit_price),
      low_stock_threshold:
        form.low_stock_threshold === '' ? null : Number(form.low_stock_threshold),
      notes: form.notes.trim() || null,
      is_active: form.is_active,
    })
    emit('updated')
  } catch (saveError) {
    error.value = saveError instanceof Error ? saveError.message : 'Failed to save part'
  } finally {
    saving.value = false
  }
}

async function applyStockChange() {
  if (!part.value || stockDelta.value === 0) {
    return
  }

  adjusting.value = true
  error.value = ''

  try {
    part.value = await adjustPartStock(part.value.id, stockDelta.value)
    stockDelta.value = 0
    emit('updated')
  } catch (adjustError) {
    error.value = adjustError instanceof Error ? adjustError.message : 'Failed to adjust stock'
  } finally {
    adjusting.value = false
  }
}

function bumpStock(amount: number) {
  stockDelta.value += amount
}

watch(
  () => props.partId,
  () => {
    void loadPart()
  },
  { immediate: true },
)
</script>

<template>
  <aside class="detail-panel">
    <div v-if="loading" class="state">Loading part...</div>
    <div v-else-if="error && !part" class="state state--error">{{ error }}</div>

    <template v-else-if="part">
      <header class="detail-panel__header">
        <div>
          <h2>{{ part.name }}</h2>
          <p>{{ part.category_name ?? 'Uncategorized' }}</p>
        </div>
        <span v-if="part.is_low_stock" class="low-stock-badge">Low stock</span>
      </header>

      <section class="stock-card">
        <div class="stock-card__value">
          <span>On hand</span>
          <strong>{{ part.quantity_on_hand }}</strong>
        </div>

        <div class="stock-card__controls">
          <button type="button" class="stock-button" @click="bumpStock(-1)">−</button>
          <input v-model.number="stockDelta" type="number" step="1" class="stock-input" />
          <button type="button" class="stock-button" @click="bumpStock(1)">+</button>
        </div>

        <button
          type="button"
          class="button button--primary button--block"
          :disabled="adjusting || stockDelta === 0"
          @click="applyStockChange"
        >
          {{ adjusting ? 'Updating...' : 'Apply stock change' }}
        </button>
      </section>

      <form class="detail-form" @submit.prevent="saveDetails">
        <label>
          <span>Name</span>
          <input v-model="form.name" type="text" required />
        </label>

        <label>
          <span>Category</span>
          <input v-model="form.category_name" type="text" />
        </label>

        <label>
          <span>Unit price</span>
          <input v-model.number="form.unit_price" type="number" min="0" step="0.01" required />
        </label>

        <label>
          <span>Low stock warning at</span>
          <input
            v-model.number="form.low_stock_threshold"
            type="number"
            min="0"
            step="1"
            placeholder="Optional"
          />
        </label>

        <label>
          <span>Notes</span>
          <textarea v-model="form.notes" rows="3" />
        </label>

        <label class="checkbox-row">
          <input v-model="form.is_active" type="checkbox" />
          <span>Active in inventory</span>
        </label>

        <p v-if="error" class="detail-form__error">{{ error }}</p>

        <div class="detail-form__meta">
          Current price: {{ formatMoney(part.unit_price) }}
        </div>

        <button type="submit" class="button button--primary button--block" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save changes' }}
        </button>
      </form>
    </template>
  </aside>
</template>

<style scoped>
.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: 100%;
  padding: 1rem;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
}

.detail-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: flex-start;
}

.detail-panel__header h2 {
  font-size: 1.15rem;
  color: var(--color-heading);
}

.detail-panel__header p {
  margin-top: 0.2rem;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.low-stock-badge {
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: #fef3c7;
  color: #b45309;
  font-size: 0.75rem;
  font-weight: 600;
}

.stock-card {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.9rem;
  background: var(--color-surface-muted);
}

.stock-card__value span {
  display: block;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
}

.stock-card__value strong {
  font-size: 2rem;
  color: var(--color-heading);
}

.stock-card__controls {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.5rem;
}

.stock-button {
  width: 2.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  background: var(--color-surface);
  font-size: 1.2rem;
  cursor: pointer;
}

.stock-input {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.65rem 0.75rem;
  text-align: center;
  background: var(--color-background);
  color: var(--color-text);
}

.detail-form {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

label span {
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

input,
textarea {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.65rem 0.75rem;
  background: var(--color-background);
  color: var(--color-text);
}

.checkbox-row {
  flex-direction: row;
  align-items: center;
  gap: 0.55rem;
}

.detail-form__meta {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.detail-form__error {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  padding: 0.75rem;
}

.button {
  border-radius: 0.75rem;
  padding: 0.7rem 1rem;
  cursor: pointer;
}

.button--block {
  width: 100%;
}

.button--primary {
  border: none;
  background: var(--color-accent);
  color: white;
  font-weight: 600;
}

.button--primary:disabled {
  opacity: 0.7;
  cursor: wait;
}

.state {
  padding: 1.5rem 0.5rem;
  text-align: center;
  color: var(--color-text-muted);
}

.state--error {
  color: #b91c1c;
}
</style>
