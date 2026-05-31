<script setup lang="ts">
import { reactive, ref } from 'vue'

import { createCase, type CreateCasePayload } from '@/api/cases'
import type { CasePriority } from '@/types'
import { casePriorityLabels } from '@/utils/cases'

const emit = defineEmits<{
  created: []
  close: []
}>()

const saving = ref(false)
const error = ref('')

const form = reactive<CreateCasePayload>({
  customer_name: '',
  customer_phone: '',
  device_type: 'Laptop',
  device_brand: '',
  device_model: '',
  reported_issue: '',
  priority: 'normal',
})

const priorityOptions = Object.entries(casePriorityLabels) as Array<[CasePriority, string]>

async function handleSubmit() {
  saving.value = true
  error.value = ''

  try {
    await createCase(form)
    emit('created')
    emit('close')
  } catch (submitError) {
    error.value = submitError instanceof Error ? submitError.message : 'Failed to create case'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal" role="dialog" aria-labelledby="new-case-title">
      <header class="modal__header">
        <div>
          <h2 id="new-case-title">New case</h2>
          <p>Enter customer and device details to open a repair case.</p>
        </div>
        <button type="button" class="modal__close" aria-label="Close" @click="emit('close')">×</button>
      </header>

      <form class="modal__form" @submit.prevent="handleSubmit">
        <div class="field-grid">
          <label>
            <span>Customer name</span>
            <input v-model="form.customer_name" type="text" required />
          </label>

          <label>
            <span>Phone</span>
            <input v-model="form.customer_phone" type="text" required />
          </label>

          <label>
            <span>Device type</span>
            <input v-model="form.device_type" type="text" required />
          </label>

          <label>
            <span>Brand</span>
            <input v-model="form.device_brand" type="text" required />
          </label>

          <label>
            <span>Model</span>
            <input v-model="form.device_model" type="text" required />
          </label>

          <label>
            <span>Priority</span>
            <select v-model="form.priority">
              <option v-for="[value, label] in priorityOptions" :key="value" :value="value">
                {{ label }}
              </option>
            </select>
          </label>
        </div>

        <label>
          <span>Reported issue</span>
          <textarea v-model="form.reported_issue" rows="4" required />
        </label>

        <p v-if="error" class="modal__error">{{ error }}</p>

        <div class="modal__actions">
          <button type="button" class="button button--ghost" @click="emit('close')">Cancel</button>
          <button type="submit" class="button button--primary" :disabled="saving">
            {{ saving ? 'Creating...' : 'Create case' }}
          </button>
        </div>
      </form>
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
  padding: 1.25rem 1.5rem 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.modal__header h2 {
  font-size: 1.25rem;
  color: var(--color-heading);
}

.modal__header p {
  margin-top: 0.25rem;
  color: var(--color-text-muted);
  font-size: 0.92rem;
}

.modal__close {
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}

.modal__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem 1.5rem 1.5rem;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

label span {
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

input,
select,
textarea {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 0.7rem 0.85rem;
  background: var(--color-background);
  color: var(--color-text);
}

textarea {
  resize: vertical;
  min-height: 110px;
}

.modal__error {
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  padding: 0.75rem 0.85rem;
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.button {
  border-radius: 0.75rem;
  padding: 0.7rem 1rem;
  cursor: pointer;
}

.button--ghost {
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text);
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

@media (max-width: 640px) {
  .field-grid {
    grid-template-columns: 1fr;
  }
}
</style>
