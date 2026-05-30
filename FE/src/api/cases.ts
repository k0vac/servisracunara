import { api } from './client'
import type { CaseListResponse, CaseStatus } from '@/types'

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
