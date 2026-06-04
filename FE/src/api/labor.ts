import { api } from './client'
import type { LaborType } from '@/types'

export function fetchLaborTypes() {
  return api<LaborType[]>('/api/labor-types')
}
