import { api } from './client'
import type { Category, PartDetail, PartListResponse } from '@/types'

export interface CreatePartPayload {
  name: string
  category_name: string | null
  unit_price: number
  quantity_on_hand: number
  low_stock_threshold: number | null
  notes: string | null
}

export interface UpdatePartPayload {
  name?: string
  category_name?: string | null
  unit_price?: number
  low_stock_threshold?: number | null
  notes?: string | null
  is_active?: boolean
}

export function fetchCategories() {
  return api<Category[]>('/api/inventory/categories')
}

export function fetchParts(params: {
  search?: string
  category_id?: number
  include_inactive?: boolean
} = {}) {
  const query = new URLSearchParams()

  if (params.search) {
    query.set('search', params.search)
  }

  if (params.category_id) {
    query.set('category_id', String(params.category_id))
  }

  if (params.include_inactive) {
    query.set('include_inactive', 'true')
  }

  const suffix = query.toString() ? `?${query.toString()}` : ''

  return api<PartListResponse>(`/api/inventory/parts${suffix}`)
}

export function fetchPart(partId: number) {
  return api<PartDetail>(`/api/inventory/parts/${partId}`)
}

export function createPart(payload: CreatePartPayload) {
  return api<PartDetail>('/api/inventory/parts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updatePart(partId: number, payload: UpdatePartPayload) {
  return api<PartDetail>(`/api/inventory/parts/${partId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function adjustPartStock(partId: number, delta: number) {
  return api<PartDetail>(`/api/inventory/parts/${partId}/adjust-stock`, {
    method: 'POST',
    body: JSON.stringify({ delta }),
  })
}
