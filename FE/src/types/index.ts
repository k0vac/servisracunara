export type UserRole = 'admin' | 'technician'

export type CaseStatus = 'open' | 'in_progress' | 'awaiting_payment' | 'closed'

export type CasePriority = 'low' | 'normal' | 'urgent'

export type CaseEventType = 'note' | 'diagnosis' | 'repair' | 'part_used'

export interface User {
  id: number
  username: string
  role: UserRole
  must_change_password: boolean
}

export interface LoginResponse {
  user: User
  notifications: string[]
}

export interface CaseListItem {
  id: number
  ticket_number: string
  customer_name: string
  customer_phone: string
  device_type: string
  device_brand: string
  device_model: string
  status: CaseStatus
  priority: CasePriority
  assigned_to_username: string | null
  created_at: string
}

export interface CaseListResponse {
  items: CaseListItem[]
  total: number
}

export interface CaseEvent {
  id: number
  event_type: CaseEventType
  description: string
  is_public: boolean
  created_by_username: string | null
  created_at: string
  parts_used: CaseEventPartItem[]
  labor: CaseEventLaborItem[]
}

export interface CaseEventPartItem {
  part_name: string
  quantity: number
  unit_price_at_time: string
  line_total: string
}

export interface CaseEventLaborItem {
  labor_type_name: string
  hours: string
  rate_at_time: string
  line_total: string
}

export interface LaborType {
  id: number
  name: string
  hourly_rate: string
  is_active: boolean
}

export interface CaseDetail {
  id: number
  ticket_number: string
  customer_name: string
  customer_phone: string
  device_type: string
  device_brand: string
  device_model: string
  reported_issue: string
  status: CaseStatus
  priority: CasePriority
  assigned_to_username: string | null
  estimated_completion: string | null
  created_at: string
  closed_at: string | null
  events: CaseEvent[]
}

export interface Category {
  id: number
  name: string
}

export interface PartListItem {
  id: number
  name: string
  category_id: number | null
  category_name: string | null
  unit_price: string
  quantity_on_hand: number
  low_stock_threshold: number | null
  is_active: boolean
  is_low_stock: boolean
  created_at: string
}

export interface PartDetail extends PartListItem {
  notes: string | null
}

export interface PartListResponse {
  items: PartListItem[]
  total: number
}
