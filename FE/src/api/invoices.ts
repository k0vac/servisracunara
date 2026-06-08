import { api } from './client'
import type { InvoiceDetail, InvoiceListResponse, InvoiceStatus } from '@/types'

export function fetchInvoices(params: { status?: InvoiceStatus } = {}) {
  const query = new URLSearchParams()

  if (params.status) {
    query.set('status', params.status)
  }

  const suffix = query.toString() ? `?${query.toString()}` : ''

  return api<InvoiceListResponse>(`/api/invoices${suffix}`)
}

export function fetchInvoice(invoiceId: number) {
  return api<InvoiceDetail>(`/api/invoices/${invoiceId}`)
}

export function generateCasePayment(caseId: number) {
  return api<InvoiceDetail>(`/api/cases/${caseId}/invoice/generate`, {
    method: 'POST',
  })
}

export function markCaseInvoicePaid(caseId: number) {
  return api<InvoiceDetail>(`/api/cases/${caseId}/invoice/mark-paid`, {
    method: 'POST',
  })
}

export function retractCaseInvoice(caseId: number, reason: string) {
  return api<InvoiceDetail>(`/api/cases/${caseId}/invoice/retract`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  })
}
