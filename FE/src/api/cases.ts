import { api } from './client'
import type { CaseDetail, CaseListResponse, CasePriority, CaseStatus } from '@/types'

export interface CreateCasePayload {
  customer_name: string
  customer_phone: string
  device_type: string
  device_brand: string
  device_model: string
  reported_issue: string
  priority: CasePriority
}

export function fetchCases(params: { status?: CaseStatus; search?: string } = {}) {
  const query = new URLSearchParams()

  if (params.status) {
    query.set('status', params.status)
  }

  if (params.search) {
    query.set('search', params.search)
  }

  const suffix = query.toString() ? `?${query.toString()}` : ''

  return api<CaseListResponse>(`/api/cases${suffix}`)
}

export function createCase(payload: CreateCasePayload) {
  return api<CaseListResponse['items'][number]>('/api/cases', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchCase(caseId: number) {
  return api<CaseDetail>(`/api/cases/${caseId}`)
}
