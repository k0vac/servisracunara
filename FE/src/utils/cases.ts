import type { CasePriority, CaseStatus } from '@/types'

export const caseStatusLabels: Record<CaseStatus, string> = {
  open: 'Open',
  in_progress: 'In Progress',
  awaiting_payment: 'Awaiting Payment',
  closed: 'Closed',
}

export const casePriorityLabels: Record<CasePriority, string> = {
  low: 'Low',
  normal: 'Normal',
  urgent: 'Urgent',
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}
