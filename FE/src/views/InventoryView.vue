<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { fetchCategories, fetchParts } from '@/api/inventory'
import NewPartModal from '@/components/inventory/NewPartModal.vue'
import PartDetailPanel from '@/components/inventory/PartDetailPanel.vue'
import type { Category, PartListItem } from '@/types'
import { formatMoney } from '@/utils/inventory'

const parts = ref<PartListItem[]>([])
const categories = ref<Category[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const categoryFilter = ref<number | 'all'>('all')
const showInactive = ref(false)
const showNewPartModal = ref(false)
const selectedPartId = ref<number | null>(null)

const filteredCount = computed(() => parts.value.length)

let searchTimer: number | undefined

async function loadInventory() {
  loading.value = true
  error.value = ''

  try {
    const [partsResponse, categoriesResponse] = await Promise.all([
      fetchParts({
        search: search.value.trim() || undefined,
        category_id: categoryFilter.value === 'all' ? undefined : categoryFilter.value,
        include_inactive: showInactive.value,
      }),
      fetchCategories(),
    ])

    parts.value = partsResponse.items
    categories.value = categoriesResponse

    if (
      selectedPartId.value !== null &&
      !parts.value.some((part) => part.id === selectedPartId.value)
    ) {
      selectedPartId.value = parts.value[0]?.id ?? null
    }
  } catch (loadError) {
    error.value = loadError instanceof Error ? loadError.message : 'Failed to load inventory'
  } finally {
    loading.value = false
  }
}

function selectPart(partId: number) {
  selectedPartId.value = partId
}

function handlePartCreated() {
  void loadInventory()
}

function handlePartUpdated() {
  void loadInventory()
}

watch(categoryFilter, () => {
  void loadInventory()
})

watch(showInactive, () => {
  void loadInventory()
})

watch(search, () => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    void loadInventory()
  }, 300)
})

onMounted(() => {
  void loadInventory()
})
</script>

<template>
  <section class="inventory-page">
    <header class="page-header">
      <div>
        <h1>Inventory</h1>
        <p>Parts on hand for repairs and restocking.</p>
      </div>
      <div class="page-header__actions">
        <div class="page-header__meta">{{ filteredCount }} parts</div>
        <button type="button" class="primary-button" @click="showNewPartModal = true">
          New part
        </button>
      </div>
    </header>

    <div class="toolbar">
      <input
        v-model="search"
        class="search"
        type="search"
        placeholder="Search parts or categories..."
      />

      <select v-model="categoryFilter" class="select">
        <option value="all">All categories</option>
        <option v-for="category in categories" :key="category.id" :value="category.id">
          {{ category.name }}
        </option>
      </select>

      <label class="checkbox">
        <input v-model="showInactive" type="checkbox" />
        <span>Show inactive</span>
      </label>
    </div>

    <div v-if="error" class="banner banner--error">{{ error }}</div>

    <div class="inventory-layout">
      <div class="inventory-list panel">
        <div v-if="loading" class="state">Loading inventory...</div>

        <div v-else-if="parts.length === 0" class="state">
          No parts found. Add your first item to get started.
        </div>

        <div v-else class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="part in parts"
                :key="part.id"
                class="part-row"
                :class="{ 'part-row--selected': selectedPartId === part.id }"
                @click="selectPart(part.id)"
              >
                <td>
                  <strong>{{ part.name }}</strong>
                </td>
                <td>{{ part.category_name ?? '—' }}</td>
                <td>{{ part.quantity_on_hand }}</td>
                <td>{{ formatMoney(part.unit_price) }}</td>
                <td>
                  <span v-if="!part.is_active" class="status-pill status-pill--inactive">Inactive</span>
                  <span v-else-if="part.is_low_stock" class="status-pill status-pill--low">Low</span>
                  <span v-else class="status-pill status-pill--ok">OK</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <PartDetailPanel
        v-if="selectedPartId !== null"
        :part-id="selectedPartId"
        @updated="handlePartUpdated"
      />

      <div v-else class="inventory-placeholder panel">
        <p>Select a part to view details and adjust stock.</p>
      </div>
    </div>

    <NewPartModal
      v-if="showNewPartModal"
      @close="showNewPartModal = false"
      @created="handlePartCreated"
    />
  </section>
</template>

<style scoped>
.inventory-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  min-height: calc(100vh - 8rem);
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

.page-header__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.page-header__meta {
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.primary-button {
  border: none;
  border-radius: 0.75rem;
  padding: 0.65rem 1rem;
  background: var(--color-accent);
  color: white;
  font-weight: 600;
  cursor: pointer;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.search {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.65rem 0.85rem;
  background: var(--color-surface);
  color: var(--color-text);
  min-width: min(100%, 280px);
  flex: 1;
}

.select {
  min-width: 10rem;
  background-color: var(--color-surface);
}

.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-muted);
}

.inventory-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 0;
  min-height: 520px;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  overflow: hidden;
  background: var(--color-surface);
}

.panel {
  min-width: 0;
}

.inventory-list {
  border-right: 1px solid var(--color-border);
}

.inventory-placeholder {
  display: grid;
  place-items: center;
  padding: 2rem;
  color: var(--color-text-muted);
  text-align: center;
}

.state {
  padding: 2.5rem 1.5rem;
  text-align: center;
  color: var(--color-text-muted);
}

.table-wrap {
  overflow: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.9rem 1rem;
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

.part-row {
  cursor: pointer;
}

.part-row:hover,
.part-row--selected {
  background: rgba(37, 99, 235, 0.06);
}

.status-pill {
  display: inline-flex;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-pill--ok {
  background: #dcfce7;
  color: #15803d;
}

.status-pill--low {
  background: #fef3c7;
  color: #b45309;
}

.status-pill--inactive {
  background: #e5e7eb;
  color: #4b5563;
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

@media (max-width: 960px) {
  .inventory-layout {
    grid-template-columns: 1fr;
  }

  .inventory-list {
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }
}
</style>
