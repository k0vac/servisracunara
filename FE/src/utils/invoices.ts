import type { InvoiceLineItemSource, InvoiceStatus } from '@/types'

export const invoiceStatusLabels: Record<InvoiceStatus, string> = {
  pending: 'Pending',
  paid: 'Paid',
  cancelled: 'Cancelled',
}

export const invoiceLineSourceLabels: Record<InvoiceLineItemSource, string> = {
  material: 'Part',
  labor: 'Labor',
  fee: 'Fee',
  discount: 'Discount',
}
