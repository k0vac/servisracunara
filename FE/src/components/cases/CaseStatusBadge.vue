<script setup lang="ts">
import type { CaseStatus } from '@/types'
import { caseStatusLabels } from '@/utils/cases'

defineProps<{
  status: CaseStatus
}>()
</script>

<template>
  <span class="badge" :class="`badge--${status}`">
    {{ caseStatusLabels[status] }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
  white-space: nowrap;
}

.badge--open {
  background: #dbeafe;
  color: #1d4ed8;
}

.badge--in_progress {
  background: #fef3c7;
  color: #b45309;
}

.badge--awaiting_payment {
  background: #ede9fe;
  color: #6d28d9;
}

.badge--closed {
  background: #dcfce7;
  color: #15803d;
}
</style>
