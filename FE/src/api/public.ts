import { api } from './client'
import type { PublicCase } from '@/types'

export interface PublicCaseLookupPayload {
  phone: string
  reference_code: string
}

export function lookupPublicCase(payload: PublicCaseLookupPayload) {
  return api<PublicCase>('/api/public/case-lookup', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
