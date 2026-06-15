import type { CaseEventType, CasePriority, CaseStatus } from '@/types'

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

export const caseEventTypeLabels: Record<CaseEventType, string> = {
  note: 'Note',
  diagnosis: 'Diagnosis',
  repair: 'Repair',
  part_used: 'Part used',
}

export const publicCaseStatusDescriptions: Record<CaseStatus, string> = {
  open: 'We have received your device and opened your repair case.',
  in_progress: 'Your device is currently being diagnosed or repaired.',
  awaiting_payment: 'Repair work is complete. Payment is pending before pickup.',
  closed: 'This repair has been completed and paid.',
}

export const publicEventTypeLabels: Record<CaseEventType, string> = {
  note: 'Update',
  diagnosis: 'Diagnosis',
  repair: 'Repair progress',
  part_used: 'Parts',
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}
